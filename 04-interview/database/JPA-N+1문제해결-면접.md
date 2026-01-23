---
tags: interview, JPA, 성능최적화
created: 2026-01-23
difficulty: 최상
---

# JPA N+1 문제 해결

## 질문
> Fetch Join이 N+1의 가장 좋은 해결책인데, Fetch Join을 사용하기 어려운 상황에서는 어떻게 하시겠습니까?

## 핵심 답변 (3줄)
1. Fetch Join의 한계: `@OneToMany` 관계에서 데이터 중복(Cartesian Product) 발생, 특히 두 개 이상의 컬렉션을 Fetch Join하거나 페이징을 적용하기 어렵습니다.
2. 대안 제시: 이러한 경우 **`@BatchSize`** 설정을 사용합니다. `IN` 쿼리 방식을 통해 N번의 쿼리를 M번으로 줄여서 최적화합니다.
3. 최후의 수단: BatchSize마저 사용이 어렵다면, 연관 엔티티를 조회하는 로직을 분리하여 **Service Layer**나 **DAO**에서 별도의 쿼리로 필요한 데이터만 미리 캐싱하거나, 필요한 시점에 명시적으로 가져오도록 코드를 수정해야 합니다.

## 상세 설명

### Fetch Join의 한계

1. **Cartesian Product 문제**: `@OneToMany` 관계에서 Fetch Join을 사용하면, 1 대 N 관계로 인해 부모 데이터가 중복되어 조회됩니다.

```sql
-- Post 1개, Comment 5개인 경우
SELECT p.*, c.* FROM Post p JOIN Comment c ON p.id = c.post_id
-- 결과: Post 데이터가 5번 반복됨
```

2. **페이징 불가**: 위의 중복 때문에 LIMIT/OFFSET 페이징이 제대로 작동하지 않습니다.

3. **MultipleBagFetchException**: 두 개 이상의 컬렉션을 동시에 Fetch Join하면 예외 발생

### 해결책 순서

1. **@BatchSize 사용** (권장)
```java
@Entity
public class Post {
    @BatchSize(size = 20)
    @OneToMany(mappedBy = "post")
    private List<Comment> comments;
}
```
이렇게 하면 `IN` 절을 사용하여 여러 Post의 Comment를 한 번에 조회합니다.

2. **Entity Graph 사용** (단일 컬렉션)
```java
@EntityGraph(attributePaths = "comments")
List<Post> findAll();
```

3. **Service Layer에서 분리 조회** (복잡한 상황)
```java
List<Post> posts = postRepository.findAll();
Map<Long, List<Comment>> comments = commentRepository.findByPostIds(
    posts.stream().map(Post::getId).collect(toList())
);
// 후에 메모리에서 조합
```

## 코드 예시

```java
// ❌ N+1 문제 발생
@Entity
public class Post {
    @OneToMany(mappedBy = "post", fetch = FetchType.LAZY)
    private List<Comment> comments;
}

// ✅ Fetch Join (단순 조회)
@Query("SELECT DISTINCT p FROM Post p JOIN FETCH p.member")
List<Post> findAll();

// ✅ @BatchSize (@OneToMany 최적화)
@Entity
public class Post {
    @BatchSize(size = 20)
    @OneToMany(mappedBy = "post")
    private List<Comment> comments;
}

// ✅ Entity Graph
@EntityGraph(attributePaths = {"member", "comments"})
List<Post> findAll();
```

## 꼬리 질문 예상
- @BatchSize의 size는 어떻게 정하나요?
- QueryDSL은 N+1 문제를 어떻게 해결하나요?
- 페이징과 Fetch Join을 함께 사용하면 어떤 문제가 발생하나요?
- distinct를 사용하는 이유는 무엇인가요?

## 참고
- [[JPA-성능최적화-N+1문제해결]]
- [[JPA-영속성컨텍스트-엔티티생명주기]]
