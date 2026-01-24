---
tags:
  - study
  - jpa
  - spring
  - 영속성컨텍스트
  - 캐싱
created: 2026-01-23
difficulty: 상
---
# JPA-영속성컨텍스트-엔티티생명주기

🏷️기술 카테고리: JPA, Spring
💡핵심키워드: #영속성컨텍스트, #캐싱
💼 면접 빈출도: 최상

# 1. Abstract: 핵심 요약

**영속성 컨텍스트(Persistence Context)**는 JPA의 핵심으로, 엔티티를 영구 저장하기 전에 메모리에서 관리하는 **1차 캐시** 공간입니다. 이를 통해 **변경 감지(Dirty Checking)**, **동일성 보장**, **지연 로딩** 등을 구현합니다.

**핵심 원칙**:
- 영속성 컨텍스트 = 엔티티 관리자 (EntityManager)
- 1차 캐시: 같은 트랜잭션 내에서 동일성 보장
- 엔티티 생명주기: 비영속 → 영속 → 준영속 → 삭제

# 2. 영속성 컨텍스트란?

```java
@Service
public class UserService {
    @PersistenceContext
    private EntityManager em;
    
    @Transactional
    public void example() {
        // 1. 비영속 상태 (new)
        User user = new User("John", "john@example.com");
        
        // 2. 영속 상태 (persist)
        em.persist(user);  // 1차 캐시에 저장
        
        // 3. 동일성 보장
        User found = em.find(User.class, user.getId());
        System.out.println(user == found);  // true!
        
        // 4. 변경 감지 (Dirty Checking)
        user.changeName("Jane");  // UPDATE 쿼리 자동 생성
    }
}
```

# 3. 1차 캐시

**동작 방식**:

```java
@Transactional
public void cacheExample() {
    // 첫 번째 조회: DB에서 SELECT
    User user1 = em.find(User.class, 1L);
    
    // 두 번째 조회: 1차 캐시에서 가져오기 (DB 조회 X)
    User user2 = em.find(User.class, 1L);
    
    // 동일성 보장
    System.out.println(user1 == user2);  // true
}
```

# 4. 엔티티 생명주기

## 4.1 4가지 상태

```java
// 1. 비영속 (Transient)
User user = new User();  // JPA가 모르는 상태

// 2. 영속 (Managed)
em.persist(user);  // 영속성 컨텍스트가 관리

// 3. 준영속 (Detached)
em.detach(user);  // 영속성 컨텍스트에서 분리

// 4. 삭제 (Removed)
em.remove(user);  // 삭제 대상
```

## 4.2 상태별 특징

| 상태 | 변경 감지 | 1차 캐시 | 트랜잭션 |
| --- | --- | --- | --- |
| 비영속 | X | X | X |
| 영속 | O | O | O |
| 준영속 | X | X | X |
| 삭제 | X | X | O |

# 5. 변경 감지 (Dirty Checking)

```java
@Transactional
public void updateUser(Long id) {
    User user = em.find(User.class, id);
    
    // ✅ 엔티티 수정만 하면 된다!
    user.changeName("New Name");
    user.changeEmail("new@email.com");
    
    // ❌ em.update(user) 불필요!
    // 트랜잭션 커밋 시 자동으로 UPDATE SQL 실행
}
```

**작동 원리**:
1. 엔티티 조회 시 스냅샷 저장
2. 트랜잭션 커밋 시 비교
3. 변경 감지 시 UPDATE SQL 실행

# 6. Interview Readiness

## Q1: 영속성 컨텍스트란?

**A**: 엔티티를 영구 저장하기 전에 메모리에서 관리하는 **1차 캐시** 공간입니다. 동일 트랜잭션 내에서 같은 엔티티는 항상 동일한 객체(==)를 반환하여 동일성을 보장하고, 변경 감지로 자동 UPDATE를 제공합니다.

## Q2: 변경 감지가 작동하는 원리는?

**A**: JPA는 엔티티를 처음 조회할 때 스냅샷을 저장합니다. 트랜잭션 커밋 시점에 현재 엔티티 상태와 스냅샷을 비교하여 변경이 감지되면 자동으로 UPDATE SQL을 실행합니다.

## Q3: 1차 캐시의 장점은?

**A**:
1. 동일성 보장: 같은 ID는 같은 객체 반환 (==)
2. 성능 향상: 같은 트랜잭션 내 중복 조회 방지
3. 쓰기 지연: INSERT/UPDATE를 모아서 한 번에 실행

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
