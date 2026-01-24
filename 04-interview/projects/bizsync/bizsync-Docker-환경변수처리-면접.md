---
tags:
  - interview
  - docker
  - vite
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - Docker 환경변수 처리

## 질문
> React(Vite) 빌드 시 환경변수를 어떻게 주입했나요?

## 핵심 답변 (3줄)
1. **ARG → ENV 전환** - 빌드 시점에 ARG로 받아 ENV로 설정
2. **Vite 환경변수 규칙** - `VITE_` 접두사 필수 (클라이언트 노출용)
3. **빌드 타임 바인딩** - 런타임이 아닌 빌드 시점에 값이 고정됨

## 상세 설명
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

## 꼬리 질문 예상
- 런타임에 환경변수를 변경하려면 어떻게 해야 하나요?
- `npm ci`와 `npm install`의 차이는?

## 참고
- [[Vite-환경변수-설정]]
- [[bizsync-Docker-멀티스테이지빌드-면접]]
