---
tags:
  - interview
  - JPA
  - database
  - performance
difficulty: 중
category: backend
---
# JPA N+1 문제와 해결 방법

## 질문
> JPA에서 N+1 문제가 무엇인지 설명하고, 실제 프로젝트에서 어떻게 해결했는지 말씀해주세요.

## 핵심 답변 (3줄)
1. **N+1 문제**: 1번의 쿼리로 N개의 데이터를 조회한 후, 각 데이터마다 추가 쿼리가 발생하여 총 N+1번의 쿼리가 실행되는 성능 문제
2. **원인**: 지연 로딩(Lazy Loading)에서 연관된 엔티티를 접근할 때마다 새로운 쿼리 발생
3. **해결 방법**: Fetch Join, BatchSize, EntityGraph, 쿼리 최적화 등으로 해결 가능

## 상세 설명

### 문제 상황
```
1. SELECT * FROM users; (1번 쿼리)
2. SELECT * FROM posts WHERE user_id = 1; (N번 쿼리)
3. SELECT * FROM posts WHERE user_id = 2;
...
N+1번의 쿼리 실행
```

**원인 분석**
- **지연 로딩 (Lazy Loading)**: User 엔티티만 조회되고, Post는 접근할 때 로드
- `user.getPosts()` 호출 시마다 새로운 SELECT 쿼리 발생
- 반복문에서 100개의 User가 있으면 1 + 100 = 101번 쿼리 실행

### 해결 방법

#### 1️⃣ **Fetch Join (가장 권장)**
```java
@Query("SELECT u FROM User u JOIN FETCH u.posts WHERE u.id = :userId")
User findUserWithPostsJoinFetch(@Param("userId") Long userId);
```
- 한 번의 쿼리로 User와 Post를 함께 로드
- **장점**: 명확하고 효율적, 복잡한 조인 가능
- **단점**: 페이징 불가능 (데이터 중복 문제), 컬렉션 2개 이상 JOIN 불가
- **실무 경험**: 대부분의 조회 쿼리에서 이 방식 사용

#### 2️⃣ **@BatchSize (대량 조회 최적화)**
```java
@Entity
public class User {
    @Id
    private Long id;
    
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    @BatchSize(size = 10)
    private List<Post> posts = new ArrayList<>();
}
```
- N번의 쿼리를 로그 기준으로 줄임 (N/BatchSize번)
- 100개 User + BatchSize(10) = 1 + 10 = 11번 쿼리
- **사용 시기**: 리스트 조회에서 여러 컬렉션 필요할 때
- **주의**: WHERE IN 절 사용으로 쿼리 단순화

#### 3️⃣ **@EntityGraph**
```java
@EntityGraph(attributePaths = {"posts"})
@Query("SELECT u FROM User u")
List<User> findAllUsers();
```
- Fetch Join과 유사하지만 어노테이션 기반
- **장점**: 코드 간결, 유연함
- **단점**: 복잡한 로직에는 어렵고 중복 데이터 문제 동일

#### 4️⃣ **명시적 쿼리 (JPQL/Native Query)**
```java
@Query("""
    SELECT new map(
        u.id AS userId,
        u.name AS userName,
        p.id AS postId,
        p.title AS postTitle
    )
    FROM User u
    LEFT JOIN u.posts p
    WHERE u.active = true
""")
List<Map<String, Object>> findUsersWithPosts();
```
- 필요한 데이터만 선택적으로 조회
- **가장 효율적**: 불필요한 칼럼 제외

## 코드 예시

### ❌ N+1 문제 발생 코드
```java
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public List<UserDTO> getUsersWithPosts() {
        List<User> users = userRepository.findAll(); // 1번 쿼리
        
        return users.stream().map(user -> {
            List<Post> posts = user.getPosts(); // 여기서 N번 쿼리 발생!
            return new UserDTO(user.getId(), user.getName(), posts);
        }).collect(Collectors.toList());
    }
}
```
**쿼리 로그:**
```
Hibernate: SELECT * FROM users;
Hibernate: SELECT * FROM posts WHERE user_id = 1;
Hibernate: SELECT * FROM posts WHERE user_id = 2;
Hibernate: SELECT * FROM posts WHERE user_id = 3;
...
```

### ✅ Fetch Join으로 해결
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    @Query("SELECT DISTINCT u FROM User u JOIN FETCH u.posts")
    List<User> findAllWithPosts();
}

@Service
public class UserService {
    
    public List<UserDTO> getUsersWithPosts() {
        // 1번 쿼리로 모든 데이터 로드
        List<User> users = userRepository.findAllWithPosts();
        
        return users.stream()
            .map(user -> new UserDTO(user.getId(), user.getName(), user.getPosts()))
            .collect(Collectors.toList());
    }
}
```
**쿼리 로그:**
```
Hibernate: 
    SELECT DISTINCT u.* FROM users u 
    INNER JOIN posts p ON u.id = p.user_id;
```

### ✅ BatchSize로 해결
```java
@Entity
public class User {
    @Id
    private Long id;
    private String name;
    
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    @BatchSize(size = 50)  // 50개씩 조회
    private List<Post> posts;
}

// 사용
List<User> users = userRepository.findAll(); // 1번
users.forEach(user -> {
    user.getPosts().size(); // 2번 쿼리 (IN으로 50개씩 묶음)
});
```

## 성능 비교

| 방식 | 쿼리 수 | 메모리 | 장점 | 단점 |
|------|--------|--------|------|------|
| **문제 코드** | N+1 | 낮음 | 간단함 | 성능 나쁨 |
| **Fetch Join** | 1 | 중간 | 가장 빠름 | 페이징 불가 |
| **BatchSize** | 1 + N/size | 중간 | 유연함 | 약간 복잡 |
| **EntityGraph** | 1 | 중간 | 깔끔함 | Fetch Join과 동일 |

## 실무 적용 전략

**상황별 선택 기준:**
1. **단일 조회 + 연관 엔티티 1개**: Fetch Join 사용
2. **리스트 조회 + 여러 컬렉션**: BatchSize(50~100) 권장
3. **페이징 필요**: BatchSize + 별도 count 쿼리
4. **복잡한 데이터**: QueryDSL + 명시적 쿼리

## 꼬리 질문 예상
- **"Fetch Join으로 페이징하면 어떻게 되나요?"**
  → 메모리에서 페이징되어 성능 저하. 두 개의 쿼리로 분리 필요
  
- **"BatchSize와 Fetch Join의 차이점은?"**
  → Fetch Join: 1번 쿼리, 메모리에 모두 로드 / BatchSize: N/size번 쿼리, 필요할 때 로드
  
- **"OneToMany 중복 데이터 문제는?"**
  → DISTINCT를 JPQL에 추가하거나 LinkedHashSet 사용, 또는 별도 컬렉션 처리
  
- **"실무에서 어떻게 검증했나요?"**
  → 로그 레벨 DEBUG로 설정해서 실제 SQL 확인, 성능 테스트 진행

## 참고 자료
- [Spring Data JPA - Fetch Join](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#repositories.query-methods.query-creation)
- [Hibernate - N+1 Problem](https://hibernate.org/orm/documentation/5.6/)
- [QueryDSL - 쿼리 최적화](http://www.querydsl.com/)
