---
tags:
  - study
  - websocket
  - spring
  - spring-boot
  - realtime
created: 2026-02-15
---

# WebSocket Spring 통합

## 한 줄 요약
> Spring WebSocket은 @EnableWebSocket, WebSocketHandler, WebSocketSession을 제공하여 실시간 양방향 통신을 쉽게 구현하며, Interceptor와 Handler로 세션 관리와 메시지 처리를 효율적으로 수행한다.

## 상세 설명

### Spring WebSocket이란?
- Spring Framework의 WebSocket 지원 모듈
- 저수준 WebSocket API를 고수준으로 추상화
- Spring MVC와 통합되어 사용 편리

### 주요 구성 요소
1. **WebSocketConfigurer**: WebSocket 엔드포인트 등록
2. **WebSocketHandler**: 메시지 수신/전송 처리
3. **WebSocketSession**: 클라이언트 연결 세션
4. **HandshakeInterceptor**: 연결 전 인증/검증

## 1. 프로젝트 설정

### Gradle 의존성
```gradle
dependencies {
    // Spring Boot WebSocket
    implementation 'org.springframework.boot:spring-boot-starter-websocket'
    
    // JSON 처리
    implementation 'com.fasterxml.jackson.core:jackson-databind'
    
    // Lombok (선택)
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
}
```

### application.yml 설정
```yaml
server:
  port: 8080

spring:
  application:
    name: websocket-demo

logging:
  level:
    org.springframework.web.socket: DEBUG
```

## 2. 기본 WebSocket 구현

### WebSocket 설정
```java
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {
    
    @Autowired
    private ChatWebSocketHandler chatWebSocketHandler;
    
    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry
            .addHandler(chatWebSocketHandler, "/ws/chat")  // 엔드포인트
            .setAllowedOrigins("*")  // CORS 설정
            .addInterceptors(new HttpSessionHandshakeInterceptor());  // 인터셉터
    }
}
```

### WebSocketHandler 구현
```java
@Component
@Slf4j
public class ChatWebSocketHandler extends TextWebSocketHandler {
    
    // 연결된 모든 세션 저장
    private final Set<WebSocketSession> sessions = 
        Collections.synchronizedSet(new HashSet<>());
    
    // 사용자별 세션 매핑
    private final Map<String, WebSocketSession> userSessions = 
        new ConcurrentHashMap<>();
    
    // 1. 연결 수립 시
    @Override
    public void afterConnectionEstablished(WebSocketSession session) 
            throws Exception {
        
        sessions.add(session);
        
        // 사용자 ID 추출 (쿼리 파라미터에서)
        String userId = getUserId(session);
        if (userId != null) {
            userSessions.put(userId, session);
        }
        
        log.info("WebSocket 연결: sessionId={}, userId={}", 
            session.getId(), userId);
        
        // 환영 메시지 전송
        ChatMessage welcome = ChatMessage.builder()
            .type(MessageType.SYSTEM)
            .content("채팅방에 입장하셨습니다.")
            .sender("SYSTEM")
            .timestamp(LocalDateTime.now())
            .build();
        
        session.sendMessage(new TextMessage(
            new ObjectMapper().writeValueAsString(welcome)
        ));
        
        // 다른 사용자들에게 입장 알림
        broadcastMessage(ChatMessage.builder()
            .type(MessageType.JOIN)
            .sender(userId)
            .content(userId + "님이 입장하셨습니다.")
            .timestamp(LocalDateTime.now())
            .build(), session);
    }
    
    // 2. 메시지 수신 시
    @Override
    protected void handleTextMessage(WebSocketSession session, 
                                     TextMessage message) throws Exception {
        
        String payload = message.getPayload();
        log.info("메시지 수신: sessionId={}, payload={}", 
            session.getId(), payload);
        
        try {
            // JSON 파싱
            ObjectMapper mapper = new ObjectMapper();
            ChatMessage chatMessage = mapper.readValue(payload, ChatMessage.class);
            
            // 타임스탬프 추가
            chatMessage.setTimestamp(LocalDateTime.now());
            
            // 메시지 타입별 처리
            switch (chatMessage.getType()) {
                case CHAT:
                    // 일반 채팅 메시지 - 모두에게 전송
                    broadcastMessage(chatMessage, null);
                    break;
                    
                case PRIVATE:
                    // 특정 사용자에게만 전송
                    sendToUser(chatMessage.getReceiver(), chatMessage);
                    break;
                    
                case TYPING:
                    // 타이핑 중 알림
                    broadcastMessage(chatMessage, session);
                    break;
                    
                default:
                    log.warn("알 수 없는 메시지 타입: {}", chatMessage.getType());
            }
            
        } catch (Exception e) {
            log.error("메시지 처리 실패: {}", payload, e);
            
            // 에러 메시지 전송
            sendErrorMessage(session, "메시지 처리 중 오류가 발생했습니다.");
        }
    }
    
    // 3. 연결 종료 시
    @Override
    public void afterConnectionClosed(WebSocketSession session, 
                                      CloseStatus status) throws Exception {
        
        String userId = getUserId(session);
        
        sessions.remove(session);
        if (userId != null) {
            userSessions.remove(userId);
        }
        
        log.info("WebSocket 연결 종료: sessionId={}, userId={}, status={}", 
            session.getId(), userId, status);
        
        // 퇴장 알림
        if (userId != null) {
            broadcastMessage(ChatMessage.builder()
                .type(MessageType.LEAVE)
                .sender(userId)
                .content(userId + "님이 퇴장하셨습니다.")
                .timestamp(LocalDateTime.now())
                .build(), null);
        }
    }
    
    // 4. 에러 발생 시
    @Override
    public void handleTransportError(WebSocketSession session, 
                                     Throwable exception) throws Exception {
        
        log.error("WebSocket 에러: sessionId={}", session.getId(), exception);
        
        // 세션 정리
        sessions.remove(session);
        String userId = getUserId(session);
        if (userId != null) {
            userSessions.remove(userId);
        }
        
        // 연결 종료
        if (session.isOpen()) {
            session.close(CloseStatus.SERVER_ERROR);
        }
    }
    
    // === 헬퍼 메서드 ===
    
    // 모든 세션에 메시지 전송 (브로드캐스트)
    private void broadcastMessage(ChatMessage message, 
                                  WebSocketSession excludeSession) {
        
        ObjectMapper mapper = new ObjectMapper();
        
        sessions.forEach(session -> {
            if (session.isOpen() && !session.equals(excludeSession)) {
                try {
                    String json = mapper.writeValueAsString(message);
                    session.sendMessage(new TextMessage(json));
                } catch (Exception e) {
                    log.error("메시지 전송 실패: sessionId={}", 
                        session.getId(), e);
                }
            }
        });
    }
    
    // 특정 사용자에게만 전송
    private void sendToUser(String userId, ChatMessage message) {
        WebSocketSession session = userSessions.get(userId);
        
        if (session != null && session.isOpen()) {
            try {
                String json = new ObjectMapper().writeValueAsString(message);
                session.sendMessage(new TextMessage(json));
            } catch (Exception e) {
                log.error("메시지 전송 실패: userId={}", userId, e);
            }
        } else {
            log.warn("사용자 세션 없음: userId={}", userId);
        }
    }
    
    // 에러 메시지 전송
    private void sendErrorMessage(WebSocketSession session, String errorMsg) {
        try {
            ChatMessage error = ChatMessage.builder()
                .type(MessageType.ERROR)
                .content(errorMsg)
                .timestamp(LocalDateTime.now())
                .build();
            
            String json = new ObjectMapper().writeValueAsString(error);
            session.sendMessage(new TextMessage(json));
        } catch (Exception e) {
            log.error("에러 메시지 전송 실패", e);
        }
    }
    
    // URI에서 사용자 ID 추출
    private String getUserId(WebSocketSession session) {
        URI uri = session.getUri();
        if (uri != null && uri.getQuery() != null) {
            String query = uri.getQuery();
            String[] params = query.split("&");
            for (String param : params) {
                String[] keyValue = param.split("=");
                if (keyValue.length == 2 && "userId".equals(keyValue[0])) {
                    return keyValue[1];
                }
            }
        }
        return null;
    }
}
```

### 메시지 DTO
```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatMessage {
    
    private MessageType type;
    private String sender;
    private String receiver;  // PRIVATE 메시지용
    private String content;
    private LocalDateTime timestamp;
    
    public enum MessageType {
        CHAT,      // 일반 채팅
        JOIN,      // 입장
        LEAVE,     // 퇴장
        PRIVATE,   // 1:1 메시지
        TYPING,    // 타이핑 중
        SYSTEM,    // 시스템 메시지
        ERROR      // 에러
    }
}
```

## 3. Handshake Interceptor (인증/검증)

### JWT 토큰 검증 인터셉터
```java
@Component
@Slf4j
public class WebSocketAuthInterceptor implements HandshakeInterceptor {
    
    @Autowired
    private JwtTokenProvider jwtTokenProvider;
    
    @Override
    public boolean beforeHandshake(ServerHttpRequest request, 
                                   ServerHttpResponse response,
                                   WebSocketHandler wsHandler, 
                                   Map<String, Object> attributes) 
            throws Exception {
        
        if (request instanceof ServletServerHttpRequest) {
            ServletServerHttpRequest servletRequest = 
                (ServletServerHttpRequest) request;
            
            HttpServletRequest httpRequest = servletRequest.getServletRequest();
            
            // 1. 토큰 추출
            String token = extractToken(httpRequest);
            
            if (token == null) {
                log.warn("WebSocket 인증 실패: 토큰 없음");
                return false;
            }
            
            // 2. 토큰 검증
            if (!jwtTokenProvider.validateToken(token)) {
                log.warn("WebSocket 인증 실패: 유효하지 않은 토큰");
                return false;
            }
            
            // 3. 사용자 정보 추출 및 attributes에 저장
            String userId = jwtTokenProvider.getUserId(token);
            attributes.put("userId", userId);
            attributes.put("token", token);
            
            log.info("WebSocket 인증 성공: userId={}", userId);
            return true;
        }
        
        return false;
    }
    
    @Override
    public void afterHandshake(ServerHttpRequest request, 
                              ServerHttpResponse response,
                              WebSocketHandler wsHandler, 
                              Exception exception) {
        
        if (exception != null) {
            log.error("WebSocket Handshake 실패", exception);
        }
    }
    
    private String extractToken(HttpServletRequest request) {
        // 1. 헤더에서 추출
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        
        // 2. 쿼리 파라미터에서 추출 (WebSocket은 헤더 설정 어려울 수 있음)
        String tokenParam = request.getParameter("token");
        if (tokenParam != null) {
            return tokenParam;
        }
        
        return null;
    }
}
```

### 설정에 인터셉터 추가
```java
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {
    
    @Autowired
    private ChatWebSocketHandler chatWebSocketHandler;
    
    @Autowired
    private WebSocketAuthInterceptor authInterceptor;
    
    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry
            .addHandler(chatWebSocketHandler, "/ws/chat")
            .setAllowedOrigins("*")
            .addInterceptors(authInterceptor);  // 인증 인터셉터 추가
    }
}
```

## 4. 클라이언트 구현 (JavaScript)

### 기본 연결
```javascript
class WebSocketClient {
    constructor(url, token) {
        this.url = url;
        this.token = token;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect() {
        // 토큰을 쿼리 파라미터로 전달
        this.socket = new WebSocket(`${this.url}?token=${this.token}`);
        
        this.socket.onopen = () => {
            console.log('WebSocket 연결 성공');
            this.reconnectAttempts = 0;
            this.onConnected();
        };
        
        this.socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket 에러:', error);
        };
        
        this.socket.onclose = (event) => {
            console.log('WebSocket 연결 종료:', event.code, event.reason);
            this.onDisconnected();
            
            // 재연결 시도
            if (event.code !== 1000 && 
                this.reconnectAttempts < this.maxReconnectAttempts) {
                
                const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
                console.log(`${delay}ms 후 재연결 시도...`);
                
                setTimeout(() => {
                    this.reconnectAttempts++;
                    this.connect();
                }, delay);
            }
        };
    }
    
    sendMessage(type, content, receiver = null) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            const message = {
                type: type,
                content: content,
                receiver: receiver,
                sender: this.userId
            };
            
            this.socket.send(JSON.stringify(message));
        } else {
            console.error('WebSocket이 연결되지 않음');
        }
    }
    
    handleMessage(message) {
        switch (message.type) {
            case 'CHAT':
                this.onChatMessage(message);
                break;
            case 'JOIN':
                this.onUserJoin(message);
                break;
            case 'LEAVE':
                this.onUserLeave(message);
                break;
            case 'SYSTEM':
                this.onSystemMessage(message);
                break;
            case 'ERROR':
                this.onError(message);
                break;
        }
    }
    
    // 오버라이드할 메서드들
    onConnected() {}
    onDisconnected() {}
    onChatMessage(message) {}
    onUserJoin(message) {}
    onUserLeave(message) {}
    onSystemMessage(message) {}
    onError(message) {}
    
    disconnect() {
        if (this.socket) {
            this.socket.close(1000, '정상 종료');
        }
    }
}

// 사용 예시
const chatClient = new WebSocketClient('ws://localhost:8080/ws/chat', userToken);

chatClient.onConnected = () => {
    console.log('채팅 연결됨');
};

chatClient.onChatMessage = (message) => {
    displayMessage(message);
};

chatClient.connect();

// 메시지 전송
chatClient.sendMessage('CHAT', '안녕하세요!');
```

## 5. BizSync 프로젝트 실전 예시

### 실시간 문서 협업
```java
@Component
@Slf4j
public class DocumentWebSocketHandler extends TextWebSocketHandler {
    
    // 문서별 세션 관리
    private final Map<Long, Set<WebSocketSession>> documentSessions = 
        new ConcurrentHashMap<>();
    
    @Override
    protected void handleTextMessage(WebSocketSession session, 
                                     TextMessage message) throws Exception {
        
        String payload = message.getPayload();
        DocumentEditEvent event = 
            new ObjectMapper().readValue(payload, DocumentEditEvent.class);
        
        Long documentId = event.getDocumentId();
        
        // 같은 문서를 보고 있는 다른 사용자들에게 전송
        Set<WebSocketSession> sessions = documentSessions.get(documentId);
        if (sessions != null) {
            sessions.forEach(s -> {
                if (s.isOpen() && !s.equals(session)) {
                    try {
                        s.sendMessage(message);
                    } catch (Exception e) {
                        log.error("메시지 전송 실패", e);
                    }
                }
            });
        }
    }
    
    // 문서 구독
    public void subscribeDocument(WebSocketSession session, Long documentId) {
        documentSessions
            .computeIfAbsent(documentId, k -> ConcurrentHashMap.newKeySet())
            .add(session);
    }
    
    // 문서 구독 해제
    public void unsubscribeDocument(WebSocketSession session, Long documentId) {
        Set<WebSocketSession> sessions = documentSessions.get(documentId);
        if (sessions != null) {
            sessions.remove(session);
            if (sessions.isEmpty()) {
                documentSessions.remove(documentId);
            }
        }
    }
}
```

## 관련 개념
- [[WebSocket-기본개념]] - WebSocket 프로토콜
- [[WebSocket-STOMP프로토콜]] - STOMP 메시징
- [[WebSocket-Redis연동과확장]] - 다중 서버 환경
- [[Spring-Security]] - 인증/인가
- [[Redis-PubSub과트랜잭션]] - Redis 메시징

## 면접 질문

1. **Spring WebSocket의 주요 구성 요소는?**
   - WebSocketConfigurer: 엔드포인트 등록
   - WebSocketHandler: 메시지 처리
   - WebSocketSession: 세션 관리
   - HandshakeInterceptor: 인증/검증

2. **WebSocket에서 인증은 어떻게 처리하나요?**
   - HandshakeInterceptor에서 토큰 검증
   - 쿼리 파라미터 또는 헤더로 토큰 전달
   - 검증 실패 시 연결 거부

3. **연결 종료 시 어떻게 처리하나요?**
   - afterConnectionClosed에서 세션 제거
   - Map에서 사용자 정보 삭제
   - 다른 사용자들에게 퇴장 알림

4. **모든 사용자에게 메시지를 보내려면?**
   - Set<WebSocketSession>에 저장
   - forEach로 모든 세션에 sendMessage

5. **프로젝트에서 WebSocket을 어떻게 사용했나요?**
   - 실시간 문서 협업 (BizSync)
   - 사용자 편집 내용 즉시 동기화
   - JWT 토큰으로 인증

## 참고 자료
- [Spring WebSocket 공식 문서](https://docs.spring.io/spring-framework/reference/web/websocket.html)
- [Spring Boot WebSocket](https://spring.io/guides/gs/messaging-stomp-websocket/)
- [WebSocket Security](https://docs.spring.io/spring-security/reference/servlet/integrations/websocket.html)
