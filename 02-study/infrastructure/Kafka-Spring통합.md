---
tags:
  - study
  - kafka
  - spring
  - spring-boot
  - spring-kafka
created: 2026-02-15
---

# Kafka Spring 통합

## 한 줄 요약
> Spring Kafka는 @KafkaListener, KafkaTemplate, @EnableKafka를 제공하여 Kafka를 Spring Boot에 쉽게 통합하며, 트랜잭션, 에러 처리, 테스트를 지원한다.

## 상세 설명

### Spring Kafka란?
- **Spring의 Kafka 통합 라이브러리**
- 선언적 메시지 리스닝 (@KafkaListener)
- 간편한 메시지 발행 (KafkaTemplate)
- Spring 트랜잭션과 통합

## 1. 프로젝트 설정

### Gradle 의존성
```gradle
dependencies {
    // Spring Kafka
    implementation 'org.springframework.kafka:spring-kafka'
    
    // Spring Boot Starter (자동 설정 포함)
    implementation 'org.springframework.boot:spring-boot-starter'
    
    // JSON 직렬화
    implementation 'com.fasterxml.jackson.core:jackson-databind'
    
    // 테스트
    testImplementation 'org.springframework.kafka:spring-kafka-test'
}
```

### application.yml 설정
```yaml
spring:
  kafka:
    # Kafka 서버 주소
    bootstrap-servers: localhost:9092
    
    # Producer 설정
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      acks: all  # 모든 복제본 확인
      retries: 3
      properties:
        linger.ms: 10
        batch.size: 16384
        compression.type: snappy
        enable.idempotence: true
    
    # Consumer 설정
    consumer:
      group-id: order-service
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      auto-offset-reset: earliest
      enable-auto-commit: false  # 수동 커밋
      properties:
        spring.json.trusted.packages: "*"
        max.poll.records: 500
    
    # Listener 설정
    listener:
      ack-mode: manual  # 수동 ACK
      concurrency: 3    # 동시 처리 스레드 수
```

## 2. Producer 구현

### 기본 설정
```java
@Configuration
@EnableKafka
public class KafkaProducerConfig {
    
    @Value("${spring.kafka.bootstrap-servers}")
    private String bootstrapServers;
    
    @Bean
    public ProducerFactory<String, OrderEvent> orderProducerFactory() {
        Map<String, Object> config = new HashMap<>();
        config.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        config.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        config.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        config.put(ProducerConfig.ACKS_CONFIG, "all");
        config.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        
        return new DefaultKafkaProducerFactory<>(config);
    }
    
    @Bean
    public KafkaTemplate<String, OrderEvent> orderKafkaTemplate() {
        return new KafkaTemplate<>(orderProducerFactory());
    }
    
    // 여러 타입을 위한 Generic Template
    @Bean
    public KafkaTemplate<String, Object> genericKafkaTemplate() {
        return new KafkaTemplate<>(genericProducerFactory());
    }
}
```

### Producer Service 구현
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderEventProducer {
    
    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    private static final String TOPIC = "orders";
    
    // 1. 기본 발행
    public void publishOrderCreated(OrderEvent event) {
        kafkaTemplate.send(TOPIC, event.getOrderId().toString(), event);
        log.info("주문 이벤트 발행: {}", event.getOrderId());
    }
    
    // 2. 콜백으로 결과 확인
    public void publishWithCallback(OrderEvent event) {
        kafkaTemplate.send(TOPIC, event.getOrderId().toString(), event)
            .addCallback(
                result -> {
                    RecordMetadata metadata = result.getRecordMetadata();
                    log.info("전송 성공 - Topic: {}, Partition: {}, Offset: {}", 
                        metadata.topic(), metadata.partition(), metadata.offset());
                },
                ex -> {
                    log.error("전송 실패: {}", event, ex);
                    // 재시도 또는 DLQ 전송
                    handleFailure(event, ex);
                }
            );
    }
    
    // 3. CompletableFuture 사용
    public CompletableFuture<SendResult<String, OrderEvent>> publishAsync(OrderEvent event) {
        return kafkaTemplate.send(TOPIC, event.getOrderId().toString(), event)
            .completable()
            .whenComplete((result, ex) -> {
                if (ex != null) {
                    log.error("비동기 전송 실패", ex);
                } else {
                    log.info("비동기 전송 성공: {}", result.getRecordMetadata().offset());
                }
            });
    }
    
    // 4. 헤더 추가
    public void publishWithHeaders(OrderEvent event) {
        ProducerRecord<String, OrderEvent> record = new ProducerRecord<>(
            TOPIC, event.getOrderId().toString(), event);
        
        // 커스텀 헤더 추가
        record.headers().add("source", "order-service".getBytes());
        record.headers().add("version", "1.0".getBytes());
        record.headers().add("timestamp", String.valueOf(System.currentTimeMillis()).getBytes());
        
        kafkaTemplate.send(record);
    }
    
    private void handleFailure(OrderEvent event, Throwable ex) {
        // DLQ로 전송 또는 재시도 로직
        log.error("이벤트 처리 실패, DLQ로 전송: {}", event.getOrderId());
    }
}
```

### 트랜잭션 발행
```java
@Configuration
public class KafkaTransactionConfig {
    
    @Bean
    public ProducerFactory<String, OrderEvent> transactionalProducerFactory() {
        Map<String, Object> config = new HashMap<>();
        config.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        config.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        config.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        
        // 트랜잭션 설정
        config.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "order-tx-");
        config.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        
        DefaultKafkaProducerFactory<String, OrderEvent> factory = 
            new DefaultKafkaProducerFactory<>(config);
        
        factory.setTransactionIdPrefix("order-tx-");
        return factory;
    }
    
    @Bean
    public KafkaTemplate<String, OrderEvent> transactionalKafkaTemplate() {
        return new KafkaTemplate<>(transactionalProducerFactory());
    }
}

@Service
@RequiredArgsConstructor
public class TransactionalOrderService {
    
    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;
    private final OrderRepository orderRepository;
    
    @Transactional
    public void createOrderWithEvent(OrderDto dto) {
        // 1. DB 저장
        Order order = orderRepository.save(new Order(dto));
        
        // 2. Kafka 이벤트 발행 (DB 트랜잭션과 연동)
        OrderEvent event = OrderEvent.from(order);
        kafkaTemplate.send("orders", order.getId().toString(), event);
        
        // 3. DB와 Kafka 모두 성공하거나 모두 실패
        // 롤백 시 Kafka 전송도 취소됨
    }
}
```

## 3. Consumer 구현

### 기본 설정
```java
@Configuration
@EnableKafka
public class KafkaConsumerConfig {
    
    @Value("${spring.kafka.bootstrap-servers}")
    private String bootstrapServers;
    
    @Bean
    public ConsumerFactory<String, OrderEvent> orderConsumerFactory() {
        Map<String, Object> config = new HashMap<>();
        config.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        config.put(ConsumerConfig.GROUP_ID_CONFIG, "order-service");
        config.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        config.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, ErrorHandlingDeserializer.class);
        config.put(ErrorHandlingDeserializer.VALUE_DESERIALIZER_CLASS, JsonDeserializer.class);
        config.put(JsonDeserializer.TRUSTED_PACKAGES, "*");
        config.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        
        return new DefaultKafkaConsumerFactory<>(config);
    }
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> 
            kafkaListenerContainerFactory() {
        
        ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        
        factory.setConsumerFactory(orderConsumerFactory());
        factory.setConcurrency(3);  // 3개 스레드
        factory.getContainerProperties().setAckMode(AckMode.MANUAL);
        
        // 에러 핸들러 설정
        factory.setCommonErrorHandler(new DefaultErrorHandler(
            new FixedBackOff(1000L, 3L)  // 1초 간격, 3번 재시도
        ));
        
        return factory;
    }
    
    // 배치 리스너
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> 
            batchListenerFactory() {
        
        ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        
        factory.setConsumerFactory(orderConsumerFactory());
        factory.setBatchListener(true);  // 배치 모드
        factory.setConcurrency(3);
        
        return factory;
    }
}
```

### Consumer Service 구현
```java
@Service
@Slf4j
@RequiredArgsConstructor
public class OrderEventConsumer {
    
    private final InventoryService inventoryService;
    private final NotificationService notificationService;
    
    // 1. 기본 소비
    @KafkaListener(topics = "orders", groupId = "inventory-service")
    public void consumeOrder(OrderEvent event) {
        log.info("주문 이벤트 수신: {}", event.getOrderId());
        inventoryService.decreaseStock(event);
    }
    
    // 2. 메타데이터 활용
    @KafkaListener(topics = "orders", groupId = "notification-service")
    public void consumeWithMetadata(
            ConsumerRecord<String, OrderEvent> record,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset) {
        
        log.info("Partition: {}, Offset: {}, Key: {}", 
            partition, offset, record.key());
        
        notificationService.sendOrderNotification(record.value());
    }
    
    // 3. 수동 ACK
    @KafkaListener(topics = "orders", 
                   groupId = "analytics-service",
                   containerFactory = "kafkaListenerContainerFactory")
    public void consumeManualAck(
            ConsumerRecord<String, OrderEvent> record,
            Acknowledgment acknowledgment) {
        
        try {
            // 메시지 처리
            processOrder(record.value());
            
            // 처리 성공 시 수동 커밋
            acknowledgment.acknowledge();
            
        } catch (Exception e) {
            log.error("처리 실패 - Offset: {}", record.offset(), e);
            // 커밋하지 않음 → 재처리
        }
    }
    
    // 4. 배치 소비
    @KafkaListener(topics = "orders", 
                   groupId = "batch-service",
                   containerFactory = "batchListenerFactory")
    public void consumeBatch(
            List<ConsumerRecord<String, OrderEvent>> records,
            Acknowledgment acknowledgment) {
        
        log.info("배치 수신: {} 건", records.size());
        
        List<OrderEvent> events = records.stream()
            .map(ConsumerRecord::value)
            .collect(Collectors.toList());
        
        // 배치 처리
        orderService.processBatch(events);
        
        // 전체 배치 커밋
        acknowledgment.acknowledge();
    }
    
    // 5. 여러 토픽 구독
    @KafkaListener(topics = {"orders", "payments", "shipments"},
                   groupId = "audit-service")
    public void consumeMultipleTopics(String message,
                                     @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
        log.info("Topic: {}, Message: {}", topic, message);
        auditService.log(topic, message);
    }
    
    // 6. 특정 파티션만 구독
    @KafkaListener(
        topicPartitions = @TopicPartition(
            topic = "orders",
            partitions = {"0", "1"}
        ),
        groupId = "special-service"
    )
    public void consumeSpecificPartitions(OrderEvent event) {
        log.info("특정 파티션 처리: {}", event);
    }
    
    // 7. 조건부 소비
    @KafkaListener(topics = "orders", groupId = "vip-service")
    public void consumeVipOrders(OrderEvent event) {
        if (event.isVip()) {
            // VIP 주문만 처리
            vipService.processVipOrder(event);
        }
    }
}
```

### 에러 처리
```java
@Configuration
public class KafkaErrorHandlingConfig {
    
    // 1. Custom Error Handler
    @Bean
    public DefaultErrorHandler errorHandler() {
        // 재시도 정책: 1초, 2초, 4초 간격으로 3번 재시도
        BackOff backOff = new ExponentialBackOff(1000, 2.0);
        
        DefaultErrorHandler handler = new DefaultErrorHandler(
            (record, exception) -> {
                // 최종 실패 처리 (DLQ 전송)
                log.error("최종 실패 - DLQ로 전송: {}", record, exception);
                sendToDLQ(record);
            },
            backOff
        );
        
        // 재시도하지 않을 예외
        handler.addNotRetryableExceptions(IllegalArgumentException.class);
        
        return handler;
    }
    
    // 2. DLQ (Dead Letter Queue)
    @Bean
    public DeadLetterPublishingRecoverer deadLetterPublishingRecoverer(
            KafkaTemplate<String, Object> kafkaTemplate) {
        
        return new DeadLetterPublishingRecoverer(kafkaTemplate,
            (record, ex) -> {
                // DLQ 토픽 결정
                return new TopicPartition(record.topic() + "-dlq", -1);
            }
        );
    }
    
    private void sendToDLQ(ConsumerRecord<?, ?> record) {
        // DLQ로 전송 로직
    }
}

@Service
public class DeadLetterQueueConsumer {
    
    @KafkaListener(topics = "orders-dlq", groupId = "dlq-handler")
    public void consumeDLQ(ConsumerRecord<String, OrderEvent> record) {
        log.error("DLQ 메시지 수신 - 수동 처리 필요: {}", record.value());
        
        // 수동 처리, 알림, 모니터링 등
        alertService.sendAlert("DLQ 메시지 발생: " + record.value());
    }
}
```

### Retry Topic
```java
@Configuration
@EnableKafka
@EnableKafkaRetryTopic
public class KafkaRetryConfig {
    
    @Bean
    public RetryTopicConfiguration retryTopicConfiguration(
            KafkaTemplate<String, Object> kafkaTemplate) {
        
        return RetryTopicConfigurationBuilder
            .newInstance()
            .maxAttempts(4)  // 총 4번 시도 (원본 1 + 재시도 3)
            .exponentialBackoff(1000, 2, 10000)  // 1초, 2초, 4초
            .retryTopicSuffix("-retry")
            .dltSuffix("-dlt")  // Dead Letter Topic
            .dltHandlerMethod("processDltMessage")
            .create(kafkaTemplate);
    }
}

@Service
public class RetryableOrderConsumer {
    
    @RetryableTopic(
        attempts = "4",
        backoff = @Backoff(delay = 1000, multiplier = 2.0),
        include = {RetryableException.class}
    )
    @KafkaListener(topics = "orders", groupId = "retryable-service")
    public void consume(OrderEvent event) {
        if (shouldRetry(event)) {
            throw new RetryableException("재시도 필요");
        }
        processOrder(event);
    }
    
    @DltHandler
    public void processDltMessage(OrderEvent event) {
        log.error("DLT 메시지: {}", event);
        // 최종 실패 처리
    }
}
```

## 4. 통합 예제: 주문 시스템

### Domain Event
```java
@Data
@Builder
public class OrderEvent {
    private Long orderId;
    private Long userId;
    private List<OrderItem> items;
    private BigDecimal totalAmount;
    private OrderStatus status;
    private LocalDateTime createdAt;
    
    public static OrderEvent from(Order order) {
        return OrderEvent.builder()
            .orderId(order.getId())
            .userId(order.getUserId())
            .items(order.getItems())
            .totalAmount(order.getTotalAmount())
            .status(order.getStatus())
            .createdAt(order.getCreatedAt())
            .build();
    }
}
```

### Order Service (Producer)
```java
@Service
@RequiredArgsConstructor
@Transactional
public class OrderService {
    
    private final OrderRepository orderRepository;
    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    public Order createOrder(CreateOrderRequest request) {
        // 1. 주문 생성
        Order order = Order.create(request);
        orderRepository.save(order);
        
        // 2. 이벤트 발행
        OrderEvent event = OrderEvent.from(order);
        kafkaTemplate.send("orders", order.getId().toString(), event)
            .addCallback(
                result -> log.info("주문 이벤트 발행 성공: {}", order.getId()),
                ex -> log.error("주문 이벤트 발행 실패: {}", order.getId(), ex)
            );
        
        return order;
    }
}
```

### Inventory Service (Consumer)
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class InventoryEventConsumer {
    
    private final InventoryService inventoryService;
    private final KafkaTemplate<String, InventoryEvent> kafkaTemplate;
    
    @KafkaListener(topics = "orders", groupId = "inventory-service")
    @Transactional
    public void handleOrderCreated(OrderEvent event, Acknowledgment ack) {
        try {
            log.info("재고 차감 시작: {}", event.getOrderId());
            
            // 재고 차감
            for (OrderItem item : event.getItems()) {
                inventoryService.decreaseStock(
                    item.getProductId(), 
                    item.getQuantity()
                );
            }
            
            // 재고 차감 완료 이벤트 발행
            InventoryEvent inventoryEvent = InventoryEvent.builder()
                .orderId(event.getOrderId())
                .status(InventoryStatus.RESERVED)
                .build();
            
            kafkaTemplate.send("inventory", event.getOrderId().toString(), inventoryEvent);
            
            // 성공 시 커밋
            ack.acknowledge();
            
        } catch (OutOfStockException e) {
            log.error("재고 부족: {}", event.getOrderId(), e);
            
            // 재고 부족 이벤트 발행
            InventoryEvent failEvent = InventoryEvent.builder()
                .orderId(event.getOrderId())
                .status(InventoryStatus.FAILED)
                .reason("재고 부족")
                .build();
            
            kafkaTemplate.send("inventory", event.getOrderId().toString(), failEvent);
            ack.acknowledge();
            
        } catch (Exception e) {
            log.error("재고 처리 실패: {}", event.getOrderId(), e);
            // 커밋하지 않음 → 재처리
        }
    }
}
```

## 5. 테스트

### Embedded Kafka 테스트
```java
@SpringBootTest
@EmbeddedKafka(
    partitions = 1,
    topics = {"orders", "inventory"},
    brokerProperties = {
        "listeners=PLAINTEXT://localhost:9092",
        "port=9092"
    }
)
class KafkaIntegrationTest {
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    @Autowired
    private OrderEventConsumer consumer;
    
    @Test
    @DisplayName("주문 이벤트 발행 및 소비 테스트")
    void testOrderEvent() throws Exception {
        // Given
        OrderEvent event = OrderEvent.builder()
            .orderId(1L)
            .userId(100L)
            .totalAmount(BigDecimal.valueOf(50000))
            .build();
        
        // When
        kafkaTemplate.send("orders", "1", event).get();
        
        // Then
        await().atMost(5, TimeUnit.SECONDS)
            .untilAsserted(() -> {
                verify(consumer).consumeOrder(any(OrderEvent.class));
            });
    }
}
```

### TestContainer 테스트
```java
@SpringBootTest
@Testcontainers
class KafkaTestContainerTest {
    
    @Container
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:latest")
    );
    
    @DynamicPropertySource
    static void kafkaProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }
    
    @Test
    void testWithRealKafka() {
        // 실제 Kafka 컨테이너로 테스트
    }
}
```

## 관련 개념
- [[Kafka-기본개념]] - Kafka 개요
- [[Kafka-Producer-Consumer]] - 메시지 발행/소비
- [[Spring-트랜잭션]] - 트랜잭션 관리
- [[Spring-테스트]] - 통합 테스트
- [[이벤트기반아키텍처]] - MSA 이벤트 패턴

## 면접 질문

1. **Spring Kafka의 @KafkaListener가 어떻게 동작하나요?**
   - Spring AOP 기반 프록시
   - 백그라운드 스레드로 poll() 호출
   - 메시지 수신 시 메서드 실행

2. **KafkaTemplate과 @KafkaListener의 차이는?**
   - KafkaTemplate: Producer (메시지 발행)
   - @KafkaListener: Consumer (메시지 수신)

3. **Kafka 트랜잭션을 어떻게 구현하나요?**
   - transactional-id 설정
   - @Transactional 어노테이션
   - DB와 Kafka가 하나의 트랜잭션

4. **에러 발생 시 어떻게 처리하나요?**
   - 재시도 (ExponentialBackOff)
   - DLQ로 전송
   - 수동 커밋으로 재처리

5. **Spring Kafka 테스트는 어떻게 하나요?**
   - @EmbeddedKafka (간단)
   - TestContainers (실제 Kafka)

6. **프로젝트에서 Spring Kafka를 어떻게 활용하겠습니까?**
   - 주문 생성 시 이벤트 발행
   - 재고/알림 서비스에서 소비
   - 수동 커밋, DLQ로 안정성 확보

## 참고 자료
- [Spring for Apache Kafka 공식 문서](https://docs.spring.io/spring-kafka/docs/current/reference/html/)
- [Spring Kafka Samples](https://github.com/spring-projects/spring-kafka/tree/main/samples)
- [Baeldung - Spring Kafka Tutorial](https://www.baeldung.com/spring-kafka)
- [Spring Kafka Error Handling](https://docs.spring.io/spring-kafka/docs/current/reference/html/#error-handling)
