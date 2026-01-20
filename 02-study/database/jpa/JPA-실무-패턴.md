# JPA 실무 패턴: N+1 문제와 해결 전략

🏷️기술 카테고리: JPA, ORM
💡핵심키워드: #N+1, #성능최적화
💼 면접 빈출도: 최상

# 1. N+1 문제란?

한 번의 쿼리로 N개의 데이터를 조회한 후, 각 데이터에 대해 추가로 N번의 쿼리가 실행되는 문제입니다.

```java
// 1개 쿼리: 모든 사용자 조회
List<User> users = userRepository.findAll();

// N개 쿼리: 각 사용자의 주문 조회
for (User user : users) {
    List<Order> orders = user.getOrders();  // N번 쿼리 실행!
}
```

---

# 2. 원인과 해결 방법

## 2.1 Lazy Loading의 함정

```java
@Entity
public class User {
    @OneToMany(fetch = FetchType.LAZY)  // 기본값
    private List<Order> orders;
}
```

**해결 1: Eager Loading**
```java
@OneToMany(fetch = FetchType.EAGER)
private List<Order> orders;
```

**해결 2: FETCH JOIN**
```java
@Query("SELECT u FROM User u JOIN FETCH u.orders")
List<User> findAllWithOrders();
```

**해결 3: @EntityGraph**
```java
@EntityGraph(attributePaths = {"orders"})
@Query("SELECT u FROM User u")
List<User> findAll();
```

---

# 3. Dirty Checking (변경 감지)

JPA는 엔티티의 변화를 추적하여 자동으로 UPDATE 쿼리를 생성합니다.

```java
@Transactional
public void updateUser(Long id, String newName) {
    User user = userRepository.findById(id).orElseThrow();
    user.setName(newName);  // 변경 감지 → UPDATE 자동 생성
    // repository.save() 호출 불필요!
}
```

---

# 4. @NoArgsConstructor 필수 이유

JPA는 리플렉션으로 엔티티를 생성하므로 기본 생성자가 필수입니다.

```java
@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class User {
    // JPA가 이 생성자를 사용하여 엔티티 인스턴스 생성
}
```

---

# 5. 도메인 모델 패턴

Setter를 최소화하고 비즈니스 메서드로 상태 변경을 관리합니다.

```java
@Entity
public class Order {
    private Long id;
    private OrderStatus status;
    private List<OrderItem> items;
    
    // Setter 없음!
    
    // 비즈니스 메서드
    public void cancel() {
        if (this.status == OrderStatus.DELIVERED) {
            throw new IllegalStateException("배송 완료 주문은 취소 불가");
        }
        this.status = OrderStatus.CANCELLED;
    }
}
```

---

**작성일**: 2026년
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
