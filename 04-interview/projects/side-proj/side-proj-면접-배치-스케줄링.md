---
tags: interview, batch, scheduler, spring, side-proj, project
created: 2025-01-23
difficulty: 중
---

# Side-Proj - 배치 처리 & 스케줄링 면접

## 질문 1: 배치 처리 설계 구조
> 대량의 공매 데이터를 수집하는 배치 처리를 어떻게 설계했나요?

### 핵심 답변 (3줄)
1. **페이지 단위 처리** - API 응답을 페이지별로 나눠 메모리 효율적 처리
2. **트랜잭션 분리** - 페이지별로 트랜잭션 커밋하여 실패 시 해당 페이지만 롤백
3. **책임 분리** - BatchService(흐름 제어) / TransactionService(데이터 처리) 분리

### 상세 설명
```java
@Service
@RequiredArgsConstructor
public class AuctionBatchService {

    private final OnbidApiService onbidApiService;
    private final AuctionTransactionService transactionService;

    public void fetchAndSaveOnbidData() {
        int pageNo = 1;
        int totalCount = 0;
        final int numOfRows = 100;

        while (hasMorePages(pageNo, numOfRows, totalCount)) {
            // 1. API 호출
            OnbidApiResponseDTO response = fetchApiResponse(pageNo, numOfRows);
            if (response == null) break;

            // 2. 첫 페이지에서 전체 개수 초기화
            if (pageNo == 1) {
                totalCount = response.getBody().getTotalCount();
            }

            // 3. 페이지 단위 트랜잭션 처리
            List<OnbidItemDTO> items = response.getBody().getItems();
            if (!processPageWithTransaction(items, pageNo)) {
                break;  // 실패 시 배치 중단
            }

            pageNo++;
            waitForNextPage();  // Rate Limiting
        }
    }

    private boolean processPageWithTransaction(List<OnbidItemDTO> items, int pageNo) {
        try {
            transactionService.processPageItems(items);  // 페이지 단위 트랜잭션
            return true;
        } catch (Exception e) {
            log.error("{} 페이지 실패. 롤백됨.", pageNo);
            return false;
        }
    }
}
```

### 꼬리 질문 예상
- 전체 배치를 하나의 트랜잭션으로 묶지 않은 이유는?
- Spring Batch를 사용하지 않은 이유는?

---

## 질문 2: 트랜잭션 단위 설계
> 페이지별 트랜잭션으로 분리한 이유와 롤백 전략은?

### 핵심 답변 (3줄)
1. **부분 실패 허용** - 1개 페이지 실패가 전체 데이터 손실로 이어지지 않음
2. **커밋 단위 최적화** - 100개씩 커밋하여 DB 락 시간 최소화
3. **명확한 실패 지점** - 어느 페이지에서 실패했는지 로그로 추적 가능

### 상세 설명
```java
@Service
@RequiredArgsConstructor
public class AuctionTransactionService {

    @Transactional  // 페이지 단위 트랜잭션
    public void processPageItems(List<OnbidItemDTO> items) {
        log.info("{}개 항목 트랜잭션 시작", items.size());

        for (OnbidItemDTO item : items) {
            processItem(item);  // 개별 아이템 처리
        }
        
        // 메서드 종료 시 자동 커밋
        log.info("{}개 항목 트랜잭션 커밋", items.size());
    }

    private void processItem(OnbidItemDTO item) {
        try {
            // 1. 데이터 변환
            AuctionMasterDTO master = dataCleansingService.createMasterFrom(item);
            AuctionHistoryDTO history = dataCleansingService.createHistoryFrom(item);

            // 2. 좌표 조회 (외부 API)
            processGeocoding(master);

            // 3. UPSERT (INSERT or UPDATE)
            auctionItemMapper.upsertMaster(master);
            auctionItemMapper.upsertHistory(history);

        } catch (Exception e) {
            log.error("아이템({}) 처리 실패 → 전체 페이지 롤백", item.getCltrNo());
            throw new RuntimeException("아이템 처리 실패", e);
        }
    }
}
```

**트랜잭션 흐름:**
```
페이지 1 (100개) → 성공 → 커밋 ✅
페이지 2 (100개) → 성공 → 커밋 ✅  
페이지 3 (100개) → 50번째 실패 → 페이지 3 전체 롤백 ❌
배치 중단 (페이지 1, 2는 이미 커밋됨)
```

### 꼬리 질문 예상
- 개별 아이템 단위로 트랜잭션을 분리하면 어떤 문제가 있나요?
- UPSERT 대신 INSERT만 한다면 어떤 문제가 생길 수 있나요?

---

## 질문 3: 스케줄러 설정 및 분산 환경 고려
> 스케줄러를 어떻게 설정했고, 다중 서버에서는 어떻게 대응하나요?

### 핵심 답변 (3줄)
1. **@Scheduled** - Spring 내장 스케줄러로 Cron 표현식 기반 실행
2. **ShedLock** - 분산 환경에서 중복 실행 방지 (DB 기반 락)
3. **락 시간 설정** - `lockAtLeast`, `lockAtMost`로 락 유지 시간 제어

### 상세 설명
```java
@Service
public class AuctionBatchService {

    @Scheduled(cron = "0 0 1 * * ?")  // 매일 새벽 1시
    @SchedulerLock(
        name = "onbidBatchRun",        // 락 이름
        lockAtLeastFor = "PT5M",       // 최소 5분 락 유지
        lockAtMostFor = "PT30M"        // 최대 30분 후 자동 해제
    )
    public void scheduledBatchRun() {
        log.info("스케줄러에 의해 배치가 실행됩니다.");
        fetchAndSaveOnbidData();
    }
}
```

**ShedLock 설정:**
```java
@Configuration
@EnableSchedulerLock(defaultLockAtMostFor = "PT10M")
public class SchedulerConfig {
    
    @Bean
    public LockProvider lockProvider(DataSource dataSource) {
        return new JdbcTemplateLockProvider(
            JdbcTemplateLockProvider.Configuration.builder()
                .withJdbcTemplate(new JdbcTemplate(dataSource))
                .usingDbTime()  // DB 시간 기준
                .build()
        );
    }
}
```

**shedlock 테이블:**
```sql
CREATE TABLE shedlock (
    name VARCHAR(64) NOT NULL PRIMARY KEY,
    lock_until TIMESTAMP NOT NULL,
    locked_at TIMESTAMP NOT NULL,
    locked_by VARCHAR(255) NOT NULL
);
```

### 꼬리 질문 예상
- `lockAtLeast`를 설정하는 이유는?
- Redis 기반 분산 락과의 차이점은?

---

## 질문 4: 외부 API 호출과 트랜잭션 경계
> 트랜잭션 내에서 외부 API(카카오 지오코딩)를 호출하는 것의 문제점은?

### 핵심 답변 (3줄)
1. **트랜잭션 시간 증가** - API 응답 대기 시간만큼 DB 커넥션 점유
2. **롤백 불가** - API 호출은 롤백되지 않음 (트랜잭션 외부 작업)
3. **현재 구조의 절충** - 좌표 없이 저장 후 나중에 보강하는 방식 가능

### 상세 설명
```java
// 현재 구조 - 트랜잭션 내 API 호출 (문제점 있음)
@Transactional
public void processPageItems(List<OnbidItemDTO> items) {
    for (OnbidItemDTO item : items) {
        AuctionMasterDTO master = createMasterFrom(item);
        
        // ⚠️ 트랜잭션 내 외부 API 호출
        processGeocoding(master);  // 카카오 API 호출 → 응답 대기
        
        auctionItemMapper.upsertMaster(master);
    }
    // API 호출 시간 + DB 작업 시간 동안 커넥션 점유
}

// 개선안 1: 좌표 없이 먼저 저장 → 별도 배치로 좌표 보강
@Transactional
public void processPageItems(List<OnbidItemDTO> items) {
    for (OnbidItemDTO item : items) {
        AuctionMasterDTO master = createMasterFrom(item);
        auctionItemMapper.upsertMaster(master);  // 좌표 없이 저장
    }
}

// 별도 배치: 좌표 없는 데이터만 조회 → 좌표 보강
@Scheduled(cron = "0 0 2 * * ?")
public void geocodingBatch() {
    List<AuctionMasterDTO> noCoordItems = mapper.findWithoutCoordinates();
    for (AuctionMasterDTO item : noCoordItems) {
        DocumentDTO coords = kakaoMapService.getCoordinates(item.getAddress());
        if (coords != null) {
            mapper.updateCoordinates(item.getCltrNo(), coords.getLat(), coords.getLng());
        }
    }
}
```

### 꼬리 질문 예상
- 외부 API 호출을 트랜잭션 밖으로 빼려면 어떻게 해야 하나요?
- 보상 트랜잭션(Compensating Transaction) 패턴이란?

---

## 질문 5: 배치 모니터링 및 에러 핸들링
> 배치 실패 시 알림이나 복구는 어떻게 처리하나요?

### 핵심 답변 (3줄)
1. **구조화된 로깅** - 페이지 번호, 처리 건수, 에러 내용을 상세히 기록
2. **부분 성공 허용** - 실패 페이지 이전까지는 데이터 보존
3. **재시작 용이성** - 마지막 성공 페이지부터 재시작 가능하도록 설계

### 상세 설명
```java
@Service
@Slf4j
public class AuctionBatchService {

    public void fetchAndSaveOnbidData() {
        int pageNo = 1;
        int successCount = 0;
        int failedPage = -1;

        try {
            while (hasMorePages(...)) {
                if (!processPageWithTransaction(items, pageNo)) {
                    failedPage = pageNo;
                    break;
                }
                successCount += items.size();
                pageNo++;
            }
        } finally {
            // 배치 결과 요약 로그
            log.info("=== 배치 실행 결과 ===");
            log.info("처리 성공: {} 건", successCount);
            log.info("마지막 성공 페이지: {}", pageNo - 1);
            if (failedPage > 0) {
                log.error("실패 페이지: {}", failedPage);
                // 알림 발송 (Slack, Email 등)
                notificationService.sendBatchFailureAlert(failedPage);
            }
        }
    }
}

// 재시작 지원 (마지막 성공 페이지부터)
public void resumeBatch(int startPage) {
    log.info("{} 페이지부터 배치 재시작", startPage);
    // ...
}
```

**배치 상태 테이블 (고급):**
```sql
CREATE TABLE batch_execution (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    batch_name VARCHAR(100),
    start_time DATETIME,
    end_time DATETIME,
    status ENUM('RUNNING', 'COMPLETED', 'FAILED'),
    last_page INT,
    total_count INT,
    error_message TEXT
);
```

### 꼬리 질문 예상
- Spring Batch의 JobRepository와 비교하면 어떤 차이가 있나요?
- 배치 중 서버가 갑자기 종료되면 어떻게 되나요?

---

## 참고
- [[Spring-Scheduler-가이드]]
- [[ShedLock-분산락]]
- [[side-proj-면접-WebClient-API연동]]
