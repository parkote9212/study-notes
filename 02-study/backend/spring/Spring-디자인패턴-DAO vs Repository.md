# Spring-디자인패턴-DAO vs Repository

🏷️기술 카테고리: Design Pattern, Spring
💡핵심키워드: #디자인패턴, #레이어드아키텍처, #DDD
💼 면접 빈출도: 상

# 1. Abstract: 핵심 요약

DAO와 Repository는 모두 데이터 접근 계층을 추상화하는 패턴이지만, 관점과 추상화 수준에서 차이가 있습니다.

**핵심 차이**:
- DAO: 기술적 관점 (데이터 접근)
- Repository: 도메인 친화적 관점 (객체 컬렉션)
- Modern Spring에서는 Repository 용어를 권장

# 2. DAO (Data Access Object)

## 2.1 정의

데이터베이스나 기타 영구 저장소에 접근하는 로직을 캡슐화하는 객체입니다.

## 2.2 핵심 역할

### 1. CRUD 작업 수행
Create, Read, Update, Delete 작업 수행

### 2. 데이터 기술 캡슐화
JDBC, MyBatis, JPA 등 구현 기술의 세부 사항을 외부에 숨김

### 3. 관심사의 분리

| 계층 | 역할 |
| --- | --- |
| Controller | 클라이언트 요청/응답 처리 |
| Service | 핵심 비즈니스 로직 |
| DAO/Repository | 순수 데이터 접근 |

## 2.3 전통적인 DAO 구현

```java
public interface UserDao {
    void save(User user);
    User findById(Long id);
    List<User> findAll();
    void update(User user);
    void delete(Long id);
}

@Repository
public class UserDaoImpl implements UserDao {
    private final JdbcTemplate jdbcTemplate;
    
    @Override
    public User findById(Long id) {
        return jdbcTemplate.queryForObject(
            "SELECT * FROM users WHERE id = ?",
            new UserRowMapper(),
            id
        );
    }
}
```

# 3. Repository (Modern Spring)

## 3.1 정의

Domain Driven Design(DDD)에서 유래한 용어로, 도메인 객체 컬렉션의 접근을 추상화하는 개념입니다.

## 3.2 Spring Data JPA

```java
// 인터페이스만 정의
public interface UserRepository extends JpaRepository<User, Long> {
    // 메서드 이름으로 쿼리 자동 생성
    Optional<User> findByUsername(String username);
    List<User> findByAgeGreaterThan(int age);
}

// Spring이 런타임에 프록시 객체 자동 생성
```

# 4. DAO vs Repository 비교

| 구분 | DAO | Repository |
| --- | --- | --- |
| **기원** | Java EE 패턴 | Domain Driven Design (DDD) |
| **관점** | 기술적 (DB 테이블 중심) | 도메인 친화적 (객체 컬렉션) |
| **추상화 수준** | 낮음 | 높음 |
| **현대 프레임워크** | 제한적 지원 | Spring Data JPA 전체 지원 |
| **구현 방식** | 직접 구현 필요 | 인터페이스만 정의 |

# 5. 언제 DAO가 여전히 필요한가?

## 5.1 QueryDSL 사용

```java
public interface UserRepositoryCustom {
    List<User> searchUsers(UserSearchCondition condition);
}

@RequiredArgsConstructor
public class UserRepositoryImpl implements UserRepositoryCustom {
    private final JPAQueryFactory queryFactory;
    
    @Override
    public List<User> searchUsers(UserSearchCondition condition) {
        return queryFactory
            .selectFrom(user)
            .where(
                usernameEq(condition.getUsername()),
                ageGoe(condition.getAge())
            )
            .fetch();
    }
}
```

## 5.2 대규모 Batch 작업

```java
@Repository
@RequiredArgsConstructor
public class UserBatchDao {
    private final JdbcTemplate jdbcTemplate;
    
    public void batchInsert(List<User> users) {
        jdbcTemplate.batchUpdate(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            users,
            1000,
            (ps, user) -> {
                ps.setString(1, user.getUsername());
                ps.setString(2, user.getEmail());
            }
        );
    }
}
```

# 6. Modern Spring Boot 환경에서의 권장 사항

```java
// ✅ 기본 CRUD: Spring Data JPA Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsername(String username);
}

// ✅ 복잡한 쿼리: QueryDSL Custom Repository
public interface UserRepositoryCustom {
    List<User> complexSearch(SearchCondition condition);
}

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;  // Repository 용어 사용
    
    public User getUser(Long id) {
        return userRepository.findById(id)
            .orElseThrow();
    }
}
```

# 7. Interview Readiness

## Q: DAO와 Repository의 차이점을 설명하세요.

**A**: DAO는 데이터 접근 로직을 캡슐화하는 패턴 이름으로, 구현 기술에 상관없이 데이터 조작을 담당합니다. Repository는 Domain Driven Design(DDD)에서 유래한 용어로, 도메인 객체 컬렉션의 접근을 추상화하는 개념입니다. DAO보다 좀 더 도메인 친화적입니다.

Spring Data JPA에서는 DAO의 역할을 Repository 인터페이스로 구현합니다. 이는 데이터 접근을 기술적인 관점(DAO)보다는 비즈니스 도메인 관점(Repository)에서 바라보도록 유도하는 Modern 프레임워크의 흐름을 반영한 것입니다. 따라서 Spring Boot 프로젝트에서는 Repository라는 용어를 주로 사용해야 합니다.

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐ (상)
