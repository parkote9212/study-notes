---
tags:
  - interview
  - websocket
  - reconnect
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - WebSocket 재연결 전략

## 질문
> useBoardSocket 훅에서 reconnectDelay를 설정한 이유와 네트워크 단절 시 재연결 전략을 설명해주세요.

## 핵심 답변 (3줄)
1. 네트워크 불안정이나 서버 재시작 등으로 연결이 끊어질 수 있으므로 자동 재연결 메커니즘이 필수입니다
2. reconnectDelay를 5초로 설정하여 연결 실패 시 즉시 재시도하지 않고 지연시켜 서버 부하를 방지합니다
3. @stomp/stompjs의 reconnectDelay는 자동으로 exponential backoff를 적용하여 재시도 간격을 점진적으로 늘립니다

## 상세 설명
실시간 애플리케이션에서 WebSocket 연결은 다양한 이유로 끊어질 수 있습니다. 사용자의 네트워크 전환(Wi-Fi → 모바일), 서버 재시작, 방화벽 타임아웃 등이 대표적입니다.

reconnectDelay는 연결이 끊어졌을 때 재연결을 시도하기 전 대기 시간입니다. BizSync는 5000ms(5초)로 설정했습니다.

@stomp/stompjs는 기본적으로 exponential backoff 전략을 사용합니다. 첫 재연결은 5초 후, 실패하면 10초, 20초... 이런 식으로 점진적으로 간격이 늘어나 최대 30초까지 증가합니다.

## 코드 예시
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
    
    return () => {
      client.current?.deactivate();
    };
  }, [projectId, onUpdate]);
};
```

## 꼬리 질문 예상
- maxReconnectAttempts를 설정하지 않으면 어떤 문제가 발생할 수 있나요?
- Heartbeat 메커니즘은 무엇이며, 어떻게 설정하나요?

## 참고
- [[bizsync-WebSocket-STOMP선택-면접]]
- [[bizsync-WebSocket-배포주의사항-면접]]
