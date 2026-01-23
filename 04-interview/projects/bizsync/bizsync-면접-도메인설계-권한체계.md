---
tags: interview, domain, jpa, spring, bizsync, project
created: 2025-01-23
difficulty: 중
---

# BizSync - 도메인 설계 & 권한 체계 면접

## 질문 1: 프로젝트별 권한 체계 설계
> 시스템 권한(ADMIN/MEMBER)과 프로젝트 권한(PL/DEV/MEMBER)을 분리한 이유와 구현 방법은?

### 핵심 답변 (3줄)
1. **2계층 권한 체계** - 시스템 레벨(Role)과 프로젝트 레벨(ProjectMember.Role) 분리
2. **커스텀 어노테이션** - `@RequireProjectLeader`, `@RequireProjectMember`로 선언적 권한 검증
3. **SpEL + Service 조합** - `@PreAuthorize`와 `ProjectSecurityService`로 동적 권한 체크

### 상세 설명
```java
// 시스템 권한 (User 엔티티)
public enum Role {
    ADMIN,   // 시스템 관리자
    MEMBER   // 일반 사용자
}

// 프로젝트 권한 (ProjectMember 엔티티)
public enum Role {
    PL,          // Project Leader - 프로젝트 관리 권한
    DEV,         // 개발자
    DESIGN,      // 디자이너
    STAKEHOLDER, // 이해관계자 (읽기 전용)
    MEMBER       // 일반 멤버
}

// 커스텀 어노테이션 정의
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@PreAuthorize("@projectSecurityService.isProjectLeader(#projectId)")
public @interface RequireProjectLeader {}

// 서비스에서 사용
@RequireProjectLeader
public void deleteProject(Long projectId) {
    // PL만 실행 가능
}
```

### 코드 예시
```java
// ProjectSecurityService - SpEL에서 호출되는 서비스
@Service
public class ProjectSecurityService {
    
    public boolean isProjectLeader(Long projectId) {
        Long userId = SecurityUtil.getCurrentUserIdOrThrow();
        
        ProjectMember member = projectMemberRepository
            .findByProject_ProjectIdAndUser_UserId(projectId, userId)
            .orElse(null);
        
        return member != null && member.getRole() == ProjectMember.Role.PL;
    }
    
    public boolean isProjectMember(Long projectId) {
        Long userId = SecurityUtil.getCurrentUserIdOrThrow();
        return projectMemberRepository
            .existsByProject_ProjectIdAndUser_UserId(projectId, userId);
    }
}
```

### 꼬리 질문 예상
- `@PreAuthorize`에서 SpEL로 빈을 호출할 때 `@`를 붙이는 이유는?
- 권한 체크 실패 시 어떤 예외가 발생하고 어떻게 처리하나요?

---

## 질문 2: 엔티티 설계 - Setter 미사용 패턴
> 엔티티에 Setter를 사용하지 않은 이유와 대안은 무엇인가요?

### 핵심 답변 (3줄)
1. **불변성 보장** - 의도치 않은 상태 변경 방지, 도메인 무결성 유지
2. **의미 있는 메서드** - `spendBudget()`, `complete()` 등 비즈니스 의도를 드러내는 메서드 제공
3. **빌더 패턴** - 생성 시점에만 값 설정, 이후 변경은 명시적 메서드로만

### 상세 설명
```java
@Entity
@Getter  // Setter 없음!
@NoArgsConstructor(access = AccessLevel.PROTECTED)  // JPA용 기본 생성자
@Builder
public class Project {
    
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long projectId;
    
    private String name;
    private BigDecimal totalBudget;
    private BigDecimal usedBudget;
    private ProjectStatus status;
    
    // ❌ Setter 대신 → ✅ 비즈니스 메서드
    public void spendBudget(BigDecimal amount) {
        BigDecimal expected = this.usedBudget.add(amount);
        if (this.totalBudget.compareTo(expected) < 0) {
            throw new IllegalStateException("예산 초과!");
        }
        this.usedBudget = expected;
    }
    
    public void complete() {
        this.status = ProjectStatus.COMPLETED;
    }
    
    public void update(String name, String description, ...) {
        if (name != null && !name.isBlank()) {
            this.name = name;
        }
        // 선택적 필드 업데이트
    }
}
```

### 꼬리 질문 예상
- `@NoArgsConstructor(access = PROTECTED)`를 사용하는 이유는?
- 업데이트 메서드에서 null 체크하는 이유는?

---

## 질문 3: 연관관계 매핑 설계
> ProjectMember의 다대다 관계를 중간 테이블 엔티티로 풀어낸 이유는?

### 핵심 답변 (3줄)
1. **추가 속성 필요** - 단순 매핑이 아닌 `role` 컬럼 등 부가 정보 저장
2. **양방향 매핑 회피** - 순환 참조 문제 방지, 쿼리 예측 가능
3. **독립적인 생명주기** - 멤버 추가/삭제가 Project나 User에 영향 X

### 상세 설명
```java
// ❌ @ManyToMany 사용 시 문제
@Entity
public class Project {
    @ManyToMany
    @JoinTable(name = "project_member")
    private Set<User> members;  // role 정보 저장 불가!
}

// ✅ 중간 엔티티로 해결
@Entity
public class ProjectMember {
    @Id @GeneratedValue
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id")
    private Project project;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;
    
    @Enumerated(EnumType.STRING)
    private Role role;  // 추가 속성!
    
    private LocalDateTime joinedAt;  // 필요 시 확장 가능
}
```

### 꼬리 질문 예상
- Project에서 members를 조회하려면 어떻게 해야 하나요?
- `@ManyToMany`를 사용해도 되는 경우는 언제인가요?

---

## 질문 4: 엔티티 삭제 전략 - 연관 데이터 처리
> 프로젝트 삭제 시 연관된 데이터(Task, Column, Member)를 어떻게 처리했나요?

### 핵심 답변 (3줄)
1. **명시적 삭제 순서** - 외래키 제약을 고려해 자식 → 부모 순으로 삭제
2. **Cascade 미사용** - 의도치 않은 연쇄 삭제 방지, 명시적 제어
3. **트랜잭션 보장** - `@Transactional`로 일관성 유지, 실패 시 전체 롤백

### 상세 설명
```java
@RequireProjectLeader
@Transactional
public void deleteProject(Long projectId) {
    // 1. 프로젝트 존재 여부 확인
    if (!projectRepository.existsById(projectId)) {
        throw new IllegalArgumentException("프로젝트를 찾을 수 없습니다.");
    }
    
    // 2. 연관 데이터 삭제 (순서 중요!)
    // 2-1. Task 삭제 (Column에 종속)
    taskRepository.deleteByColumn_Project_ProjectId(projectId);
    
    // 2-2. KanbanColumn 삭제
    List<KanbanColumn> columns = kanbanColumnRepository
        .findByProject_ProjectId(projectId);
    kanbanColumnRepository.deleteAll(columns);
    
    // 2-3. ProjectMember 삭제
    List<ProjectMember> members = projectMemberRepository
        .findAllByProject_ProjectId(projectId);
    projectMemberRepository.deleteAll(members);
    
    // 2-4. ApprovalDocument 삭제
    List<ApprovalDocument> docs = approvalDocumentRepository
        .findByProject_ProjectId(projectId);
    approvalDocumentRepository.deleteAll(docs);
    
    // 3. 프로젝트 삭제
    projectRepository.deleteById(projectId);
}
```

### 꼬리 질문 예상
- `CascadeType.REMOVE`를 사용하지 않은 이유는?
- Soft Delete 방식을 적용했다면 어떻게 구현했을까요?

---

## 질문 5: 도메인 모델 vs 영속성 모델
> 엔티티가 도메인 로직까지 포함하는 구조(Rich Domain Model)를 선택한 이유는?

### 핵심 답변 (3줄)
1. **응집도 향상** - 데이터와 행위가 같은 곳에 위치하여 이해하기 쉬움
2. **서비스 빈약 방지** - Anemic Domain Model의 절차적 코드 패턴 회피
3. **불변식 보장** - 도메인 규칙(예: 예산 초과 불가)을 엔티티 내부에서 강제

### 상세 설명
```java
// ✅ Rich Domain Model (현재 구조)
@Entity
public class Project {
    public void spendBudget(BigDecimal amount) {
        // 도메인 규칙: 예산 초과 불가
        if (this.totalBudget.compareTo(this.usedBudget.add(amount)) < 0) {
            throw new IllegalStateException("예산 초과!");
        }
        this.usedBudget = this.usedBudget.add(amount);
    }
}

// ❌ Anemic Domain Model (피해야 할 패턴)
@Entity
public class Project {
    @Setter
    private BigDecimal usedBudget;  // 검증 없이 변경 가능
}

@Service
public class ProjectService {
    public void spendBudget(Long projectId, BigDecimal amount) {
        Project p = repo.findById(projectId);
        if (p.getTotalBudget().compareTo(p.getUsedBudget().add(amount)) < 0) {
            throw new Exception();  // 여기서만 검증 → 누락 위험
        }
        p.setUsedBudget(p.getUsedBudget().add(amount));
    }
}
```

### 꼬리 질문 예상
- 엔티티에 로직이 많아지면 테스트는 어떻게 하나요?
- 외부 서비스 호출이 필요한 도메인 로직은 어디에 두나요?

---

## 참고
- [[JPA-엔티티-설계-가이드]]
- [[도메인주도설계-DDD]]
- [[bizsync-면접-JPA-MyBatis]]
