---
tags:
  - study
  - kafka
  - messaging
  - event-streaming
  - msa
created: 2026-02-15
---

# Kafka 기본개념

## 한 줄 요약
> Kafka는 분산 이벤트 스트리밍 플랫폼으로, 대용량 실시간 데이터 파이프라인과 이벤트 기반 아키텍처를 구축하는 데 사용되는 고성능 메시지 브로커이다.

## 상세 설명

### Kafka란?
**Apache Kafka**는 LinkedIn에서 개발한 분산 스트리밍 플랫폼입니다.

**핵심 특징:**
1. **대용량 처리**: 초당 수백만 건의 이벤트 처리
2. **영속성**: 디스크에 메시지 저장 (재처리 가능)
3. **확장성**: 수평적 확장 용이 (브로커 추가)
4. **고가용성**: 복제(Replication)를 통한 장애 대응
5. **순서 보장**: 파티션 내에서 메시지 순서 유지

### 왜 Kafka를 사용하는가?

**1. 시스템 간 결합도 감소**
```
기존:
[주문 서비스] → [재고 서비스]
             → [알림 서비스]
             → [분석 서비스]
(직접 연결, 강한 결합)

Kafka 도입:
[주문 서비스] → [Kafka] → [재고 서비스]
                       → [알림 서비스]
                       → [분석 서비스]
(느슨한 결합, 확장 용이)
```

**2. 데이터 파이프라인**
- 여러 소스에서 데이터 수집
- 중앙 집중식 데이터 허브
- 다양한 목적지로 전송

**3. 이벤트 소싱**
- 모든 상태 변경을 이벤트로 저장
- 과거 이벤트 재처리 가능
- 시계열 데이터 분석

### Redis Pub/Sub vs Kafka

| 항목 | Redis Pub/Sub | Kafka |
|------|--------------|-------|
| **메시지 저장** | ❌ 저장 안 됨 | ✅ 디스크 저장 |
| **재처리** | ❌ 불가능 | ✅ 가능 (오프셋) |
| **처리량** | 중간 | 매우 높음 |
| **지연시간** | 매우 낮음 (ms) | 낮음 (수십 ms) |
| **확장성** | 제한적 | 매우 높음 |
| **사용 사례** | 실시간 알림, 캐싱 | 데이터 파이프라인, MSA 이벤트 |

→ **Redis**: 빠르고 간단한 실시간 알림  
→ **Kafka**: 안정적이고 대용량 이벤트 스트리밍

## 핵심 개념

### 1. Producer (생산자)
메시지를 Kafka에 발행하는 애플리케이션
```
주문 서비스 → Kafka Topic "orders"
```

### 2. Consumer (소비자)
Kafka에서 메시지를 읽는 애플리케이션
```
Kafka Topic "orders" → 재고 서비스
                     → 알림 서비스
```

### 3. Topic (토픽)
메시지를 분류하는 카테고리 (데이터베이스의 테이블과 유사)
```
topics:
  - orders          # 주문 이벤트
  - user-activity   # 사용자 활동
  - payments        # 결제 이벤트
```

### 4. Partition (파티션)
토픽을 나눈 물리적 단위 (병렬 처리)
```
Topic "orders" → Partition 0
              → Partition 1
              → Partition 2
(각 파티션은 순서 보장)
```

### 5. Broker (브로커)
Kafka 서버 인스턴스 (여러 개로 클러스터 구성)
```
Kafka Cluster:
  - Broker 1
  - Broker 2
  - Broker 3
```

### 6. Consumer Group (컨슈머 그룹)
여러 컨슈머가 협력하여 메시지 처리
```
Topic "orders" (3개 파티션)
  → Consumer Group "inventory-service"
    - Consumer 1 → Partition 0
    - Consumer 2 → Partition 1
    - Consumer 3 → Partition 2
(각 파티션은 그룹 내 하나의 컨슈머만 처리)
```

## 실무 사용 사례

### 1. MSA 이벤트 기반 아키텍처
```java
// 주문 생성 이벤트 발행
@Service
public class OrderService {
    
    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    @Transactional
    public Order createOrder(OrderDto dto) {
        // 1. DB에 주문 저장
        Order order = orderRepository.save(new Order(dto));
        
        // 2. Kafka에 이벤트 발행
        OrderEvent event = OrderEvent.builder()
            .orderId(order.getId())
            .userId(order.getUserId())
            .products(order.getProducts())
            .totalAmount(order.getTotalAmount())
            .timestamp(LocalDateTime.now())
            .build();
        
        kafkaTemplate.send("orders", order.getId().toString(), event);
        
        return order;
    }
}

// 재고 서비스에서 이벤트 소비
@Service
public class InventoryService {
    
    @KafkaListener(topics = "orders", groupId = "inventory-service")
    public void handleOrderCreated(OrderEvent event) {
        log.info("주문 이벤트 수신: {}", event.getOrderId());
        
        // 재고 차감
        for (Product product : event.getProducts()) {
            inventoryRepository.decreaseStock(product.getId(), product.getQuantity());
        }
    }
}

// 알림 서비스에서 동일 이벤트 소비
@Service
public class NotificationService {
    
    @KafkaListener(topics = "orders", groupId = "notification-service")
    public void handleOrderCreated(OrderEvent event) {
        // 주문 확인 알림 발송
        emailService.sendOrderConfirmation(event.getUserId(), event.getOrderId());
    }
}
```

### 2. 로그 수집 및 분석
```
애플리케이션 서버들 → Kafka Topic "logs"
                   → Elasticsearch (검색)
                   → S3 (장기 보관)
                   → 실시간 분석 시스템
```

### 3. 활동 추적 (Activity Tracking)
```
웹/앱 → Kafka Topic "user-activity"
    → 실시간 대시보드
    → 추천 시스템
    → 마케팅 분석
```

### 4. CDC (Change Data Capture)
```
MySQL → Debezium → Kafka → 검색 엔진 (Elasticsearch)
                        → 캐시 (Redis)
                        → 데이터 웨어하우스
```

## 간단한 예제

### Kafka 설치 (Docker)
```bash
# docker-compose.yml
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
  
  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

```bash
docker-compose up -d
```

### Kafka CLI 명령어
```bash
# 토픽 생성
kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --partitions 3 \
  --replication-factor 1

# 토픽 목록 조회
kafka-topics --list --bootstrap-server localhost:9092

# 메시지 발행 (Producer)
kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic orders

# 메시지 소비 (Consumer)
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --from-beginning

# 컨슈머 그룹 확인
kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --list
```

## 주요 특징 상세

### 1. 영속성 (Persistence)
- 메시지를 디스크에 저장
- 재시작해도 데이터 유지
- 설정된 보관 기간 동안 보존 (기본 7일)

### 2. 확장성 (Scalability)
```
파티션 추가 → 병렬 처리 증가
브로커 추가 → 처리량 증가
```

### 3. 복제 (Replication)
- 각 파티션을 여러 브로커에 복제
- Leader와 Follower 구조
- 장애 발생 시 자동 failover

### 4. 순서 보장
- **파티션 내에서만** 순서 보장
- 같은 키를 가진 메시지는 같은 파티션으로

## 주의사항 / 함정

### 1. 순서 보장 범위
❌ **오해**: Kafka는 모든 메시지의 순서를 보장한다
✅ **진실**: 같은 파티션 내에서만 순서 보장
```
Partition 0: [msg1, msg2, msg3] (순서 보장)
Partition 1: [msg4, msg5, msg6] (순서 보장)
전체 순서: msg1, msg4, msg2, msg5... (순서 보장 안 됨)
```

### 2. 메시지 손실 vs 중복
- **최소 한 번 (at-least-once)**: 중복 가능, 손실 없음 (기본)
- **최대 한 번 (at-most-once)**: 손실 가능, 중복 없음
- **정확히 한 번 (exactly-once)**: 손실/중복 없음 (복잡, 성능 저하)

### 3. Consumer Lag (지연)
- Producer가 메시지를 빠르게 생산
- Consumer가 처리 속도 느림
- 백로그 증가 → 모니터링 필요

### 4. 파티션 수 설정
```java
// ❌ 나쁜 예: 파티션 1개 → 병렬 처리 불가
// ✅ 좋은 예: 파티션 3개 이상 → 병렬 처리 가능
```

## Kafka가 적합한 경우 / 부적합한 경우

### ✅ 적합한 경우
- 대용량 이벤트 스트리밍
- 여러 시스템 간 데이터 파이프라인
- MSA 이벤트 기반 아키텍처
- 로그 수집 및 분석
- 재처리가 필요한 경우

### ❌ 부적합한 경우
- 실시간성이 극도로 중요 (밀리초 이하)
- 메시지 양이 적음 (수천 건/일)
- 간단한 Pub/Sub (Redis로 충분)
- RPC 스타일 통신 (gRPC, REST가 나음)

## 관련 개념
- [[Kafka-아키텍처]] - Broker, Partition, Replica
- [[Kafka-Producer-Consumer]] - 메시지 발행/구독
- [[Kafka-성능과운영]] - 성능 최적화, 모니터링
- [[Kafka-Spring통합]] - Spring Kafka 사용법
- [[Redis-PubSub과트랜잭션]] - Redis Pub/Sub 비교
- [[MSA-이벤트기반아키텍처]] - 이벤트 소싱, CQRS

## 면접 질문

1. **Kafka가 무엇이며, 왜 사용하나요?**
   - 분산 이벤트 스트리밍 플랫폼
   - 대용량 실시간 데이터 파이프라인 구축
   - MSA에서 서비스 간 느슨한 결합

2. **Kafka와 RabbitMQ의 차이는?**
   - Kafka: 이벤트 스트리밍, 높은 처리량, 영속성
   - RabbitMQ: 전통적 메시지 큐, 복잡한 라우팅

3. **Kafka가 Redis Pub/Sub보다 나은 점은?**
   - 메시지 영속성 (디스크 저장)
   - 재처리 가능 (오프셋)
   - 높은 처리량과 확장성

4. **Kafka의 순서 보장은 어떻게 되나요?**
   - 같은 파티션 내에서만 순서 보장
   - 파티션 간에는 순서 보장 안 됨
   - 같은 키는 같은 파티션으로 전송

5. **Kafka는 어떤 경우에 사용하면 좋나요?**
   - MSA 이벤트 기반 통신
   - 대용량 로그 수집
   - 실시간 데이터 파이프라인
   - 이벤트 소싱

6. **프로젝트에서 Kafka를 어떻게 활용할 수 있나요? (예시)**
   - 주문 생성 이벤트를 Kafka로 발행
   - 재고 서비스, 알림 서비스가 독립적으로 소비
   - 각 서비스는 느슨하게 결합

## 참고 자료
- [Kafka 공식 문서](https://kafka.apache.org/documentation/)
- [Confluent Kafka Documentation](https://docs.confluent.io/)
- [Introduction to Apache Kafka](https://kafka.apache.org/intro)
- [Kafka: The Definitive Guide (책)](https://www.confluent.io/resources/kafka-the-definitive-guide/)
