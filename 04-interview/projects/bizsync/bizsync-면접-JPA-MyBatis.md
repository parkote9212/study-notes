---
tags: interview, jpa, mybatis, bizsync
created: 2026-01-23
difficulty: 상
---

# BizSync - JPA + MyBatis 하이브리드 ORM 면접질문

## 질문 1
> BizSync에서 JPA와 MyBatis를 함께 사용하는 하이브리드 방식을 채택한 이유와 각각의 사용 케이스를 설명해주세요.

## 핵심 답변 (3줄)
1. JPA는 단순 CRUD와 엔티티 중심의 비즈니스 로직에서 생산성과 유지보수성이 뛰어나고, MyBatis는 복잡한 조인과 동적 쿼리에서 성능과 유연성이 뛰어납니다
2. 프로젝트 보드 조회처럼 여러 테이블을 조인하고 중첩된 컬렉션을 매핑해야 하는 경우 MyBatis의 ResultMap이 더 효율적입니다
3. 두 기술을 혼용하면 각 상황에 최적화된 도구를 선택할 수 있지만, 일관성 유지와 트랜잭션 관리에 주의해야 합니다

## 상세 설명
BizSync는 대부분의 기본 CRUD 작업에 JPA를 사용하지만, 칸반 보드 전체 조회처럼 복잡한 쿼리가 필요한 경우 MyBatis를 활용합니다.

**JPA 사용 케이스 (BizSync):**
- Project, User, Task 등의 단순 CRUD
- 연관관계 기반 객체 그래프 탐색
- Dirty Checking을 활용한 업데이트 (project.update())
- 엔티티 생명주기 이벤트 (@PrePersist)
- Spring Data JPA의 메서드 쿼리 (findByEmail)

**MyBatis 사용 케이스 (BizSync):**
- ProjectBoardDTO 조회: Project → KanbanColumn → Task를 한 번의 쿼리로 조인
- 복잡한 통계 쿼리나 집계 함수 활용
- 동적 검색 조건이 많은 경우
- 레거시 DB 스키마와의 호환성

ProjectMapper.selectProjectBoard()는 프로젝트, 컬럼, 업무를 LEFT JOIN으로 한 번에 조회하고, MyBatis의 중첩 ResultMap으로 계층적 DTO를 구성합니다. 이를 JPA로 구현하려면 N+1 문제가 발생하거나, Fetch Join + DTO 변환 로직이 복잡해집니다.

하이브리드 방식의 주의사항은 JPA의 1차 캐시와 MyBatis의 직접 쿼리가 충돌할 수 있다는 점입니다. MyBatis로 데이터를 변경한 후 JPA로 조회하면 캐시된 옛 데이터를 가져올 수 있으므로, 필요시 EntityManager.flush()나 clear()를 사용해야 합니다.

## 코드 예시 (필요시)
```java
// JPA 방식 - 단순 CRUD와 객체 중심 로직
@Service
public class ProjectService {
    private final ProjectRepository projectRepository;  // JpaRepository
    
    @Transactional
    public void completeProject(Long projectId) {
        Project project = projectRepository.findById(projectId)
            .orElseThrow(() -> new IllegalArgumentException("프로젝트 없음"));
        
        project.complete();  // Dirty Checking으로 자동 UPDATE
    }
}

// MyBatis 방식 - 복잡한 조인과 계층적 매핑
@Mapper
public interface ProjectMapper {
    Optional<ProjectBoardDTO> selectProjectBoard(@Param("projectId") Long projectId);
}

// MyBatis XML - 복잡한 ResultMap
<resultMap id="ProjectBoardMap" type="ProjectBoardDTO">
    <id property="projectId" column="project_id"/>
    <result property="name" column="project_name"/>
    
    <collection property="columns" ofType="KanbanColumnDTO">
        <id property="columnId" column="column_id"/>
        <result property="name" column="column_name"/>
        
        <collection property="tasks" ofType="TaskDTO">
            <id property="taskId" column="task_id"/>
            <result property="title" column="task_title"/>
        </collection>
    </collection>
</resultMap>

<select id="selectProjectBoard" resultMap="ProjectBoardMap">
    SELECT p.project_id, p.name AS project_name,
           c.column_id, c.name AS column_name,
           t.task_id, t.title AS task_title
    FROM project p
    LEFT JOIN kanban_column c ON p.project_id = c.project_id
    LEFT JOIN task t ON c.column_id = t.column_id
    WHERE p.project_id = #{projectId}
    ORDER BY c.sequence, t.sequence
</select>
```

## 꼬리 질문 예상
- JPA로 동일한 쿼리를 작성한다면 어떻게 최적화할 수 있나요? (@EntityGraph, Fetch Join)
- MyBatis만 사용하지 않고 JPA를 함께 사용하는 이유는 무엇인가요?
- 트랜잭션 내에서 JPA와 MyBatis를 함께 사용할 때 주의사항은 무엇인가요?

## 참고
- [[JPA vs MyBatis 비교]]
- [[하이브리드 ORM 전략]]

---

## 질문 2
> JPA의 Dirty Checking 메커니즘과 BizSync의 Project 엔티티에서 이를 활용한 update() 메서드를 설명해주세요.

## 핵심 답변 (3줄)
1. Dirty Checking은 영속 상태의 엔티티가 변경되면 트랜잭션 커밋 시점에 자동으로 UPDATE 쿼리를 실행하는 JPA의 기능입니다
2. 1차 캐시의 스냅샷과 현재 엔티티를 비교하여 변경된 필드만 감지하므로, 명시적인 update() 호출 없이도 DB에 반영됩니다
3. BizSync는 편의 메서드(project.update())로 엔티티를 변경하면 자동으로 UPDATE가 실행되어 코드가 간결해집니다

## 상세 설명
JPA의 영속성 컨텍스트는 엔티티를 관리할 때 최초 조회 시점의 상태를 스냅샷으로 저장합니다. 트랜잭션이 커밋될 때 JPA는 현재 엔티티와 스냅샷을 비교(Dirty Check)하여 변경사항이 있으면 UPDATE 쿼리를 자동 생성합니다.

**Dirty Checking의 동작 과정:**
1. 엔티티를 영속성 컨텍스트에 로딩 (SELECT)
2. 최초 상태를 스냅샷으로 저장
3. 비즈니스 로직에서 엔티티의 필드 변경 (setter 또는 편의 메서드)
4. 트랜잭션 커밋 전 flush() 호출 시 변경 감지
5. 변경된 필드만 포함된 UPDATE 쿼리 자동 생성 및 실행

BizSync의 Project 엔티티는 update() 편의 메서드를 제공하여 불변성을 보장하면서도 Dirty Checking을 활용합니다. @Setter 대신 명시적인 메서드로 변경 지점을 명확히 하고, null 체크 로직을 중앙화합니다.

ProjectService.updateProject()는 @Transactional 내에서 project.update()를 호출하면, 메서드 종료 시 자동으로 UPDATE 쿼리가 실행됩니다. 개발자가 명시적으로 save()를 호출할 필요가 없어 코드가 간결해집니다.

주의할 점은 Dirty Checking은 영속 상태의 엔티티에만 작동한다는 것입니다. new로 생성한 객체나 detached 상태의 엔티티는 변경을 감지하지 못합니다.

## 코드 예시 (필요시)
```java
// Project.java - 편의 메서드
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Project {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long projectId;
    
    private String name;
    private String description;
    // ... 기타 필드
    
    /**
     * 프로젝트 정보 수정 (Dirty Checking 활용)
     */
    public void update(String name, String description, 
                      LocalDate startDate, LocalDate endDate, 
                      BigDecimal totalBudget) {
        if (name != null && !name.isBlank()) {
            this.name = name;  // 필드 변경
        }
        if (description != null) {
            this.description = description;
        }
        if (startDate != null) {
            this.startDate = startDate;
        }
        // ... 나머지 필드 업데이트
    }
}

// ProjectService.java - Dirty Checking 활용
@Service
@RequiredArgsConstructor
@Transactional
public class ProjectService {
    
    private final ProjectRepository projectRepository;
    
    @RequireProjectLeader
    public void updateProject(Long projectId, ProjectUpdateRequestDTO dto) {
        // 1. 엔티티 조회 (영속 상태로 로딩)
        Project project = projectRepository.findById(projectId)
            .orElseThrow(() -> new IllegalArgumentException("프로젝트 없음"));
        
        // 2. 엔티티 변경 (편의 메서드 호출)
        project.update(dto.name(), dto.description(), 
                      dto.startDate(), dto.endDate(), dto.totalBudget());
        
        // 3. save() 호출 불필요! 트랜잭션 커밋 시 자동 UPDATE
    }
}

// 실행되는 SQL (변경된 필드만 포함)
// UPDATE project 
// SET name = ?, description = ?, start_date = ?, end_date = ?, total_budget = ? 
// WHERE project_id = ?
```

## 꼬리 질문 예상
- @DynamicUpdate를 사용하면 어떤 차이가 있나요?
- Dirty Checking과 merge()의 차이는 무엇인가요?
- @Transactional(readOnly = true)에서 엔티티를 변경하면 어떻게 되나요?

## 참고
- [[JPA 영속성 컨텍스트]]
- [[Dirty Checking vs Save]]

---

## 질문 3
> MyBatis의 중첩 ResultMap에서 collection 태그를 사용한 일대다 매핑과 N+1 문제 회피 방법을 설명해주세요.

## 핵심 답변 (3줄)
1. MyBatis의 `<collection>`은 일대다 관계를 한 번의 쿼리로 조회하여 부모 객체에 자식 컬렉션을 매핑하는 기능입니다
2. LEFT JOIN으로 데이터를 한 번에 가져오고, resultMap의 id 태그로 부모-자식을 구분하여 중복 제거와 계층 구조를 생성합니다
3. JPA의 지연 로딩에서 발생하는 N+1 문제를 원천적으로 방지하며, 단일 쿼리로 복잡한 객체 그래프를 효율적으로 구성합니다

## 상세 설명
BizSync의 ProjectMapper.selectProjectBoard()는 프로젝트, 칸반 컬럼, 업무를 한 번의 쿼리로 조회합니다. Project는 여러 KanbanColumn을 가지고, 각 KanbanColumn은 여러 Task를 가지는 이중 일대다 관계입니다.

**ResultMap의 collection 동작 원리:**

1. LEFT JOIN으로 모든 행을 FLAT하게 조회
2. `<id>` 태그로 각 엔티티의 고유 식별자 지정
3. 같은 project_id를 가진 행들을 하나의 Project 객체로 그룹화
4. 각 Project 내에서 column_id로 KanbanColumn 그룹화
5. 각 KanbanColumn 내에서 task_id로 Task 그룹화

이 방식은 JPA의 Fetch Join과 유사하지만, DTO로 직접 매핑할 때 MyBatis가 더 간결합니다. JPA는 엔티티를 조회한 후 DTO로 변환하는 추가 과정이 필요하지만, MyBatis는 쿼리 결과를 바로 DTO로 매핑합니다.

**N+1 문제 회피:**
만약 JPA로 Project를 조회한 후 getColumns()를 호출하면 지연 로딩으로 인해 컬럼 개수만큼 추가 쿼리가 발생합니다(N+1). MyBatis는 애초에 JOIN으로 한 번에 가져오므로 이 문제가 없습니다.

다만 collection이 많으면 카테시안 곱으로 인해 결과 행 수가 폭발적으로 증가할 수 있습니다. 예를 들어 프로젝트 1개, 컬럼 3개, 각 컬럼에 Task 10개면 30행이 반환됩니다. 이를 고려하여 적절한 페이징이나 분리 조회 전략이 필요할 수 있습니다.

## 코드 예시 (필요시)
```xml
<!-- ProjectMapper.xml -->
<resultMap id="ProjectBoardMap" type="ProjectBoardDTO">
    <!-- 부모 엔티티 매핑 -->
    <id property="projectId" column="project_id"/>  <!-- 중요: 고유 식별자 -->
    <result property="name" column="project_name"/>
    <result property="totalBudget" column="total_budget"/>
    
    <!-- 일대다 컬렉션 매핑 (Project → KanbanColumn) -->
    <collection property="columns" 
                ofType="KanbanColumnDTO"
                javaType="java.util.ArrayList">
        <id property="columnId" column="column_id"/>  <!-- 컬럼 식별자 -->
        <result property="name" column="column_name"/>
        <result property="sequence" column="column_seq"/>
        
        <!-- 중첩 일대다 컬렉션 매핑 (KanbanColumn → Task) -->
        <collection property="tasks" 
                    ofType="TaskDTO"
                    javaType="java.util.ArrayList">
            <id property="taskId" column="task_id"/>  <!-- Task 식별자 -->
            <result property="title" column="task_title"/>
            <result property="sequence" column="task_seq"/>
            <result property="workerName" column="worker_name"/>
        </collection>
    </collection>
</resultMap>

<select id="selectProjectBoard" resultMap="ProjectBoardMap">
    SELECT p.project_id,
           p.name AS project_name,
           p.total_budget,
           
           c.column_id,
           c.name AS column_name,
           c.sequence AS column_seq,
           
           t.task_id,
           t.title AS task_title,
           t.sequence AS task_seq,
           u.name AS worker_name
           
    FROM project p
    LEFT JOIN kanban_column c ON p.project_id = c.project_id
    LEFT JOIN task t ON c.column_id = t.column_id
    LEFT JOIN users u ON t.worker_id = u.user_id
    
    WHERE p.project_id = #{projectId}
    ORDER BY c.sequence ASC, t.sequence ASC
</select>

<!-- 반환 구조 -->
<!-- 
ProjectBoardDTO {
    projectId: 1,
    name: "BizSync 프로젝트",
    columns: [
        KanbanColumnDTO {
            columnId: 10,
            name: "To Do",
            tasks: [
                TaskDTO { taskId: 100, title: "회원가입 구현" },
                TaskDTO { taskId: 101, title: "로그인 구현" }
            ]
        },
        KanbanColumnDTO {
            columnId: 11,
            name: "In Progress",
            tasks: [ ... ]
        }
    ]
}
-->
```

## 꼬리 질문 예상
- JPA의 @EntityGraph와 MyBatis의 collection 중 어떤 것이 더 효율적인가요?
- 카테시안 곱 문제를 해결하기 위한 전략은 무엇인가요? (분리 쿼리, 페이징 등)
- MyBatis의 lazy loading과 JPA의 지연 로딩의 차이는 무엇인가요?

## 참고
- [[MyBatis ResultMap 심화]]
- [[N+1 문제 해결 전략]]

---

## 질문 4
> @PrePersist와 @Builder.Default를 함께 사용할 때 발생할 수 있는 문제와 BizSync의 Project 엔티티에서 기본값 설정 전략을 설명해주세요.

## 핵심 답변 (3줄)
1. @Builder.Default는 빌더 패턴 사용 시 기본값을 설정하지만, 엔티티 저장 전에 적용되므로 null 체크 로직이 중복될 수 있습니다
2. @PrePersist는 엔티티가 영속화되기 직전에 실행되는 JPA 생명주기 콜백으로, DB 저장 직전 최종 검증과 기본값 설정에 사용됩니다
3. BizSync는 usedBudget과 status에 대해 두 방법을 모두 사용하여 빌더와 직접 생성 모두에서 기본값을 보장합니다

## 상세 설명
Lombok의 @Builder는 편리하지만 기본값 설정이 까다롭습니다. @Builder.Default를 사용하면 빌더로 객체를 생성할 때만 기본값이 적용되고, new Project()처럼 직접 생성하면 적용되지 않습니다.

@PrePersist는 JPA 엔티티가 persist() 호출로 영속성 컨텍스트에 들어가기 직전에 실행되는 콜백입니다. 이 시점에서 기본값을 설정하면 생성 방식과 무관하게 항상 동일한 초기화 로직을 보장할 수 있습니다.

**BizSync의 전략:**
```java
@Builder.Default
private ProjectStatus status = ProjectStatus.IN_PROGRESS;

@PrePersist
public void prePersist() {
    if (this.usedBudget == null)
        this.usedBudget = BigDecimal.ZERO;
    if (this.status == null)
        this.status = ProjectStatus.IN_PROGRESS;
}
```

이 코드는 방어적 프로그래밍입니다. @Builder.Default가 있어도 @PrePersist에서 한 번 더 확인합니다. 이유는:
1. 직접 생성 시 안전성 보장
2. Reflection 등으로 우회 생성 시 대비
3. 명시적인 null 설정 방지

createdAt은 @PrePersist에서만 설정합니다. 이는 항상 시스템이 결정해야 하는 값이므로 개발자가 빌더로 설정할 수 없게 합니다.

단점은 @Builder.Default와 @PrePersist의 로직이 중복되어 유지보수 포인트가 늘어난다는 것입니다. 팀 컨벤션에 따라 한 가지 방법만 사용하는 것도 좋습니다.

## 코드 예시 (필요시)
```java
@Entity
@Table(name = "project")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Builder
public class Project {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long projectId;
    
    @Column(nullable = false)
    private String name;
    
    // 예산: Builder와 PrePersist 모두에서 기본값 설정
    @Column(name = "used_budget", precision = 19, scale = 2)
    @Builder.Default  // 빌더 사용 시 기본값
    private BigDecimal usedBudget = BigDecimal.ZERO;
    
    // 상태: Builder와 PrePersist 모두에서 기본값 설정
    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    @Builder.Default  // 빌더 사용 시 기본값
    private ProjectStatus status = ProjectStatus.IN_PROGRESS;
    
    // 생성 시각: 시스템이 자동 설정, Builder로 설정 불가
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
    
    /**
     * JPA 생명주기 콜백: 영속화 직전 실행
     */
    @PrePersist
    public void prePersist() {
        this.createdAt = LocalDateTime.now();  // 항상 시스템 시간
        
        // 방어적 프로그래밍: Builder 우회 시 대비
        if (this.usedBudget == null)
            this.usedBudget = BigDecimal.ZERO;
        if (this.status == null)
            this.status = ProjectStatus.IN_PROGRESS;
    }
}

// 사용 예시 1: Builder 사용 (Default 적용)
Project project1 = Project.builder()
    .name("BizSync")
    .totalBudget(new BigDecimal("10000000"))
    // usedBudget, status 미설정 → @Builder.Default 적용
    .build();
// → usedBudget = 0, status = IN_PROGRESS

// 사용 예시 2: 직접 생성 (Default 미적용)
Project project2 = new Project();
project2.setName("BizSync");
// → usedBudget = null, status = null
// → @PrePersist에서 기본값 설정

// 사용 예시 3: Builder로 명시적 null 설정
Project project3 = Project.builder()
    .name("BizSync")
    .usedBudget(null)  // 명시적으로 null
    .build();
// → @PrePersist에서 BigDecimal.ZERO로 변경
```

## 꼬리 질문 예상
- @PrePersist 외에 다른 JPA 생명주기 콜백은 어떤 것들이 있나요?
- @PostLoad와 @PostPersist의 차이는 무엇인가요?
- 기본값 설정을 DB 레벨(DEFAULT)과 애플리케이션 레벨 중 어디서 하는 것이 좋나요?

## 참고
- [[JPA 엔티티 생명주기]]
- [[Lombok Builder 패턴]]

---

## 질문 5
> ProjectService에서 프로젝트 삭제 시 연관 데이터를 수동으로 삭제하는 이유와 JPA Cascade 옵션을 사용하지 않은 이유를 설명해주세요.

## 핵심 답변 (3줄)
1. JPA의 CascadeType.REMOVE는 연관된 엔티티를 자동 삭제하지만, 복잡한 연관관계에서는 삭제 순서와 제약 조건 위반 문제가 발생할 수 있습니다
2. BizSync는 Task → KanbanColumn → ProjectMember → ApprovalDocument → Project 순서로 명시적 삭제를 수행하여 외래키 제약 조건을 만족시킵니다
3. 명시적 삭제는 코드가 길지만 삭제 로직이 명확하고, 디버깅과 로깅이 쉬우며, 예상치 못한 Cascade 전파를 방지합니다

## 상세 설명
JPA의 Cascade 옵션은 부모 엔티티의 상태 변화를 자식 엔티티에 전파하는 기능입니다. CascadeType.REMOVE를 설정하면 부모를 삭제할 때 자식도 자동 삭제됩니다.

**Cascade를 사용하지 않는 이유:**

1. **복잡한 연관관계**: BizSync는 Project가 KanbanColumn, ProjectMember, ApprovalDocument 등 여러 엔티티와 연관됩니다. Cascade를 사용하면 모든 연관관계에 설정해야 하고, 의도치 않은 삭제가 발생할 수 있습니다.

2. **외래키 제약 조건**: Task는 KanbanColumn을 참조하므로, Column을 먼저 삭제하면 제약 위반입니다. 명시적 순서 제어가 필요합니다.

3. **명확성과 안전성**: 삭제는 복구 불가능한 작업이므로, 각 단계를 명시적으로 작성하여 실수를 방지합니다.

4. **성능**: Cascade는 각 엔티티를 영속성 컨텍스트에 로딩한 후 하나씩 DELETE 쿼리를 실행합니다. 반면 명시적 삭제는 Bulk DELETE로 최적화할 수 있습니다.

**BizSync의 삭제 순서:**
```
1. Task 삭제 (외래키: column_id)
2. KanbanColumn 삭제 (외래키: project_id)
3. ProjectMember 삭제 (외래키: project_id)
4. ApprovalDocument 삭제 (외래키: project_id)
5. Project 삭제 (부모)
```

이 순서를 지키지 않으면 "Cannot delete or update a parent row: a foreign key constraint fails" 에러가 발생합니다.

대안으로 DB 레벨에서 ON DELETE CASCADE를 설정할 수도 있지만, 이는 애플리케이션 로직이 DB에 종속되고, 삭제 로그를 남기기 어렵다는 단점이 있습니다.

## 코드 예시 (필요시)
```java
// ProjectService.java - 명시적 삭제
@RequireProjectLeader
@Transactional
public void deleteProject(Long projectId) {
    // 1. 프로젝트 존재 여부 확인
    if (!projectRepository.existsById(projectId)) {
        throw new IllegalArgumentException("프로젝트를 찾을 수 없습니다.");
    }
    
    // 2. 연관된 데이터 삭제 (순서 중요!)
    // 2-1. Task 먼저 삭제 (외래키: column_id)
    taskRepository.deleteByColumn_Project_ProjectId(projectId);
    
    // 2-2. KanbanColumn 삭제 (외래키: project_id)
    List<KanbanColumn> columns = kanbanColumnRepository
        .findByProject_ProjectId(projectId);
    kanbanColumnRepository.deleteAll(columns);
    
    // 2-3. ProjectMember 삭제 (외래키: project_id)
    List<ProjectMember> members = projectMemberRepository
        .findAllByProject_ProjectId(projectId);
    projectMemberRepository.deleteAll(members);
    
    // 2-4. ApprovalDocument 삭제 (외래키: project_id)
    List<ApprovalDocument> approvalDocs = approvalDocumentRepository
        .findByProject_ProjectId(projectId);
    approvalDocumentRepository.deleteAll(approvalDocs);
    
    // 3. 마지막으로 프로젝트 삭제
    projectRepository.deleteById(projectId);
}

// Cascade를 사용한다면 (권장하지 않음)
@Entity
public class Project {
    
    @OneToMany(mappedBy = "project", 
               cascade = CascadeType.REMOVE,  // 자동 삭제
               orphanRemoval = true)
    private List<KanbanColumn> columns = new ArrayList<>();
    
    @OneToMany(mappedBy = "project", 
               cascade = CascadeType.REMOVE)
    private List<ProjectMember> members = new ArrayList<>();
}

// Cascade 사용 시 삭제
@Transactional
public void deleteProject(Long projectId) {
    Project project = projectRepository.findById(projectId)
        .orElseThrow();
    
    projectRepository.delete(project);  // 연관 엔티티 자동 삭제
    // 문제: Task와 Column 삭제 순서 보장 안 됨
}
```

## 꼬리 질문 예상
- orphanRemoval과 CascadeType.REMOVE의 차이는 무엇인가요?
- @OnDelete(action = OnDeleteAction.CASCADE)는 언제 사용하나요?
- Bulk DELETE (@Query + @Modifying)를 사용하면 성능이 더 좋지 않나요?

## 참고
- [[JPA Cascade 옵션]]
- [[외래키 제약 조건과 삭제 순서]]

---

## 질문 6
> @Enumerated(EnumType.STRING)을 사용하는 이유와 EnumType.ORDINAL의 문제점을 설명해주세요.

## 핵심 답변 (3줄)
1. EnumType.ORDINAL은 Enum의 순서(0, 1, 2...)를 DB에 저장하여 공간 효율적이지만, Enum 순서가 변경되면 데이터 무결성이 깨집니다
2. EnumType.STRING은 Enum의 이름 문자열을 저장하여 가독성이 높고, 중간에 값을 추가하거나 순서를 변경해도 안전합니다
3. BizSync는 ProjectStatus와 ApprovalStatus에 STRING 타입을 사용하여 유지보수성과 안정성을 확보했습니다

## 상세 설명
JPA에서 Enum을 매핑하는 방법은 두 가지입니다:

**EnumType.ORDINAL (기본값, 권장하지 않음):**
```java
enum ProjectStatus {
    IN_PROGRESS,  // 0
    COMPLETED,    // 1
    ON_HOLD       // 2
}
```
DB에 0, 1, 2로 저장됩니다. 문제는 나중에 CANCELLED을 IN_PROGRESS 앞에 추가하면:
```java
enum ProjectStatus {
    CANCELLED,    // 0 (변경!)
    IN_PROGRESS,  // 1 (변경!)
    COMPLETED,    // 2 (변경!)
    ON_HOLD       // 3 (변경!)
}
```
기존 DB의 0(IN_PROGRESS)이 CANCELLED로 잘못 해석됩니다.

**EnumType.STRING (권장):**
```java
@Enumerated(EnumType.STRING)
@Column(name = "status", nullable = false, length = 20)
private ProjectStatus status;
```
DB에 "IN_PROGRESS", "COMPLETED", "ON_HOLD"로 저장됩니다. 중간에 값을 추가하거나 순서를 바꿔도 영향이 없습니다.

**단점과 고려사항:**
1. 저장 공간이 더 필요 (INT vs VARCHAR)
2. Enum 이름 자체를 변경하면 문제 발생 (예: IN_PROGRESS → ACTIVE)
3. 대소문자 민감성 (DB collation 설정 주의)

BizSync는 비즈니스 로직의 명확성과 안정성을 우선시하여 STRING 타입을 선택했습니다. 스토리지 비용보다 데이터 무결성이 더 중요하기 때문입니다.

추가로 columnDefinition으로 VARCHAR 길이를 명시하여 DB 스키마를 명확히 했습니다.

## 코드 예시 (필요시)
```java
// ProjectStatus.java - Enum 정의
public enum ProjectStatus {
    IN_PROGRESS("진행중"),
    COMPLETED("완료"),
    ON_HOLD("보류"),
    CANCELLED("취소");
    
    private final String korean;
    
    ProjectStatus(String korean) {
        this.korean = korean;
    }
    
    public String getKorean() {
        return korean;
    }
}

// Project.java - STRING 타입으로 매핑
@Entity
public class Project {
    
    @Enumerated(EnumType.STRING)  // 문자열로 저장
    @Column(name = "status", nullable = false, 
            length = 20,  // VARCHAR(20)
            columnDefinition = "VARCHAR(20) DEFAULT 'IN_PROGRESS'")
    @Builder.Default
    private ProjectStatus status = ProjectStatus.IN_PROGRESS;
}

// DB 테이블 스키마
// CREATE TABLE project (
//     ...
//     status VARCHAR(20) NOT NULL DEFAULT 'IN_PROGRESS',
//     ...
// );

// DB에 저장된 실제 데이터
// | project_id | name      | status       |
// |------------|-----------|--------------|
// | 1          | BizSync   | IN_PROGRESS  |
// | 2          | Old Proj  | COMPLETED    |
// | 3          | New Proj  | ON_HOLD      |

// ORDINAL 사용 시 문제 (권장하지 않음)
@Enumerated(EnumType.ORDINAL)  // 0, 1, 2로 저장
private ProjectStatus status;

// DB에 저장된 데이터
// | project_id | status |
// |------------|--------|
// | 1          | 0      |  <- IN_PROGRESS
// | 2          | 1      |  <- COMPLETED

// Enum 순서 변경 시
enum ProjectStatus {
    CANCELLED,    // 0 (새로 추가)
    IN_PROGRESS,  // 1 (변경됨!)
    COMPLETED,    // 2 (변경됨!)
}
// → 기존 데이터 0이 CANCELLED로 잘못 해석됨!
```

## 꼬리 질문 예상
- Enum 이름을 변경해야 한다면 어떻게 마이그레이션하나요?
- @Converter를 사용한 커스텀 Enum 매핑은 언제 필요한가요?
- Enum에 메서드를 추가하여 비즈니스 로직을 캡슐화하는 패턴은 무엇인가요?

## 참고
- [[JPA Enum 매핑 전략]]
- [[Enum 활용 패턴]]

---

## 질문 7
> BigDecimal을 사용한 금액 처리와 spendBudget() 메서드의 예산 초과 검증 로직을 설명해주세요.

## 핵심 답변 (3줄)
1. BigDecimal은 부동소수점 오차가 없는 정확한 십진수 연산을 제공하여 금액 계산에 필수적입니다 (double은 0.1을 정확히 표현 못함)
2. BizSync는 totalBudget과 usedBudget을 BigDecimal로 관리하며, spendBudget()에서 compareTo()로 안전하게 비교합니다
3. 예산 초과 시 예외를 던져 비즈니스 규칙을 강제하고, 트랜잭션 롤백으로 데이터 일관성을 보장합니다

## 상세 설명
금융 시스템이나 회계 시스템에서는 절대 double이나 float를 사용해서는 안 됩니다. 이진 부동소수점 방식은 0.1, 0.2 같은 십진수를 정확히 표현할 수 없어 반복 연산 시 오차가 누적됩니다.

**double의 문제:**
```java
double budget = 0.1;
double spent = 0.2;
double remaining = 0.3 - spent - budget;
System.out.println(remaining);  // 0.0이 아닌 5.551115123125783E-17
```

**BigDecimal의 장점:**
```java
BigDecimal budget = new BigDecimal("0.1");
BigDecimal spent = new BigDecimal("0.2");
BigDecimal remaining = new BigDecimal("0.3").subtract(spent).subtract(budget);
System.out.println(remaining);  // 정확히 0.0
```

BizSync의 spendBudget() 메서드는 예산을 사용할 때 안전성을 보장합니다:

1. **불변성 유지**: BigDecimal은 불변 객체이므로 add()는 새 객체를 반환합니다
2. **정확한 비교**: compareTo()로 크기 비교 (==는 객체 참조 비교이므로 사용 불가)
3. **비즈니스 규칙 강제**: 예산 초과 시 IllegalStateException 발생
4. **트랜잭션 보호**: @Transactional 내에서 예외 발생 시 롤백

DB 컬럼 정의에서 `precision = 19, scale = 2`는 최대 19자리 숫자에 소수점 이하 2자리를 의미합니다. 예: 99999999999999999.99 (약 1경까지)

## 코드 예시 (필요시)
```java
// Project.java
@Entity
public class Project {
    
    @Column(name = "total_budget", precision = 19, scale = 2)
    private BigDecimal totalBudget;  // 총 예산
    
    @Column(name = "used_budget", precision = 19, scale = 2)
    private BigDecimal usedBudget;   // 사용 예산
    
    /**
     * 예산 사용 메서드 (비즈니스 로직)
     */
    public void spendBudget(BigDecimal amount) {
        // 1. 사용 후 총액 계산 (BigDecimal은 불변이므로 새 객체 반환)
        BigDecimal expectedUsage = this.usedBudget.add(amount);
        
        // 2. 예산 초과 검증
        if (this.totalBudget.compareTo(expectedUsage) < 0) {
            throw new IllegalStateException("예산이 초과되었습니다.");
        }
        
        // 3. 예산 차감
        this.usedBudget = expectedUsage;
    }
    
    /**
     * 잔여 예산 계산
     */
    public BigDecimal getRemainingBudget() {
        return this.totalBudget.subtract(this.usedBudget);
    }
}

// ApprovalService.java - 사용 예시
@Transactional
public void approveExpense(Long projectId, BigDecimal amount) {
    Project project = projectRepository.findById(projectId)
        .orElseThrow();
    
    try {
        project.spendBudget(amount);  // 예산 사용
        // 예산 차감 성공 → 결재 승인 로직
    } catch (IllegalStateException e) {
        // 예산 초과 → 결재 거부
        throw new IllegalArgumentException("예산 부족으로 결재를 거부합니다.");
    }
}

// BigDecimal 사용 시 주의사항
// 1. 생성자: new BigDecimal(0.1) → 부정확
//           new BigDecimal("0.1") → 정확 (문자열 사용)
BigDecimal wrong = new BigDecimal(0.1);  // 0.1000000000000000055511...
BigDecimal correct = new BigDecimal("0.1");  // 정확히 0.1

// 2. 비교: equals() vs compareTo()
BigDecimal a = new BigDecimal("10.0");
BigDecimal b = new BigDecimal("10.00");
a.equals(b);      // false (scale이 다름)
a.compareTo(b);   // 0 (값은 같음, 권장)

// 3. 연산: 불변 객체이므로 메서드 체이닝
BigDecimal result = amount
    .add(tax)
    .subtract(discount)
    .multiply(quantity)
    .divide(exchangeRate, 2, RoundingMode.HALF_UP);
```

## 꼬리 질문 예상
- scale과 precision의 차이는 무엇이며, 각각 어떻게 설정해야 하나요?
- RoundingMode의 종류와 금융 시스템에서 권장되는 모드는 무엇인가요?
- Money 패턴(Value Object)을 적용한다면 어떻게 설계하시겠습니까?

## 참고
- [[BigDecimal 완벽 가이드]]
- [[금융 시스템 설계 패턴]]

---

## 질문 8
> Spring Data JPA의 메서드 쿼리(Query Method)와 BizSync에서 사용된 복잡한 메서드명 생성 규칙을 설명해주세요.

## 핵심 답변 (3줄)
1. Spring Data JPA는 메서드 이름을 분석하여 자동으로 JPQL 쿼리를 생성하는 기능으로, 간단한 조회 로직을 SQL 없이 구현할 수 있습니다
2. findBy, existsBy, deleteBy 등의 키워드와 엔티티 필드명을 조합하여 쿼리를 표현하며, And, Or, Between 등으로 복잡한 조건도 가능합니다
3. BizSync는 findByProject_ProjectIdAndUser_UserId처럼 연관 엔티티를 언더스코어로 탐색하여 조인 조건을 명시합니다

## 상세 설명
Spring Data JPA의 메서드 쿼리는 메서드 이름 규칙에 따라 쿼리를 자동 생성합니다. 개발자는 인터페이스에 메서드만 선언하면 됩니다.

**메서드 쿼리 구조:**
```
[동작키워드][By][필드명][조건][And/Or][필드명][조건]...
```

**BizSync 사용 예시:**

1. `findByEmail(String email)` → WHERE u.email = ?
2. `existsByProject_ProjectIdAndUser_UserId(Long projectId, Long userId)`
   → JOIN 후 존재 여부 확인
3. `deleteByColumn_Project_ProjectId(Long projectId)`
   → Task의 column을 통해 project까지 탐색

**연관 엔티티 탐색:**
언더스코어(_)는 연관관계를 따라가는 문법입니다:
- `Project_ProjectId`: ProjectMember의 project 필드 → Project 엔티티의 projectId
- `Column_Project_ProjectId`: Task의 column → KanbanColumn의 project → Project의 projectId

이는 다음 JPQL로 변환됩니다:
```sql
SELECT t FROM Task t 
WHERE t.column.project.projectId = :projectId
```

**장점:**
- SQL 작성 불필요
- 컴파일 타임 에러 검출 (오타 시 에러)
- 가독성 좋음

**단점:**
- 메서드명이 매우 길어질 수 있음
- 복잡한 쿼리는 표현 불가 (→ @Query 사용)
- 동적 쿼리 작성 어려움 (→ Specification 사용)

BizSync는 간단한 조회는 메서드 쿼리로, 복잡한 조회는 MyBatis로 분리하여 각각의 장점을 활용합니다.

## 코드 예시 (필요시)
```java
// ProjectMemberRepository.java
public interface ProjectMemberRepository 
    extends JpaRepository<ProjectMember, Long> {
    
    // 1. 단순 조회 (project의 projectId로 필터링)
    List<ProjectMember> findAllByProject_ProjectId(Long projectId);
    // → SELECT pm FROM ProjectMember pm 
    //    WHERE pm.project.projectId = :projectId
    
    // 2. 복합 조건 (AND)
    Optional<ProjectMember> findByProject_ProjectIdAndUser_UserId(
        Long projectId, Long userId);
    // → SELECT pm FROM ProjectMember pm 
    //    WHERE pm.project.projectId = :projectId 
    //    AND pm.user.userId = :userId
    
    // 3. 존재 여부 확인
    boolean existsByProject_ProjectIdAndUser_UserId(
        Long projectId, Long userId);
    // → SELECT COUNT(pm) > 0 FROM ProjectMember pm 
    //    WHERE pm.project.projectId = :projectId 
    //    AND pm.user.userId = :userId
}

// TaskRepository.java
public interface TaskRepository extends JpaRepository<Task, Long> {
    
    // 4. 중첩 연관관계 탐색 (Task → Column → Project)
    void deleteByColumn_Project_ProjectId(Long projectId);
    // → DELETE FROM Task t 
    //    WHERE t.column.project.projectId = :projectId
    
    // 5. 최댓값 조회 (컬럼별 최대 sequence)
    @Query("SELECT COALESCE(MAX(t.sequence), 0) FROM Task t " +
           "WHERE t.column.columnId = :columnId")
    int findMaxSequence(@Param("columnId") Long columnId);
}

// UserRepository.java
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 6. Optional 반환 (없으면 빈 Optional)
    Optional<User> findByEmail(String email);
    // → SELECT u FROM User u WHERE u.email = :email
}

// 복잡한 메서드 쿼리 예시 (가능하지만 권장하지 않음)
List<Project> findByNameContainingAndStatusAndStartDateBetween(
    String name, ProjectStatus status, 
    LocalDate start, LocalDate end);
// → WHERE name LIKE %:name% 
//    AND status = :status 
//    AND startDate BETWEEN :start AND :end

// 위처럼 복잡한 경우 @Query 사용 권장
@Query("SELECT p FROM Project p " +
       "WHERE p.name LIKE %:name% " +
       "AND p.status = :status " +
       "AND p.startDate BETWEEN :start AND :end")
List<Project> searchProjects(@Param("name") String name, ...);
```

## 꼬리 질문 예상
- 메서드 쿼리로 Left Join과 Inner Join을 구분할 수 있나요?
- 메서드 쿼리의 성능은 @Query와 차이가 있나요?
- Specification 패턴은 언제 사용하며, 메서드 쿼리와 어떻게 다른가요?

## 참고
- [[Spring Data JPA Query Methods]]
- [[JPA 동적 쿼리 전략]]

---

## 질문 9
> @Transactional(readOnly = true)의 의미와 성능 최적화 효과, 그리고 쓰기 작업 시 발생하는 문제를 설명해주세요.

## 핵심 답변 (3줄)
1. readOnly = true는 트랜잭션을 읽기 전용으로 표시하여 Dirty Checking을 비활성화하고, DB 커넥션을 읽기 전용 모드로 설정하여 성능을 향상시킵니다
2. Hibernate는 스냅샷 저장을 생략하고, flush를 호출하지 않으며, DB는 읽기 최적화 경로를 사용할 수 있습니다
3. readOnly 트랜잭션 내에서 엔티티를 변경해도 UPDATE 쿼리가 실행되지 않으며, 의도치 않은 쓰기를 방지하는 안전 장치 역할을 합니다

## 상세 설명
Spring의 @Transactional에 readOnly = true를 설정하면 여러 레벨에서 최적화가 적용됩니다.

**최적화 효과:**

1. **JPA 레벨**:
   - 영속성 컨텍스트가 엔티티의 스냅샷을 저장하지 않음
   - Dirty Checking을 수행하지 않음 (flush 생략)
   - 메모리 사용량 감소

2. **JDBC 레벨**:
   - Connection.setReadOnly(true) 호출
   - DB에게 읽기 전용임을 알림

3. **DB 레벨** (DB마다 다름):
   - Master-Slave 구조에서 Slave로 라우팅
   - 읽기 최적화 실행 계획 사용
   - 잠금(Lock) 최소화

**BizSync 사용 예시:**
```java
// 읽기 전용 메서드
@Transactional(readOnly = true)
public ProjectBoardDTO getProjectBoard(Long projectId) {
    return projectMapper.selectProjectBoard(projectId)
        .orElseThrow();
}

// 쓰기 메서드 (readOnly 미설정, 기본값 false)
@Transactional
public void updateProject(Long projectId, ProjectUpdateRequestDTO dto) {
    Project project = projectRepository.findById(projectId)
        .orElseThrow();
    project.update(...);  // UPDATE 쿼리 실행
}
```

**주의사항:**
readOnly = true 트랜잭션에서 엔티티를 변경해도 예외가 발생하지 않습니다. 단지 flush가 호출되지 않아 DB에 반영되지 않을 뿐입니다. 이는 버그의 원인이 될 수 있으므로, 서비스 레이어에서 읽기/쓰기를 명확히 구분해야 합니다.

일부 DB(PostgreSQL 등)는 readOnly 트랜잭션에서 INSERT/UPDATE/DELETE를 시도하면 에러를 발생시켜 더 안전합니다.

## 코드 예시 (필요시)
```java
// ProjectService.java
@Service
@RequiredArgsConstructor
@Transactional  // 클래스 레벨: 기본 쓰기 트랜잭션
public class ProjectService {
    
    // 읽기 전용 메서드들은 메서드 레벨에서 readOnly = true
    @Transactional(readOnly = true)
    public List<ProjectListResponseDTO> getMyProjects(Long userId) {
        return projectMemberRepository.findAllByUser_UserId(userId)
            .stream()
            .map(pm -> new ProjectListResponseDTO(...))
            .toList();
    }
    
    @Transactional(readOnly = true)
    public ProjectBoardDTO getProjectBoard(Long projectId) {
        ProjectBoardDTO boardDTO = projectMapper.selectProjectBoard(projectId)
            .orElseThrow();
        
        // readOnly이므로 Dirty Checking 비활성화
        // 엔티티를 변경해도 UPDATE 실행 안 됨
        return boardDTO;
    }
    
    // 쓰기 메서드는 클래스 레벨 설정 상속 (readOnly = false)
    @RequireProjectLeader
    public void updateProject(Long projectId, ProjectUpdateRequestDTO dto) {
        Project project = projectRepository.findById(projectId)
            .orElseThrow();
        
        project.update(...);  // Dirty Checking 활성화 → UPDATE 실행
    }
}

// readOnly에서 쓰기 시도 예시 (작동하지 않음)
@Transactional(readOnly = true)
public void wrongMethod(Long projectId) {
    Project project = projectRepository.findById(projectId)
        .orElseThrow();
    
    project.update("New Name", ...);  // 변경 시도
    
    // 트랜잭션 커밋 시점
    // → flush() 호출 안 됨
    // → UPDATE 쿼리 실행 안 됨
    // → DB는 변경되지 않음
    // → 예외도 발생하지 않음 (조용히 무시됨)
}

// Master-Slave 라우팅 예시 (설정에 따라 다름)
@Transactional(readOnly = true)  // → Slave DB로 라우팅
public List<User> findAll() {
    return userRepository.findAll();
}

@Transactional  // → Master DB로 라우팅
public void saveUser(User user) {
    userRepository.save(user);
}
```

## 꼬리 질문 예상
- readOnly = true인 메서드에서 save()를 호출하면 어떻게 되나요?
- OSIV(Open Session In View)가 활성화된 상태에서 readOnly의 동작은 어떻게 달라지나요?
- 클래스 레벨과 메서드 레벨에 모두 @Transactional이 있으면 어느 것이 우선하나요?

## 참고
- [[Transactional 어노테이션 심화]]
- [[JPA 성능 최적화]]

---

## 질문 10
> JPA Repository의 save() 메서드가 INSERT와 UPDATE를 어떻게 구분하는지, 그리고 식별자 생성 전략(@GeneratedValue)과의 관계를 설명해주세요.

## 핵심 답변 (3줄)
1. save()는 엔티티의 @Id 필드가 null이거나 0이면 새 엔티티로 판단하여 persist()를 호출하고, 값이 있으면 기존 엔티티로 판단하여 merge()를 호출합니다
2. @GeneratedValue(strategy = IDENTITY)는 DB에 INSERT 후 자동 생성된 ID를 받아오므로, 영속화 즉시 ID가 할당됩니다
3. merge()는 SELECT → UPDATE 순서로 실행되어 불필요한 쿼리가 발생할 수 있으므로, 수정 시에는 Dirty Checking을 사용하는 것이 권장됩니다

## 상세 설명
Spring Data JPA의 save() 메서드는 내부적으로 SimpleJpaRepository에 구현되어 있습니다:

```java
@Transactional
public <S extends T> S save(S entity) {
    if (entityInformation.isNew(entity)) {
        em.persist(entity);  // 새 엔티티: INSERT
        return entity;
    } else {
        return em.merge(entity);  // 기존 엔티티: SELECT + UPDATE
    }
}
```

**isNew() 판단 기준:**
1. @Id 필드가 null → 새 엔티티
2. @Id 필드가 0 (숫자 타입) → 새 엔티티
3. @Id 필드에 값이 있음 → 기존 엔티티

BizSync의 Project는 `@GeneratedValue(strategy = IDENTITY)`를 사용합니다:

```java
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long projectId;
```

IDENTITY 전략은 DB의 AUTO_INCREMENT를 사용하므로, INSERT를 실행해야 ID를 알 수 있습니다. 따라서 persist() 호출 시 즉시 INSERT 쿼리가 실행됩니다 (쓰기 지연 불가).

**save() 사용 시나리오:**

1. **새 엔티티 저장** (권장):
```java
Project project = Project.builder()
    .name("BizSync")
    .build();
// projectId = null → isNew() = true
projectRepository.save(project);  // persist() → INSERT
// 이후 project.getProjectId() != null
```

2. **기존 엔티티 수정** (비권장, merge 사용):
```java
Project project = projectRepository.findById(1L).get();
project.setName("Updated");
projectRepository.save(project);  
// projectId != null → isNew() = false
// merge() → SELECT + UPDATE
```

3. **기존 엔티티 수정** (권장, Dirty Checking):
```java
@Transactional
public void updateProject(Long id) {
    Project project = projectRepository.findById(id).get();
    project.update("Updated", ...);
    // save() 호출 불필요!
    // 트랜잭션 커밋 시 자동 UPDATE
}
```

merge()의 문제는 detached 엔티티를 받아서 새로운 managed 엔티티를 반환하므로, 불필요한 SELECT가 발생하고, 반환 값을 다시 받아야 한다는 점입니다. 수정은 Dirty Checking을 사용하고, save()는 새 엔티티 저장에만 사용하는 것이 베스트 프랙티스입니다.

## 코드 예시 (필요시)
```java
// ProjectService.java
@Service
@RequiredArgsConstructor
@Transactional
public class ProjectService {
    
    private final ProjectRepository projectRepository;
    
    // 올바른 사용: 새 엔티티 저장
    public Long createProject(Long userId, ProjectCreateRequestDTO dto) {
        Project project = Project.builder()
                .name(dto.name())
                .description(dto.description())
                .totalBudget(dto.totalBudget())
                .build();
        // project.getProjectId() == null → isNew() == true
        
        Project savedProject = projectRepository.save(project);
        // persist() 호출 → INSERT 실행
        // savedProject.getProjectId() != null (DB가 할당)
        
        return savedProject.getProjectId();
    }
    
    // 비권장: merge() 사용
    public void wrongUpdate(Long projectId, String newName) {
        Project project = new Project();  // detached 상태
        project.setProjectId(projectId);  // ID 설정
        project.setName(newName);
        
        projectRepository.save(project);
        // isNew() == false (ID 있음)
        // merge() 호출
        // → SELECT project WHERE id = ? (불필요)
        // → UPDATE project SET name = ? WHERE id = ?
    }
    
    // 권장: Dirty Checking 사용
    public void correctUpdate(Long projectId, String newName) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow();
        // project는 managed 상태
        
        project.update(newName, ...);
        // save() 호출 불필요
        // 트랜잭션 커밋 시 자동 UPDATE
    }
}

// @GeneratedValue 전략별 차이
@Entity
public class Project {
    
    // IDENTITY: INSERT 즉시 실행, ID 즉시 할당
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long projectId;
    
    // SEQUENCE: 시퀀스에서 ID 받은 후 INSERT (배치 가능)
    // @Id
    // @GeneratedValue(strategy = GenerationType.SEQUENCE)
    // private Long projectId;
    
    // AUTO: DB에 따라 자동 선택
    // @Id
    // @GeneratedValue(strategy = GenerationType.AUTO)
    // private Long projectId;
}

// SimpleJpaRepository의 실제 구현 (간소화)
public class SimpleJpaRepository<T, ID> implements JpaRepository<T, ID> {
    
    @Transactional
    public <S extends T> S save(S entity) {
        if (entityInformation.isNew(entity)) {
            em.persist(entity);
            return entity;
        } else {
            return em.merge(entity);
        }
    }
}
```

## 꼬리 질문 예상
- @Version을 사용한 낙관적 락과 save()의 관계는 무엇인가요?
- Persistable 인터페이스를 구현하여 isNew() 로직을 커스터마이징하는 방법은 무엇인가요?
- IDENTITY 전략의 배치 INSERT 제한과 대안은 무엇인가요?

## 참고
- [[JPA 식별자 생성 전략]]
- [[persist vs merge]]
