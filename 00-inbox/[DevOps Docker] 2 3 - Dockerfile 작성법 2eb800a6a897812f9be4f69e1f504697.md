# [DevOps Docker] 2/3 - Dockerfile 작성법

🏷️기술 카테고리: DevOps, Docker
💡핵심키워드: #설정관리, #컨테이너
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 17일 오후 11:58
📅 다음 복습일: 2026년 1월 25일

# 1. Abstract: 핵심 요약

> **Dockerfile**은 Docker 이미지를 빌드하기 위한 명령어 스크립트입니다. 코드와 함께 버전 관리하면 **"어떻게 빌드했는지" 문서화**되고, 누구나 동일한 환경을 재현할 수 있습니다.
> 

**핵심 원칙**:

- 레이어 기반: 각 명령어는 새 레이어 생성
- 캐시 활용: 변경되지 않은 레이어는 재사용
- Multi-stage: 최종 이미지 크기 최소화

---

# 2. Dockerfile 기본 구조

## 2.1 기본 템플릿

```docker
# 1. 기본 이미지
FROM node:20-alpine

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 파일 복사
COPY package*.json ./

# 4. 의존성 설치
RUN npm install

# 5. 소스 코드 복사
COPY . .

# 6. 포트 노출
EXPOSE 3000

# 7. 실행 명령
CMD ["npm", "start"]
```

---

# 3. 핵심 명령어

## 3.1 FROM - 기본 이미지

```docker
# 태그 명시 (권장)
FROM eclipse-temurin:21-jdk-alpine

# Multi-stage 빌드에서 별칭 사용
FROM node:20 AS builder
```

**팁**:

- `latest` 태그는 피하기
- `alpine` 버전은 최소 크기
- 보안 업데이트가 있는 공식 이미지 사용

---

## 3.2 WORKDIR - 작업 디렉토리

```docker
# 절대 경로 사용 (권장)
WORKDIR /app

# 상대 경로 (피하기)
# WORKDIR ./app  # 안 좋음
```

**효과**:

- 이후 모든 명령어의 기본 경로
- 디렉토리가 없으면 자동 생성

---

## 3.3 COPY vs ADD

**COPY (권장)**:

```docker
# 파일/폴더 복사
COPY package.json .
COPY src/ ./src/
COPY . .

# 소유자 지정
COPY --chown=node:node . .
```

**ADD (제한적 사용)**:

```docker
# URL 다운로드
ADD [https://example.com/file.tar.gz](https://example.com/file.tar.gz) /tmp/

# tar 파일 자동 압축 해제
ADD archive.tar.gz /app/
```

**차이점**:

- COPY: 단순 복사만 (권장)
- ADD: URL 다운로드 + 압축 해제 기능

---

## 3.4 RUN - 명령 실행

```docker
# Shell 형식 (sh -c 사용)
RUN apt-get update && apt-get install -y curl

# Exec 형식 (권장)
RUN ["apt-get", "update"]

# 레이어 최소화 - 명령어 합치기 (권장)
RUN apt-get update && \
    apt-get install -y \
        curl \
        vim \
        git && \
    rm -rf /var/lib/apt/lists/*
```

**주의**:

- 각 RUN은 새 레이어 생성
- `&&`로 합치면 레이어 갯수 감소
- 캐시 청소 필수

---

## 3.5 ENV - 환경변수

```docker
# 런타임에도 유지되는 환경변수
ENV NODE_ENV=production
ENV DB_HOST=[localhost](http://localhost)
ENV APP_PORT=3000

# 한 줄로
ENV NODE_ENV=production \
    DB_HOST=[localhost](http://localhost) \
    APP_PORT=3000
```

---

## 3.6 ARG - 빌드 인자

```docker
# 빌드 시에만 사용
ARG BUILD_VERSION=1.0.0
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-alpine

# ARG는 런타임에 사라짐
```

**사용**:

```bash
docker build --build-arg BUILD_VERSION=2.0.0 -t myapp .
```

---

## 3.7 CMD vs ENTRYPOINT

**CMD (기본 명령)**:

```docker
# 쉽게 덮어쓸 수 있음
CMD ["npm", "start"]
```

**ENTRYPOINT (고정 명령)**:

```docker
# 덮어쓰기 어려움
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**함께 사용 (권장)**:

```docker
ENTRYPOINT ["java", "-jar", "app.jar"]
CMD ["--port=8080"]  # 기본 옵션
```

```bash
# 기본 실행
docker run myapp
# → java -jar app.jar --port=8080

# 옵션 변경
docker run myapp --port=9000
# → java -jar app.jar --port=9000
```

---

## 3.8 EXPOSE - 포트 노출

```docker
EXPOSE 3000
EXPOSE 8080
```

**주의**: 실제 포트 매핑은 `docker run -p`로!

---

## 3.9 VOLUME - 데이터 영속성

```docker
# 데이터 볼륨 지정
VOLUME ["/var/lib/mysql"]
VOLUME ["/app/logs"]
```

---

## 3.10 USER - 실행 사용자

```docker
# 보안을 위해 root 비권한 사용자로 실행
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

USER appuser

# 이후 모든 명령은 appuser로 실행
CMD ["npm", "start"]
```

---

# 4. Multi-stage Build

## 4.1 Spring Boot 예제

```docker
# 1단계: 빌드
FROM gradle:8.5-jdk21 AS builder

WORKDIR /app
COPY . .

# 테스트 제외하고 빌드
RUN gradle clean build -x test --no-daemon

# 2단계: 실행
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# 빌드 단계에서 JAR만 복사
COPY --from=builder /app/build/libs/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

**장점**:

- 최종 이미지에 Gradle 포함 X
- 이미지 크기 대폭 감소 (2GB → 200MB)

---

## 4.2 React 예제

```docker
# 1단계: 빌드
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# 2단계: Nginx로 서빙
FROM nginx:alpine

# Vite 빌드 결과물 복사
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

# 5. 베스트 프랙티스

## 5.1 .dockerignore

```
# 빌드에 포함하지 않을 파일
node_modules
.git
.env
*.log
[README.md](http://README.md)
.dockerignore
Dockerfile
```

---

## 5.2 레이어 최소화

```docker
# ❌ Bad - 3개 레이어
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ✅ Good - 1개 레이어
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

---

## 5.3 캐시 활용

```docker
# ❌ Bad - 변경이 잘 일어나는 파일 먼저
COPY . .
RUN npm install

# ✅ Good - 의존성 파일 먼저
COPY package*.json ./
RUN npm install
COPY . .
```

**이유**: `package.json` 미변경 시 `npm install` 캐시 사용

---

## 5.4 보안

```docker
# ✅ root 비권한 사용자
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# ✅ 민감 정보 ARG로 (ENV X)
ARG DB_PASSWORD
# ENV DB_PASSWORD=${DB_PASSWORD}  # 안됨!

# ✅ 최소 권한 원칙
COPY --chown=appuser:appgroup . .
```

---

# 6. Interview Readiness

## ▶ Q1: Multi-stage 빌드란?

**A**: 하나의 Dockerfile에 여러 FROM을 사용하여 **빌드 단계와 실행 단계를 분리**하는 기법입니다.

**장점**:

- 최종 이미지 크기 감소
- 빌드 도구가 실행 환경에 포함되지 않음

---

## ▶ Q2: CMD와 ENTRYPOINT의 차이는?

**A**:

| 구분 | CMD | ENTRYPOINT |
| --- | --- | --- |
| **용도** | 기본 명령/인자 | 고정 명령 |
| **덮어쓰기** | 쉽음 (`docker run` 인자) | 어려움 |
| **권장** | 함께 사용 | ENTRYPOINT + CMD |

```docker
ENTRYPOINT ["python", "[app.py](http://app.py)"]
CMD ["--port=8000"]  # 기본 옵션
```

---

## ▶ Q3: COPY와 ADD의 차이는?

**A**:

- **COPY**: 단순 파일/폴더 복사 (권장)
- **ADD**: URL 다운로드 + tar 압축 해제

모호함을 피하기 위해 **대부분 COPY 사용 권장**

---

## ▶ Q4: 이미지 크기를 줄이는 방법은?

**A**:

1. **Alpine 기반 이미지** 사용
2. **Multi-stage 빌드**
3. **레이어 최소화** (RUN 명령 합치기)
4. **.dockerignore** 활용
5. **불필요한 파일 삭제** (`rm -rf /var/lib/apt/lists/*`)

---

## 🔑 핵심 체크리스트

- [ ]  FROM에 태그 명시 (latest 피하기)
- [ ]  WORKDIR 절대 경로 사용
- [ ]  COPY 권장, ADD는 필요시만
- [ ]  RUN 명령 합치기 (레이어 갯수 감소)
- [ ]  Multi-stage로 빌드/실행 분리
- [ ]  .dockerignore 작성
- [ ]  USER로 root 비권한 사용자 사용

---

**작성일**: 2026-01-17  

**면접 빈출도**: ⭐⭐⭐ (상)