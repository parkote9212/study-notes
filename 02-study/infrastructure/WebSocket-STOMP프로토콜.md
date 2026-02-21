---
tags:
  - study
  - websocket
  - stomp
  - messaging
  - spring
created: 2026-02-15
---

# WebSocket STOMP 프로토콜

## 한 줄 요약
> STOMP(Simple Text Oriented Messaging Protocol)는 WebSocket 위에서 동작하는 메시징 프로토콜로, @MessageMapping과 @SendTo를 통해 Pub/Sub 패턴을 간편하게 구현하여 채팅, 알림 시스템을 효율적으로 개발할 수 있다.

## 상세 설명

### STOMP란?
**STOMP (Simple Text Oriented Messaging Protocol)**
- WebSocket 위에서 동작하는 **텍스트 기반 메시징 프로토콜**
- HTTP와 유사한 프레임 구조
- Pub/Sub (발행/구독) 패턴 지원

### 왜 STOMP를 사용하는가?

**순수 WebSocket의 문제:**
```java
// ❌ 순수 WebSocket - 직접 라우팅 처리 필요
@Override
protected void handleTextMessage(WebSocketSession session, TextMessage message) {
    String payload = message.getPayload();
    
    if (payload.startsWith("/chat")) {
        handleChat(session, payload);
    } else if (payload.startsWith("/notification")) {
        handleNotification(session, payload);
    }
    // 복잡한 분기 처리...
}
```

**STOMP 사용 시:**
```java
// ✅ STOMP - 선언적이고 간단
@MessageMapping("/chat")  // 경로 자동 라우팅
@SendTo("/topic/public")   // 자동 브로드캐스트
public ChatMessage sendMessage(ChatMessage message) {
    return message;
}
```

### 순수 WebSocket vs STOMP

| 항목 | 순수 WebSocket | STOMP |
|------|---------------|-------|
| **라우팅** | 수동 처리 | 자동 (@MessageMapping) |
| **구독 관리** | 수동 구현 | 자동 (브로커) |
| **메시지 형식** | 자유 | 정해진 프레임 |
| **복잡도** | 높음 | 낮음 |
| **사용 사례** | 단순 통신 | 채팅, 알림, 실시간 협업 |

## STOMP 프레임 구조

### 기본 프레임
```
COMMAND
header1:value1
header2:value2

Body^@
```

### 주요 커맨드

**클라이언트 → 서버:**
- `CONNECT`: 연결 요청
- `SEND`: 메시지 전송
- `SUBSCRIBE`: 토픽 구독
- `UNSUBSCRIBE`: 구독 해제
- `DISCONNECT`: 연결 종료

**서버 → 클라이언트:**
- `CONNECTED`: 연결 성공
- `MESSAGE`: 메시지 수신
- `RECEIPT`: 수신 확인
- `ERROR`: 에러

### 예시
```
SEND
destination:/app/chat
content-type:application/json

{"sender":"Alice","content":"Hello"}^@
```

## 1. Spring STOMP 설정

### Gradle 의존성
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-websocket'
    implementation 'org.webjars:webjars-locator-core'
    implementation 'org.webjars:sockjs-client:1.5.1'
    implementation 'org.webjars:stomp-websocket:2.3.4'
}
```

### STOMP 설정
```java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketStompConfig implements WebSocketMessageBrokerConfigurer {
    
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry
            .addEndpoint("/ws")  // WebSocket 엔드포인트
            .setAllowedOriginPatterns("*")  // CORS
            .withSockJS();  // SockJS fallback
    }
    
    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        // 1. Simple Broker (인메모리)
        registry.enableSimpleBroker("/topic", "/queue");
        
        // 2. 클라이언트 → 서버 메시지 prefix
        registry.setApplicationDestinationPrefixes("/app");
        
        // 3. 사용자별 메시지 prefix
        registry.setUserDestinationPrefix("/user");
    }
}
```

### 설정 설명

**Destination 구조:**
```
/app/**      → 클라이언트가 서버로 메시지 전송 (@MessageMapping)
/topic/**    → 1:N 브로드캐스트 (Pub/Sub)
/queue/**    → 1:1 메시지
/user/**     → 특정 사용자에게만 전송
```

**예시:**
```
클라이언트 → /app/chat.send       (서버의 @MessageMapping("/chat.send") 실행)
서버 → /topic/public              (구독한 모든 클라이언트에게 전송)
서버 → /user/{userId}/queue/reply (특정 사용자에게만 전송)
```

## 2. Controller 구현

### 채팅 Controller
```java
@Controller
@Slf4j
public class ChatController {
    
    @Autowired
    private SimpMessagingTemplate messagingTemplate;
    
    // 1. 채팅 메시지 전송 (브로드캐스트)
    @MessageMapping("/chat.send")  // 클라이언트가 /app/chat.send로 전송
    @SendTo("/topic/public")        // 구독자 모두에게 전송
    public ChatMessage sendMessage(ChatMessage message) {
        log.info("채팅 메시지 수신: {}", message);
        
        message.setTimestamp(LocalDateTime.now());
        return message;  // 자동으로 /topic/public으로 전송됨
    }
    
    // 2. 입장 메시지
    @MessageMapping("/chat.join")
    @SendTo("/topic/public")
    public ChatMessage joinChat(@Payload ChatMessage message,
                                SimpMessageHeaderAccessor headerAccessor) {
        
        // WebSocket 세션에 사용자 이름 저장
        headerAccessor.getSessionAttributes().put("username", message.getSender());
        
        message.setType(MessageType.JOIN);
        message.setContent(message.getSender() + "님이 입장하셨습니다.");
        message.setTimestamp(LocalDateTime.now());
        
        return message;
    }
    
    // 3. 1:1 메시지 (특정 사용자에게만)
    @MessageMapping("/chat.private")
    public void sendPrivateMessage(@Payload ChatMessage message) {
        log.info("1:1 메시지: {} -> {}", message.getSender(), message.getReceiver());
        
        message.setTimestamp(LocalDateTime.now());
        
        // 특정 사용자에게만 전송
        messagingTemplate.convertAndSendToUser(
            message.getReceiver(),           // 수신자
            "/queue/private",                // destination
            message                          // 메시지
        );
    }
    
    // 4. 타이핑 중 알림
    @MessageMapping("/chat.typing")
    @SendTo("/topic/typing")
    public TypingEvent sendTypingEvent(TypingEvent event) {
        return event;
    }
}
```

### 알림 Controller
```java
@Controller
@Slf4j
public class NotificationController {
    
    @Autowired
    private SimpMessagingTemplate messagingTemplate;
    
    // 특정 사용자에게 알림 전송
    public void sendNotification(String userId, Notification notification) {
        messagingTemplate.convertAndSendToUser(
            userId,
            "/queue/notifications",
            notification
        );
    }
    
    // 전체 사용자에게 공지
    @MessageMapping("/admin.broadcast")
    @SendTo("/topic/announcements")
    public Announcement broadcastAnnouncement(Announcement announcement) {
        announcement.setTimestamp(LocalDateTime.now());
        return announcement;
    }
}
```

### Service에서 메시지 전송
```java
@Service
@RequiredArgsConstructor
public class OrderService {
    
    private final SimpMessagingTemplate messagingTemplate;
    
    @Transactional
    public Order createOrder(OrderDto dto) {
        Order order = orderRepository.save(new Order(dto));
        
        // 주문 완료 알림 전송
        Notification notification = Notification.builder()
            .type("ORDER_CREATED")
            .message("주문이 접수되었습니다.")
            .orderId(order.getId())
            .timestamp(LocalDateTime.now())
            .build();
        
        // 해당 사용자에게만 알림
        messagingTemplate.convertAndSendToUser(
            order.getUserId().toString(),
            "/queue/notifications",
            notification
        );
        
        return order;
    }
}
```

## 3. 클라이언트 구현

### SockJS + STOMP.js
```html
<!DOCTYPE html>
<html>
<head>
    <title>STOMP Chat</title>
    <script src="https://cdn.jsdelivr.net/npm/sockjs-client@1/dist/sockjs.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@stomp/stompjs@6/bundles/stomp.umd.min.js"></script>
</head>
<body>
    <div id="chat-container">
        <div id="messages"></div>
        <input type="text" id="message-input" placeholder="메시지 입력...">
        <button onclick="sendMessage()">전송</button>
    </div>
    
    <script>
        let stompClient = null;
        const username = "User" + Math.floor(Math.random() * 1000);
        
        // 연결
        function connect() {
            const socket = new SockJS('http://localhost:8080/ws');
            stompClient = Stomp.over(socket);
            
            stompClient.connect({}, onConnected, onError);
        }
        
        // 연결 성공
        function onConnected() {
            console.log('STOMP 연결 성공');
            
            // 1. 공개 채팅방 구독
            stompClient.subscribe('/topic/public', onMessageReceived);
            
            // 2. 개인 메시지 구독
            stompClient.subscribe('/user/queue/private', onPrivateMessage);
            
            // 3. 타이핑 이벤트 구독
            stompClient.subscribe('/topic/typing', onTypingEvent);
            
            // 4. 입장 메시지 전송
            stompClient.send('/app/chat.join', {}, JSON.stringify({
                sender: username,
                type: 'JOIN'
            }));
        }
        
        // 연결 실패
        function onError(error) {
            console.error('STOMP 연결 실패:', error);
        }
        
        // 메시지 전송
        function sendMessage() {
            const input = document.getElementById('message-input');
            const content = input.value.trim();
            
            if (content && stompClient) {
                const chatMessage = {
                    sender: username,
                    content: content,
                    type: 'CHAT'
                };
                
                stompClient.send('/app/chat.send', {}, JSON.stringify(chatMessage));
                input.value = '';
            }
        }
        
        // 메시지 수신
        function onMessageReceived(payload) {
            const message = JSON.parse(payload.body);
            displayMessage(message);
        }
        
        // 1:1 메시지 수신
        function onPrivateMessage(payload) {
            const message = JSON.parse(payload.body);
            displayPrivateMessage(message);
        }
        
        // 타이핑 이벤트 수신
        function onTypingEvent(payload) {
            const event = JSON.parse(payload.body);
            showTypingIndicator(event.username);
        }
        
        // 1:1 메시지 전송
        function sendPrivateMessage(receiver, content) {
            const message = {
                sender: username,
                receiver: receiver,
                content: content,
                type: 'PRIVATE'
            };
            
            stompClient.send('/app/chat.private', {}, JSON.stringify(message));
        }
        
        // 연결 해제
        function disconnect() {
            if (stompClient) {
                stompClient.disconnect(() => {
                    console.log('STOMP 연결 해제');
                });
            }
        }
        
        // 페이지 로드 시 자동 연결
        window.onload = connect;
        window.onbeforeunload = disconnect;
    </script>
</body>
</html>
```

### React 예시
```javascript
import React, { useEffect, useState } from 'react';
import SockJS from 'sockjs-client';
import { Stomp } from '@stomp/stompjs';

function ChatComponent() {
    const [stompClient, setStompClient] = useState(null);
    const [messages, setMessages] = useState([]);
    const [connected, setConnected] = useState(false);
    
    useEffect(() => {
        // 연결
        const socket = new SockJS('http://localhost:8080/ws');
        const client = Stomp.over(socket);
        
        client.connect({}, () => {
            console.log('연결 성공');
            setConnected(true);
            
            // 구독
            client.subscribe('/topic/public', (message) => {
                const chatMessage = JSON.parse(message.body);
                setMessages(prev => [...prev, chatMessage]);
            });
        });
        
        setStompClient(client);
        
        // 클린업
        return () => {
            if (client) {
                client.disconnect();
            }
        };
    }, []);
    
    const sendMessage = (content) => {
        if (stompClient && connected) {
            const message = {
                sender: 'User',
                content: content,
                type: 'CHAT'
            };
            
            stompClient.send('/app/chat.send', {}, JSON.stringify(message));
        }
    };
    
    return (
        <div>
            <div className="messages">
                {messages.map((msg, idx) => (
                    <div key={idx}>{msg.sender}: {msg.content}</div>
                ))}
            </div>
            <button onClick={() => sendMessage('Hello!')}>전송</button>
        </div>
    );
}
```

## 4. 이벤트 리스너

### 연결/종료 이벤트 처리
```java
@Component
@Slf4j
public class WebSocketEventListener {
    
    @Autowired
    private SimpMessagingTemplate messagingTemplate;
    
    // 연결 수립 시
    @EventListener
    public void handleWebSocketConnectListener(SessionConnectedEvent event) {
        StompHeaderAccessor headerAccessor = 
            StompHeaderAccessor.wrap(event.getMessage());
        
        String sessionId = headerAccessor.getSessionId();
        log.info("새 WebSocket 연결: sessionId={}", sessionId);
    }
    
    // 연결 해제 시
    @EventListener
    public void handleWebSocketDisconnectListener(SessionDisconnectEvent event) {
        StompHeaderAccessor headerAccessor = 
            StompHeaderAccessor.wrap(event.getMessage());
        
        String username = (String) headerAccessor
            .getSessionAttributes()
            .get("username");
        
        if (username != null) {
            log.info("사용자 퇴장: {}", username);
            
            // 퇴장 알림 전송
            ChatMessage leaveMessage = ChatMessage.builder()
                .type(MessageType.LEAVE)
                .sender(username)
                .content(username + "님이 퇴장하셨습니다.")
                .timestamp(LocalDateTime.now())
                .build();
            
            messagingTemplate.convertAndSend("/topic/public", leaveMessage);
        }
    }
    
    // 구독 시
    @EventListener
    public void handleSubscribeEvent(SessionSubscribeEvent event) {
        StompHeaderAccessor headerAccessor = 
            StompHeaderAccessor.wrap(event.getMessage());
        
        String destination = headerAccessor.getDestination();
        log.info("새 구독: destination={}", destination);
    }
}
```

## 5. 외부 메시지 브로커 (RabbitMQ)

### 설정
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-amqp'
}
```

```java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketStompConfig implements WebSocketMessageBrokerConfigurer {
    
    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        // RabbitMQ 브로커 사용
        registry.enableStompBrokerRelay("/topic", "/queue")
            .setRelayHost("localhost")
            .setRelayPort(61613)  // STOMP 포트
            .setClientLogin("guest")
            .setClientPasscode("guest");
        
        registry.setApplicationDestinationPrefixes("/app");
    }
}
```

**Simple Broker vs RabbitMQ:**

| 항목 | Simple Broker | RabbitMQ |
|------|--------------|----------|
| **확장성** | 단일 서버만 | 다중 서버 지원 |
| **영속성** | 없음 | 있음 |
| **성능** | 빠름 | 약간 느림 |
| **용도** | 개발/소규모 | 프로덕션 |

## 주의사항 / 함정

### 1. Destination 경로 일치
```java
// ❌ 잘못된 예
@MessageMapping("/chat")     // /app/chat
@SendTo("/public")          // /public (X)

// ✅ 올바른 예
@MessageMapping("/chat")     // /app/chat
@SendTo("/topic/public")    // /topic/public (O)
```

### 2. 세션 정보 접근
```java
@MessageMapping("/chat")
public ChatMessage handleMessage(
        @Payload ChatMessage message,
        SimpMessageHeaderAccessor headerAccessor) {  // 헤더 접근
    
    String sessionId = headerAccessor.getSessionId();
    Map<String, Object> attrs = headerAccessor.getSessionAttributes();
    
    return message;
}
```

### 3. 에러 처리
```java
@MessageExceptionHandler
@SendToUser("/queue/errors")
public ErrorMessage handleException(Exception e) {
    return new ErrorMessage(e.getMessage());
}
```

## 관련 개념
- [[WebSocket-기본개념]] - WebSocket 프로토콜
- [[WebSocket-Spring통합]] - Spring WebSocket
- [[WebSocket-Redis연동과확장]] - 다중 서버
- [[RabbitMQ]] - 메시지 브로커

## 면접 질문

1. **STOMP가 무엇이며, 왜 사용하나요?**
   - WebSocket 위의 메시징 프로토콜
   - Pub/Sub 패턴 지원
   - 라우팅, 구독 관리 자동화

2. **/app, /topic, /queue의 차이는?**
   - /app: 클라이언트 → 서버
   - /topic: 1:N 브로드캐스트
   - /queue: 1:1 메시지

3. **Simple Broker와 RabbitMQ 차이는?**
   - Simple: 인메모리, 단일 서버
   - RabbitMQ: 다중 서버, 영속성

4. **특정 사용자에게만 메시지를 보내려면?**
   - convertAndSendToUser()
   - /user/{userId}/queue/...

5. **프로젝트에서 STOMP를 어떻게 사용했나요?**
   - 실시간 채팅, 알림 시스템
   - @MessageMapping으로 간편한 라우팅

## 참고 자료
- [STOMP 프로토콜 명세](https://stomp.github.io/stomp-specification-1.2.html)
- [Spring STOMP 공식 문서](https://docs.spring.io/spring-framework/reference/web/websocket/stomp.html)
- [STOMP.js](https://stomp-js.github.io/stomp-websocket/)
