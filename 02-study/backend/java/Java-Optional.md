---
tags:
  - study
  - java
  - optional
  - null-safety
created: 2025-02-02
---

# Java Optional

## 한 줄 요약
> null을 안전하게 다루기 위한 컨테이너 클래스

## 상세 설명

### Optional의 기본 개념

Optional은 Java 8에서 도입된 클래스로, 값이 있을 수도 있고 없을 수도 있는 상황을 명시적으로 표현합니다. NullPointerException을 방지하고 null 처리 로직을 더 명확하게 작성할 수 있게 합니다.

**주요 특징**
- 값의 존재 여부를 명시적으로 표현
- null 체크를 강제하지 않고도 안전한 코드 작성
- 함수형 프로그래밍 스타일 지원
- 불변 객체 (thread-safe)

### Optional을 사용하는 이유

**Optional 이전 방식의 문제점**
```java
// ❌ null 체크 누락 위험
User user = userRepository.findById(id);
String email = user.getEmail();  // NullPointerException 위험

// ❌ 중첩된 null 체크
if (user != null) {
    Address address = user.getAddress();
    if (address != null) {
        String city = address.getCity();
        // ...
    }
}
```

**Optional의 장점**
1. 명시적인 null 처리
2. 메서드 체이닝으로 간결한 코드
3. 컴파일 타임에 null 처리 강제
4. 가독성 향상

## 코드 예시

### Optional 생성

```java
// 1. Optional.of() - null이 아닌 값으로 생성
Optional<String> optional1 = Optional.of("Hello");
// Optional<String> optional2 = Optional.of(null);  // NullPointerException

// 2. Optional.ofNullable() - null 가능성이 있는 값
String value = getValue();  // null일 수 있음
Optional<String> optional3 = Optional.ofNullable(value);

// 3. Optional.empty() - 빈 Optional
Optional<String> optional4 = Optional.empty();
```

### 값 확인과 가져오기

```java
Optional<String> optional = Optional.of("Hello");

// 1. isPresent() - 값 존재 여부 확인
if (optional.isPresent()) {
    System.out.println("값이 있음");
}

// 2. isEmpty() - 값 없음 확인 (Java 11+)
if (optional.isEmpty()) {
    System.out.println("값이 없음");
}

// 3. get() - 값 가져오기 (권장 안함)
String value = optional.get();  // 값이 없으면 NoSuchElementException
```

### orElse, orElseGet, orElseThrow

```java
Optional<String> optional = Optional.empty();

// 1. orElse() - 기본값 반환
String result1 = optional.orElse("기본값");
System.out.println(result1);  // "기본값"

// 2. orElseGet() - Supplier로 기본값 생성 (지연 실행)
String result2 = optional.orElseGet(() -> {
    System.out.println("기본값 생성");
    return "생성된 기본값";
});

// 3. orElseThrow() - 예외 발생
String result3 = optional.orElseThrow(
    () -> new IllegalArgumentException("값이 없습니다")
);
```

### orElse vs orElseGet 차이

```java
class Example {
    public String getDefaultValue() {
        System.out.println("getDefaultValue() 호출됨");
        return "기본값";
    }
    
    public void compare() {
        Optional<String> optional = Optional.of("존재하는 값");
        
        // ❌ orElse - 값이 있어도 항상 실행
        String result1 = optional.orElse(getDefaultValue());
        // 출력: "getDefaultValue() 호출됨"
        
        // ✅ orElseGet - 값이 없을 때만 실행
        String result2 = optional.orElseGet(() -> getDefaultValue());
        // 출력 없음 (값이 있으므로 호출 안됨)
    }
}
```

### ifPresent와 ifPresentOrElse

```java
Optional<String> optional = Optional.of("Hello");

// 1. ifPresent() - 값이 있으면 실행
optional.ifPresent(value -> {
    System.out.println("값: " + value);
});

// 2. ifPresentOrElse() - 값 유무에 따라 다른 동작 (Java 9+)
optional.ifPresentOrElse(
    value -> System.out.println("값: " + value),
    () -> System.out.println("값이 없음")
);
```

### map과 flatMap

```java
// map() - 값을 변환
Optional<String> optional = Optional.of("hello");

Optional<String> upper = optional.map(String::toUpperCase);
System.out.println(upper.get());  // "HELLO"

Optional<Integer> length = optional.map(String::length);
System.out.println(length.get());  // 5

// 체이닝
Optional<String> result = Optional.of("hello")
    .map(String::toUpperCase)
    .map(s -> s + " WORLD");
System.out.println(result.get());  // "HELLO WORLD"
```

### flatMap 활용

```java
class User {
    private Optional<Address> address;
    
    public Optional<Address> getAddress() {
        return address;
    }
}

class Address {
    private String city;
    
    public Optional<String> getCity() {
        return Optional.ofNullable(city);
    }
}

// ❌ map 사용 시 - Optional<Optional<String>>
Optional<User> user = findUser();
Optional<Optional<String>> city1 = user.map(User::getAddress)
                                        .map(Address::getCity);  // 중첩 Optional

// ✅ flatMap 사용
Optional<String> city2 = user.flatMap(User::getAddress)
                              .flatMap(Address::getCity);
```

### filter 활용

```java
Optional<String> optional = Optional.of("Hello");

// filter() - 조건을 만족하는 경우만 값 유지
Optional<String> filtered = optional.filter(s -> s.length() > 3);
System.out.println(filtered.isPresent());  // true

Optional<String> filtered2 = optional.filter(s -> s.length() > 10);
System.out.println(filtered2.isPresent());  // false

// 실전 예시: 나이 검증
Optional<User> user = findUser();
Optional<User> adult = user.filter(u -> u.getAge() >= 18);
```

### or 메서드 (Java 9+)

```java
Optional<String> optional1 = Optional.empty();
Optional<String> optional2 = Optional.of("Backup");

// or() - 첫 번째 Optional이 비어있으면 두 번째 Optional 반환
Optional<String> result = optional1.or(() -> optional2);
System.out.println(result.get());  // "Backup"
```

### stream 메서드 (Java 9+)

```java
List<Optional<String>> list = Arrays.asList(
    Optional.of("A"),
    Optional.empty(),
    Optional.of("B"),
    Optional.empty(),
    Optional.of("C")
);

// Optional을 Stream으로 변환
List<String> values = list.stream()
    .flatMap(Optional::stream)  // 값이 있는 것만 Stream으로
    .collect(Collectors.toList());

System.out.println(values);  // [A, B, C]
```

### 실무 예시: Repository 패턴

```java
interface UserRepository {
    Optional<User> findById(Long id);
    Optional<User> findByEmail(String email);
}

class UserService {
    private UserRepository userRepository;
    
    public User getUser(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException("User not found: " + id));
    }
    
    public String getUserEmail(Long id) {
        return userRepository.findById(id)
            .map(User::getEmail)
            .orElse("no-email@example.com");
    }
    
    public boolean isAdult(Long id) {
        return userRepository.findById(id)
            .map(User::getAge)
            .filter(age -> age >= 18)
            .isPresent();
    }
}
```

### 실무 예시: 설정값 처리

```java
class Configuration {
    public Optional<String> getProperty(String key) {
        String value = System.getProperty(key);
        return Optional.ofNullable(value);
    }
    
    public int getTimeout() {
        return getProperty("timeout")
            .map(Integer::parseInt)
            .filter(t -> t > 0)
            .orElse(3000);  // 기본값 3초
    }
    
    public String getDbUrl() {
        return getProperty("db.url")
            .orElseThrow(() -> new IllegalStateException("DB URL이 설정되지 않았습니다"));
    }
}
```

### 실무 예시: 중첩 null 체크 제거

```java
// ❌ Before - 중첩된 null 체크
public String getCityName(User user) {
    if (user != null) {
        Address address = user.getAddress();
        if (address != null) {
            City city = address.getCity();
            if (city != null) {
                return city.getName();
            }
        }
    }
    return "Unknown";
}

// ✅ After - Optional 체이닝
public String getCityName(Optional<User> user) {
    return user.flatMap(User::getAddress)
               .flatMap(Address::getCity)
               .map(City::getName)
               .orElse("Unknown");
}
```

### 실무 예시: 캐시 조회

```java
class CacheService {
    private Map<String, String> cache = new HashMap<>();
    
    public Optional<String> getFromCache(String key) {
        return Optional.ofNullable(cache.get(key));
    }
    
    public String getValue(String key) {
        return getFromCache(key)
            .orElseGet(() -> {
                String value = fetchFromDatabase(key);
                cache.put(key, value);
                return value;
            });
    }
    
    private String fetchFromDatabase(String key) {
        // DB 조회 로직
        return "DB Value";
    }
}
```

## 주의사항 / 함정

### 1. 필드로 Optional 사용 금지

```java
// ❌ 나쁜 예 - 필드로 Optional 사용
class User {
    private Optional<String> email;  // 직렬화 문제, 메모리 낭비
    
    public Optional<String> getEmail() {
        return email;
    }
}

// ✅ 좋은 예 - 반환 타입으로만 사용
class User {
    private String email;  // null 가능
    
    public Optional<String> getEmail() {
        return Optional.ofNullable(email);
    }
}
```

### 2. Optional을 매개변수로 사용 금지

```java
// ❌ 나쁜 예
public void setUser(Optional<User> user) {
    user.ifPresent(u -> this.user = u);
}

// ✅ 좋은 예
public void setUser(User user) {
    this.user = user;
}

// 또는 메서드 오버로딩
public void setUser(User user) {
    this.user = user;
}

public void clearUser() {
    this.user = null;
}
```

### 3. Optional.get() 남용

```java
// ❌ 나쁜 예 - isPresent() + get()
Optional<String> optional = findValue();
if (optional.isPresent()) {
    String value = optional.get();
    System.out.println(value);
}

// ✅ 좋은 예 - ifPresent() 사용
optional.ifPresent(System.out::println);

// ✅ 좋은 예 - orElse 계열 사용
String value = optional.orElse("기본값");
```

### 4. 컬렉션을 Optional로 감싸지 말 것

```java
// ❌ 나쁜 예
public Optional<List<String>> getItems() {
    return Optional.ofNullable(items);
}

// ✅ 좋은 예 - 빈 컬렉션 반환
public List<String> getItems() {
    return items != null ? items : Collections.emptyList();
}
```

### 5. Optional 중첩 지양

```java
// ❌ 나쁜 예
Optional<Optional<String>> nested = Optional.of(Optional.of("value"));

// ✅ 좋은 예 - flatMap 사용
Optional<String> flattened = findUser()
    .flatMap(User::getEmail);
```

### 6. 성능을 고려한 사용

```java
// ❌ 성능이 중요한 곳에서 Optional 사용
public Optional<Integer> sum(int[] arr) {
    int sum = 0;
    for (int i : arr) {
        sum += i;
    }
    return Optional.of(sum);  // 불필요한 객체 생성
}

// ✅ null 허용
public Integer sum(int[] arr) {
    if (arr == null || arr.length == 0) {
        return null;
    }
    int sum = 0;
    for (int i : arr) {
        sum += i;
    }
    return sum;
}
```

### 7. Optional의 직렬화

```java
// Optional은 Serializable을 구현하지 않음
class User implements Serializable {
    // ❌ 직렬화 불가
    private Optional<String> email;
    
    // ✅ 대안
    private String email;
    
    public Optional<String> getEmail() {
        return Optional.ofNullable(email);
    }
}
```

## 관련 개념
- [[Java-람다-Stream]]
- [[Java-예외처리-Exception]]

## 면접 질문
1. Optional을 사용하는 이유와 장점은 무엇인가요?
2. orElse와 orElseGet의 차이점은?

## 참고 자료
- Effective Java 3/E - Item 55 (옵셔널 반환은 신중히 하라)
- Java Optional API Documentation
- Oracle Optional Best Practices