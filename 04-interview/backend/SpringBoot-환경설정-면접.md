---
tags:
  - interview
  - Spring
  - Spring-Boot
  - Backend
created: 2026-01-24
difficulty: 상
---

# Spring Boot 환경 설정 면접

## 질문
> Spring Boot Profile, 환경변수 관리, .env 파일 사용법, 개발/프로덕션 환경 분리

## 핵심 답변 (3줄)
1. Profile로 환경별 설정 분리, application-{profile}.yml이 공통 설정을 오버라이드
2. 민감정보는 환경변수로 관리, .env 파일은 .gitignore 필수
3. 개발은 ddl-auto=update, 프로덕션은 validate로 설정하여 안전성 확보

## 상세 설명

### Q1: Spring Boot Profile은 어떻게 동작하나요?

**A**: `spring.profiles.active` 속성으로 지정된 Profile을 활성화합니다. 먼저 `application.yml`의 공통 설정을 로드한 후, `application-{profile}.yml` 파일의 설정을 로드하여 공통 설정을 오버라이드합니다.

예를 들어 `spring.profiles.active=dev`로 설정하면:
1. `application.yml` 로드 (공통)
2. `application-dev.yml` 로드 (환경별)
3. dev 설정이 공통 설정을 덮어씀

실행 시 `--spring.profiles.active=dev` 또는 환경변수 `SPRING_PROFILES_ACTIVE=dev`로 지정할 수 있습니다.

---

### Q2: .env 파일을 왜 .gitignore에 추가해야 하나요?

**A**: .env 파일에는 데이터베이스 비밀번호, JWT Secret Key, API Key 등 민감한 정보가 포함되어 있습니다. 이 파일이 Git 저장소에 커밋되면:

1. **보안 위험**: 누구나 저장소에 접근하면 민감정보 확인 가능
2. **공격 표적**: GitHub 등 공개 저장소에 올라가면 자동 크롤러가 탐지하여 악용
3. **규정 위반**: 개인정보보호법, 정보보안 규정 위반 가능

대신 `.env.example` 파일을 제공하여 팀원들이 복사해서 사용하도록 하고, 실제 값은 각자 로컬 환경이나 배포 서버의 환경변수로 관리해야 합니다.

---

### Q3: 개발 환경과 프로덕션 환경의 설정 차이는?

**A**:

| 항목 | 개발(dev) | 프로덕션(prod) |
|------|-----------|---------------|
| **ddl-auto** | update (자동 변경) | validate (검증만) |
| **show-sql** | true (디버깅) | false (성능) |
| **로그 레벨** | DEBUG | INFO/WARN |
| **JWT 만료** | 길게 (1시간) | 짧게 (15분) |
| **Connection Pool** | 작게 (5) | 크게 (20) |

개발 환경은 개발 편의성과 디버깅에 초점을 맞추고, 프로덕션은 보안과 성능에 초점을 맞춥니다.

---

### Q4: 환경변수를 읽는 우선순위는?

**A**: Spring Boot의 환경변수 우선순위는 다음과 같습니다 (높은 것부터):

1. 커맨드라인 인자 (`--spring.datasource.url=...`)
2. OS 환경변수 (`export SPRING_DATASOURCE_URL=...`)
3. application-{profile}.yml
4. application.yml
5. 기본값 (`${VAR:defaultValue}`의 defaultValue)

```yaml
url: ${SPRING_DATASOURCE_URL:jdbc:mariadb://localhost:3306/db}
```

이 경우:
1. 환경변수 `SPRING_DATASOURCE_URL`이 있으면 사용
2. 없으면 기본값 `jdbc:mariadb://localhost:3306/db` 사용

---

### Q5: IDE에서 환경변수 설정하는 방법은?

**A**:

**IntelliJ IDEA**:
1. Run → Edit Configurations
2. Environment variables 항목에 추가: `SPRING_DATASOURCE_URL=...;SPRING_DATASOURCE_PASSWORD=...`
3. Active profiles: dev

**또는 EnvFile 플러그인 사용**:
1. Plugins → "EnvFile" 설치
2. Run Configuration에서 .env 파일 선택

**추천 방법: application-local.yml**
```yaml
# application-local.yml (Git 제외)
spring:
  datasource:
    password: my-local-password
```
`.gitignore`에 추가하고 `--spring.profiles.active=local`로 실행

---

### Q6: JWT Secret을 안전하게 생성하는 방법은?

**A**:

```bash
# Base64 256-bit 키 생성
openssl rand -base64 32
# 출력: lN0xUqML23EcTlpnWIwhUkhiyTPYhnfKNxKq3A2H3gU=
```

또는 Java로 생성:
```java
import java.security.SecureRandom;
import java.util.Base64;

SecureRandom random = new SecureRandom();
byte[] key = new byte[32];  // 256 bits
random.nextBytes(key);
String encodedKey = Base64.getEncoder().encodeToString(key);
System.out.println("JWT_SECRET=" + encodedKey);
```

**중요**: 256-bit 이상의 안전한 키 사용 필수

---

### Q7: 프로덕션 배포 시 체크리스트는?

**A**:
- [ ] .env 파일이 .gitignore에 포함
- [ ] application-prod.yml에 하드코딩된 비밀번호 없음
- [ ] JWT Secret이 256-bit 이상
- [ ] ddl-auto가 validate 또는 none
- [ ] show-sql이 false
- [ ] 로그 레벨이 INFO 이상
- [ ] Connection Pool 설정이 적절
- [ ] 환경변수가 모두 설정됨

## 꼬리 질문 예상
- Profile을 여러 개 동시에 활성화할 수 있나요?
- @Value와 @ConfigurationProperties의 차이는?
- Spring Cloud Config는 무엇인가요?

## 참고
- [[SpringBoot-환경별-설정-관리]]
- [[환경변수-관리]]
- [[보안-설정]]
