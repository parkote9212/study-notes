# AWS ECR + GitHub Actions CI/CD 배포 가이드

> BizSync 프로젝트 배포 과정에서 겪은 문제와 해결 방법 정리

---

## 📋 아키텍처 개요

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│   GitHub    │────▶│   GitHub    │────▶│      AWS ECR        │
│   (Push)    │     │   Actions   │     │  (Docker Registry)  │
└─────────────┘     └─────────────┘     └──────────┬──────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                        AWS EC2                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    Nginx    │  │  Frontend   │  │      Backend        │  │
│  │  (Proxy)    │◀▶│  (React)    │  │   (Spring Boot)     │  │
│  └─────────────┘  └─────────────┘  └──────────┬──────────┘  │
└────────────────────────────────────────────────┼────────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │    AWS RDS      │
                                        │   (MariaDB)     │
                                        └─────────────────┘
```

---

## 🔧 사전 준비

### GitHub Secrets 설정

Settings → Secrets and variables → Actions:

```
AWS_ACCESS_KEY_ID        # IAM Access Key
AWS_SECRET_ACCESS_KEY    # IAM Secret Key
AWS_ACCOUNT_ID           # 123456789012
EC2_HOST                 # 54.180.155.0
EC2_USER                 # ec2-user
EC2_SSH_KEY              # -----BEGIN RSA PRIVATE KEY----- ...
VITE_API_BASE_URL        # http://54.180.155.0/api
VITE_WS_URL              # ws://54.180.155.0/ws
```

---

## 🚨 트러블슈팅: Docker 설치 문제

### ❌ 문제

Amazon Linux 2023에서 `docker-compose` 설치 실패:

```bash
sudo dnf install -y docker docker-compose
# Error: No match for argument: docker-compose
```

### ✅ 해결

Amazon Linux 2023에서는 `docker-compose`가 기본 패키지에 없음!

**Docker 설치:**
```bash
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# 재접속 필요
exit
```

**Docker Compose 수동 설치:**
```bash
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "v\K[0-9.]+')

sudo curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# 확인
docker-compose --version
```

---

## 🚨 트러블슈팅: 환경변수 문제

### ❌ 문제

EC2에서 컨테이너 실행 시 환경변수가 적용 안 됨:
- DB 연결 실패
- JWT Secret 누락

### ✅ 해결

**1. .env 파일 생성:**
```bash
# /home/ec2-user/bizsync-project/.env
SPRING_DATASOURCE_URL=jdbc:mariadb://bizsync-db.xxx.rds.amazonaws.com:3306/bizsync
SPRING_DATASOURCE_USERNAME=admin
SPRING_DATASOURCE_PASSWORD=yourpassword
JWT_SECRET=your-256-bit-secret-key
ADMIN_EMAIL=admin@bizsync.com
ADMIN_PASSWORD=Admin123!@#
```

**2. docker-compose.yml에서 env_file 사용:**
```yaml
services:
  backend:
    env_file:
      - .env
```

**3. GitHub Secrets → EC2 환경변수 전달:**
```yaml
# cd.yml에서 SSH 명령으로 .env 파일 업데이트
echo "JWT_SECRET=${{ secrets.JWT_SECRET }}" >> .env
```

---

## 🚨 트러블슈팅: ECR 로그인 만료

### ❌ 문제

12시간 후 ECR 로그인 만료로 docker pull 실패

### ✅ 해결

CD 파이프라인에서 매번 ECR 로그인:
```yaml
- name: Deploy to EC2 via SSH
  script: |
    # 매번 ECR 로그인 (12시간 유효)
    aws ecr get-login-password --region ap-northeast-2 | \
      docker login --username AWS --password-stdin \
      ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.ap-northeast-2.amazonaws.com
```

---

## ⚠️ 배포 전 체크리스트

### 로컬에서 반드시 확인:

```bash
# 1. 프론트엔드 린트 (필수!)
cd frontend
npm run lint

# 2. 프론트엔드 빌드
npm run build

# 3. 백엔드 빌드
cd ../backend
./gradlew build

# 4. 테스트
./gradlew test
```

### 흔한 실수:
- [ ] ESLint 에러 무시하고 푸시 → CI 실패
- [ ] TypeScript 타입 에러 → 빌드 실패
- [ ] import 순서 틀림 → 린트 실패
- [ ] 환경변수 누락 → 런타임 에러

---

## 📁 CI/CD 파일 구조

```
.github/workflows/
├── ci.yml          # PR/Push 시 빌드 & 테스트
└── cd.yml          # main 푸시 시 ECR 배포
```

### ci.yml 주요 단계:
1. Backend: Gradle 빌드 + 테스트 (MariaDB 컨테이너)
2. Frontend: npm lint + tsc + build
3. Docker: 이미지 빌드 테스트

### cd.yml 주요 단계:
1. ECR 로그인
2. Backend/Frontend Docker 이미지 빌드 & 푸시
3. SSH로 EC2 접속 → docker compose pull & up

---

## 🔑 유용한 명령어

### EC2 접속:
```bash
ssh -i bizsync-key.pem ec2-user@54.180.155.0
```

### 로그 확인:
```bash
cd ~/bizsync-project
docker compose logs -f backend
docker compose logs -f frontend
```

### 수동 배포:
```bash
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin [ACCOUNT_ID].dkr.ecr.ap-northeast-2.amazonaws.com
docker compose pull
docker compose up -d
```

### 컨테이너 재시작:
```bash
docker compose restart backend
docker compose restart frontend
```

---

## 📝 핵심 교훈

1. **배포 전 로컬 빌드 필수** - lint, build 돌려서 헛짓거리 방지
2. **Amazon Linux 2023 ≠ Amazon Linux 2** - docker-compose 수동 설치 필요
3. **환경변수는 .env 파일로 관리** - GitHub Secrets → .env → docker-compose
4. **ECR 로그인은 12시간 유효** - CD 파이프라인에서 매번 로그인

---

**작성일**: 2026-01-26  
**프로젝트**: BizSync
