---
tags:
  - interview
  - logging
  - monitoring
  - side-proj
  - project
created: 2025-01-23
difficulty: 중
---

# Side-proj - 배치 로깅 모니터링

## 질문
> 배치 작업의 성공/실패를 모니터링하는 방법은?

## 핵심 답변 (3줄)
1. **구조화된 로깅** - 작업 시작/종료, 처리 건수, 소요 시간 기록
2. **로그 레벨 분리** - INFO(정상), WARN(경고), ERROR(실패)
3. **알림 연동** - Slack, Email 등으로 실패 시 즉시 알림

## 상세 설명
```java
@Component
@Slf4j
public class AptDataBatchScheduler {
    
    @Scheduled(cron = "0 0 2 * * *")
    public void runDailyBatch() {
        long startTime = System.currentTimeMillis();
        String batchId = UUID.randomUUID().toString();
        
        log.info("[BATCH-START] ID: {}, Time: {}", batchId, LocalDateTime.now());
        
        try {
            LocalDate targetDate = LocalDate.now().minusDays(1);
            int processedCount = batchService.collectAptTradeData(targetDate);
            
            long duration = System.currentTimeMillis() - startTime;
            
            log.info("[BATCH-SUCCESS] ID: {}, Processed: {}, Duration: {}ms", 
                batchId, processedCount, duration);
            
            // 메트릭 기록
            recordBatchMetrics(batchId, processedCount, duration, true);
            
        } catch (Exception e) {
            long duration = System.currentTimeMillis() - startTime;
            
            log.error("[BATCH-FAILED] ID: {}, Duration: {}ms, Error: {}", 
                batchId, duration, e.getMessage(), e);
            
            // 실패 알림
            notificationService.sendFailureAlert(batchId, e);
            
            recordBatchMetrics(batchId, 0, duration, false);
        }
    }
    
    private void recordBatchMetrics(String batchId, int count, 
                                    long duration, boolean success) {
        BatchHistory history = BatchHistory.builder()
            .batchId(batchId)
            .processedCount(count)
            .durationMs(duration)
            .status(success ? "SUCCESS" : "FAILED")
            .executedAt(LocalDateTime.now())
            .build();
        
        batchHistoryRepository.save(history);
    }
}
```

**Logback 설정:**
```xml
<!-- logback-spring.xml -->
<configuration>
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/batch.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/batch.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <logger name="com.project.batch" level="INFO" additivity="false">
        <appender-ref ref="FILE"/>
    </logger>
</configuration>
```

## 꼬리 질문 예상
- ELK 스택을 도입한다면 어떻게 구성하나요?
- 배치 실패율이 높아지면 어떻게 감지하나요?

## 참고
- [[구조화된-로깅-패턴]]
- [[배치-모니터링-전략]]
