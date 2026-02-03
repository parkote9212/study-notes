---
tags:
  - study
created: 2026-01-23
difficulty: 중
---
# Claude Desktop MCP 설정 가이드

## MCP (Model Context Protocol)란?

Claude가 외부 도구 및 데이터 소스와 연결할 수 있게 해주는 오픈 프로토콜입니다.
- 파일 시스템, 데이터베이스, API 등에 직접 접근 가능
- 개발 생산성 극대화

## 주요 MCP 서버

### 파일 시스템
- 로컬 파일 읽기/쓰기
- 디렉토리 탐색 및 프로젝트 구조 파악
- 코드 파일 직접 수정

### 데이터베이스
- PostgreSQL, MySQL, SQLite 등 DB 직접 쿼리
- 스키마 확인 및 데이터 분석
- 마이그레이션 스크립트 생성

### 외부 서비스
- **GitHub**: 리포지토리 관리, PR 생성, 이슈 관리
- **Notion**: 페이지 생성/수정, 데이터베이스 관리
- **Slack**: 메시지 전송, 채널 관리
- **Google Drive**: 문서 접근 및 편집
- **Jira**: 이슈 트래킹
- **Linear**: 프로젝트 관리

## MCP 설정 파일 위치

```
macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
Windows: %APPDATA%\Claude\claude_desktop_config.json
```

## 설정 파일 예시

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/yourname/projects"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/dbname"
      }
    }
  }
}
```

## 실전 활용 팁

1. **보안 주의**: 민감한 디렉토리는 MCP 접근에서 제외
2. **토큰 관리**: 환경 변수로 API 토큰 분리 관리
3. **서버 재시작**: 설정 변경 후 Claude Desktop 완전히 재시작 필요

## 트러블슈팅

**MCP 서버가 연결되지 않을 때:**
1. 설정 파일 경로 확인
2. JSON 문법 오류 확인
3. Claude Desktop 완전히 종료 후 재시작
4. 필요한 npm 패키지 설치 여부 확인
