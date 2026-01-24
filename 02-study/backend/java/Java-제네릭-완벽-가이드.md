---
tags:
  - study
  - generics
  - java
  - 불변성
  - 제네릭스
created: 2026-01-17
difficulty: 상
---
# Java 제네릭 완벽 가이드 (타입 안전성)

🏷️기술 카테고리: Generics, Java
💡핵심키워드: #불변성, #제네릭스
💼 면접 빈출도: 최상

# 1. Abstract: 핵심 요약

제네릭(Generics)은 클래스나 메서드에서 사용할 내부 데이터 타입을 컴파일 시점에 지정하는 기술입니다. 런타임 에러(ClassCastException)를 방지하고 형변환을 제거하여 코드 안정성을 높입니다.

**핵심 원칙**:
- 타입 안전성: 컴파일 시점 타입 체크
- 형변환 제거: 코드 간결성 향상
- 코드 재사용: 하나의 코드로 여러 타입 처리

---

# 2. 제네릭 기본

## 2.1 주요 타입 파라미터

| 기호 | 의미 | 예시 |
| --- | --- | --- |
| **T** | Type | `class Box<T>` |
| **E** | Element | `List<E>` |
| **K, V** | Key, Value | `Map<K, V>` |
| **N** | Number | `<N extends Number>` |

## 2.2 제네릭 클래스

```java
public class Box<T> {
    private T item;
    
    public void set(T item) {
        this.item = item;
    }
    
    public T get() {
        return item;
    }
}

// 사용
Box<String> stringBox = new Box<>();
stringBox.set("Hello");
String value = stringBox.get();  // 형변환 불필요!
```

## 2.3 제네릭 메서드

```java
public class Utils {
    // 제네릭 메서드
    public static <T> void printArray(T[] array) {
        for (T element : array) {
            System.out.println(element);
        }
    }
    
    // 타입 제한
    public static <T extends Number> double sum(T[] array) {
        double sum = 0.0;
        for (T element : array) {
            sum += element.doubleValue();
        }
        return sum;
    }
}
```

---

# 3. 와일드카드 (?, extends, super)

## 3.1 상한 제한 (? extends T)

```java
// Producer - 데이터를 읽어올 때
public double sumOfList(List<? extends Number> list) {
    double sum = 0.0;
    for (Number num : list) {
        sum += num.doubleValue();
    }
    return sum;
}

// 사용
sumOfList(List.of(1, 2, 3));      // Integer OK
sumOfList(List.of(1.1, 2.2));     // Double OK
```

## 3.2 하한 제한 (? super T)

```java
// Consumer - 데이터를 추가할 때
public void addNumbers(List<? super Integer> list) {
    list.add(1);
    list.add(2);
    list.add(3);
}

// 사용
addNumbers(new ArrayList<Integer>());  // OK
addNumbers(new ArrayList<Number>());   // OK
addNumbers(new ArrayList<Object>());   // OK
```

## 3.3 PECS 원칙

**Producer Extends, Consumer Super**

```java
// 읽기: extends 사용 (Producer)
// 쓰기: super 사용 (Consumer)
public <T> void copy(List<? extends T> src, List<? super T> dest) {
    for (T item : src) {
        dest.add(item);
    }
}
```

---

# 4. Object vs 제네릭 비교

## 4.1 Object 사용 (문제점)

```java
// ❌ Bad
public class Box {
    private Object item;
    
    public void set(Object item) {
        this.item = item;
    }
    
    public Object get() {
        return item;  // 매번 형변환 필요
    }
}

// 사용
Box box = new Box();
box.set("Hello");
String str = (String) box.get();  // 형변환
```

## 4.2 제네릭 사용 (해결)

```java
// ✅ Good
public class Box<T> {
    private T item;
    
    public void set(T item) {
        this.item = item;
    }
    
    public T get() {
        return item;  // 형변환 불필요
    }
}

// 사용
Box<String> box = new Box<>();
box.set("Hello");
String str = box.get();  // 형변환 없음!
```

---

# 5. 타입 소거 (Type Erasure)

Java의 제네릭은 컴파일 시점에만 타입 체크를 하고, 런타임에는 타입 정보가 소거됩니다.

```java
Box<String> stringBox = new Box<>();
Box<Integer> intBox = new Box<>();

// 런타임에는 둘 다 Box로 같음!
System.out.println(stringBox.getClass() == intBox.getClass());  // true
```

**영향**:
- 제네릭 타입으로 배열 생성 불가: `new T[10]` ❌
- instanceof 검사 불가: `obj instanceof List<String>` ❌
- 리플렉션 제한 사항 있음

---

# 6. 실무 활용

## 6.1 컬렉션 API

```java
// 타입 안전한 리스트
List<String> names = new ArrayList<>();
names.add("Alice");
names.add("Bob");

// 반복 시 형변환 불필요
for (String name : names) {
    System.out.println(name);
}

// Map
Map<String, Integer> scores = new HashMap<>();
scores.put("Alice", 95);
scores.put("Bob", 87);
```

## 6.2 함수형 인터페이스

```java
// 제네릭 함수형 인터페이스
@FunctionalInterface
public interface Converter<F, T> {
    T convert(F from);
}

// 사용
Converter<String, Integer> converter = Integer::parseInt;
Integer result = converter.convert("123");
```

---

# 7. Interview Readiness

## ▶ Q1: 제네릭이 필요한 이유는?

**A**: 
1. **타입 안전성** - 컴파일 시점에 타입 체크로 런타임 에러 방지
2. **형변환 제거** - 코드 간결성 향상
3. **코드 재사용** - 하나의 클래스/메서드로 여러 타입 처리

## ▶ Q2: ? extends vs ? super 언제 쓰나?

**A**: 
- **? extends** - 리스트에서 값을 읽어올 때 (Producer)
- **? super** - 리스트에 값을 추가할 때 (Consumer)

## ▶ Q3: 제네릭 타입 소거란?

**A**: Java 제네릭은 컴파일 시점에만 존재하고 런타임에는 타입 정보가 제거됩니다. 따라서 `Box<String>`과 `Box<Integer>`는 런타임에 모두 `Box`로 동일합니다.

---

**작성일**: 2026-01-17
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
