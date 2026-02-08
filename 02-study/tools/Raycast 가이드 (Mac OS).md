
## 목차

- [소개](https://claude.ai/chat/bb777c03-4329-4e96-a032-d4cff9e9220b#%EC%86%8C%EA%B0%9C)
- [설치](https://claude.ai/chat/bb777c03-4329-4e96-a032-d4cff9e9220b#%EC%84%A4%EC%B9%98)
- [기본 사용법](https://claude.ai/chat/bb777c03-4329-4e96-a032-d4cff9e9220b#%EA%B8%B0%EB%B3%B8-%EC%82%AC%EC%9A%A9%EB%B2%95)
- [핵심 기능](https://claude.ai/chat/bb777c03-4329-4e96-a032-d4cff9e9220b#%ED%95%B5%EC%8B%AC-%EA%B8%B0%EB%8A%A5)
- [개발자를 위한 기능](https://claude.ai/chat/bb777c03-4329-4e96-a032-d4cff9e9220b#%EA%B0%9C%EB%B0%9C%EC%9E%90%EB%A5%BC-%EC%9C%84%ED%95%9C-%EA%B8%B0%EB%8A%A5)
- [추천 Extension](https://claude.ai/chat/bb777c03-4329-4e96-a032-d4cff9e9220b#%EC%B6%94%EC%B2%9C-extension)
- [단축키 모음](https://claude.ai/chat/bb777c03-4329-4e96-a032-d4cff9e9220b#%EB%8B%A8%EC%B6%95%ED%82%A4-%EB%AA%A8%EC%9D%8C)
- [팁과 트릭](https://claude.ai/chat/bb777c03-4329-4e96-a032-d4cff9e9220b#%ED%8C%81%EA%B3%BC-%ED%8A%B8%EB%A6%AD)

---

## 소개

Raycast는 Mac용 생산성 런처로, Spotlight를 대체하여 더욱 강력한 기능을 제공합니다.

### 주요 특징

- **빠른 앱 실행**: 앱, 파일, 문서를 즉시 검색하고 실행
- **스크립트 실행**: 터미널 명령어를 GUI에서 실행
- **Extension**: 다양한 서드파티 확장 기능
- **클립보드 관리**: 복사 히스토리 관리
- **윈도우 관리**: 창 정렬 및 관리
- **AI 통합**: ChatGPT, Claude 등 AI 어시스턴트 통합

---

## 설치

### 1. 다운로드 및 설치

```bash
# Homebrew를 통한 설치 (권장)
brew install --cask raycast
```

또는 [공식 웹사이트](https://www.raycast.com/)에서 직접 다운로드

### 2. 초기 설정

1. Raycast 실행
2. 접근 권한 허용 (시스템 환경설정 → 개인 정보 보호 및 보안)
    - 손쉬운 사용
    - 화면 기록
3. 기본 단축키 설정: `⌘ + Space` (또는 원하는 키 조합)

### 3. Spotlight 대체 (선택사항)

- 시스템 환경설정 → Spotlight → 단축키 변경 또는 해제
- Raycast를 `⌘ + Space`로 설정

---

## 기본 사용법

### 검색 및 실행

```
⌘ + Space          # Raycast 열기
앱 이름 입력        # 앱 검색 및 실행
파일 이름 입력      # 파일 검색
Enter             # 선택한 항목 실행
⌘ + Enter         # 새 창에서 열기
```

### 계산기

```
25 * 4            # 수식 입력하면 즉시 계산
=10+5*2           # = 로 시작하면 계산기 모드
```

### 빠른 명령어

```
> 명령어           # 명령어 직접 입력
shutdown          # 시스템 종료
restart           # 재시작
sleep             # 절전 모드
```

---

## 핵심 기능

### 1. **Clipboard History** (클립보드 히스토리)

- 복사한 모든 내용의 히스토리 관리
- 단축키: `⌘ + Shift + V`
- 텍스트, 이미지, 파일 모두 저장
- 검색 가능

**사용 예시:**

```
1. 여러 텍스트를 차례로 복사
2. ⌘ + Shift + V 로 히스토리 열기
3. 원하는 항목 검색 후 붙여넣기
```

### 2. **Window Management** (윈도우 관리)

창 정렬 단축키:

```
⌥ + ⌘ + ←        # 왼쪽 절반
⌥ + ⌘ + →        # 오른쪽 절반
⌥ + ⌘ + ↑        # 위쪽 절반
⌥ + ⌘ + ↓        # 아래쪽 절반
⌥ + ⌘ + F        # 전체 화면
⌥ + ⌘ + C        # 중앙 정렬
```

### 3. **Snippets** (스니펫)

자주 사용하는 텍스트를 단축어로 저장

**설정 방법:**

1. Raycast → Extensions → Snippets
2. Create Snippet
3. 단축어와 내용 입력

**예시:**

```
@@email     → your.email@example.com
@@sign      → Best regards, Your Name
@@addr      → 서울특별시 강남구...
```

### 4. **Quicklinks** (퀵링크)

자주 방문하는 웹사이트를 빠르게 열기

**설정 방법:**

1. Raycast → Extensions → Quicklinks
2. Create Quicklink
3. 이름과 URL 입력

**예시:**

```
gh          → https://github.com/yourusername
notion      → https://notion.so/yourworkspace
gmail       → https://mail.google.com
```

---

## 개발자를 위한 기능

### 1. **Script Commands**

터미널 스크립트를 GUI에서 실행

**스크립트 폴더 위치:**

```bash
~/Library/Application Support/com.raycast.macos/script-commands
```

**예시 스크립트:** `git-status.sh`

```bash
#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Git Status
# @raycast.mode fullOutput

# Optional parameters:
# @raycast.icon 🔧
# @raycast.packageName Git

cd ~/Projects/my-project
git status
```

### 2. **Developer 유틸리티**

#### JSON Pretty Print

```
1. JSON 텍스트 복사
2. Raycast에서 "JSON Pretty Print" 검색
3. 포맷팅된 JSON 확인
```

#### Base64 인코딩/디코딩

```
Raycast → Encode/Decode → Base64
```

#### UUID 생성

```
Raycast → Generate UUID
```

#### Color Picker

```
⌥ + ⌘ + C      # 화면의 색상 추출
```

### 3. **Git Integration**

```
git clone     # Repository 클론
git pull      # Pull 실행
git status    # 상태 확인
```

---

## 추천 Extension

### 개발 도구

- **GitHub**: PR, Issue, Repository 검색 및 관리
- **Docker**: 컨테이너 관리
- **Homebrew**: 패키지 검색 및 설치
- **Stack Overflow**: 질문 검색
- **DevDocs**: 개발 문서 검색
- **Port Manager**: 포트 사용 확인 및 프로세스 종료

### 생산성

- **Notion**: 페이지 검색 및 생성
- **Google Calendar**: 일정 확인 및 생성
- **Todoist**: 할 일 관리
- **Slack**: 메시지 검색 및 전송

### 유틸리티

- **Kill Process**: 프로세스 종료
- **System Monitor**: 시스템 리소스 모니터링
- **File Search**: 강력한 파일 검색
- **Calculator**: 고급 계산기
- **Currency Converter**: 환율 변환

### AI 도구

- **AI Chat**: ChatGPT, Claude 등과 대화
- **Translate**: 텍스트 번역
- **Grammar Check**: 문법 검사

---

## 단축키 모음

### 기본 단축키

```
⌘ + Space          # Raycast 열기
Esc                # 닫기
⌘ + K              # 액션 메뉴 열기
⌘ + ,              # 설정 열기
⌘ + Backspace      # 입력 지우기
Tab                # 자동완성
↑ ↓                # 항목 이동
```

### 클립보드

```
⌘ + Shift + V      # 클립보드 히스토리
⌘ + P              # 클립보드에서 붙여넣기
```

### 윈도우 관리

```
⌥ + ⌘ + ←/→/↑/↓    # 창 정렬
⌥ + ⌘ + F          # 전체 화면
⌥ + ⌘ + C          # 중앙 정렬
⌥ + ⌘ + M          # 모니터 이동
```

### 검색 필터

```
'                  # 파일만 검색
>                  # 명령어 검색
?                  # 도움말 검색
!                  # 스크립트 검색
```

---

## 팁과 트릭

### 1. **Fallback Commands** (폴백 명령어)

검색 결과가 없을 때 실행할 명령어 설정

- 설정 → Advanced → Fallback Commands
- 예: 검색어를 Google에서 검색

### 2. **Aliases** (별칭)

명령어에 짧은 별칭 지정

```
Calculator → calc
File Search → fs
```

### 3. **Custom Hotkeys**

자주 사용하는 Extension에 전용 단축키 설정

```
설정 → Extensions → 해당 Extension → Record Hotkey
```

### 4. **Workflow 자동화**

여러 명령어를 순차적으로 실행

**예시: 개발 환경 시작**

```bash
#!/bin/bash
# @raycast.title Start Dev Environment

code ~/Projects/my-project
open -a "Google Chrome" http://localhost:3000
npm run dev
```

### 5. **AI 명령어 활용**

- 선택한 텍스트를 AI로 전송: 텍스트 선택 → Raycast → "AI Chat"
- 문법 교정: 텍스트 선택 → "Fix Grammar"
- 번역: 텍스트 선택 → "Translate"

### 6. **QuickLinks with Parameters**

동적 파라미터가 있는 링크

```
Google Search: https://google.com/search?q={Query}
GitHub Repo: https://github.com/{username}/{repo}
```

### 7. **Custom Themes**

- 설정 → Appearance → Theme
- 다크/라이트 모드 자동 전환 가능

---

## 추가 리소스

- [공식 문서](https://manual.raycast.com/)
- [Extension Store](https://www.raycast.com/store)
- [GitHub Repository](https://github.com/raycast)
- [Community Forum](https://raycast.com/community)

---

## Pro 버전 기능

무료 버전도 강력하지만, Pro 버전에서 제공하는 추가 기능:

- **AI 무제한 사용**: ChatGPT, Claude 통합
- **Cloud Sync**: 설정 및 히스토리 동기화
- **무제한 클립보드 히스토리**: 제한 없는 저장
- **Translation**: 번역 기능
- **Custom Themes**: 더 많은 테마 옵션

---

## 문제 해결

### Raycast가 느려질 때

```bash
# 캐시 삭제
rm -rf ~/Library/Caches/com.raycast.macos

# 재시작
killall Raycast
open -a Raycast
```

### Extension이 작동하지 않을 때

1. Extension 재설치
2. Raycast 재시작
3. 접근 권한 확인

### 단축키 충돌

- 시스템 환경설정 → 키보드 → 단축키에서 충돌 확인
- Raycast 단축키 변경

---

## 마무리

Raycast는 Mac 생산성을 크게 향상시킬 수 있는 도구입니다. 처음에는 기본 기능(앱 실행, 파일 검색)부터 시작하고, 점차 클립보드 히스토리, 윈도우 관리, Extension을 활용하면서 자신만의 워크플로우를 구축해보세요.

**추천 학습 순서:**

1. 기본 검색 및 실행 (1주)
2. 클립보드 히스토리 (1주)
3. 윈도우 관리 (1주)
4. Snippets & Quicklinks (1주)
5. Extension 설치 및 활용 (지속적)
6. Script Commands 작성 (고급)