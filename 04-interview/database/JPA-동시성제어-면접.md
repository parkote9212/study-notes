---
tags: interview, JPA, Database, Lock
created: 2026-01-24
difficulty: 상
---

# JPA 동시성 제어 면접

## 질문
> Pessimistic Lock, Optimistic Lock, 동시성 문제, SELECT FOR UPDATE, 트랜잭션 격리수준

## 핵심 답변 (3줄)
1. Pessimistic Lock은 SELECT FOR UPDATE로 데이터를 읽는 순간 락을 걸어 동시 접근 차단
2. Optimistic Lock은 @Version으로 충돌 감지 후 재시도, 충돌 확률 낮을 때 사용
3. @Transactional 필수이며 DeadLock 방지를 위해 락 획득 순서 통일과 Timeout 설정 필요

## 상세 설명

### Q1: Pessimistic Lock과 Optimistic Lock의 차이는?

**A**:

| 구분 | Pessimistic Lock | Optimistic Lock |
|------|------------------|-----------------|
| **전략** | 충돌이 일어날 것이라 가정 | 충돌이 거의 없을 것이라 가정 |
| **구현** | `SELECT ... FOR UPDATE` | `@Version` 컬럼 사용 |
| **성능** | 대기 시간 발생 (느림) | 빠름 (락 없음) |
| **충돌 처리** | 대기 후 처리 | 재시도 필요 |
| **적합한 상황** | 충돌 확률 높음 (예산, 재고) | 충돌 확률 낮음 (읽기 위주) |

```java
// Pessimistic Lock
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT p FROM Project p WHERE p.projectId = :id")
Optional<Project> findByIdForUpdate(@Param("id") Long id);

// Optimistic Lock
@Entity
public class Product {
    @Version
    private Long version;
}
```

---

### Q2: SELECT FOR UPDATE가 무엇이며 언제 사용하나?

**A**: SELECT FOR UPDATE는 데이터를 조회하면서 동시에 해당 행에 배타적 락을 거는 SQL 명령입니다.

**동작 원리**:
1. 트랜잭션이 SELECT FOR UPDATE 실행
2. 해당 행에 배타적 락 획득
3. 다른 트랜잭션은 락이 해제될 때까지 대기
4. 트랜잭션 커밋/롤백 시 락 해제

**사용 시기**:
- 동시 수정 확률이 높은 경우 (재고, 예산, 좌석 예약)
- 데이터 정합성이 매우 중요한 경우
- Lost Update 문제를 방지해야 할 때

```java
@Transactional
public void deductBudget(Long projectId, BigDecimal amount) {
    Project project = projectRepository
        .findByIdForUpdate(projectId)
        .orElseThrow();
    
    project.spendBudget(amount);  // 안전하게 차감
}
```

---

### Q3: @Transactional 없이 Lock을 사용하면 어떻게 되나?

**A**: 락이 즉시 해제되어 동시성 제어가 되지 않습니다.

```java
// ❌ 잘못된 예
public void deductBudget() {
    Project p = projectRepository.findByIdForUpdate(id).orElseThrow();
    // 메서드 종료 → 즉시 락 해제!
    // 다른 트랜잭션이 동시에 접근 가능
}

// ✅ 올바른 예
@Transactional
public void deductBudget() {
    Project p = projectRepository.findByIdForUpdate(id).orElseThrow();
    p.spendBudget(amount);
    // 트랜잭션 종료까지 락 유지
}
```

**이유**: JPA는 트랜잭션 범위 안에서 영속성 컨텍스트를 관리하고, 트랜잭션이 없으면 즉시 닫혀버리기 때문입니다.

---

### Q4: DeadLock을 방지하는 방법은?

**A**:

**원인**: 두 개 이상의 트랜잭션이 서로의 락을 기다리는 상황

```
트랜잭션 A: 프로젝트 1 락 → 프로젝트 2 대기
트랜잭션 B: 프로젝트 2 락 → 프로젝트 1 대기
→ DeadLock!
```

**방지 방법**:

1. **락 획득 순서 통일**
```java
// ✅ 항상 ID 오름차순으로 락 획득
List<Long> sortedIds = projectIds.stream().sorted().collect(Collectors.toList());
for (Long id : sortedIds) {
    projectRepository.findByIdForUpdate(id);
}
```

2. **Timeout 설정**
```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
@QueryHints({@QueryHint(name = "javax.persistence.lock.timeout", value = "3000")})
Optional<Project> findByIdForUpdate(Long id);
```

3. **트랜잭션 짧게 유지**
```java
@Transactional
public void deductBudget() {
    // 필요한 작업만 빠르게 처리
    Project p = projectRepository.findByIdForUpdate(id).orElseThrow();
    p.spendBudget(amount);
}
```

---

### Q5: Lost Update 문제란?

**A**: 두 트랜잭션이 동시에 같은 데이터를 읽고 수정하여 한 쪽의 변경사항이 사라지는 문제입니다.

```
시간 | 트랜잭션 A        | 트랜잭션 B
-----|------------------|------------------
t1   | 잔액 100 읽음    |
t2   |                  | 잔액 100 읽음
t3   | 50 차감 (50 저장)|
t4   |                  | 60 차감 (40 저장)
결과 | A의 변경사항 소실! 잔액 40 (실제는 -10이어야 함)
```

**해결책**: Pessimistic Lock 또는 Optimistic Lock 사용

---

### Q6: 트랜잭션 격리수준과 락의 관계는?

**A**:

| 격리수준 | Dirty Read | Non-Repeatable Read | Phantom Read |
|---------|------------|---------------------|--------------|
| **READ UNCOMMITTED** | 발생 | 발생 | 발생 |
| **READ COMMITTED** | 방지 | 발생 | 발생 |
| **REPEATABLE READ** | 방지 | 방지 | 발생 |
| **SERIALIZABLE** | 방지 | 방지 | 방지 |

**Pessimistic Lock과의 관계**:
- PESSIMISTIC_WRITE는 SERIALIZABLE과 유사한 효과
- 격리수준이 낮아도 명시적으로 강한 락 보장 가능

```java
// Spring Boot 기본: REPEATABLE READ (MySQL InnoDB)
// Pessimistic Lock으로 더 강한 보장 가능
```

---

### Q7: 낙관적 락 충돌 시 재시도 전략은?

**A**:

```java
@Service
public class OrderService {
    
    private static final int MAX_RETRIES = 3;
    
    @Transactional
    public void updateStock(Long productId, int quantity) {
        int retryCount = 0;
        
        while (retryCount < MAX_RETRIES) {
            try {
                Product product = productRepository.findById(productId).orElseThrow();
                product.decreaseStock(quantity);
                productRepository.save(product);
                return;  // 성공
            } catch (OptimisticLockException e) {
                retryCount++;
                if (retryCount >= MAX_RETRIES) {
                    throw new RuntimeException("재고 차감 실패: 재시도 횟수 초과");
                }
                // 잠시 대기 후 재시도
                Thread.sleep(100);
            }
        }
    }
}
```

**주의**: 무한 재시도는 금지, 최대 재시도 횟수 설정 필수

---

### Q8: 읽기 전용 트랜잭션에서 락이 필요한가?

**A**: 대부분 불필요하지만, 특정 상황에서는 필요합니다.

**불필요한 경우** (대부분):
```java
@Transactional(readOnly = true)
public List<User> findAllUsers() {
    return userRepository.findAll();  // 락 불필요
}
```

**필요한 경우**:
- 조회한 데이터를 기반으로 중요한 의사결정을 할 때
- 조회 중 데이터가 변경되면 안 되는 경우

```java
@Transactional(readOnly = true)
public BigDecimal calculateRemainingBudget(Long projectId) {
    // 계산 중 예산이 변경되면 안 됨
    Project project = projectRepository
        .findByIdWithSharedLock(projectId)  // PESSIMISTIC_READ
        .orElseThrow();
    
    return project.getTotalBudget().subtract(project.getUsedBudget());
}
```

---

### Q9: 분산 환경에서 동시성 제어는?

**A**: 단일 서버의 락만으로는 부족하며, 분산 락이 필요합니다.

**방법**:
1. **Redis 분산 락**: Redisson 사용
2. **DB 레벨 락**: SELECT FOR UPDATE (여러 서버에서도 동작)
3. **Zookeeper**: 분산 코디네이션

```java
// Redis 분산 락 예시
@Service
public class OrderService {
    
    private final RedissonClient redissonClient;
    
    public void processOrder(Long orderId) {
        RLock lock = redissonClient.getLock("order:" + orderId);
        
        try {
            boolean isLocked = lock.tryLock(10, 30, TimeUnit.SECONDS);
            if (isLocked) {
                // 주문 처리
            }
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            lock.unlock();
        }
    }
}
```

---

### Q10: 성능과 정합성 트레이드오프는?

**A**: 상황에 따라 적절한 전략을 선택해야 합니다.

**정합성이 최우선** (금융, 재고):
- Pessimistic Lock 사용
- 성능 저하 감수

**성능이 우선** (조회수, 좋아요):
- Optimistic Lock 또는 비동기 처리
- 약간의 오차 허용

**균형점** (대부분 상황):
- 충돌 확률에 따라 선택
- 높으면 Pessimistic, 낮으면 Optimistic

```java
// 재고 (정합성 최우선)
@Lock(LockModeType.PESSIMISTIC_WRITE)
Optional<Product> findByIdForUpdate(Long id);

// 조회수 (성능 우선)
@Async
public void increaseViewCount(Long postId) {
    // 비동기로 처리, 약간의 오차 허용
}
```

## 꼬리 질문 예상
- Named Lock과 Pessimistic Lock의 차이는?
- Gap Lock이란?
- 2PL(Two-Phase Locking) 프로토콜이란?

## 참고
- [[JPA-Pessimistic-Lock-동시성제어]]
- [[Optimistic-Lock]]
- [[트랜잭션-격리수준]]
- [[분산-락]]
