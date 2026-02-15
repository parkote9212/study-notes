---
tags:
  - study
  - redis
  - pubsub
  - transaction
  - messaging
created: 2026-02-15
---

# Redis PubSub과 트랜잭션

## 한 줄 요약
> Redis Pub/Sub은 실시간 메시징을 위한 경량 메시지 브로커이며, 트랜잭션(MULTI/EXEC)은 여러 명령어를 원자적으로 실행하여 데이터 일관성을 보장한다.

## 상세 설명

### Pub/Sub과 트랜잭션이 필요한 이유

**Pub/Sub:**
- 실시간 알림, 채팅, 이벤트 브로드캐스팅
- 서버 간 메시지 전달 (MSA 환경)
- 가볍고 빠른 메시징

**트랜잭션:**
- 여러 작업의 원자성 보장
- Race Condition 방지
- 데이터 일관성 유지

## 1. Redis Pub/Sub (메시징)

### 동작 방식
```
Publisher → Redis Channel → Subscribers (1:N)
          "notification"     [Server1, Server2, Server3]
```

### 특징
✅ **경량**: Kafka처럼 무겁지 않음  
✅ **빠름**: 메모리 기반  
✅ **간단**: 설정 없이 즉시 사용  
❌ **메시지 보장 없음**: 구독자가 없으면 메시지 손실  
❌ **영속성 없음**: 메시지 저장 안 됨  
❌ **재전송 없음**: 한 번 전송되면 끝

### 주요 명령어
```bash
# 구독 (Subscriber)
SUBSCRIBE channel1 channel2   # 채널 구독
PSUBSCRIBE news.*            # 패턴 매칭 구독

# 발행 (Publisher)
PUBLISH channel1 "message"   # 메시지 발행, 구독자 수 반환

# 구독 해제
UNSUBSCRIBE channel1
PUNSUBSCRIBE news.*

# 활성 채널 확인
PUBSUB CHANNELS              # 모든 채널
PUBSUB NUMSUB channel1       # 채널별 구독자 수
```

### 실무 코드 예시: 실시간 알림 시스템

**Publisher (알림 발송)**
```java
@Service
public class NotificationPublisher {
    
    private final RedisTemplate<String, String> redisTemplate;
    
    public void sendNotification(String userId, String message) {
        String channel = "notification:" + userId;
        
        // JSON 형태로 메시지 발행
        NotificationDto notification = NotificationDto.builder()
            .userId(userId)
            .message(message)
            .timestamp(LocalDateTime.now())
            .build();
        
        String jsonMessage = new ObjectMapper().writeValueAsString(notification);
        
        // 메시지 발행
        redisTemplate.convertAndSend(channel, jsonMessage);
        
        log.info("알림 발송: {}", channel);
    }
    
    // 전체 사용자에게 브로드캐스트
    public void broadcast(String message) {
        redisTemplate.convertAndSend("notification:all", message);
    }
}
```

**Subscriber (알림 수신)**
```java
@Configuration
public class RedisConfig {
    
    @Bean
    public RedisMessageListenerContainer messageListenerContainer(
            RedisConnectionFactory connectionFactory,
            MessageListenerAdapter listenerAdapter) {
        
        RedisMessageListenerContainer container = new RedisMessageListenerContainer();
        container.setConnectionFactory(connectionFactory);
        
        // 패턴 매칭으로 모든 notification 채널 구독
        container.addMessageListener(listenerAdapter, 
            new PatternTopic("notification:*"));
        
        return container;
    }
    
    @Bean
    public MessageListenerAdapter listenerAdapter(NotificationSubscriber subscriber) {
        return new MessageListenerAdapter(subscriber, "onMessage");
    }
}

@Component
public class NotificationSubscriber {
    
    public void onMessage(String message, String channel) {
        log.info("메시지 수신 - 채널: {}, 메시지: {}", channel, message);
        
        // 메시지 처리 (WebSocket으로 클라이언트에 전송 등)
        try {
            NotificationDto notification = 
                new ObjectMapper().readValue(message, NotificationDto.class);
            
            // WebSocket으로 클라이언트에 전송
            webSocketService.sendToUser(notification.getUserId(), notification);
            
        } catch (Exception e) {
            log.error("메시지 파싱 실패: {}", message, e);
        }
    }
}
```

### 실무 적용 예시: 분산 환경에서 캐시 무효화

**문제 상황:**
```
Server 1: 상품 가격 변경 → DB 업데이트 → 로컬 캐시 삭제
Server 2: 여전히 오래된 캐시 보유 → 오래된 가격 반환 (문제!)
```

**해결: Pub/Sub으로 모든 서버에 캐시 무효화 알림**
```java
@Service
public class ProductService {
    
    private final ProductRepository productRepository;
    private final RedisTemplate<String, String> redisTemplate;
    private final ConcurrentHashMap<Long, Product> localCache = new ConcurrentHashMap<>();
    
    @Transactional
    public void updateProduct(Long productId, ProductDto dto) {
        // 1. DB 업데이트
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new NotFoundException("상품 없음"));
        product.update(dto);
        productRepository.save(product);
        
        // 2. Redis 캐시 삭제
        redisTemplate.delete("product:" + productId);
        
        // 3. 로컬 캐시 삭제
        localCache.remove(productId);
        
        // 4. 다른 서버들에게 캐시 무효화 알림
        redisTemplate.convertAndSend("cache:invalidate", 
            "product:" + productId);
    }
}

@Component
public class CacheInvalidationSubscriber {
    
    private final ConcurrentHashMap<Long, Product> localCache;
    
    public void onMessage(String cacheKey, String channel) {
        log.info("캐시 무효화 수신: {}", cacheKey);
        
        if (cacheKey.startsWith("product:")) {
            Long productId = Long.parseLong(cacheKey.split(":")[1]);
            localCache.remove(productId);
        }
    }
}
```

### BizSync 프로젝트 적용 예시: 실시간 협업 알림
```java
@Service
public class CollaborationNotifier {
    
    private final RedisTemplate<String, String> redisTemplate;
    
    // 문서 편집 알림
    public void notifyDocumentEdit(Long documentId, String editorName, String content) {
        String channel = "document:" + documentId;
        
        EditEventDto event = EditEventDto.builder()
            .documentId(documentId)
            .editorName(editorName)
            .content(content)
            .timestamp(System.currentTimeMillis())
            .build();
        
        redisTemplate.convertAndSend(channel, 
            new ObjectMapper().writeValueAsString(event));
    }
    
    // 새 댓글 알림
    public void notifyNewComment(Long documentId, CommentDto comment) {
        String channel = "document:" + documentId + ":comments";
        redisTemplate.convertAndSend(channel, 
            new ObjectMapper().writeValueAsString(comment));
    }
}
```

## 2. Redis 트랜잭션

### 트랜잭션이 필요한 이유
Redis는 단일 스레드지만, **네트워크 요청은 동시에 들어옴**
```
User A: GET balance (100)
User B: GET balance (100)
User A: SET balance 80   (100 - 20)
User B: SET balance 90   (100 - 10)
→ 최종 balance: 90 (잘못됨! 70이어야 함)
```

### MULTI/EXEC (트랜잭션)

```bash
MULTI                    # 트랜잭션 시작
SET key1 "value1"        # 명령어 큐잉
INCR counter             # 명령어 큐잉
EXPIRE key1 60           # 명령어 큐잉
EXEC                     # 일괄 실행 (원자성 보장)
```

### 특징
✅ **원자성**: 모두 성공 or 모두 실패  
✅ **격리성**: 다른 클라이언트의 명령어 끼어들지 못함  
❌ **롤백 없음**: 중간 실패해도 이전 명령은 유지 (주의!)

### WATCH (낙관적 락)
```bash
WATCH balance            # balance 키 감시
MULTI
DECRBY balance 20
EXEC                     # balance가 변경됐으면 실패 (nil 반환)
```

### 실무 코드 예시: 잔액 차감 (동시성 제어)

**방법 1: WATCH 사용 (낙관적 락)**
```java
@Service
public class BalanceService {
    
    private final RedisTemplate<String, String> redisTemplate;
    
    public boolean deductBalance(String userId, int amount) {
        String key = "balance:" + userId;
        
        // 최대 3번 재시도
        for (int i = 0; i < 3; i++) {
            try {
                // WATCH로 키 감시
                redisTemplate.watch(key);
                
                String balanceStr = redisTemplate.opsForValue().get(key);
                int currentBalance = balanceStr != null ? Integer.parseInt(balanceStr) : 0;
                
                // 잔액 부족
                if (currentBalance < amount) {
                    redisTemplate.unwatch();
                    return false;
                }
                
                // 트랜잭션 시작
                redisTemplate.multi();
                redisTemplate.opsForValue().set(key, 
                    String.valueOf(currentBalance - amount));
                
                // 실행 (다른 클라이언트가 변경했으면 null 반환)
                List<Object> result = redisTemplate.exec();
                
                if (result != null && !result.isEmpty()) {
                    return true; // 성공
                }
                
                // 실패 → 재시도
                log.warn("트랜잭션 충돌 재시도: {}", i + 1);
                
            } catch (Exception e) {
                redisTemplate.unwatch();
                throw e;
            }
        }
        
        throw new ConcurrencyException("동시성 처리 실패");
    }
}
```

**방법 2: Lua 스크립트 사용 (권장)**
```java
@Service
public class BalanceService {
    
    private final RedisTemplate<String, String> redisTemplate;
    
    // Lua 스크립트는 원자적으로 실행됨
    private static final String LUA_SCRIPT = 
        "local balance = tonumber(redis.call('GET', KEYS[1]) or '0') " +
        "if balance >= tonumber(ARGV[1]) then " +
        "  redis.call('DECRBY', KEYS[1], ARGV[1]) " +
        "  return 1 " +
        "else " +
        "  return 0 " +
        "end";
    
    public boolean deductBalance(String userId, int amount) {
        String key = "balance:" + userId;
        
        DefaultRedisScript<Long> script = new DefaultRedisScript<>();
        script.setScriptText(LUA_SCRIPT);
        script.setResultType(Long.class);
        
        Long result = redisTemplate.execute(script, 
            Collections.singletonList(key), 
            String.valueOf(amount));
        
        return result != null && result == 1;
    }
}
```

### 재고 차감 (동시성 제어)
```java
@Service
public class InventoryService {
    
    private final RedisTemplate<String, String> redisTemplate;
    
    // Lua 스크립트로 재고 차감
    private static final String DEDUCT_STOCK_SCRIPT = 
        "local stock = tonumber(redis.call('GET', KEYS[1]) or '0') " +
        "if stock >= tonumber(ARGV[1]) then " +
        "  redis.call('DECRBY', KEYS[1], ARGV[1]) " +
        "  return stock - tonumber(ARGV[1]) " +  // 남은 재고 반환
        "else " +
        "  return -1 " +  // 재고 부족
        "end";
    
    public int deductStock(Long productId, int quantity) {
        String key = "stock:" + productId;
        
        DefaultRedisScript<Long> script = new DefaultRedisScript<>();
        script.setScriptText(DEDUCT_STOCK_SCRIPT);
        script.setResultType(Long.class);
        
        Long remainingStock = redisTemplate.execute(script, 
            Collections.singletonList(key), 
            String.valueOf(quantity));
        
        if (remainingStock == null || remainingStock < 0) {
            throw new OutOfStockException("재고 부족");
        }
        
        return remainingStock.intValue();
    }
}
```

### Pipeline (성능 최적화)
트랜잭션과 다르지만, 여러 명령어를 한 번에 전송하여 네트워크 오버헤드 감소

```java
@Service
public class BatchService {
    
    private final RedisTemplate<String, String> redisTemplate;
    
    public void batchInsert(Map<String, String> data) {
        // Pipeline 사용
        redisTemplate.executePipelined(new SessionCallback<Object>() {
            @Override
            public Object execute(RedisOperations operations) {
                for (Map.Entry<String, String> entry : data.entrySet()) {
                    operations.opsForValue().set(entry.getKey(), entry.getValue());
                }
                return null; // Pipeline은 결과를 반환하지 않음
            }
        });
    }
    
    // 1000개 키 조회
    public List<String> batchGet(List<String> keys) {
        List<Object> results = redisTemplate.executePipelined(
            new SessionCallback<Object>() {
                @Override
                public Object execute(RedisOperations operations) {
                    for (String key : keys) {
                        operations.opsForValue().get(key);
                    }
                    return null;
                }
            }
        );
        
        return results.stream()
            .map(obj -> (String) obj)
            .collect(Collectors.toList());
    }
}
```

## 주의사항 / 함정

### 1. Pub/Sub 메시지 손실
❌ **문제**: 구독자가 없으면 메시지 소실
✅ **해결**: 
- 중요 메시지는 Kafka, RabbitMQ 사용
- Redis는 실시간 알림 등 손실 허용 가능한 경우만

### 2. 트랜잭션 롤백 없음
```bash
MULTI
SET key1 "value1"        # 성공
INCR string_key          # 실패 (문자열이므로)
SET key2 "value2"        # 성공
EXEC
→ key1, key2는 저장됨 (롤백 안 됨!)
```

✅ **해결**: Lua 스크립트 사용 (에러 시 전체 실패)

### 3. WATCH 키가 너무 많으면 성능 저하
- 최소한의 키만 WATCH
- Lua 스크립트가 더 나은 선택

### 4. Pub/Sub는 메시지 저장 안 함
- 실시간 전송만 가능
- 과거 메시지 조회 불가능

## 관련 개념
- [[Redis-기본개념]] - Redis 개요
- [[Kafka-기본개념]] - 메시징 시스템 비교
- [[데이터베이스-트랜잭션]] - ACID 속성
- [[동시성-제어]] - Lock, 낙관적/비관적 락
- [[WebSocket]] - 실시간 통신

## 면접 질문

1. **Redis Pub/Sub과 Kafka의 차이는?**
   - Redis: 실시간, 경량, 메시지 보장 없음, 영속성 없음
   - Kafka: 메시지 저장, 재전송 가능, 고가용성, 무겁고 복잡
   - 용도: Redis는 실시간 알림, Kafka는 이벤트 스트리밍

2. **Redis 트랜잭션이 롤백을 지원하지 않는 이유는?**
   - 단순함과 성능 우선
   - 에러는 주로 프로그래밍 실수 (타입 오류 등)
   - 네트워크/하드웨어 장애는 전체 실패로 처리

3. **WATCH와 Lua 스크립트 중 무엇을 선택하겠습니까?**
   - Lua 스크립트 권장
   - WATCH는 재시도 필요, 성능 저하 가능
   - Lua는 원자적 실행, 에러 시 전체 롤백

4. **재고 차감을 Redis로 구현할 때 동시성 문제를 어떻게 해결하나요?**
   - Lua 스크립트로 조회+차감을 원자적으로 실행
   - WATCH/MULTI/EXEC는 재시도 필요
   - 분산 락 (SETNX) 사용 가능

5. **Pipeline과 트랜잭션의 차이는?**
   - Pipeline: 네트워크 왕복 감소, 원자성 보장 없음
   - 트랜잭션: 원자성 보장, 네트워크 감소 효과도 있음
   - 용도: Pipeline은 성능, 트랜잭션은 일관성

6. **프로젝트에서 Pub/Sub을 어떻게 사용했나요? (BizSync 예시)**
   - 실시간 문서 편집 알림 전송
   - 여러 서버 간 이벤트 동기화
   - WebSocket과 연동하여 클라이언트에 알림

## 참고 자료
- [Redis Pub/Sub 공식 문서](https://redis.io/docs/manual/pubsub/)
- [Redis Transactions](https://redis.io/docs/manual/transactions/)
- [Lua Scripting in Redis](https://redis.io/docs/manual/programmability/eval-intro/)
- [Spring Data Redis - Pub/Sub](https://docs.spring.io/spring-data/redis/docs/current/reference/html/#pubsub)
