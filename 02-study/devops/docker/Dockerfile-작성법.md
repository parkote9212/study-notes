---
tags: study, Docker, DevOps, Dockerfile
created: 2026-01-24
---

# Dockerfile 작성법

## 한 줄 요약
> Dockerfile은 Docker 이미지를 빌드하기 위한 명령어 스크립트로, 레이어 기반으로 동작하며 캐시를 활용하여 효율적으로 이미지를 생성

## 상세 설명

Dockerfile은 코드와 함께 버전 관리하면 "어떻게 빌드했는지" 문서화되고, 누구나 동일한 환경을 재현할 수 있습니다.

### 핵심 원칙
- **레이어 기반**: 각 명령어는 새 레이어 생성
- **캐시 활용**: 변경되지 않은 레이어는 재사용
- **Multi-stage**: 최종 이미지 크기 최소화

### 주요 명령어

**FROM - 기본 이미지**
- 태그 명시 권장 (latest 피하기)
- alpine 버전은 최소 크기
- 보안 업데이트가 있는 공식 이미지 사용

**WORKDIR - 작업 디렉토리**
- 절대 경로 사용 권장
- 디렉토리가 없으면 자동 생성

**COPY vs ADD**
- COPY: 단순 복사만 (권장)
- ADD: URL 다운로드 + 압축 해제 기능

**RUN - 명령 실행**
- 각 RUN은 새 레이어 생성
- `&&`로 합치면 레이어 갯수 감소
- 캐시 청소 필수

**ENV vs ARG**
- ENV: 런타임에도 유지되는 환경변수
- ARG: 빌드 시에만 사용

**CMD vs ENTRYPOINT**
- CMD: 기본 명령 (쉽게 덮어쓸 수 있음)
- ENTRYPOINT: 고정 명령 (덮어쓰기 어려움)
- 함께 사용 권장

**EXPOSE - 포트 노출**
- 실제 포트 매핑은 `docker run -p`로 수행

**VOLUME - 데이터 영속성**
- 데이터 볼륨 지정

**USER - 실행 사용자**
- 보안을 위해 root 비권장 사용자로 실행

### Multi-stage Build

하나의 Dockerfile에 여러 FROM을 사용하여 빌드 단계와 실행 단계를 분리하는 기법입니다.

장점:
- 최종 이미지 크기 대폭 감소 (2GB → 200MB)
- 빌드 도구가 실행 환경에 포함되지 않음

## 코드 예시

```dockerfile
# 기본 템플릿
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]

# Spring Boot Multi-stage
FROM gradle:8.5-jdk21 AS builder
WORKDIR /app
COPY . .
RUN gradle clean build -x test --no-daemon

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]

# React Multi-stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 주의사항 / 함정

1. **레이어 최소화**: 여러 RUN 명령을 &&로 합치기
2. **캐시 활용**: 변경이 잘 일어나는 파일은 나중에 COPY
3. **보안**: root 사용자 대신 비권한 사용자 사용
4. **.dockerignore**: 불필요한 파일 제외
5. **Alpine 이미지**: 최소 크기이지만 일부 패키지 누락 가능

### 베스트 프랙티스

```dockerfile
# ❌ Bad - 3개 레이어
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ✅ Good - 1개 레이어
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# ❌ Bad - 변경이 잘 일어나는 파일 먼저
COPY . .
RUN npm install

# ✅ Good - 의존성 파일 먼저
COPY package*.json ./
RUN npm install
COPY . .
```

## 관련 개념
- [[Docker-기본-명령어]]
- [[Docker-Compose]]
- [[Multi-stage-Build]]
- [[Docker-레이어]]

## 면접 질문
1. Multi-stage 빌드란?
2. CMD와 ENTRYPOINT의 차이는?
3. COPY와 ADD의 차이는?
4. 이미지 크기를 줄이는 방법은?

## 참고 자료
- Docker 공식 문서
- Dockerfile 베스트 프랙티스
