---
tags:
  - interview
  - mybatis
  - dynamic-sql
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - MyBatis 동적 쿼리

## 질문
> 검색 조건이 선택적일 때 MyBatis 동적 쿼리를 어떻게 작성했나요?

## 핵심 답변 (3줄)
1. **`<if>` 태그** - 조건부로 WHERE 절 추가
2. **`<where>` 태그** - 첫 번째 AND 자동 제거
3. **`<foreach>` 태그** - IN 절이나 다중 값 처리

## 상세 설명
```xml
<!-- ProjectMapper.xml -->
<select id="selectProjectList" resultType="ProjectSearchResponse">
    SELECT 
        p.project_id,
        p.name,
        p.status,
        u.user_name AS owner_name
    FROM project p
    JOIN user u ON p.owner_id = u.user_id
    <where>
        <if test="workspaceId != null">
            AND p.workspace_id = #{workspaceId}
        </if>
        <if test="status != null and status != ''">
            AND p.status = #{status}
        </if>
        <if test="keyword != null and keyword != ''">
            AND (p.name LIKE CONCAT('%', #{keyword}, '%')
                 OR p.description LIKE CONCAT('%', #{keyword}, '%'))
        </if>
        <if test="ownerIds != null and ownerIds.size() > 0">
            AND p.owner_id IN
            <foreach item="id" collection="ownerIds" 
                     open="(" separator="," close=")">
                #{id}
            </foreach>
        </if>
    </where>
    ORDER BY p.created_at DESC
    LIMIT #{offset}, #{limit}
</select>
```

```java
// 사용 예시
public record ProjectSearchRequest(
    Long workspaceId,
    String status,
    String keyword,
    List<Long> ownerIds,
    int offset,
    int limit
) {}
```

## 꼬리 질문 예상
- `<trim>` 태그는 언제 사용하나요?
- JPA의 Criteria API와 비교하면?

## 참고
- [[MyBatis-동적SQL-완벽가이드]]
- [[bizsync-MyBatis-중첩ResultMap-면접]]
