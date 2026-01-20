# [Spring Boot] 환경별 설정 관리 완벽 가이드 (Profile, .env)

🏷️기술 카테고리: DevOps, Spring
💡핵심키워드: #Profile, #dotenv, #설정관리, #환경변수
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): Yes
날짜: 2026년 1월 16일 오후 11:04
📅 다음 복습일: 2026년 1월 25일

# 1. Abstract: 핵심 요약

> **환경별 설정 관리**는 개발(dev), 스테이징(staging), 프로덕션(prod) 환경을 분리하여 각각에 적합한 설정을 적용하는 전략입니다. Spring Boot Profile과 .env 파일을 활용하여 보안성과 유지보수성을 동시에 확보합니다.
> 

**핵심 원칙**:

- 환경별 설정 파일 분리 (application-{profile}.yml)
- 민감정보는 .env 파일 또는 환경변수로 관리
- .env 파일은 반드시 .gitignore에 추가
- IDE별 환경변수 설정 방법 숙지

---

# 2. Spring Boot Profile 전략

## 2.1 Profile 개념

**Profile**은 환경별로 다른 설정을 적용하기 위한 Spring의 기능입니다.

```
📁 src/main/resources
├── application.yml           # 공통 설정 (모든 환경)
├── application-dev.yml       # 개발 환경
├── application-staging.yml   # 스테이징 환경
└── application-prod.yml      # 프로덕션 환경
```

**동작 원리**:

```
1. application.yml 로드 (기본 설정)
    ↓
2. spring.profiles.active 확인
    ↓
3. application-{active}.yml 로드 (환경별 설정)
    ↓
4. 환경별 설정이 공통 설정을 오버라이드
```

---

## 2.2 실전 예시: BizSync 프로젝트

### application.yml (공통 설정)

```yaml
spring:
  application:
    name: BizSync

  # 공통 설정
  servlet:
    encoding:
      charset: UTF-8
      force: true

mybatis:
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: com.bizsync.backend.domain
  configuration:
    map-underscore-to-camel-case: true
```

**포인트**:

- 모든 환경에서 공통으로 사용하는 설정만 작성
- DB 연결 정보, 포트 등 환경별로 다른 설정은 제외

---

### application-dev.yml (개발 환경)

```yaml
spring:
  datasource:
    driver-class-name: ${SPRING_DATASOURCE_DRIVER:org.mariadb.jdbc.Driver}
    url: ${SPRING_DATASOURCE_URL:jdbc:mariadb://[localhost:3306/bizsync](http://localhost:3306/bizsync)}
    username: ${SPRING_DATASOURCE_USERNAME:root}
    password: ${SPRING_DATASOURCE_PASSWORD:1234}

  jpa:
    hibernate:
      ddl-auto: update  # ✅ 개발: 스키마 자동 업데이트
    show-sql: true      # ✅ SQL 로그 출력
    properties:
      hibernate:
        format_sql: true  # SQL 포맷팅
        dialect: org.hibernate.dialect.MariaDBDialect

server:
  port: ${SERVER_PORT:8080}

app:
  jwt:
    secret: ${JWT_SECRET:dev-secret-key-must-be-256-bits}
    expiration-ms: 3600000      # 1시간
    refresh-expiration-ms: 604800000  # 7일

# 개발 전용 설정
logging:
  level:
    com.bizsync.backend: DEBUG
    org.hibernate.SQL: DEBUG
```

**특징**:

- `ddl-auto: update` - 스키마 자동 생성/수정
- `show-sql: true` - SQL 쿼리 확인
- DEBUG 레벨 로깅

---

### application-prod.yml (프로덕션 환경)

```yaml
spring:
  datasource:
    driver-class-name: ${SPRING_DATASOURCE_DRIVER}
    url: ${SPRING_DATASOURCE_URL}
    username: ${SPRING_DATASOURCE_USERNAME}
    password: ${SPRING_DATASOURCE_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000

  jpa:
    hibernate:
      ddl-auto: validate  # ❌ 프로덕션: 스키마 검증만
    show-sql: false       # ❌ SQL 로그 비활성화
    properties:
      hibernate:
        format_sql: false
        dialect: org.hibernate.dialect.MariaDBDialect

server:
  port: ${SERVER_PORT:8080}
  shutdown: graceful  # 우아한 종료

app:
  jwt:
    secret: ${JWT_SECRET}  # ⚠️ 환경변수 필수 (기본값 없음)
    expiration-ms: ${JWT_EXPIRATION_MS:900000}  # 15분
    refresh-expiration-ms: ${JWT_REFRESH_EXPIRATION_MS:604800000}

logging:
  level:
    root: WARN
    com.bizsync.backend: INFO
```

**특징**:

- `ddl-auto: validate` - 스키마 변경 불가, 검증만
- `show-sql: false` - 성능을 위해 SQL 로그 비활성화
- Connection Pool 설정
- 짧은 Access Token 만료시간
- 기본값 제거 (환경변수 강제)

---

# 3. .env 파일 활용

## 3.1 .env 파일이란?

**정의**: 환경변수를 파일로 관리하는 방식 (Node.js의 dotenv와 유사)

**장점**:

- ✅ 민감정보 분리 (Git 제외)
- ✅ 로컬 개발 편의성
- ✅ 팀원마다 다른 설정 가능

**주의**:

- ⚠️ Spring Boot는 기본적으로 .env를 지원하지 않음
- ⚠️ IDE 플러그인 또는 직접 환경변수로 등록 필요

---

## 3.2 .env 파일 예시

```bash
# .env (프로젝트 루트)

# Database
SPRING_DATASOURCE_DRIVER=org.mariadb.jdbc.Driver
SPRING_DATASOURCE_URL=jdbc:mariadb://[localhost:3306/bizsync?serverTimezone=Asia/Seoul](http://localhost:3306/bizsync?serverTimezone=Asia/Seoul)
SPRING_DATASOURCE_USERNAME=root
SPRING_DATASOURCE_PASSWORD=1234

# JPA
SPRING_JPA_HIBERNATE_DDL_AUTO=update
SPRING_JPA_SHOW_SQL=true

# JWT (⚠️ 실제 프로덕션에서는 안전한 키 사용)
JWT_SECRET=lN0xUqML23EcTlpnWIwhUkhiyTPYhnfKNxKq3A2H3gU=
JWT_EXPIRATION_MS=3600000

# Server
SERVER_PORT=8080

# Active Profile
SPRING_PROFILES_ACTIVE=dev
```

---

## 3.3 .env.example 템플릿 제공

```bash
# .env.example (Git에 커밋)

# Database
SPRING_DATASOURCE_DRIVER=org.mariadb.jdbc.Driver
SPRING_DATASOURCE_URL=jdbc:mariadb://[localhost:3306/your_database](http://localhost:3306/your_database)
SPRING_DATASOURCE_USERNAME=your_username
SPRING_DATASOURCE_PASSWORD=your_password

# JWT
JWT_SECRET=generate-your-own-256-bit-secret-key
JWT_EXPIRATION_MS=3600000

# Server
SERVER_PORT=8080
SPRING_PROFILES_ACTIVE=dev
```

**사용법**:

```bash
# 새 팀원 온보딩
cp .env.example .env
# .env 파일 수정 (자신의 환경에 맞게)
```

---

## 3.4 .gitignore 필수 설정

```
# .gitignore

### Environment Variables ###
.env
.env.local
.env.*.local

### IDE ###
.idea/
*.iml
.vscode/

### Build ###
build/
target/
*.jar
*.war
```

**⚠️ 중요**: .env 파일이 Git에 포함되면 보안 사고 발생!

---

# 4. IDE별 환경변수 설정

## 4.1 IntelliJ IDEA 설정

### 방법 1: Run Configuration (권장)

```
1. Run → Edit Configurations
    ↓
2. Spring Boot Application 선택
    ↓
3. Environment variables 항목에 추가:
   SPRING_DATASOURCE_URL=jdbc:mariadb://[localhost:3306/bizsync](http://localhost:3306/bizsync);
   SPRING_DATASOURCE_USERNAME=root;
   SPRING_DATASOURCE_PASSWORD=1234;
   JWT_SECRET=your-secret-key
    ↓
4. Active profiles: dev
```

**장점**:

- 프로젝트별 독립적 관리
- 팀원 간 충돌 없음

---

### 방법 2: EnvFile Plugin

```
1. Plugins → "EnvFile" 설치
    ↓
2. Run → Edit Configurations
    ↓
3. EnvFile 탭 선택
    ↓
4. Enable EnvFile 체크
    ↓
5. + 버튼 → .env 파일 선택
    ↓
6. Apply → OK
```

**장점**:

- .env 파일 직접 사용
- Node.js 개발자에게 익숙

---

### 방법 3: application-local.yml (추천)

```yaml
# application-local.yml (Git 제외)

spring:
  datasource:
    url: jdbc:mariadb://[localhost:3306/bizsync](http://localhost:3306/bizsync)
    username: root
    password: my-local-password  # 개인 설정

app:
  jwt:
    secret: my-local-jwt-secret
```

```bash
# 실행 시
java -jar app.jar --spring.profiles.active=local
```

**.gitignore 추가**:

```
application-local.yml
[application-local.properties](http://application-local.properties)
```

---

## 4.2 Eclipse 설정

```
1. Run → Run Configurations
    ↓
2. Spring Boot App 선택
    ↓
3. (x)= Environment 탭
    ↓
4. New 버튼으로 환경변수 추가
   Name: SPRING_DATASOURCE_URL
   Value: jdbc:mariadb://[localhost:3306/bizsync](http://localhost:3306/bizsync)
    ↓
5. Profile 탭 → dev 입력
```

---

## 4.3 VS Code 설정

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "java",
      "name": "Spring Boot-BackendApplication",
      "request": "launch",
      "mainClass": "com.bizsync.backend.BackendApplication",
      "projectName": "backend",
      "args": "--spring.profiles.active=dev",
      "env": {
        "SPRING_DATASOURCE_URL": "jdbc:mariadb://[localhost:3306/bizsync](http://localhost:3306/bizsync)",
        "SPRING_DATASOURCE_USERNAME": "root",
        "SPRING_DATASOURCE_PASSWORD": "1234",
        "JWT_SECRET": "your-secret-key"
      },
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

**.gitignore 추가**:

```
.vscode/
!.vscode/launch.json.example
```

---

# 5. Profile 전환 방법

## 5.1 실행 시 Profile 지정

### Gradle

```bash
# 개발 환경
./gradlew bootRun --args='--spring.profiles.active=dev'

# 프로덕션 환경
./gradlew bootRun --args='--spring.profiles.active=prod'
```

### JAR 실행

```bash
# 개발
java -jar app.jar --spring.profiles.active=dev

# 프로덕션
java -jar -Dspring.profiles.active=prod app.jar

# 환경변수로
export SPRING_PROFILES_ACTIVE=prod
java -jar app.jar
```

### Docker

```docker
# Dockerfile
FROM openjdk:21-jdk-slim
ARG JAR_FILE=build/libs/*.jar
COPY ${JAR_FILE} app.jar

ENV SPRING_PROFILES_ACTIVE=prod

ENTRYPOINT ["java", "-jar", "/app.jar"]
```

```bash
# docker-compose.yml
version: '3'
services:
  backend:
    build: .
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - SPRING_DATASOURCE_URL=${DB_URL}
      - JWT_SECRET=${JWT_SECRET}
    env_file:
      - .[env.prod](http://env.prod)
```

---

## 5.2 application.yml에서 기본 Profile 설정

```yaml
spring:
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}  # 기본값: dev
```

**장점**: 별도 지정 없으면 dev 환경 사용

---

# 6. 보안 모범 사례

## 6.1 민감정보 관리 원칙

### ❌ 절대 하지 말 것

```yaml
# ❌ application.yml에 하드코딩
spring:
  datasource:
    password: admin1234  # Git에 노출!

app:
  jwt:
    secret: my-secret-key  # 보안 취약!
```

---

### ✅ 올바른 방법

```yaml
# ✅ 환경변수 사용
spring:
  datasource:
    password: ${SPRING_DATASOURCE_PASSWORD}

app:
  jwt:
    secret: ${JWT_SECRET}
```

**환경변수로만 전달**:

```bash
export SPRING_DATASOURCE_PASSWORD="secure-password"
export JWT_SECRET="256-bit-secure-random-key"
```

---

## 6.2 JWT Secret 생성

### 안전한 Secret Key 생성

```bash
# Base64 256-bit 키 생성
openssl rand -base64 32
# 출력: lN0xUqML23EcTlpnWIwhUkhiyTPYhnfKNxKq3A2H3gU=
```

```java
// Java로 생성
import [java.security](http://java.security).SecureRandom;
import java.util.Base64;

public class KeyGenerator {
    public static void main(String[] args) {
        SecureRandom random = new SecureRandom();
        byte[] key = new byte[32];  // 256 bits
        random.nextBytes(key);
        String encodedKey = Base64.getEncoder().encodeToString(key);
        System.out.println("JWT_SECRET=" + encodedKey);
    }
}
```

---

## 6.3 프로덕션 환경 체크리스트

- [ ]  .env 파일이 .gitignore에 포함되어 있는가?
- [ ]  application-prod.yml에 하드코딩된 비밀번호가 없는가?
- [ ]  JWT Secret이 256-bit 이상인가?
- [ ]  ddl-auto가 validate 또는 none인가?
- [ ]  show-sql이 false인가?
- [ ]  로그 레벨이 INFO 이상인가?
- [ ]  Connection Pool 설정이 적절한가?
- [ ]  환경변수가 모두 설정되어 있는가?

---

# 7. 트러블슈팅

## 문제 1: Profile이 적용되지 않음

```bash
# 증상
# application-dev.yml 설정이 무시됨

# 원인
# Profile이 활성화되지 않음

# 해결
# 1. 확인
java -jar app.jar --debug | grep "active profiles"

# 2. 명시적 지정
java -jar app.jar --spring.profiles.active=dev

# 3. 환경변수 확인
echo $SPRING_PROFILES_ACTIVE
```

---

## 문제 2: 환경변수가 인식되지 않음

```bash
# 증상
# ${SPRING_DATASOURCE_URL} 그대로 출력

# 원인
# 1. 환경변수 미설정
# 2. IDE Run Configuration 미설정

# 해결
# IntelliJ: Run → Edit Configurations → Environment variables
# 또는 터미널에서:
export SPRING_DATASOURCE_URL="jdbc:mariadb://[localhost:3306/db](http://localhost:3306/db)"
./gradlew bootRun
```

---

## 문제 3: .env 파일이 작동하지 않음

```bash
# 증상
# .env 파일 설정이 무시됨

# 원인
# Spring Boot는 기본적으로 .env 미지원

# 해결
# 1. EnvFile 플러그인 설치 (IntelliJ)
# 2. 또는 직접 환경변수로 export
set -a
source .env
set +a
./gradlew bootRun

# 3. 또는 application-local.yml 사용
```

---

# 8. Interview Readiness

## ▶ Q1: Spring Boot Profile은 어떻게 동작하나요?

**A**: Spring Boot는 `spring.profiles.active` 속성으로 지정된 Profile을 활성화합니다. 먼저 `application.yml`의 공통 설정을 로드한 후, `application-{profile}.yml` 파일의 설정을 로드하여 공통 설정을 오버라이드합니다.

예를 들어 `spring.profiles.active=dev`로 설정하면:

1. `application.yml` 로드 (공통)
2. `application-dev.yml` 로드 (환경별)
3. dev 설정이 공통 설정을 덮어씀

실행 시 `--spring.profiles.active=dev` 또는 환경변수 `SPRING_PROFILES_ACTIVE=dev`로 지정할 수 있으며, 여러 Profile을 동시에 활성화할 수도 있습니다 (`dev,local`).

---

## ▶ Q2: .env 파일을 왜 .gitignore에 추가해야 하나요?

**A**: .env 파일에는 데이터베이스 비밀번호, JWT Secret Key, API Key 등 민감한 정보가 포함되어 있습니다. 이 파일이 Git 저장소에 커밋되면:

1. **보안 위험**: 누구나 저장소에 접근하면 민감정보 확인 가능
2. **공격 표적**: GitHub 등 공개 저장소에 올라가면 자동 크롤러가 탐지하여 악용
3. **규정 위반**: 개인정보보호법, 정보보안 규정 위반 가능

대신 `.env.example` 파일을 제공하여 팀원들이 복사해서 사용하도록 하고, 실제 값은 각자 로컬 환경이나 배포 서버의 환경변수로 관리해야 합니다.

---

## ▶ Q3: 개발 환경과 프로덕션 환경의 설정 차이는?

**A**:

| 항목 | 개발(dev) | 프로덕션(prod) |
| --- | --- | --- |
| **ddl-auto** | update (자동 변경) | validate (검증만) |
| **show-sql** | true (디버깅) | false (성능) |
| **로그 레벨** | DEBUG | INFO/WARN |
| **JWT 만료** | 길게 (1시간) | 짧게 (15분) |
| **Connection Pool** | 작게 (5) | 크게 (20) |

개발 환경은 개발 편의성과 디버깅에 초점을 맞추고, 프로덕션은 보안과 성능에 초점을 맞춥니다.

---

## ▶ Q4: 환경변수를 읽는 우선순위는?

**A**: Spring Boot의 환경변수 우선순위는 다음과 같습니다 (높은 것부터):

1. 커맨드라인 인자 (`--spring.datasource.url=...`)
2. OS 환경변수 (`export SPRING_DATASOURCE_URL=...`)
3. application-{profile}.yml
4. application.yml
5. 기본값 (`${VAR:defaultValue}`의 defaultValue)

예를 들어:

```yaml
url: ${SPRING_DATASOURCE_URL:jdbc:mariadb://[localhost:3306/db](http://localhost:3306/db)}
```

이 경우:

1. 환경변수 `SPRING_DATASOURCE_URL`이 있으면 사용
2. 없으면 기본값 `jdbc:mariadb://[localhost:3306/db](http://localhost:3306/db)` 사용

---

## 🔑 핵심 체크리스트

- [ ]  application.yml에 공통 설정만 작성
- [ ]  환경별 설정은 application-{profile}.yml로 분리
- [ ]  민감정보는 환경변수로 관리
- [ ]  .env 파일은 .gitignore에 추가
- [ ]  .env.example 템플릿 제공
- [ ]  IDE Run Configuration 설정
- [ ]  프로덕션: ddl-auto=validate, show-sql=false
- [ ]  JWT Secret 256-bit 이상
- [ ]  Profile 전환 방법 숙지

---

**작성일**: 2026-01-16  

**면접 빈출도**: ⭐⭐⭐⭐ (상)  

**프로젝트**: bizsync-backend 실제 사례 기반