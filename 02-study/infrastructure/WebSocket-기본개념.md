---
tags:
  - study
  - websocket
  - realtime
  - protocol
created: 2026-02-15
---

# WebSocket 기본개념

## 한 줄 요약
> WebSocket은 클라이언트와 서버 간 양방향 실시간 통신을 가능하게 하는 프로토콜로, HTTP의 단방향 요청-응답 방식의 한계를 극복하여 채팅, 알림, 실시간 협업 등에 사용된다.

## 상세 설명

### WebSocket이란?
**WebSocket**은 HTML5 표준의 일부로, 클라이언트와 서버 간 **지속적인 양방향 통신 채널**을 제공하는 프로토콜입니다.

**핵심 특징:**
1. **양방향 통신**: 클라이언트 ↔ 서버 모두 메시지 전송 가능
2. **실시간성**: 낮은 지연 시간 (latency)
3. **지속적 연결**: 한 번 연결 후 계속 유지
4. **효율적**: HTTP 폴링보다 오버헤드 적음
5. **프로토콜**: `ws://` (비암호화) 또는 `wss://` (암호화)

### 왜 WebSocket이 필요한가?

**HTTP의 한계:**
```
기존 HTTP (요청-응답):
클라이언트 → 서버: "새로운 메시지 있어?"
서버 → 클라이언트: "없어요"
(1초 후 다시 요청)
클라이언트 → 서버: "새로운 메시지 있어?"
서버 → 클라이언트: "없어요"
→ 비효율적! 불필요한 요청 반복
```

**WebSocket 방식:**
```
1. 초기 연결 (HTTP Upgrade)
2. 지속적 연결 유지
3. 서버가 새 메시지 생기면 즉시 전송
→ 효율적! 실시간!
```

### HTTP vs WebSocket

| 항목 | HTTP | WebSocket |
|------|------|-----------|
| **통신 방향** | 단방향 (요청-응답) | 양방향 |
| **연결** | 요청마다 새로 연결 | 지속적 연결 |
| **오버헤드** | 높음 (헤더 반복) | 낮음 (한 번만) |
| **실시간성** | 낮음 (폴링 필요) | 높음 |
| **프로토콜** | `http://`, `https://` | `ws://`, `wss://` |
| **포트** | 80, 443 | 80, 443 (동일) |
| **사용 사례** | API, 웹 페이지 | 채팅, 실시간 알림 |

## WebSocket 동작 원리

### 1. Handshake (연결 수립)

**클라이언트 → 서버 (HTTP Upgrade 요청):**
```http
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

**서버 → 클라이언트 (Upgrade 승인):**
```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

### 2. 데이터 프레임 교환

연결 수립 후 **WebSocket Frame** 형식으로 통신:
```
┌─────────────────────────────────┐
│ FIN | Opcode | Mask | Payload  │
└─────────────────────────────────┘

Opcode:
  0x1 = Text (텍스트 메시지)
  0x2 = Binary (바이너리 데이터)
  0x8 = Close (연결 종료)
  0x9 = Ping (연결 확인)
  0xA = Pong (Ping 응답)
```

### 3. 연결 종료

**정상 종료:**
```
클라이언트/서버 → Close Frame 전송
상대방 → Close Frame 응답
TCP 연결 종료
```

## 실무 사용 사례

### 1. 실시간 채팅
```
사용자 A: "안녕하세요" → WebSocket → 서버
서버 → WebSocket → 사용자 B, C, D에게 즉시 전송
```

### 2. 실시간 알림
```
주문 접수 → 서버가 관리자에게 WebSocket으로 즉시 알림
새 댓글 → 작성자에게 실시간 알림
```

### 3. 실시간 협업 (BizSync 예시)
```
사용자 A가 문서 편집 → WebSocket → 서버
서버 → WebSocket → 사용자 B, C 화면에 실시간 반영
```

### 4. 게임, 주식 시세
```
게임 서버: 플레이어 위치, 액션 실시간 동기화
주식: 시세 변동 즉시 전송
```

### 5. IoT 센서 데이터
```
센서 → WebSocket → 서버
서버 → 대시보드에 실시간 표시
```

## 기본 코드 예시

### JavaScript (브라우저 클라이언트)
```javascript
// 1. WebSocket 연결
const socket = new WebSocket('ws://localhost:8080/chat');

// 2. 연결 성공
socket.onopen = (event) => {
    console.log('WebSocket 연결 성공');
    
    // 메시지 전송
    socket.send(JSON.stringify({
        type: 'JOIN',
        username: 'Alice'
    }));
};

// 3. 메시지 수신
socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('수신:', message);
    
    // UI 업데이트
    displayMessage(message);
};

// 4. 에러 처리
socket.onerror = (error) => {
    console.error('WebSocket 에러:', error);
};

// 5. 연결 종료
socket.onclose = (event) => {
    console.log('WebSocket 연결 종료:', event.code, event.reason);
    
    // 재연결 시도
    if (event.code !== 1000) {
        setTimeout(() => reconnect(), 3000);
    }
};

// 메시지 전송 함수
function sendMessage(text) {
    const message = {
        type: 'CHAT',
        content: text,
        timestamp: new Date().toISOString()
    };
    socket.send(JSON.stringify(message));
}
```

### Spring Boot (서버)
```java
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {
    
    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(chatHandler(), "/chat")
                .setAllowedOrigins("*");  // CORS 설정
    }
    
    @Bean
    public WebSocketHandler chatHandler() {
        return new ChatWebSocketHandler();
    }
}

@Component
public class ChatWebSocketHandler extends TextWebSocketHandler {
    
    // 연결된 세션 저장
    private final Set<WebSocketSession> sessions = new CopyOnWriteArraySet<>();
    
    // 클라이언트 연결 시
    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        sessions.add(session);
        log.info("새 연결: {}", session.getId());
    }
    
    // 메시지 수신 시
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) 
            throws Exception {
        
        String payload = message.getPayload();
        log.info("메시지 수신: {}", payload);
        
        // 모든 클라이언트에게 브로드캐스트
        for (WebSocketSession s : sessions) {
            if (s.isOpen()) {
                s.sendMessage(new TextMessage(payload));
            }
        }
    }
    
    // 연결 종료 시
    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        sessions.remove(session);
        log.info("연결 종료: {}, 이유: {}", session.getId(), status);
    }
    
    // 에러 발생 시
    @Override
    public void handleTransportError(WebSocketSession session, Throwable exception) {
        log.error("WebSocket 에러: {}", session.getId(), exception);
        sessions.remove(session);
    }
}
```

## WebSocket 대안 기술

### 1. Polling (단순 폴링)
```javascript
// 1초마다 서버에 요청
setInterval(() => {
    fetch('/api/messages')
        .then(res => res.json())
        .then(data => updateUI(data));
}, 1000);
```

**장점:** 구현 간단  
**단점:** 서버 부하 큼, 실시간성 낮음, 불필요한 요청

### 2. Long Polling
```javascript
function longPoll() {
    fetch('/api/messages/long-poll')
        .then(res => res.json())
        .then(data => {
            updateUI(data);
            longPoll();  // 재귀 호출
        });
}
```

**장점:** 폴링보다 효율적  
**단점:** WebSocket보다 복잡, 서버 연결 많이 사용

### 3. Server-Sent Events (SSE)
```javascript
const eventSource = new EventSource('/api/events');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);
};
```

**장점:** 간단, HTTP 기반  
**단점:** **단방향** (서버 → 클라이언트만)

### 비교

| 기술 | 통신 방향 | 실시간성 | 복잡도 | 사용 사례 |
|------|----------|---------|--------|----------|
| **Polling** | 단방향 | 낮음 | 낮음 | 업데이트 빈도 낮음 |
| **Long Polling** | 단방향 | 중간 | 중간 | 레거시 환경 |
| **SSE** | 단방향 | 높음 | 낮음 | 알림, 피드 |
| **WebSocket** | 양방향 | 매우 높음 | 중간 | 채팅, 협업, 게임 |

## 주의사항 / 함정

### 1. 방화벽/프록시 문제
❌ **문제**: 일부 방화벽이 WebSocket 차단  
✅ **해결**: 
- `wss://` (암호화) 사용
- Fallback (SSE, Long Polling) 제공

### 2. 연결 관리
❌ **문제**: 네트워크 끊김 시 재연결 필요  
✅ **해결**:
```javascript
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connect() {
    const socket = new WebSocket('ws://localhost:8080');
    
    socket.onclose = () => {
        if (reconnectAttempts < maxReconnectAttempts) {
            setTimeout(() => {
                reconnectAttempts++;
                connect();
            }, 1000 * reconnectAttempts);
        }
    };
    
    socket.onopen = () => {
        reconnectAttempts = 0;  // 성공 시 리셋
    };
}
```

### 3. 메시지 순서 보장
- TCP 기반이므로 **순서는 보장됨**
- 단, 여러 서버 환경에서는 추가 처리 필요

### 4. 메모리 누수
❌ **문제**: 연결 종료 시 세션 정리 안 하면 메모리 누수  
✅ **해결**:
```java
@Override
public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
    sessions.remove(session);  // 반드시 제거
    cleanupUserData(session);
}
```

### 5. 확장성 (Scale-Out)
❌ **문제**: 여러 서버에서 WebSocket 세션 공유 어려움  
✅ **해결**: Redis Pub/Sub 활용 (다음 챕터에서 설명)

## 관련 개념
- [[WebSocket-Spring통합]] - Spring WebSocket 구현
- [[WebSocket-STOMP프로토콜]] - 메시징 프로토콜
- [[WebSocket-Redis연동과확장]] - 다중 서버 환경
- [[Redis-PubSub과트랜잭션]] - Redis 메시징
- [[HTTP-프로토콜]] - HTTP와 비교

## 면접 질문

1. **WebSocket이 무엇이며, HTTP와 어떻게 다른가요?**
   - 양방향 실시간 통신 프로토콜
   - HTTP: 단방향 요청-응답, WebSocket: 지속적 양방향
   - 채팅, 알림 등 실시간 기능에 사용

2. **WebSocket Handshake 과정을 설명하세요.**
   - 클라이언트가 HTTP Upgrade 요청
   - 서버가 101 Switching Protocols 응답
   - WebSocket 연결 수립

3. **WebSocket과 SSE의 차이는?**
   - WebSocket: 양방향, 복잡
   - SSE: 단방향 (서버→클라이언트), 간단
   - 알림만 필요하면 SSE, 채팅은 WebSocket

4. **WebSocket 연결이 끊어지면 어떻게 처리하나요?**
   - onclose 이벤트에서 재연결 로직
   - Exponential Backoff (1초, 2초, 4초...)
   - 최대 재시도 횟수 설정

5. **WebSocket의 단점은?**
   - 오래된 브라우저/프록시 호환성
   - 상태 유지 필요 (Stateful)
   - Scale-Out 시 세션 공유 어려움

6. **프로젝트에서 WebSocket을 어떻게 사용했나요? (BizSync 예시)**
   - 실시간 문서 협업 시스템
   - 사용자 편집 내용 즉시 동기화
   - Spring WebSocket + Redis Pub/Sub 조합

## 참고 자료
- [WebSocket RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455)
- [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Spring WebSocket 공식 문서](https://docs.spring.io/spring-framework/reference/web/websocket.html)
- [WebSocket vs SSE vs Polling](https://ably.com/blog/websockets-vs-long-polling)
