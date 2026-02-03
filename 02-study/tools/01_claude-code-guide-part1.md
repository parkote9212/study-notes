# Claude Code 완벽 가이드 (macOS) - Part 1: 기본편

> **작성일**: 2026-02-03  
> **대상**: macOS 사용자 / Claude Code 입문~중급  
> **버전**: Claude Code 2.x 기준 (2026년 1월 최신)

---

## 1. Claude Code란?

Claude Code는 Anthropic이 개발한 **터미널 기반 에이전틱 코딩 도구**다. 터미널에서 자연어로 대화하면서 코드를 작성, 수정, 디버깅, 리팩토링할 수 있다. 단순한 코드 생성기가 아니라, 코드베이스를 이해하고 파일을 읽고 쓰며, Git 워크플로우까지 처리하는 **자율 에이전트**다.

### 주요 특징
- 터미널에서 직접 실행 — IDE 불필요 (VS Code/Cursor 확장도 지원)
- 코드베이스 전체를 이해하고 컨텍스트 유지
- 파일 읽기/쓰기, 셸 명령 실행, Git 작업 자동화
- MCP(Model Context Protocol)로 외부 도구 연결
- Skills, Subagents, Hooks로 워크플로우 자동화
- Claude Pro/Max 구독 또는 API 키로 사용

---

## 2. 설치 및 초기 설정

### 2.1 사전 요구사항

```bash
# Node.js 18+ 확인
node --version

# npm 확인
npm --version
```

### 2.2 설치

```bash
# 권장 설치 방법 (Homebrew)
brew install claude-code

# 또는 npx로 직접 실행
npx claude-code
```

> ⚠️ npm 글로벌 설치(`npm install -g`)는 **deprecated** 상태. Homebrew 또는 npx 권장.

### 2.3 인증 설정

**방법 1: Claude Pro/Max 구독 (브라우저 인증)**
```bash
claude
# 첫 실행 시 브라우저가 열리며 로그인 → 자동 인증
```

**방법 2: API 키 사용**
```bash
# 환경변수 설정 (zsh 기준)
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
source ~/.zshrc

# 또는 실행 시 직접 지정
ANTHROPIC_API_KEY="sk-ant-..." claude
```

### 2.4 첫 실행

```bash
# 프로젝트 디렉토리로 이동
cd ~/projects/my-app

# Claude Code 실행
claude

# 초기 설정 (CLAUDE.md 자동 생성)
> /init
```

---

## 3. 기본 사용법

### 3.1 인터랙티브 모드

```bash
# 기본 실행
claude

# 특정 모델 지정
claude --model sonnet    # Sonnet 4.5 (일반 작업)
claude --model opus      # Opus 4.5 (복잡한 작업)
```

### 3.2 자연어로 코딩

```
> 이 프로젝트의 폴더 구조를 설명해줘
> src/auth/login.ts에 JWT 토큰 검증 로직을 추가해줘
> 이 에러를 디버깅해줘: "TypeError: Cannot read property 'id' of undefined"
> 이 컴포넌트에 대한 단위 테스트를 작성해줘
```

### 3.3 파일 참조 (@)

```
> @src/utils/validation.ts 이 파일의 함수들을 리팩토링해줘
> @./src/ 이 디렉토리의 코드 구조를 분석해줘
> @package.json 의존성 패키지 중 보안 취약점이 있는지 확인해줘
```

### 3.4 셸 명령 직접 실행 (!)

```
> !git status
> !npm run test
> !ls -la src/
```

### 3.5 이미지 활용

- **스크린샷**: `Cmd + Ctrl + Shift + 4` → 클립보드 캡처 → `Ctrl + V` 붙여넣기
- **파일 드래그**: `Shift` 키를 누른 채 이미지 파일을 터미널에 드래그

---

## 4. 슬래시 명령어 (Slash Commands)

### 4.1 기본 슬래시 명령어

| 명령어 | 설명 |
|--------|------|
| `/init` | CLAUDE.md 초기 생성 |
| `/help` | 사용 가능한 모든 명령어 표시 |
| `/status` | 현재 모델, 설정, 상태 확인 |
| `/config` | 설정 변경 |
| `/context` | 현재 컨텍스트 사용량 확인 |
| `/permissions` | 권한 설정 관리 |
| `/allowed-tools` | 도구 권한 설정 |
| `/hooks` | 훅 설정 (인터랙티브) |
| `/agents` | 서브에이전트 관리 |
| `/terminal-setup` | 터미널 설정 최적화 |
| `/bug` | Anthropic에 버그 리포트 |
| `/compact` | 컨텍스트 압축 |
| `/clear` | 컨텍스트 초기화 |
| `/add-dir` | 추가 디렉토리 참조 |
| `/tasks` | 백그라운드 작업 확인 |
| `/fork` | 현재 세션 포크 |

### 4.2 커스텀 슬래시 명령어

**프로젝트 레벨** (팀 공유)
```bash
mkdir -p .claude/commands
```

```markdown
<!-- .claude/commands/fix-issue.md -->
$ARGUMENTS 이슈를 분석하고 수정하세요.

1. `gh issue view`로 이슈 상세 확인
2. 관련 코드 검색
3. 수정 사항 구현
4. 테스트 작성 및 실행
5. lint/type-check 통과 확인
6. 커밋 메시지 작성
```

**사용자 레벨** (개인 전용)
```bash
mkdir -p ~/.claude/commands
```

```markdown
<!-- ~/.claude/commands/review-security.md -->
현재 코드의 보안 취약점을 검토하세요:
- SQL Injection
- XSS
- CSRF
- 인증/인가 문제
- 민감 정보 노출
```

**사용법**:
```
> /project:fix-issue 1234
> /user:review-security
```

**매개변수 활용**:
- `$ARGUMENTS`: 명령어 뒤에 입력한 모든 텍스트
- `!`\`git status\``: 명령어 내 동적 컨텍스트 주입

### 4.3 고급 커스텀 명령어 (프론트매터 활용)

```markdown
<!-- .claude/commands/commit.md -->
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: 컨텍스트 기반 깃 커밋 생성
---

## Context
- 현재 상태: !`git status`
- 현재 diff: !`git diff HEAD`
- 현재 브랜치: !`git branch --show-current`

위 변경사항을 분석하여 의미있는 커밋 메시지를 작성하세요.
Conventional Commits 형식을 따르세요.
```

---

## 5. CLI 플래그 및 옵션

### 5.1 핵심 플래그

```bash
# 세션 관리
claude -c                    # 마지막 세션 이어서 작업
claude --resume              # 특정 세션 복원
claude --resume <session-id> # 세션 ID로 복원

# 모델 선택
claude --model sonnet        # Sonnet 4.5
claude --model opus          # Opus 4.5

# 추가 디렉토리
claude --add-dir ../frontend --add-dir ../shared

# 비대화형 모드 (파이프라인/스크립팅)
claude -p "이 코드를 리뷰해줘"
echo "버그 설명" | claude -p "이 버그를 수정해줘"

# 출력 형식
claude -p "보안 리뷰" --output-format json

# 최대 턴 수 제한
claude -p "테스트 실행" --max-turns 5

# 시스템 프롬프트 추가
claude --append-system-prompt "항상 한국어로 응답하세요"
claude --append-system-prompt-file ./my-prompt.md
```

### 5.2 권한 관리 플래그

```bash
# 허용 도구 제한
claude --allowedTools Read,Write,Bash

# 위험 모드 (모든 권한 자동 승인 — 신뢰할 수 있는 환경에서만)
claude --dangerously-skip-permissions
```

### 5.3 파이프라인 활용 예시

```bash
# Git 로그로 릴리스 노트 생성
git log --oneline -n 20 | claude -p "이 커밋들로 릴리스 노트를 작성해줘"

# 테스트 실패 분석
npm test 2>&1 | claude -p "실패한 테스트를 분석하고 수정 방법을 제안해줘"

# PR 리뷰 자동화
gh pr diff 42 | claude -p "이 PR의 코드를 리뷰해줘. 버그와 보안 이슈에 집중해줘"

# 보안 리포트 생성 (JSON)
claude -p "보안 이슈를 분석해줘" \
  --output-format json \
  --allowedTools Read,Grep,Glob \
  --max-turns 3 > security_report.json
```

---

## 6. 키보드 단축키

| 단축키 | 설명 |
|--------|------|
| `Tab` | 파일/폴더 자동완성 |
| `Shift + Tab` | 모드 전환 (Normal → Auto-accept → Plan) |
| `Ctrl + C` | 현재 작업 중단 |
| `Ctrl + U` | 입력 라인 삭제 |
| `Ctrl + V` | 이미지 붙여넣기 (⚠️ Cmd+V 아님!) |
| `Esc` | 현재 응답 중단 |
| `/` | 슬래시 명령어 |
| `!` | 셸 명령 직접 실행 |
| `@` | 파일/디렉토리 참조 |

---

## 7. CLAUDE.md — 프로젝트 메모리

CLAUDE.md는 Claude Code의 **장기 기억** 파일이다. 매 세션 시작 시 자동으로 읽혀서 프로젝트 컨텍스트를 제공한다.

### 7.1 파일 계층 구조

```
~/.claude/CLAUDE.md              # 글로벌 (모든 프로젝트)
프로젝트루트/CLAUDE.md            # 프로젝트 레벨 (팀 공유, git 추적)
프로젝트루트/.claude/CLAUDE.md    # 로컬 프로젝트 (개인, git 무시)
하위디렉토리/CLAUDE.md            # 하위 디렉토리 (해당 경로 작업 시)
```

**우선순위**: 하위 디렉토리 > 프로젝트 > 글로벌

### 7.2 효과적인 CLAUDE.md 작성 예시

```markdown
# 프로젝트 개요
BizSync - Spring Boot + React 기반 ERP 협업 시스템

## 기술 스택
- Backend: Java 17, Spring Boot 3.2, Spring Security, JPA
- Frontend: React 18, TypeScript, Axios
- Database: MariaDB 10.11
- Build: Gradle (backend), Vite (frontend)

## 프로젝트 구조
```
src/main/java/com/bizsync/
├── config/         # 설정 클래스 (SecurityConfig, WebConfig)
├── controller/     # REST API 컨트롤러
├── service/        # 비즈니스 로직
├── repository/     # JPA 레포지토리
├── entity/         # JPA 엔티티
├── dto/            # 데이터 전송 객체
└── exception/      # 커스텀 예외
```

## 핵심 명령어
- 빌드: `./gradlew build`
- 테스트: `./gradlew test`
- 로컬 실행: `./gradlew bootRun`
- 프론트엔드: `cd frontend && npm run dev`

## 코딩 컨벤션
- Java: Google Java Style Guide 준수
- REST API: RESTful 원칙, ResponseEntity 사용
- 커밋: Conventional Commits (feat:, fix:, refactor: 등)
- 테스트: 각 Service 클래스에 대한 단위 테스트 필수

## 주의사항
- .env 파일은 절대 커밋하지 않기
- 모든 API 엔드포인트에 인증 필요 (public 제외)
- DB 마이그레이션은 Flyway 사용
```

### 7.3 CLAUDE.md 관리 팁

- `/init`으로 초기 생성 후 점진적으로 확장
- 프로젝트별 빌드/테스트 명령어는 반드시 포함
- 코딩 스타일, 네이밍 컨벤션 명시
- 에러가 자주 발생하는 패턴과 해결 방법 기록
- `claude --resume`으로 과거 세션의 교훈을 CLAUDE.md에 반영
