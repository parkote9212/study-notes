---
tags:
  - study
  - java
  - immutable
  - design-pattern
  - thread-safety
created: 2025-02-08
---

# Java 불변 객체 (Immutable Object)

## 한 줄 요약
> 생성 후 상태를 변경할 수 없는 객체로 Thread-Safe하고 예측 가능한 설계 패턴

## 상세 설명

### 불변 객체란?

불변 객체는 **생성 이후 내부 상태를 변경할 수 없는 객체**입니다. 한번 만들어진 후에는 어떤 방법으로도 내부 데이터를 수정할 수 없습니다.

**대표적인 불변 객체**
- `String`
- `Integer`, `Long` 등 Wrapper 클래스
- `LocalDate`, `LocalDateTime` 등 날짜/시간 클래스
- `BigDecimal`, `BigInteger`
- `Record` (Java 16+)

**왜 필요한가?**
1. **Thread-Safety**: 멀티스레드 환경에서 안전
2. **예측 가능성**: 상태 변경 걱정 없음
3. **캐싱**: 안전하게 재사용 가능
4. **방어적 복사 불필요**: 참조를 자유롭게 공유
5. **HashMap/HashSet 키로 안전**: 해시값 변경 없음

## 코드 예시

### String의 불변성

```java
public class StringImmutability {
    public static void main(String[] args) {
        String str = "Hello";
        System.out.println(str);  // Hello
        System.out.println(System.identityHashCode(str));  // 주소 확인
        
        // toUpperCase()는 새로운 String 객체 반환
        String upper = str.toUpperCase();
        System.out.println(str);    // Hello (원본 불변)
        System.out.println(upper);  // HELLO (새 객체)
        System.out.println(System.identityHashCode(upper));  // 다른 주소
        
        // concat()도 새 객체 반환
        String concat = str.concat(" World");
        System.out.println(str);     // Hello (원본 불변)
        System.out.println(concat);  // Hello World (새 객체)
    }
}
```

### 가변 객체 vs 불변 객체

```java
// ❌ 가변 객체 (Mutable)
class MutablePerson {
    private String name;
    private int age;
    
    public MutablePerson(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // Setter - 상태 변경 가능
    public void setName(String name) {
        this.name = name;
    }
    
    public void setAge(int age) {
        this.age = age;
    }
    
    public String getName() { return name; }
    public int getAge() { return age; }
}

// ✅ 불변 객체 (Immutable)
final class ImmutablePerson {
    private final String name;
    private final int age;
    
    public ImmutablePerson(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // Getter만 제공
    public String getName() { return name; }
    public int getAge() { return age; }
    
    // 변경이 필요하면 새 객체 반환
    public ImmutablePerson withName(String newName) {
        return new ImmutablePerson(newName, this.age);
    }
    
    public ImmutablePerson withAge(int newAge) {
        return new ImmutablePerson(this.name, newAge);
    }
}
```

### 불변 객체 만들기 - 5가지 규칙

```java
// ✅ 완벽한 불변 객체
public final class ImmutableAddress {
    // 1. final class - 상속 방지
    
    // 2. 모든 필드 private final
    private final String street;
    private final String city;
    private final int zipCode;
    
    // 3. 생성자에서만 초기화
    public ImmutableAddress(String street, String city, int zipCode) {
        this.street = street;
        this.city = city;
        this.zipCode = zipCode;
    }
    
    // 4. Getter만 제공 (Setter 없음)
    public String getStreet() { return street; }
    public String getCity() { return city; }
    public int getZipCode() { return zipCode; }
    
    // 5. 가변 필드가 있다면 방어적 복사 (아래 예시 참고)
}
```

### 내부에 가변 객체가 있는 경우

```java
import java.util.*;

// ❌ 잘못된 불변 객체 - 내부 가변 객체 노출
final class BadImmutableClass {
    private final List<String> items;
    
    public BadImmutableClass(List<String> items) {
        this.items = items;  // 외부 리스트 참조 그대로 저장
    }
    
    public List<String> getItems() {
        return items;  // 내부 리스트 직접 노출
    }
}

// 문제 발생
List<String> list = new ArrayList<>(Arrays.asList("A", "B"));
BadImmutableClass bad = new BadImmutableClass(list);

// ❌ 외부에서 내부 상태 변경 가능
list.add("C");  // 생성자 파라미터 변경
bad.getItems().add("D");  // getter로 얻은 리스트 변경

System.out.println(bad.getItems());  // [A, B, C, D] - 불변성 깨짐!
```

```java
// ✅ 올바른 불변 객체 - 방어적 복사
final class GoodImmutableClass {
    private final List<String> items;
    
    public GoodImmutableClass(List<String> items) {
        // 방어적 복사 - 새 리스트 생성
        this.items = new ArrayList<>(items);
    }
    
    public List<String> getItems() {
        // 방어적 복사 - 새 리스트 반환
        return new ArrayList<>(items);
        
        // 또는 불변 리스트 반환
        // return Collections.unmodifiableList(items);
    }
}

// 안전
List<String> list = new ArrayList<>(Arrays.asList("A", "B"));
GoodImmutableClass good = new GoodImmutableClass(list);

// ✅ 외부 변경이 내부에 영향 없음
list.add("C");
System.out.println(good.getItems());  // [A, B]

// ✅ getter로 얻은 리스트 변경해도 원본 안전
List<String> retrieved = good.getItems();
retrieved.add("D");
System.out.println(good.getItems());  // [A, B]
```

### 불변 컬렉션 활용

```java
import java.util.*;

public class ImmutableCollections {
    public static void main(String[] args) {
        // ❌ 가변 컬렉션
        List<String> mutableList = new ArrayList<>();
        mutableList.add("A");
        mutableList.add("B");
        
        // ✅ 불변 컬렉션 (Java 9+)
        List<String> immutableList = List.of("A", "B", "C");
        // immutableList.add("D");  // UnsupportedOperationException
        
        Set<String> immutableSet = Set.of("A", "B", "C");
        Map<String, Integer> immutableMap = Map.of("A", 1, "B", 2);
        
        // ✅ Collections.unmodifiable (Java 8 이하)
        List<String> original = new ArrayList<>(Arrays.asList("A", "B"));
        List<String> unmodifiable = Collections.unmodifiableList(original);
        // unmodifiable.add("C");  // UnsupportedOperationException
        
        // ⚠️ 주의: 원본 변경은 가능
        original.add("C");
        System.out.println(unmodifiable);  // [A, B, C]
    }
}
```

### Record로 불변 객체 만들기 (Java 16+)

```java
// ✅ Record - 자동으로 불변 객체
public record Person(String name, int age) {
    // 자동 생성:
    // - private final 필드
    // - 생성자
    // - getter (name(), age())
    // - equals(), hashCode(), toString()
    
    // 커스텀 생성자 (유효성 검증)
    public Person {
        if (age < 0) {
            throw new IllegalArgumentException("나이는 0 이상이어야 합니다");
        }
    }
    
    // 추가 메서드
    public Person withAge(int newAge) {
        return new Person(this.name, newAge);
    }
}

// 사용
Person person = new Person("Alice", 25);
System.out.println(person.name());  // Alice
System.out.println(person.age());   // 25

// 변경이 필요하면 새 객체 생성
Person older = person.withAge(30);
System.out.println(person.age());  // 25 (원본 불변)
System.out.println(older.age());   // 30 (새 객체)
```

## 실무 예시

### 1. Builder 패턴으로 불변 객체 생성

```java
public final class User {
    private final String username;
    private final String email;
    private final int age;
    private final List<String> roles;
    
    private User(Builder builder) {
        this.username = builder.username;
        this.email = builder.email;
        this.age = builder.age;
        this.roles = Collections.unmodifiableList(
            new ArrayList<>(builder.roles)
        );
    }
    
    // Getters
    public String getUsername() { return username; }
    public String getEmail() { return email; }
    public int getAge() { return age; }
    public List<String> getRoles() { return roles; }
    
    // Builder
    public static class Builder {
        private String username;
        private String email;
        private int age;
        private List<String> roles = new ArrayList<>();
        
        public Builder username(String username) {
            this.username = username;
            return this;
        }
        
        public Builder email(String email) {
            this.email = email;
            return this;
        }
        
        public Builder age(int age) {
            this.age = age;
            return this;
        }
        
        public Builder addRole(String role) {
            this.roles.add(role);
            return this;
        }
        
        public User build() {
            return new User(this);
        }
    }
}

// 사용
User user = new User.Builder()
    .username("alice")
    .email("alice@example.com")
    .age(25)
    .addRole("USER")
    .addRole("ADMIN")
    .build();
```

### 2. 값 객체 (Value Object)

```java
public final class Money {
    private final BigDecimal amount;
    private final String currency;
    
    public Money(BigDecimal amount, String currency) {
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("금액은 0 이상이어야 합니다");
        }
        this.amount = amount;
        this.currency = currency;
    }
    
    // 연산 메서드 - 새 객체 반환
    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("통화가 다릅니다");
        }
        return new Money(
            this.amount.add(other.amount),
            this.currency
        );
    }
    
    public Money multiply(int factor) {
        return new Money(
            this.amount.multiply(BigDecimal.valueOf(factor)),
            this.currency
        );
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Money)) return false;
        Money money = (Money) o;
        return amount.equals(money.amount) && 
               currency.equals(money.currency);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(amount, currency);
    }
}

// 사용
Money price = new Money(new BigDecimal("100"), "USD");
Money doubled = price.multiply(2);
System.out.println(price);    // 100 USD (원본 불변)
System.out.println(doubled);  // 200 USD (새 객체)
```

### 3. Thread-Safe 캐시

```java
public final class UserCache {
    // 불변 객체는 Thread-Safe하므로 동기화 불필요
    private final Map<String, User> cache;
    
    public UserCache(Map<String, User> users) {
        // 불변 맵 생성
        this.cache = Map.copyOf(users);
    }
    
    public User getUser(String username) {
        return cache.get(username);
    }
    
    // 변경이 필요하면 새 캐시 생성
    public UserCache withUser(User user) {
        Map<String, User> newCache = new HashMap<>(cache);
        newCache.put(user.getUsername(), user);
        return new UserCache(newCache);
    }
}
```

### 4. API Response DTO

```java
// ✅ 불변 Response - 안전한 데이터 전달
public record ApiResponse<T>(
    int status,
    String message,
    T data,
    LocalDateTime timestamp
) {
    public ApiResponse {
        if (status < 100 || status >= 600) {
            throw new IllegalArgumentException("Invalid HTTP status");
        }
    }
    
    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(
            200,
            "Success",
            data,
            LocalDateTime.now()
        );
    }
    
    public static <T> ApiResponse<T> error(String message) {
        return new ApiResponse<>(
            500,
            message,
            null,
            LocalDateTime.now()
        );
    }
}

// 사용
ApiResponse<User> response = ApiResponse.success(user);
// response는 불변이므로 안전하게 공유 가능
```

### 5. 날짜/시간 불변성

```java
import java.time.*;

public class DateTimeImmutability {
    public static void main(String[] args) {
        // ❌ 가변 (Deprecated)
        Date oldDate = new Date();
        oldDate.setTime(1234567890L);  // 상태 변경 가능
        
        // ✅ 불변
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime future = now.plusDays(7);
        
        System.out.println(now);     // 원본 불변
        System.out.println(future);  // 새 객체
        
        // 모든 날짜/시간 연산은 새 객체 반환
        LocalDate date = LocalDate.of(2025, 2, 8);
        LocalDate nextMonth = date.plusMonths(1);
        LocalDate nextYear = date.plusYears(1);
    }
}
```

### 6. 함수형 프로그래밍과 불변성

```java
import java.util.*;
import java.util.stream.*;

public class FunctionalImmutability {
    // ❌ 가변 방식
    public static List<Integer> doubleListMutable(List<Integer> numbers) {
        for (int i = 0; i < numbers.size(); i++) {
            numbers.set(i, numbers.get(i) * 2);  // 원본 수정
        }
        return numbers;
    }
    
    // ✅ 불변 방식
    public static List<Integer> doubleListImmutable(List<Integer> numbers) {
        return numbers.stream()
            .map(n -> n * 2)
            .collect(Collectors.toUnmodifiableList());  // 새 리스트
    }
    
    public static void main(String[] args) {
        List<Integer> original = new ArrayList<>(List.of(1, 2, 3));
        
        List<Integer> doubled = doubleListImmutable(original);
        System.out.println(original);  // [1, 2, 3] - 원본 보존
        System.out.println(doubled);   // [2, 4, 6] - 새 리스트
    }
}
```

## 주의사항 / 함정

### 1. 얕은 복사 vs 깊은 복사

```java
// ❌ 얕은 복사 - 내부 객체는 공유
final class ShallowCopy {
    private final List<MutablePerson> people;
    
    public ShallowCopy(List<MutablePerson> people) {
        this.people = new ArrayList<>(people);  // 리스트만 복사
    }
    
    public List<MutablePerson> getPeople() {
        return new ArrayList<>(people);
    }
}

// 문제: MutablePerson 객체는 여전히 가변
ShallowCopy sc = new ShallowCopy(Arrays.asList(
    new MutablePerson("Alice", 25)
));
sc.getPeople().get(0).setAge(30);  // 내부 객체 변경 가능!

// ✅ 깊은 복사 - 내부 객체도 복사
final class DeepCopy {
    private final List<ImmutablePerson> people;
    
    public DeepCopy(List<ImmutablePerson> people) {
        // 불변 객체 사용
        this.people = List.copyOf(people);
    }
    
    public List<ImmutablePerson> getPeople() {
        return people;  // 불변이므로 안전
    }
}
```

### 2. 상속 방지 필수

```java
// ❌ final 없음 - 상속 가능
class NotFinalClass {
    private final String value;
    
    public NotFinalClass(String value) {
        this.value = value;
    }
    
    public String getValue() {
        return value;
    }
}

// 가변 서브클래스 생성 가능
class MutableSubclass extends NotFinalClass {
    private String mutableValue;
    
    public MutableSubclass(String value) {
        super(value);
        this.mutableValue = value;
    }
    
    // 불변성 깨짐
    public void setMutableValue(String value) {
        this.mutableValue = value;
    }
    
    @Override
    public String getValue() {
        return mutableValue;  // 변경 가능한 값 반환
    }
}

// ✅ final class - 상속 방지
final class FinalClass {
    private final String value;
    
    public FinalClass(String value) {
        this.value = value;
    }
    
    public String getValue() {
        return value;
    }
}
```

### 3. 불변 객체의 성능

```java
// ❌ 성능 문제 - 문자열 연결
public String badStringConcat(String[] words) {
    String result = "";
    for (String word : words) {
        result += word;  // 매번 새 String 객체 생성 → O(n²)
    }
    return result;
}

// ✅ StringBuilder 사용
public String goodStringConcat(String[] words) {
    StringBuilder sb = new StringBuilder();
    for (String word : words) {
        sb.append(word);  // 가변 객체로 효율적 → O(n)
    }
    return sb.toString();  // 마지막에 불변 String 반환
}
```

### 4. 불필요한 객체 생성

```java
// ❌ 매번 새 객체 생성
public class WastefulCreation {
    public Money calculateTotal(List<Money> items) {
        Money total = new Money(BigDecimal.ZERO, "USD");
        for (Money item : items) {
            total = total.add(item);  // 매번 새 객체
        }
        return total;
    }
}

// ✅ 가변 객체로 작업 후 불변 객체 반환
public class EfficientCreation {
    public Money calculateTotal(List<Money> items) {
        BigDecimal sum = BigDecimal.ZERO;
        for (Money item : items) {
            sum = sum.add(item.getAmount());
        }
        return new Money(sum, "USD");  // 마지막에 한번만 생성
    }
}
```

### 5. HashMap/HashSet 키로 사용 시 주의

```java
// ✅ 불변 객체 - HashMap 키로 안전
final class SafeKey {
    private final String id;
    
    public SafeKey(String id) {
        this.id = id;
    }
    
    @Override
    public boolean equals(Object o) {
        if (!(o instanceof SafeKey)) return false;
        return id.equals(((SafeKey) o).id);
    }
    
    @Override
    public int hashCode() {
        return id.hashCode();
    }
}

Map<SafeKey, String> map = new HashMap<>();
SafeKey key = new SafeKey("123");
map.put(key, "value");
System.out.println(map.get(key));  // "value" - 안전

// ❌ 가변 객체 - HashMap 키로 위험
Map<MutablePerson, String> badMap = new HashMap<>();
MutablePerson person = new MutablePerson("Alice", 25);
badMap.put(person, "value");

person.setAge(30);  // hashCode 변경!
System.out.println(badMap.get(person));  // null - 찾을 수 없음
```

## 관련 개념
- [[Java-Record]]
- [[Java-문자열처리심화]]
- [[Java-제네릭스-Generics]]

## 면접 질문
1. 불변 객체란 무엇이며 왜 사용하나요?
2. 불변 객체를 만드는 방법은?
3. String이 불변인 이유는?
4. 불변 객체의 장단점은?
5. 방어적 복사가 필요한 이유는?
6. Record와 일반 클래스의 차이는?

## 참고 자료
- Effective Java 3/E - Item 17 (변경 가능성을 최소화하라)
- Java Concurrency in Practice
- Domain-Driven Design (Value Object 패턴)
