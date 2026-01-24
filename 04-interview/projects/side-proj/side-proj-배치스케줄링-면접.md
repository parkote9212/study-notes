---
tags:
  - interview
  - batch
  - scheduling
  - spring
  - side-proj
  - project
created: 2025-01-23
difficulty: 중
---

# Side-proj - Spring Batch 스케줄링

## 질문
> @Scheduled를 사용한 배치 작업 스케줄링 구현 방법은?

## 핵심 답변 (3줄)
1. **@EnableScheduling** - 스케줄링 기능 활성화
2. **Cron 표현식** - 매일 새벽 2시 실행 등 정교한 시간 설정
3. **비동기 처리** - `@Async`로 메인 스레드 블로킹 방지

## 상세 설명
```java
@Configuration
@EnableScheduling
public class SchedulingConfig {
    
    @Bean
    public TaskScheduler taskScheduler() {
        ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
        scheduler.setPoolSize(5);
        scheduler.setThreadNamePrefix("batch-scheduler-");
        scheduler.initialize();
        return scheduler;
    }
}

@Component
@RequiredArgsConstructor
@Slf4j
public class AptDataBatchScheduler {
    
    private final AptDataBatchService batchService;
    
    // 매일 새벽 2시 실행
    @Scheduled(cron = "0 0 2 * * *")
    public void runDailyBatch() {
        log.info("=== 아파트 실거래 데이터 수집 시작 ===");
        
        try {
            LocalDate yesterday = LocalDate.now().minusDays(1);
            batchService.collectAptTradeData(yesterday);
            log.info("=== 배치 작업 완료 ===");
        } catch (Exception e) {
            log.error("배치 작업 실패", e);
            // 알림 발송 등 후속 처리
        }
    }
    
    // 매시간 정각 실행
    @Scheduled(cron = "0 0 * * * *")
    public void runHourlyHealthCheck() {
        log.info("Health check at {}", LocalDateTime.now());
        // 시스템 상태 점검 로직
    }
}
```

**Cron 표현식:**
```
0 0 2 * * *   → 매일 2:00
0 */30 * * * *  → 매 30분마다
0 0 0 * * MON  → 매주 월요일 자정
```

## 꼬리 질문 예상
- 배치가 이전 실행이 끝나기 전에 다시 시작되면?
- Quartz Scheduler와의 차이는?

## 참고
- [[Spring-Scheduling-완벽가이드]]
- [[side-proj-배치중복실행방지-면접]]
