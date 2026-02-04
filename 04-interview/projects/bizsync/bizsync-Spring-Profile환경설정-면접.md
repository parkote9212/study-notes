---
tags:
  - interview
  - spring
  - profile
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - Spring Profile 환경별 설정

## 질문
> 로컬/개발/운영 환경 설정을 어떻게 분리했나요?

## 핵심 답변 (3줄)
1. **Spring Profile** - `application-{profile}.yml`로 환경별 설정 분리
2. **환경변수 주입** - Docker에서 `SPRING_PROFILES_ACTIVE=prod` 전달
3. **민감정보 외부화** - DB 비밀번호, JWT Secret은 `.env` 파일로 관리

## 상세 설명
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

## 꼬리 질문 예상
- `.env` 파일이 유출되면 어떻게 대응하나요?
- AWS Secrets Manager를 사용한다면 어떻게 구성하나요?

## 참고
- [[bizsync-Docker-환경변수처리-면접]]
