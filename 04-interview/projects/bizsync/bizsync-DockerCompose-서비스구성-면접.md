---
tags:
  - interview
  - docker
  - docker-compose
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - Docker Compose 서비스 구성

## 질문
> docker-compose.yml에서 서비스 간 의존성과 헬스체크를 어떻게 설정했나요?

## 핵심 답변 (3줄)
1. **depends_on + condition** - 헬스체크 통과 후 의존 서비스 시작
2. **healthcheck 정의** - actuator/health 엔드포인트로 상태 확인
3. **네트워크 분리** - 커스텀 bridge 네트워크로 서비스 간 통신

## 상세 설명
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: bizsync-backend
    ports:
      - "8080:8080"
    environment:
      - SPRING_DATASOURCE_URL=${SPRING_DATASOURCE_URL}
      - JWT_SECRET=${JWT_SECRET}
      - SPRING_PROFILES_ACTIVE=prod
    restart: unless-stopped
    networks:
      - bizsync-network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", 
             "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s  # 앱 시작 대기 시간

  frontend:
    build:
      context: ./frontend
      args:
        - VITE_API_BASE_URL=${VITE_API_BASE_URL}
    depends_on:
      backend:
        condition: service_healthy  # 헬스체크 통과 후 시작
    networks:
      - bizsync-network

networks:
  bizsync-network:
    driver: bridge
```

## 꼬리 질문 예상
- `restart: unless-stopped`와 `always`의 차이는?
- 컨테이너 간 통신 시 localhost 대신 무엇을 사용하나요?

## 참고
- [[Docker-Compose-헬스체크]]
- [[bizsync-Docker-환경별설정-면접]]
