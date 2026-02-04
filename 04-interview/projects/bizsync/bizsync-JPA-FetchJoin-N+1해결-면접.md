---
tags:
  - interview
  - jpa
  - fetch-join
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - Fetch Join으로 N+1 해결

## 질문
> N+1 문제를 Fetch Join으로 해결한 사례를 설명해주세요.

## 핵심 답변 (3줄)
1. **N+1 문제** - 연관 엔티티 조회 시 추가 쿼리 N번 발생
2. **Fetch Join** - `JOIN FETCH`로 한 번에 연관 엔티티까지 조회
3. **성능 개선** - 쿼리 1+N번 → 1번으로 감소

## 상세 설명
```java
// ❌ N+1 발생 코드
@Query("SELECT p FROM Project p WHERE p.workspace.workspaceId = :workspaceId")
List<Project> findByWorkspace(Long workspaceId);
// 1. SELECT p FROM project (1번)
// 2. SELECT u FROM user WHERE u.user_id = ? (N번 - 각 project마다)

// ✅ Fetch Join 적용
@Query("SELECT p FROM Project p " +
       "JOIN FETCH p.owner " +
       "WHERE p.workspace.workspaceId = :workspaceId")
List<Project> findByWorkspaceWithOwner(Long workspaceId);
// SELECT p.*, u.* FROM project p JOIN user u ON p.owner_id = u.user_id (1번만!)

// 서비스에서 사용
public List<ProjectResponse> getWorkspaceProjects(Long workspaceId) {
    List<Project> projects = projectRepository.findByWorkspaceWithOwner(workspaceId);
    return projects.stream()
        .map(p -> ProjectResponse.from(p))  // p.getOwner().getName() 호출해도 추가 쿼리 없음
        .toList();
}
```

**컬렉션 Fetch Join 주의사항:**
- 페이징 사용 불가 (메모리에서 처리)
- 카테시안 곱 발생 가능
- `@BatchSize`나 `@EntityGraph`로 대체 고려

## 꼬리 질문 예상
- Fetch Join과 EntityGraph의 차이는?
- 컬렉션 Fetch Join 시 DISTINCT를 사용하는 이유는?

## 참고
- [[bizsync-JPA-MyBatis하이브리드-면접]]
