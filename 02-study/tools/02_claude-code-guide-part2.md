# Claude Code 완벽 가이드 (macOS) - Part 2: 고급편

> **Part 1 이어서**: Settings, Hooks, Skills, Subagents, MCP, 워크플로우

---

## 8. Settings 시스템

### 8.1 설정 파일 계층

```
~/.claude/settings.json              # 사용자 글로벌 (모든 프로젝트)
프로젝트/.claude/settings.json       # 프로젝트 공유 (git 추적)
프로젝트/.claude/settings.local.json # 프로젝트 로컬 (git 무시)
```

**우선순위** (높은 순): Managed(조직) > 프로젝트 공유 > 프로젝트 로컬 > 사용자 글로벌

### 8.2 settings.json 구조 및 주요 설정

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "permissions": {
    "allowedTools": [
      "Read",
      "Write(src/**)",
      "Bash(git *)",
      "Bash(npm *)",
      "Bash(./gradlew *)"
    ],
    "deny": [
      "Read(.env*)",
      "Read(./secrets/**)",
      "Write(production.config.*)",
      "Bash(rm -rf *)",
      "Bash(sudo *)"
    ]
  },
  "env": {
    "NODE_ENV": "development",
    "JAVA_HOME": "/opt/homebrew/opt/openjdk@17"
  }
}
```

### 8.3 권한 규칙 패턴

```
Read                    # 모든 파일 읽기
Read(src/**)            # src 하위만 읽기
Write(src/**)           # src 하위만 쓰기
Bash(git *)             # git 명령만 허용
Bash(npm run *)         # npm run 스크립트만 허용
Bash(./gradlew *)       # gradle 래퍼만 허용
```

### 8.4 설정 관리 명령어

```bash
# 설정 확인
claude config list

# 글로벌 설정 변경
claude config set -g model claude-opus-4-5

# 대화형 설정
> /config
> /permissions
> /allowed-tools
```

---

## 9. Hooks (자동화 트리거)

Hooks는 Claude Code의 **라이프사이클 이벤트에 반응하는 셸 명령**이다. AI가 확률적으로 작업하는 반면, Hooks는 **결정적(deterministic)** 으로 매번 동일하게 실행된다.

### 9.1 Hook 이벤트 종류

| 이벤트 | 타이밍 | 용도 |
|--------|--------|------|
| `PreToolUse` | 도구 실행 전 | 코드 검증, 권한 체크, 실행 차단 |
| `PostToolUse` | 도구 실행 후 | 코드 포맷팅, 린트, 알림 |
| `Notification` | Claude 알림 시 | 데스크톱 알림, Slack 전송 |
| `Stop` | 응답 완료 시 | 정리 작업, 다음 단계 안내 |
| `SubagentStart` | 서브에이전트 시작 | 초기화 스크립트 |
| `SubagentStop` | 서브에이전트 종료 | 정리, 결과 수집 |

### 9.2 Hook 설정 예시

**`.claude/settings.json`에 직접 작성**:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write(*.py)",
        "hooks": [
          {
            "type": "command",
            "command": "black $CLAUDE_FILE_PATHS"
          },
          {
            "type": "command",
            "command": "mypy $CLAUDE_FILE_PATHS --ignore-missing-imports"
          }
        ]
      },
      {
        "matcher": "Write(*.ts)|Write(*.tsx)",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $CLAUDE_FILE_PATHS"
          },
          {
            "type": "command",
            "command": "npx tsc --noEmit --skipLibCheck $CLAUDE_FILE_PATHS"
          }
        ]
      },
      {
        "matcher": "Write(*.java)",
        "hooks": [
          {
            "type": "command",
            "command": "google-java-format --replace $CLAUDE_FILE_PATHS"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/validate-command.sh"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code 알림\" with title \"Claude\"'"
          }
        ]
      }
    ]
  }
}
```

### 9.3 Hook 입력/출력

- Hook은 **stdin**으로 JSON 데이터를 받음
- **exit code 0**: 성공 (계속 진행)
- **exit code 2**: 차단 (해당 도구 실행 중단 + 에러 메시지 피드백)

```bash
#!/bin/bash
# scripts/validate-command.sh
# stdin에서 JSON 읽기
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

# rm -rf 차단
if echo "$COMMAND" | grep -q "rm -rf"; then
  echo "❌ rm -rf 명령은 차단되었습니다" >&2
  exit 2
fi

exit 0
```

### 9.4 대화형 Hook 설정

```
> /hooks
```
메뉴에서 이벤트 타입 선택 → matcher 패턴 입력 → 실행할 명령 작성 → 저장 위치 선택 (User/Project)

---

## 10. Skills (기술 패키지)

Skills는 Claude가 **특정 도메인의 전문 지식을 온디맨드로 로드**하는 시스템이다. 시스템 프롬프트에 항상 포함하는 대신, 필요할 때만 불러와서 컨텍스트를 절약한다.

### 10.1 Skill 디렉토리 구조

```
~/.claude/skills/              # 사용자 레벨 (모든 프로젝트)
.claude/skills/                # 프로젝트 레벨
```

각 Skill은 디렉토리 형태:
```
my-skill/
├── SKILL.md          # 핵심 파일 (필수)
├── templates/        # 템플릿 파일 (선택)
├── examples/         # 예시 파일 (선택)
└── scripts/          # 실행 스크립트 (선택)
    └── generate.sh
```

### 10.2 SKILL.md 구조

```yaml
---
name: spring-boot-service
description: Spring Boot 서비스 레이어 생성 가이드. Service 클래스, DTO, 예외 처리 패턴을 포함.
---
```

```markdown
# Spring Boot Service 생성 가이드

## 서비스 클래스 패턴
- @Service 어노테이션 사용
- 생성자 주입 (final 필드 + @RequiredArgsConstructor)
- 트랜잭션 관리: @Transactional 사용
- 예외 처리: 커스텀 BusinessException 활용

## DTO 패턴
- record 클래스 사용 (Java 17+)
- Request/Response DTO 분리
- Validation: @Valid + Bean Validation

## 예시
[templates/ServiceTemplate.java 참조]
```

### 10.3 호출 방식

| 방식 | 설명 |
|------|------|
| 자동 호출 | description이 대화 맥락과 매칭되면 자동 로드 |
| 수동 호출 | `/skill-name`으로 직접 트리거 |

### 10.4 실전 Skill 예시: 코드베이스 시각화

```yaml
---
name: codebase-visualizer
description: 프로젝트 구조를 인터랙티브 HTML 트리로 시각화
---
```

```markdown
# 코드베이스 시각화

다음 스크립트를 실행하여 프로젝트 구조를 시각화합니다:

`scripts/visualize.sh`를 실행하세요.
결과물 `codebase-map.html`을 브라우저에서 엽니다.
```

### 10.5 공식 제공 Skills

Anthropic이 제공하는 내장 Skills:
- **docx**: Word 문서 생성/편집
- **xlsx**: Excel 스프레드시트 처리
- **pptx**: PowerPoint 프레젠테이션
- **pdf**: PDF 생성/편집/OCR
- **frontend-design**: 고품질 프론트엔드 UI

### 10.6 Skills 설치 (npx skills)

```bash
# 사용 가능한 Skills 목록 조회
npx -y skills add -l <github-repo>

# 전체 설치
npx -y skills add --all <github-repo>

# 선택 설치
npx -y skills add <github-repo>
```

---

## 11. Subagents (서브에이전트)

Subagents는 **독립된 컨텍스트 윈도우를 가진 전문 AI 인스턴스**다. 메인 에이전트가 특정 작업을 서브에이전트에게 위임하고, 결과만 돌려받는다.

### 11.1 내장 서브에이전트

| 에이전트 | 역할 |
|----------|------|
| `Explore` | 코드베이스 탐색, 파일 검색, 구조 분석 |
| `Task` | 범용 작업 위임 |
| `claude-code-guide` | Claude Code 사용법 안내 |

### 11.2 커스텀 서브에이전트 생성

```bash
# 프로젝트 레벨
mkdir -p .claude/agents

# 사용자 레벨 (모든 프로젝트에서 사용)
mkdir -p ~/.claude/agents
```

**`.claude/agents/code-reviewer.md`**:
```yaml
---
name: code-reviewer
description: 코드 리뷰 전문가. 코드 변경 후 자동으로 리뷰를 수행한다.
model: sonnet
tools:
  - Read
  - Grep
  - Glob
  - Bash(git diff *)
---
```

```markdown
# Code Reviewer

당신은 시니어 코드 리뷰어입니다.

## 리뷰 기준
1. **보안**: SQL 인젝션, XSS, 인증 우회 등
2. **성능**: N+1 쿼리, 불필요한 루프, 메모리 누수
3. **가독성**: 네이밍, 코드 구조, 주석
4. **테스트**: 테스트 커버리지, 엣지 케이스

## 출력 형식
각 이슈를 다음 형식으로 보고:
- **파일**: 파일 경로
- **라인**: 라인 번호
- **심각도**: 🔴 Critical / 🟡 Warning / 🟢 Info
- **설명**: 이슈 내용
- **제안**: 수정 방법
```

**`.claude/agents/db-reader.md`** (읽기 전용 DB 에이전트):
```yaml
---
name: db-reader
description: 읽기 전용 데이터베이스 쿼리 실행
tools:
  - Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

```markdown
# Database Reader

읽기 전용 SQL 쿼리만 실행하세요.
INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE 문은 절대 사용하지 마세요.
```

### 11.3 서브에이전트 호출

```
> code-reviewer 에이전트로 최근 변경사항을 리뷰해줘
> @code-reviewer 이 PR을 리뷰해줘
```

또는 Claude가 description을 기반으로 **자동 위임**한다.

### 11.4 /agents 명령어로 대화형 생성

```
> /agents
# → Create new agent 선택
# → User-level 또는 Project-level 선택
# → Generate with Claude 또는 직접 작성
```

### 11.5 비동기 에이전트

```bash
# 백그라운드 작업 실행
& 인증 모듈을 리팩토링해줘
& 플레이키 테스트를 수정해줘
& API 문서를 업데이트해줘

# 백그라운드 작업 확인
> /tasks
# → 't'를 눌러 텔레포트 (진행 중인 작업으로 이동)
```

### 11.6 Subagent 활용 전략

**권장 패턴**:
- 탐색/리서치 → Explore 서브에이전트
- 코드 리뷰 → 전문 리뷰어 서브에이전트
- 테스트 작성 → 테스트 전문 서브에이전트
- 대규모 리팩토링 → 병렬 서브에이전트

**주의사항**:
- 서브에이전트는 메인 컨텍스트에서 격리됨 → 결과만 반환
- 너무 많은 커스텀 서브에이전트 → 오히려 유연성 저하
- 대안: Claude가 자체적으로 `Task()`를 사용해 동적으로 위임하게 하기

---

## 12. MCP (Model Context Protocol)

MCP는 Claude Code를 외부 도구/서비스와 연결하는 **플러그인 프로토콜**이다.

### 12.1 MCP 서버 추가

```bash
# GitHub 통합
claude mcp add github -- npx -y @modelcontextprotocol/server-github

# 파일시스템 확장
claude mcp add filesystem -- npx @modelcontextprotocol/server-filesystem ~/projects

# Puppeteer (브라우저 자동화)
claude mcp add puppeteer -- npx -y @anthropic/mcp-puppeteer

# PostgreSQL
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres postgresql://localhost:5432/mydb

# 확인
claude mcp list
```

### 12.2 MCP 설정 파일

**프로젝트 공유** (`.mcp.json`):
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "sentry": {
      "command": "npx",
      "args": ["-y", "@sentry/mcp-server"],
      "env": {
        "SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}"
      }
    }
  }
}
```

### 12.3 MCP 디버깅

```bash
claude --mcp-debug
```

### 12.4 MCP 컨텍스트 관리

```
> /context   # MCP가 사용 중인 컨텍스트 확인
```

MCP 서버가 많으면 컨텍스트가 빠르게 소모된다. 사용하지 않는 서버는 제거하자.

---

## 13. Plugins (플러그인)

Plugins는 Skills, Commands, Hooks, Subagents를 **하나의 패키지로 묶어 배포**하는 시스템이다. 2025년 12월 공식 마켓플레이스가 런칭되었다.

```bash
# 플러그인 설치
> /plugins install typescript-lsp

# 설치된 플러그인 목록
> /plugins list

# 업데이트
> /plugins update
```

---

## 14. 요금제 및 제한

### 14.1 구독 플랜별 사용량 (2025년 8월 이후 주간 제한)

| 플랜 | Sonnet (시간/주) | Opus (시간/주) | 월 세션 | 가격 |
|------|------------------|----------------|---------|------|
| Pro | 40~80 | — | 50x5hr | $20/월 |
| Max ($100) | 140~280 | 15~35 | 50x5hr | $100/월 |
| Max ($200) | 240~480 | 24~40 | 50x5hr | $200/월 |

### 14.2 API 사용

Pay-as-you-go 방식. 토큰 사용량에 따라 과금. 제한 없이 사용 가능하나 비용 관리 필요.

---

## 15. 실전 워크플로우 예시

### 15.1 TDD (테스트 주도 개발)

```
> 사용자 인증 기능을 TDD로 개발해줘
  1. 먼저 실패하는 테스트를 작성
  2. 테스트를 통과하는 최소한의 코드 작성
  3. 리팩토링
  4. 다음 테스트 케이스로 반복
```

### 15.2 PR 리뷰 자동화

```bash
# .claude/commands/review-pr.md
gh pr diff $ARGUMENTS | cat

위 PR diff를 리뷰하세요:
- 버그 및 보안 취약점 집중
- 성능 이슈
- 코딩 컨벤션 위반
간결하게 핵심만 보고하세요.
```

### 15.3 코드베이스 온보딩

```
> 이 프로젝트의 전체 아키텍처를 설명해줘
> 인증 시스템이 어떻게 동작하는지 상세하게 설명해줘
> 새로운 API 엔드포인트를 추가하려면 어떤 파일들을 수정해야 해?
```

### 15.4 멀티 레포 작업

```bash
claude --add-dir ../backend --add-dir ../shared-lib
> backend의 UserService와 shared-lib의 타입 정의를 함께 수정해줘
```

### 15.5 Cloud Code (웹 기반)

Claude.ai에서 `</>` 아이콘을 클릭하면 **Cloud Code** 사용 가능:
- GitHub 연동 필요
- 비동기 자율 코딩 (커피 마시고 와도 됨)
- 버그 수정, 문서화, 소규모 수정에 적합
- `claude --resume` 으로 로컬에서 이어서 작업 가능 (cloud → local)

---

## 16. 핵심 팁 정리

1. **CLAUDE.md를 잘 관리하라** — 프로젝트 지식의 핵심
2. **서브에이전트를 활용하라** — 탐색과 작업을 분리해서 컨텍스트 절약
3. **Hooks로 품질을 자동화하라** — 포맷터, 린터, 타입체크
4. **한 채팅에 한 작업** — 긴 대화일수록 성능 저하
5. **`/compact`를 적극 사용** — 컨텍스트 압축으로 대화 연장
6. **`claude -c`로 세션 이어가기** — 컨텍스트 재구축 시간 절약
7. **비대화형 모드(`-p`)로 자동화** — CI/CD, 스크립팅에 활용
8. **이미지를 적극 활용** — 디자인 목업, 에러 스크린샷
9. **Plan 모드** — 복잡한 작업은 계획 먼저 (`Shift+Tab`으로 전환)
10. **커스텀 명령어를 Git에 커밋** — 팀 전체가 동일한 워크플로우 공유
