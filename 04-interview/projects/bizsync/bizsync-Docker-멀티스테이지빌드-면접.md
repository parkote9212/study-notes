---
tags:
  - interview
  - docker
  - devops
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - Docker 멀티 스테이지 빌드

## 질문
> Dockerfile에서 멀티 스테이지 빌드를 사용한 이유와 효과는?

## 핵심 답변 (3줄)
1. **이미지 크기 최소화** - 빌드 도구(JDK, Node) 제외하고 런타임만 포함
2. **보안 강화** - 소스코드, 빌드 캐시가 최종 이미지에 포함되지 않음
3. **빌드 캐시 활용** - 의존성 레이어 캐싱으로 재빌드 시간 단축

## 상세 설명
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

## 꼬리 질문 예상
- Alpine 베이스 이미지를 선택한 이유는?
- `--no-daemon` 옵션을 사용하는 이유는?

## 참고
- [[bizsync-Docker-환경변수처리-면접]]
- [[bizsync-DockerCompose-서비스구성-면접]]
