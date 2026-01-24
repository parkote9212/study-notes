---
tags:
  - interview
  - domain
  - jpa
  - spring
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - 프로젝트별 권한체계 설계

## 질문
> 시스템 권한(ADMIN/MEMBER)과 프로젝트 권한(PL/DEV/MEMBER)을 분리한 이유와 구현 방법은?

## 핵심 답변 (3줄)
1. **2계층 권한 체계** - 시스템 레벨(Role)과 프로젝트 레벨(ProjectMember.Role) 분리
2. **커스텀 어노테이션** - `@RequireProjectLeader`, `@RequireProjectMember`로 선언적 권한 검증
3. **SpEL + Service 조합** - `@PreAuthorize`와 `ProjectSecurityService`로 동적 권한 체크

## 상세 설명
```java
// 시스템 권한 (User 엔티티)
public enum Role {
    ADMIN,   // 시스템 관리자
    MEMBER   // 일반 사용자
}

// 프로젝트 권한 (ProjectMember 엔티티)
public enum Role {
    PL,          // Project Leader
    DEV,         // 개발자
    DESIGN,      // 디자이너
    STAKEHOLDER, // 이해관계자
    MEMBER       // 일반 멤버
}

// 커스텀 어노테이션 정의
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@PreAuthorize("@projectSecurityService.isProjectLeader(#projectId)")
public @interface RequireProjectLeader {}
```

## 코드 예시
```java
// ProjectSecurityService
@Service
public class ProjectSecurityService {
    public boolean isProjectLeader(Long projectId) {
        Long userId = SecurityUtil.getCurrentUserIdOrThrow();
        ProjectMember member = projectMemberRepository
            .findByProject_ProjectIdAndUser_UserId(projectId, userId)
            .orElse(null);
        return member != null && member.getRole() == ProjectMember.Role.PL;
    }
}

// 서비스에서 사용
@RequireProjectLeader
public void deleteProject(Long projectId) {
    // PL만 실행 가능
}
```

## 꼬리 질문 예상
- `@PreAuthorize`에서 SpEL로 빈을 호출할 때 `@`를 붙이는 이유는?
- 권한 체크 실패 시 어떤 예외가 발생하나요?

## 참고
- [[Spring-Security-권한체계]]
- [[커스텀-어노테이션-AOP]]
