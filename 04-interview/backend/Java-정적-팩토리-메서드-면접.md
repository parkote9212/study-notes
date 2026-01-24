---
tags:
  - interview
  - java
  - design-pattern
created: 2026-01-08
difficulty: 상
---

# Java 정적 팩토리 메서드 (면접 Q&A)

## 질문
> 정적 팩토리 메서드의 장점은 무엇이며, 언제 사용하는 것이 좋은가요?

## 핵심 답변 (3줄)
1. **명확한 이름** - 생성 목적을 메서드 이름으로 표현, 의도가 명확함
2. **객체 생성 제어** - 캐싱, 싱글턴 등으로 메모리 효율성 향상
3. **하위 타입 반환** - 인터페이스로 선언하고 구현체 반환, 유연한 설계

## 상세 설명

정적 팩토리 메서드는 세 가지 주요 장점을 제공합니다:

**1. 메서드에 이름을 붙일 수 있음**

생성자는 클래스 이름과 같아야 하므로 다양한 생성 방식을 표현할 수 없습니다. 하지만 정적 팩토리 메서드는 생성 목적을 명확하게 드러낼 수 있습니다:

```java
// 생성자는 의도가 불명확
new MemberTicket(member, product, 10);

// 팩토리 메서드는 의도가 명확
MemberTicket.createByPurchase(member, product);
MemberTicket.createByTransfer(member, count);
```

**2. 호출할 때마다 새로운 객체를 생성하지 않아도 됨**

생성자는 무조건 새 객체를 생성하지만, 메서드는 미리 만들어둔 객체를 반환하거나 싱글턴처럼 관리할 수 있습니다:

```java
// Boolean.valueOf()는 불변 인스턴스 캐싱
Boolean.valueOf(true);   // 항상 같은 객체
Boolean.valueOf(false);  // 항상 같은 객체
```

이것이 중요한 이유는 객체 생성 비용을 줄일 수 있고, 같은 객체를 여러 곳에서 공유할 수 있기 때문입니다.

**3. 하위 타입 객체를 반환할 수 있음**

생성자는 정확히 그 클래스의 객체만 생성하지만, 팩토리 메서드는 인터페이스나 부모 클래스를 반환 타입으로 선언하고, 실제로는 상황에 맞는 자식 클래스 객체를 반환할 수 있습니다:

```java
public static <T> List<T> unmodifiableList(List<? extends T> list) {
    return new UnmodifiableList<>(list);  // 구현체 반환
}
```

**4. JPA 엔티티에서의 실무 활용**

특히 JPA 엔티티에서 `@NoArgsConstructor(protected)`와 함께 사용하면 효과적입니다:

```java
@Entity
public class MemberTicket {
    @Builder(access = AccessLevel.PRIVATE)
    private MemberTicket(...) {}
    
    public static MemberTicket createFirstPurchase(Member member, Product product) {
        return MemberTicket.builder()...build();
    }
}
```

이렇게 하면 무분별한 객체 생성을 방지하면서도 의미 있는 생성 경로를 제공할 수 있습니다.

## 코드 예시
```java
@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class User {
    @Id
    private Long id;
    private String email;
    
    @Builder(access = AccessLevel.PRIVATE)
    private User(String email) {
        this.email = email;
    }
    
    // ✅ 정적 팩토리 메서드
    public static User createFromEmail(String email) {
        validateEmail(email);
        return User.builder().email(email).build();
    }
    
    public static User createFromId(Long id) {
        return User.builder().id(id).build();
    }
}

// 사용
User user = User.createFromEmail("test@example.com");
```

## 꼬리 질문 예상
- "생성자를 private으로 감싸면 반드시 팩토리 메서드를 써야 하나요?" → 테스트 코드에서 쓸 수 없으므로 package-private이 나을 수 있습니다.
- "팩토리 메서드의 이름은 정해져 있나요?" → 컨벤션이 있습니다. `from`, `of`, `valueOf`, `create`, `newInstance` 등이 일반적입니다.

## 참고
- [[Java-정적-팩토리-메서드]]
- Effective Java Item 1
