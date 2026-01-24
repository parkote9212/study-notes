---
tags:
  - interview
  - batch
  - concurrency
  - spring
  - side-proj
  - project
created: 2025-01-23
difficulty: 중
---

# Side-proj - 배치 중복 실행 방지

## 질문
> 동시에 여러 배치가 실행되는 것을 어떻게 방지했나요?

## 핵심 답변 (3줄)
1. **AtomicBoolean** - 배치 실행 여부를 원자적으로 체크
2. **compareAndSet()** - Lock-free 알고리즘으로 동시성 제어
3. **Early Return** - 이미 실행 중이면 즉시 리턴

## 상세 설명
```java
@Component
@Slf4j
public class AptDataBatchScheduler {
    
    private final AtomicBoolean isRunning = new AtomicBoolean(false);
    private final AptDataBatchService batchService;
    
    @Scheduled(cron = "0 0 2 * * *")
    public void runDailyBatch() {
        // CAS(Compare-And-Set) 연산으로 락 획득 시도
        if (!isRunning.compareAndSet(false, true)) {
            log.warn("이전 배치 작업이 아직 실행 중입니다. 건너뜁니다.");
            return;
        }
        
        try {
            log.info("=== 배치 작업 시작 ===");
            LocalDate yesterday = LocalDate.now().minusDays(1);
            batchService.collectAptTradeData(yesterday);
            log.info("=== 배치 작업 완료 ===");
        } catch (Exception e) {
            log.error("배치 작업 실패", e);
        } finally {
            // 항상 락 해제
            isRunning.set(false);
        }
    }
}
```

**AtomicBoolean vs synchronized 비교:**
| 방식 | 장점 | 단점 |
|------|------|------|
| AtomicBoolean | Lock-free, 성능 우수 | 단순 플래그만 가능 |
| synchronized | 복잡한 임계영역 가능 | Thread blocking |

**대안: ShedLock 라이브러리**
```java
@SchedulerLock(name = "aptDataBatch", 
               lockAtMostFor = "1h",
               lockAtLeastFor = "5m")
@Scheduled(cron = "0 0 2 * * *")
public void runDailyBatch() {
    // 분산 환경에서도 동작
}
```

## 꼬리 질문 예상
- 분산 환경(여러 서버)에서는 어떻게 중복 방지하나요?
- Redis를 사용한 분산 락 구현 방법은?

## 참고
- [[Java-Atomic-클래스]]
- [[분산락-구현-전략]]
