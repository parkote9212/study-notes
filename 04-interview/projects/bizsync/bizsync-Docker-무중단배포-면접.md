---
tags:
  - interview
  - docker
  - deployment
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - 무중단 배포 전략

## 질문
> 현재 구조에서 무중단 배포를 적용하려면 어떻게 해야 하나요?

## 핵심 답변 (3줄)
1. **Rolling Update** - 새 컨테이너 시작 후 구 컨테이너 종료
2. **헬스체크 활용** - 새 컨테이너가 healthy 상태가 되면 트래픽 전환
3. **로드밸런서 연동** - ALB/NLB로 다중 인스턴스 트래픽 분산

## 상세 설명
```bash
# 방법 1: Docker Compose Rolling Update
docker compose up -d --no-deps --build backend
# --no-deps: 의존 서비스 재시작 안함
# 기존 컨테이너 중지 전 새 컨테이너 시작

# 방법 2: Blue-Green with Nginx
# nginx.conf에서 upstream 서버 전환
upstream backend {
    server backend-blue:8080;  # 현재
    # server backend-green:8080;  # 대기
}

# 방법 3: AWS ECS/EKS 사용 시
# - ECS 서비스의 Rolling Update 설정
# - minimumHealthyPercent: 50
# - maximumPercent: 200
```

**현재 단일 EC2 구조의 한계:**
- 배포 시 짧은 다운타임 발생 (컨테이너 재시작 시간)
- 해결: ALB + 다중 EC2 or ECS Fargate 전환

## 꼬리 질문 예상
- Blue-Green과 Rolling의 장단점은?
- 배포 실패 시 롤백은 어떻게 하나요?

## 참고
- [[bizsync-DockerCompose-서비스구성-면접]]
- [[bizsync-Docker-멀티스테이지빌드-면접]]
