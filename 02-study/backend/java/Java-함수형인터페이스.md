---
tags:
  - study
  - java
  - functional-interface
  - lambda
created: 2025-02-08
---

# Java 함수형 인터페이스

## 한 줄 요약
> 단 하나의 추상 메서드를 가진 인터페이스로 람다 표현식의 타입 역할

## 상세 설명

### 함수형 인터페이스란?

함수형 인터페이스(Functional Interface)는 **정확히 하나의 추상 메서드**만을 가진 인터페이스입니다. Java 8부터 도입된 람다 표현식은 함수형 인터페이스의 인스턴스를 생성합니다.

**특징**
- 추상 메서드가 정확히 1개
- `@FunctionalInterface` 어노테이션으로 명시 (선택)
- default 메서드, static 메서드는 여러 개 가능
- Object 클래스의 public 메서드는 카운트 안함

**왜 필요한가?**
1. 람다 표현식의 타입 지정
2. 코드 간결성
3. 함수형 프로그래밍 지원
4. Stream API와 완벽한 통합

## 코드 예시

### @FunctionalInterface 어노테이션

```java
// ✅ 올바른 함수형 인터페이스
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);  // 추상 메서드 1개
    
    // default 메서드는 OK
    default void printResult(int result) {
        System.out.println("결과: " + result);
    }
    
    // static 메서드도 OK
    static Calculator add() {
        return (a, b) -> a + b;
    }
}

// ❌ 컴파일 에러 - 추상 메서드 2개
@FunctionalInterface
interface Invalid {
    void method1();
    void method2();  // 에러!
}
```

### 람다 표현식과 함수형 인터페이스

```java
@FunctionalInterface
interface Greeting {
    void sayHello(String name);
}

// 익명 클래스 방식 (이전)
Greeting greeting1 = new Greeting() {
    @Override
    public void sayHello(String name) {
        System.out.println("Hello, " + name);
    }
};

// ✅ 람다 표현식 (간결)
Greeting greeting2 = name -> System.out.println("Hello, " + name);

// 사용
greeting2.sayHello("World");  // Hello, World
```

## 표준 함수형 인터페이스 (java.util.function)

### 1. Predicate<T> - 조건 검사

```java
@FunctionalInterface
public interface Predicate<T> {
    boolean test(T t);
}

// 사용 예시
Predicate<Integer> isPositive = n -> n > 0;
System.out.println(isPositive.test(5));   // true
System.out.println(isPositive.test(-3));  // false

// 실전: 필터링
List<Integer> numbers = Arrays.asList(1, -2, 3, -4, 5);
List<Integer> positive = numbers.stream()
    .filter(n -> n > 0)  // Predicate
    .collect(Collectors.toList());
System.out.println(positive);  // [1, 3, 5]

// 체이닝 메서드
Predicate<Integer> isEven = n -> n % 2 == 0;
Predicate<Integer> isPositiveAndEven = isPositive.and(isEven);
System.out.println(isPositiveAndEven.test(4));   // true
System.out.println(isPositiveAndEven.test(-4));  // false

Predicate<Integer> isPositiveOrEven = isPositive.or(isEven);
System.out.println(isPositiveOrEven.test(-4));  // true

Predicate<Integer> isNotPositive = isPositive.negate();
System.out.println(isNotPositive.test(-3));  // true
```

### 2. Function<T, R> - 변환

```java
@FunctionalInterface
public interface Function<T, R> {
    R apply(T t);
}

// 사용 예시
Function<String, Integer> strLength = s -> s.length();
System.out.println(strLength.apply("Hello"));  // 5

Function<Integer, Integer> square = n -> n * n;
System.out.println(square.apply(5));  // 25

// 실전: 변환
List<String> words = Arrays.asList("apple", "banana", "cherry");
List<Integer> lengths = words.stream()
    .map(String::length)  // Function
    .collect(Collectors.toList());
System.out.println(lengths);  // [5, 6, 6]

// 체이닝: compose, andThen
Function<Integer, Integer> multiplyBy2 = n -> n * 2;
Function<Integer, Integer> add10 = n -> n + 10;

// andThen: 먼저 실행 후 다음 실행
Function<Integer, Integer> combined1 = multiplyBy2.andThen(add10);
System.out.println(combined1.apply(5));  // (5 * 2) + 10 = 20

// compose: 나중 실행 후 먼저 실행
Function<Integer, Integer> combined2 = multiplyBy2.compose(add10);
System.out.println(combined2.apply(5));  // (5 + 10) * 2 = 30
```

### 3. Consumer<T> - 소비 (void)

```java
@FunctionalInterface
public interface Consumer<T> {
    void accept(T t);
}

// 사용 예시
Consumer<String> printer = s -> System.out.println(s);
printer.accept("Hello");  // Hello

// 실전: forEach
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
names.forEach(name -> System.out.println("Name: " + name));

// 체이닝
Consumer<String> upper = s -> System.out.println(s.toUpperCase());
Consumer<String> lower = s -> System.out.println(s.toLowerCase());

Consumer<String> both = upper.andThen(lower);
both.accept("Hello");
// HELLO
// hello
```

### 4. Supplier<T> - 공급

```java
@FunctionalInterface
public interface Supplier<T> {
    T get();
}

// 사용 예시
Supplier<Double> randomSupplier = () -> Math.random();
System.out.println(randomSupplier.get());  // 0.xxx

Supplier<LocalDateTime> nowSupplier = LocalDateTime::now;
System.out.println(nowSupplier.get());  // 현재 시간

// 실전: 지연 실행
class Logger {
    public void log(Supplier<String> messageSupplier) {
        if (isDebugEnabled()) {
            String message = messageSupplier.get();  // 필요할 때만 실행
            System.out.println(message);
        }
    }
    
    private boolean isDebugEnabled() {
        return true;
    }
}

Logger logger = new Logger();
logger.log(() -> "Heavy computation: " + heavyComputation());
```

### 5. BiFunction<T, U, R> - 두 개의 매개변수

```java
@FunctionalInterface
public interface BiFunction<T, U, R> {
    R apply(T t, U u);
}

// 사용 예시
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
System.out.println(add.apply(3, 5));  // 8

BiFunction<String, Integer, String> repeat = (s, n) -> s.repeat(n);
System.out.println(repeat.apply("Ha", 3));  // HaHaHa

// 실전: Map.merge()
Map<String, Integer> scores = new HashMap<>();
scores.put("Alice", 85);
scores.put("Bob", 90);

scores.merge("Alice", 10, (oldVal, newVal) -> oldVal + newVal);
System.out.println(scores.get("Alice"));  // 95
```

### 6. BiPredicate<T, U> - 두 개 매개변수 조건 검사

```java
BiPredicate<String, Integer> isLongerThan = (s, len) -> s.length() > len;
System.out.println(isLongerThan.test("Hello", 3));  // true
System.out.println(isLongerThan.test("Hi", 5));     // false
```

### 7. BiConsumer<T, U> - 두 개 매개변수 소비

```java
BiConsumer<String, Integer> printWithCount = (s, n) -> {
    for (int i = 0; i < n; i++) {
        System.out.println(s);
    }
};

printWithCount.accept("Hello", 3);
// Hello
// Hello
// Hello

// 실전: Map.forEach()
Map<String, Integer> map = Map.of("A", 1, "B", 2);
map.forEach((key, value) -> System.out.println(key + " = " + value));
```

### 8. UnaryOperator<T> - 단항 연산

```java
@FunctionalInterface
public interface UnaryOperator<T> extends Function<T, T> {
}

// Function<T, T>의 특수화
UnaryOperator<Integer> square = n -> n * n;
System.out.println(square.apply(5));  // 25

// 실전: List.replaceAll()
List<String> words = new ArrayList<>(Arrays.asList("apple", "banana"));
words.replaceAll(s -> s.toUpperCase());
System.out.println(words);  // [APPLE, BANANA]
```

### 9. BinaryOperator<T> - 이항 연산

```java
@FunctionalInterface
public interface BinaryOperator<T> extends BiFunction<T, T, T> {
}

// BiFunction<T, T, T>의 특수화
BinaryOperator<Integer> add = (a, b) -> a + b;
System.out.println(add.apply(3, 5));  // 8

BinaryOperator<String> concat = (s1, s2) -> s1 + s2;
System.out.println(concat.apply("Hello", "World"));  // HelloWorld

// 실전: reduce
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
int sum = numbers.stream()
    .reduce(0, (a, b) -> a + b);  // BinaryOperator
System.out.println(sum);  // 15
```

## 기본형 특화 함수형 인터페이스

박싱/언박싱 비용을 줄이기 위한 기본형 특화 버전들이 있습니다.

### IntPredicate, LongPredicate, DoublePredicate

```java
// ❌ 박싱 발생
Predicate<Integer> pred1 = n -> n > 0;

// ✅ 박싱 없음
IntPredicate pred2 = n -> n > 0;

// 성능 비교
IntStream.range(0, 1_000_000)
    .filter(n -> n % 2 == 0)  // IntPredicate
    .sum();
```

### IntFunction, IntToDoubleFunction 등

```java
IntFunction<String> intToString = n -> "Number: " + n;
System.out.println(intToString.apply(5));  // Number: 5

IntToDoubleFunction sqrt = n -> Math.sqrt(n);
System.out.println(sqrt.applyAsDouble(16));  // 4.0

ToIntFunction<String> strLength = s -> s.length();
System.out.println(strLength.applyAsInt("Hello"));  // 5
```

### IntConsumer, LongConsumer, DoubleConsumer

```java
IntConsumer printInt = n -> System.out.println("Value: " + n);
printInt.accept(42);  // Value: 42
```

### IntSupplier, LongSupplier, DoubleSupplier

```java
IntSupplier randomInt = () -> (int)(Math.random() * 100);
System.out.println(randomInt.getAsInt());
```

### IntUnaryOperator, IntBinaryOperator

```java
IntUnaryOperator doubleOp = n -> n * 2;
System.out.println(doubleOp.applyAsInt(5));  // 10

IntBinaryOperator add = (a, b) -> a + b;
System.out.println(add.applyAsInt(3, 5));  // 8
```

## 실무 예시

### 1. 전략 패턴 (Strategy Pattern)

```java
@FunctionalInterface
interface DiscountStrategy {
    double applyDiscount(double price);
}

class PriceCalculator {
    public double calculate(double price, DiscountStrategy strategy) {
        return strategy.applyDiscount(price);
    }
}

// 사용
PriceCalculator calculator = new PriceCalculator();

// 10% 할인
double price1 = calculator.calculate(10000, price -> price * 0.9);
System.out.println(price1);  // 9000.0

// 고정 금액 할인
double price2 = calculator.calculate(10000, price -> price - 1000);
System.out.println(price2);  // 9000.0

// VIP 할인 (20% + 1000원)
DiscountStrategy vipDiscount = price -> (price * 0.8) - 1000;
double price3 = calculator.calculate(10000, vipDiscount);
System.out.println(price3);  // 7000.0
```

### 2. 유효성 검증

```java
class Validator<T> {
    private final List<Predicate<T>> rules = new ArrayList<>();
    
    public Validator<T> addRule(Predicate<T> rule) {
        rules.add(rule);
        return this;
    }
    
    public boolean validate(T value) {
        return rules.stream().allMatch(rule -> rule.test(value));
    }
}

// 사용: 비밀번호 검증
Validator<String> passwordValidator = new Validator<String>()
    .addRule(s -> s.length() >= 8)
    .addRule(s -> s.matches(".*[A-Z].*"))  // 대문자 포함
    .addRule(s -> s.matches(".*[0-9].*"))  // 숫자 포함
    .addRule(s -> s.matches(".*[!@#$].*"));  // 특수문자 포함

System.out.println(passwordValidator.validate("Pass123!"));   // true
System.out.println(passwordValidator.validate("password"));   // false
```

### 3. 지연 실행 (Lazy Evaluation)

```java
class LazyValue<T> {
    private T value;
    private Supplier<T> supplier;
    
    public LazyValue(Supplier<T> supplier) {
        this.supplier = supplier;
    }
    
    public T get() {
        if (value == null) {
            value = supplier.get();  // 최초 호출 시에만 실행
        }
        return value;
    }
}

// 사용
LazyValue<String> lazyValue = new LazyValue<>(() -> {
    System.out.println("무거운 연산 실행...");
    return "결과값";
});

System.out.println("값 생성 전");
System.out.println(lazyValue.get());  // 무거운 연산 실행... / 결과값
System.out.println(lazyValue.get());  // 결과값 (캐시됨)
```

### 4. 콜백 패턴

```java
class AsyncTask {
    public void execute(Runnable task, Consumer<String> onSuccess, Consumer<Exception> onError) {
        try {
            task.run();
            onSuccess.accept("작업 완료");
        } catch (Exception e) {
            onError.accept(e);
        }
    }
}

// 사용
AsyncTask asyncTask = new AsyncTask();
asyncTask.execute(
    () -> System.out.println("비동기 작업 실행"),
    result -> System.out.println("성공: " + result),
    error -> System.err.println("실패: " + error.getMessage())
);
```

### 5. 빌더 패턴 with Consumer

```java
class Email {
    private String to;
    private String subject;
    private String body;
    
    public static class Builder {
        private String to;
        private String subject;
        private String body;
        
        public Builder to(String to) {
            this.to = to;
            return this;
        }
        
        public Builder subject(String subject) {
            this.subject = subject;
            return this;
        }
        
        public Builder body(String body) {
            this.body = body;
            return this;
        }
        
        // Consumer로 설정
        public Builder with(Consumer<Builder> consumer) {
            consumer.accept(this);
            return this;
        }
        
        public Email build() {
            Email email = new Email();
            email.to = this.to;
            email.subject = this.subject;
            email.body = this.body;
            return email;
        }
    }
}

// 사용
Email email = new Email.Builder()
    .with(b -> {
        b.to("user@example.com");
        b.subject("안녕하세요");
        b.body("메일 본문입니다.");
    })
    .build();
```

### 6. 필터 체이닝

```java
class ProductFilter {
    private List<Predicate<Product>> filters = new ArrayList<>();
    
    public ProductFilter priceRange(double min, double max) {
        filters.add(p -> p.getPrice() >= min && p.getPrice() <= max);
        return this;
    }
    
    public ProductFilter category(String category) {
        filters.add(p -> p.getCategory().equals(category));
        return this;
    }
    
    public ProductFilter inStock() {
        filters.add(Product::isInStock);
        return this;
    }
    
    public List<Product> apply(List<Product> products) {
        return products.stream()
            .filter(filters.stream().reduce(p -> true, Predicate::and))
            .collect(Collectors.toList());
    }
}

// 사용
List<Product> filtered = new ProductFilter()
    .priceRange(10000, 50000)
    .category("전자제품")
    .inStock()
    .apply(allProducts);
```

## 주의사항 / 함정

### 1. 예외 처리

```java
// ❌ 함수형 인터페이스는 체크 예외를 던질 수 없음
List<String> files = Arrays.asList("file1.txt", "file2.txt");
// files.forEach(f -> Files.readString(Path.of(f)));  // 컴파일 에러

// ✅ 해결 1: try-catch로 감싸기
files.forEach(f -> {
    try {
        String content = Files.readString(Path.of(f));
        System.out.println(content);
    } catch (IOException e) {
        throw new UncheckedIOException(e);
    }
});

// ✅ 해결 2: 래퍼 함수 만들기
@FunctionalInterface
interface ThrowingConsumer<T, E extends Exception> {
    void accept(T t) throws E;
    
    static <T> Consumer<T> unchecked(ThrowingConsumer<T, Exception> consumer) {
        return t -> {
            try {
                consumer.accept(t);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        };
    }
}

files.forEach(ThrowingConsumer.unchecked(f -> 
    System.out.println(Files.readString(Path.of(f)))
));
```

### 2. 람다에서 외부 변수 수정 불가

```java
// ❌ effectively final 위반
int count = 0;
List<String> list = Arrays.asList("a", "b", "c");
list.forEach(s -> count++);  // 컴파일 에러

// ✅ 해결 1: 배열 사용
int[] count = {0};
list.forEach(s -> count[0]++);

// ✅ 해결 2: AtomicInteger 사용
AtomicInteger count = new AtomicInteger(0);
list.forEach(s -> count.incrementAndGet());

// ✅ 해결 3: Stream 연산 사용 (권장)
long count = list.stream().count();
```

### 3. 메서드 참조 주의사항

```java
// ❌ null 위험
List<String> list = Arrays.asList("a", null, "c");
// list.forEach(System.out::println);  // NullPointerException

// ✅ null 체크
list.stream()
    .filter(Objects::nonNull)
    .forEach(System.out::println);
```

### 4. 성능 - 기본형 특화 사용

```java
// ❌ 박싱/언박싱 오버헤드
List<Integer> numbers = IntStream.range(0, 1_000_000)
    .boxed()
    .collect(Collectors.toList());

long sum = numbers.stream()
    .reduce(0, (a, b) -> a + b);  // Integer 박싱/언박싱

// ✅ 기본형 스트림 사용
long sum = IntStream.range(0, 1_000_000)
    .sum();  // 훨씬 빠름
```

## 관련 개념
- [[Java-람다-Stream]]
- [[Java-제네릭스-Generics]]
- [[Java-Optional]]
- [[Java-내부클래스]]

## 면접 질문
1. 함수형 인터페이스란 무엇이며 왜 필요한가요?
2. Predicate와 Function의 차이는?
3. Consumer와 Supplier의 용도는?
4. 람다에서 외부 변수를 수정할 수 없는 이유는?
5. 기본형 특화 함수형 인터페이스를 사용하는 이유는?

## 참고 자료
- Java 8 in Action
- Effective Java 3/E - Item 42~44
- java.util.function 패키지 문서
