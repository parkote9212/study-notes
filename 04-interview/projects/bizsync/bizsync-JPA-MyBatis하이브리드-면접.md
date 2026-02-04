---
tags:
  - interview
  - jpa
  - mybatis
  - bizsync
  - project
created: 2025-01-23
difficulty: 상
---

# BizSync - JPA MyBatis 하이브리드 ORM

## 질문
> BizSync에서 JPA와 MyBatis를 함께 사용하는 하이브리드 방식을 채택한 이유와 각각의 사용 케이스를 설명해주세요.

## 핵심 답변 (3줄)
1. JPA는 단순 CRUD와 엔티티 중심의 비즈니스 로직에서 생산성과 유지보수성이 뛰어나고, MyBatis는 복잡한 조인과 동적 쿼리에서 성능과 유연성이 뛰어납니다
2. 프로젝트 보드 조회처럼 여러 테이블을 조인하고 중첩된 컬렉션을 매핑해야 하는 경우 MyBatis의 ResultMap이 더 효율적입니다
3. 두 기술을 혼용하면 각 상황에 최적화된 도구를 선택할 수 있지만, 일관성 유지와 트랜잭션 관리에 주의해야 합니다

## 상세 설명
BizSync는 대부분의 기본 CRUD 작업에 JPA를 사용하지만, 칸반 보드 전체 조회처럼 복잡한 쿼리가 필요한 경우 MyBatis를 활용합니다.

**JPA 사용 케이스:**
- Project, User, Task 등의 단순 CRUD
- 연관관계 기반 객체 그래프 탐색
- Dirty Checking을 활용한 업데이트
- Spring Data JPA의 메서드 쿼리

**MyBatis 사용 케이스:**
- ProjectBoardDTO 조회: Project → KanbanColumn → Task를 한 번의 쿼리로 조인
- 복잡한 통계 쿼리나 집계 함수 활용
- 동적 검색 조건이 많은 경우

## 코드 예시
```java
// JPA 방식 - 단순 CRUD
@Service
public class ProjectService {
    private final ProjectRepository projectRepository;
    
    @Transactional
    public void completeProject(Long projectId) {
        Project project = projectRepository.findById(projectId)
            .orElseThrow();
        project.complete();  // Dirty Checking으로 자동 UPDATE
    }
}

// MyBatis 방식 - 복잡한 조인
@Mapper
public interface ProjectMapper {
    Optional<ProjectBoardDTO> selectProjectBoard(@Param("projectId") Long projectId);
}
```

```xml
<!-- MyBatis XML - 복잡한 ResultMap -->
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
- JPA로 동일한 쿼리를 작성한다면 어떻게 최적화할 수 있나요?
- 트랜잭션 내에서 JPA와 MyBatis를 함께 사용할 때 주의사항은?

## 참고
- [[bizsync-MyBatis-중첩ResultMap-면접]]
- [[bizsync-JPA-FetchJoin-N+1해결-면접]]
