# Claude Projects & Skills 완벽 가이드

> **작성일**: 2026-02-03  
> **대상**: Claude.ai 웹/앱 사용자 (Pro, Max, Team, Enterprise)  
> **범위**: Claude Projects (claude.ai), Agent Skills (공통 표준)

---

## Part 1: Claude Projects

### 1. Projects란?

Claude Projects는 claude.ai 내의 **영구적인 워크스페이스**다. 일반 대화가 매번 컨텍스트를 잃는 반면, Projects는 커스텀 지시사항, 문서 라이브러리, 대화 기록을 **지속적으로 유지**한다.

**핵심 가치**: AI와의 대화에서 가장 큰 비효율인 **"매번 처음부터 설명하기"** 문제를 해결한다.

### 2. Projects의 주요 기능

| 기능 | 설명 |
|------|------|
| 커스텀 지시사항 | 프로젝트별 행동 규칙/페르소나 설정 |
| 문서 업로드 | 파일을 한 번 업로드하면 모든 대화에서 참조 |
| 대화 기록 유지 | 프로젝트 내 모든 대화가 정리되어 보관 |
| 팀 협업 | 프로젝트를 팀원과 공유 (View Only 가능) |
| 200K 토큰 컨텍스트 | 약 500페이지 분량의 문서를 컨텍스트에 유지 |

### 3. Projects 생성 및 설정

#### 3.1 프로젝트 생성

1. claude.ai 접속 → 좌측 사이드바 **"Projects"** 클릭
2. 우측 상단 **"New Project"** 클릭
3. 프로젝트 이름 입력 (예: "BizSync 개발", "기술면접 준비")
4. 설명 입력 (선택)

#### 3.2 커스텀 지시사항 작성

**"Set Custom Instructions"** 클릭 후 작성:

```
당신은 시니어 Java/Spring Boot 개발자입니다.

## 역할
- 코드 리뷰 시 보안과 성능을 우선시합니다
- 모든 응답은 한국어로 합니다
- 코드 예시는 Java 17+ 문법을 사용합니다

## 코딩 스타일
- Spring Boot 3.x + JPA 기반
- RESTful API 설계 원칙 준수
- Conventional Commits 형식
- Google Java Style Guide 준수

## 응답 형식
- 코드 블록에는 항상 언어 지정
- 중요한 설계 결정은 이유도 함께 설명
- 복잡한 로직은 단계별로 분해
```

#### 3.3 문서 업로드

**"Upload from Device"** 또는 드래그 앤 드롭:

**권장 업로드 문서 유형**:
- 프로젝트 코드베이스 주요 파일
- API 문서/스펙
- 스타일 가이드/코딩 컨벤션
- 아키텍처 설계 문서
- 면접 준비 자료
- 이력서, 자기소개서 초안

### 4. 효과적인 커스텀 지시사항 작성법

#### 4.1 구성 요소

```
# 역할 정의
당신은 [구체적인 역할]입니다.

# 배경 정보
[사용자에 대한 컨텍스트: 경력, 기술 수준, 목표 등]

# 행동 규칙
- [구체적인 행동 지침 1]
- [구체적인 행동 지침 2]
- [금지사항]

# 응답 형식
- [원하는 응답 스타일]
- [사용할 언어/톤]

# 참고사항
- [프로젝트 특이사항]
- [자주 사용하는 도구/기술]
```

#### 4.2 실전 예시

**기술면접 준비 프로젝트**:
```
당신은 10년 경력의 시니어 Java 개발자이자 기술 면접관입니다.

## 컨텍스트
- 면접 대상: 건설업 8년 경력 후 풀스택 개발로 전환한 지원자
- 기술 스택: Java, Spring Boot, React, MariaDB
- 포트폴리오: BizSync(ERP), fitneeds(스포츠시설), Recipick(AI레시피)

## 행동 규칙
- 실제 면접처럼 질문하고 답변을 평가해주세요
- 답변이 부족하면 꼬리 질문을 하세요
- 각 답변에 대해 5점 만점으로 채점하고 개선점을 알려주세요
- 실무 프로젝트 경험과 연결된 질문을 우선하세요

## 금지사항
- 지나치게 쉬운 질문은 하지 마세요
- 정답을 바로 알려주지 말고 힌트를 먼저 주세요
```

**코드 리뷰 프로젝트**:
```
당신은 코드 리뷰 전문 AI입니다.

## 리뷰 기준 (우선순위 순)
1. 보안 취약점 (Critical)
2. 성능 문제 (High)
3. 코드 품질 및 가독성 (Medium)
4. 테스트 커버리지 (Low)

## 출력 형식
각 이슈를 다음 형태로 보고:
🔴 [Critical] 파일명:라인 - 설명
🟡 [Warning] 파일명:라인 - 설명
🟢 [Info] 파일명:라인 - 설명

## 규칙
- 간결하게 핵심만 지적
- 사소한 스타일 이슈는 무시
- 수정 코드 제안 시 before/after 형식 사용
```

### 5. Projects 활용 시나리오

| 시나리오 | 적합 여부 | 이유 |
|----------|-----------|------|
| 장기 프로젝트 개발 | ✅ | 컨텍스트 영속성 필요 |
| 기술면접 준비 | ✅ | 반복 학습, 진행 상황 추적 |
| 문서 분석 (계약서, 보고서) | ✅ | 대량 문서 기반 질의 |
| 팀 협업 (공유 워크스페이스) | ✅ | 일관된 AI 행동 보장 |
| 단순 질문 (날씨, 번역) | ❌ | 일반 대화로 충분 |
| 일회성 코드 스니펫 | ❌ | Projects 오버헤드 불필요 |

### 6. Projects 제한사항

- **플랜 제한**: Pro, Max, Team, Enterprise만 사용 가능
- **스토리지**: 프로젝트별 토큰 제한 (약 200K tokens)
- **격리된 컨텍스트**: 프로젝트 간 정보 공유 불가
- **파일 크기**: 업로드 파일 크기 제한 있음
- **팀 협업 시**: View Only 공유 — 수정 권한 공유 불가

---

## Part 2: Agent Skills

### 7. Agent Skills란?

Agent Skills는 Claude의 능력을 **모듈형 패키지로 확장**하는 시스템이다. 2025년 10월에 출시되었으며, **Agent Skills 오픈 스탠다드**를 기반으로 Claude.ai, Claude Code, Cursor 등 여러 플랫폼에서 사용 가능하다.

**핵심 개념**: "매번 같은 프로세스를 설명하는 대신, 한 번 패키징하면 자동으로 적용된다."

### 8. Skills vs Projects vs GPTs

| 특성 | Skills | Projects | Custom GPTs |
|------|--------|----------|-------------|
| 코드 실행 | ✅ 스크립트 포함 가능 | ❌ | ❌ |
| 자동 호출 | ✅ 맥락 매칭 시 자동 | ❌ 수동 선택 | ❌ 수동 선택 |
| 크로스 플랫폼 | ✅ 오픈 스탠다드 | ❌ claude.ai 전용 | ❌ ChatGPT 전용 |
| 재사용성 | ✅ 프로젝트 간 공유 | ❌ 프로젝트 고정 | 제한적 |
| 파일 포함 | ✅ 템플릿, 스크립트 | ✅ 문서 업로드 | 제한적 |

### 9. Skill 구조

#### 9.1 기본 구조

```
my-skill/
├── SKILL.md           # 핵심 파일 (필수)
├── templates/         # 템플릿 (선택)
│   └── template.md
├── examples/          # 예시 (선택)
│   └── sample.md
├── scripts/           # 실행 스크립트 (선택)
│   └── generate.py
└── resources/         # 참조 자료 (선택)
    └── reference.md
```

#### 9.2 SKILL.md 필수 구조

```yaml
---
name: skill-name
description: >
  이 Skill이 언제 사용되어야 하는지 설명.
  Claude가 이 설명을 보고 자동으로 호출할지 결정한다.
---
```

```markdown
# Skill 제목

## 목적
이 Skill은 [목적]을 위해 사용됩니다.

## 지시사항
1. [단계 1]
2. [단계 2]
3. [단계 3]

## 입력
- [예상 입력 형태]

## 출력
- [기대하는 출력 형태]

## 예시
[구체적인 입력/출력 예시]
```

### 10. Skill 저장 위치

#### Claude.ai (웹/앱)

Skills는 코드 실행 환경에서 자동 감지:
```
/mnt/skills/public/     # Anthropic 공식 Skills
/mnt/skills/user/       # 사용자 업로드 Skills
/mnt/skills/examples/   # 예시 Skills
```

#### Claude Code

```
~/.claude/skills/       # 사용자 레벨 (모든 프로젝트)
.claude/skills/         # 프로젝트 레벨
```

**우선순위**: enterprise > personal > project

### 11. Skill 작성 실전 예시

#### 11.1 이력서 최적화 Skill

```yaml
---
name: resume-optimizer
description: >
  이력서를 특정 채용공고에 맞게 최적화.
  이력서 수정, 키워드 매칭, ATS 최적화 시 사용.
---
```

```markdown
# 이력서 최적화

## 프로세스
1. 채용공고의 핵심 요구사항과 키워드를 추출
2. 현재 이력서의 강점/약점 분석
3. 채용공고 키워드와 이력서 매칭률 계산
4. 수정 제안 사항 작성

## 출력 형식
### 📊 매칭 분석
- 필수 요구사항 매칭: X/Y
- 키워드 매칭률: XX%
- 누락된 핵심 키워드: [목록]

### ✏️ 수정 제안
각 섹션별 구체적 수정안 제시

### 📝 수정된 이력서
최종 이력서 전문
```

#### 11.2 Spring Boot API 생성 Skill

```yaml
---
name: spring-api-generator
description: >
  Spring Boot REST API 엔드포인트를 표준 패턴으로 생성.
  컨트롤러, 서비스, DTO, 테스트를 한 번에 생성.
---
```

```markdown
# Spring Boot API Generator

## 생성 파일
주어진 엔티티 이름을 기반으로 다음 파일들을 생성합니다:

1. `{Entity}Controller.java` - REST 컨트롤러
2. `{Entity}Service.java` - 서비스 인터페이스
3. `{Entity}ServiceImpl.java` - 서비스 구현
4. `{Entity}RequestDto.java` - 요청 DTO (record)
5. `{Entity}ResponseDto.java` - 응답 DTO (record)
6. `{Entity}ServiceTest.java` - 서비스 단위 테스트

## 코드 패턴
- @RestController + @RequestMapping
- 생성자 주입 (@RequiredArgsConstructor)
- ResponseEntity<> 반환
- @Valid 검증
- Pageable 지원 (목록 조회)
- JUnit 5 + Mockito 테스트

## 사용법
"User 엔티티에 대한 CRUD API를 생성해줘"라고 요청하면
위 파일들을 프로젝트 구조에 맞게 생성합니다.

## 참조 템플릿
[templates/ 디렉토리의 템플릿 파일 참조]
```

#### 11.3 스크립트 포함 Skill

```yaml
---
name: dependency-audit
description: >
  프로젝트 의존성의 보안 취약점과 라이선스 문제를 검사.
  의존성 감사, 보안 검사 요청 시 사용.
---
```

```markdown
# 의존성 감사

## 실행 방법
다음 스크립트를 실행하여 의존성을 감사합니다:

### Node.js 프로젝트
```bash
npm audit --json > audit-report.json
```

### Java/Gradle 프로젝트
```bash
./gradlew dependencyCheckAnalyze
```

## 보고서 작성
스크립트 결과를 분석하여 다음 형식으로 보고:

### 🔴 Critical (즉시 수정 필요)
### 🟡 High (1주 내 수정)
### 🟢 Medium/Low (다음 스프린트에 수정)

각 항목에 업그레이드 방법과 호환성 이슈를 포함.
```

### 12. Skills 관리 팁

#### 12.1 description이 핵심이다

Claude는 description을 기반으로 Skill을 자동 호출할지 결정한다. **라우팅 정확도는 description 품질에 달렸다.**

**나쁜 예**:
```yaml
description: 코드 관련 도움
```

**좋은 예**:
```yaml
description: >
  Spring Boot REST API 엔드포인트 생성.
  컨트롤러, 서비스, DTO, 테스트를 표준 패턴으로 한 번에 생성할 때 사용.
  "API 생성", "엔드포인트 추가", "CRUD 만들어줘" 같은 요청에 반응.
```

#### 12.2 SKILL.md는 가볍게, 참조 파일은 별도로

SKILL.md 자체는 **퀵 스타트 가이드**처럼 작성하고, 긴 템플릿이나 참조 문서는 하위 파일로 분리한다. 이렇게 해야 컨텍스트 윈도우를 효율적으로 사용할 수 있다.

#### 12.3 점진적 확장

1. 간단한 지시사항으로 시작
2. 테스트 후 부족한 부분 보완
3. 스크립트/템플릿 추가
4. 예시 파일로 품질 개선

#### 12.4 Skill 컨텍스트 예산

Claude Code에서 Skills의 description들은 컨텍스트에 로드된다 (기본 15,000자 한도). `/context`로 확인하고, 불필요한 Skills는 정리하자.

### 13. agentskills.io — 오픈 스탠다드

Agent Skills는 **오픈 스탠다드**다. Claude Code, Cursor, 기타 AI 도구에서 동일한 SKILL.md 형식을 사용할 수 있다. 한 번 만든 Skill을 여러 플랫폼에서 재사용할 수 있다는 의미다.

참고: [https://agentskills.io](https://agentskills.io)
