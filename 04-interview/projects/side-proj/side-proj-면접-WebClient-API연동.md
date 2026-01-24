---
tags: interview, {{topic}}
created:
  "{ date:YYYY-MM-DD }":
difficulty: 중
---

# {{title}}

## 질문
> 

## 핵심 답변 (3줄)
1. 
2. 
3. 

## 상세 설명


## 코드 예시 (필요시)
```java
```

## 꼬리 질문 예상
- 
- 

## 참고
- [[]]
```
# Side-Proj - WebClient & 외부 API 연동 면접

## 질문 1: WebClient vs RestTemplate 선택 이유
> RestTemplate 대신 WebClient를 사용한 이유는 무엇인가요?

### 핵심 답변 (3줄)
1. **비동기/논블로킹** - 응답 대기 중 스레드가 블로킹되지 않아 효율적
2. **Spring 5+ 권장** - RestTemplate은 유지보수 모드, WebClient가 공식 권장
3. **유연한 에러 처리** - `onStatus()`로 HTTP 상태별 세밀한 예외 처리 가능

### 상세 설명
```java
// WebClient 빈 설정 (Config)
@Bean
@Qualifier("kakaoWebClient")
public WebClient kakaoWebClient() {
    return WebClient.builder()
            .baseUrl("https://dapi.kakao.com")
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .build();
}

// 서비스에서 사용
@Service
public class KakaoMapService {
    private final WebClient kakaoWebClient;
    
    public DocumentDTO getCoordinates(String address) {
        return kakaoWebClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/v2/local/search/address.json")
                        .queryParam("query", address)
                        .build())
                .header("Authorization", "KakaoAK " + kakaoApiKey)
                .retrieve()
                .onStatus(status -> status.is4xxClientError(), res -> {
                    log.error("클라이언트 에러: {}", res.statusCode());
                    return res.createException();
                })
                .bodyToMono(KakaoAddressResponseDTO.class)
                .timeout(Duration.ofSeconds(10))
                .block();  // 동기식 호출이 필요한 경우
    }
}
```

### 꼬리 질문 예상
- `.block()`을 사용하면 논블로킹의 장점이 사라지는 것 아닌가요?
- WebClient를 완전 비동기로 사용하려면 어떻게 해야 하나요?

---

## 질문 2: 재시도(Retry) 전략 구현
> 외부 API 호출 실패 시 재시도 로직은 어떻게 구현했나요?

### 핵심 답변 (3줄)
1. **Spring Retry** - `@Retryable` 어노테이션으로 선언적 재시도
2. **Backoff 전략** - 재시도 간격을 점진적으로 늘려 서버 부하 방지
3. **특정 예외만 재시도** - 5xx 서버 에러는 재시도, 4xx 클라이언트 에러는 즉시 실패

### 상세 설명
```java
@Service
public class KakaoMapService {

    @Retryable(
            value = {WebClientResponseException.class},  // 재시도 대상 예외
            maxAttempts = 3,                              // 최대 3회 시도
            backoff = @Backoff(delay = 1000)              // 1초 간격
    )
    public DocumentDTO getCoordinates(String address) {
        return kakaoWebClient.get()
                .uri(...)
                .retrieve()
                .onStatus(status -> status.is5xxServerError(), res -> {
                    log.warn("서버 에러 발생 - 재시도 예정: {}", res.statusCode());
                    return res.createException();  // 예외 발생 → 재시도
                })
                .bodyToMono(KakaoAddressResponseDTO.class)
                .block();
    }
    
    @Recover  // 모든 재시도 실패 시 호출
    public DocumentDTO recoverGetCoordinates(WebClientResponseException e, String address) {
        log.error("모든 재시도 실패. 기본값 반환: {}", address);
        return null;
    }
}
```

**@EnableRetry 활성화 필요:**
```java
@Configuration
@EnableRetry
public class RetryConfig {}
```

### 꼬리 질문 예상
- Exponential Backoff는 어떻게 구현하나요?
- Circuit Breaker 패턴과의 차이점은?

---

## 질문 3: XML 응답 파싱 처리
> 온비드 API의 XML 응답을 어떻게 처리했나요?

### 핵심 답변 (3줄)
1. **Jackson XmlMapper** - JSON과 동일한 방식으로 XML ↔ 객체 변환
2. **String으로 수신 후 파싱** - WebClient에서 직접 DTO 변환 시 오류 방지
3. **@JacksonXmlProperty** - XML 태그명과 필드명 매핑

### 상세 설명
```java
@Service
public class OnbidApiService {
    private final XmlMapper xmlMapper = new XmlMapper();
    
    public OnbidApiResponseDTO fetchOnbidData(int pageNo, int numOfRows) {
        // 1. XML 문자열로 수신
        String xmlResponse = onbidWebClient
                .get()
                .uri(uriBuilder -> uriBuilder
                        .path("/getKamcoPbctCltrList")
                        .queryParam("serviceKey", serviceKey)
                        .queryParam("pageNo", pageNo)
                        .queryParam("numOfRows", numOfRows)
                        .build())
                .retrieve()
                .bodyToMono(String.class)
                .block();
        
        // 2. XmlMapper로 파싱
        return xmlMapper.readValue(xmlResponse, OnbidApiResponseDTO.class);
    }
}
```

**DTO 정의:**
```java
@Getter
@JacksonXmlRootElement(localName = "response")
public class OnbidApiResponseDTO {
    
    @JacksonXmlProperty(localName = "header")
    private Header header;
    
    @JacksonXmlProperty(localName = "body")
    private Body body;
    
    @Getter
    public static class Body {
        @JacksonXmlProperty(localName = "totalCount")
        private int totalCount;
        
        @JacksonXmlElementWrapper(localName = "items")
        @JacksonXmlProperty(localName = "item")
        private List<OnbidItemDTO> items;
    }
}
```

### 꼬리 질문 예상
- JSON과 XML 둘 다 지원해야 한다면 어떻게 설계하나요?
- JAXB와 Jackson XmlMapper의 차이점은?

---

## 질문 4: Rate Limiting 처리
> 외부 API의 호출 제한(Rate Limit)은 어떻게 대응했나요?

### 핵심 답변 (3줄)
1. **Thread.sleep()** - 요청 간 1초 대기로 단순 Rate Limiting
2. **배치 단위 처리** - 페이지 단위로 데이터 처리 후 대기
3. **429 응답 처리** - Rate Limit 초과 시 지수 백오프 적용 가능

### 상세 설명
```java
@Service
public class AuctionBatchService {

    private void processBatchData() {
        int pageNo = 1;
        
        while (hasMorePages(pageNo, numOfRows, totalCount)) {
            // 1. API 호출
            OnbidApiResponseDTO response = fetchApiResponse(pageNo, numOfRows);
            
            // 2. 데이터 처리
            processPageWithTransaction(response.getBody().getItems(), pageNo);
            
            pageNo++;
            
            // 3. Rate Limiting - 다음 요청 전 1초 대기
            waitForNextPage();
        }
    }
    
    private boolean waitForNextPage() {
        try {
            log.info("다음 페이지 요청 전 1초 대기 (Rate Limiting)...");
            Thread.sleep(1000);
            return true;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
    }
}
```

**고급 Rate Limiting (Bucket4j 라이브러리):**
```java
// 초당 10개 요청으로 제한
Bucket bucket = Bucket.builder()
    .addLimit(Bandwidth.simple(10, Duration.ofSeconds(1)))
    .build();

if (bucket.tryConsume(1)) {
    // API 호출
} else {
    // 대기 또는 예외
}
```

### 꼬리 질문 예상
- Thread.sleep() 사용의 단점은?
- 분산 환경에서 Rate Limiting은 어떻게 구현하나요?

---

## 질문 5: 여러 외부 API WebClient 분리 관리
> 온비드 API와 카카오 API의 WebClient를 어떻게 분리 관리했나요?

### 핵심 답변 (3줄)
1. **@Qualifier 사용** - 동일 타입의 빈을 이름으로 구분하여 주입
2. **baseUrl 분리** - 각 API별로 기본 URL 설정
3. **공통 설정 재사용** - 타임아웃, 로깅 등 공통 설정은 빌더로 추출

### 상세 설명
```java
@Configuration
public class WebClientConfig {

    @Bean
    @Qualifier("onbidWebClient")
    public WebClient onbidWebClient() {
        return WebClient.builder()
                .baseUrl("https://api.odcloud.kr/api/15058775/v1")
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_XML_VALUE)
                .codecs(config -> config.defaultCodecs().maxInMemorySize(10 * 1024 * 1024))
                .build();
    }

    @Bean
    @Qualifier("kakaoWebClient")
    public WebClient kakaoWebClient() {
        return WebClient.builder()
                .baseUrl("https://dapi.kakao.com")
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .build();
    }
}

// 서비스에서 주입
@Service
public class OnbidApiService {
    public OnbidApiService(@Qualifier("onbidWebClient") WebClient onbidWebClient) {
        this.onbidWebClient = onbidWebClient;
    }
}

@Service
public class KakaoMapService {
    public KakaoMapService(@Qualifier("kakaoWebClient") WebClient kakaoWebClient) {
        this.kakaoWebClient = kakaoWebClient;
    }
}
```

### 꼬리 질문 예상
- WebClient를 스레드 안전(thread-safe)하게 재사용해도 되나요?
- 각 API별로 다른 타임아웃을 적용하려면?

---

## 참고
- [[Spring-WebClient-가이드]]
- [[Spring-Retry-설정]]
- [[side-proj-면접-외부API-배치]]
