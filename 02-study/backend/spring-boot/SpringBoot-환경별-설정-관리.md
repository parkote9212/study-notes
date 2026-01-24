---
tags: study, Spring, Spring-Boot, Profile, DevOps
created: 2026-01-24
---

# Spring Boot 환경별 설정 관리

## 한 줄 요약
> Spring Boot Profile과 환경변수로 개발/스테이징/프로덕션 환경을 분리하여 각각에 적합한 설정을 적용하고 보안성 확보

## 상세 설명

환경별 설정 관리는 각 환경(dev, staging, prod)에 맞는 설정을 적용하는 전략입니다. Profile로 환경을 분리하고, 민감정보는 환경변수로 관리하며, .env 파일은 반드시 .gitignore에 추가합니다.

### Profile 개념

```
application.yml (공통) → application-{profile}.yml (환경별)
```

**동작 원리**:
1. application.yml 로드 (기본 설정)
2. spring.profiles.active 확인
3. application-{active}.yml 로드 (환경별 설정)
4. 환경별 설정이 공통 설정을 오버라이드

### 환경별 주요 차이

| 항목 | 개발(dev) | 프로덕션(prod) |
|------|-----------|---------------|
| **ddl-auto** | update (자동 변경) | validate (검증만) |
| **show-sql** | true (디버깅) | false (성능) |
| **로그 레벨** | DEBUG | INFO/WARN |
| **JWT 만료** | 길게 (1시간) | 짧게 (15분) |
| **Connection Pool** | 작게 (5) | 크게 (20) |

### .env 파일 활용

**장점**:
- 민감정보 분리 (Git 제외)
- 로컬 개발 편의성
- 팀원마다 다른 설정 가능

**주의**: Spring Boot는 기본적으로 .env를 지원하지 않음, IDE 플러그인 또는 직접 환경변수로 등록 필요

### Profile 전환 방법

**Gradle**:
```bash
./gradlew bootRun --args='--spring.profiles.active=dev'
```

**JAR 실행**:
```bash
java -jar app.jar --spring.profiles.active=prod
```

**환경변수**:
```bash
export SPRING_PROFILES_ACTIVE=prod
java -jar app.jar
```

### 보안 모범 사례

**절대 하지 말 것**:
- application.yml에 비밀번호 하드코딩
- JWT Secret을 Git에 커밋
- .env 파일을 Git에 포함

**올바른 방법**:
- 환경변수로만 전달
- 256-bit 이상의 안전한 Secret Key
- .env.example 템플릿 제공

## 코드 예시

```yaml
# application.yml (공통)
spring:
  application:
    name: BizSync
mybatis:
  mapper-locations: classpath:mapper/**/*.xml

# application-dev.yml (개발)
spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:mariadb://localhost:3306/bizsync}
    username: ${SPRING_DATASOURCE_USERNAME:root}
    password: ${SPRING_DATASOURCE_PASSWORD:1234}
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
logging:
  level:
    com.bizsync.backend: DEBUG

# application-prod.yml (프로덕션)
spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL}
    username: ${SPRING_DATASOURCE_USERNAME}
    password: ${SPRING_DATASOURCE_PASSWORD}
    hikari:
      maximum-pool-size: 20
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
logging:
  level:
    root: WARN
    com.bizsync.backend: INFO

# .env 파일
SPRING_DATASOURCE_URL=jdbc:mariadb://localhost:3306/bizsync
SPRING_DATASOURCE_USERNAME=root
SPRING_DATASOURCE_PASSWORD=1234
JWT_SECRET=lN0xUqML23EcTlpnWIwhUkhiyTPYhnfKNxKq3A2H3gU=
SPRING_PROFILES_ACTIVE=dev

# JWT Secret 생성
openssl rand -base64 32
```

## 주의사항 / 함정

1. **.env 파일 Git 커밋**: 보안 사고 발생
2. **환경변수 미설정**: 프로덕션에서 기본값 사용되어 문제 발생
3. **Profile 미활성화**: 개발 설정이 프로덕션에 적용
4. **하드코딩된 비밀번호**: 저장소 노출 시 보안 위협

**프로덕션 체크리스트**:
- [ ] .env 파일이 .gitignore에 포함
- [ ] 하드코딩된 비밀번호 없음
- [ ] JWT Secret이 256-bit 이상
- [ ] ddl-auto가 validate 또는 none
- [ ] show-sql이 false
- [ ] 로그 레벨이 INFO 이상

## 관련 개념
- [[Spring-Profile]]
- [[환경변수-관리]]
- [[보안-설정]]
- [[Docker-환경변수]]

## 면접 질문
1. Spring Boot Profile은 어떻게 동작하나요?
2. .env 파일을 왜 .gitignore에 추가해야 하나요?
3. 개발 환경과 프로덕션 환경의 설정 차이는?
4. 환경변수를 읽는 우선순위는?

## 참고 자료
- Spring Boot 공식 문서
- 실무 프로젝트: BizSync
