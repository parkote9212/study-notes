---
tags:
  - interview
  - JPA
  - Concurrency
  - Transaction
created: 2026-01-20
difficulty: 상
---

# JPA에서 동시성 문제를 어떻게 해결하나요?

## 질문
> 여러 사용자가 동시에 같은 데이터를 수정할 때 발생하는 동시성 문제를 JPA에서 어떻게 해결할 수 있나요?

## 핵심 답변 (3줄)
1. **Pessimistic Lock**: `@Lock(LockModeType.PESSIMISTIC_WRITE)`로 SELECT FOR UPDATE 쿼리를 실행해 트랜잭션 종료까지 다른 접근 차단
2. **Optimistic Lock**: `@Version` 어노테이션으로 버전 필드를 관리하여 수정 시 버전 불일치 시 예외 발생
3. 충돌 확률이 높으면 Pessimistic, 낮으면 Optimistic을 선택하며, 반드시 @Transactional과 함께 사용

## 상세 설명

### 1. Pessimistic Lock (비관적 락)

**언제 사용?**
- 충돌 확률이 높을 때 (예: 예산 차감, 재고 감소, 좌석 예약)
- 데이터 정합성이 매우 중요할 때

**구현 방법:**
```java
@Repository
public interface ProjectRepository extends JpaRepository<Project, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Project p WHERE p.projectId = :id")
    Optional<Project> findByIdForUpdate(@Param("id") Long id);
}

@Service
@Transactional  // 필수!
public class ApprovalService {
    private void deductBudget(Long projectId, BigDecimal amount) {
        Project project = projectRepository
            .findByIdForUpdate(projectId)
            .orElseThrow();
        
        project.spendBudget(amount);  // 안전하게 차감
    }
}
```

**장점:**
- 데이터 정합성 확실히 보장
- 충돌 발생 시 대기만 하면 됨

**단점:**
- 성능 저하 (대기 시간 발생)
- DeadLock 위험

### 2. Optimistic Lock (낙관적 락)

**언제 사용?**
- 충돌 확률이 낮을 때
- 읽기가 많고 쓰기가 적을 때

**구현 방법:**
```java
@Entity
public class Product {
    @Id
    private Long id;
    
    @Version  // JPA가 자동으로 버전 관리
    private Long version;
    
    private Integer stock;
}

// Service
@Transactional
public void decreaseStock(Long productId, Integer quantity) {
    Product product = productRepository.findById(productId).orElseThrow();
    product.decreaseStock(quantity);
    // UPDATE 시 version이 일치하지 않으면 OptimisticLockException 발생
}
```

**장점:**
- 성능 좋음 (락 없음)
- DeadLock 없음

**단점:**
- 충돌 시 재시도 로직 필요
- 충돌 많으면 비효율적

### 3. 비교표

| 구분 | Pessimistic Lock | Optimistic Lock |
|------|------------------|-----------------|
| **전략** | 충돌 예상 | 충돌 거의 없음 예상 |
| **구현** | @Lock + FOR UPDATE | @Version |
| **성능** | 느림 (대기) | 빠름 |
| **충돌 처리** | 대기 | 예외 + 재시도 |
| **적합 상황** | 예산, 재고, 좌석 | 게시글, 프로필 |

## 코드 예시 (필요시)
```java
// 실무 예시: BizSync 예산 차감
@Service
@RequiredArgsConstructor
@Transactional
public class ApprovalService {
    
    private final ProjectRepository projectRepository;
    
    private void deductBudget(ApprovalDocument document) {
        // Pessimistic Lock으로 안전하게 조회
        Project project = projectRepository
            .findByIdForUpdate(document.getProject().getProjectId())
            .orElseThrow();
        
        // 예산 차감
        try {
            project.spendBudget(document.getAmount());
        } catch (IllegalStateException e) {
            throw new IllegalStateException(
                "예산 부족: " + e.getMessage()
            );
        }
    }
}
```

## 꼬리 질문 예상
- **Q1: @Transactional이 왜 필수인가요?**
  - A: Lock은 트랜잭션 범위 내에서만 유지되며, 트랜잭션이 커밋/롤백될 때 락이 해제됩니다.

- **Q2: DeadLock을 어떻게 방지하나요?**
  - A: 락을 거는 순서를 통일하고, Timeout을 설정합니다.

- **Q3: Optimistic Lock 충돌 시 어떻게 처리하나요?**
  - A: OptimisticLockException을 catch하여 일정 횟수 재시도합니다.

- **Q4: 분산 환경에서는 어떻게 동시성을 제어하나요?**
  - A: Redis의 분산 락(Redisson 등)을 사용합니다.

## 참고
- [[Pessimistic_Lock_동시성제어]]
- [[트랜잭션_격리수준]]
- [[SELECT_FOR_UPDATE]]
