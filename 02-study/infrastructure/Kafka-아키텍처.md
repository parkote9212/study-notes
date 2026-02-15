---
tags:
  - study
  - kafka
  - architecture
  - broker
  - partition
  - replica
created: 2026-02-15
---

# Kafka 아키텍처

## 한 줄 요약
> Kafka는 Broker 클러스터, Topic의 Partition, Leader-Follower Replica 구조로 고가용성과 확장성을 제공하며, Zookeeper를 통해 메타데이터를 관리한다.

## 상세 설명

### Kafka 전체 구조
```
┌─────────────────────────────────────────────────┐
│           Producer Applications                  │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────▼──────────┐
        │  Kafka Cluster      │
        │  ┌──────────────┐  │
        │  │  Broker 1    │  │
        │  │  Broker 2    │  │
        │  │  Broker 3    │  │
        │  └──────────────┘  │
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │  Zookeeper Cluster  │
        └────────────────────┘
                  │
        ┌─────────▼──────────┐
        │ Consumer Groups     │
        │  - Group A          │
        │  - Group B          │
        └────────────────────┘
```

## 1. Broker (브로커)

### Broker란?
- Kafka 서버 인스턴스
- 메시지 저장 및 관리
- 클러스터 구성 시 여러 브로커가 협력

### Broker의 역할
1. **메시지 저장**: 디스크에 영속적 저장
2. **Producer 요청 처리**: 메시지 수신 및 저장
3. **Consumer 요청 처리**: 메시지 전송
4. **복제 관리**: 파티션 복제본 관리

### Broker ID
```
Kafka Cluster:
  - Broker ID 1 (broker1.example.com:9092)
  - Broker ID 2 (broker2.example.com:9092)
  - Broker ID 3 (broker3.example.com:9092)
```

## 2. Topic과 Partition

### Topic (토픽)
메시지를 논리적으로 분류하는 단위
```
Topic "orders"
  └─ 주문 관련 모든 이벤트
```

### Partition (파티션)
Topic을 물리적으로 나눈 단위

**왜 파티션이 필요한가?**
1. **병렬 처리**: 여러 컨슈머가 동시에 처리
2. **확장성**: 파티션 추가로 처리량 증가
3. **순서 보장**: 파티션 내에서만 순서 유지

### 파티션 구조
```
Topic "orders" (3 Partitions)

Partition 0: [msg0, msg3, msg6, msg9...]  → Broker 1
Partition 1: [msg1, msg4, msg7, msg10...] → Broker 2
Partition 2: [msg2, msg5, msg8, msg11...] → Broker 3

각 파티션은 독립적인 로그 파일
```

### 파티션 할당 방식

**1. 키 기반 (Key-based)**
```java
// 같은 userId는 항상 같은 파티션으로
kafkaTemplate.send("orders", userId.toString(), orderEvent);

// 내부적으로: hash(key) % partition_count
```

**2. 라운드 로빈 (Round-robin)**
```java
// 키 없으면 순차적으로 분배
kafkaTemplate.send("orders", orderEvent);

// Partition 0 → 1 → 2 → 0 → 1 → 2...
```

**3. 커스텀 파티셔너**
```java
public class CustomPartitioner implements Partitioner {
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        // 비즈니스 로직에 따른 파티션 선택
        if (key.toString().startsWith("VIP")) {
            return 0;  // VIP 고객은 Partition 0
        }
        return Math.abs(key.hashCode()) % cluster.partitionCountForTopic(topic);
    }
}
```

## 3. Replication (복제)

### Replication Factor
각 파티션을 여러 브로커에 복제하여 고가용성 확보

```
Topic "orders", Partition 0, Replication Factor = 3

Broker 1: Partition 0 (Leader)   ← 읽기/쓰기 처리
Broker 2: Partition 0 (Follower) ← Leader 동기화
Broker 3: Partition 0 (Follower) ← Leader 동기화
```

### Leader와 Follower

**Leader:**
- 읽기/쓰기 요청 처리
- 각 파티션마다 하나의 Leader

**Follower:**
- Leader 복제
- Leader 장애 시 새로운 Leader로 선출됨
- 읽기 요청은 처리 안 함 (Leader만)

### ISR (In-Sync Replica)
- Leader와 동기화된 복제본 목록
- 장애 시 ISR에서 새 Leader 선출
```
Partition 0:
  Leader: Broker 1
  ISR: [Broker 1, Broker 2, Broker 3]  ← 모두 동기화됨
```

### Failover 과정
```
1. 초기 상태
   Leader: Broker 1
   ISR: [1, 2, 3]

2. Broker 1 장애 발생
   → Zookeeper가 감지

3. ISR에서 새 Leader 선출
   Leader: Broker 2 (새 Leader)
   ISR: [2, 3]

4. Broker 1 복구 후
   → Follower로 복귀
   → 데이터 동기화 후 ISR 재진입
```

## 4. Offset (오프셋)

### Offset이란?
파티션 내 메시지의 고유 번호 (0부터 시작, 순차 증가)

```
Partition 0:
  Offset 0: {"orderId": 1, ...}
  Offset 1: {"orderId": 2, ...}
  Offset 2: {"orderId": 3, ...}
  Offset 3: {"orderId": 4, ...}
  ...
```

### Consumer Offset
Consumer가 어디까지 읽었는지 기록

```
Topic "orders", Consumer Group "inventory-service"
  Partition 0: Offset 150  ← 151번째 메시지부터 읽음
  Partition 1: Offset 200
  Partition 2: Offset 175
```

### Offset 관리 방식

**1. 자동 커밋 (Auto Commit)**
```yaml
spring:
  kafka:
    consumer:
      enable-auto-commit: true
      auto-commit-interval: 5000  # 5초마다 자동 커밋
```

**2. 수동 커밋 (Manual Commit)**
```java
@KafkaListener(topics = "orders", groupId = "inventory-service")
public void consume(ConsumerRecord<String, OrderEvent> record,
                    Acknowledgment acknowledgment) {
    try {
        // 메시지 처리
        processOrder(record.value());
        
        // 처리 성공 시 수동 커밋
        acknowledgment.acknowledge();
    } catch (Exception e) {
        // 처리 실패 시 커밋하지 않음 → 재처리
        log.error("처리 실패: {}", record.offset(), e);
    }
}
```

## 5. Segment (세그먼트)

### Segment란?
파티션의 물리적 로그 파일 단위

```
Partition 0 Directory:
  00000000000000000000.log  ← Segment 1 (Offset 0~999)
  00000000000000001000.log  ← Segment 2 (Offset 1000~1999)
  00000000000000002000.log  ← Segment 3 (Offset 2000~...)
```

### Segment 설정
```properties
# 1GB마다 새 세그먼트 생성
log.segment.bytes=1073741824

# 7일 지난 세그먼트 삭제
log.retention.hours=168

# 압축 활성화
log.cleanup.policy=delete  # 또는 compact
```

### Log Compaction
같은 키의 최신 값만 유지 (CDC, 상태 저장에 유용)
```
Before Compaction:
  key=user1, value={"name": "Alice", "age": 25}
  key=user1, value={"name": "Alice", "age": 26}
  key=user1, value={"name": "Alice", "age": 27}

After Compaction:
  key=user1, value={"name": "Alice", "age": 27}  ← 최신 값만 유지
```

## 6. Zookeeper의 역할

### Zookeeper가 관리하는 정보
1. **Broker 목록**: 클러스터 내 살아있는 브로커
2. **Leader 선출**: 파티션 Leader 결정
3. **Consumer Group 관리**: 오프셋 저장 (구버전)
4. **Topic 설정**: 파티션 수, 복제 계수

### KRaft 모드 (Kafka 3.0+)
Zookeeper 없이 Kafka 자체 메타데이터 관리
```
기존: Kafka + Zookeeper
신규: Kafka 단독 (KRaft)
```

**KRaft 장점:**
- 아키텍처 단순화
- 메타데이터 처리 속도 향상
- 수십만 개 파티션 지원

## 7. Consumer Group

### Consumer Group이란?
여러 Consumer가 협력하여 메시지 소비

### 파티션 할당
```
Topic "orders" (3 Partitions)

Consumer Group "service-a" (2 consumers)
  Consumer 1 → Partition 0, 1
  Consumer 2 → Partition 2

Consumer Group "service-b" (3 consumers)
  Consumer 1 → Partition 0
  Consumer 2 → Partition 1
  Consumer 3 → Partition 2
```

**규칙:**
- 각 파티션은 그룹 내 하나의 컨슈머에만 할당
- 컨슈머 수 > 파티션 수 → 일부 컨슈머는 유휴 상태
- 컨슈머 수 < 파티션 수 → 일부 컨슈머가 여러 파티션 처리

### Rebalancing (리밸런싱)
컨슈머 추가/제거 시 파티션 재할당

```
초기:
  Consumer 1 → Partition 0, 1, 2

Consumer 2 추가:
  Consumer 1 → Partition 0, 1
  Consumer 2 → Partition 2

Consumer 1 장애:
  Consumer 2 → Partition 0, 1, 2
```

## 실무 설계 예시

### 주문 시스템 Kafka 구성
```yaml
Topic: orders
  Partitions: 6
  Replication Factor: 3
  Retention: 7 days

Partition 할당 전략:
  - 키: userId
  - 이유: 같은 사용자의 주문은 순서 보장 필요

Consumer Groups:
  - inventory-service (3 consumers)
  - notification-service (2 consumers)
  - analytics-service (1 consumer)

Broker 구성:
  - 3개 브로커 (고가용성)
  - 각 브로커 500GB SSD
```

## 주의사항 / 함정

### 1. 파티션 수 설정
❌ **너무 적음**: 병렬 처리 제한
❌ **너무 많음**: 메타데이터 부담, 리밸런싱 느림
✅ **적정**: 처리량과 컨슈머 수 고려 (초기 3~10개)

### 2. Replication Factor
❌ **1**: 장애 시 데이터 손실
✅ **3**: 일반적 (2개 브로커 장애까지 견딤)
❌ **5+**: 과도한 복제 비용

### 3. 파티션 추가는 가능, 삭제는 불가
```bash
# 파티션 추가 (3 → 6)
kafka-topics --alter --topic orders --partitions 6

# 파티션 감소는 불가능!
```

### 4. 메시지 순서 보장 범위
- **같은 파티션**: 순서 보장
- **다른 파티션**: 순서 보장 안 됨
- **같은 키**: 같은 파티션 → 순서 보장

## 관련 개념
- [[Kafka-기본개념]] - Kafka 개요
- [[Kafka-Producer-Consumer]] - 메시지 발행/소비
- [[Kafka-성능과운영]] - 최적화, 모니터링
- [[분산시스템-CAP이론]] - 일관성, 가용성
- [[데이터베이스-샤딩]] - 파티셔닝 개념

## 면접 질문

1. **Kafka의 파티션이 무엇이며, 왜 필요한가요?**
   - Topic을 물리적으로 나눈 단위
   - 병렬 처리, 확장성, 순서 보장

2. **Leader와 Follower의 역할을 설명하세요.**
   - Leader: 읽기/쓰기 처리
   - Follower: Leader 복제, 장애 시 Leader로 승격

3. **ISR이 무엇이며, 왜 중요한가요?**
   - In-Sync Replica, Leader와 동기화된 복제본
   - 장애 시 ISR에서 새 Leader 선출
   - 데이터 일관성 보장

4. **파티션 수를 늘릴 수 있지만, 줄일 수 없는 이유는?**
   - 기존 메시지의 파티션 재분배 불가능
   - 순서 보장 깨짐
   - 오프셋 불일치

5. **Consumer Group에서 컨슈머가 파티션보다 많으면 어떻게 되나요?**
   - 일부 컨슈머는 파티션 할당 안 됨
   - 유휴 상태로 대기
   - 파티션 수만큼만 병렬 처리 가능

6. **Rebalancing이 언제 발생하나요?**
   - 컨슈머 추가/제거
   - 컨슈머 장애
   - 파티션 추가
   - 일시적으로 메시지 처리 중단 (주의)

7. **Kafka는 순서 보장을 어떻게 하나요?**
   - 파티션 내에서만 순서 보장
   - 같은 키는 같은 파티션
   - 전체 순서는 보장 안 됨

## 참고 자료
- [Kafka Architecture](https://kafka.apache.org/documentation/#design)
- [Kafka Internals](https://kafka.apache.org/documentation/#implementation)
- [Understanding Kafka Partitions](https://www.confluent.io/blog/apache-kafka-partitions/)
- [Kafka Replication](https://www.confluent.io/blog/hands-free-kafka-replication/)
