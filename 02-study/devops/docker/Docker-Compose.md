---
tags: study, Docker, Docker-Compose, DevOps
created: 2026-01-24
---

# Docker Compose

## 한 줄 요약
> Docker Compose는 여러 컨테이너를 하나의 YAML 파일로 정의하고 관리하는 도구로, 한 줄의 명령어로 전체 애플리케이션 스택을 실행 가능

## 상세 설명

Docker Compose는 선언적 설정으로 모든 서비스를 정의하고, 네트워크를 자동 생성하며, 서비스 시작 순서와 의존성을 관리합니다.

### 핵심 명령어

**기본 명령어**
- `docker compose up -d`: 컨테이너 실행 (백그라운드)
- `docker compose logs -f`: 로그 확인
- `docker compose down`: 중지 및 제거
- `docker compose stop`: 중지만 (컨테이너 유지)
- `docker compose restart`: 재시작
- `docker compose ps`: 실행 중인 컨테이너 확인

**빌드 관련**
- `docker compose up --build`: 이미지 빌드 후 실행
- `docker compose build`: 이미지만 빌드
- `docker compose build --no-cache`: 캐시 없이 빌드

**서비스 제어**
- `docker compose up backend`: 특정 서비스만 실행
- `docker compose up -d --scale backend=3`: 서비스 스케일링
- `docker compose logs -f backend`: 특정 서비스 로그만
- `docker compose exec backend bash`: 서비스 내부 접속

### docker-compose.yml 구조

**서비스 정의**
- image 또는 build로 이미지 지정
- ports로 포트 매핑
- environment로 환경변수 설정
- volumes로 볼륨 마운트
- depends_on으로 의존성 정의
- restart로 재시작 정책
- networks로 네트워크 설정

**환경변수 관리**
- .env 파일 사용
- ${VAR:-default} 문법으로 기본값 지정

**네트워크**
- 기본적으로 프로젝트별 네트워크 자동 생성
- 여러 네트워크 정의 가능

**볼륨**
- 네임드 볼륨: 데이터 영속성
- 바인드 마운트: 호스트와 동기화

**헬스체크**
- healthcheck로 서비스 준비 상태 확인
- depends_on과 함께 사용하여 시작 순서 보장

## 코드 예시

```yaml
version: '3.8'

services:
  # 프론트엔드
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
  
  # 백엔드
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - SPRING_DATASOURCE_URL=jdbc:mysql://db:3306/mydb
      - SPRING_DATASOURCE_USERNAME=root
      - SPRING_DATASOURCE_PASSWORD=password
    depends_on:
      db:
        condition: service_healthy
    restart: on-failure
  
  # 데이터베이스
  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=mydb
    volumes:
      - db-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      retries: 3
    restart: unless-stopped

volumes:
  db-data:

# 개발 환경 오버라이드 (docker-compose.dev.yml)
services:
  backend:
    volumes:
      - ./backend:/app  # 핫 리로드
    environment:
      - DEBUG=true

# 실행
# 개발: docker compose -f docker-compose.yml -f docker-compose.dev.yml up
# 프로덕션: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 주의사항 / 함정

1. **컨테이너 간 통신 문제**: localhost 대신 서비스 이름 사용
2. **시작 순서 문제**: depends_on만으로는 부족, healthcheck 필수
3. **볼륨 데이터 유지**: `docker compose down -v`는 볼륨까지 삭제
4. **.env 파일**: Git에 커밋하지 말 것

### 트러블슈팅

```yaml
# ❌ Bad - localhost 사용
services:
  backend:
    environment:
      - DB_HOST=localhost  # 안 됨!

# ✅ Good - 서비스 이름 사용
services:
  backend:
    environment:
      - DB_HOST=db  # 서비스 이름으로!

# ❌ Bad - depends_on만 사용
services:
  backend:
    depends_on:
      - db  # DB가 준비되지 않았을 수 있음

# ✅ Good - healthcheck와 함께
services:
  backend:
    depends_on:
      db:
        condition: service_healthy
  
  db:
    healthcheck:
      test: ["CMD", "mysqladmin", "ping"]
      interval: 5s
      retries: 10
```

## 관련 개념
- [[Docker-기본-명령어]]
- [[Dockerfile-작성법]]
- [[Docker-네트워크]]
- [[Docker-볼륨]]

## 면접 질문
1. Docker Compose를 사용하는 이유는?
2. depends_on의 한계는?
3. 컨테이너 간 통신 방법은?
4. 개발/프로덕션 환경 분리 방법은?

## 참고 자료
- Docker Compose 공식 문서
