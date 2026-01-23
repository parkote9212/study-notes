---
tags: interview, webflux, api, batch, side-proj, project
created: 2025-01-23
difficulty: 중
---

# Side-Proj - 외부 API 연동 & 배치 처리 면접

## 질문 1: WebClient를 사용한 외부 API 연동
> RestTemplate 대신 WebClient를 선택한 이유와 구현 방법은?

### 핵심 답변 (3줄)
1. **Non-blocking I/O** - 비동기 처리로 스레드 자원 효율적 사용
2. **Fluent API** - 메서드 체이닝으로 가독성 높은 코드
3. **리액티브 스택 호환** - Mono/Flux로 확장 가능, 대량 요청 처리에 유리

### 상세 설명
```java
@Service
public class OnbidApiService {
    
    private final WebClient onbidWebClient;
    private final XmlMapper xmlMapper;
    
    public OnbidApiService(@Qualifier("onbidWebClient") WebClient webClient,
                          @Value("${onbid.api.serviceKey}") String serviceKey) {
        this.onbidWebClient = webClient;
        this.xmlMapper = new XmlMapper();
    }
    
    public OnbidApiResponseDTO fetchOnbidData(int pageNo, int numOfRows) {
        try {
            // 1. WebClient로 XML 문자열 받기
            String xmlResponse = onbidWebClient
                .get()
                .uri(uriBuilder -> uriBuilder
                    .path("/getKamcoPbctCltrList")
                    .queryParam("serviceKey", serviceKey)
                    .queryParam("pageNo", pageNo)
                    .queryParam("numOfRows", numOfRows)
                    .queryParam("DPSL_MTD_CD", "0001")
                    .build())
                .retrieve()
                .bodyToMono(String.class)
                .block();  // 동기 처리 (배치에서 순차 처리 필요)
            
            // 2. Jackson XmlMapper로 수동 파싱
            return xmlMapper.readValue(xmlResponse, OnbidApiResponseDTO.class);
            
        } catch (Exception e) {
            log.error("Onbid API 호출 실패", e);
            throw new RuntimeException("API 처리 중 오류", e);
        }
    }
}
```

### WebClient 설정 (Bean)
```java
@Configuration
public class WebClientConfig {
    
    @Bean("onbidWebClient")
    public WebClient onbidWebClient() {
        return WebClient.builder()
            .baseUrl("https://api.onbid.co.kr")
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_XML_VALUE)
            .codecs(config -> config.defaultCodecs().maxInMemorySize(5 * 1024 * 1024))
            .build();
    }
    
    @Bean("kakaoWebClient")
    public WebClient kakaoWebClient() {
        return WebClient.builder()
            .baseUrl("https://dapi.kakao.com")
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .build();
    }
}
```

### 꼬리 질문 예상
- `block()`을 사용하면 Non-blocking의 장점이 사라지지 않나요?
- XML 응답을 JSON처럼 처리하려면 어떻게 해야 하나요?

---

## 질문 2: Spring Retry를 활용한 재시도 로직
> 외부 API 호출 실패 시 재시도 로직을 어떻게 구현했나요?

### 핵심 답변 (3줄)
1. **@Retryable 어노테이션** - 선언적 재시도로 코드 간결
2. **대상 예외 지정** - `WebClientResponseException`(5xx) 발생 시만 재시도
3. **Backoff 전략** - 재시도 간격 1초, 최대 3회로 서버 부하 방지

### 상세 설명
```java
@Service
public class KakaoMapService {
    
    @Retryable(
        value = {WebClientResponseException.class},  // 재시도 대상 예외
        maxAttempts = 3,                              // 최대 3회
        backoff = @Backoff(delay = 1000)              // 1초 간격
    )
    public DocumentDTO getCoordinates(String address) {
        return kakaoWebClient.get()
            .uri(uriBuilder -> uriBuilder
                .path("/v2/local/search/address.json")
                .queryParam("query", address)
                .build())
            .header("Authorization", "KakaoAK " + kakaoApiKey)
            .retrieve()
            .onStatus(status -> status.is5xxServerError(), response -> {
                log.warn("카카오 API 서버 에러 (재시도 대상)");
                return response.createException();  // 예외 발생 → 재시도
            })
            .bodyToMono(KakaoAddressResponseDTO.class)
            .timeout(Duration.ofSeconds(10))
            .block();
    }
    
    @Recover  // 모든 재시도 실패 시 호출
    public DocumentDTO recoverGetCoordinates(WebClientResponseException e, String address) {
        log.error("카카오 API 재시도 모두 실패: {}", address);
        return null;  // 좌표 없이 진행
    }
}
```

```java
// Application에서 Retry 활성화
@SpringBootApplication
@EnableRetry
public class SideProjApplication { }
```

### 꼬리 질문 예상
- 지수 백오프(Exponential Backoff)는 어떻게 설정하나요?
- Circuit Breaker 패턴과의 차이점은?

---

## 질문 3: 배치 처리와 트랜잭션 분리
> 대량 데이터 수집 배치에서 트랜잭션을 어떻게 관리했나요?

### 핵심 답변 (3줄)
1. **페이지 단위 트랜잭션** - 100건씩 묶어서 커밋 (전체 롤백 방지)
2. **서비스 분리** - `AuctionBatchService`(배치 흐름) + `AuctionTransactionService`(트랜잭션)
3. **Rate Limiting** - API 호출 간 1초 대기로 서버 부하 방지

### 상세 설명
```java
// 배치 흐름 관리 (트랜잭션 없음)
@Service
@RequiredArgsConstructor
public class AuctionBatchService {
    
    private final OnbidApiService onbidApiService;
    private final AuctionTransactionService txService;  // 트랜잭션 서비스
    
    @Scheduled(cron = "0 0 1 * * ?")  // 매일 새벽 1시
    @SchedulerLock(name = "onbidBatchRun", lockAtLeastFor = "PT5M", lockAtMostFor = "PT30M")
    public void scheduledBatchRun() {
        int pageNo = 1;
        final int numOfRows = 100;
        
        while (true) {
            OnbidApiResponseDTO response = onbidApiService.fetchOnbidData(pageNo, numOfRows);
            if (response == null || response.getBody().getItems().isEmpty()) break;
            
            // 페이지 단위 트랜잭션 (실패 시 해당 페이지만 롤백)
            try {
                txService.processPageItems(response.getBody().getItems());
                log.info("{} 페이지 처리 완료", pageNo);
            } catch (Exception e) {
                log.error("{} 페이지 실패, 다음 페이지로 진행", pageNo);
            }
            
            pageNo++;
            Thread.sleep(1000);  // Rate Limiting
        }
    }
}

// 트랜잭션 단위 처리
@Service
@RequiredArgsConstructor
public class AuctionTransactionService {
    
    @Transactional  // 페이지 단위로 커밋/롤백
    public void processPageItems(List<OnbidItemDTO> items) {
        for (OnbidItemDTO item : items) {
            AuctionMasterDTO master = dataCleansingService.createMasterFrom(item);
            AuctionHistoryDTO history = dataCleansingService.createHistoryFrom(item);
            
            processGeocoding(master);  // 카카오 API 호출
            
            auctionItemMapper.upsertMaster(master);
            auctionItemMapper.upsertHistory(history);
        }
    }
}
```

### 꼬리 질문 예상
- `@SchedulerLock`은 왜 필요한가요? (다중 인스턴스 환경)
- 트랜잭션 내에서 외부 API를 호출하는 것의 문제점은?

---

## 질문 4: 데이터 정제(Cleansing) 로직
> 외부 API 응답 데이터를 어떻게 정제했나요?

### 핵심 답변 (3줄)
1. **주소 정제** - 괄호, 상세 정보 제거로 Geocoding 정확도 향상
2. **날짜 형식 변환** - "yyyyMMddHHmmss" → LocalDateTime
3. **단일 책임** - `DataCleansingService`로 변환/정제 로직 분리

### 상세 설명
```java
@Service
public class DataCleansingService {
    
    private static final DateTimeFormatter ONBID_FORMATTER =
        DateTimeFormatter.ofPattern("yyyyMMddHHmmss");
    
    public AuctionMasterDTO createMasterFrom(OnbidItemDTO item) {
        return AuctionMasterDTO.builder()
            .cltrNo(item.getCltrNo())
            .cltrNm(item.getCltrNm())
            .ldnmAdrs(item.getLdnmAdrs())  // 원본 저장
            .clnLdnmAdrs(cleanseAddress(item.getLdnmAdrs()))  // 정제 주소
            .onbidDetailUrl("https://www.onbid.co.kr/.../cltrView.do?cltrCltrNo=" + item.getCltrNo())
            .build();
    }
    
    /**
     * 주소 정제: Geocoding 정확도 향상
     * - 괄호 내용 제거: "(토지)", "[일좌권1매]" 등
     * - 다중 지번 제거: "589-1, 589-2, 589-3" → "589-1"
     * - 상세 정보 제거: "외 2필지", "보관중인 출자증권" 등
     */
    private String cleanseAddress(String rawAddress) {
        if (rawAddress == null) return "";
        
        String cleaned = rawAddress.trim();
        
        // 1. 괄호 내용 제거
        cleaned = cleaned.replaceAll("\\([^\\)]*\\)", "");
        cleaned = cleaned.replaceAll("\\[[^\\]]*\\]", "");
        
        // 2. 상세 정보 제거
        cleaned = cleaned.replaceAll(" 외\\s*\\d*필지.*", "");
        cleaned = cleaned.replaceAll("\\s보관중인.*", "");
        
        // 3. 쉼표 이후 제거 (첫 번째 지번만 유지)
        int comma = cleaned.indexOf(',');
        if (comma != -1) {
            cleaned = cleaned.substring(0, comma);
        }
        
        return cleaned.trim();
    }
    
    private LocalDateTime parseOnbidDateTime(String str) {
        if (str == null || str.isBlank()) return null;
        
        try {
            return LocalDateTime.parse(str, ONBID_FORMATTER);
        } catch (DateTimeParseException e) {
            log.warn("날짜 파싱 실패: {}", str);
            return null;
        }
    }
}
```

### 꼬리 질문 예상
- 정규식 성능 문제는 없나요? (Pattern.compile 캐싱)
- 주소 정제 후에도 Geocoding 실패하면 어떻게 처리하나요?

---

## 질문 5: UPSERT 패턴 구현
> 데이터 중복 시 INSERT/UPDATE를 어떻게 처리했나요?

### 핵심 답변 (3줄)
1. **MyBatis + MySQL UPSERT** - `INSERT ... ON DUPLICATE KEY UPDATE` 구문
2. **Master/History 분리** - 불변 데이터(Master)와 가변 데이터(History) 구분
3. **효율적 갱신** - 전체 DELETE 후 INSERT가 아닌 선택적 UPDATE

### 상세 설명
```xml
<!-- AuctionItemMapper.xml -->

<!-- Master: 물건번호(cltr_no)가 PK -->
<insert id="upsertMaster" parameterType="AuctionMasterDTO">
    INSERT INTO auction_master (
        cltr_no, cltr_nm, ctgr_full_nm,
        ldnm_adrs, nmrd_adrs, cln_ldnm_adrs, cln_nmrd_adrs,
        latitude, longitude, onbid_detail_url
    ) VALUES (
        #{cltrNo}, #{cltrNm}, #{ctgrFullNm},
        #{ldnmAdrs}, #{nmrdAdrs}, #{clnLdnmAdrs}, #{clnNmrdAdrs},
        #{latitude}, #{longitude}, #{onbidDetailUrl}
    )
    ON DUPLICATE KEY UPDATE
        cltr_nm = VALUES(cltr_nm),
        ctgr_full_nm = VALUES(ctgr_full_nm),
        latitude = COALESCE(VALUES(latitude), latitude),  -- null이면 기존값 유지
        longitude = COALESCE(VALUES(longitude), longitude),
        updated_at = CURRENT_TIMESTAMP
</insert>

<!-- History: 물건이력번호(cltr_hstr_no)가 PK -->
<insert id="upsertHistory" parameterType="AuctionHistoryDTO">
    INSERT INTO auction_history (
        cltr_hstr_no, cltr_no, pbct_cltr_stat_nm,
        pbct_begn_dtm, pbct_cls_dtm, min_bid_prc, apsl_ases_avg_amt
    ) VALUES (
        #{cltrHstrNo}, #{cltrNo}, #{pbctCltrStatNm},
        #{pbctBegnDtm}, #{pbctClsDtm}, #{minBidPrc}, #{apslAsesAvgAmt}
    )
    ON DUPLICATE KEY UPDATE
        pbct_cltr_stat_nm = VALUES(pbct_cltr_stat_nm),
        pbct_begn_dtm = VALUES(pbct_begn_dtm),
        pbct_cls_dtm = VALUES(pbct_cls_dtm),
        min_bid_prc = VALUES(min_bid_prc),
        updated_at = CURRENT_TIMESTAMP
</insert>
```

### 꼬리 질문 예상
- `COALESCE`를 사용한 이유는?
- PostgreSQL에서는 UPSERT를 어떻게 구현하나요? (`INSERT ... ON CONFLICT`)

---

## 질문 6: Full-Text Search 구현
> 물건 검색 기능을 어떻게 최적화했나요?

### 핵심 답변 (3줄)
1. **MySQL Full-Text Index** - 정제된 주소(`cln_ldnm_adrs`)에 인덱스 생성
2. **MATCH ... AGAINST 구문** - 자연어 검색으로 관련도 순 정렬
3. **LIKE 대비 성능 향상** - 대용량 데이터에서 10배 이상 빠른 검색

### 상세 설명
```sql
-- 테이블 생성 시 Full-Text Index
CREATE TABLE auction_master (
    cltr_no VARCHAR(50) PRIMARY KEY,
    cltr_nm VARCHAR(500),
    cln_ldnm_adrs VARCHAR(500),
    cln_nmrd_adrs VARCHAR(500),
    
    FULLTEXT INDEX ft_address (cln_ldnm_adrs, cln_nmrd_adrs),
    FULLTEXT INDEX ft_name (cltr_nm)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

```xml
<!-- MyBatis 검색 쿼리 -->
<select id="searchByKeyword" resultType="AuctionMasterDTO">
    SELECT *
    FROM auction_master
    WHERE MATCH(cln_ldnm_adrs, cln_nmrd_adrs) AGAINST(#{keyword} IN NATURAL LANGUAGE MODE)
       OR MATCH(cltr_nm) AGAINST(#{keyword} IN NATURAL LANGUAGE MODE)
    ORDER BY 
        MATCH(cln_ldnm_adrs, cln_nmrd_adrs) AGAINST(#{keyword}) DESC,
        MATCH(cltr_nm) AGAINST(#{keyword}) DESC
    LIMIT #{limit} OFFSET #{offset}
</select>
```

### 꼬리 질문 예상
- Full-Text Index의 한계는? (2글자 이하 검색어)
- Elasticsearch를 도입한다면 어떤 이점이 있나요?

---

## 참고
- [[WebClient-vs-RestTemplate]]
- [[Spring-Retry-Circuit-Breaker]]
- [[MySQL-Full-Text-Search]]
