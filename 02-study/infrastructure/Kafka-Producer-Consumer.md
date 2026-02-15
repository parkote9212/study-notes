---
tags:
  - study
  - kafka
  - producer
  - consumer
  - messaging
created: 2026-02-15
---

# Kafka Producer-Consumer

## 한 줄 요약
> Kafka Producer는 메시지를 토픽에 발행하고, Consumer는 Consumer Group을 통해 메시지를 병렬로 소비하며, acks와 offset 관리를 통해 신뢰성을 보장한다.

## 상세 설명

### Producer와 Consumer의 역할

**Producer (생산자):**
- 메시지를 Kafka Topic에 발행
- 파티션 선택 (키 기반 또는 라운드 로빈)
- 직렬화 (객체 → 바이트)

**Consumer (소비자):**
- Kafka Topic에서 메시지 읽기
- 역직렬화 (바이트 → 객체)
- Offset 관리 (어디까지 읽었는지)

## 1. Producer 상세

### Producer 동작 과정
```
1. 애플리케이션 → send(topic, key, value)
2. Serializer → 객체를 바이트로 변환
3. Partitioner → 파티션 선택
4. Record Accumulator → 배치로 묶음
5. Sender Thread → Kafka Broker 전송
6. Broker → 디스크 저장 + ACK 반환
```

### Producer 설정 (Spring Kafka)
```java
@Configuration
public class KafkaProducerConfig {
    
    @Bean
    public ProducerFactory<String, OrderEvent> producerFactory() {
        Map<String, Object> config = new HashMap<>();
        
        // Kafka 서버 주소
        config.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        
        // 직렬화 설정
        config.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, 
            StringSerializer.class);
        config.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, 
            JsonSerializer.class);
        
        // ACK 설정 (신뢰성)
        config.put(ProducerConfig.ACKS_CONFIG, "all");  // 모든 복제본 확인
        
        // 재시도 설정
        config.put(ProducerConfig.RETRIES_CONFIG, 3);
        
        // 배치 설정 (성능)
        config.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);  // 16KB
        config.put(ProducerConfig.LINGER_MS_CONFIG, 10);  // 10ms 대기
        
        // 압축
        config.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "snappy");
        
        // 멱등성 (중복 방지)
        config.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        
        return new DefaultKafkaProducerFactory<>(config);
    }
    
    @Bean
    public KafkaTemplate<String, OrderEvent> kafkaTemplate() {
        return new KafkaTemplate<>(producerFactory());
    }
}
```

### Producer 사용 예시
```java
@Service
@RequiredArgsConstructor
public class OrderProducerService {
    
    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;
    private static final String TOPIC = "orders";
    
    // 1. 기본 전송
    public void sendOrder(OrderEvent event) {
        kafkaTemplate.send(TOPIC, event);
    }
    
    // 2. 키와 함께 전송 (파티셔닝)
    public void sendOrderWithKey(String userId, OrderEvent event) {
        // 같은 userId는 같은 파티션 → 순서 보장
        kafkaTemplate.send(TOPIC, userId, event);
    }
    
    // 3. 특정 파티션 지정
    public void sendToPartition(int partition, OrderEvent event) {
        kafkaTemplate.send(TOPIC, partition, null, event);
    }
    
    // 4. 콜백으로 결과 확인
    public void sendWithCallback(String userId, OrderEvent event) {
        ListenableFuture<SendResult<String, OrderEvent>> future = 
            kafkaTemplate.send(TOPIC, userId, event);
        
        future.addCallback(
            result -> {
                RecordMetadata metadata = result.getRecordMetadata();
                log.info("메시지 전송 성공 - Partition: {}, Offset: {}", 
                    metadata.partition(), metadata.offset());
            },
            ex -> {
                log.error("메시지 전송 실패: {}", event, ex);
                // 실패 처리 (재시도, 알림 등)
            }
        );
    }
    
    // 5. CompletableFuture (비동기)
    public CompletableFuture<SendResult<String, OrderEvent>> sendAsync(
            String userId, OrderEvent event) {
        return kafkaTemplate.send(TOPIC, userId, event).completable();
    }
    
    // 6. 트랜잭션 전송
    @Transactional
    public void sendTransactional(List<OrderEvent> events) {
        for (OrderEvent event : events) {
            kafkaTemplate.send(TOPIC, event.getUserId().toString(), event);
        }
        // 모두 성공하거나 모두 실패
    }
}
```

### Producer ACK 설정

| 값 | 의미 | 지연 시간 | 데이터 안정성 |
|----|------|----------|------------|
| **0** | ACK 안 기다림 | 매우 낮음 | 낮음 (손실 가능) |
| **1** | Leader만 확인 | 낮음 | 중간 |
| **all (-1)** | 모든 ISR 확인 | 높음 | 높음 (권장) |

```java
// 손실 허용 가능 (로그 등)
config.put(ProducerConfig.ACKS_CONFIG, "1");

// 데이터 손실 방지 (주문, 결제 등)
config.put(ProducerConfig.ACKS_CONFIG, "all");
```

### 멱등성 Producer (Idempotent)
중복 메시지 방지
```java
config.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

// 내부적으로:
// - 각 메시지에 고유 ID 부여
// - Broker가 중복 감지 후 무시
```

## 2. Consumer 상세

### Consumer 설정 (Spring Kafka)
```java
@Configuration
public class KafkaConsumerConfig {
    
    @Bean
    public ConsumerFactory<String, OrderEvent> consumerFactory() {
        Map<String, Object> config = new HashMap<>();
        
        // Kafka 서버 주소
        config.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        
        // Consumer Group ID (필수)
        config.put(ConsumerConfig.GROUP_ID_CONFIG, "order-service");
        
        // 역직렬화 설정
        config.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, 
            StringDeserializer.class);
        config.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, 
            JsonDeserializer.class);
        config.put(JsonDeserializer.TRUSTED_PACKAGES, "*");
        
        // Offset 자동 커밋 (기본값)
        config.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, true);
        config.put(ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG, 5000);
        
        // Offset 초기 위치
        config.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        // earliest: 처음부터, latest: 최신부터, none: 에러
        
        // 한 번에 가져올 레코드 수
        config.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 500);
        
        return new DefaultKafkaConsumerFactory<>(config);
    }
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> 
            kafkaListenerContainerFactory() {
        
        ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        
        factory.setConsumerFactory(consumerFactory());
        factory.setConcurrency(3);  // 3개 스레드로 병렬 처리
        
        return factory;
    }
}
```

### Consumer 사용 예시
```java
@Service
@Slf4j
public class OrderConsumerService {
    
    // 1. 기본 소비
    @KafkaListener(topics = "orders", groupId = "inventory-service")
    public void consume(OrderEvent event) {
        log.info("주문 이벤트 수신: {}", event);
        // 재고 차감 로직
        inventoryService.decreaseStock(event);
    }
    
    // 2. 메시지 메타데이터 사용
    @KafkaListener(topics = "orders", groupId = "notification-service")
    public void consumeWithMetadata(
            ConsumerRecord<String, OrderEvent> record) {
        
        log.info("Partition: {}, Offset: {}, Key: {}", 
            record.partition(), record.offset(), record.key());
        
        OrderEvent event = record.value();
        notificationService.sendOrderNotification(event);
    }
    
    // 3. 수동 Offset 커밋
    @KafkaListener(topics = "orders", 
                   groupId = "analytics-service",
                   containerFactory = "manualCommitFactory")
    public void consumeManualCommit(
            ConsumerRecord<String, OrderEvent> record,
            Acknowledgment acknowledgment) {
        
        try {
            // 메시지 처리
            analyticsService.processOrder(record.value());
            
            // 처리 성공 시 수동 커밋
            acknowledgment.acknowledge();
            
        } catch (Exception e) {
            log.error("처리 실패 - Offset: {}", record.offset(), e);
            // 커밋하지 않음 → 재처리
        }
    }
    
    // 4. 배치 처리
    @KafkaListener(topics = "orders", 
                   groupId = "batch-service",
                   containerFactory = "batchFactory")
    public void consumeBatch(List<OrderEvent> events) {
        log.info("배치 처리: {} 건", events.size());
        
        // 대량 처리 (DB 벌크 insert 등)
        orderRepository.saveAll(events);
    }
    
    // 5. 여러 토픽 동시 구독
    @KafkaListener(topics = {"orders", "payments", "shipments"},
                   groupId = "audit-service")
    public void consumeMultipleTopics(String message) {
        auditService.log(message);
    }
    
    // 6. 파티션 지정
    @KafkaListener(
        topicPartitions = @TopicPartition(
            topic = "orders",
            partitions = {"0", "1"}  // Partition 0, 1만 소비
        ),
        groupId = "special-service"
    )
    public void consumeSpecificPartitions(OrderEvent event) {
        // 특정 파티션만 처리
    }
    
    // 7. 에러 핸들링
    @KafkaListener(topics = "orders", groupId = "error-handling-service")
    public void consumeWithErrorHandling(OrderEvent event) {
        try {
            processOrder(event);
        } catch (BusinessException e) {
            // 비즈니스 예외 → DLQ로 전송
            kafkaTemplate.send("orders-dlq", event);
        } catch (Exception e) {
            // 시스템 예외 → 재처리 (커밋 안 함)
            throw e;
        }
    }
}
```

### Consumer Offset 관리

**1. 자동 커밋 (권장: 간단한 처리)**
```yaml
spring:
  kafka:
    consumer:
      enable-auto-commit: true
      auto-commit-interval: 5000  # 5초마다 자동 커밋
```

**장점:** 간단, 코드 간결  
**단점:** 메시지 손실 또는 중복 가능

**2. 수동 커밋 (권장: 중요한 데이터)**
```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> 
        manualCommitFactory() {
    
    ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory = 
        new ConcurrentKafkaListenerContainerFactory<>();
    
    factory.setConsumerFactory(consumerFactory());
    factory.getContainerProperties()
        .setAckMode(ContainerProperties.AckMode.MANUAL);  // 수동 커밋
    
    return factory;
}
```

**장점:** 정확한 제어, 메시지 손실 방지  
**단점:** 코드 복잡, 개발자 책임

## 3. 메시지 전달 보장 수준

### At-Most-Once (최대 한 번)
```
Consumer: 메시지 읽기 → 즉시 Offset 커밋 → 처리
문제: 처리 중 실패 → 메시지 손실
```

### At-Least-Once (최소 한 번) ⭐ 기본값
```
Consumer: 메시지 읽기 → 처리 → Offset 커밋
문제: 커밋 전 실패 → 메시지 중복
```

**해결: 멱등성 보장**
```java
@KafkaListener(topics = "orders", groupId = "idempotent-service")
public void consumeIdempotent(OrderEvent event) {
    // 1. 중복 체크 (DB unique constraint 또는 Redis)
    if (orderRepository.existsById(event.getOrderId())) {
        log.info("중복 메시지 무시: {}", event.getOrderId());
        return;
    }
    
    // 2. 처리
    orderService.processOrder(event);
}
```

### Exactly-Once (정확히 한 번) ⭐ 이상적
Kafka Transactions + Idempotent Consumer
```yaml
spring:
  kafka:
    producer:
      transaction-id-prefix: tx-
      enable-idempotence: true
```

```java
@Transactional
public void sendTransactional(OrderEvent event) {
    kafkaTemplate.send("orders", event);
    // DB 저장과 Kafka 전송이 하나의 트랜잭션
    orderRepository.save(event);
}
```

## 4. Consumer Rebalancing

### Rebalancing이란?
Consumer 추가/제거 시 파티션 재할당

### Rebalancing 과정
```
1. Consumer 1 추가
   → Coordinator에게 알림

2. Rebalancing 시작
   → 모든 Consumer 일시 중지

3. 파티션 재할당
   → Partition 0, 1 → Consumer 1
   → Partition 2    → Consumer 2

4. Rebalancing 완료
   → Consumer 처리 재개
```

### Rebalancing 최소화
```java
// 1. 세션 타임아웃 증가
config.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 30000);  // 30초

// 2. 하트비트 간격 감소
config.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, 3000);  // 3초

// 3. Max Poll Interval 증가 (처리 시간이 긴 경우)
config.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 300000);  // 5분
```

## 5. 실무 패턴

### Dead Letter Queue (DLQ)
처리 실패 메시지를 별도 토픽으로 전송
```java
@KafkaListener(topics = "orders", groupId = "dlq-service")
public void consume(OrderEvent event) {
    try {
        processOrder(event);
    } catch (Exception e) {
        log.error("처리 실패, DLQ로 전송: {}", event, e);
        
        // DLQ로 전송
        kafkaTemplate.send("orders-dlq", event);
        
        // 원본 메시지는 커밋 (재처리 방지)
    }
}
```

### Retry Topic
재시도 로직 구현
```java
@RetryableTopic(
    attempts = "3",
    backoff = @Backoff(delay = 1000, multiplier = 2),
    include = RetryableException.class
)
@KafkaListener(topics = "orders", groupId = "retry-service")
public void consumeWithRetry(OrderEvent event) {
    if (!isValid(event)) {
        throw new RetryableException("재시도 필요");
    }
    processOrder(event);
}
```

### Consumer Lag 모니터링
```java
@Scheduled(fixedRate = 60000)  // 1분마다
public void checkConsumerLag() {
    Map<TopicPartition, Long> endOffsets = kafkaConsumer.endOffsets(...);
    Map<TopicPartition, Long> currentOffsets = kafkaConsumer.position(...);
    
    for (TopicPartition partition : endOffsets.keySet()) {
        long lag = endOffsets.get(partition) - currentOffsets.get(partition);
        
        if (lag > 1000) {
            log.warn("높은 Consumer Lag: Partition {}, Lag {}", 
                partition, lag);
        }
    }
}
```

## 주의사항 / 함정

### 1. Consumer는 스레드 안전하지 않음
```java
// ❌ 나쁜 예: 여러 스레드에서 같은 Consumer 사용
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(...);
thread1.start(() -> consumer.poll(...));
thread2.start(() -> consumer.poll(...));

// ✅ 좋은 예: Consumer 1개당 스레드 1개
```

### 2. poll() 주기적 호출 필요
```java
// max.poll.interval.ms 내에 poll() 호출 안 하면 Rebalancing 발생
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    // 처리 시간이 max.poll.interval.ms보다 짧아야 함
}
```

### 3. 순서 보장 범위
- 같은 파티션 내에서만 순서 보장
- 여러 파티션에 걸치면 순서 보장 안 됨

### 4. 메시지 크기 제한
```java
// 기본 1MB, 큰 메시지는 S3 등에 저장 후 참조만 전송
config.put(ProducerConfig.MAX_REQUEST_SIZE_CONFIG, 1048576);
```

## 관련 개념
- [[Kafka-기본개념]] - Kafka 개요
- [[Kafka-아키텍처]] - Partition, Replica
- [[Kafka-성능과운영]] - 최적화, 모니터링
- [[Kafka-Spring통합]] - Spring Kafka 심화
- [[메시징-패턴]] - 메시징 아키텍처 패턴

## 면접 질문

1. **Producer ACK 설정 중 'all'이 무엇인가요?**
   - 모든 ISR(In-Sync Replica)이 메시지 받았는지 확인
   - 데이터 손실 최소화, 지연 시간 증가

2. **At-Least-Once와 Exactly-Once의 차이는?**
   - At-Least-Once: 중복 가능, 손실 없음 (기본)
   - Exactly-Once: 중복/손실 없음 (트랜잭션 필요)

3. **Consumer Offset을 언제 커밋해야 하나요?**
   - 자동 커밋: 간단, 손실/중복 가능
   - 수동 커밋: 처리 후, 정확한 제어

4. **Rebalancing이 왜 문제가 되나요?**
   - 일시적으로 메시지 처리 중단
   - 잦은 Rebalancing은 처리량 감소
   - 세션 타임아웃, 하트비트 조정 필요

5. **처리 실패한 메시지는 어떻게 처리하나요?**
   - DLQ(Dead Letter Queue)로 전송
   - Retry Topic으로 재시도
   - 로그 기록 후 무시

6. **같은 키를 가진 메시지의 순서는 보장되나요?**
   - 네, 같은 키 → 같은 파티션 → 순서 보장

7. **프로젝트에서 Kafka Producer/Consumer를 어떻게 사용하겠습니까?**
   - 주문 생성 시 Producer로 이벤트 발행
   - 재고/알림 서비스에서 Consumer로 처리
   - ACK=all, 수동 커밋으로 신뢰성 확보

## 참고 자료
- [Kafka Producer API](https://kafka.apache.org/documentation/#producerapi)
- [Kafka Consumer API](https://kafka.apache.org/documentation/#consumerapi)
- [Spring for Apache Kafka](https://docs.spring.io/spring-kafka/docs/current/reference/html/)
- [Kafka Producer Configurations](https://kafka.apache.org/documentation/#producerconfigs)
- [Kafka Consumer Configurations](https://kafka.apache.org/documentation/#consumerconfigs)
