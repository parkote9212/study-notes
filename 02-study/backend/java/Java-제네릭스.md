---
tags:
  - study
  - java
  - generics
created: 2025-02-01
---

# Java 제네릭스

## 한 줄 요약
> 타입 파라미터화로 컴파일 타임 타입 안전성 보장

## 상세 설명

### What
타입을 파라미터로 받아 사용하는 기능

### Why
- 컴파일 타임 타입 체크
- 타입 캐스팅 불필요
- 코드 재사용성

## 제네릭 클래스

```java
class Box<T> {
    private T item;
    public void set(T item) { this.item = item; }
    public T get() { return item; }
}

Box<String> box = new Box<>();
box.set("Hello");
```

## 제네릭 메서드

```java
public static <T> void print(T[] array) {
    for (T element : array) {
        System.out.println(element);
    }
}
```

## 와일드카드

### extends (상한 경계)
```java
public static double sum(List<? extends Number> list) {
    double total = 0;
    for (Number num : list) {
        total += num.doubleValue();
    }
    return total;
}
```
- 읽기만 가능 (Producer)

### super (하한 경계)
```java
public static void addNumbers(List<? super Integer> list) {
    list.add(1);
    list.add(2);
}
```
- 쓰기 가능 (Consumer)

## PECS 원칙
**Producer Extends, Consumer Super**

```java
public static void copy(
    List<? extends Number> src,  // Producer
    List<? super Number> dest     // Consumer
) {
    for (Number num : src) {
        dest.add(num);
    }
}
```

## 타입 소거

```java
// 컴파일 전
class Box<T> { private T item; }

// 컴파일 후
class Box { private Object item; }
```

**제약:**
- `new T()` 불가
- `T[]` 배열 생성 불가
- `static T` 불가

## 코드 예시
```java
// Pair 클래스
class Pair<K, V> {
    private K key;
    private V value;
    
    public Pair(K key, V value) {
        this.key = key;
        this.value = value;
    }
}

Pair<String, Integer> pair = new Pair<>("Age", 25);
```

## 주의사항 / 함정

1. **Raw Type 금지**
   ```java
   // ❌
   List list = new ArrayList();
   
   // ✅
   List<String> list = new ArrayList<>();
   ```

2. **extends는 추가 불가**
   ```java
   List<? extends Number> list = new ArrayList<Integer>();
   list.add(1); // 컴파일 에러!
   ```

## 면접 질문
1. 제네릭스 사용 이유는?
2. extends vs super 차이는?
3. PECS 원칙이란?
4. 타입 소거란?

## 참고 자료
- Effective Java Item 26-31