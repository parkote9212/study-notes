---
tags: interview, websocket, stomp, bizsync
created: 2026-01-23
difficulty: 중상
---

# BizSync - WebSocket (STOMP) 실시간 통신 면접질문

## 질문 1
> BizSync에서 WebSocket과 STOMP 프로토콜을 함께 사용한 이유와 STOMP가 순수 WebSocket 대비 제공하는 장점을 설명해주세요.

## 핵심 답변 (3줄)
1. STOMP(Simple Text Oriented Messaging Protocol)는 WebSocket 위에서 동작하는 메시징 프로토콜로, Pub/Sub 패턴을 쉽게 구현할 수 있습니다
2. 순수 WebSocket은 양방향 통신만 제공하지만, STOMP는 목적지(destination) 개념과 브로커 구조를 통해 메시지 라우팅을 표준화합니다
3. Spring Framework가 STOMP를 기본 지원하여 @MessageMapping과 SimpMessagingTemplate으로 쉽게 구현할 수 있습니다

## 상세 설명
순수 WebSocket은 클라이언트와 서버 간의 양방향 통신 채널을 제공하지만, 메시지 포맷이나 라우팅 규칙을 정의하지 않습니다. 개발자가 직접 메시지 구조를 설계하고 파싱 로직을 구현해야 합니다.

반면 STOMP는 WebSocket 위에서 동작하는 텍스트 기반 프로토콜로, 메시지 프레임(CONNECT, SUBSCRIBE, SEND 등)과 헤더 구조를 표준화합니다. 이를 통해 Pub/Sub 패턴을 간단하게 구현할 수 있습니다.

BizSync에서는 실시간 채팅, 칸반 보드 동기화, 알림 전송에 WebSocket/STOMP를 활용합니다. 예를 들어 칸반 보드에서 한 사용자가 업무를 이동하면, 같은 프로젝트를 보고 있는 모든 사용자에게 변경사항이 실시간으로 전파됩니다.

STOMP의 장점은 클라이언트가 특정 토픽(/topic/projects/123)을 구독하고, 서버가 해당 토픽으로 메시지를 발행하면 구독자 전원에게 자동으로 전달된다는 점입니다. 이런 브로커 패턴을 순수 WebSocket으로 구현하려면 연결 관리, 메시지 라우팅, 구독자 추적을 모두 직접 구현해야 합니다.

## 코드 예시 (필요시)
```java
// WebSocketConfig.java - STOMP 설정
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        // WebSocket 엔드포인트 등록
        registry.addEndpoint("/ws")
                .setAllowedOriginPatterns("*");
    }
    
    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        // 구독 경로: 클라이언트가 메시지를 받을 prefix
        registry.enableSimpleBroker("/sub", "/topic");
        
        // 발행 경로: 클라이언트가 메시지를 보낼 prefix
        registry.setApplicationDestinationPrefixes("/pub", "/app");
    }
}

// 프론트엔드 - STOMP 클라이언트
const client = new Client({
    brokerURL: "ws://localhost:8080/ws",
    onConnect: () => {
        // 구독 (Subscribe)
        client.subscribe("/topic/projects/123", (message) => {
            console.log(message.body);
        });
    }
});
client.activate();
```

## 꼬리 질문 예상
- SockJS를 사용하지 않은 이유는 무엇인가요? (WebSocket을 지원하지 않는 브라우저 대응)
- STOMP 대신 Socket.IO를 사용할 수도 있지 않나요? 차이점은 무엇인가요?
- Spring의 Simple Broker와 외부 메시지 브로커(RabbitMQ, Kafka)를 사용하는 경우의 차이는 무엇인가요?

## 참고
- [[WebSocket 프로토콜 동작 원리]]
- [[STOMP vs Socket.IO 비교]]

---

## 질문 2
> useBoardSocket 훅에서 reconnectDelay를 설정한 이유와 네트워크 단절 시 재연결 전략을 설명해주세요.

## 핵심 답변 (3줄)
1. 네트워크 불안정이나 서버 재시작 등으로 연결이 끊어질 수 있으므로 자동 재연결 메커니즘이 필수입니다
2. reconnectDelay를 5초로 설정하여 연결 실패 시 즉시 재시도하지 않고 지연시켜 서버 부하를 방지합니다
3. @stomp/stompjs의 reconnectDelay는 자동으로 exponential backoff를 적용하여 재시도 간격을 점진적으로 늘립니다

## 상세 설명
실시간 애플리케이션에서 WebSocket 연결은 다양한 이유로 끊어질 수 있습니다. 사용자의 네트워크 전환(Wi-Fi → 모바일), 서버 재시작, 방화벽 타임아웃 등이 대표적입니다.

reconnectDelay는 연결이 끊어졌을 때 재연결을 시도하기 전 대기 시간입니다. BizSync는 5000ms(5초)로 설정했습니다. 이는 너무 짧으면 서버가 복구되지 않은 상태에서 계속 재시도하여 부하를 주고, 너무 길면 사용자 경험이 나빠지는 것을 고려한 값입니다.

@stomp/stompjs는 기본적으로 exponential backoff 전략을 사용합니다. 첫 재연결은 5초 후, 실패하면 10초, 20초... 이런 식으로 점진적으로 간격이 늘어나 최대 30초까지 증가합니다. 이를 통해 일시적 네트워크 문제에는 빠르게 복구하면서도, 지속적인 장애에는 서버 부하를 최소화합니다.

프론트엔드에서는 useEffect의 cleanup 함수에서 client.deactivate()를 호출하여, 컴포넌트 언마운트 시 연결을 확실히 종료합니다. 이를 통해 메모리 누수와 불필요한 연결 유지를 방지합니다.

## 코드 예시 (필요시)
```typescript
// useBoardSocket.ts
export const useBoardSocket = (
  projectId: string | undefined,
  onUpdate: () => void,
) => {
  const client = useRef<Client | null>(null);
  
  useEffect(() => {
    if (!projectId) return;
    
    client.current = new Client({
      brokerURL: WS_URL,
      reconnectDelay: 5000,  // 5초 대기 후 재연결
      
      onConnect: () => {
        console.log(`Connected to Project ${projectId}`);
        client.current?.subscribe(`/topic/projects/${projectId}`, (message) => {
          if (message.body === "BOARD_UPDATE") {
            onUpdate();
          }
        });
      },
      
      onStompError: (frame) => {
        console.error("Broker error: " + frame.headers["message"]);
      },
      
      onWebSocketClose: (event) => {
        console.log("Connection closed:", event.reason);
        // reconnectDelay 후 자동으로 재연결 시도
      }
    });
    
    client.current.activate();
    
    // Cleanup: 언마운트 시 연결 종료
    return () => {
      console.log("Disconnecting...");
      client.current?.deactivate();
    };
  }, [projectId, onUpdate]);
};
```

## 꼬리 질문 예상
- maxReconnectAttempts를 설정하지 않으면 어떤 문제가 발생할 수 있나요?
- Heartbeat 메커니즘은 무엇이며, 어떻게 설정하나요?
- React에서 WebSocket을 useState가 아닌 useRef로 관리하는 이유는 무엇인가요?

## 참고
- [[WebSocket 연결 관리 전략]]
- [[Exponential Backoff 알고리즘]]

---

## 질문 3
> @MessageMapping과 SimpMessagingTemplate의 역할 차이와 메시지 발행/구독 흐름을 설명해주세요.

## 핵심 답변 (3줄)
1. @MessageMapping은 클라이언트가 특정 destination으로 보낸 메시지를 처리하는 핸들러 메서드를 정의합니다 (Publish 수신)
2. SimpMessagingTemplate은 서버에서 특정 destination으로 메시지를 발행하여 구독자들에게 전달하는 도구입니다 (Subscribe 발행)
3. 클라이언트는 SEND로 메시지를 발행하고, SUBSCRIBE로 메시지를 구독하며, 서버는 이 둘을 연결하는 중개자 역할을 합니다

## 상세 설명
STOMP는 Pub/Sub 패턴 기반의 메시징 프로토콜입니다. BizSync의 채팅 기능을 예로 들면 다음과 같은 흐름입니다.

1. 클라이언트 A가 "/pub/chat/message"로 메시지 전송 (SEND 프레임)
2. 서버의 @MessageMapping("/chat/message") 메서드가 메시지 수신
3. ChatService에서 DB에 메시지 저장
4. SimpMessagingTemplate.convertAndSend()로 "/sub/chat/room/123"에 메시지 발행
5. 해당 방을 구독(SUBSCRIBE)하고 있던 모든 클라이언트에게 메시지 전달

@MessageMapping은 Spring MVC의 @RequestMapping과 유사하게, 특정 경로로 들어온 메시지를 처리하는 컨트롤러 메서드입니다. 반면 SimpMessagingTemplate은 서버에서 능동적으로 메시지를 발행할 때 사용하는 템플릿 객체입니다.

중요한 점은 @MessageMapping 메서드의 반환값을 @SendTo로 지정할 수도 있지만, BizSync는 SimpMessagingTemplate을 명시적으로 사용합니다. 이는 비즈니스 로직(DB 저장, 검증 등)을 먼저 처리한 후 결과를 발행할 수 있어 더 유연합니다.

## 코드 예시 (필요시)
```java
// ChatController.java
@RestController
@RequiredArgsConstructor
public class ChatController {
    
    private final SimpMessagingTemplate messagingTemplate;
    private final ChatService chatService;
    
    // 1. 클라이언트 메시지 수신 (Publish 수신)
    @MessageMapping("/chat/message")  // 클라이언트가 /pub/chat/message로 전송
    public void sendMessage(ChatMessageDTO message) {
        // 2. 비즈니스 로직: DB 저장
        ChatMessageDTO savedMessage = chatService.saveMessage(message);
        
        // 3. 구독자에게 발행 (Subscribe 발행)
        messagingTemplate.convertAndSend(
            "/sub/chat/room/" + savedMessage.roomId(), 
            savedMessage
        );
    }
}

// 프론트엔드 - 메시지 발행 (Publish)
client.publish({
    destination: "/pub/chat/message",
    body: JSON.stringify({
        roomId: 123,
        content: "Hello!",
        senderId: 1
    })
});

// 프론트엔드 - 메시지 구독 (Subscribe)
client.subscribe("/sub/chat/room/123", (message) => {
    const chatMessage = JSON.parse(message.body);
    console.log(chatMessage.content);
});
```

## 꼬리 질문 예상
- @SendTo와 SimpMessagingTemplate의 차이는 무엇이며, 언제 어떤 것을 사용해야 하나요?
- convertAndSend()와 convertAndSendToUser()의 차이는 무엇인가요?
- Message Broker의 메모리 기반 큐가 가득 찬 경우 어떻게 처리되나요?

## 참고
- [[STOMP 메시지 흐름]]
- [[Spring WebSocket Annotation]]

---

## 질문 4
> WebSocket 연결에 JWT 인증을 적용하는 방법과 STOMP 헤더에 토큰을 전달하는 전략을 설명해주세요.

## 핵심 답변 (3줄)
1. WebSocket은 HTTP Upgrade 요청으로 시작하므로 최초 핸드셰이크 시 쿼리 파라미터나 HTTP 헤더로 JWT를 전달할 수 있습니다
2. STOMP 연결 후에는 CONNECT 프레임의 커스텀 헤더에 토큰을 포함시켜 매 메시지마다 인증을 검증할 수 있습니다
3. Spring Security의 ChannelInterceptor를 구현하여 STOMP 메시지를 가로채고 JWT 검증 로직을 추가할 수 있습니다

## 상세 설명
WebSocket은 처음 연결 시 HTTP Upgrade 요청을 보내므로, 이 시점에 JWT를 전달하는 것이 일반적입니다. 방법은 크게 세 가지입니다:

1. **쿼리 파라미터**: ws://localhost:8080/ws?token=eyJhbGc... 형태로 URL에 토큰 포함
2. **HTTP 헤더**: 초기 핸드셰이크 시 Authorization 헤더에 토큰 포함
3. **STOMP 헤더**: CONNECT 프레임에 커스텀 헤더로 토큰 포함

BizSync는 현재 WebSocket 엔드포인트(/ws)를 permitAll()로 열어두고 있지만, 프로덕션 환경에서는 인증이 필요합니다. 이를 위해 HandshakeInterceptor를 구현하여 핸드셰이크 단계에서 토큰을 검증하거나, ChannelInterceptor를 구현하여 STOMP 메시지 레벨에서 검증할 수 있습니다.

ChannelInterceptor 방식이 더 권장되는데, 이는 재연결 시마다 토큰을 새로 전달할 수 있고, 메시지별 세밀한 권한 제어가 가능하기 때문입니다. 예를 들어 특정 프로젝트의 채팅방을 구독하려면 해당 프로젝트 멤버여야 한다는 검증을 추가할 수 있습니다.

## 코드 예시 (필요시)
```java
// JwtChannelInterceptor.java - STOMP 인증 인터셉터
@Component
public class JwtChannelInterceptor implements ChannelInterceptor {
    
    private final JwtProvider jwtProvider;
    
    @Override
    public Message<?> preSend(Message<?> message, MessageChannel channel) {
        StompHeaderAccessor accessor = 
            StompHeaderAccessor.wrap(message);
        
        if (StompCommand.CONNECT.equals(accessor.getCommand())) {
            // CONNECT 프레임에서 토큰 추출
            String token = accessor.getFirstNativeHeader("Authorization");
            
            if (token != null && token.startsWith("Bearer ")) {
                token = token.substring(7);
                
                if (jwtProvider.validateToken(token)) {
                    Long userId = jwtProvider.getUserId(token);
                    accessor.setUser(new JwtAuthentication(userId));
                }
            }
        }
        
        return message;
    }
}

// WebSocketConfig.java - 인터셉터 등록
@Override
public void configureClientInboundChannel(ChannelRegistration registration) {
    registration.interceptors(jwtChannelInterceptor);
}

// 프론트엔드 - 토큰 전달
const client = new Client({
    brokerURL: WS_URL,
    connectHeaders: {
        Authorization: `Bearer ${accessToken}`  // JWT 토큰 전달
    }
});
```

## 꼬리 질문 예상
- WebSocket 연결 후 Access Token이 만료되면 어떻게 처리해야 하나요?
- 쿼리 파라미터로 토큰을 전달하는 것의 보안 위험은 무엇인가요?
- User Principal을 사용한 개인화 메시징은 어떻게 구현하나요?

## 참고
- [[WebSocket 인증 전략]]
- [[STOMP Header 활용]]

---

## 질문 5
> 칸반 보드의 실시간 동기화에서 "BOARD_UPDATE" 메시지만 전송하고 전체 데이터를 다시 fetch하는 방식의 장단점을 설명해주세요.

## 핵심 답변 (3줄)
1. 메시지 크기를 최소화(단순 문자열)하여 네트워크 대역폭과 브로커 메모리 사용량을 줄일 수 있습니다
2. 변경된 데이터만 전송하는 방식보다 구현이 단순하고, 데이터 일관성을 보장하기 쉽습니다
3. 다만 동시 사용자가 많거나 변경이 빈번하면 불필요한 API 요청이 증가하여 서버 부하가 늘어날 수 있습니다

## 상세 설명
BizSync의 칸반 보드 동기화는 "알림 방식(Notification Pattern)"을 사용합니다. 사용자 A가 업무를 이동하면, 서버는 같은 프로젝트를 보고 있는 모든 사용자에게 "BOARD_UPDATE"라는 간단한 메시지만 브로드캐스트합니다. 이 메시지를 받은 클라이언트는 자체적으로 API를 호출하여 최신 데이터를 가져옵니다.

**장점:**
1. WebSocket 메시지가 매우 가볍습니다 (수 바이트)
2. 서버 로직이 단순합니다 - 변경 감지만 알리면 됨
3. 데이터 일관성 보장이 쉽습니다 - 항상 DB의 최신 상태를 fetch
4. 복잡한 변경사항(여러 엔티티 동시 수정 등)도 동일하게 처리

**단점:**
1. 클라이언트가 변경되지 않은 데이터도 모두 다시 받습니다
2. HTTP API 호출이 추가로 발생하여 레이턴시가 증가합니다
3. 동시 사용자가 많으면 API 서버 부하가 증가합니다

대안으로 "Delta Sync" 방식이 있습니다. 변경된 데이터만 WebSocket으로 전송하는 방식인데, 구현이 복잡하고 클라이언트가 로컬 상태를 정확히 업데이트해야 하는 부담이 있습니다. BizSync는 현재 단순성과 안정성을 우선시하여 알림 방식을 채택했습니다.

## 코드 예시 (필요시)
```typescript
// useBoardSocket.ts - 알림 방식
export const useBoardSocket = (
  projectId: string | undefined,
  onUpdate: () => void,  // 데이터 재fetch 콜백
) => {
  useEffect(() => {
    if (!projectId) return;
    
    const client = new Client({
      brokerURL: WS_URL,
      onConnect: () => {
        client.subscribe(`/topic/projects/${projectId}`, (message) => {
          if (message.body === "BOARD_UPDATE") {  // 단순 문자열
            console.log("Update detected, refetching data...");
            onUpdate();  // 전체 데이터 다시 fetch
          }
        });
      }
    });
    
    client.activate();
    return () => client.deactivate();
  }, [projectId, onUpdate]);
};

// KanbanService.java - 알림 발행
@Transactional
public void moveTask(Long taskId, Long targetColumnId, Integer newSequence) {
    Task task = taskRepository.findById(taskId)
        .orElseThrow(() -> new IllegalArgumentException("업무를 찾을 수 없습니다."));
    
    task.updatePosition(targetColumn, newSequence);
    
    // 변경 감지 알림만 전송 (데이터 미포함)
    Long projectId = task.getProjectId();
    messagingTemplate.convertAndSend(
        "/topic/projects/" + projectId, 
        "BOARD_UPDATE"  // 단순 문자열
    );
}
```

## 꼬리 질문 예상
- Delta Sync 방식을 구현한다면 어떤 데이터 구조를 사용하시겠습니까?
- Optimistic UI Update를 적용한다면 어떻게 충돌을 해결하시겠습니까?
- WebSocket과 Server-Sent Events(SSE)를 비교했을 때 이 사용 사례에 더 적합한 것은 무엇인가요?

## 참고
- [[실시간 데이터 동기화 패턴]]
- [[Optimistic vs Pessimistic Update]]

---

## 질문 6
> WebSocketEventListener에서 SessionConnectEvent와 SessionSubscribeEvent를 감지하는 이유와 실무에서의 활용 방안을 설명해주세요.

## 핵심 답변 (3줄)
1. SessionConnectEvent는 WebSocket 연결 생성을 감지하여 접속 로그, 동시 접속자 수 추적, 인증 검증 등에 활용할 수 있습니다
2. SessionSubscribeEvent는 특정 토픽 구독을 감지하여 권한 검증, 구독자 목록 관리, 통계 수집 등에 활용할 수 있습니다
3. 이벤트 기반 아키텍처를 통해 WebSocket 생명주기를 모니터링하고, 부가 기능을 비침투적으로 추가할 수 있습니다

## 상세 설명
Spring WebSocket은 다양한 이벤트를 발행하여 연결 생명주기를 추적할 수 있게 합니다. BizSync에서는 WebSocketEventListener로 이러한 이벤트를 감지합니다.

**SessionConnectEvent**: 클라이언트가 STOMP CONNECT 프레임을 보낼 때 발생합니다. 이 시점에서 다음을 수행할 수 있습니다:
- 접속 로그 기록 (누가, 언제, 어디서)
- 동시 접속자 수 카운팅
- 세션 ID와 사용자 매핑 저장
- IP 차단 목록 확인
- Rate Limiting 적용

**SessionSubscribeEvent**: 클라이언트가 특정 destination을 구독할 때 발생합니다. 활용 방안:
- 구독 권한 검증 (예: 프로젝트 멤버만 해당 채팅방 구독 가능)
- 구독자 목록 관리 (누가 어떤 방을 보고 있는지)
- 구독 통계 수집 (인기 채널 분석)
- 자동 입장 메시지 전송

현재 BizSync는 단순 로깅만 하고 있지만, 프로덕션 환경에서는 이를 확장하여 모니터링, 보안, 분석 기능을 추가할 수 있습니다.

## 코드 예시 (필요시)
```java
// WebSocketEventListener.java - 이벤트 처리
@Slf4j
@Component
public class WebSocketEventListener {
    
    private final ConcurrentHashMap<String, String> sessionUserMap = 
        new ConcurrentHashMap<>();
    
    @EventListener
    public void handleWebSocketConnectListener(SessionConnectEvent event) {
        StompHeaderAccessor accessor = StompHeaderAccessor.wrap(event.getMessage());
        String sessionId = accessor.getSessionId();
        
        // 사용자 정보 추출 (JWT에서)
        Principal user = accessor.getUser();
        if (user != null) {
            sessionUserMap.put(sessionId, user.getName());
            log.info("User {} connected. SessionId: {}", user.getName(), sessionId);
        }
        
        // 동시 접속자 수 추적
        log.info("Active connections: {}", sessionUserMap.size());
    }
    
    @EventListener
    public void handleWebSocketSubscribeListener(SessionSubscribeEvent event) {
        StompHeaderAccessor accessor = StompHeaderAccessor.wrap(event.getMessage());
        String destination = (String) accessor.getHeader("simpDestination");
        String sessionId = accessor.getSessionId();
        
        log.info("User {} subscribed to {}", 
            sessionUserMap.get(sessionId), destination);
        
        // 권한 검증 예시
        if (destination.startsWith("/sub/chat/room/")) {
            String roomId = destination.substring("/sub/chat/room/".length());
            // 채팅방 접근 권한 확인 로직
        }
    }
    
    @EventListener
    public void handleWebSocketDisconnectListener(SessionDisconnectEvent event) {
        String sessionId = event.getSessionId();
        String username = sessionUserMap.remove(sessionId);
        
        log.info("User {} disconnected. SessionId: {}", username, sessionId);
        log.info("Remaining connections: {}", sessionUserMap.size());
    }
}
```

## 꼬리 질문 예상
- SessionDisconnectEvent는 네트워크 단절 시 즉시 발생하나요, 아니면 지연이 있나요?
- WebSocket 세션과 HTTP 세션의 차이는 무엇인가요?
- 구독자 수를 실시간으로 화면에 표시하려면 어떻게 구현해야 하나요?

## 참고
- [[Spring WebSocket Events]]
- [[세션 관리 전략]]

---

## 질문 7
> Simple Broker를 사용할 때의 제약사항과 RabbitMQ나 Redis 같은 외부 브로커로 전환해야 하는 시점을 설명해주세요.

## 핵심 답변 (3줄)
1. Simple Broker는 인메모리 방식으로 단일 서버 환경에서는 충분하지만, 메시지 지속성이 없고 서버 재시작 시 연결이 모두 끊어집니다
2. 서버를 수평 확장(Scale-out)할 때는 외부 브로커가 필수이며, 서로 다른 서버 인스턴스 간 메시지 라우팅이 불가능하기 때문입니다
3. RabbitMQ나 Redis Pub/Sub은 클러스터 환경에서 메시지를 중앙 집중화하여 관리하고, 영속성과 고가용성을 제공합니다

## 상세 설명
Spring의 Simple Broker(`enableSimpleBroker()`)는 내장 인메모리 브로커로, 별도의 설치 없이 간단하게 STOMP 메시징을 구현할 수 있습니다. 하지만 다음과 같은 제약이 있습니다:

**Simple Broker의 제약:**
1. 단일 서버 전용 - 같은 JVM 프로세스 내 연결만 브로드캐스트 가능
2. 메시지 비영속성 - 서버 재시작 시 모든 메시지 소실
3. 제한된 기능 - 메시지 라우팅, 큐잉, 트랜잭션 등 고급 기능 없음
4. 확장성 한계 - 대규모 동시 접속 처리 어려움

**외부 브로커 전환 시점:**
- 서버 인스턴스가 2대 이상으로 증가할 때 (로드 밸런서 뒤)
- 동시 접속자가 수천 명 이상으로 증가할 때
- 메시지 영속성이 필요할 때 (채팅 이력 등)
- 복잡한 메시지 라우팅이 필요할 때

BizSync는 현재 단일 서버로 운영되므로 Simple Broker로 충분합니다. 하지만 향후 AWS ECS나 Kubernetes로 배포하여 여러 컨테이너를 실행한다면, RabbitMQ나 Redis를 도입해야 합니다.

## 코드 예시 (필요시)
```java
// Simple Broker (현재)
@Override
public void configureMessageBroker(MessageBrokerRegistry registry) {
    registry.enableSimpleBroker("/sub", "/topic");  // 인메모리
    registry.setApplicationDestinationPrefixes("/pub", "/app");
}

// RabbitMQ Broker (확장 시)
@Override
public void configureMessageBroker(MessageBrokerRegistry registry) {
    registry.enableStompBrokerRelay("/topic", "/queue")
        .setRelayHost("localhost")
        .setRelayPort(61613)
        .setClientLogin("guest")
        .setClientPasscode("guest");
    
    registry.setApplicationDestinationPrefixes("/app");
}

// Redis Pub/Sub (대안)
@Bean
public RedisMessageListenerContainer redisContainer() {
    RedisMessageListenerContainer container = 
        new RedisMessageListenerContainer();
    container.setConnectionFactory(redisConnectionFactory);
    // Redis Pub/Sub 설정
    return container;
}
```

## 꼬리 질문 예상
- RabbitMQ와 Kafka 중 어떤 것을 선택해야 하며, 차이점은 무엇인가요?
- Redis Pub/Sub은 메시지를 영속화하나요?
- 외부 브로커 도입 시 기존 코드를 얼마나 수정해야 하나요?

## 참고
- [[Message Broker 비교]]
- [[Spring WebSocket Scalability]]

---

## 질문 8
> WebSocket 연결 수가 증가할 때 발생할 수 있는 성능 문제와 최적화 전략을 설명해주세요.

## 핵심 답변 (3줄)
1. 각 WebSocket 연결은 서버의 스레드와 메모리를 소비하므로, 연결 수가 C10K(1만 개) 이상 증가하면 리소스 고갈 문제가 발생합니다
2. Netty 같은 Non-blocking I/O 기반 서버를 사용하고, 커넥션 풀링과 Heartbeat 타임아웃을 적절히 설정하여 리소스를 효율적으로 관리해야 합니다
3. 메시지 브로드캐스트 시 불필요한 직렬화를 피하고, 메시지 크기를 최소화하며, 필요시 메시지 압축을 적용합니다

## 상세 설명
WebSocket은 양방향 지속 연결(Persistent Connection)이므로 각 연결마다 서버 리소스를 계속 점유합니다. 전통적인 Blocking I/O 서버(Tomcat 등)에서는 각 연결당 하나의 스레드를 할당하므로, 연결 수가 증가하면 스레드 고갈 문제가 발생합니다.

**성능 문제:**
1. 스레드 고갈 - 연결당 1 스레드 모델의 한계
2. 메모리 압박 - 각 연결의 버퍼, 세션 정보 등
3. 브로드캐스트 오버헤드 - N명에게 메시지 전송 시 O(N) 비용
4. GC 압박 - 대량의 메시지 객체 생성/소멸

**최적화 전략:**
1. **Non-blocking I/O**: Spring WebFlux + Netty 사용하여 단일 스레드로 수천 개 연결 처리
2. **Heartbeat 설정**: 유휴 연결 자동 종료로 좀비 연결 방지
3. **메시지 최적화**: JSON 대신 Protobuf/MessagePack 사용, 압축 적용
4. **구독 필터링**: 브로드캐스트 전에 실제 구독자만 필터링
5. **로드 밸런싱**: Sticky Session으로 같은 방 사용자를 같은 서버로 라우팅

BizSync는 현재 수백 명 수준의 동시 접속을 가정하므로 기본 설정으로 충분하지만, 대규모 서비스로 성장하면 이러한 최적화가 필수입니다.

## 코드 예시 (필요시)
```java
// WebSocketConfig.java - Heartbeat 설정
@Override
public void configureMessageBroker(MessageBrokerRegistry registry) {
    registry.enableSimpleBroker("/sub", "/topic")
        .setHeartbeatValue(new long[] {10000, 10000});  // 10초마다 heartbeat
    
    registry.setApplicationDestinationPrefixes("/pub");
}

// 메시지 크기 최소화
@MessageMapping("/chat/message")
public void sendMessage(ChatMessageDTO message) {
    // 불필요한 필드 제거 후 전송
    ChatMessageDTO minimal = new ChatMessageDTO(
        message.roomId(),
        message.content(),
        message.senderId()
        // 나머지 필드는 제외
    );
    
    messagingTemplate.convertAndSend(
        "/sub/chat/room/" + message.roomId(), 
        minimal
    );
}

// 프론트엔드 - Heartbeat 설정
const client = new Client({
    brokerURL: WS_URL,
    heartbeatIncoming: 10000,  // 서버로부터 heartbeat 기대 간격
    heartbeatOutgoing: 10000,  // 클라이언트 heartbeat 전송 간격
    reconnectDelay: 5000
});
```

## 꼬리 질문 예상
- Sticky Session의 장단점은 무엇인가요?
- WebSocket과 HTTP/2 Server Push를 비교했을 때 어떤 것이 더 효율적인가요?
- Long Polling과 WebSocket의 리소스 사용량을 비교하면 어떤가요?

## 참고
- [[WebSocket 성능 최적화]]
- [[Non-blocking I/O 원리]]

---

## 질문 9
> 프론트엔드에서 useEffect의 dependency에 onUpdate 콜백을 포함시킨 이유와 발생할 수 있는 문제를 설명해주세요.

## 핵심 답변 (3줄)
1. onUpdate 콜백을 dependency에 포함시키면 콜백이 변경될 때마다 WebSocket 연결을 재생성하여 최신 콜백을 구독에 반영할 수 있습니다
2. 하지만 부모 컴포넌트가 리렌더링될 때마다 새로운 콜백 함수가 생성되면 불필요한 재연결이 발생하여 성능과 안정성에 문제가 생깁니다
3. useCallback으로 콜백을 메모이제이션하거나, useRef를 사용하여 안정적인 참조를 유지하는 것이 권장됩니다

## 상세 설명
React의 useEffect는 dependency 배열의 값이 변경될 때 effect를 재실행합니다. useBoardSocket에서 onUpdate를 dependency에 포함시키면, 이 콜백이 바뀔 때마다 WebSocket 연결을 끊고 다시 연결합니다.

**문제 상황:**
```typescript
// 부모 컴포넌트
function KanbanBoard() {
  const [data, setData] = useState([]);
  
  // 매 렌더링마다 새로운 함수 생성
  const handleUpdate = () => {
    fetchBoardData().then(setData);
  };
  
  // onUpdate가 매번 바뀌므로 WebSocket 재연결 반복
  useBoardSocket(projectId, handleUpdate);
}
```

이렇게 하면 부모 컴포넌트가 리렌더링될 때마다 handleUpdate가 새로 생성되고, WebSocket이 재연결됩니다. 이는 다음 문제를 야기합니다:
- 네트워크 오버헤드 (불필요한 재연결)
- 일시적 연결 끊김 (메시지 누락 가능)
- 서버 리소스 낭비

**해결 방법:**
1. useCallback으로 콜백 메모이제이션
2. useRef로 콜백을 감싸서 안정적인 참조 유지
3. dependency에서 제외하고 useRef.current로 접근

BizSync 코드를 개선한다면 useCallback을 추가하거나, useBoardSocket 내부에서 useRef를 사용하여 이 문제를 방지해야 합니다.

## 코드 예시 (필요시)
```typescript
// 문제: 매 렌더링마다 재연결
function KanbanBoard() {
  const [data, setData] = useState([]);
  
  const handleUpdate = () => {  // 매번 새로 생성
    fetchBoardData().then(setData);
  };
  
  useBoardSocket(projectId, handleUpdate);  // 재연결 반복
}

// 해결 1: useCallback 사용
function KanbanBoard() {
  const [data, setData] = useState([]);
  
  const handleUpdate = useCallback(() => {
    fetchBoardData().then(setData);
  }, []);  // 빈 배열: 한 번만 생성
  
  useBoardSocket(projectId, handleUpdate);  // 안정적
}

// 해결 2: useBoardSocket 내부에서 useRef 사용
export const useBoardSocket = (projectId, onUpdate) => {
  const onUpdateRef = useRef(onUpdate);
  
  useEffect(() => {
    onUpdateRef.current = onUpdate;  // 최신 콜백 유지
  }, [onUpdate]);
  
  useEffect(() => {
    if (!projectId) return;
    
    const client = new Client({
      onConnect: () => {
        client.subscribe(`/topic/projects/${projectId}`, () => {
          onUpdateRef.current();  // ref로 접근
        });
      }
    });
    
    client.activate();
    return () => client.deactivate();
  }, [projectId]);  // onUpdate 제외
};
```

## 꼬리 질문 예상
- useCallback의 dependency가 자주 변경되면 메모이제이션 효과가 없지 않나요?
- useRef와 useState의 차이는 무엇이며, 언제 각각을 사용해야 하나요?
- React 19의 useEvent Hook은 이 문제를 어떻게 해결하나요?

## 참고
- [[React useEffect 최적화]]
- [[useCallback vs useMemo vs useRef]]

---

## 질문 10
> WebSocket 메시지 유실을 방지하기 위한 전략과 메시지 신뢰성을 보장하는 방법을 설명해주세요.

## 핵심 답변 (3줄)
1. WebSocket은 TCP 기반이므로 전송 중 패킷 유실은 재전송으로 복구되지만, 연결 끊김이나 서버 재시작 시 버퍼의 메시지는 유실됩니다
2. 메시지에 고유 ID(sequence number)를 부여하고, 클라이언트가 수신한 메시지 ID를 추적하여 누락 감지 및 재전송 요청을 구현할 수 있습니다
3. 중요한 메시지는 DB에 영속화하고, ACK(확인) 메커니즘을 도입하여 전달 보장(at-least-once delivery)을 구현합니다

## 상세 설명
WebSocket은 신뢰성 있는 전송을 보장하지 않습니다. 다음 상황에서 메시지가 유실될 수 있습니다:

**메시지 유실 시나리오:**
1. 클라이언트가 오프라인 상태일 때 서버가 메시지 발행
2. 네트워크 단절 직전/직후의 메시지
3. 서버 재시작 중 Simple Broker 메모리 소실
4. 클라이언트 재연결 중 발생한 이벤트

**신뢰성 보장 전략:**

1. **메시지 영속화**: 채팅 메시지처럼 중요한 데이터는 DB에 먼저 저장 후 WebSocket으로 전송. 클라이언트는 접속 시 마지막 메시지 이후의 내역을 HTTP API로 fetch.

2. **Sequence Number**: 각 메시지에 순차 ID 부여. 클라이언트가 lastSeenId를 추적하고, 재연결 시 누락된 메시지를 서버에 요청.

3. **ACK 메커니즘**: 클라이언트가 메시지 수신 시 ACK 응답을 보내고, 서버는 ACK를 못 받으면 재전송.

4. **Idempotency**: 메시지를 중복 수신해도 같은 결과를 보장하도록 설계. 예를 들어 메시지 ID로 중복 체크.

BizSync의 채팅 기능은 DB 영속화를 사용하여 기본적인 신뢰성을 확보하고 있습니다. 클라이언트가 채팅방에 입장하면 과거 메시지를 HTTP로 먼저 로드하고, 이후 WebSocket으로 실시간 메시지를 받습니다.

## 코드 예시 (필요시)
```java
// ChatService.java - 메시지 영속화
@Transactional
public ChatMessageDTO saveMessage(ChatMessageDTO message) {
    // 1. DB에 먼저 저장 (영속화)
    ChatMessage entity = ChatMessage.builder()
            .roomId(message.roomId())
            .content(message.content())
            .senderId(message.senderId())
            .timestamp(LocalDateTime.now())
            .build();
    
    ChatMessage saved = chatMessageRepository.save(entity);
    
    // 2. 저장 성공 후 WebSocket 전송
    return ChatMessageDTO.from(saved);
}

// 클라이언트 - 메시지 누락 감지 및 복구
class ChatClient {
  private lastSeenMessageId: number = 0;
  
  connect() {
    this.client.subscribe("/sub/chat/room/123", (message) => {
      const data = JSON.parse(message.body);
      
      // 순서 검증
      if (data.id !== this.lastSeenMessageId + 1) {
        // 누락 감지: HTTP로 누락된 메시지 fetch
        this.fetchMissingMessages(this.lastSeenMessageId, data.id);
      }
      
      this.lastSeenMessageId = data.id;
      this.displayMessage(data);
    });
  }
  
  async fetchMissingMessages(fromId: number, toId: number) {
    const response = await fetch(
      `/api/chat/messages?from=${fromId}&to=${toId}`
    );
    const messages = await response.json();
    messages.forEach(this.displayMessage);
  }
}

// 재연결 시 마지막 메시지 이후 내역 로드
onConnect: () => {
  const lastId = localStorage.getItem('lastMessageId');
  if (lastId) {
    fetchChatHistory({ afterId: lastId }).then(messages => {
      messages.forEach(displayMessage);
    });
  }
  
  client.subscribe("/sub/chat/room/123", handleMessage);
}
```

## 꼬리 질문 예상
- At-most-once, At-least-once, Exactly-once 전달 보장의 차이는 무엇인가요?
- WebSocket 대신 MQTT를 사용하면 신뢰성이 더 좋아지나요?
- 메시지 순서 보장(Ordering)은 어떻게 구현하나요?

## 참고
- [[메시지 전달 보장 수준]]
- [[분산 시스템의 신뢰성]]
