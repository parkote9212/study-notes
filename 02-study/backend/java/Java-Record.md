---
tags:
  - study
  - java
  - record
  - java17
  - immutable
created: 2025-02-02
---

# Java Record

## 한 줄 요약
> 불변 데이터 클래스를 간결하게 정의하는 Java 17 신기능

## 상세 설명

### Record의 기본 개념

Record는 Java 14에서 프리뷰로 도입되고 Java 16에서 정식 기능이 된 특수한 클래스입니다. 데이터 전달 목적의 불변 클래스(DTO, VO)를 간결하게 작성할 수 있습니다.

**자동 생성되는 것들**
1. private final 필드
2. public 생성자
3. getter 메서드 (getXxx() 아닌 필드명())
4. equals(), hashCode()
5. toString()

### Record를 사용하는 이유

**기존 방식의 문제점**
- 보일러플레이트 코드 과다
- Lombok 의존성 필요
- 실수 가능성 (equals/hashCode 누락)

**Record의 장점**
- 코드 간결성
- 컴파일 타임 안정성
- 불변성 보장
- 표준 Java 기능

## 코드 예시

### 기본 Record 선언

```java
// ❌ 기존 방식 - 약 50줄
public class Person {
    private final String name;
    private final int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String getName() { return name; }
    public int getAge() { return age; }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && Objects.equals(name, person.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
    
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
}

// ✅ Record - 1줄
public record Person(String name, int age) {}
```

### Record 사용

```java
record Person(String name, int age) {}

// 생성
Person person = new Person("홍길동", 30);

// getter (필드명으로 호출)
String name = person.name();  // getXxx() 아님!
int age = person.age();

// toString()
System.out.println(person);  
// Person[name=홍길동, age=30]

// equals()
Person p1 = new Person("홍길동", 30);
Person p2 = new Person("홍길동", 30);
System.out.println(p1.equals(p2));  // true

// hashCode()
System.out.println(p1.hashCode() == p2.hashCode());  // true
```

### 컴팩트 생성자

```java
record Person(String name, int age) {
    // 컴팩트 생성자 - 유효성 검증
    public Person {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("이름은 필수입니다");
        }
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException("나이가 올바르지 않습니다");
        }
        // 필드 할당은 자동으로 수행됨
    }
}

// 사용
Person person = new Person("홍길동", 30);  // OK
// Person invalid = new Person("", 30);  // IllegalArgumentException
```

### 정규 생성자 (커스터마이징)

```java
record Person(String name, int age) {
    // 정규 생성자 - 값 변환
    public Person(String name, int age) {
        this.name = name.trim().toUpperCase();  // 변환
        this.age = Math.max(0, age);  // 음수 방지
    }
}

// 사용
Person person = new Person("  hong  ", -5);
System.out.println(person.name());  // "HONG"
System.out.println(person.age());   // 0
```

### 추가 생성자

```java
record Person(String name, int age, String email) {
    // 기본 생성자
    public Person(String name, int age) {
        this(name, age, null);  // 위임
    }
    
    // 이름만 받는 생성자
    public Person(String name) {
        this(name, 0, null);
    }
}

// 사용
Person p1 = new Person("홍길동", 30, "hong@example.com");
Person p2 = new Person("김철수", 25);
Person p3 = new Person("이영희");
```

### 메서드 추가

```java
record Person(String name, int age) {
    // 인스턴스 메서드
    public boolean isAdult() {
        return age >= 18;
    }
    
    public String getDisplayName() {
        return name + " (" + age + "세)";
    }
    
    // 정적 메서드
    public static Person of(String name, int age) {
        return new Person(name, age);
    }
}

// 사용
Person person = Person.of("홍길동", 30);
System.out.println(person.isAdult());  // true
System.out.println(person.getDisplayName());  // 홍길동 (30세)
```

### 제네릭 Record

```java
record Pair<T, U>(T first, U second) {}

// 사용
Pair<String, Integer> pair1 = new Pair<>("name", 30);
Pair<Integer, String> pair2 = new Pair<>(1, "first");

System.out.println(pair1.first());   // "name"
System.out.println(pair1.second());  // 30
```

### 실전 예시: DTO

```java
// API 응답 DTO
record UserResponse(
    Long id,
    String username,
    String email,
    LocalDateTime createdAt
) {
    // 변환 메서드
    public static UserResponse from(User user) {
        return new UserResponse(
            user.getId(),
            user.getUsername(),
            user.getEmail(),
            user.getCreatedAt()
        );
    }
}

// 사용
User user = userRepository.findById(1L);
UserResponse response = UserResponse.from(user);
```

### 실전 예시: 값 객체 (VO)

```java
record Money(BigDecimal amount, String currency) {
    public Money {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("금액은 0 이상이어야 합니다");
        }
        if (currency == null || currency.isBlank()) {
            throw new IllegalArgumentException("통화는 필수입니다");
        }
    }
    
    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("통화가 다릅니다");
        }
        return new Money(
            this.amount.add(other.amount),
            this.currency
        );
    }
    
    public Money multiply(int multiplier) {
        return new Money(
            this.amount.multiply(BigDecimal.valueOf(multiplier)),
            this.currency
        );
    }
}

// 사용
Money price = new Money(new BigDecimal("10000"), "KRW");
Money total = price.multiply(3);
System.out.println(total);  // Money[amount=30000, currency=KRW]
```

### 실전 예시: 이벤트 객체

```java
record OrderCreatedEvent(
    String orderId,
    String userId,
    BigDecimal amount,
    LocalDateTime createdAt
) {
    public OrderCreatedEvent(String orderId, String userId, BigDecimal amount) {
        this(orderId, userId, amount, LocalDateTime.now());
    }
}

// 사용
OrderCreatedEvent event = new OrderCreatedEvent("ORD-001", "USER-123", new BigDecimal("50000"));
eventPublisher.publish(event);
```

### 중첩 Record

```java
record Order(
    String orderId,
    Customer customer,
    List<Item> items
) {
    record Customer(String name, String email) {}
    record Item(String productId, int quantity, BigDecimal price) {}
}

// 사용
Order order = new Order(
    "ORD-001",
    new Order.Customer("홍길동", "hong@example.com"),
    List.of(
        new Order.Item("P001", 2, new BigDecimal("10000")),
        new Order.Item("P002", 1, new BigDecimal("20000"))
    )
);
```

### 인터페이스 구현

```java
interface Identifiable {
    Long getId();
}

record User(Long id, String name) implements Identifiable {
    // getId() 자동 구현됨 (id() 메서드가 있으므로)
}

// 또는 명시적 구현
record Product(Long productId, String name) implements Identifiable {
    @Override
    public Long getId() {
        return productId;
    }
}
```

### Record vs 일반 클래스

```java
// Record - 불변 데이터
record Point(int x, int y) {}

// 일반 클래스 - 가변 상태 필요
class MutablePoint {
    private int x;
    private int y;
    
    public void move(int dx, int dy) {
        this.x += dx;
        this.y += dy;
    }
}
```

### Record vs Lombok

```java
// Lombok
@Data
@AllArgsConstructor
public class PersonLombok {
    private final String name;
    private final int age;
}

// Record (의존성 불필요)
record Person(String name, int age) {}
```

### 컬렉션과 함께 사용

```java
record Product(String id, String name, int price) {}

List<Product> products = List.of(
    new Product("P001", "노트북", 1000000),
    new Product("P002", "마우스", 30000),
    new Product("P003", "키보드", 50000)
);

// Stream과 함께
products.stream()
    .filter(p -> p.price() > 40000)
    .map(Product::name)
    .forEach(System.out::println);
```

### Pattern Matching과 함께 (Java 21+)

```java
record Point(int x, int y) {}

Object obj = new Point(10, 20);

// Pattern Matching for instanceof
if (obj instanceof Point(int x, int y)) {
    System.out.println("x: " + x + ", y: " + y);
}
```

## 주의사항 / 함정

### 1. 불변성

```java
record Person(String name, List<String> hobbies) {}

Person person = new Person("홍길동", new ArrayList<>(List.of("독서", "운동")));

// ❌ List는 가변!
person.hobbies().add("음악");  // 변경됨!

// ✅ 불변 컬렉션 사용
record Person(String name, List<String> hobbies) {
    public Person(String name, List<String> hobbies) {
        this.name = name;
        this.hobbies = List.copyOf(hobbies);  // 불변 복사
    }
}
```

### 2. 상속 불가

```java
// ❌ Record는 다른 클래스 상속 불가
// record Employee(String name) extends Person {}  // 컴파일 에러

// ❌ Record 상속 불가
// class Manager extends Employee {}  // 컴파일 에러

// ✅ 인터페이스는 구현 가능
record Employee(String name) implements Identifiable {}
```

### 3. setter 없음

```java
record Person(String name, int age) {}

Person person = new Person("홍길동", 30);

// ❌ setter 없음
// person.setAge(31);  // 메서드 없음

// ✅ 새 객체 생성 (with 패턴)
record Person(String name, int age) {
    public Person withAge(int newAge) {
        return new Person(this.name, newAge);
    }
}

Person updated = person.withAge(31);
```

### 4. Jackson 직렬화 주의

```java
record User(String name, int age) {}

// Jackson 2.12+ 필요
ObjectMapper mapper = new ObjectMapper();

// 직렬화 OK
String json = mapper.writeValueAsString(new User("홍길동", 30));

// 역직렬화는 Jackson 설정 필요
// @JsonCreator 또는 ParameterNamesModule 필요
```

### 5. JPA Entity로 사용 불가

```java
// ❌ Record는 Entity로 사용 불가
// @Entity  // 컴파일 에러
// record User(Long id, String name) {}

// ✅ DTO로만 사용
record UserDto(Long id, String name) {
    static UserDto from(User entity) {
        return new UserDto(entity.getId(), entity.getName());
    }
}
```

### 6. null 허용

```java
record Person(String name, int age) {}

// ❌ null 체크 없으면 NPE 가능
Person person = new Person(null, 30);  // 가능
// person.name().toUpperCase();  // NullPointerException

// ✅ 컴팩트 생성자로 방지
record Person(String name, int age) {
    public Person {
        Objects.requireNonNull(name, "name cannot be null");
    }
}
```

## 관련 개념
- [[Java-불변객체]]
- [[Java-final]]
- [[Java-디자인패턴-빌더]]
- [[Java-Pattern-Matching]]

## 면접 질문
1. Record와 일반 클래스의 차이점은 무엇인가요?
2. Record를 사용하면 안 되는 경우는 언제인가요?

## 참고 자료
- JEP 395: Records
- Java 17 Documentation
- Effective Java (Record 관련 업데이트)