---
tags: interview, docker, devops, aws, bizsync, project
created: 2025-01-23
difficulty: 중
---

# BizSync - Docker 컨테이너화 & AWS 배포 면접

## 질문 1: 멀티 스테이지 빌드 적용 이유
> Dockerfile에서 멀티 스테이지 빌드를 사용한 이유와 효과는?

### 핵심 답변 (3줄)
1. **이미지 크기 최소화** - 빌드 도구(JDK, Node) 제외하고 런타임만 포함
2. **보안 강화** - 소스코드, 빌드 캐시가 최종 이미지에 포함되지 않음
3. **빌드 캐시 활용** - 의존성 레이어 캐싱으로 재빌드 시간 단축

### 상세 설명
```dockerfile
# Backend Dockerfile - 멀티 스테이지
# === Build Stage (JDK 필요) ===
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /app

COPY gradlew gradle build.gradle settings.gradle ./
COPY src src
RUN chmod +x ./gradlew && ./gradlew bootJar --no-daemon

# === Run Stage (JRE만 필요) ===
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /app/build/libs/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "-Dspring.profiles.active=prod", "app.jar"]
```

**이미지 크기 비교:**
| 방식 | 이미지 크기 |
|------|-----------|
| 단일 스테이지 (JDK 포함) | ~500MB |
| 멀티 스테이지 (JRE만) | ~200MB |

### 꼬리 질문 예상
- Alpine 베이스 이미지를 선택한 이유는?
- `--no-daemon` 옵션을 사용하는 이유는?

---

## 질문 2: 프론트엔드 빌드 시 환경변수 처리
> React(Vite) 빌드 시 환경변수를 어떻게 주입했나요?

### 핵심 답변 (3줄)
1. **ARG → ENV 전환** - 빌드 시점에 ARG로 받아 ENV로 설정
2. **Vite 환경변수 규칙** - `VITE_` 접두사 필수 (클라이언트 노출용)
3. **빌드 타임 바인딩** - 런타임이 아닌 빌드 시점에 값이 고정됨

### 상세 설명
```dockerfile
# Frontend Dockerfile
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# 빌드 시 환경변수 주입 (docker-compose에서 전달)
ARG VITE_API_BASE_URL
ARG VITE_WS_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_WS_URL=${VITE_WS_URL}

RUN npm run build -- --mode production

# Nginx로 정적 파일 서빙
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

```yaml
# docker-compose.yml
frontend:
  build:
    context: ./frontend
    args:
      - VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://localhost:8080/api}
      - VITE_WS_URL=${VITE_WS_URL:-ws://localhost:8080/ws}
```

### 꼬리 질문 예상
- 런타임에 환경변수를 변경하려면 어떻게 해야 하나요?
- `npm ci`와 `npm install`의 차이는?

---

## 질문 3: Docker Compose 서비스 구성
> docker-compose.yml에서 서비스 간 의존성과 헬스체크를 어떻게 설정했나요?

### 핵심 답변 (3줄)
1. **depends_on + condition** - 헬스체크 통과 후 의존 서비스 시작
2. **healthcheck 정의** - actuator/health 엔드포인트로 상태 확인
3. **네트워크 분리** - 커스텀 bridge 네트워크로 서비스 간 통신

### 상세 설명
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

### 꼬리 질문 예상
- `restart: unless-stopped`와 `always`의 차이는?
- 컨테이너 간 통신 시 localhost 대신 무엇을 사용하나요?

---

## 질문 4: 환경별 설정 분리 (Profile)
> 로컬/개발/운영 환경 설정을 어떻게 분리했나요?

### 핵심 답변 (3줄)
1. **Spring Profile** - `application-{profile}.yml`로 환경별 설정 분리
2. **환경변수 주입** - Docker에서 `SPRING_PROFILES_ACTIVE=prod` 전달
3. **민감정보 외부화** - DB 비밀번호, JWT Secret은 `.env` 파일로 관리

### 상세 설명
```
backend/src/main/resources/
├── application.yml          # 공통 설정
├── application-dev.yml      # 개발 환경 (H2, 상세 로그)
└── application-prod.yml     # 운영 환경 (RDS, 최소 로그)
```

```yaml
# application.yml (공통)
spring:
  jpa:
    hibernate:
      ddl-auto: validate  # 운영에서는 validate

app:
  jwt:
    secret: ${JWT_SECRET}
    expiration-ms: ${JWT_EXPIRATION_MS:3600000}

# application-prod.yml (운영)
spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL}
    username: ${SPRING_DATASOURCE_USERNAME}
    password: ${SPRING_DATASOURCE_PASSWORD}

logging:
  level:
    root: WARN
    com.bizsync: INFO
```

```bash
# .env 파일 (Git 제외)
SPRING_DATASOURCE_URL=jdbc:mariadb://rds-endpoint:3306/bizsync
SPRING_DATASOURCE_PASSWORD=secure_password
JWT_SECRET=256비트_이상의_시크릿_키
```

### 꼬리 질문 예상
- `.env` 파일이 유출되면 어떻게 대응하나요?
- AWS Secrets Manager를 사용한다면 어떻게 구성하나요?

---

## 질문 5: 무중단 배포 전략
> 현재 구조에서 무중단 배포를 적용하려면 어떻게 해야 하나요?

### 핵심 답변 (3줄)
1. **Rolling Update** - 새 컨테이너 시작 후 구 컨테이너 종료
2. **헬스체크 활용** - 새 컨테이너가 healthy 상태가 되면 트래픽 전환
3. **로드밸런서 연동** - ALB/NLB로 다중 인스턴스 트래픽 분산

### 상세 설명
```bash
# 방법 1: Docker Compose Rolling Update
docker compose up -d --no-deps --build backend
# --no-deps: 의존 서비스 재시작 안함
# 기존 컨테이너 중지 전 새 컨테이너 시작

# 방법 2: Blue-Green with Nginx
# nginx.conf에서 upstream 서버 전환
upstream backend {
    server backend-blue:8080;  # 현재
    # server backend-green:8080;  # 대기
}

# 방법 3: AWS ECS/EKS 사용 시
# - ECS 서비스의 Rolling Update 설정
# - minimumHealthyPercent: 50
# - maximumPercent: 200
```

**현재 단일 EC2 구조의 한계:**
- 배포 시 짧은 다운타임 발생 (컨테이너 재시작 시간)
- 해결: ALB + 다중 EC2 or ECS Fargate 전환

### 꼬리 질문 예상
- Blue-Green과 Rolling의 장단점은?
- 배포 실패 시 롤백은 어떻게 하나요?

---

## 질문 6: WebSocket 배포 시 주의사항
> WebSocket을 운영 환경에 배포할 때 고려해야 할 점은?

### 핵심 답변 (3줄)
1. **Nginx Upgrade 헤더** - HTTP → WebSocket 프로토콜 전환 설정 필수
2. **Sticky Session** - 로드밸런서에서 동일 서버 연결 유지
3. **타임아웃 설정** - 유휴 연결 유지를 위한 timeout 값 조정

### 상세 설명
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

### 꼬리 질문 예상
- HTTPS 환경에서 WebSocket URL은 어떻게 되나요? (wss://)
- 연결이 끊어졌을 때 재연결 로직은 어디에 구현하나요?

---

## 참고
- [[Docker-멀티스테이지-빌드]]
- [[AWS-ECS-배포-가이드]]
- [[bizsync-면접-WebSocket-STOMP]]
