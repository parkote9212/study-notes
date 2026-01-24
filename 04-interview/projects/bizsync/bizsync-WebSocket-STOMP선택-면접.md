---
tags:
  - interview
  - websocket
  - stomp
  - bizsync
  - project
created: 2025-01-23
difficulty: 중상
---

# BizSync - WebSocket STOMP 선택이유

## 질문
> WebSocket과 STOMP 프로토콜을 함께 사용한 이유와 STOMP가 순수 WebSocket 대비 제공하는 장점을 설명해주세요.

## 핵심 답변 (3줄)
1. **STOMP**는 WebSocket 위에서 동작하는 메시징 프로토콜로, Pub/Sub 패턴을 쉽게 구현할 수 있습니다
2. 순수 WebSocket은 양방향 통신만 제공하지만, STOMP는 목적지(destination) 개념과 브로커 구조를 통해 메시지 라우팅을 표준화합니다
3. Spring Framework가 STOMP를 기본 지원하여 @MessageMapping과 SimpMessagingTemplate으로 쉽게 구현할 수 있습니다

## 상세 설명
순수 WebSocket은 클라이언트와 서버 간의 양방향 통신 채널을 제공하지만, 메시지 포맷이나 라우팅 규칙을 정의하지 않습니다.

STOMP는 WebSocket 위에서 동작하는 텍스트 기반 프로토콜로, 메시지 프레임(CONNECT, SUBSCRIBE, SEND 등)과 헤더 구조를 표준화합니다.

BizSync에서는 실시간 채팅, 칸반 보드 동기화, 알림 전송에 WebSocket/STOMP를 활용합니다. 칸반 보드에서 한 사용자가 업무를 이동하면, 같은 프로젝트를 보고 있는 모든 사용자에게 변경사항이 실시간으로 전파됩니다.

## 코드 예시
```java
// WebSocketConfig.java - STOMP 설정
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws").setAllowedOriginPatterns("*");
    }
    
    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        registry.enableSimpleBroker("/sub", "/topic");
        registry.setApplicationDestinationPrefixes("/pub", "/app");
    }
}
```

## 꼬리 질문 예상
- SockJS를 사용하지 않은 이유는?
- STOMP 대신 Socket.IO를 사용할 수도 있지 않나요?

## 참고
- [[WebSocket-STOMP-개념]]
- [[bizsync-WebSocket-재연결전략-면접]]
