---
tags: study, Docker, DevOps
created: 2026-01-24
---

# Docker 기본 명령어

## 한 줄 요약
> Docker는 애플리케이션을 컨테이너로 패키징하여 어떤 환경에서도 동일하게 실행할 수 있게 하는 컨테이너 가상화 플랫폼

## 상세 설명

Docker는 VM보다 경량이며 초 단위로 시작되고 적은 메모리를 사용합니다. 이미지 기반으로 한 번 빌드하면 어디서나 실행 가능하며, 각 컨테이너는 독립적인 환경을 제공합니다.

### 컨테이너 생애주기 관리

**docker run - 컨테이너 생성 및 실행**

주요 옵션:
- `-d`: 백그라운드 모드
- `-p`: 포트 매핑 (호스트:컨테이너)
- `--name`: 컨테이너 이름 지정
- `-v`: 볼륨 마운트
- `-e`: 환경변수 설정
- `--rm`: 종료 시 자동 삭제
- `-it`: 인터랙티브 터미널

**docker start / stop / restart**

이미 생성된 컨테이너를 제어합니다.

**docker rm - 컨테이너 삭제**

옵션:
- `-f`: 실행 중 강제 삭제
- `-v`: 연결된 익명 볼륨도 삭제

### 이미지 관리

**docker pull / push**
- pull: Docker Hub에서 이미지 다운로드
- push: Docker Hub에 이미지 업로드

**docker images / rmi**
- images: 이미지 목록 확인
- rmi: 이미지 삭제

### 상태 확인 및 디버깅

**docker ps - 컨테이너 목록**

옵션:
- `-a`: 중지된 컨테이너 포함
- `-q`: ID만 출력
- `--format`: 출력 포맷 지정

**docker logs - 로그 확인**

옵션:
- `-f`: 실시간 스트리밍
- `--tail`: 마지막 N줄만
- `-t`: 타임스탬프 표시

**docker exec - 컨테이너 내부 명령 실행**

주로 컨테이너 내부 셸 접속에 사용: `docker exec -it [container] /bin/bash`

**docker inspect - 상세 정보**

컨테이너의 모든 정보를 JSON 형식으로 출력합니다.

### 네트워크 관리

**docker network**

명령어:
- `ls`: 네트워크 목록
- `create`: 사용자 정의 네트워크 생성
- `inspect`: 네트워크 상세 정보
- `connect`: 컨테이너를 네트워크에 연결

같은 네트워크의 컨테이너는 컨테이너 이름으로 통신 가능합니다.

### 볼륨 관리

**docker volume**

명령어:
- `ls`: 볼륨 목록
- `create`: 볼륨 생성
- `inspect`: 볼륨 상세 정보
- `rm`: 볼륨 삭제

볼륨을 사용하면 컨테이너를 삭제해도 데이터가 보존됩니다.

### 시스템 정리

**docker system prune**

옵션:
- `-a`: 모든 이미지 포함
- `--volumes`: 볼륨까지 삭제
- `-f`: 확인 없이 즉시 삭제

## 코드 예시
```bash
# Nginx 웹 서버 실행
docker run -d \
  --name my-nginx \
  -p 80:80 \
  -v ~/html:/usr/share/nginx/html \
  nginx:latest

# MySQL 데이터베이스 실행
docker run -d \
  --name my-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=password \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0

# 네트워크 생성 및 컨테이너 연결
docker network create app-network

docker run -d \
  --name mysql \
  --network app-network \
  -e MYSQL_ROOT_PASSWORD=password \
  mysql:8.0

docker run -d \
  --name backend \
  --network app-network \
  -e DB_HOST=mysql \
  myapp:latest
```

## 주의사항 / 함정

1. 컨테이너 간 통신은 같은 Docker 네트워크에 연결해야 가능합니다
2. `-v`와 `--mount`의 차이: `-v`는 간단하지만 `--mount`가 더 명시적이고 권장됩니다
3. 볼륨 데이터를 유지하려면 `docker rm -v` 대신 `docker rm` 사용
4. 컨테이너 이름은 고유해야 합니다

## 관련 개념
- [[Dockerfile-작성법]]
- [[Docker-Compose]]
- [[컨테이너-가상화]]
- [[Docker-네트워크]]

## 면접 질문
1. Docker와 VM의 차이는?
2. docker run과 docker start의 차이는?
3. -v와 --mount의 차이는?
4. 컨테이너간 통신은 어떻게 하나요?

## 참고 자료
- Docker 공식 문서
