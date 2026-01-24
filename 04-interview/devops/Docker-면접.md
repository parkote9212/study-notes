---
tags:
  - interview
  - Docker
  - DevOps
created: 2026-01-24
difficulty: 상
---

# Docker 면접

## 질문
> Docker와 VM의 차이, Docker 기본 명령어, Dockerfile 작성법, Docker Compose 사용법

## 핵심 답변 (3줄)
1. Docker는 컨테이너 가상화로 VM보다 경량이며 초 단위 시작, 호스트 OS 커널 공유
2. Dockerfile은 레이어 기반으로 동작하며 Multi-stage 빌드로 이미지 크기 최소화
3. Docker Compose는 YAML로 여러 컨테이너를 정의하고 한 번에 관리

## 상세 설명

### Q1: Docker와 VM의 차이는?

**A**: Docker는 컨테이너 가상화, VM은 하드웨어 가상화입니다.

| 구분 | Docker | VM |
|------|--------|-----|
| **시작 속도** | 초 단위 | 분 단위 |
| **리소스** | 경량 (호스트 OS 공유) | 무거움 (각자 OS) |
| **격리 수준** | 프로세스 수준 | OS 수준 |
| **이식성** | 높음 | 낮음 |

Docker는 호스트 OS의 커널을 공유하므로 가볍고 빠르며, VM은 각각 독립적인 OS를 가져 완전한 격리를 제공합니다.

---

### Q2: docker run과 docker start의 차이는?

**A**:
- **docker run**: 이미지로부터 새 컨테이너 생성 + 실행
- **docker start**: 이미 생성된 중지된 컨테이너 재시작

```bash
# 처음 실행
docker run -d --name my-app nginx

# 중지
docker stop my-app

# 재시작 (설정 그대로 유지)
docker start my-app
```

---

### Q3: Multi-stage 빌드란?

**A**: 하나의 Dockerfile에 여러 FROM을 사용하여 빌드 단계와 실행 단계를 분리하는 기법입니다.

**장점**:
- 최종 이미지 크기 감소 (빌드 도구 제외)
- 빌드 환경과 실행 환경 분리

```dockerfile
# 1단계: 빌드
FROM gradle:8.5-jdk21 AS builder
WORKDIR /app
COPY . .
RUN gradle clean build -x test

# 2단계: 실행
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/build/libs/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

최종 이미지에는 JRE만 포함되고 Gradle은 제외되어 2GB → 200MB로 감소합니다.

---

### Q4: CMD와 ENTRYPOINT의 차이는?

**A**:

| 구분 | CMD | ENTRYPOINT |
|------|-----|-----------|
| **용도** | 기본 명령/인자 | 고정 명령 |
| **덮어쓰기** | 쉬움 (`docker run` 인자) | 어려움 |
| **권장** | 함께 사용 | ENTRYPOINT + CMD |

```dockerfile
ENTRYPOINT ["python", "app.py"]
CMD ["--port=8000"]  # 기본 옵션
```

```bash
# 기본 실행
docker run myapp
# → python app.py --port=8000

# 옵션 변경
docker run myapp --port=9000
# → python app.py --port=9000
```

---

### Q5: COPY와 ADD의 차이는?

**A**:
- **COPY**: 단순 파일/폴더 복사 (권장)
- **ADD**: URL 다운로드 + tar 압축 해제

모호함을 피하기 위해 대부분 COPY 사용을 권장합니다.

```dockerfile
# ✅ 권장
COPY package.json .
COPY src/ ./src/

# ❌ 특별한 이유 없이 ADD 사용
ADD package.json .
```

---

### Q6: Docker Compose를 사용하는 이유는?

**A**: 여러 컨테이너를 하나의 YAML 파일로 정의하고 관리할 수 있습니다.

**장점**:
1. **간편함**: `docker compose up` 한 줄로 전체 스택 실행
2. **재현성**: 동일한 환경을 어디서든 재현
3. **버전 관리**: YAML 파일을 Git으로 관리
4. **네트워크**: 서비스 간 자동 연결

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    depends_on:
      - db
  db:
    image: mysql:8.0
```

---

### Q7: depends_on의 한계는?

**A**: `depends_on`은 컨테이너 시작 순서만 보장하고, 서비스가 준비되었는지는 보장하지 않습니다.

**해결책**: healthcheck와 함께 사용

```yaml
services:
  backend:
    depends_on:
      db:
        condition: service_healthy  # 헬스체크 필수!
  
  db:
    healthcheck:
      test: ["CMD", "mysqladmin", "ping"]
      interval: 5s
      retries: 10
```

---

### Q8: 컨테이너 간 통신 방법은?

**A**: 서비스 이름을 호스트명으로 사용합니다.

```yaml
services:
  backend:
    environment:
      - DB_HOST=db  # 서비스 이름
  
  db:
    image: mysql:8.0
```

Docker Compose가 자동으로 네트워크를 생성하고, 같은 네트워크의 서비스는 서비스 이름으로 통신 가능합니다.

---

### Q9: 이미지 크기를 줄이는 방법은?

**A**:
1. **Alpine 기반 이미지** 사용
2. **Multi-stage 빌드**
3. **레이어 최소화** (RUN 명령 합치기)
4. **.dockerignore** 활용
5. **불필요한 파일 삭제** (`rm -rf /var/lib/apt/lists/*`)

```dockerfile
# ✅ Good - 1개 레이어
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

---

### Q10: 개발/프로덕션 환경 분리 방법은?

**A**: 여러 Compose 파일을 조합합니다.

```
docker-compose.yml           # 기본 설정
docker-compose.dev.yml       # 개발 환경
docker-compose.prod.yml      # 프로덕션 환경
```

```bash
# 개발
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# 프로덕션
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 꼬리 질문 예상
- Docker 네트워크 종류는?
- 볼륨과 바인드 마운트의 차이는?
- Docker 레이어 캐싱 원리는?
- Dockerfile 베스트 프랙티스는?

## 참고
- [[Docker-기본-명령어]]
- [[Dockerfile-작성법]]
- [[Docker-Compose]]
