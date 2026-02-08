---
tags:
  - study
  - spring
  - data
  - jpa
  - spring-data-jpa
created: 2025-02-08
---

# Spring Data JPA 연동

## 한 줄 요약
> Spring Data JPA는 JPA 기반 데이터 접근 계층을 간소화하여, 반복적인 CRUD 코드 없이 인터페이스 정의만으로 Repository를 구현할 수 있게 하는 Spring의 데이터 접근 추상화 기술이다.

## 상세 설명

### Spring Data JPA란?
- **JPA를 쉽게 사용하기 위한 Spring 프로젝트**
- Repository 인터페이스만 정의하면 구현체 자동 생성
- 메서드 이름으로 쿼리 자동 생성
- 페이징, 정렬 기능 기본 제공

### JPA vs Spring Data JPA

| JPA (표준) | Spring Data JPA |
|-----------|-----------------|
| EntityManager 직접 사용 | Repository 인터페이스 |
| JPQL 직접 작성 | 메서드 이름으로 쿼리 생성 |
| 반복적인 CRUD 코드 | 기본 CRUD 자동 제공 |
| 페이징 직접 구현 | Pageable 지원 |

### Repository 계층 구조
```
Repository (마커 인터페이스)
  ↓
CrudRepository (기본 CRUD)
  ↓
PagingAndSortingRepository (페이징, 정렬)
  ↓
JpaRepository (JPA 특화 기능)
```

### 주요 기능

#### 1. 메서드 이름으로 쿼리 생성
```java
findByNameAndAge(String name, int age)
→ SELECT u FROM User u WHERE u.name = ?1 AND u.age = ?2
```

#### 2. @Query로 JPQL 작성
```java
@Query("SELECT u FROM User u WHERE u.email = :email")
User findByEmail(@Param("email") String email);
```

#### 3. 네이티브 쿼리 지원
```java
@Query(value = "SELECT * FROM users WHERE status = ?1", nativeQuery = true)
List<User> findByStatusNative(String status);
```

#### 4. 페이징과 정렬
```java
Page<User> findAll(Pageable pageable);
```

#### 5. Auditing (자동 생성/수정 시각)
```java
@CreatedDate
private LocalDateTime createdAt;
```

## 코드 예시

```java
// 1. 기본 Entity 정의
@Entity
@Table(name = "users")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 50)
    private String name;
    
    @Column(unique = true, nullable = false)
    private String email;
    
    private int age;
    
    @Enumerated(EnumType.STRING)
    private UserStatus status;
    
    @Builder
    public User(String name, String email, int age) {
        this.name = name;
        this.email = email;
        this.age = age;
        this.status = UserStatus.ACTIVE;
    }
}

// 2. JpaRepository 인터페이스
public interface UserRepository extends JpaRepository<User, Long> {
    // 기본 CRUD 메서드 자동 제공:
    // save(), findById(), findAll(), delete(), etc.
}

// 3. 쿼리 메서드 (메서드 이름으로 쿼리 생성)
public interface UserRepository extends JpaRepository<User, Long> {
    
    // SELECT * FROM users WHERE email = ?
    Optional<User> findByEmail(String email);
    
    // SELECT * FROM users WHERE name = ? AND age = ?
    List<User> findByNameAndAge(String name, int age);
    
    // SELECT * FROM users WHERE age > ?
    List<User> findByAgeGreaterThan(int age);
    
    // SELECT * FROM users WHERE name LIKE %?%
    List<User> findByNameContaining(String keyword);
    
    // SELECT * FROM users WHERE email IN (?, ?, ...)
    List<User> findByEmailIn(List<String> emails);
    
    // SELECT * FROM users ORDER BY name ASC
    List<User> findAllByOrderByNameAsc();
    
    // SELECT COUNT(*) FROM users WHERE status = ?
    long countByStatus(UserStatus status);
    
    // SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)
    boolean existsByEmail(String email);
    
    // DELETE FROM users WHERE age < ?
    void deleteByAgeLessThan(int age);
}

// 4. @Query 사용
public interface UserRepository extends JpaRepository<User, Long> {
    
    // JPQL
    @Query("SELECT u FROM User u WHERE u.email = :email")
    Optional<User> findByEmail(@Param("email") String email);
    
    // JPQL with JOIN
    @Query("SELECT u FROM User u " +
           "LEFT JOIN FETCH u.orders " +
           "WHERE u.id = :id")
    Optional<User> findByIdWithOrders(@Param("id") Long id);
    
    // Native Query
    @Query(value = "SELECT * FROM users WHERE status = ?1", 
           nativeQuery = true)
    List<User> findByStatusNative(String status);
    
    // 수정 쿼리
    @Modifying
    @Query("UPDATE User u SET u.status = :status WHERE u.id = :id")
    int updateStatus(@Param("id") Long id, @Param("status") UserStatus status);
    
    // 삭제 쿼리
    @Modifying
    @Query("DELETE FROM User u WHERE u.status = :status")
    int deleteByStatus(@Param("status") UserStatus status);
}

// 5. 페이징과 정렬
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 페이징
    Page<User> findByStatus(UserStatus status, Pageable pageable);
    
    // 슬라이스 (다음 페이지 존재 여부만)
    Slice<User> findByAgeGreaterThan(int age, Pageable pageable);
    
    // 리스트 (페이징 메타 정보 없음)
    List<User> findByName(String name, Sort sort);
}

// 사용 예시
@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    
    public Page<User> getUsers(int page, int size) {
        // 페이지 번호, 크기, 정렬 조건
        Pageable pageable = PageRequest.of(page, size, 
                            Sort.by("name").ascending());
        return userRepository.findAll(pageable);
    }
    
    public Page<User> getActiveUsers(int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return userRepository.findByStatus(UserStatus.ACTIVE, pageable);
    }
}

// 6. Auditing (자동 생성/수정 시각)
@EntityListeners(AuditingEntityListener.class)
@MappedSuperclass
@Getter
public abstract class BaseEntity {
    
    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;
    
    @LastModifiedDate
    private LocalDateTime updatedAt;
    
    @CreatedBy
    @Column(updatable = false)
    private String createdBy;
    
    @LastModifiedBy
    private String updatedBy;
}

// Auditing 설정
@EnableJpaAuditing
@Configuration
public class JpaConfig {
    
    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> {
            // 현재 로그인한 사용자 정보 반환
            Authentication authentication = 
                SecurityContextHolder.getContext().getAuthentication();
            
            if (authentication == null || !authentication.isAuthenticated()) {
                return Optional.empty();
            }
            
            return Optional.of(authentication.getName());
        };
    }
}

// Entity에서 사용
@Entity
public class User extends BaseEntity {
    // createdAt, updatedAt, createdBy, updatedBy 자동 관리
}

// 7. Specification (동적 쿼리)
public interface UserRepository 
        extends JpaRepository<User, Long>, JpaSpecificationExecutor<User> {
}

public class UserSpecification {
    
    public static Specification<User> hasName(String name) {
        return (root, query, criteriaBuilder) -> 
            criteriaBuilder.equal(root.get("name"), name);
    }
    
    public static Specification<User> hasAgeGreaterThan(int age) {
        return (root, query, criteriaBuilder) -> 
            criteriaBuilder.greaterThan(root.get("age"), age);
    }
    
    public static Specification<User> hasStatus(UserStatus status) {
        return (root, query, criteriaBuilder) -> 
            criteriaBuilder.equal(root.get("status"), status);
    }
}

// 사용
@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    
    public List<User> searchUsers(String name, Integer minAge, UserStatus status) {
        Specification<User> spec = Specification.where(null);
        
        if (name != null) {
            spec = spec.and(UserSpecification.hasName(name));
        }
        if (minAge != null) {
            spec = spec.and(UserSpecification.hasAgeGreaterThan(minAge));
        }
        if (status != null) {
            spec = spec.and(UserSpecification.hasStatus(status));
        }
        
        return userRepository.findAll(spec);
    }
}

// 8. Custom Repository 구현
public interface UserRepositoryCustom {
    List<User> findByComplexCondition(UserSearchCondition condition);
}

@RequiredArgsConstructor
public class UserRepositoryImpl implements UserRepositoryCustom {
    
    private final EntityManager em;
    
    @Override
    public List<User> findByComplexCondition(UserSearchCondition condition) {
        String jpql = "SELECT u FROM User u WHERE 1=1";
        
        if (condition.getName() != null) {
            jpql += " AND u.name = :name";
        }
        if (condition.getMinAge() != null) {
            jpql += " AND u.age >= :minAge";
        }
        
        TypedQuery<User> query = em.createQuery(jpql, User.class);
        
        if (condition.getName() != null) {
            query.setParameter("name", condition.getName());
        }
        if (condition.getMinAge() != null) {
            query.setParameter("minAge", condition.getMinAge());
        }
        
        return query.getResultList();
    }
}

// 인터페이스 상속
public interface UserRepository 
        extends JpaRepository<User, Long>, UserRepositoryCustom {
}

// 9. QueryDSL 연동 (타입 안전한 쿼리)
public interface UserRepository 
        extends JpaRepository<User, Long>, QuerydslPredicateExecutor<User> {
}

@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    
    public List<User> searchUsers(String name, int minAge) {
        QUser user = QUser.user;
        
        BooleanBuilder builder = new BooleanBuilder();
        
        if (name != null) {
            builder.and(user.name.eq(name));
        }
        builder.and(user.age.goe(minAge));
        
        return (List<User>) userRepository.findAll(builder);
    }
}

// 10. Projection (DTO 직접 조회)
public interface UserSummary {
    String getName();
    String getEmail();
}

public interface UserRepository extends JpaRepository<User, Long> {
    
    // 인터페이스 프로젝션
    List<UserSummary> findAllProjectedBy();
    
    // 클래스 프로젝션
    @Query("SELECT new com.example.dto.UserDto(u.name, u.email) " +
           "FROM User u")
    List<UserDto> findAllAsDto();
}

// 11. @EntityGraph (N+1 문제 해결)
public interface UserRepository extends JpaRepository<User, Long> {
    
    // EAGER 로딩으로 조회
    @EntityGraph(attributePaths = {"orders", "address"})
    @Query("SELECT u FROM User u")
    List<User> findAllWithOrdersAndAddress();
    
    // 특정 조건에만 EAGER
    @EntityGraph(attributePaths = "orders")
    Optional<User> findByEmail(String email);
}

// 12. Lock 사용
public interface ProductRepository extends JpaRepository<Product, Long> {
    
    // 비관적 락
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Optional<Product> findByIdWithLock(@Param("id") Long id);
    
    // 낙관적 락 (@Version 필드 필요)
    @Lock(LockModeType.OPTIMISTIC)
    Optional<Product> findById(Long id);
}
```

## 주의사항 / 함정

### 1. N+1 문제
```java
// ❌ N+1 문제 발생
@GetMapping("/users")
public List<UserDto> getUsers() {
    List<User> users = userRepository.findAll();  // 1번 쿼리
    return users.stream()
            .map(u -> new UserDto(u, u.getOrders()))  // N번 쿼리!
            .collect(Collectors.toList());
}

// ✅ Fetch Join으로 해결
@Query("SELECT u FROM User u LEFT JOIN FETCH u.orders")
List<User> findAllWithOrders();

// ✅ EntityGraph로 해결
@EntityGraph(attributePaths = "orders")
List<User> findAll();
```

### 2. @Modifying 없이 UPDATE/DELETE
```java
// ❌ @Modifying 없으면 예외 발생
@Query("UPDATE User u SET u.status = :status WHERE u.id = :id")
int updateStatus(@Param("id") Long id, @Param("status") UserStatus status);

// ✅ @Modifying 필수
@Modifying
@Query("UPDATE User u SET u.status = :status WHERE u.id = :id")
int updateStatus(@Param("id") Long id, @Param("status") UserStatus status);
```

### 3. @Modifying 후 영속성 컨텍스트 불일치
```java
@Transactional
public void updateAndFind(Long id) {
    User user = userRepository.findById(id).get();
    System.out.println(user.getStatus());  // ACTIVE
    
    // Bulk Update (영속성 컨텍스트 거치지 않음)
    userRepository.updateStatus(id, UserStatus.INACTIVE);
    
    User user2 = userRepository.findById(id).get();
    System.out.println(user2.getStatus());  // ❌ 여전히 ACTIVE!
}

// ✅ clearAutomatically = true
@Modifying(clearAutomatically = true)
@Query("UPDATE User u SET u.status = :status WHERE u.id = :id")
int updateStatus(@Param("id") Long id, @Param("status") UserStatus status);
```

### 4. delete 메서드의 비효율
```java
// ❌ 비효율: SELECT 후 DELETE
userRepository.deleteById(id);  // SELECT + DELETE

// ✅ 효율적: 바로 DELETE
@Modifying
@Query("DELETE FROM User u WHERE u.id = :id")
void deleteByIdDirectly(@Param("id") Long id);
```

### 5. Page vs Slice vs List
```java
// Page: 전체 개수 조회 (COUNT 쿼리 추가)
Page<User> page = userRepository.findAll(pageable);
long total = page.getTotalElements();  // COUNT 쿼리 실행

// Slice: 다음 페이지 존재 여부만 (COUNT 쿼리 없음)
Slice<User> slice = userRepository.findAll(pageable);
boolean hasNext = slice.hasNext();  // COUNT 쿼리 없음

// List: 페이징 메타 정보 없음 (가장 빠름)
List<User> list = userRepository.findAll();
```

### 6. Optional 잘못된 사용
```java
// ❌ Optional 불필요한 언박싱
Optional<User> userOpt = userRepository.findById(id);
if (userOpt.isPresent()) {
    User user = userOpt.get();
    // ...
}

// ✅ Optional 활용
User user = userRepository.findById(id)
        .orElseThrow(UserNotFoundException::new);
```

### 7. 쿼리 메서드 네이밍 제한
```java
// ❌ 너무 복잡한 메서드 이름
List<User> findByNameAndAgeGreaterThanAndStatusAndEmailContaining(
    String name, int age, UserStatus status, String email);

// ✅ @Query 사용
@Query("SELECT u FROM User u WHERE " +
       "u.name = :name AND u.age > :age AND " +
       "u.status = :status AND u.email LIKE %:email%")
List<User> searchUsers(@Param("name") String name, 
                       @Param("age") int age,
                       @Param("status") UserStatus status, 
                       @Param("email") String email);
```

## 관련 개념

### Spring 관련
- [[트랜잭션-관리]]
- [[트랜잭션-전파]]
- [[트랜잭션-격리수준]]

### JPA 기초 (선행 학습 권장)
- [[../../database/jpa/JPA-영속성컨텍스트-엔티티생명주기]]
- [[../../database/jpa/JPA-영속성컨텍스트-변경감지]]
- [[../../database/jpa/JPA-엔티티설계-NoArgsConstructor]]
- [[../../database/jpa/JPA-연관관계-매핑가이드]]
- [[../../database/jpa/JPA-성능최적化-N+1문제해결]]
- [[../../database/jpa/JPA-쿼리-JPQL과Criteria]]
- [[../../database/jpa/JPA-쿼리-QueryDSL]]

## 면접 질문

1. **JPA와 Spring Data JPA의 차이는?**
   - JPA: Java 표준 ORM 스펙
   - Spring Data JPA: JPA를 쉽게 사용하기 위한 Spring 프로젝트

2. **JpaRepository가 제공하는 기본 메서드는?**
   - save(), findById(), findAll(), delete(), count() 등

3. **N+1 문제란 무엇이고 해결 방법은?**
   - 연관 엔티티 조회 시 추가 쿼리 발생 (1 + N번)
   - Fetch Join, EntityGraph, Batch Size 설정으로 해결

4. **@Modifying을 사용하는 이유는?**
   - UPDATE, DELETE 쿼리임을 Spring Data JPA에 알림
   - 영속성 컨텍스트 관리 (clearAutomatically)

5. **Page와 Slice의 차이는?**
   - Page: 전체 개수 조회 (COUNT 쿼리)
   - Slice: 다음 페이지 존재 여부만 (COUNT 없음, 더 빠름)

6. **메서드 이름으로 쿼리 생성 규칙은?**
   - findBy, existsBy, countBy, deleteBy 등
   - And, Or, GreaterThan, LessThan, Containing 등 조합

7. **@EntityGraph를 사용하는 이유는?**
   - N+1 문제 해결
   - EAGER/LAZY 로딩 동적 변경

## 참고 자료
- 김영한의 스프링 데이터 JPA
- Spring Data JPA Reference Documentation
- https://docs.spring.io/spring-data/jpa/reference/
