---
tags:
  - study
  - java
  - final
  - immutable
created: 2025-02-02
---

# Java final

## 한 줄 요약
> 값의 변경을 방지하여 불변성과 안정성을 보장하는 키워드

## 상세 설명

### final의 기본 개념

`final`은 "최종적인", "변경 불가능한"이라는 의미로, 변수, 메서드, 클래스에 적용할 수 있습니다. final이 적용된 대상은 한 번 정해지면 변경할 수 없습니다.

**적용 대상별 의미**
- **final 변수**: 값 변경 불가 (상수)
- **final 메서드**: 오버라이딩 불가
- **final 클래스**: 상속 불가

### final을 사용하는 이유

1. **불변성 보장**: 예측 가능한 코드 작성
2. **스레드 안전성**: 동시성 문제 감소
3. **성능 최적화**: JVM이 최적화 가능
4. **의도 명확화**: 변경되지 않아야 함을 명시

## 코드 예시

### final 변수 (상수)

```java
class Circle {
    // final 변수는 선언과 동시에 초기화
    final double PI = 3.14159;
    
    public void calculate() {
        // PI = 3.14;  // ❌ 컴파일 에러 - 값 변경 불가
        
        double area = PI * 10 * 10;
    }
}
```

### final 변수 초기화 방법

```java
class Student {
    // 1. 선언과 동시에 초기화
    final String SCHOOL_NAME = "한국대학교";
    
    // 2. 생성자에서 초기화
    final String studentId;
    final String name;
    
    public Student(String studentId, String name) {
        this.studentId = studentId;
        this.name = name;
    }
    
    // 3. 초기화 블록에서 초기화
    final int admissionYear;
    {
        admissionYear = 2025;
    }
}
```

### static final (상수)

```java
class Constants {
    // 클래스 레벨 상수 - 관례상 대문자와 언더스코어
    public static final int MAX_SIZE = 100;
    public static final String DEFAULT_ENCODING = "UTF-8";
    public static final double TAX_RATE = 0.1;
    
    // 여러 관련 상수를 그룹화
    public static final class HttpStatus {
        public static final int OK = 200;
        public static final int BAD_REQUEST = 400;
        public static final int NOT_FOUND = 404;
        public static final int SERVER_ERROR = 500;
    }
}

// 사용
int maxSize = Constants.MAX_SIZE;
int status = Constants.HttpStatus.OK;
```

### final 참조 변수의 주의점

```java
class Person {
    private String name;
    
    public Person(String name) {
        this.name = name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
}

// final 참조 변수
final Person person = new Person("홍길동");

// ❌ 참조 변경 불가
// person = new Person("김철수");  // 컴파일 에러

// ✅ 객체 내부 상태 변경 가능
person.setName("김철수");  // OK - 객체 자체는 변경 가능
```

### final 컬렉션

```java
// final List - 참조만 불변
final List<String> names = new ArrayList<>();

names.add("홍길동");  // ✅ OK - 내용 변경 가능
names.add("김철수");  // ✅ OK

// ❌ 참조 변경 불가
// names = new ArrayList<>();  // 컴파일 에러

// 진정한 불변 List 만들기
final List<String> immutableNames = Collections.unmodifiableList(
    Arrays.asList("홍길동", "김철수")
);

// immutableNames.add("이영희");  // ❌ UnsupportedOperationException
```

### final 메서드

```java
class Parent {
    // final 메서드 - 오버라이딩 불가
    public final void importantMethod() {
        System.out.println("이 로직은 변경되면 안됩니다");
    }
    
    public void normalMethod() {
        System.out.println("오버라이딩 가능");
    }
}

class Child extends Parent {
    // ❌ final 메서드 오버라이딩 불가
    // @Override
    // public void importantMethod() { }  // 컴파일 에러
    
    // ✅ 일반 메서드는 오버라이딩 가능
    @Override
    public void normalMethod() {
        System.out.println("오버라이딩됨");
    }
}
```

### final 클래스

```java
// final 클래스 - 상속 불가
final class ImmutablePoint {
    private final int x;
    private final int y;
    
    public ImmutablePoint(int x, int y) {
        this.x = x;
        this.y = y;
    }
    
    public int getX() { return x; }
    public int getY() { return y; }
}

// ❌ final 클래스 상속 불가
// class ExtendedPoint extends ImmutablePoint { }  // 컴파일 에러
```

### 실전 예시: 불변 객체

```java
public final class User {
    private final String id;
    private final String name;
    private final int age;
    
    public User(String id, String name, int age) {
        this.id = id;
        this.name = name;
        this.age = age;
    }
    
    // getter만 제공 (setter 없음)
    public String getId() { return id; }
    public String getName() { return name; }
    public int getAge() { return age; }
    
    // 변경이 필요하면 새 객체 생성
    public User withAge(int newAge) {
        return new User(this.id, this.name, newAge);
    }
}
```

### 불변 컬렉션 필드

```java
public final class Team {
    private final String name;
    private final List<String> members;
    
    public Team(String name, List<String> members) {
        this.name = name;
        // 방어적 복사 + 불변 리스트
        this.members = Collections.unmodifiableList(new ArrayList<>(members));
    }
    
    public String getName() {
        return name;
    }
    
    public List<String> getMembers() {
        // 불변 리스트 반환
        return members;
    }
}

// 사용
List<String> memberList = new ArrayList<>(Arrays.asList("김철수", "이영희"));
Team team = new Team("개발팀", memberList);

// ✅ 원본 리스트 변경해도 team에 영향 없음
memberList.add("박민수");
System.out.println(team.getMembers().size());  // 2

// ❌ team 내부 리스트 변경 불가
// team.getMembers().add("최영수");  // UnsupportedOperationException
```

### final 매개변수

```java
class Calculator {
    // final 매개변수 - 메서드 내에서 값 변경 불가
    public int calculate(final int a, final int b) {
        // a = 10;  // ❌ 컴파일 에러
        // b = 20;  // ❌ 컴파일 에러
        
        return a + b;
    }
    
    // 람다에서 사용할 변수는 effectively final이어야 함
    public void process(List<Integer> numbers) {
        int multiplier = 2;  // effectively final
        
        numbers.forEach(n -> System.out.println(n * multiplier));
        
        // multiplier = 3;  // ❌ 에러 (effectively final 위반)
    }
}
```

### enum과 final

```java
// enum 클래스는 암묵적으로 final
enum Status {
    ACTIVE,
    INACTIVE,
    PENDING;
    
    // enum 필드도 final로 선언 권장
    private final String description;
    
    Status() {
        this.description = name().toLowerCase();
    }
}
```

### static final 초기화

```java
class Config {
    // 컴파일 타임 상수
    public static final int MAX_USERS = 1000;
    
    // 런타임에 초기화되는 상수
    public static final String START_TIME;
    
    static {
        START_TIME = LocalDateTime.now().toString();
    }
}
```

### Builder 패턴에서 final 활용

```java
public final class Product {
    private final String id;
    private final String name;
    private final int price;
    private final String category;
    
    private Product(Builder builder) {
        this.id = builder.id;
        this.name = builder.name;
        this.price = builder.price;
        this.category = builder.category;
    }
    
    public static class Builder {
        private String id;
        private String name;
        private int price;
        private String category;
        
        public Builder id(String id) {
            this.id = id;
            return this;
        }
        
        public Builder name(String name) {
            this.name = name;
            return this;
        }
        
        public Builder price(int price) {
            this.price = price;
            return this;
        }
        
        public Builder category(String category) {
            this.category = category;
            return this;
        }
        
        public Product build() {
            return new Product(this);
        }
    }
}

// 사용
Product product = new Product.Builder()
    .id("P001")
    .name("노트북")
    .price(1000000)
    .category("전자제품")
    .build();
```

## 주의사항 / 함정

### 1. final과 불변성의 차이

```java
class Container {
    // final이지만 완전히 불변은 아님
    private final List<String> items = new ArrayList<>();
    
    public void addItem(String item) {
        items.add(item);  // ✅ OK - 리스트 내용 변경 가능
    }
    
    public List<String> getItems() {
        // ❌ 가변 리스트 반환 - 외부에서 수정 가능
        return items;
    }
}

// ✅ 진정한 불변 클래스
class ImmutableContainer {
    private final List<String> items;
    
    public ImmutableContainer(List<String> items) {
        this.items = Collections.unmodifiableList(new ArrayList<>(items));
    }
    
    public List<String> getItems() {
        return items;  // 불변 리스트 반환
    }
}
```

### 2. blank final 초기화 누락

```java
class Student {
    final String name;
    final int age;
    
    // ❌ final 변수 초기화 안함
    public Student() {
        // name = "Unknown";  // 이것도 빠뜨림
    }  // 컴파일 에러
}

// ✅ 모든 final 변수 초기화 필수
class Student {
    final String name;
    final int age;
    
    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

### 3. final과 성능 오해

```java
// final이 항상 성능 향상을 보장하지는 않음
// 현대 JVM은 충분히 똑똑함

// ❌ 과도한 final 사용
public void method(final int a, final int b, final int c, final int d) {
    final int sum = a + b;
    final int product = c * d;
    final int result = sum + product;
    // ...
}

// ✅ 적절한 final 사용
public void method(int a, int b, int c, int d) {
    int sum = a + b;
    int product = c * d;
    return sum + product;
}
```

### 4. 상속 차단의 영향

```java
// ❌ 유틸리티 클래스를 final로 만들 필요 없음
final class StringUtils {
    public static String reverse(String s) {
        return new StringBuilder(s).reverse().toString();
    }
}

// ✅ private 생성자로 충분
class StringUtils {
    private StringUtils() {
        throw new AssertionError();
    }
    
    public static String reverse(String s) {
        return new StringBuilder(s).reverse().toString();
    }
}
```

### 5. 배열의 final

```java
class ArrayExample {
    // final 배열 - 참조는 불변, 내용은 가변
    private final int[] numbers = {1, 2, 3, 4, 5};
    
    public void modify() {
        // ❌ 배열 참조 변경 불가
        // numbers = new int[]{6, 7, 8};  // 컴파일 에러
        
        // ✅ 배열 내용 변경 가능
        numbers[0] = 100;  // OK
    }
    
    // 불변 배열처럼 사용하려면
    public int[] getNumbers() {
        return numbers.clone();  // 복사본 반환
    }
}
```

### 6. null 허용

```java
class Example {
    // final이어도 null 할당 가능
    private final String value;
    
    public Example() {
        this.value = null;  // ✅ OK (권장 안함)
    }
}

// ✅ null 방지
class Example {
    private final String value;
    
    public Example(String value) {
        this.value = Objects.requireNonNull(value, "value cannot be null");
    }
}
```

## 관련 개념
- [[Java-static]]
- [[Java-불변객체]]
- [[Java-상속과다형성]]
- [[Java-디자인패턴-빌더]]

## 면접 질문
1. final 변수, final 메서드, final 클래스의 차이점은?
2. final 참조 변수가 가리키는 객체의 내부 상태를 변경할 수 있는 이유는?

## 참고 자료
- Effective Java 3/E - Item 17 (변경 가능성을 최소화하라)
- Effective Java 3/E - Item 50 (적시에 방어적 복사본을 만들라)
- Java Language Specification - Final Variables