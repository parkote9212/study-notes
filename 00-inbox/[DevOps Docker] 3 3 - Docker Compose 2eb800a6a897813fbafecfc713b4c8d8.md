# [DevOps Docker] 3/3 - Docker Compose

🏷️기술 카테고리: DevOps, Docker
💡핵심키워드: #설정관리, #컨테이너
💼 면접 빈출도: 최상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 18일 오전 12:01
📅 다음 복습일: 2026년 1월 25일

# 1. Abstract: 핵심 요약

> **Docker Compose**는 여러 컨테이너를 하나의 YAML 파일로 정의하고 관리하는 도구입니다. **한 줄의 명령어**로 전체 애플리케이션 스택(프론트엔드, 백엔드, DB, 캐시 등)을 실행할 수 있습니다.
> 

**핵심 원칙**:

- 선언적 설정: docker-compose.yml에 모든 서비스 정의
- 네트워크 자동 생성: 같은 Compose 파일의 컨테이너는 자동 연결
- 오케스트레이션: 서비스 시작 순서와 의존성 관리

---

# 2. docker-compose.yml 기본 구조

## 2.1 기본 템플릿

```yaml
version: '3.8'

services:
  # 서비스 1: 백엔드
  backend:
    image: myapp:latest
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=db
    depends_on:
      - db
  
  # 서비스 2: 데이터베이스
  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
    volumes:
      - db-data:/var/lib/mysql

volumes:
  db-data:
```

---

# 3. 핵심 명령어

## 3.1 기본 명령어

```bash
# 컨테이너 실행 (백그라운드)
docker compose up -d

# 로그 확인
docker compose logs -f

# 중지 및 제거
docker compose down

# 중지만 (컨테이너 유지)
docker compose stop

# 재시작
docker compose restart

# 실행 중인 컨테이너 확인
docker compose ps
```

---

## 3.2 빌드 관련

```bash
# 이미지 빌드 후 실행
docker compose up --build

# 이미지만 빌드
docker compose build

# 특정 서비스만 빌드
docker compose build backend

# 캐시 없이 빌드
docker compose build --no-cache
```

---

## 3.3 서비스 제어

```bash
# 특정 서비스만 실행
docker compose up backend

# 서비스 스케일링
docker compose up -d --scale backend=3

# 특정 서비스 로그만
docker compose logs -f backend

# 서비스 내부 접속
docker compose exec backend bash
```

---

# 4. docker-compose.yml 상세

## 4.1 서비스 정의

```yaml
services:
  backend:
    # 방법 1: 기존 이미지 사용
    image: myapp:1.0
    
    # 방법 2: Dockerfile로 빌드
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        - BUILD_VERSION=1.0
    
    # 컨테이너 이름
    container_name: backend-app
    
    # 포트 매핑
    ports:
      - "8080:8080"
      - "8443:443"
    
    # 환경변수
    environment:
      - NODE_ENV=production
      - DB_HOST=db
      - DB_PORT=3306
    
    # 볼륨 마운트
    volumes:
      - ./logs:/app/logs
      - app-data:/app/data
    
    # 의존성 (시작 순서)
    depends_on:
      db:
        condition: service_healthy
    
    # 재시작 정책
    restart: on-failure
    
    # 네트워크
    networks:
      - app-network
```

---

## 4.2 환경변수 관리

**docker-compose.yml**:

```yaml
services:
  backend:
    environment:
      - DB_HOST=${DB_HOST:-[localhost](http://localhost)}
      - DB_PORT=${DB_PORT:-3306}
    env_file:
      - .env
```

**.env 파일**:

```bash
DB_HOST=mysql
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=secret
```

---

## 4.3 네트워크

```yaml
services:
  backend:
    networks:
      - frontend-net
      - backend-net
  
  db:
    networks:
      - backend-net

networks:
  frontend-net:
    driver: bridge
  backend-net:
    driver: bridge
```

---

## 4.4 볼륨

```yaml
services:
  db:
    volumes:
      # 네임드 볼륨
      - db-data:/var/lib/mysql
      
      # 바인드 마운트
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
      
      # 익명 볼륨
      - /app/temp

volumes:
  db-data:
    driver: local
```

---

## 4.5 헬스체크

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "[http://localhost:8080/health](http://localhost:8080/health)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
  
  db:
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "[localhost](http://localhost)"]
      interval: 10s
      timeout: 5s
      retries: 5
```

---

# 5. 실전 예제

## 5.1 Full-Stack 애플리케이션

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
      test: ["CMD", "mysqladmin", "ping", "-h", "[localhost](http://localhost)"]
      interval: 10s
      retries: 3
    restart: unless-stopped

volumes:
  db-data:
```

**실행**:

```bash
docker compose up -d --build
```

---

## 5.2 개발 vs 프로덕션

**docker-compose.yml** (기본):

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8080:8080"
```

[**docker-compose.dev](http://docker-compose.dev).yml** (개발):

```yaml
services:
  backend:
    volumes:
      - ./backend:/app  # 핫 리로드
    environment:
      - DEBUG=true
```

[**docker-compose.prod](http://docker-compose.prod).yml** (프로덕션):

```yaml
services:
  backend:
    restart: always
    environment:
      - DEBUG=false
```

**사용**:

```bash
# 개발
docker compose -f docker-compose.yml -f [docker-compose.dev](http://docker-compose.dev).yml up

# 프로덕션
docker compose -f docker-compose.yml -f [docker-compose.prod](http://docker-compose.prod).yml up -d
```

---

# 6. 트러블슈팅

## 6.1 컨테이너 간 통신 문제

```yaml
# ❌ Bad - [localhost](http://localhost) 사용
services:
  backend:
    environment:
      - DB_HOST=[localhost](http://localhost)  # 안 됨!

# ✅ Good - 서비스 이름 사용
services:
  backend:
    environment:
      - DB_HOST=db  # 서비스 이름으로!
```

---

## 6.2 시작 순서 문제

```yaml
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

---

## 6.3 볼륨 데이터 유지

```bash
# ❌ 볼륨까지 삭제
docker compose down -v

# ✅ 컨테이너만 삭제 (볼륨 유지)
docker compose down

# ✅ 볼륨 확인
docker volume ls
```

---

# 7. 베스트 프랙티스

## 7.1 .env 파일 사용

```bash
# .env
DB_PASSWORD=secret123
API_KEY=mykey

# .gitignore에 추가!
.env
```

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - DB_PASSWORD=${DB_PASSWORD}
```

---

## 7.2 로그 관리

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 7.3 리소스 제한

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          memory: 256M
```

---

# 8. Interview Readiness

## ▶ Q1: Docker Compose를 사용하는 이유는?

**A**: 여러 컨테이너를 **하나의 YAML 파일로 정의하고 관리**할 수 있습니다.

**장점**:

1. **간편함**: `docker compose up` 한 줄로 전체 스택 실행
2. **재현성**: 동일한 환경을 어디서든 재현
3. **버전 관리**: YAML 파일을 Git으로 관리
4. **네트워크**: 서비스 간 자동 연결

---

## ▶ Q2: depends_on의 한계는?

**A**: `depends_on`은 **컨테이너 시작 순서**만 보장하고, **서비스가 준비되었는지는 보장하지 않습니다**.

**해결책**:

```yaml
services:
  backend:
    depends_on:
      db:
        condition: service_healthy  # 헬스체크 필수!
  
  db:
    healthcheck:
      test: ["CMD", "mysqladmin", "ping"]
```

---

## ▶ Q3: 컨테이너 간 통신 방법은?

**A**: **서비스 이름**을 호스트명으로 사용합니다.

```yaml
services:
  backend:
    environment:
      - DB_HOST=db  # 서비스 이름
  
  db:
    image: mysql:8.0
```

Docker Compose가 자동으로 네트워크를 생성하고, 같은 네트워크의 서비스는 서비스 이름으로 통신 가능합니다.

---

## ▶ Q4: 개발/프로덕션 환경 분리 방법은?

**A**: **여러 Compose 파일**을 조합합니다.

```bash
# 기본 설정
docker-compose.yml

# 개발 환경 추가 설정
[docker-compose.dev](http://docker-compose.dev).yml

# 프로덕션 환경 추가 설정
[docker-compose.prod](http://docker-compose.prod).yml
```

```bash
# 개발
docker compose -f docker-compose.yml -f [docker-compose.dev](http://docker-compose.dev).yml up

# 프로덕션
docker compose -f docker-compose.yml -f [docker-compose.prod](http://docker-compose.prod).yml up -d
```

---

## 🔑 핵심 체크리스트

- [ ]  `docker compose up -d` 백그라운드 실행
- [ ]  서비스 이름으로 컨테이너 간 통신
- [ ]  `depends_on` + `healthcheck` 조합
- [ ]  `.env` 파일로 환경변수 관리
- [ ]  볼륨으로 데이터 영속성 확보
- [ ]  `down` vs `down -v` 차이 이해
- [ ]  개발/프로덕션 환경 분리

---

**작성일**: 2026-01-17  

**면접 빈출도**: ⭐⭐⭐⭐ (최상)