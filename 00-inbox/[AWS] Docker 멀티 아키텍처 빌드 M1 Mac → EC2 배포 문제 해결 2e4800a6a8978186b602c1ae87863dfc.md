# [AWS] Docker 멀티 아키텍처 빌드: M1 Mac → EC2 배포 문제 해결

🏷️기술 카테고리: AWS, DevOps, Docker, Infra
💡핵심키워드: #아키텍처, #컨테이너
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): Yes
날짜: 2026년 1월 10일 오후 5:45

# 1. Abstract: 핵심 요약

> **Mac (ARM64)**에서 빌드한 Docker 이미지는 **AWS EC2 (x86-64)**에서 실행되지 않습니다. 개발 환경과 배포 환경의 CPU 아키텍처 차이로 인한 문제이며, Docker Buildx의 `--platform` 옵션을 사용하여 **크로스 플랫폼 빌드**를 수행해야 합니다.
> 

**핵심 원칙**: "Build Once, Deploy Anywhere" - 한 번 빌드한 이미지가 어떤 환경에서도 동작해야 함

---

# 2. Technical Deep Dive: CPU 아키텍처 이해

## 2.1 x86-64 vs ARM64 차이점

| 구분 | x86-64 (AMD64) | ARM64 (AArch64) |
| --- | --- | --- |
| **주요 사용처** | AWS EC2, 대부분의 서버 | Apple Silicon Mac, AWS Graviton |
| **명령어 세트** | CISC (복잡한 명령어) | RISC (단순한 명령어) |
| **전력 효율** | 보통 | 높음 (모바일, Mac) |
| **Docker 이미지** | linux/amd64 | linux/arm64 |

## 2.2 왜 문제가 발생하는가?

```bash
# M1 Mac에서 일반 빌드
docker build -t my-app .
# → ARM64 이미지 생성

# AWS EC2 (x86-64)에서 실행 시도
docker run my-app
# ❌ exec format error 또는 컨테이너 즉시 종료
```

**원인**: CPU가 이해할 수 없는 명령어 세트로 이루어진 바이너리

- 비유: 한국어 책을 러시아 사람에게 읽어보라고 하는 것과 동일

---

# 3. Critical Thinking: 해결 방법 비교

## ⚖️ 의사결정: 크로스 플랫폼 빌드 전략

### ❌ Before: 아키텍처 불일치 문제

```bash
# M1 Mac (로컬 개발 환경)
docker build -t my-backend .
# 결과: linux/arm64 이미지

# AWS EC2 (배포 환경)
docker pull my-backend
docker run my-backend
# ❌ 실행 실패: "exec /usr/local/bin/java: exec format error"
```

**문제점**:

- 로컬에서는 정상 작동
- 배포 환경에서만 에러 발생
- 디버깅이 매우 어려움

### ✅ After: Docker Buildx 멀티 플랫폼 빌드

**방법 1: 빌드 시 타겟 플랫폼 명시**

```bash
# M1 Mac에서 x86-64용 이미지 빌드
docker buildx build --platform linux/amd64 \
  -t my-backend:latest \
  --push \
  .
```

**방법 2: 멀티 아키텍처 이미지 생성**

```bash
# ARM64와 x86-64 둘 다 지원하는 이미지 생성
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t my-backend:latest \
  --push \
  .
```

**Decision**: 

- 배포 대상이 AWS EC2만 있다면 **방법 1** (빌드 속도 빠름)
- AWS Graviton도 사용할 예정이라면 **방법 2** (범용성 높음)

### 성능 트레이드오프

```
M1 Mac에서 빌드 시간 비교:

네이티브 빌드 (ARM64):     ██████░░░░ 30초
QEMU 크로스 빌드 (x86-64): ████████████████ 2분 30초 (5배 느림)
멀티 아키텍처:              ████████████████████ 3분 (6배 느림)
```

**QEMU 에뮬레이션**으로 인한 속도 저하는 감수해야 함

---

# 4. Project Case Study: 실무 적용

## 🏗️ 공매 물건 정보 시스템 - 아키텍처 호환성 문제 해결

**S (Situation)**:

- M1 MacBook에서 Spring Boot 애플리케이션 개발
- Docker Compose로 로컬 테스트 성공
- AWS EC2 (Ubuntu x86-64)에 배포 시 컨테이너 실행 실패

**T (Task)**:

- 로컬 개발 환경과 배포 환경 간 호환성 확보
- CI/CD 파이프라인에서 자동으로 올바른 아키텍처 이미지 빌드

**A (Action)**:

**1. Dockerfile 수정 (멀티 스테이지 빌드)**

```docker
# STAGE 1: 빌드 (JDK 포함)
FROM eclipse-temurin:21-jdk-jammy AS build
WORKDIR /app

# Gradle 래퍼 복사
COPY gradlew .
COPY gradle gradle
COPY build.gradle settings.gradle .

# ✅ Windows 줄바꿈 문자 제거 (크로스 플랫폼 대응)
RUN sed -i 's/\r$//' gradlew && chmod +x gradlew

# 종속성 설치
RUN ./gradlew dependencies --no-daemon

# 소스 복사 및 빌드
COPY src src
RUN ./gradlew bootJar -x test --no-daemon

# STAGE 2: 실행 (JRE만)
FROM eclipse-temurin:21-jre-alpine AS final
WORKDIR /app
COPY --from=build /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**2. 로컬 빌드 스크립트 작성**

```bash
#!/bin/bash
# [build-for-aws.sh](http://build-for-aws.sh)

# Buildx 빌더 인스턴스 생성 (최초 1회)
docker buildx create --name mybuilder --use 2>/dev/null || true

# x86-64 플랫폼 지정하여 빌드 및 Docker Hub 푸시
docker buildx build \
  --platform linux/amd64 \
  -t myusername/auction-backend:latest \
  --push \
  .

echo "✅ AWS EC2용 이미지 빌드 완료!"
```

**3. GitHub Actions CI/CD 파이프라인**

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest  # ✅ GitHub Runner는 x86-64
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          platforms: linux/amd64  # ✅ 명시적으로 지정
          push: true
          tags: myusername/auction-backend:latest
```

**R (Result)**:

- ✅ M1 Mac에서 개발 → AWS EC2에서 정상 실행
- ✅ CI/CD 파이프라인에서 자동으로 올바른 아키텍처 이미지 생성
- ✅ 아키텍처 불일치로 인한 배포 실패 0건
- ⚠️ 로컬 빌드 시간 30초 → 2분 30초로 증가 (감수 가능한 수준)

---

# 5. Interview Readiness: 예상 질문

- Q: M1 Mac에서 빌드한 Docker 이미지가 AWS에서 실행 안 되는 이유는?
    
    **A**: M1 Mac은 **ARM64 아키텍처**를 사용하고, 대부분의 AWS EC2 인스턴스는 **x86-64 아키텍처**를 사용하기 때문입니다. Docker 이미지는 빌드된 플랫폼의 CPU 명령어 세트를 포함하므로, ARM64용 이미지는 x86-64 CPU에서 실행할 수 없습니다. `--platform linux/amd64` 옵션으로 크로스 플랫폼 빌드를 수행해야 합니다.
    
- Q: docker build와 docker buildx의 차이는 무엇인가요?
    
    **A**: `docker build`는 현재 시스템의 아키텍처로만 빌드하는 기본 명령어입니다. 반면 `docker buildx`는 **BuildKit 백엔드**를 사용하여 여러 플랫폼용 이미지를 동시에 빌드할 수 있는 확장 기능입니다. QEMU 에뮬레이션을 통해 다른 아키텍처용 이미지를 빌드하거나, 여러 아키텍처를 포함하는 멀티 플랫폼 매니페스트를 생성할 수 있습니다.
    
- Q: 크로스 플랫폼 빌드 시 속도가 느린 이유와 해결 방법은?
    
    **A**: M1 Mac에서 x86-64 이미지를 빌드할 때는 **QEMU 에뮬레이션**을 사용하므로 네이티브 빌드보다 5~6배 느립니다. 해결 방법은:
    
    1. **GitHub Actions 등 CI 서버 활용**: x86-64 러너에서 빌드하면 에뮬레이션 불필요
    2. **캐싱 최적화**: Docker 레이어 캐싱, Buildx 캐시 활용
    3. **AWS Graviton (ARM64) 인스턴스 사용**: 개발 환경과 아키텍처 일치

---

## 🔧 트러블슈팅 체크리스트

### 문제: "exec format error" 발생 시

```bash
# 1. 이미지 아키텍처 확인
docker inspect myimage | grep Architecture
# 결과: "Architecture": "arm64"  ❌ 문제!
# 기대: "Architecture": "amd64"  ✅

# 2. Buildx 빌더 확인
docker buildx ls
# linux/amd64 지원 여부 확인

# 3. 올바른 명령어로 재빌드
docker buildx build --platform linux/amd64 -t myimage .
```

### Windows 개발자 주의사항

```bash
# Windows (WSL2)에서도 아키텍처는 x86-64
# 따라서 --platform 옵션 불필요
docker build -t myimage .  # ✅ 바로 AWS 호환

# 단, 줄바꿈 문자는 주의 필요 (CRLF → LF)
git config --global core.autocrlf input
```

**핵심**: 개발 환경의 아키텍처를 항상 인지하고, 배포 대상 플랫폼에 맞춰 빌드