# CLI 도구 완벽 사용 가이드

---

## 📚 목차

1. [fzf - 퍼지 파인더](https://claude.ai/chat/3747cfd2-57eb-4319-b262-77a6c25343f6#1-fzf---%ED%8D%BC%EC%A7%80-%ED%8C%8C%EC%9D%B8%EB%8D%94)
2. [ripgrep - 초고속 검색](https://claude.ai/chat/3747cfd2-57eb-4319-b262-77a6c25343f6#2-ripgrep---%EC%B4%88%EA%B3%A0%EC%86%8D-%EA%B2%80%EC%83%89)
3. [lazygit - Git UI](https://claude.ai/chat/3747cfd2-57eb-4319-b262-77a6c25343f6#3-lazygit---git-ui)
4. [bat - 파일 뷰어](https://claude.ai/chat/3747cfd2-57eb-4319-b262-77a6c25343f6#4-bat---%ED%8C%8C%EC%9D%BC-%EB%B7%B0%EC%96%B4)
5. [실전 조합 활용](https://claude.ai/chat/3747cfd2-57eb-4319-b262-77a6c25343f6#5-%EC%8B%A4%EC%A0%84-%EC%A1%B0%ED%95%A9-%ED%99%9C%EC%9A%A9)
6. [문제 해결](https://claude.ai/chat/3747cfd2-57eb-4319-b262-77a6c25343f6#6-%EB%AC%B8%EC%A0%9C-%ED%95%B4%EA%B2%B0)

---

## 1. fzf - 퍼지 파인더

### 🎯 핵심 기능

**모든 것을 빠르게 검색 (파일, 명령어, 히스토리)**

### 📌 기본 단축키

#### `Ctrl+T` - 파일 검색

```bash
# 사용법
$ vim [Ctrl+T]

→ 현재 폴더 하위 모든 파일 검색창 열림
→ 타이핑하면 실시간 필터링
→ 화살표 ↑↓ 로 이동
→ Enter로 선택
→ vim 뒤에 파일 경로 자동 입력
```

**실전 예시:**

```bash
# Git에 파일 추가
$ git add [Ctrl+T]
→ UserService.java 검색
→ git add src/main/java/UserService.java

# 파일 열기
$ code [Ctrl+T]
→ application.yml 검색
→ VS Code로 열기

# 파일 복사
$ cp [Ctrl+T] ./backup/
→ 파일 선택해서 backup 폴더로 복사
```

#### `Ctrl+R` - 명령어 히스토리 검색

```bash
# 사용법
$ [Ctrl+R]

→ 이전에 실행한 모든 명령어 검색
→ 타이핑하면 필터링
→ Enter로 실행
```

**실전 예시:**

```bash
$ [Ctrl+R]
→ "docker" 타이핑
→ docker-compose up -d 찾기
→ Enter (바로 실행)

$ [Ctrl+R]
→ "mvn" 타이핑
→ mvn clean install -DskipTests
→ Enter
```

#### `Alt+C` (또는 `Opt+C`) - 디렉토리 이동

```bash
# 사용법
$ cd [Alt+C]

→ 하위 디렉토리 검색
→ 선택하면 바로 이동
```

**실전 예시:**

```bash
$ [Alt+C]
→ "spring" 타이핑
→ ~/projects/spring-boot-project 선택
→ 바로 이동!
```

### 🎨 fzf 단독 사용

#### 파일 검색 후 작업

```bash
# 파일 찾아서 열기
$ vim $(fzf)

# 여러 파일 선택 (Tab으로 선택)
$ fzf -m
→ Tab으로 여러 개 선택
→ Enter로 확정
```

#### 프로세스 검색해서 종료

```bash
# 실행 중인 프로세스 검색
$ kill -9 $(ps aux | fzf | awk '{print $2}')
```

### ⚙️ 커스터마이징

```bash
# ~/.zshrc에 추가

# fzf 테마 설정
export FZF_DEFAULT_OPTS='
  --height 40%
  --layout=reverse
  --border
  --preview "bat --color=always {}"
'

# ripgrep과 조합
export FZF_DEFAULT_COMMAND='rg --files --hidden'
```

---

## 2. ripgrep - 초고속 검색

### 🎯 핵심 기능

**프로젝트 전체에서 코드 초고속 검색 (grep보다 100배 빠름)**

### 📌 기본 사용법

#### 단순 검색

```bash
# 기본 문법
$ rg "검색어"

# 예시
$ rg "UserService"
→ 현재 폴더에서 "UserService" 포함된 모든 파일 찾기
→ 파일명:줄번호:내용 표시
→ 색상으로 강조
```

#### 파일 타입 지정

```bash
# Java 파일만
$ rg "UserService" --type java
$ rg "UserService" -t java

# TypeScript 파일만
$ rg "useState" -t ts

# 여러 타입
$ rg "import" -t java -t kotlin
```

#### 대소문자 구분 없이

```bash
$ rg "userservice" -i
$ rg "USERSERVICE" -i
→ UserService, userService, USERSERVICE 모두 찾음
```

#### 정규식 사용

```bash
# @로 시작하는 어노테이션 찾기
$ rg "@\w+" -t java

# 이메일 패턴 찾기
$ rg "\w+@\w+\.\w+"

# TODO 주석 찾기
$ rg "TODO|FIXME"
```

### 🎯 실전 활용

#### Spring Boot 개발

```bash
# 모든 Controller 찾기
$ rg "@RestController|@Controller" -t java

# 특정 엔드포인트 찾기
$ rg "@GetMapping.*users" -t java

# SQL 쿼리 찾기
$ rg "SELECT.*FROM" -t java -t xml

# 에러 처리 찾기
$ rg "throw new" -t java

# 환경 변수 사용처 찾기
$ rg "application\.yml|application\.properties"
```

#### 리팩토링

```bash
# 사용하지 않는 import 찾기
$ rg "^import.*\*" -t java

# deprecated 코드 찾기
$ rg "@Deprecated" -t java

# System.out.println 찾기 (제거용)
$ rg "System\.out\.println"
```

#### 보안 감사

```bash
# 하드코딩된 비밀번호 찾기
$ rg "password.*=.*\".*\"" -i

# API 키 패턴
$ rg "['\"]?api[_-]?key['\"]?\s*[:=]" -i

# TODO 남은 것
$ rg "TODO|FIXME|XXX|HACK"
```

### 🎨 고급 옵션

```bash
# 파일 이름만 표시
$ rg "UserService" -l

# 매칭된 부분만 표시
$ rg "UserService" -o

# 컨텍스트 표시 (앞뒤 3줄)
$ rg "UserService" -C 3

# 특정 폴더 제외
$ rg "UserService" --glob '!test/**'

# 숨김 파일도 검색
$ rg "config" --hidden

# 바이너리 파일도 검색
$ rg "secret" --binary
```

### 💡 팁: fzf와 조합

```bash
# ripgrep 결과를 fzf로 필터링
$ rg "import" -t java | fzf

# 검색 후 파일 열기
$ vim $(rg "UserService" -l | fzf)
```

---

## 3. lazygit - Git UI

### 🎯 핵심 기능

**Git 작업을 TUI(Text UI)에서 쉽고 빠르게**

### 📌 시작하기

```bash
# Git 저장소 폴더에서
$ lazygit

# 종료
q (quit)
```

### 🎮 핵심 단축키

#### 기본 네비게이션

```
탭 이동:
1, 2, 3, 4, 5 - 패널 전환
1: Status (변경사항)
2: Files (파일 목록)
3: Branches (브랜치)
4: Commits (커밋 히스토리)
5: Stash (임시 저장)

화살표:
↑↓ - 항목 이동
← → - 탭 이동
Enter - 선택/확장
Esc - 뒤로/취소
```

#### Status 패널 (1번)

```bash
# 파일 스테이징
Space - 파일 스테이징/언스테이징
a - 모든 파일 스테이징

# 커밋
c - 커밋 (메시지 입력창)
    → 메시지 작성
    → Enter로 커밋

# 변경사항 확인
Enter - 변경사항 상세 보기

# 변경사항 되돌리기
d - 변경사항 버리기 (discard)
```

#### 커밋 (Commit)

```bash
# 기본 커밋
c - 커밋 메시지 입력
→ 메시지 작성
→ Enter

# 수정 커밋
A - 이전 커밋에 추가 (amend)

# 커밋 메시지 수정
r - 커밋 메시지만 수정 (reword)
```

#### Commits 패널 (4번)

```bash
# 커밋 히스토리
↑↓ - 커밋 이동
Enter - 커밋 상세 보기

# 커밋 되돌리기
g - Reset 메뉴
  → soft: 변경사항 유지
  → mixed: 스테이징 해제
  → hard: 완전 삭제 ⚠️

# 체리픽
c - 현재 커밋 체리픽

# Rebase
e - 커밋 편집 (edit)
d - 커밋 삭제 (drop)
s - 커밋 합치기 (squash)
```

#### Branches 패널 (3번)

```bash
# 브랜치 전환
Enter - 브랜치 체크아웃

# 브랜치 생성
n - 새 브랜치 생성
  → 이름 입력
  → Enter

# 브랜치 병합
M - 현재 브랜치로 병합 (Merge)
r - 리베이스 (Rebase)

# 브랜치 삭제
d - 브랜치 삭제
D - 강제 삭제
```

#### Push/Pull

```bash
P - Push (대문자)
p - Pull (소문자)
f - Fetch

# Push 옵션
P 
→ Push to origin
→ Force push (주의!)
```

#### Stash (임시 저장)

```bash
# Files 패널(2번)에서
s - 현재 변경사항 stash

# Stash 패널(5번)에서
Space - Stash 적용
g - Stash 삭제
```

### 🎯 실전 워크플로우

#### 일반적인 커밋 플로우

```
1. lazygit 실행
2. 패널 1 (Status)
3. Space로 파일 스테이징
4. c로 커밋
5. 메시지 입력 → Enter
6. P로 Push
```

#### 브랜치 작업

```
1. 패널 3 (Branches)
2. n으로 새 브랜치 생성
3. 작업 후 커밋
4. 원래 브랜치로 전환
5. M으로 병합
```

#### 커밋 수정

```
# 마지막 커밋에 파일 추가
1. 파일 수정
2. Space로 스테이징
3. A (amend)

# 커밋 메시지만 수정
1. 패널 4 (Commits)
2. r (reword)
3. 메시지 수정
```

#### 실수 복구

```
# 변경사항 되돌리기
1. 패널 2 (Files)
2. d (discard)

# 커밋 되돌리기
1. 패널 4 (Commits)
2. g (reset)
3. soft/mixed/hard 선택
```

### 💡 꿀팁

```bash
# 설정 보기
? - 도움말
x - 명령어 메뉴

# 커스텀 명령어
: - 명령어 입력 모드

# 로그 보기
패널 4 → Enter → 상세 변경사항

# Diff 보기
패널 2 → Enter → 파일별 변경사항
```

### ⚙️ 설정 (~/.config/lazygit/config.yml)

```yaml
gui:
  theme:
    activeBorderColor:
      - green
      - bold
    inactiveBorderColor:
      - white
  
git:
  paging:
    colorArg: always
    pager: delta --dark --paging=never
```

---

## 4. bat - 파일 뷰어

### 🎯 핵심 기능

**cat의 업그레이드 버전 (문법 하이라이팅 + 줄번호)**

### 📌 기본 사용법

#### 파일 보기

```bash
# 기본
$ bat filename.java

# 여러 파일
$ bat file1.java file2.java

# 표준 입력
$ echo "hello" | bat
```

#### 언어 지정

```bash
# 언어 자동 감지 안 될 때
$ bat --language java MyFile.txt

# 사용 가능한 언어 목록
$ bat --list-languages
```

#### 줄번호 범위

```bash
# 10번째 줄부터 20번째 줄까지
$ bat --line-range 10:20 file.java

# 10번째 줄부터 끝까지
$ bat --line-range 10: file.java

# 처음부터 10번째 줄까지
$ bat --line-range :10 file.java
```

### 🎯 실전 활용

#### 코드 리뷰

```bash
# 변경된 파일 확인
$ git diff --name-only | xargs bat

# 특정 커밋의 파일
$ git show commit-hash:path/to/file.java | bat -l java
```

#### 로그 파일 보기

```bash
# 색상 있는 로그
$ bat /var/log/application.log

# 실시간 로그 (tail + bat)
$ tail -f application.log | bat --paging=never -l log
```

#### 설정 파일 확인

```bash
# application.yml
$ bat application.yml

# Dockerfile
$ bat Dockerfile

# .gitignore
$ bat .gitignore
```

### 🎨 스타일 옵션

```bash
# 줄번호만 (Git 변경사항 숨김)
$ bat --style=numbers file.java

# 순수 텍스트 (헤더 없이)
$ bat --style=plain file.java

# 그리드 + 줄번호
$ bat --style=grid,numbers file.java

# 모든 스타일
$ bat --style=full file.java
```

### 💡 팁: 다른 도구와 조합

#### fzf와 조합

```bash
# 파일 선택해서 보기
$ fzf --preview 'bat --color=always {}'

# 검색 후 미리보기
$ rg "UserService" -l | fzf --preview 'bat --color=always {}'
```

#### Git과 조합

```bash
# staged 파일 보기
$ git diff --staged --name-only | xargs bat

# 특정 브랜치의 파일
$ git show branch-name:file.java | bat -l java
```

### ⚙️ 설정 파일 (~/.config/bat/config)

```bash
# 기본 테마 설정
--theme="Monokai Extended"

# 기본 스타일
--style="numbers,changes,header"

# 줄 감싸기 안 함
--wrap=never

# 탭 크기
--tabs=2
```

#### 테마 변경

```bash
# 사용 가능한 테마 보기
$ bat --list-themes

# 테마 미리보기
$ bat --theme="Dracula" file.java
```

---

## 5. 실전 조합 활용

### 🎯 Spring Boot 개발 시나리오

#### 1. 컨트롤러 찾아서 수정

```bash
# 1. UserController 찾기
$ rg "@RestController" -l | fzf
→ UserController.java 선택

# 2. 파일 열기
$ vim $(rg "@RestController" -l | fzf)

# 또는 한 줄로
$ vim $(rg "UserController" -l | fzf --preview 'bat --color=always {}')
```

#### 2. Git 작업 플로우

```bash
# 1. 코드 수정 후
$ rg "TODO" -t java
→ TODO 확인

# 2. 변경사항 확인
$ lazygit
→ Space로 스테이징
→ c로 커밋
→ P로 Push
```

#### 3. 에러 디버깅

```bash
# 1. 에러 메시지로 검색
$ rg "NullPointerException" -C 3

# 2. 해당 파일 확인
$ bat $(rg "NullPointerException" -l | fzf)

# 3. Git 히스토리 확인
$ lazygit
→ 패널 4에서 커밋 히스토리
```

#### 4. 리팩토링

```bash
# 1. 사용처 모두 찾기
$ rg "oldMethodName" -l

# 2. 각 파일 확인하며 수정
$ rg "oldMethodName" -l | while read file; do
    bat "$file"
    vim "$file"
done

# 3. 변경사항 커밋
$ lazygit
```

### 🎯 MyBatis 쿼리 작업

```bash
# 1. 특정 쿼리 찾기
$ rg "SELECT.*FROM users" -t xml

# 2. Mapper 파일 열기
$ vim $(rg "UserMapper" -l | fzf)

# 3. 쿼리 확인
$ bat $(find . -name "*Mapper.xml" | fzf)
```

### 🎯 환경 설정 관리

```bash
# 1. 설정 파일 찾기
$ fd "application" | fzf --preview 'bat {}'

# 2. 환경별 설정 비교
$ bat application-dev.yml application-prod.yml

# 3. 특정 설정 값 찾기
$ rg "spring.datasource" -t yml
```

### 🎯 의존성 관리

```bash
# 1. pom.xml 확인
$ bat pom.xml

# 2. 특정 라이브러리 사용처
$ rg "spring-boot-starter-" -t xml

# 3. 버전 확인
$ rg "<version>" pom.xml | bat
```

### 💡 나만의 별칭 (Aliases)

`~/.zshrc`에 추가:

```bash
# Git 관련
alias lg="lazygit"
alias gf="git diff --name-only | fzf --preview 'bat --color=always {}'"

# 검색 관련
alias f="fzf --preview 'bat --color=always {}'"
alias search="rg -i"

# 파일 보기
alias cat="bat"
alias c="bat"

# 조합
alias vf="vim \$(fzf --preview 'bat --color=always {}')"
alias cf="code \$(fzf --preview 'bat --color=always {}')"

# 프로젝트 이동
alias cdf="cd \$(fd -t d | fzf)"

# Java 개발
alias findjava="fd -e java | fzf --preview 'bat --color=always {}'"
alias findxml="fd -e xml | fzf --preview 'bat --color=always {}'"
```

저장 후:

```bash
$ source ~/.zshrc
```

### 🎯 복잡한 워크플로우 예시

#### 기능 개발 전체 플로우

```bash
# 1. 브랜치 생성
$ lazygit
→ n으로 feature/user-api 생성

# 2. 관련 파일 찾기
$ rg "User" -t java -l | fzf
→ 기존 User 관련 코드 확인

# 3. 파일 생성/수정
$ vim src/main/java/UserController.java

# 4. 테스트 코드 확인
$ rg "@Test" -t java | fzf
→ 테스트 패턴 참고

# 5. 변경사항 확인
$ bat $(git diff --name-only)

# 6. 커밋
$ lazygit
→ 스테이징 → 커밋 → Push

# 7. PR 전 최종 확인
$ rg "TODO|FIXME" -t java
→ 남은 TODO 확인
```

---

## 6. 문제 해결

### fzf

#### Q: `Ctrl+T`가 안 먹혀요

```bash
# fzf 키바인딩 재설치
$ $(brew --prefix)/opt/fzf/install
→ 모두 'y' 선택

# 터미널 재시작
$ source ~/.zshrc
```

#### Q: 미리보기가 안 보여요

```bash
# bat 설치 확인
$ bat --version

# fzf 옵션 추가 (~/.zshrc)
export FZF_DEFAULT_OPTS='--preview "bat --color=always {}"'
```

### ripgrep

#### Q: 특정 폴더가 검색 안 돼요

```bash
# 숨김 파일/폴더 포함
$ rg "검색어" --hidden

# .gitignore 무시
$ rg "검색어" --no-ignore

# 특정 폴더 명시
$ rg "검색어" path/to/folder
```

#### Q: 너무 많은 결과가 나와요

```bash
# 파일 타입 제한
$ rg "검색어" -t java

# 파일 개수만
$ rg "검색어" -c

# 파일 이름만
$ rg "검색어" -l
```

### lazygit

#### Q: lazygit이 느려요

```bash
# 큰 저장소에서 성능 향상
$ git config --global core.untrackedCache true
$ git config --global core.fsmonitor true
```

#### Q: 한글이 깨져요

```bash
# locale 확인
$ echo $LANG
→ UTF-8 포함되어 있어야 함

# ~/.zshrc에 추가
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
```

### bat

#### Q: 색상이 안 나와요

```bash
# 테마 확인
$ bat --list-themes

# 기본 테마 설정
$ echo '--theme="Monokai Extended"' >> ~/.config/bat/config

# 캐시 재생성
$ bat cache --build
```

---

## 🎓 학습 로드맵

### 1주차: 기본 익히기

```
Day 1-2: fzf
- Ctrl+T로 파일 찾기
- Ctrl+R로 명령어 찾기

Day 3-4: ripgrep
- 기본 검색 rg "검색어"
- 타입 지정 -t java

Day 5-6: lazygit
- 기본 커밋 플로우
- 브랜치 전환

Day 7: bat
- 파일 보기
- 미리보기 설정
```

### 2주차: 조합 활용

```
- fzf + bat 미리보기
- ripgrep + fzf 검색
- lazygit 고급 기능
- 별칭(alias) 만들기
```

### 3주차: 마스터

```
- 나만의 워크플로우
- 복잡한 검색 패턴
- Git 고급 작업
- 자동화 스크립트
```

---

## 📚 추가 학습 자료

### 공식 문서

- fzf: https://github.com/junegunn/fzf
- ripgrep: https://github.com/BurntSushi/ripgrep
- lazygit: https://github.com/jesseduffield/lazygit
- bat: https://github.com/sharkdp/bat

### 치트시트

```bash
# fzf 치트시트
$ tldr fzf

# ripgrep 치트시트
$ rg --help

# lazygit 치트시트
$ lazygit 실행 후 ?
```

---

## 🎯 다음 단계

### 추가 도구 고려

```bash
# 디렉토리 점프
brew install zoxide

# ls 업그레이드
brew install eza

# JSON 파싱
brew install jq

# 명령어 치트시트
brew install tldr
```

### 생산성 극대화

```
1. 자주 쓰는 명령어 alias 등록
2. fzf 미리보기 커스터마이징
3. lazygit 테마 변경
4. 나만의 워크플로우 정립
```

---

**🎉 이제 CLI 도구 마스터입니다!**

**매일 사용하면서 익숙해지세요. 1주일이면 손에 익습니다!** 🚀

---

이 가이드를 복사해서:

```bash
# 1. 파일 생성
$ nano ~/cli-guide.md

# 2. 위 내용 전체 복사/붙여넣기

# 3. Ctrl+O (저장)

# 4. Ctrl+X (종료)

# 5. 확인
$ bat ~/cli-guide.md
```

완료! ✅