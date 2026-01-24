---
tags:
  - study
  - database
  - jpa
  - n
  - 성능최적화
  - 쿼리최적화
  - 패치조인
created: 2026-01-23
difficulty: 상
---
# JPA-성능최적화-N+1문제해결

🏷️기술 카테고리: DataBase, JPA
💡핵심키워드: #N+1, #성능최적화, #쿼리최적화, #패치조인
💼 면접 빈출도: 최상

# 1. Abstract: 핵심 요약

N+1 문제는 1개의 쿼리로 리스트를 가져왔을 때, 해당 리스트에 포함된 N개의 연관 엔티티를 가져오기 위해 N번의 추가 쿼리가 나가는 현상입니다. 총 1 + N번의 쿼리가 실행되어 성능 저하를 일으킵니다.

**핵심 원칙**:
- 지연 로딩(Lazy Loading)이 주요 원인
- Fetch Join, Entity Graph, @BatchSize로 해결
- 상황에 맞는 최적의 전략 선택

# 2. N+1 문제 이해

## 2.1 발생 원인

JPA의 기본 전략인 **지연 로딩(Lazy Loading, FetchType.LAZY)** 때문에 발생합니다.

- JPA는 Entity의 연관 관계를 기본적으로 **프록시(Proxy) 객체**로 감싼다
- 1번 쿼리 실행 시, 연관 객체는 프록시 상태로 남아있다
- 반복문에서 프록시에 최초로 접근하는 순간, JPA는 실제 데이터를 로드하기 위해 **추가 쿼리(N번)**를 실행한다

## 2.2 구체적 예시

```java
// Service
List<Post> posts = postRepository.findAll();  // 1번 쿼리

for (Post post : posts) {
    Member member = post.getMember();  // N번 쿼리 (프록시 접근 시)
    System.out.println(member.getName());
}
```

**결과**: 총 1 + N번의 쿼리 실행

```sql
-- 1번 쿼리: 게시글 100개 조회
SELECT * FROM Post WHERE ...

-- N번 쿼리: 각 게시글의 작성자 조회 (100번 실행)
SELECT * FROM Member WHERE id = ?
SELECT * FROM Member WHERE id = ?
...(100번 반복)
```

# 3. 해결 방법

## 3.1 Fetch Join (가장 강력)

JPQL을 사용하여 명시적으로 JOIN을 수행하고, 연관 엔티티를 한 번에 가져옵니다.

```java
@Query("""
    SELECT p 
    FROM Post p 
    JOIN FETCH p.member 
    WHERE p.title LIKE :titleKeyword
""")
List<Post> findAllWithMemberByTitle(@Param("titleKeyword") String titleKeyword);
```

**결과**: 단 1번의 쿼리로 Post와 Member를 모두 가져옴

**장점:**
- 가장 직관적이고 강력
- 가장 좋은 성능

**단점:**
- `@OneToMany` 관계에서 Cartesian Product 발생 (데이터 중복)
- 페이징 적용 어려움

## 3.2 Entity Graph (선언적 방식)

`@EntityGraph` 애너테이션으로 선언적으로 연관 엔티티 로드를 지정합니다.

```java
@EntityGraph(attributePaths = {"member"})
@Query("SELECT p FROM Post p")
List<Post> findAll();
```

**장점:**
- 코드 간결
- 쿼리 수정 없이 로딩 전략 유연 변경

**단점:**
- 다중 컬렉션 Fetch 불가

## 3.3 @BatchSize (차선책)

N번의 쿼리를 M번의 쿼리로 최적화합니다.

```java
@BatchSize(size = 10)
@OneToMany(mappedBy = "post")
private List<Comment> comments;
```

**원리**: N개를 하나씩 조회하는 대신, `IN` 절을 사용하여 한 번에 조회

**예시**: 게시글 100개 / BatchSize = 10 → 10번의 쿼리 (총 11번)

**장점:**
- `@OneToMany` 여러 개 동시 로딩 가능

**단점:**
- Fetch Join보다는 쿼리 수 많음

## 3.4 Projection (DTO)

필요한 컬럼만 조회하여 불필요한 연관관계 로딩 방지

```java
@Query("""
    SELECT new com.example.PostDTO(p.id, p.title, m.name)
    FROM Post p
    JOIN p.member m
""")
List<PostDTO> findPostDTOs();
```

# 4. 해결 전략 선택 가이드

| 상황 | 추천 해결책 | 이유 |
| --- | --- | --- |
| 가장 빈번한 조회 경로 | **Fetch Join** | 성능 최고, `ManyToOne`에 최적 |
| 특정 API에서만 다른 전략 필요 | **Entity Graph** | 선언적 관리, 복잡한 환경 유리 |
| 두 개 이상 `@OneToMany` 동시 로딩 | **@BatchSize** | Fetch Join 한계 극복 |
| 단순 데이터만 필요 | **Projection** | 불필요한 로딩 방지 |

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
