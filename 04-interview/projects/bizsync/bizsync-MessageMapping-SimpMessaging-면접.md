---
tags:
  - interview
  - websocket
  - messagemapping
  - bizsync
  - project
created: 2025-01-23
difficulty: 중상
---

# BizSync - MessageMapping과 SimpMessagingTemplate

## 질문
> @MessageMapping과 SimpMessagingTemplate의 역할 차이와 메시지 발행/구독 흐름을 설명해주세요.

## 핵심 답변 (3줄)
1. **@MessageMapping**은 클라이언트가 특정 destination으로 보낸 메시지를 처리하는 핸들러 메서드를 정의합니다 (Publish 수신)
2. **SimpMessagingTemplate**은 서버에서 특정 destination으로 메시지를 발행하여 구독자들에게 전달하는 도구입니다 (Subscribe 발행)
3. 클라이언트는 SEND로 메시지를 발행하고, SUBSCRIBE로 메시지를 구독하며, 서버는 이 둘을 연결하는 중개자 역할을 합니다

## 상세 설명
STOMP는 Pub/Sub 패턴 기반의 메시징 프로토콜입니다. BizSync의 채팅 기능을 예로 들면:

1. 클라이언트 A가 "/pub/chat/message"로 메시지 전송 (SEND 프레임)
2. 서버의 @MessageMapping("/chat/message") 메서드가 메시지 수신
3. ChatService에서 DB에 메시지 저장
4. SimpMessagingTemplate.convertAndSend()로 "/sub/chat/room/123"에 메시지 발행
5. 해당 방을 구독(SUBSCRIBE)하고 있던 모든 클라이언트에게 메시지 전달

## 코드 예시
```java
// ChatController.java
@RestController
@RequiredArgsConstructor
public class ChatController {
    
    private final SimpMessagingTemplate messagingTemplate;
    private final ChatService chatService;
    
    // 1. 클라이언트 메시지 수신 (Publish 수신)
    @MessageMapping("/chat/message")
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

// 프론트엔드 - 메시지 발행
client.publish({
    destination: "/pub/chat/message",
    body: JSON.stringify({
        roomId: 123,
        content: "Hello!",
        senderId: 1
    })
});

// 프론트엔드 - 메시지 구독
client.subscribe("/sub/chat/room/123", (message) => {
    const chatMessage = JSON.parse(message.body);
    console.log(chatMessage.content);
});
```

## 꼬리 질문 예상
- @SendTo와 SimpMessagingTemplate의 차이는?
- convertAndSend()와 convertAndSendToUser()의 차이는?

## 참고
- [[bizsync-WebSocket-STOMP선택-면접]]
