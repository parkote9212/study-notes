# [AWS] IAM Role vs Access Key: 보안 베스트 프랙티스

🏷️기술 카테고리: AWS, DevOps, Infra, Security
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): Yes
날짜: 2026년 1월 10일 오후 5:39

# 1. Abstract: 핵심 요약

> **AWS IAM (Identity and Access Management)**는 AWS 자원에 대한 접근 권한을 안전하게 제어하는 서비스입니다. **최소 권한의 원칙(Least Privilege)**에 따라 필요한 권한만 부여하고, 루트 계정 대신 IAM 사용자와 역할을 사용하는 것이 클라우드 보안의 기본입니다.
> 

**핵심 년지**: Access Key는 유출 위험이 항상 존재하지만, **IAM Role**은 AWS가 임시 자격 증명을 자동 갱신해주므로 코드에 비밀 정보를 남기지 않고도 안전하게 연동 가능

---

# 2. Technical Deep Dive: IAM 구성 요소

## 2.1 IAM 핵심 4가지 개념

| 요소 | 정의 | 실무 활용 |
| --- | --- | --- |
| **User (사용자)** | 실제 사람이나 애플리케이션 | 개발자 개인 계정, CI/CD 도구 전용 계정 |
| **Group (그룹)** | 사용자들의 집합 | 'Developer' 그룹에 S3 Read 권한 부여 후 팀원 추가 |
| **Role (역할)** | **서비스나 리소스**에 부여하는 권한 | EC2 인스턴스가 S3에 접근할 때 사용 (Key 불필요) |
| **Policy (정책)** | 권한을 정의한 JSON 문서 | "A 버킷에 대해서만 읽기 권한을 허용" 명세 |

## 2.2 보안 필수 수칙

- Root 계정 봉인
    - MFA(OTP) 설정 후 일상적인 작업에는 절대 사용 금지
    - Root는 결제 정보 변경, 계정 삭제 등 모든 권한 보유
    - 유출 시 복구 불가능할 정도로 치명적
- Access Key 관리
    - 로컬 환경변수나 AWS CLI 설정 이용
    - **코드에 직접 노출 절대 금지**
    - GitHub Secret Scanning에 걸리면 즉시 해킹 대상
- 최소 권한 부여
    - 필요한 리소스 ARN을 명시하여 권한 범위 제한
    - `S3:*` (모든 권한) 대신 `S3:PutObject` (특정 액션만)

---

# 3. Critical Thinking: EC2에서 S3 접근 방식

## ⚖️ 의사결정: Access Key vs IAM Role

**Situation**: Spring Boot 서버(EC2)에서 S3 버킷에 파일을 업로드해야 하는 상황

### ❌ Before: Access Key 하드코딩 방식

```yaml
# application.yml
cloud:
  aws:
    credentials:
      # ⚠️ 위험: 깃허브에 올라가는 순간 해킹 및 요금 폭탄의 주범
      access-key: AKIAIOSFODNN7EXAMPLE 
      secret-key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE
    region:
      static: ap-northeast-2
```

**문제점**:

1. 환경변수로 빼도 `.env` 파일이 Git에 올라가면 끝
2. 키 로테이션(갱신) 관리 부담
3. 코드 공유 시 보안 취약점 증가

### ✅ After: IAM Role 사용 방식

**1. IAM Policy 생성** (JSON)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

**2. IAM Role 생성 및 EC2에 연결**

- AWS Console → IAM → 역할 생성 → EC2 선택
- 위 Policy 연결
- EC2 인스턴스 → 보안 → IAM 역할 수정

**3. Spring Boot 코드**

```yaml
# application.yml
cloud:
  aws:
    # ✅ Key 정보를 입력하지 않음!
    # EC2 인스턴스에 부여된 IAM Role을 통해 자동으로 인증 수행
    region:
      static: ap-northeast-2
    stack:
      auto: false
```

**Decision**: 

IAM Role을 사용하면 AWS가 **임시 자격 증명을 자동 갱신**해주므로:

- 키 유출 위험 0%
- 키 로테이션 관리 불필요
- 코드에 보안 정보 미포함

---

# 4. Project Case Study: 실무 적용

## 🛡️ 산업안전 AI: 탐지 이미지 S3 적재

**S (Situation)**:

- AI 모델이 탐지한 위험 상황 이미지를 S3에 업로드하여 관리
- 협업 환경(GitHub)에서 보안 자격 증명 유출 방지 필요

**T (Task)**:

- GitHub에 Access Key가 노출되지 않도록 서버 인프라 보안 구축
- S3 업로드 기능 구현

**A (Action)**:

1. **S3 PutObject 전용 IAM Policy 생성**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::safety-detection-images/*"
    }
  ]
}
```

1. **IAM Role 생성 및 EC2에 할당**
    - Role 이름: `EC2-S3-Upload-Role`
    - 위 Policy 연결
    - EC2 인스턴스에 Role 할당
2. **Spring Boot 코드에서 별도 키 설정 없이 AWS SDK 사용**

```java
@Service
public class S3Service {
    private final S3Client s3Client = S3Client.builder()
        .region(Region.AP_NORTHEAST_2)
        // IAM Role이 자동으로 인증 처리
        .build();
    
    public void uploadImage(String key, byte[] imageData) {
        s3Client.putObject(
            PutObjectRequest.builder()
                .bucket("safety-detection-images")
                .key(key)
                .build(),
            RequestBody.fromBytes(imageData)
        );
    }
}
```

**R (Result)**:

- ✅ 보안 취약점 원천 차단
- ✅ GitHub Secret Scanning에서 단 한 건의 유출 경고 없이 안정적 운영
- ✅ 키 로테이션 관리 부담 제거

---

# 5. Interview Readiness: 예상 질문

- Q: 루트 계정과 IAM 사용자의 차이는 무엇이며, 왜 루트를 쓰면 안 되나요?
    
    **A**: 루트 계정은 결제 정보 변경, 계정 삭제 등 **모든 권한을 가진 마스터 계정**입니다. 유출 시 복구가 불가능할 정도로 치명적이기 때문에 MFA를 설정하고 일상 업무에서는 권한이 제한된 IAM 사용자를 만들어 사용하는 것이 보안 표준입니다.
    
- Q: '최소 권한의 원칙'을 프로젝트에서 어떻게 실천했나요?
    
    **A**: S3 접근 권한을 줄 때 `S3:*` (모든 권한) 대신, `s3:PutObject`처럼 특정 액션만 허용하고, Resource 항목에 전체가 아닌 특정 버킷의 ARN만 명시하여 권한 오남용을 막았습니다. 예를 들어 `arn:aws:s3:::my-specific-bucket/*`로 특정 버킷으로 제한했습니다.
    
- Q: IAM Role과 Access Key의 차이점을 설명해주세요.
    
    **A**: Access Key는 영구적인 자격 증명으로, 한 번 생성하면 수동으로 로테이션하기 전까지 계속 유효합니다. 반면 IAM Role은 **임시 자격 증명**을 AWS가 자동으로 발급/갱신하므로 코드에 키를 노출하지 않고도 보안을 유지할 수 있습니다. EC2, Lambda 등 AWS 리소스에서 다른 AWS 서비스에 접근할 때는 항상 Role을 사용해야 합니다.
    

---

## 🔑 보안 체크리스트

- [ ]  Root 계정 MFA 설정 후 봉인
- [ ]  Access Key를 코드에 하드코딩하지 않기
- [ ]  EC2 → S3 접근 시 IAM Role 사용
- [ ]  Policy에 특정 Action과 Resource ARN 명시
- [ ]  불필요한 권한은 부여하지 않기 (Least Privilege)