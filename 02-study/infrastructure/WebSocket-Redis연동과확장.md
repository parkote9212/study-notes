---
tags:
  - study
  - websocket
  - redis
  - scaling
  - clustering
  - pubsub
created: 2026-02-15
---

# WebSocket Redis 연동과 확장

## 한 줄 요약
> WebSocket의 Scale-Out 환경에서는 Redis Pub/Sub을 활용하여 여러 서버 간 메시지를 동기화하고, Session Clustering으로 세션 공유 문제를 해결하여 고가용성 실시간 시스템을 구축한다.

## 상세 설명

### WebSocket Scale-Out 문제

**단일 서버 환경:**
```
      ┌─────────┐
      │ Server  │
      └────┬────┘
      ┌────┴────┐
   User A    User B
   (같은 서버에 연결)
   → A의 메시지가 B에게 즉시 전달 ✅
```

**다중 서버 환경 (문제 발생):**
```
   ┌─────────┐       ┌─────────┐
   │Server 1 │       │Server 2 │
   └────┬────┘       └────┬────┘
      User A            User B
      
   User A → Server 1 → ❌ Server 2에 전달 안 됨!
   → User B는 메시지 받지 못함
```

### 해결 방법: Redis Pub/Sub

```
   ┌─────────┐       ┌─────────┐
   │Server 1 │       │Server 2 │
   └────┬────┘       └────┬────┘
        │                 │
        └────┬───────┬────┘
           ┌─▼───────▼─┐
           │  Redis    │
           │  Pub/Sub  │
           └───────────┘
           
   User A → Server 1 → Redis Pub/Sub → Server 2 → User B ✅
```

## 1. Redis Pub/Sub 통합

### Gradle 의존성
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-websocket'
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
}
```

### Redis 설정
```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password:  # 옵션
```

### Redis Pub/Sub 설정
```java
@Configuration
public class RedisPubSubConfig {
    
    @Bean
    public RedisMessageListenerContainer redisMessageListenerContainer(
            RedisConnectionFactory connectionFactory,
            MessageListenerAdapter listenerAdapter) {
        
        RedisMessageListenerContainer container = 
            new RedisMessageListenerContainer();
        
        container.setConnectionFactory(connectionFactory);
        
        // 채팅 메시지 채널 구독
        container.addMessageListener(
            listenerAdapter, 
            new ChannelTopic("chat:messages")
        );
        
        return container;
    }
    
    @Bean
    public MessageListenerAdapter listenerAdapter(
            RedisMessageSubscriber subscriber) {
        return new MessageListenerAdapter(subscriber, "onMessage");
    }
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate(
            RedisConnectionFactory connectionFactory) {
        
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        
        Jackson2JsonRedisSerializer<Object> serializer = 
            new Jackson2JsonRedisSerializer<>(Object.class);
        
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(serializer);
        
        return template;
    }
}
```

### Redis Publisher (메시지 발행)
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class RedisMessagePublisher {
    
    private final RedisTemplate<String, Object> redisTemplate;
    
    // 채팅 메시지 발행
    public void publishChatMessage(ChatMessage message) {
        log.info("Redis Pub: {}", message);
        redisTemplate.convertAndSend("chat:messages", message);
    }
    
    // 알림 발행
    public void publishNotification(String userId, Notification notification) {
        String channel = "notification:" + userId;
        redisTemplate.convertAndSend(channel, notification);
    }
    
    // 브로드캐스트
    public void broadcast(String channel, Object message) {
        redisTemplate.convertAndSend(channel, message);
    }
}
```

### Redis Subscriber (메시지 수신)
```java
@Component
@RequiredArgsConstructor
@Slf4j
public class RedisMessageSubscriber {
    
    private final SimpMessagingTemplate messagingTemplate;
    
    // Redis에서 메시지 수신 → WebSocket으로 전달
    public void onMessage(String message, String channel) {
        log.info("Redis Sub: channel={}, message={}", channel, message);
        
        try {
            ChatMessage chatMessage = 
                new ObjectMapper().readValue(message, ChatMessage.class);
            
            // WebSocket으로 브로드캐스트
            messagingTemplate.convertAndSend("/topic/public", chatMessage);
            
        } catch (Exception e) {
            log.error("메시지 파싱 실패: {}", message, e);
        }
    }
}
```

## 2. STOMP + Redis 통합

### STOMP Controller (Redis 연동)
```java
@Controller
@RequiredArgsConstructor
@Slf4j
public class ChatController {
    
    private final RedisMessagePublisher redisPublisher;
    
    @MessageMapping("/chat.send")
    public void sendMessage(@Payload ChatMessage message) {
        log.info("메시지 수신: {}", message);
        
        message.setTimestamp(LocalDateTime.now());
        
        // Redis Pub/Sub으로 발행 → 모든 서버에 전달
        redisPublisher.publishChatMessage(message);
    }
    
    @MessageMapping("/chat.join")
    public void joinChat(@Payload ChatMessage message,
                        SimpMessageHeaderAccessor headerAccessor) {
        
        headerAccessor.getSessionAttributes().put("username", message.getSender());
        
        message.setType(MessageType.JOIN);
        message.setContent(message.getSender() + "님이 입장하셨습니다.");
        message.setTimestamp(LocalDateTime.now());
        
        // Redis로 발행
        redisPublisher.publishChatMessage(message);
    }
}
```

### 전체 흐름
```
1. User A (Server 1) → STOMP 메시지 전송
2. Server 1 Controller → Redis Pub/Sub 발행
3. Redis → Server 1, Server 2 모두에게 전달
4. Server 1, 2의 Subscriber → WebSocket으로 전달
5. User A, B 모두 메시지 수신 ✅
```

## 3. BizSync 프로젝트 실전 예시

### 실시간 문서 협업 (Redis 연동)
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class DocumentCollaborationService {
    
    private final RedisTemplate<String, Object> redisTemplate;
    private final SimpMessagingTemplate messagingTemplate;
    
    // 문서 편집 이벤트 발행
    public void publishEditEvent(DocumentEditEvent event) {
        String channel = "document:" + event.getDocumentId();
        
        log.info("문서 편집 이벤트 발행: documentId={}, userId={}", 
            event.getDocumentId(), event.getUserId());
        
        // Redis Pub/Sub
        redisTemplate.convertAndSend(channel, event);
    }
    
    // 문서별 구독 관리
    @PostConstruct
    public void setupSubscriptions() {
        RedisMessageListenerContainer container = 
            new RedisMessageListenerContainer();
        
        // 모든 문서 채널 구독
        container.addMessageListener(
            (message, pattern) -> {
                DocumentEditEvent event = 
                    (DocumentEditEvent) redisTemplate
                        .getValueSerializer()
                        .deserialize(message.getBody());
                
                // WebSocket으로 전달
                String destination = "/topic/document/" + event.getDocumentId();
                messagingTemplate.convertAndSend(destination, event);
            },
            new PatternTopic("document:*")
        );
    }
}
```

### 온라인 사용자 관리 (Redis Set)
```java
@Service
@RequiredArgsConstructor
public class OnlineUserService {
    
    private final RedisTemplate<String, String> redisTemplate;
    
    // 사용자 온라인 처리
    public void userOnline(String userId) {
        String key = "online:users";
        redisTemplate.opsForSet().add(key, userId);
        
        // TTL 설정 (5분마다 갱신 필요)
        redisTemplate.expire(key, 5, TimeUnit.MINUTES);
    }
    
    // 사용자 오프라인 처리
    public void userOffline(String userId) {
        String key = "online:users";
        redisTemplate.opsForSet().remove(key, userId);
    }
    
    // 온라인 사용자 목록 조회
    public Set<String> getOnlineUsers() {
        String key = "online:users";
        return redisTemplate.opsForSet().members(key);
    }
    
    // 온라인 여부 확인
    public boolean isOnline(String userId) {
        String key = "online:users";
        return Boolean.TRUE.equals(
            redisTemplate.opsForSet().isMember(key, userId)
        );
    }
}
```

### WebSocket 이벤트 리스너 (Redis 통합)
```java
@Component
@RequiredArgsConstructor
@Slf4j
public class WebSocketEventListener {
    
    private final OnlineUserService onlineUserService;
    private final RedisMessagePublisher redisPublisher;
    
    @EventListener
    public void handleWebSocketConnectListener(SessionConnectedEvent event) {
        StompHeaderAccessor headerAccessor = 
            StompHeaderAccessor.wrap(event.getMessage());
        
        String userId = (String) headerAccessor
            .getSessionAttributes()
            .get("userId");
        
        if (userId != null) {
            // Redis에 온라인 상태 저장
            onlineUserService.userOnline(userId);
            
            log.info("사용자 온라인: {}", userId);
        }
    }
    
    @EventListener
    public void handleWebSocketDisconnectListener(SessionDisconnectEvent event) {
        StompHeaderAccessor headerAccessor = 
            StompHeaderAccessor.wrap(event.getMessage());
        
        String userId = (String) headerAccessor
            .getSessionAttributes()
            .get("userId");
        
        if (userId != null) {
            // Redis에서 온라인 상태 제거
            onlineUserService.userOffline(userId);
            
            // 퇴장 알림 발행
            ChatMessage leaveMessage = ChatMessage.builder()
                .type(MessageType.LEAVE)
                .sender(userId)
                .content(userId + "님이 퇴장하셨습니다.")
                .timestamp(LocalDateTime.now())
                .build();
            
            redisPublisher.publishChatMessage(leaveMessage);
            
            log.info("사용자 오프라인: {}", userId);
        }
    }
}
```

## 4. Session Clustering

### 문제: 세션 불일치
```
로드 밸런서
    │
    ├─ Server 1: User A 세션 있음
    └─ Server 2: User A 세션 없음
    
User A의 요청이 Server 2로 가면 → 세션 없음 에러!
```

### 해결: Spring Session + Redis
```gradle
dependencies {
    implementation 'org.springframework.session:spring-session-data-redis'
}
```

```yaml
spring:
  session:
    store-type: redis
    timeout: 30m
    redis:
      namespace: spring:session
```

```java
@EnableRedisHttpSession
@Configuration
public class SessionConfig {
    // 자동으로 Redis에 세션 저장
}
```

**효과:**
```
로드 밸런서
    │
    ├─ Server 1 ─┐
    └─ Server 2 ─┤
                 │
              ┌──▼──┐
              │Redis│  ← 세션 공유
              └─────┘
              
User A의 요청이 어느 서버로 가도 → Redis에서 세션 조회 ✅
```

## 5. 성능 최적화

### 1. Connection Pool 설정
```yaml
spring:
  data:
    redis:
      lettuce:
        pool:
          max-active: 10   # 최대 연결 수
          max-idle: 10     # 최대 유휴 연결
          min-idle: 2      # 최소 유휴 연결
```

### 2. 메시지 직렬화 최적화
```java
@Bean
public RedisSerializer<Object> redisSerializer() {
    // JSON 압축
    return new GenericJackson2JsonRedisSerializer(
        new ObjectMapper()
            .configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false)
    );
}
```

### 3. 불필요한 브로드캐스트 방지
```java
@MessageMapping("/chat.typing")
public void handleTyping(@Payload TypingEvent event) {
    // 타이핑 이벤트는 Redis 거치지 않고 직접 전송
    // (빈번하고 중요도 낮음)
    messagingTemplate.convertAndSend("/topic/typing", event);
}
```

### 4. 배치 처리
```java
// 여러 메시지를 한 번에 발행
public void publishBatch(List<ChatMessage> messages) {
    redisTemplate.executePipelined(new SessionCallback<Object>() {
        @Override
        public Object execute(RedisOperations operations) {
            for (ChatMessage msg : messages) {
                operations.convertAndSend("chat:messages", msg);
            }
            return null;
        }
    });
}
```

## 6. 모니터링

### WebSocket 세션 수 추적
```java
@Component
@Slf4j
public class WebSocketMetrics {
    
    private final AtomicInteger activeConnections = new AtomicInteger(0);
    
    @EventListener
    public void onConnect(SessionConnectedEvent event) {
        int count = activeConnections.incrementAndGet();
        log.info("활성 WebSocket 연결: {}", count);
    }
    
    @EventListener
    public void onDisconnect(SessionDisconnectEvent event) {
        int count = activeConnections.decrementAndGet();
        log.info("활성 WebSocket 연결: {}", count);
    }
    
    @Scheduled(fixedRate = 60000)  // 1분마다
    public void logMetrics() {
        log.info("현재 WebSocket 연결 수: {}", activeConnections.get());
    }
}
```

### Redis 메트릭
```java
@Component
@RequiredArgsConstructor
public class RedisMonitor {
    
    private final RedisTemplate<String, Object> redisTemplate;
    
    @Scheduled(fixedRate = 300000)  // 5분마다
    public void checkRedisHealth() {
        try {
            redisTemplate.opsForValue().set("health:check", "OK", 10, TimeUnit.SECONDS);
            String result = (String) redisTemplate.opsForValue().get("health:check");
            
            if ("OK".equals(result)) {
                log.info("Redis 정상");
            } else {
                log.warn("Redis 응답 이상");
            }
        } catch (Exception e) {
            log.error("Redis 연결 실패", e);
        }
    }
}
```

## 주의사항 / 함정

### 1. Redis 장애 대응
❌ **문제**: Redis 다운 시 전체 서비스 중단  
✅ **해결**:
```java
@Service
public class FallbackMessageService {
    
    public void sendMessage(ChatMessage message) {
        try {
            // Redis 우선
            redisPublisher.publish(message);
        } catch (Exception e) {
            // Fallback: 같은 서버 내에서만 전송
            log.warn("Redis 장애, 로컬 전송으로 폴백");
            messagingTemplate.convertAndSend("/topic/public", message);
        }
    }
}
```

### 2. 메시지 순서 보장
- Redis Pub/Sub은 **순서 보장 안 함**
- 필요 시 타임스탬프 + 클라이언트 정렬

### 3. 메시지 중복
- 네트워크 문제 시 중복 가능
- 클라이언트에서 중복 제거 (messageId 사용)

### 4. TTL 설정
```java
// 온라인 상태는 5분마다 갱신 필요
redisTemplate.expire("online:users", 5, TimeUnit.MINUTES);
```

## 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────┐
│                Load Balancer                     │
└───────────────┬──────────────┬───────────────────┘
                │              │
        ┌───────▼──────┐   ┌──▼──────────┐
        │  Server 1    │   │  Server 2   │
        │  (Spring)    │   │  (Spring)   │
        └───────┬──────┘   └──┬──────────┘
                │              │
                └──────┬───────┘
                       │
                ┌──────▼──────┐
                │    Redis    │
                │  Pub/Sub    │
                │  Session    │
                └─────────────┘
                
User A → Server 1 → Redis Pub/Sub → Server 2 → User B
```

## 관련 개념
- [[WebSocket-기본개념]] - WebSocket 프로토콜
- [[WebSocket-STOMP프로토콜]] - STOMP 메시징
- [[Redis-PubSub과트랜잭션]] - Redis Pub/Sub
- [[Redis-기본개념]] - Redis 개요
- [[로드밸런싱]] - Scale-Out 아키텍처

## 면접 질문

1. **WebSocket Scale-Out 시 발생하는 문제는?**
   - 서버 간 세션 공유 안 됨
   - 다른 서버의 사용자에게 메시지 전달 불가
   - 해결: Redis Pub/Sub

2. **Redis Pub/Sub을 어떻게 활용하나요?**
   - Server 1 → Redis 발행
   - Redis → 모든 서버 구독자에게 전달
   - 각 서버 → WebSocket으로 클라이언트 전송

3. **Session Clustering이 필요한 이유는?**
   - 로드 밸런서가 요청을 다른 서버로 보냄
   - 세션이 공유되지 않으면 인증 실패
   - Redis에 세션 저장하여 해결

4. **Redis 장애 시 어떻게 대응하나요?**
   - Fallback: 같은 서버 내에서만 전송
   - Redis Sentinel로 자동 Failover
   - 모니터링으로 빠른 복구

5. **메시지 순서를 보장하려면?**
   - Redis Pub/Sub은 순서 보장 안 함
   - 타임스탬프 추가
   - 클라이언트에서 정렬

6. **프로젝트에서 Redis 연동을 어떻게 했나요? (BizSync)**
   - 다중 서버 환경 대비
   - Redis Pub/Sub으로 문서 편집 동기화
   - Session Clustering으로 세션 공유

## 참고 자료
- [Spring Session Redis](https://docs.spring.io/spring-session/docs/current/reference/html5/#httpsession-redis)
- [Redis Pub/Sub](https://redis.io/docs/manual/pubsub/)
- [Spring Data Redis Pub/Sub](https://docs.spring.io/spring-data/redis/docs/current/reference/html/#pubsub)
- [WebSocket Clustering](https://docs.spring.io/spring-framework/reference/web/websocket/stomp/message-flow.html)
