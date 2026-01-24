---
tags:
  - study
  - design-pattern
  - java
  - 디자인패턴
  - 캐싱
created: 2026-01-08
difficulty: 상
---
# Java 정적 팩토리 메서드

🏷️기술 카테고리: Design Pattern, Java
💡핵심키워드: #디자인패턴, #캐싱
💼 면접 빈출도: 상

# 1. Abstract: 핵심 요약

정적 팩토리 메서드는 생성자(`new`)를 직접 사용하는 대신, 클래스 내부에 정적(static) 메서드를 만들어 객체 생성을 위임하는 디자인 패턴입니다.

**핵심 원칙**:
- 생성자 대신 이름이 있는 정적 메서드로 객체 생성
- 캐싱, 싱글턴, 하위 타입 객체 반환 가능
- JPA 엔티티에서 무분별한 생성을 방지

---

# 2. 정적 팩토리 메서드의 장점

## 1. 이름을 붙일 수 있음 (가독성)

생성자는 클래스 이름과 같아야 하지만, 메서드는 생성 목적을 이름에 담을 수 있습니다.

```java
// ❌ 생성자 - 의도 불명확
new MemberTicket(member, product, 10);

// ✅ 정적 팩토리 - 의도 명확
MemberTicket.createByPurchase(member, product);
MemberTicket.createByTransfer(member, product, count);
```

## 2. 객체 생성 제어 (캐싱)

생성자는 무조건 새 객체를 만들지만, 메서드는 캐시된 객체를 반환할 수 있습니다.

```java
// Boolean.valueOf() 예시
Boolean.valueOf(true);   // 항상 같은 TRUE 인스턴스 반환
Boolean.valueOf(false);  // 항상 같은 FALSE 인스턴스 반환
```

## 3. 하위 타입 객체 반환 가능

반환 타입을 인터페이스나 부모 클래스로 지정하고 실제로는 자식 클래스 객체를 반환할 수 있습니다.

```java
// Collections.unmodifiableList() 예시
public static <T> List<T> unmodifiableList(List<? extends T> list) {
    return new UnmodifiableList<>(list);  // 구현체 반환
}
```

---

# 3. 실무 적용

## 기본 구조

```java
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class MemberTicket extends BaseTimeEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "MBR_ID")
    private Member member;

    private int remainingCount;
    private String status;

    // ⭐️ 내부에서만 사용하는 생성자
    @Builder(access = AccessLevel.PRIVATE)
    private MemberTicket(Member member, int remainingCount, String status) {
        this.member = member;
        this.remainingCount = remainingCount;
        this.status = status;
    }

    // ⭐️ 정적 팩토리 메서드
    public static MemberTicket createFirstPurchase(Member member, TicketProduct product) {
        return MemberTicket.builder()
                .member(member)
                .remainingCount(product.getProvideCount())
                .status("ACT")
                .build();
    }

    public static MemberTicket createByTransfer(Member member, int count) {
        return MemberTicket.builder()
                .member(member)
                .remainingCount(count)
                .status("ACT")
                .build();
    }
}
```

## 서비스에서의 사용

```java
@Service
public class TicketService {
    
    public void purchaseTicket(Member member, TicketProduct product) {
        MemberTicket newTicket = MemberTicket.createFirstPurchase(member, product);
        repository.save(newTicket);
    }
}
```

**장점**: 생성자(`new`)는 테스트나 내부에서만 사용, 모든 객체 생성 로직이 엔티티에 응집

---

# 4. 네이밍 컨벤션

관례적으로 사용되는 메서드 이름:

| 메서드 이름 | 의미 | 예시 |
| --- | --- | --- |
| **`from`** | 매개변수 하나로 변환 | `Date.from(instant)` |
| **`of`** | 여러 매개변수로 조합 | `EnumSet.of(MONDAY, TUESDAY)` |
| **`valueOf`** | `from`/`of`의 더 자세한 버전 | `Integer.valueOf("123")` |
| **`create`** | 매번 새 인스턴스 생성 | `createFirstPurchase()` |
| **`newInstance`** | 새 인스턴스 생성 보장 | `Array.newInstance()` |

---

# 5. 주의사항

```java
// ❌ 잘못된 사용: public 생성자 + 팩토리 메서드
public class User {
    public User(String email) {}  // 생성자 노출
    public static User create(String email) { return new User(email); }
}

// ✅ 올바른 사용: protected 생성자 + 팩토리 메서드
public class User {
    @NoArgsConstructor(access = AccessLevel.PROTECTED)
    private User(String email) {}
    public static User create(String email) { return new User(email); }
}
```

---

**작성일**: 2026-01-08
**면접 빈출도**: ⭐⭐⭐⭐ (상)
