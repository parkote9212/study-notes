# Cursor Rules, Skills, Subagents 완벽 가이드

> **작성일**: 2026-02-03  
> **대상**: macOS Cursor IDE 사용자  
> **버전**: Cursor 2.4+ (2026년 1월 릴리스 기준)

---

## 1. 개요: Cursor의 확장 시스템

Cursor 2.4에서 대대적인 에이전트 시스템 업데이트가 있었다. 기존의 단일 `.cursorrules` 파일 방식에서 벗어나 **모듈형 확장 시스템**으로 전환되었다.

### 확장 기능 분류

| 기능 | 역할 | 위치 | 호출 방식 |
|------|------|------|-----------|
| **Rules** | 항상 적용되는 행동 규칙 | `.cursor/rules/` | 자동 (조건부/항상) |
| **Skills** | 온디맨드 전문 지식 패키지 | `.cursor/skills/` | 자동 (맥락 매칭) |
| **Subagents** | 독립 컨텍스트의 전문 에이전트 | `.cursor/agents/` | 자동/수동 위임 |
| **Commands** | 사용자가 직접 트리거하는 워크플로우 | `.cursor/commands/` | 수동 (`/명령어`) |
| **Hooks** | 이벤트 기반 자동 실행 스크립트 | 설정 파일 | 자동 (이벤트) |

### 핵심 차이점 요약

- **Rules** = 불변의 법칙 (항상/조건부 적용)
- **Skills** = 선택적 전문 지식 (필요할 때만 로드)
- **Subagents** = 독립 작업자 (격리된 컨텍스트에서 병렬 작업)
- **Commands** = 수동 단축키 (사용자가 명시적으로 호출)

---

## 2. Rules (규칙)

### 2.1 Rules란?

Rules는 Cursor 에이전트가 **항상 따라야 하는 지침**이다. `.cursor/rules/` 디렉토리에 `.mdc` 파일로 저장한다.

> ⚠️ 레거시 `.cursorrules` 파일은 deprecated 상태. `.cursor/rules/` 디렉토리로 이전 권장.

### 2.2 .mdc 파일 형식

```
---
description: "규칙의 목적을 설명하는 짧은 문장"
globs: "파일 패턴/**/*.ts"
alwaysApply: false
---

# 규칙 제목

규칙 내용 (Markdown 형식)
```

#### 프론트매터 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `description` | string | 규칙의 목적. Agent 타입 규칙에서 매칭 기준 |
| `globs` | string | 파일 패턴 (예: `**/*.ts`, `src/**/*.java`) |
| `alwaysApply` | boolean | true면 항상 컨텍스트에 포함 |

### 2.3 규칙 타입 4가지

| 타입 | 조건 | 동작 |
|------|------|------|
| **Always** | `alwaysApply: true` | 모든 요청에 항상 포함 |
| **Auto-Attach** | `globs` 정의, `alwaysApply: false` | 매칭 파일 작업 시 자동 포함 |
| **Agent** | `description` 있음, globs/always 없음 | AI가 관련성 판단 시 로드 |
| **Manual** | 아무 조건도 없음 | `@파일명`으로 수동 참조만 가능 |

### 2.4 규칙 타입별 사용 시기

**Always Apply** — 프로젝트 전역 컨텍스트:
```
---
description: "프로젝트 전역 컨텍스트 및 아키텍처 개요"
globs:
alwaysApply: true
---

# 프로젝트 컨텍스트

## 기술 스택
- Backend: Java 17, Spring Boot 3.2, JPA, MariaDB
- Frontend: React 18, TypeScript, Vite
- Build: Gradle

## 아키텍처
- 3-Tier Layered Architecture
- Controller → Service → Repository
- DTO 패턴 사용 (Entity ↔ DTO 변환)

## 네이밍 컨벤션
- 클래스: PascalCase
- 메서드/변수: camelCase
- 상수: UPPER_SNAKE_CASE
- 패키지: lowercase
```

**Auto-Attach** — 파일 타입별 자동 적용:
```
---
description: "CSS/스타일링 작업 시 적용할 규칙"
globs: "**/*.css,**/*.scss,**/*.module.css"
alwaysApply: false
---

# CSS 아키텍처 규칙

- CSS Modules 사용 (글로벌 CSS 금지)
- 디자인 토큰은 var(--token-name)으로만 사용
- 하드코딩된 색상값(hex, rgb) 금지
- BEM 네이밍 컨벤션 준수
- !important 사용 금지
```

```
---
description: "Java 파일 작업 시 적용할 코딩 표준"
globs: "**/*.java"
alwaysApply: false
---

# Java 코딩 표준

- Lombok 사용: @Getter, @RequiredArgsConstructor (Setter 지양)
- Optional 반환 시 orElseThrow() 사용
- Stream API 적극 활용 (for 루프 대신)
- checked exception 대신 RuntimeException 커스텀 계열 사용
- null 반환 대신 Optional 또는 빈 컬렉션 반환
```

**Agent** — AI가 필요할 때 로드:
```
---
description: "데이터베이스 마이그레이션이나 스키마 변경 작업 시 참조"
globs:
alwaysApply: false
---

# 데이터베이스 마이그레이션 규칙

- Flyway 사용 (V{버전}__{설명}.sql 형식)
- 마이그레이션 파일은 한 번 생성되면 수정 금지
- 반드시 롤백 스크립트도 함께 작성
- 인덱스 추가 시 CONCURRENTLY 옵션 고려
- 테이블 변경은 ALTER TABLE, DROP TABLE 최소화
```

**Manual** — 수동 참조:
```
---
description:
globs:
alwaysApply: false
---

# API 응답 형식 레퍼런스

## 성공 응답
{
  "status": "success",
  "data": { ... },
  "message": "처리되었습니다"
}

## 에러 응답
{
  "status": "error",
  "code": "ERR_001",
  "message": "에러 메시지"
}
```

사용: 대화에서 `@api-response-format` 으로 참조

### 2.5 Rules 디렉토리 구조 모범 사례

```
.cursor/
└── rules/
    ├── project-context.mdc        # Always — 프로젝트 개요
    ├── tech-stack.mdc             # Always — 기술 스택
    ├── java-standards.mdc         # Auto — Java 파일 규칙
    ├── typescript-standards.mdc   # Auto — TypeScript 규칙
    ├── css-architecture.mdc       # Auto — CSS 규칙
    ├── testing-guidelines.mdc     # Agent — 테스트 관련
    ├── db-migration.mdc           # Agent — DB 마이그레이션
    ├── security-checklist.mdc     # Agent — 보안 검토
    ├── api-design.mdc             # Agent — API 설계
    └── response-format.mdc        # Manual — 참조용
```

### 2.6 Rules 작성 팁

1. **모듈화**: 하나의 거대한 규칙 파일 대신, 도메인별로 분리
2. **구체적인 description**: Agent 타입 규칙은 description이 라우팅 기준
3. **중복 방지**: Always 규칙은 최소한으로 (컨텍스트 소모)
4. **globs 패턴 활용**: 파일 확장자, 디렉토리별로 세분화
5. **부정문 사용**: "하지 마세요" 보다 "대신 이것을 사용하세요" 형태가 효과적

### 2.7 User Rules & Team Rules

**User Rules** (Cursor Settings):
- 모든 프로젝트에 적용되는 개인 규칙
- Settings → Cursor Settings → Rules에서 설정
- 개인 작업 스타일/선호도 정의

**Team Rules (AGENTS.md)**:
- 팀 전체에 적용되는 규칙
- 프로젝트 루트에 `AGENTS.md` 파일 배치
- Git으로 버전 관리

---

## 3. Skills (스킬)

### 3.1 Skills란?

Skills는 **Agent Skills 오픈 스탠다드**를 따르는 전문 지식 패키지다. Rules가 "항상 적용되는 법칙"이라면, Skills는 "필요할 때 불러오는 전문서적"이다.

Cursor 2.4에서 공식 지원이 시작되었다.

### 3.2 Rules vs Skills

| 특성 | Rules | Skills |
|------|-------|--------|
| 적용 시점 | 항상/조건부 자동 | 맥락 매칭 시 자동 |
| 크기 | 가볍고 간결 | 길고 상세할 수 있음 |
| 코드 실행 | ❌ | ✅ 스크립트 포함 가능 |
| 포함 파일 | 단일 .mdc | 디렉토리 (SKILL.md + 하위 파일) |
| 용도 | 불변의 코딩 규칙 | 동적인 전문 지식/워크플로우 |
| 크로스 플랫폼 | Cursor 전용 | 오픈 스탠다드 (Claude Code 등) |

### 3.3 Skill 디렉토리 구조

```
.cursor/
└── skills/
    └── my-skill/
        ├── SKILL.md          # 필수 — 메인 지시사항
        ├── templates/        # 선택 — 템플릿 파일
        ├── examples/         # 선택 — 예시
        ├── scripts/          # 선택 — 실행 스크립트
        └── resources/        # 선택 — 참조 자료
```

### 3.4 SKILL.md 작성법

```yaml
---
name: react-component-generator
description: >
  React 컴포넌트를 프로젝트 표준에 맞게 생성.
  새 컴포넌트 생성, 페이지 추가, UI 모듈 작성 시 사용.
---
```

```markdown
# React Component Generator

## 목적
프로젝트 표준에 맞는 React 컴포넌트를 일관되게 생성합니다.

## 표준 구조
각 컴포넌트는 다음 파일로 구성:
- `ComponentName.tsx` — 컴포넌트 본체
- `ComponentName.module.css` — 스타일
- `ComponentName.test.tsx` — 테스트
- `index.ts` — 배럴 export

## 코드 패턴
- 함수형 컴포넌트 (arrow function)
- Props는 interface로 정의
- CSS Modules 사용
- React Testing Library로 테스트

## 참조
[templates/ComponentTemplate.tsx 참조]
```

### 3.5 실전 Skill 예시

#### API 문서 자동 생성 Skill

```yaml
---
name: api-doc-generator
description: >
  REST API 문서를 자동 생성. Swagger/OpenAPI 사양의
  API 문서화, 엔드포인트 문서 작성 요청 시 사용.
---
```

```markdown
# API Documentation Generator

## 프로세스
1. Controller 파일을 스캔
2. 각 엔드포인트의 HTTP 메서드, 경로, 파라미터 추출
3. Request/Response DTO 분석
4. Markdown 형식으로 API 문서 생성

## 출력 형식

### `POST /api/v1/users`
**설명**: 새 사용자 등록

**Request Body**:
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| email | string | ✅ | 이메일 주소 |
| password | string | ✅ | 비밀번호 (8자 이상) |
| name | string | ✅ | 이름 |

**Response** (201 Created):
| 필드 | 타입 | 설명 |
|------|------|------|
| id | number | 사용자 ID |
| email | string | 이메일 주소 |
| createdAt | string | 생성 일시 (ISO 8601) |

**에러 응답**:
- `400` — 입력값 검증 실패
- `409` — 이미 존재하는 이메일
```

#### TDD Workflow Skill

```yaml
---
name: tdd-workflow
description: >
  테스트 주도 개발(TDD) 워크플로우.
  "TDD로 개발", "테스트 먼저 작성" 요청 시 사용.
---
```

```markdown
# TDD Workflow

## 프로세스 (Red → Green → Refactor)

### 1단계: Red (실패하는 테스트 작성)
- 구현하려는 기능의 기대 동작을 테스트로 작성
- 테스트를 실행하여 실패하는지 확인
- 테스트가 실패하는 이유가 "기능이 없어서"인지 확인

### 2단계: Green (테스트 통과하는 최소 코드)
- 테스트를 통과하는 가장 단순한 코드 작성
- 완벽한 코드가 아니어도 됨 — 테스트만 통과하면 OK
- 이 단계에서는 설계 고민 최소화

### 3단계: Refactor (리팩토링)
- 테스트가 통과하는 상태를 유지하면서 코드 개선
- 중복 제거, 네이밍 개선, 패턴 적용
- 리팩토링 후 테스트 재실행으로 확인

### 4단계: 다음 테스트 케이스로 반복

## 테스트 작성 원칙
- AAA 패턴: Arrange → Act → Assert
- 한 테스트에 한 가지 검증
- 테스트 이름은 행동 기반 (should_returnUser_when_validIdGiven)
- 엣지 케이스 반드시 포함
```

### 3.6 Skills 설치 (오픈 소스)

```bash
# npx skills 도구로 설치
npx -y skills add -l <github-repo>  # 목록 조회
npx -y skills add --all <github-repo>  # 전체 설치
npx -y skills add <github-repo>  # 선택 설치
```

Anthropic 공식 Skills:
- `anthropics/skills` — PDF, DOCX, PPTX, XLSX 등

커뮤니티 Skills:
- `awesome-claude-code` — 커뮤니티 큐레이션 목록

---

## 4. Subagents (서브에이전트)

### 4.1 Subagents란?

Subagents는 **독립된 컨텍스트 윈도우에서 작동하는 전문 에이전트**다. 메인 에이전트가 복잡한 작업의 일부를 서브에이전트에게 위임하고, 결과만 받아온다.

Cursor 2.4에서 공식 지원이 시작되었다.

### 4.2 왜 Subagents를 사용하는가?

- **컨텍스트 절약**: 탐색/리서치 과정이 메인 대화를 오염시키지 않음
- **병렬 처리**: 여러 서브에이전트가 동시에 작업
- **전문성**: 각 에이전트에 특화된 프롬프트와 도구 권한 부여
- **속도**: 대규모 코드베이스 탐색을 병렬로 처리

### 4.3 기본 내장 Subagents

Cursor는 다음 서브에이전트를 기본 제공:
- **코드베이스 리서치**: 프로젝트 구조, 파일 탐색
- **터미널 명령 실행**: 셸 명령 격리 실행
- **병렬 워크스트림**: 독립적인 작업 분배
- **computerUse**: 브라우저/UI 자동화 (별도 설정)

### 4.4 커스텀 Subagent 생성

**저장 위치**:
```
.cursor/agents/    # 프로젝트 레벨
```

> ⚠️ 현재(2026년 1월 기준) Cursor는 프로젝트 레벨만 지원. 사용자 레벨(글로벌) 서브에이전트는 아직 미지원.

**`.cursor/agents/architect.md`**:
```yaml
---
name: architect
description: >
  소프트웨어 아키텍처 분석 및 설계 전문가.
  아키텍처 리뷰, 대규모 리팩토링 계획, 시스템 설계 시 사용.
model: sonnet
tools:
  - Read
  - Grep
  - Glob
---
```

```markdown
# Software Architect

당신은 시니어 소프트웨어 아키텍트입니다.

## 역할
- 코드베이스의 아키텍처를 분석
- SOLID 원칙, 클린 아키텍처 관점에서 평가
- 개선 방안을 구체적인 리팩토링 계획으로 제시
- 의존성 방향, 레이어 분리, 모듈 경계 검토

## 출력 형식
1. 현재 아키텍처 요약 (다이어그램 형태)
2. 문제점 목록 (심각도 순)
3. 개선 계획 (단계별)
4. 예상 영향 범위
```

**`.cursor/agents/test-writer.md`**:
```yaml
---
name: test-writer
description: >
  단위 테스트 및 통합 테스트 작성 전문가.
  테스트 작성, 테스트 커버리지 개선, 테스트 리팩토링 시 사용.
model: sonnet
tools:
  - Read
  - Write
  - Bash
  - Grep
---
```

```markdown
# Test Writer

## 테스트 작성 원칙
- JUnit 5 + Mockito (Java) / Jest + RTL (React)
- AAA 패턴 (Arrange-Act-Assert)
- 한 테스트에 한 가지 검증
- 행동 기반 테스트 이름

## 커버리지 목표
- 비즈니스 로직: 80% 이상
- 유틸리티 함수: 90% 이상
- 컨트롤러: Happy Path + 주요 에러 케이스

## 엣지 케이스 체크리스트
- null/undefined 입력
- 빈 문자열/컬렉션
- 경계값 (min, max, 0, 음수)
- 동시성 이슈
- 타임아웃
```

**`.cursor/agents/planner.md`**:
```yaml
---
name: planner
description: >
  복잡한 기능 구현 전 상세 구현 계획을 수립.
  대규모 기능 개발, 리팩토링 계획, 마이그레이션 계획 시 사용.
model: opus
tools:
  - Read
  - Grep
  - Glob
---
```

```markdown
# Implementation Planner

## 프로세스
1. 요구사항 분석
2. 영향 범위 파악 (관련 파일/모듈 탐색)
3. 의존성 분석
4. 구현 단계 분해 (각 단계는 독립적으로 테스트 가능해야 함)
5. 리스크 식별 및 완화 전략
6. 예상 소요 시간

## 출력 형식
### 📋 구현 계획: [기능명]

#### 1단계: [제목] (예상: X분)
- 변경 파일: [목록]
- 작업 내용: [설명]
- 테스트: [검증 방법]

#### 2단계: ...

### ⚠️ 리스크
- [리스크 1]: [완화 전략]

### 🔗 의존성
- [선행 작업 목록]
```

### 4.5 Subagent 프론트매터 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `name` | string | 에이전트 고유 이름 |
| `description` | string | 역할 설명 (자동 위임 기준) |
| `model` | string | 사용할 모델 (`sonnet`, `opus` 등) |
| `tools` | list | 허용 도구 목록 |
| `hooks` | object | 에이전트 전용 Hooks |

### 4.6 Subagent 활용 패턴

#### 패턴 1: Planner → Implementer

```
사용자: "사용자 인증 시스템을 구현해줘"
└→ Planner 서브에이전트: 구현 계획 수립
  └→ 메인 에이전트: 계획에 따라 구현
    └→ Test Writer 서브에이전트: 테스트 작성
```

#### 패턴 2: 병렬 탐색

```
사용자: "다크 모드 관련 파일을 찾아줘"
└→ 서브에이전트 1: "dark mode" 검색
└→ 서브에이전트 2: "theme" 검색
└→ 서브에이전트 3: "color scheme" 검색
└→ 결과 취합 → 메인에 보고
```

#### 패턴 3: 코드 리뷰 후 구현

```
사용자: "이 PR을 리뷰하고 이슈를 수정해줘"
└→ Reviewer 서브에이전트: 코드 리뷰
  └→ 메인 에이전트: 이슈 수정
    └→ Test Writer: 수정 사항 검증 테스트
```

### 4.7 Subagent vs Task()

Cursor 에이전트는 자체적으로 `Task()` 도구를 사용해 서브에이전트를 동적으로 생성할 수 있다. 커스텀 서브에이전트의 대안:

- **커스텀 Subagent**: 사전 정의된 역할, 프롬프트, 도구
- **Task()**: 메인 에이전트가 동적으로 결정, 더 유연

**권장**: 반복적인 전문 작업 → 커스텀 Subagent, 일회성 위임 → Task()

---

## 5. Commands (슬래시 명령어)

### 5.1 Commands란?

Commands는 `/`로 시작하는 **사용자가 직접 트리거하는 워크플로우 단축키**다.

### 5.2 Command 생성

```bash
mkdir -p .cursor/commands
```

**`.cursor/commands/convert-widget.md`**:
```markdown
---
allowed-tools: Read, Write, Bash
description: React 컴포넌트를 바닐라 HTML/CSS/JS 위젯으로 변환
---

선택된 React 컴포넌트를 프로덕션 레디 바닐라 HTML/CSS/JS 위젯으로 변환하세요.

## 변환 규칙
1. React props와 state를 분석
2. BEM 네이밍 컨벤션으로 HTML 구조 생성
3. CSS는 디자인 토큰만 사용
4. @css-architecture.mdc 규칙 적용
5. @design-system.mdc 규칙 적용
```

**사용법**: 채팅에서 `/convert-widget` 입력

### 5.3 Commands vs Skills

| 특성 | Commands | Skills |
|------|----------|--------|
| 호출 | 수동 (`/명령`) | 자동 (맥락 매칭) |
| 형식 | 단일 .md 파일 | 디렉토리 + SKILL.md |
| 용도 | 명시적 워크플로우 | 동적 전문 지식 |
| 코드 실행 | 제한적 | ✅ 스크립트 포함 |

---

## 6. 통합 워크플로우 구성

### 6.1 프로젝트 전체 구조 예시

```
프로젝트루트/
├── .cursor/
│   ├── rules/
│   │   ├── project-context.mdc        # Always
│   │   ├── java-standards.mdc         # Auto (*.java)
│   │   ├── react-standards.mdc        # Auto (*.tsx)
│   │   ├── testing-guidelines.mdc     # Agent
│   │   └── security-checklist.mdc     # Agent
│   ├── skills/
│   │   ├── spring-api-generator/
│   │   │   ├── SKILL.md
│   │   │   └── templates/
│   │   ├── react-component-gen/
│   │   │   ├── SKILL.md
│   │   │   └── templates/
│   │   └── tdd-workflow/
│   │       └── SKILL.md
│   ├── agents/
│   │   ├── architect.md
│   │   ├── code-reviewer.md
│   │   ├── test-writer.md
│   │   └── planner.md
│   └── commands/
│       ├── review-pr.md
│       ├── create-api.md
│       └── generate-docs.md
├── AGENTS.md                          # 팀 공유 규칙
├── src/
└── ...
```

### 6.2 워크플로우 파이프라인

**새 기능 개발 파이프라인**:
```
1. /create-api User           ← Command 트리거
2. Planner 서브에이전트        ← 구현 계획 수립
3. spring-api-generator Skill ← 표준 코드 생성
4. java-standards Rule        ← Auto-Attach로 규칙 적용
5. Test Writer 서브에이전트    ← 테스트 자동 생성
6. Code Reviewer 서브에이전트  ← 최종 리뷰
```

### 6.3 선택 가이드

```
반복되는 코딩 규칙?          → Rules
반복되는 전문 작업?          → Skills
복잡한 분석/리서치?          → Subagents
명시적 워크플로우 단축키?    → Commands
이벤트 기반 자동 실행?       → Hooks
```

---

## 7. 팁 & 트러블슈팅

### 7.1 규칙이 적용되지 않을 때

1. `.mdc` 확장자인지 확인 (`.md`가 아님)
2. 프론트매터 YAML 문법 검증 (`---`로 시작/끝)
3. `alwaysApply: true`인데 `globs`도 있으면 globs는 무시됨
4. 파일이 `.cursor/rules/` 디렉토리에 있는지 확인
5. Cursor를 재시작하거나 새 채팅 시작

### 7.2 Subagent가 호출되지 않을 때

1. `description`이 충분히 구체적인지 확인
2. `.cursor/agents/` 디렉토리 위치 확인
3. 명시적으로 에이전트 이름을 언급해보기
4. `tools` 목록에 필요한 도구가 포함되어 있는지 확인

### 7.3 Skill이 자동 로드되지 않을 때

1. `SKILL.md`의 description이 대화 맥락과 매칭되는지 확인
2. 수동으로 Skill 이름을 언급해보기
3. Skills 디렉토리 구조 확인 (`SKILL.md`가 디렉토리 안에 있어야 함)

### 7.4 성능 최적화

- Always Rules는 최소한으로 유지 (매 요청에 컨텍스트 소모)
- 큰 Skill은 progressive disclosure (본문은 짧게, 상세는 하위 파일로)
- 서브에이전트는 `sonnet` 모델로 충분한 경우가 많음 (비용/속도 절약)
- 한 채팅에 한 작업 — 긴 대화는 컨텍스트 품질 저하

---

## 8. Claude Code와의 비교

| 기능 | Cursor | Claude Code |
|------|--------|-------------|
| Rules | `.cursor/rules/*.mdc` | `CLAUDE.md` + `settings.json` |
| Skills | `.cursor/skills/` | `.claude/skills/` |
| Subagents | `.cursor/agents/` | `.claude/agents/` |
| Commands | `.cursor/commands/` | `.claude/commands/` |
| Hooks | 설정 파일 | `settings.json` hooks |
| Plugins | 미지원 (2026.01 기준) | `/plugins` 마켓플레이스 |
| Skill 표준 | Agent Skills 오픈 스탠다드 | Agent Skills 오픈 스탠다드 |
| UI | GUI (VS Code 기반) | CLI (터미널) |

**Agent Skills 오픈 스탠다드** 덕분에, Claude Code에서 만든 Skill을 Cursor에서도 사용할 수 있고, 그 반대도 가능하다.
