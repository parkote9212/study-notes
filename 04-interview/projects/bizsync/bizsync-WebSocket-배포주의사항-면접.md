---
tags:
  - interview
  - docker
  - nginx
  - websocket
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - WebSocket 배포 주의사항

## 질문
> WebSocket을 운영 환경에 배포할 때 고려해야 할 점은?

## 핵심 답변 (3줄)
1. **Nginx Upgrade 헤더** - HTTP → WebSocket 프로토콜 전환 설정 필수
2. **Sticky Session** - 로드밸런서에서 동일 서버 연결 유지
3. **타임아웃 설정** - 유휴 연결 유지를 위한 timeout 값 조정

## 상세 설명
```nginx
# nginx.conf - WebSocket 프록시 설정
location /ws {
    proxy_pass http://backend:8080/ws;
    proxy_http_version 1.1;
    
    # WebSocket 업그레이드 헤더 (필수!)
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    # 원본 IP 전달
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    
    # 타임아웃 설정 (기본값 60초 → 연장)
    proxy_read_timeout 86400s;  # 24시간
    proxy_send_timeout 86400s;
}
```

**ALB 사용 시 추가 설정:**
- Connection draining timeout 증가
- Stickiness 활성화 (동일 백엔드 연결 유지)

## 꼬리 질문 예상
- HTTPS 환경에서 WebSocket URL은 어떻게 되나요? (wss://)
- 연결이 끊어졌을 때 재연결 로직은 어디에 구현하나요?

## 참고
- [[Nginx-WebSocket-설정]]
- [[bizsync-WebSocket-STOMP선택-면접]]
