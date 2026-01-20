# [AWS] 배포 전략 3가지 비교: EC2 vs Docker vs Cloud Native

🏷️기술 카테고리: AWS, DevOps, Docker, Infra
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): Yes
날짜: 2026년 1월 10일 오후 5:43

# 1. Abstract: 핵심 요약

> AWS에 애플리케이션을 배포하는 방법은 크게 **3가지 전략**이 있습니다. 각 방식은 학습 곡선, 비용, 확장성, 운영 복잡도가 다르며, **프로젝트 단계와 규모**에 따라 최적의 선택이 달라집니다.
> 

**핵심 원칙**: 개인 프로젝트는 비용 최소화, 스타트업은 자동화, 엔터프라이즈는 고가용성에 최우선 순위

---

# 2. Technical Deep Dive: 3가지 배포 전략

## 2.1 방법 A: 생(Raw) EC2 배포

**개념**: EC2에 Java, Nginx, MariaDB를 **직접 설치**하는 전통적 방식

**장점**:

- 리눅스 동작 원리, 파일 시스템 등을 **깊이 이해** 가능
- 학습용으로 좋음

**단점**:

- 환경 일관성 부족으로 에러 빈번 ("내 컴퓨터에서는 되는데...")
- **확장성 제로** (서버 추가 시 수동 설정 반복)
- Swap 메모리 설정, 방화벽 설정 등 수동 관리 부담

**결론**: ❌ 학습용으로는 좋지만 실무에서는 비추천

---

## 2.2 방법 B: Docker Compose 올인원

**개념**: EC2에 Docker만 설치하고, `docker-compose.yml` 하나로 모든 서비스(Spring, Nginx, DB)를 **컨테이너로** 실행

**장점**:

- **환경 일치** (Mac과 Ubuntu에서 동일하게 동작)
- **배포가 간편** (`docker-compose up -d` 한 줄로 실행)
- 로컬 개발 환경과 동일한 구성

**단점**:

- 컨테이너 삭제/볼륨 설정 실수 시 **데이터 유실 위험**
- 리소스 경합 발생 가능성 (모든 서비스가 한 서버에서 실행)
- DB 백업/복구 직접 관리 필요

**결론**: ✅ 초기 단계에서 가장 빠르고 간편한 방법

---

## 2.3 방법 C: 클라우드 네이티브 분리 배포

**개념**: 각 컴포넌트(DB, Frontend, Backend)를 AWS 특화 서비스(RDS, S3+CloudFront, EC2+Docker)에 **분리**하여 실행

**권장 아키텍처**:

- **Frontend (React)**: S3 + CloudFront (정적 파일 서빙)
- **Backend (Spring Boot)**: EC2 + Docker
- **Database**: AWS RDS (자동 백업, 패치, Multi-AZ)

**장점**:

- **안정성**: DB 백업/패치 자동 관리 (RDS)
- **성능**: 정적 파일 전송 속도 향상 (CloudFront CDN)
- **확장성**: 각 컴포넌트 독립적으로 스케일 가능
- **비용 효율**: S3는 EC2보다 훨씬 저렴

**단점**:

- 설정해야 할 AWS 리소스가 많아 **초기 러닝 커브** 존재
- 네트워크 설정 (VPC, Security Group) 이해 필요

**결론**: ⭐ **강력 추천** (실무 표준)

---

# 3. Critical Thinking: 규모별 배포 전략

## ⚖️ 의사결정: 프로젝트 단계별 최적 전략

| 구분 | 개인 프로젝트 / 학습 | 소규모 스타트업 / MVP | 대기업 / 엔터프라이즈 |
| --- | --- | --- | --- |
| **핵심 가치** | 비용 절감, 빠른 구현 | 안정성, 자동화 | 고가용성, 보안, 무중단 |
| **Frontend** | EC2 내부 Nginx or S3 | S3 + CloudFront (HTTPS) | S3 + CloudFront + WAF |
| **Backend** | 단일 EC2 (Docker Compose) | EC2 + Auto Scaling or Elastic Beanstalk | AWS EKS (Kubernetes), ECS |
| **Database** | EC2 내부 Docker | AWS RDS (단일 AZ) | AWS Aurora (Multi-AZ, Read Replica) |
| **CI/CD** | 수동 배포 (SCP/FTP) | GitHub Actions → Docker Hub → EC2 | Jenkins/GitLab CI, Blue/Green 배포 |

### 비용 vs 안정성 트레이드오프

**개인 프로젝트 (비용 최소화)**:

```yaml
# docker-compose.yml
services:
  backend:
    image: my-backend
    ports: ["8080:8080"]
  mariadb:
    image: mariadb
    volumes: ["./data:/var/lib/mysql"]  # 로컬 볼륨
  frontend:
    image: my-frontend
    ports: ["80:80"]
```

**비용**: t3.small 1대 (~$15/월)

**스타트업 (안정성 우선)**:

- Frontend: S3 + CloudFront (~$5/월)
- Backend: t3.small EC2 (~$15/월)
- Database: RDS db.t3.micro (~$15/월)

**비용**: ~$35/월

**Decision**: 

개인 프로젝트는 **방법 B (Docker Compose)**로 시작 후, 사용자가 증가하면 **방법 C (클라우드 네이티브)**로 단계적 마이그레이션

---

# 4. Project Case Study: 실무 적용

## 🚀 공매 물건 정보 시스템 - 단계별 배포 전략

**S (Situation)**:

- 초기 개발 단계에서 빠른 배포와 테스트 필요
- 이후 사용자 증가 시 안정성 확보 필요

**T (Task)**:

- Phase 1: 빠른 MVP 출시
- Phase 2: 안정성 및 성능 개선

**A (Action)**:

**Phase 1 (Docker Compose 올인원)**:

```yaml
# docker-compose.yml
services:
  backend:
    image: auction-backend
    environment:
      - DB_HOST=mariadb
  mariadb:
    image: mariadb
    volumes:
      - db-data:/var/lib/mysql
  frontend:
    image: auction-frontend
    ports: ["80:80"]
volumes:
  db-data:
```

**배포 시간**: 30분

**비용**: t3.small 1대 ($15/월)

**Phase 2 (클라우드 네이티브 마이그레이션)**:

1. **DB 마이그레이션**: Docker MariaDB → AWS RDS
    
    ```bash
    mysqldump --host=[localhost](http://localhost) > backup.sql
    mysql --host=rds-endpoint < backup.sql
    ```
    
2. **Frontend 분리**: EC2 Nginx → S3 + CloudFront
    
    ```bash
    npm run build
    aws s3 sync dist/ s3://my-bucket/
    ```
    
3. **Backend 유지**: EC2 + Docker (환경변수만 변경)
    
    ```yaml
    environment:
      - DB_HOST=[rds-endpoint.amazonaws.com](http://rds-endpoint.amazonaws.com)
    ```
    

**R (Result)**:

- ✅ Phase 1: 2주 만에 MVP 출시
- ✅ Phase 2: RDS 자동 백업으로 데이터 유실 위험 제거
- ✅ CloudFront CDN으로 페이지 로딩 속도 50% 개선
- ✅ 비용: $15 → $35/월 (안정성 대비 합리적)

---

# 5. Interview Readiness: 예상 질문

- Q: Docker Compose와 Kubernetes의 차이점은 무엇인가요?
    
    **A**: Docker Compose는 **단일 호스트**에서 여러 컨테이너를 관리하는 도구이고, Kubernetes는 **여러 호스트(클러스터)**에서 컨테이너를 오케스트레이션하는 플랫폼입니다. 소규모 프로젝트에서는 Docker Compose로 충분하지만, 트래픽이 증가하여 여러 서버가 필요한 경우 Kubernetes (AWS EKS)로 전환합니다.
    
- Q: RDS를 사용하는 이유는 무엇인가요? EC2에 직접 DB를 설치하면 안 되나요?
    
    **A**: 기술적으로는 가능하지만, RDS는 **자동 백업, 자동 패치, Multi-AZ 복제**를 제공하여 운영 부담을 크게 줄여줍니다. 새벽 3시에 DB가 다운되어도 RDS는 자동으로 Failover 하지만, EC2에 직접 설치한 DB는 수동으로 복구해야 합니다. 실무에서는 안정성과 시간 절약을 위해 RDS를 선택합니다.
    
- Q: S3 + CloudFront를 사용하는 이유는 무엇인가요?
    
    **A**: React 빌드 결과물은 **정적 파일**(HTML, JS, CSS)이므로 서버가 필요 없습니다. S3는 저장소이고, CloudFront는 **전 세계 엣지 로케이션에 캐싱**하여 사용자와 가까운 곳에서 파일을 제공하므로 로딩 속도가 빠릅니다. EC2로 Nginx를 띄우는 것보다 비용도 저렴하고 성능도 좋습니다.
    

---

## 🗺️ 단계별 마이그레이션 로드맵

```
Phase 1: Docker Compose 올인원
└─> 빠른 MVP 출시 (비용: $15/월)
    ↓
Phase 2: DB 분리 (RDS)
└─> 데이터 안정성 확보 (비용: $30/월)
    ↓
Phase 3: Frontend 분리 (S3 + CloudFront)
└─> 성능 개선 (비용: $35/월)
    ↓
Phase 4: Backend 스케일링 (Auto Scaling)
└─> 트래픽 대응 (비용: 변동)
```

**핵심 원칙**: 한 번에 모든 것을 Cloud Native로 만들 필요 없음. **단계적으로 마이그레이션**하면서 각 단계의 이점을 체득하는 것이 학습과 실무에 모두 효과적