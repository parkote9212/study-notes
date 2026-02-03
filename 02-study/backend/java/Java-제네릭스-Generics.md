---
tags:
  - study
  - java
  - generics
created: 2025-02-03
---

# Java 제네릭스 Generics

## 한 줄 요약
> 타입을 파라미터화하여 컴파일 타임에 타입 안정성을 보장하는 기능

## 상세 설명

### 제네릭스란?

제네릭스(Generics)는 클래스나 메서드에서 사용할 타입을 외부에서 지정할 수 있게 하는 기능입니다. Java 5부터 도입되었으며, 타입 안정성을 제공하고 불필요한 타입 캐스팅을 제거합니다.

**제네릭스 도입 이전의 문제점**
```java
// Java 5 이전
List list = new ArrayList();
list.add("Hello");
list.add(123);  // 다른 타입도 추가 가능 - 런타임 에러 위험

String str = (String) list.get(0);  // 매번 캐스팅 필요
String str2 = (String) list.get(1);  // ClassCastException 발생!
```

**제네릭스 사용**
```java
// Java 5 이후
List<String> list = new ArrayList<>();
list.add("Hello");
// list.add(123);  // 컴파일 에러 - 타입 안전성 보장

String str = list.get(0);  // 캐스팅 불필요
```

### 제네릭스의 장점

1. **타입 안정성**: 컴파일 타임에 타입 체크
2. **타입 캐스팅 제거**: 명시적 캐스팅 불필요
3. **코드 재사용성**: 다양한 타입에 대해 동일한 코드 사용
4. **가독성 향상**: 코드의 의도가 명확

## 코드 예시

### 제네릭 클래스

```java
// 제네릭 클래스 정의
public class Box<T> {
    private T item;
    
    public void setItem(T item) {
        this.item = item;
    }
    
    public T getItem() {
        return item;
    }
}

// 사용
Box<String> stringBox = new Box<>();
stringBox.setItem("Hello");
String str = stringBox.getItem();  // 캐스팅 불필요

Box<Integer> intBox = new Box<>();
intBox.setItem(123);
Integer num = intBox.getItem();
```

### 제네릭 타입 파라미터 명명 규칙

```java
// 관례적으로 사용되는 타입 파라미터 이름
// E - Element (컬렉션에서 주로 사용)
// K - Key (맵의 키)
// V - Value (맵의 값)
// N - Number (숫자)
// T - Type (일반적인 타입)
// S, U, V - 2번째, 3번째, 4번째 타입

public class Pair<K, V> {
    private K key;
    private V value;
    
    public Pair(K key, V value) {
        this.key = key;
        this.value = value;
    }
    
    public K getKey() { return key; }
    public V getValue() { return value; }
}

// 사용
Pair<String, Integer> pair = new Pair<>("Age", 30);
String key = pair.getKey();
Integer value = pair.getValue();
```

### 제네릭 메서드

```java
public class GenericMethod {
    // 제네릭 메서드 - 반환 타입 앞에 <T> 선언
    public static <T> void printArray(T[] array) {
        for (T element : array) {
            System.out.print(element + " ");
        }
        System.out.println();
    }
    
    // 두 개의 타입 파라미터
    public static <K, V> boolean compare(Pair<K, V> p1, Pair<K, V> p2) {
        return p1.getKey().equals(p2.getKey()) &&
               p1.getValue().equals(p2.getValue());
    }
    
    // 제네릭 메서드와 반환 타입
    public static <T> T getMiddle(T... items) {
        return items[items.length / 2];
    }
}

// 사용
Integer[] intArray = {1, 2, 3, 4, 5};
String[] strArray = {"A", "B", "C"};

GenericMethod.printArray(intArray);  // 1 2 3 4 5
GenericMethod.printArray(strArray);  // A B C

// 타입 명시 (생략 가능)
String middle = GenericMethod.<String>getMiddle("A", "B", "C");

// 타입 추론 (일반적)
String middle2 = GenericMethod.getMiddle("A", "B", "C");
```

### 제한된 타입 파라미터 (Bounded Type Parameters)

```java
// extends 키워드로 상한 제한
public class NumberBox<T extends Number> {
    private T number;
    
    public NumberBox(T number) {
        this.number = number;
    }
    
    public double getDoubleValue() {
        return number.doubleValue();  // Number의 메서드 사용 가능
    }
}

// 사용
NumberBox<Integer> intBox = new NumberBox<>(123);
NumberBox<Double> doubleBox = new NumberBox<>(3.14);
// NumberBox<String> strBox = new NumberBox<>("text");  // 컴파일 에러

// 여러 제한 조건 (클래스 & 인터페이스)
public class MultiBox<T extends Number & Comparable<T>> {
    private T value;
    
    public boolean isGreaterThan(T other) {
        return value.compareTo(other) > 0;
    }
}
```

### 와일드카드 (Wildcards)

**1. 비한정적 와일드카드 (Unbounded Wildcards) - `<?>`**
```java
public static void printList(List<?> list) {
    for (Object obj : list) {
        System.out.print(obj + " ");
    }
    System.out.println();
}

// 모든 타입의 List 허용
printList(Arrays.asList(1, 2, 3));
printList(Arrays.asList("A", "B", "C"));
```

**2. 상한 제한 와일드카드 (Upper Bounded Wildcards) - `<? extends T>`**
```java
// Number와 그 하위 타입만 허용
public static double sumOfList(List<? extends Number> list) {
    double sum = 0.0;
    for (Number num : list) {
        sum += num.doubleValue();
    }
    return sum;
}

// 사용
List<Integer> intList = Arrays.asList(1, 2, 3);
List<Double> doubleList = Arrays.asList(1.1, 2.2, 3.3);

System.out.println(sumOfList(intList));    // 6.0
System.out.println(sumOfList(doubleList)); // 6.6
```

**3. 하한 제한 와일드카드 (Lower Bounded Wildcards) - `<? super T>`**
```java
// Integer와 그 상위 타입만 허용
public static void addNumbers(List<? super Integer> list) {
    for (int i = 1; i <= 5; i++) {
        list.add(i);
    }
}

// 사용
List<Integer> intList = new ArrayList<>();
List<Number> numberList = new ArrayList<>();
List<Object> objectList = new ArrayList<>();

addNumbers(intList);    // OK
addNumbers(numberList); // OK
addNumbers(objectList); // OK
```

### PECS 원칙 (Producer Extends, Consumer Super)

```java
// Producer: 데이터를 읽기만 함 → extends 사용
public static void printNumbers(List<? extends Number> list) {
    for (Number num : list) {
        System.out.println(num);  // 읽기
    }
    // list.add(new Integer(1));  // 컴파일 에러 - 쓰기 불가
}

// Consumer: 데이터를 쓰기만 함 → super 사용
public static void addIntegers(List<? super Integer> list) {
    list.add(1);  // 쓰기
    list.add(2);
    // Integer num = list.get(0);  // 컴파일 에러 - 타입 보장 안됨
}
```

### 제네릭 타입 상속

```java
class Parent<T> {
    private T value;
    
    public T getValue() {
        return value;
    }
}

class Child<T> extends Parent<T> {
    private T childValue;
}

// 구체적 타입 지정
class StringChild extends Parent<String> {
    // String 타입으로 고정
}

// 추가 타입 파라미터
class ExtendedChild<T, U> extends Parent<T> {
    private U additionalValue;
}
```

### 타입 소거 (Type Erasure)

```java
// 컴파일 전 (소스 코드)
public class Box<T> {
    private T item;
    
    public void setItem(T item) {
        this.item = item;
    }
    
    public T getItem() {
        return item;
    }
}

// 컴파일 후 (바이트코드) - 타입 정보 제거
public class Box {
    private Object item;  // T → Object
    
    public void setItem(Object item) {
        this.item = item;
    }
    
    public Object getItem() {
        return item;
    }
}

// 타입 소거로 인한 제약
public class TypeErasure<T> {
    // ❌ 불가능한 것들
    // private T[] array = new T[10];  // 제네릭 배열 생성 불가
    // private static T staticField;   // static에 제네릭 사용 불가
    
    // if (item instanceof T) { }      // instanceof 사용 불가
    // T obj = new T();                // 제네릭 타입의 인스턴스 생성 불가
}
```

### 실무 예시: Repository 패턴

```java
// 제네릭 Repository 인터페이스
public interface Repository<T, ID> {
    T save(T entity);
    Optional<T> findById(ID id);
    List<T> findAll();
    void delete(T entity);
    boolean existsById(ID id);
}

// 구현
public class UserRepository implements Repository<User, Long> {
    private Map<Long, User> storage = new HashMap<>();
    
    @Override
    public User save(User user) {
        storage.put(user.getId(), user);
        return user;
    }
    
    @Override
    public Optional<User> findById(Long id) {
        return Optional.ofNullable(storage.get(id));
    }
    
    @Override
    public List<User> findAll() {
        return new ArrayList<>(storage.values());
    }
    
    @Override
    public void delete(User user) {
        storage.remove(user.getId());
    }
    
    @Override
    public boolean existsById(Long id) {
        return storage.containsKey(id);
    }
}
```

### 실무 예시: Builder 패턴

```java
public class Response<T> {
    private int status;
    private String message;
    private T data;
    
    private Response(Builder<T> builder) {
        this.status = builder.status;
        this.message = builder.message;
        this.data = builder.data;
    }
    
    public static <T> Builder<T> builder() {
        return new Builder<>();
    }
    
    public static class Builder<T> {
        private int status;
        private String message;
        private T data;
        
        public Builder<T> status(int status) {
            this.status = status;
            return this;
        }
        
        public Builder<T> message(String message) {
            this.message = message;
            return this;
        }
        
        public Builder<T> data(T data) {
            this.data = data;
            return this;
        }
        
        public Response<T> build() {
            return new Response<>(this);
        }
    }
    
    // Getters
    public T getData() { return data; }
}

// 사용
Response<User> userResponse = Response.<User>builder()
    .status(200)
    .message("Success")
    .data(new User("홍길동"))
    .build();

Response<List<String>> listResponse = Response.<List<String>>builder()
    .status(200)
    .message("Success")
    .data(Arrays.asList("A", "B", "C"))
    .build();
```

### 실무 예시: Result 타입

```java
public class Result<T, E> {
    private final T value;
    private final E error;
    private final boolean isSuccess;
    
    private Result(T value, E error, boolean isSuccess) {
        this.value = value;
        this.error = error;
        this.isSuccess = isSuccess;
    }
    
    public static <T, E> Result<T, E> success(T value) {
        return new Result<>(value, null, true);
    }
    
    public static <T, E> Result<T, E> failure(E error) {
        return new Result<>(null, error, false);
    }
    
    public boolean isSuccess() {
        return isSuccess;
    }
    
    public T getValue() {
        if (!isSuccess) {
            throw new IllegalStateException("Result is not success");
        }
        return value;
    }
    
    public E getError() {
        if (isSuccess) {
            throw new IllegalStateException("Result is success");
        }
        return error;
    }
}

// 사용
public Result<User, String> findUser(Long id) {
    User user = userRepository.findById(id);
    if (user != null) {
        return Result.success(user);
    } else {
        return Result.failure("User not found");
    }
}

Result<User, String> result = findUser(1L);
if (result.isSuccess()) {
    User user = result.getValue();
} else {
    String error = result.getError();
}
```

## 주의사항 / 함정

### 1. 제네릭 배열 생성 불가

```java
// ❌ 컴파일 에러
T[] array = new T[10];
List<String>[] stringLists = new List<String>[10];

// ✅ 해결 방법 1: 리스트 사용
List<T> list = new ArrayList<>();

// ✅ 해결 방법 2: Object 배열 생성 후 캐스팅 (권장 안함)
@SuppressWarnings("unchecked")
T[] array = (T[]) new Object[10];

// ✅ 해결 방법 3: Array.newInstance() 사용
public class GenericArray<T> {
    private T[] array;
    
    @SuppressWarnings("unchecked")
    public GenericArray(Class<T> clazz, int size) {
        array = (T[]) Array.newInstance(clazz, size);
    }
}
```

### 2. static 필드나 메서드에서 클래스 타입 파라미터 사용 불가

```java
public class Box<T> {
    // ❌ static 필드에 T 사용 불가
    // private static T staticItem;
    
    // ❌ static 메서드에 T 사용 불가
    // public static T getStaticItem() { }
    
    // ✅ static 메서드는 자체 타입 파라미터 선언 필요
    public static <E> void staticMethod(E item) {
        System.out.println(item);
    }
}
```

### 3. instanceof에 제네릭 타입 사용 불가

```java
public <T> void check(Object obj) {
    // ❌ 컴파일 에러
    // if (obj instanceof T) { }
    // if (obj instanceof List<String>) { }
    
    // ✅ Raw 타입으로 체크
    if (obj instanceof List) {
        List<?> list = (List<?>) obj;
    }
}
```

### 4. 제네릭 타입의 예외 처리

```java
// ❌ 제네릭 클래스가 Throwable 상속 불가
// public class MyException<T> extends Exception { }

// ❌ catch 절에 타입 파라미터 사용 불가
public <T extends Exception> void method() {
    try {
        // ...
    } catch (T e) {  // 컴파일 에러
        // ...
    }
}
```

### 5. 원시 타입(Raw Type) 사용 지양

```java
// ❌ Raw Type - 타입 안정성 상실
List list = new ArrayList();  // 경고 발생
list.add("String");
list.add(123);

// ✅ 제네릭 타입 명시
List<Object> list = new ArrayList<>();
```

### 6. 브리지 메서드로 인한 혼란

```java
class Node<T> {
    private T data;
    
    public void setData(T data) {
        this.data = data;
    }
}

class StringNode extends Node<String> {
    @Override
    public void setData(String data) {
        super.setData(data);
    }
}

// 컴파일러가 브리지 메서드 자동 생성
// public void setData(Object data) {
//     setData((String) data);
// }
```

### 7. 공변성과 불공변성

```java
// ❌ 제네릭은 불공변(Invariant)
List<Integer> intList = new ArrayList<>();
// List<Number> numList = intList;  // 컴파일 에러

// Integer는 Number의 하위 타입이지만
// List<Integer>는 List<Number>의 하위 타입이 아님

// ✅ 와일드카드로 해결
List<? extends Number> numList = intList;  // OK
```

## 관련 개념
- [[Java-컬렉션-프레임워크]]
- [[Java-람다-Stream]]
- [[Java-Optional]]
- [[Java-함수형인터페이스]]

## 면접 질문
1. 제네릭스를 사용하는 이유는 무엇인가요?
2. 와일드카드 `<?>`, `<? extends T>`, `<? super T>`의 차이는?
3. PECS 원칙이란 무엇인가요?
4. 타입 소거(Type Erasure)란 무엇이고 왜 필요한가요?
5. 제네릭 배열을 생성할 수 없는 이유는?
6. `List<Object>`와 `List<?>`의 차이는?

## 참고 자료
- Effective Java 3/E - Item 26~31 (제네릭스)
- Java Generics and Collections
- Oracle Java Tutorials - Generics