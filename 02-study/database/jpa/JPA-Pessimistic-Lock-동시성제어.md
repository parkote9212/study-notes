---
tags:
  - study
  - jpa
  - lock
  - concurrency
created: 2026-01-24
difficulty: 중
---

# Pessimistic Lock 동시성 제어

## 한 줄 요약
> JPA의 `@Lock(LockModeType.PESSIMISTIC_WRITE)`로 SELECT FOR UPDATE 쿼리를 실행하여 동시 접근을 차단하고 데이터 정합성 보장

## 상세 설명

여러 사용자가 동시에 같은 데이터를 수정하려 할 때, 락이 없으면 데이터 정합성이 깨집니다. Pessimistic Lock은 "동시 접근이 일어날 것이다"라고 비관적으로 가정하여 데이터를 읽는 순간 락을 걸어 다른 요청을 대기시킵니다.

### 문제 상황

```
시간 | 요청 A (50만원)     | 요청 B (60만원)
-----|-------------------|-------------------
t1   | 잔액 100만원 읽음  |
t2   |                   | 잔액 100만원 읽음
t3   | 50만원 차감       |
t4   |                   | 60만원 차감
결과 | DB 잔액: 40만원 (실제는 -10만원이어야 함!)
```

### Pessimistic Lock 해결 방법

**동작 원리**:
1. 데이터 조회 시 FOR UPDATE 락 획득
2. 트랜잭션 종료까지 다른 트랜잭션 대기
3. 락 해제 후 다음 트랜잭션 실행

**장점**: 데이터 정합성 완벽 보장
**단점**: 대기 시간 발생 (성능 저하)

### Pessimistic vs Optimistic Lock

| 구분 | Pessimistic Lock | Optimistic Lock |
|------|------------------|-----------------|
| **전략** | 충돌이 일어날 것이라 가정 | 충돌이 거의 없을 것이라 가정 |
| **구현** | `SELECT ... FOR UPDATE` | `@Version` 컬럼 사용 |
| **성능** | 대기 시간 발생 (느림) | 빠름 (락 없음) |
| **충돌 처리** | 대기 후 처리 | 재시도 필요 |
| **적합한 상황** | 충돌 확률 높음 (예산, 재고) | 충돌 확률 낮음 (읽기 위주) |

## 코드 예시

```java
// 1. Repository에 Lock 메서드 정의
@Repository
public interface ProjectRepository extends JpaRepository<Project, Long> {
    
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Project p WHERE p.projectId = :id")
    Optional<Project> findByIdForUpdate(@Param("id") Long id);
}

// 2. Service에서 사용
@Service
@Transactional  // ⚠️ 필수!
public class ApprovalService {
    
    private void deductBudget(ApprovalDocument document) {
        // FOR UPDATE 락 걸고 조회
        Project project = projectRepository
            .findByIdForUpdate(document.getProject().getProjectId())
            .orElseThrow(() -> 
                new IllegalArgumentException("프로젝트를 찾을 수 없습니다."));
        
        // 안전하게 예산 차감
        try {
            project.spendBudget(document.getAmount());
            // JPA Dirty Checking으로 자동 UPDATE
        } catch (IllegalStateException e) {
            throw new IllegalStateException(
                "예산 부족: 요청 " + document.getAmount() + 
                "원, 잔액 " + (project.getTotalBudget()
                    .subtract(project.getUsedBudget())) + "원"
            );
        }
    }
}

// 3. Entity 메서드
@Entity
public class Project {
    
    public void spendBudget(BigDecimal amount) {
        BigDecimal expectedUsage = this.usedBudget.add(amount);
        
        if (this.totalBudget.compareTo(expectedUsage) < 0) {
            throw new IllegalStateException("예산이 초과되었습니다.");
        }
        this.usedBudget = expectedUsage;
    }
}

// 실행되는 SQL
SELECT * FROM project WHERE project_id = ? FOR UPDATE;
-- 트랜잭션 종료까지 다른 트랜잭션 차단
```

## 주의사항 / 함정

1. **@Transactional 필수**: 없으면 락이 즉시 해제됨
2. **DeadLock 위험**: 여러 테이블 락 시 순서 통일, Timeout 설정 권장
3. **성능 저하**: 동시 요청이 많으면 느려짐
4. **충돌 확률 고려**: 낮으면 Optimistic Lock 고려

```java
// ❌ 잘못된 예
public void deductBudget() {
    Project p = projectRepository.findByIdForUpdate(id).orElseThrow();
    // Lock이 즉시 해제됨!
}

// ✅ 올바른 예
@Transactional
public void deductBudget() {
    Project p = projectRepository.findByIdForUpdate(id).orElseThrow();
    // 메서드 종료까지 Lock 유지
}
```

## 관련 개념
- [[JPA-Lock-전략]]
- [[트랜잭션-격리수준]]
- [[Optimistic-Lock]]
- [[SELECT-FOR-UPDATE]]

## 면접 질문
1. Pessimistic Lock과 Optimistic Lock의 차이는?
2. SELECT FOR UPDATE가 무엇이며 언제 사용하나?
3. @Transactional 없이 Lock을 사용하면 어떻게 되나?
4. DeadLock을 방지하는 방법은?

## 참고 자료
- Spring Data JPA Lock 공식 문서
- 실무 프로젝트: BizSync
