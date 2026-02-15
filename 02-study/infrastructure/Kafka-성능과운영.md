---
tags:
  - study
  - kafka
  - performance
  - monitoring
  - ops
created: 2026-02-15
---

# Kafka 성능과 운영

## 한 줄 요약
> Kafka 성능 최적화는 파티션 전략, 배치 처리, 압축, 메모리 조정으로 이루어지며, Consumer Lag, JMX 메트릭, 로그 모니터링을 통해 안정적인 운영이 가능하다.

## 상세 설명

### 성능과 운영이 중요한 이유
- **대용량 데이터**: 초당 수백만 건 처리 필요
- **실시간성**: 지연 시간 최소화
- **안정성**: 24/7 무중단 운영
- **비용 절감**: 리소스 효율적 사용

## 1. 성능 최적화

### 파티션 전략

**적절한 파티션 수 결정:**
```
파티션 수 = Max(
    예상 처리량 / Consumer 처리 능력,
    Consumer 수
)
```

**예시:**
```
목표 처리량: 100,000 msg/s
Consumer 처리 능력: 10,000 msg/s
→ 최소 10개 파티션 필요

실제: 10~15개 권장 (여유 고려)
```

**파티션 수에 따른 영향:**
| 파티션 수 | 장점 | 단점 |
|---------|------|------|
| 적음 (1~3) | 순서 보장 쉬움 | 병렬 처리 제한 |
| 적당 (3~10) | 균형 잡힘 | - |
| 많음 (50+) | 높은 처리량 | 메타데이터 부담, Rebalancing 느림 |

### Producer 성능 최적화

**1. 배치 처리 (Batching)**
```java
@Bean
public ProducerFactory<String, OrderEvent> producerFactory() {
    Map<String, Object> config = new HashMap<>();
    
    // 배치 크기 (기본 16KB)
    config.put(ProducerConfig.BATCH_SIZE_CONFIG, 32768);  // 32KB
    
    // 배치 대기 시간 (기본 0ms)
    config.put(ProducerConfig.LINGER_MS_CONFIG, 10);  // 10ms
    
    // 버퍼 메모리 (기본 32MB)
    config.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 67108864);  // 64MB
    
    return new DefaultKafkaProducerFactory<>(config);
}
```

**배치 효과:**
```
배치 없음: 1000개 메시지 = 1000번 네트워크 호출
배치 있음: 1000개 메시지 = 10번 네트워크 호출 (100배 개선)
```

**2. 압축 (Compression)**
```java
config.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "snappy");
```

| 압축 타입 | 압축률 | CPU 사용 | 속도 | 용도 |
|---------|-------|---------|-----|------|
| **none** | 0% | 낮음 | 빠름 | 작은 메시지 |
| **gzip** | 높음 | 높음 | 느림 | 네트워크 비용 절감 |
| **snappy** | 중간 | 낮음 | 빠름 | **권장** |
| **lz4** | 중간 | 낮음 | 매우 빠름 | 고성능 |
| **zstd** | 매우 높음 | 중간 | 중간 | Kafka 2.1+ |

**3. 비동기 전송**
```java
// ❌ 동기 전송 (느림)
kafkaTemplate.send(topic, event).get();  // 블로킹

// ✅ 비동기 전송 (빠름)
kafkaTemplate.send(topic, event).addCallback(
    result -> log.info("성공"),
    ex -> log.error("실패")
);
```

**4. 파티셔닝 최적화**
```java
// 커스텀 파티셔너로 핫스팟 방지
public class CustomPartitioner implements Partitioner {
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        
        // VIP 고객은 전용 파티션
        if (isVIP(key)) {
            return 0;
        }
        
        // 나머지는 균등 분산
        return Math.abs(key.hashCode()) % (cluster.partitionCountForTopic(topic) - 1) + 1;
    }
}
```

### Consumer 성능 최적화

**1. 병렬 처리**
```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> 
        kafkaListenerContainerFactory() {
    
    ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory = 
        new ConcurrentKafkaListenerContainerFactory<>();
    
    factory.setConsumerFactory(consumerFactory());
    
    // 동시 실행 스레드 수
    factory.setConcurrency(3);  // Partition 수와 같거나 작게
    
    return factory;
}
```

**2. 배치 소비**
```java
@Bean
public ConsumerFactory<String, OrderEvent> batchConsumerFactory() {
    Map<String, Object> config = new HashMap<>();
    
    // 한 번에 가져올 레코드 수 (기본 500)
    config.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 1000);
    
    // Fetch 크기 (기본 50MB)
    config.put(ConsumerConfig.FETCH_MAX_BYTES_CONFIG, 52428800);
    
    return new DefaultKafkaConsumerFactory<>(config);
}

@KafkaListener(topics = "orders", 
               groupId = "batch-service",
               containerFactory = "batchListenerFactory")
public void consumeBatch(List<OrderEvent> events) {
    // 1000개씩 배치 처리
    orderRepository.batchInsert(events);
}
```

**3. 세션 타임아웃 조정**
```java
config.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 30000);  // 30초
config.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, 3000);  // 3초
config.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 300000);  // 5분
```

**4. 파티션 할당 전략**
```java
// Range (기본): 파티션을 범위로 나눔
config.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG, 
    RangeAssignor.class.getName());

// RoundRobin: 균등 분배
config.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG, 
    RoundRobinAssignor.class.getName());

// Sticky: Rebalancing 시 기존 할당 유지 (권장)
config.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG, 
    StickyAssignor.class.getName());
```

### Broker 성능 최적화

**1. 메모리 설정**
```bash
# JVM 힙 메모리 (Broker)
export KAFKA_HEAP_OPTS="-Xmx4G -Xms4G"

# 페이지 캐시 (OS 레벨)
# Kafka는 디스크 I/O를 OS 페이지 캐시에 의존
# 전체 메모리의 50~70%를 페이지 캐시로 사용
```

**2. 로그 세그먼트 설정**
```properties
# server.properties

# 세그먼트 크기 (기본 1GB)
log.segment.bytes=1073741824

# 세그먼트 롤링 시간 (기본 7일)
log.roll.hours=168

# 로그 보관 기간 (기본 7일)
log.retention.hours=168

# 압축 활성화
log.cleanup.policy=delete  # 또는 compact

# 복제 설정
default.replication.factor=3
min.insync.replicas=2  # ACK=all 시 최소 복제본 수
```

**3. 네트워크 설정**
```properties
# 네트워크 스레드 수 (CPU 코어 수)
num.network.threads=8

# I/O 스레드 수 (디스크 수)
num.io.threads=8

# 소켓 버퍼 크기
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
```

## 2. 모니터링

### 주요 모니터링 지표

**1. Consumer Lag (가장 중요)**
```
Lag = Latest Offset - Current Offset

예시:
  Latest Offset: 10000
  Current Offset: 9500
  → Lag: 500 (500개 메시지 밀림)
```

**Consumer Lag 확인:**
```bash
# CLI로 확인
kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group order-service

# 출력:
# TOPIC    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# orders   0          5000            5100            100
# orders   1          4800            4800            0
# orders   2          4900            5200            300
```

**Spring Actuator로 확인:**
```java
@Component
public class KafkaLagMonitor {
    
    private final AdminClient adminClient;
    
    @Scheduled(fixedRate = 60000)  // 1분마다
    public void monitorLag() {
        Map<TopicPartition, Long> endOffsets = /* ... */;
        Map<TopicPartition, Long> currentOffsets = /* ... */;
        
        for (TopicPartition tp : endOffsets.keySet()) {
            long lag = endOffsets.get(tp) - currentOffsets.get(tp);
            
            if (lag > 1000) {
                alertService.sendAlert("높은 Consumer Lag: " + tp + ", Lag: " + lag);
            }
            
            // Prometheus 메트릭 등록
            meterRegistry.gauge("kafka.consumer.lag", lag);
        }
    }
}
```

**2. Throughput (처리량)**
```
- Producer: messages/sec, bytes/sec
- Consumer: records consumed/sec
- Broker: bytes in/out per second
```

**3. Latency (지연 시간)**
```
- Producer: send latency
- Consumer: fetch latency
- End-to-end: Producer → Broker → Consumer
```

**4. Broker 메트릭**
```
- CPU 사용률
- 메모리 사용률
- 디스크 I/O
- 네트워크 I/O
- Active Controller (1개여야 함)
- Under-Replicated Partitions (0이어야 함)
```

### JMX 메트릭 수집

**Prometheus + Grafana 구성:**
```yaml
# docker-compose.yml
version: '3'
services:
  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_JMX_PORT: 9999
      KAFKA_JMX_HOSTNAME: localhost
  
  jmx-exporter:
    image: sscaling/jmx-prometheus-exporter
    ports:
      - "8080:8080"
    volumes:
      - ./jmx-exporter-config.yml:/config.yml
  
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### 로그 모니터링

**중요 로그 위치:**
```bash
# Kafka 서버 로그
/var/log/kafka/server.log

# Controller 로그
/var/log/kafka/controller.log

# 파티션 상태 로그
/var/log/kafka/state-change.log
```

**중요 에러 패턴:**
```
- "Leader not available": Leader 선출 중
- "Not enough replicas": ISR 부족
- "Offset out of range": Consumer offset 문제
- "Connection refused": 네트워크 문제
```

## 3. 운영 Best Practices

### Topic 설계

**1. 네이밍 컨벤션**
```
<환경>.<도메인>.<이벤트타입>

예시:
  prod.order.created
  prod.order.cancelled
  prod.payment.completed
  dev.user.registered
```

**2. 파티션 수 결정**
```java
// 초기 설정 시 여유있게 (나중에 늘리기는 쉬움)
int partitions = Math.max(
    expectedThroughput / consumerThroughput,
    consumerCount
) * 2;  // 2배 여유

// 예시: 100K msg/s, Consumer 10K msg/s → 10 * 2 = 20 partitions
```

**3. Replication Factor**
```
- 개발 환경: 1 (단일 브로커 가능)
- 스테이징: 2
- 프로덕션: 3 (권장)
```

### 데이터 보관 정책

**1. 시간 기반 보관**
```properties
log.retention.hours=168  # 7일
```

**2. 크기 기반 보관**
```properties
log.retention.bytes=10737418240  # 10GB
```

**3. Compacted Log (상태 저장)**
```properties
log.cleanup.policy=compact

# 최소 압축 비율
min.cleanable.dirty.ratio=0.5
```

### 장애 대응

**1. Broker 장애**
```
증상: Under-Replicated Partitions 증가
조치:
  1. Broker 재시작
  2. 로그 확인
  3. 디스크/메모리 체크
  4. 복구 안 되면 Broker 교체
```

**2. Consumer Lag 급증**
```
원인:
  - Consumer 처리 속도 느림
  - Rebalancing 빈번
  - 네트워크 문제

조치:
  1. Consumer 수 증가 (파티션 수 이하)
  2. 배치 처리 크기 조정
  3. 병렬 처리 스레드 증가
  4. 불필요한 로직 제거
```

**3. Rebalancing 빈번**
```
원인:
  - session.timeout.ms 짧음
  - max.poll.interval.ms 짧음
  - Consumer 처리 시간 김

조치:
  1. 타임아웃 증가
  2. max.poll.records 감소
  3. 처리 로직 최적화
```

### 보안 설정

**1. SSL/TLS 암호화**
```properties
listeners=SSL://localhost:9093
security.protocol=SSL
ssl.keystore.location=/path/to/keystore.jks
ssl.keystore.password=password
```

**2. SASL 인증**
```properties
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
```

**3. ACL (접근 제어)**
```bash
# Producer ACL
kafka-acls --add \
  --allow-principal User:producer-user \
  --operation Write \
  --topic orders

# Consumer ACL
kafka-acls --add \
  --allow-principal User:consumer-user \
  --operation Read \
  --topic orders \
  --group order-service
```

## 4. 성능 테스트

### Producer 성능 테스트
```bash
kafka-producer-perf-test \
  --topic test-topic \
  --num-records 1000000 \
  --record-size 1024 \
  --throughput -1 \
  --producer-props bootstrap.servers=localhost:9092
```

### Consumer 성능 테스트
```bash
kafka-consumer-perf-test \
  --bootstrap-server localhost:9092 \
  --topic test-topic \
  --messages 1000000
```

## 주의사항 / 함정

### 1. 파티션 수는 늘릴 수만 있음
- 감소 불가능
- 초기 설계 중요

### 2. Rebalancing 비용
- Consumer 수 ≤ Partition 수 유지
- 빈번한 Rebalancing은 성능 저하

### 3. 메모리 설정
```
JVM Heap + Page Cache = 전체 메모리
추천: Heap 4~6GB, 나머지 Page Cache
```

### 4. Consumer Lag 임계값
```
일반: Lag < 1000
경고: Lag > 1000
위험: Lag > 10000
```

## 관련 개념
- [[Kafka-기본개념]] - Kafka 개요
- [[Kafka-아키텍처]] - 내부 구조
- [[Kafka-Producer-Consumer]] - 메시지 발행/소비
- [[모니터링-Prometheus]] - 메트릭 수집
- [[성능최적화]] - 일반 성능 최적화

## 면접 질문

1. **Kafka 성능을 최적화하는 방법은?**
   - Producer: 배치 처리, 압축, 비동기 전송
   - Consumer: 병렬 처리, 배치 소비
   - Broker: 메모리/디스크 최적화, 파티션 설계

2. **Consumer Lag이 무엇이며, 왜 중요한가요?**
   - 처리해야 할 메시지 적체량
   - Lag 증가 → 실시간성 저하, 장애 신호

3. **Rebalancing을 최소화하는 방법은?**
   - 세션 타임아웃 증가
   - max.poll.interval 증가
   - Consumer 안정적 유지

4. **파티션 수를 결정하는 기준은?**
   - 예상 처리량 / Consumer 처리 능력
   - Consumer 수 이상 (병렬 처리)
   - 여유 고려 (2배 권장)

5. **Kafka 모니터링에서 가장 중요한 지표는?**
   - Consumer Lag (처리 지연)
   - Under-Replicated Partitions (복제 상태)
   - Throughput (처리량)

6. **프로덕션 Kafka 운영 시 주의사항은?**
   - Replication Factor 3 이상
   - 정기적인 Lag 모니터링
   - 로그 보관 정책 설정
   - 백업 및 장애 복구 계획

## 참고 자료
- [Kafka Performance Tuning](https://kafka.apache.org/documentation/#performance)
- [Kafka Monitoring](https://kafka.apache.org/documentation/#monitoring)
- [Confluent Monitoring Best Practices](https://docs.confluent.io/platform/current/kafka/monitoring.html)
- [LinkedIn Kafka Production Insights](https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines)
