# [JPA 실무 패턴] 2/4 - Dirty Checking (변경 감지)

🏷️기술 카테고리: DataBase, JPA
💡핵심키워드: #JPA, #영속성컨텍스트, #트랜잭션
💼 면접 빈출도: 최상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 8일 오후 11:52
📅 다음 복습일: 2026년 1월 21일

## 🧐 Dirty Checking이란?

JPA가 엔티티의 상태 변화를 감지하여 트랜잭션이 끝나는 시점에 자동으로 DB에 반영(Update SQL 실행)해주는 기능입니다.

'Dirty'는 "상태가 변경됨"을 의미하고, 'Checking'은 "검사함"을 의미합니다.

---

## 🛠️ 작동 원리

JPA는 엔티티를 조회하면 그 상태 그대로를 복사해서 **스냅샷(Snapshot)**을 찍어 영속성 컨텍스트에 보관합니다.

1. **조회:** `Optional<MemberTicket> ticket = repository.findById(1L);` (스냅샷 생성)
2. **수정:** `ticket.use();` (엔티티의 필드 값 변경)
3. **트랜잭션 커밋:** 트랜잭션이 끝나는 시점에 JPA가 **현재 엔티티 상태**와 **조회 시점의 스냅샷**을 비교
4. **플러시(Flush):** 변경 사항 발견 시 JPA가 자동으로 `UPDATE` SQL을 생성해서 DB에 반영

---

## ✅ 작동 조건

이 마법이 작동하려면 반드시 지켜야 할 두 가지:

1. **영속 상태의 엔티티:** `find`로 가져온 엔티티이거나 이미 `save`된 엔티티여야 함 (준영속/비영속 X)
2. **트랜잭션 범위 내:** 반드시 서비스 메서드에 **`@Transactional`** 어노테이션 필요

---

## 💻 실무 코드 예시

### ❌ 나쁜 예 (무의미한 save 호출)

```java
@Transactional
public void useTicket(Long id) {
    MemberTicket ticket = repository.findById(id).get();
    ticket.setRemainingCount(ticket.getRemainingCount() - 1);
    
    // 불필요! JPA가 알아서 해줌
    [repository.save](http://repository.save)(ticket); 
}
```

### ✅ 좋은 예 (Dirty Checking 활용)

```java
@Transactional
public void useTicket(Long id) {
    // 1. 조회 (스냅샷 생성)
    MemberTicket ticket = repository.findById(id)
        .orElseThrow(() -> new EntityNotFoundException("티켓이 없습니다."));
    
    // 2. 비즈니스 메서드 호출 (상태 변경)
    ticket.use(); 
    
    // 3. 메서드 종료 시 트랜잭션 커밋 → JPA가 스냅샷과 비교 후 UPDATE 자동 실행
}
```

---

## 🏗️ Setter 대신 비즈니스 메서드를 써야 하는 이유

Dirty Checking은 필드 값이 바뀌기만 하면 무조건 UPDATE를 날립니다. 

만약 `Setter`가 열려 있어서 누군가 실수로 `ticket.setRemainingCount(0)`를 호출하면, 의도치 않게 DB 값이 0으로 바뀌어 버립니다.

**비즈니스 메서드(`use()`, `expire()`)를 사용하면:**

- 그 안에서 검증 로직을 넣을 수 있음
- Dirty Checking은 **안전하게 검증된 변경 사항만** DB에 반영

```java
public void use() {
    if (this.remainingCount <= 0) {
        throw new IllegalStateException("잔여 횟수가 없습니다.");
    }
    this.remainingCount--;
}
```

---

## 💡 추가 팁: @DynamicUpdate

기본적으로 JPA는 모든 필드를 업데이트하는 쿼리를 생성합니다. 

필드가 너무 많아서(30개 이상) 변경된 부분만 쿼리에 넣고 싶다면 엔티티 상단에 **`@DynamicUpdate`**를 붙이세요.

```java
@Entity
@DynamicUpdate
public class MemberTicket {
    // ...
}
```

**주의:** 일반적인 상황(필드 10개 내외)에서는 기본 쿼리가 쿼리 재사용성 측면에서 더 유리합니다.

---

## 💡 면접 대비 핵심 포인트

**질문:** "JPA에서 엔티티를 수정할 때 save()를 호출하지 않아도 되는 이유를 설명하세요."

**모범 답변:**

"JPA의 Dirty Checking(변경 감지) 기능 덕분입니다. 영속성 컨텍스트는 엔티티를 조회할 때의 초기 상태를 스냅샷으로 보관합니다. 트랜잭션이 커밋되는 시점에 현재 엔티티의 상태와 스냅샷을 비교하여, 변경된 부분이 있다면 쓰기 지연 SQL 저장소에 UPDATE 쿼리를 생성해 두었다가 한 번에 DB에 반영하기 때문입니다."