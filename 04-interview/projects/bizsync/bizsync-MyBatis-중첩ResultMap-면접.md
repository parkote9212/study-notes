---
tags:
  - interview
  - mybatis
  - resultmap
  - bizsync
  - project
created: 2025-01-23
difficulty: 상
---

# BizSync - MyBatis 중첩 ResultMap

## 질문
> MyBatis의 중첩 ResultMap에서 collection 태그를 사용한 일대다 매핑과 N+1 문제 회피 방법을 설명해주세요.

## 핵심 답변 (3줄)
1. MyBatis의 `<collection>`은 일대다 관계를 한 번의 쿼리로 조회하여 부모 객체에 자식 컬렉션을 매핑하는 기능입니다
2. LEFT JOIN으로 데이터를 한 번에 가져오고, resultMap의 id 태그로 부모-자식을 구분하여 중복 제거와 계층 구조를 생성합니다
3. JPA의 지연 로딩에서 발생하는 N+1 문제를 원천적으로 방지하며, 단일 쿼리로 복잡한 객체 그래프를 효율적으로 구성합니다

## 상세 설명
BizSync의 ProjectMapper.selectProjectBoard()는 프로젝트, 칸반 컬럼, 업무를 한 번의 쿼리로 조회합니다.

**ResultMap의 collection 동작 원리:**
1. LEFT JOIN으로 모든 행을 FLAT하게 조회
2. `<id>` 태그로 각 엔티티의 고유 식별자 지정
3. 같은 project_id를 가진 행들을 하나의 Project 객체로 그룹화
4. 각 Project 내에서 column_id로 KanbanColumn 그룹화
5. 각 KanbanColumn 내에서 task_id로 Task 그룹화

## 코드 예시
```xml
<!-- ProjectMapper.xml -->
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
    ORDER BY c.sequence ASC, t.sequence ASC
</select>
```

## 꼬리 질문 예상
- JPA의 @EntityGraph와 MyBatis의 collection 중 어떤 것이 더 효율적인가요?
- 카테시안 곱 문제를 해결하기 위한 전략은?

## 참고
- [[bizsync-JPA-MyBatis하이브리드-면접]]
- [[bizsync-MyBatis-동적쿼리-면접]]
