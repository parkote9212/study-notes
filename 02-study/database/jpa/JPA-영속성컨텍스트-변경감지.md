# JPA-영속성컨텍스트-변경감지

🏷️기술 카테고리: DataBase, JPA
💡핵심키워드: #JPA, #영속성컨텍스트, #트랜잭션
💼 면접 빈출도: 최상

# 1. Abstract: 핵심 요약

JPA가 엔티티의 상태 변화를 감지하여 트랜잭션이 끝나는 시점에 자동으로 DB에 반영(Update SQL 실행)해주는 기능입니다.

**핵심 원칙**:
- 영속성 컨텍스트가 스냅샷을 보관
- 트랜잭션 커밋 시 스냅샷과 비교
- 변경 사항을 자동으로 UPDATE

# 2. Dirty Checking 작동 원리

JPA는 엔티티를 조회하면 그 상태 그대로를 복사해서 **스냅샷(Snapshot)**을 찍어 영속성 컨텍스트에 보관합니다.

1. **조회**: `Optional<MemberTicket> ticket = repository.findById(1L);` (스냅샷 생성)
2. **수정**: `ticket.use();` (엔티티의 필드 값 변경)
3. **트랜잭션 커밋**: JPA가 현재 엔티티 상태와 스냅샷을 비교
4. **플러시(Flush)**: 변경 사항 발견 시 자동으로 UPDATE SQL 생성 및 실행

# 3. 작동 조건

이 기능이 작동하려면 반드시:

1. **영속 상태의 엔티티**: find로 가져온 엔티티이거나 이미 save된 엔티티 (준영속/비영속 X)
2. **트랜잭션 범위 내**: 반드시 `@Transactional` 필요

# 4. 실무 코드 예시

```java
// ❌ 나쁜 예 (무의미한 save 호출)
@Transactional
public void useTicket(Long id) {
    MemberTicket ticket = repository.findById(id).get();
    ticket.setRemainingCount(ticket.getRemainingCount() - 1);
    repository.save(ticket);  // 불필요!
}

// ✅ 좋은 예 (Dirty Checking 활용)
@Transactional
public void useTicket(Long id) {
    MemberTicket ticket = repository.findById(id)
        .orElseThrow(() -> new EntityNotFoundException("티켓이 없습니다."));
    ticket.use();  // 메서드 종료 시 자동 UPDATE
}

// Entity 내부
public void use() {
    if (this.remainingCount <= 0) {
        throw new IllegalStateException("잔여 횟수가 없습니다.");
    }
    this.remainingCount--;
}
```

# 5. Setter 대신 비즈니스 메서드

Dirty Checking은 필드 값이 바뀌기만 하면 무조건 UPDATE를 날립니다. Setter가 열려 있으면 의도치 않은 변경이 발생할 수 있습니다.

**비즈니스 메서드 사용 시 장점**:
- 검증 로직 포함 가능
- 안전하게 검증된 변경 사항만 DB에 반영
- 코드의 의도가 명확해짐

# 6. @DynamicUpdate

기본적으로 JPA는 모든 필드를 업데이트하는 쿼리를 생성합니다. 필드가 너무 많으면(30개 이상) `@DynamicUpdate`를 고려하세요.

```java
@Entity
@DynamicUpdate
public class MemberTicket {
    // 변경된 필드만 UPDATE
}
```

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
