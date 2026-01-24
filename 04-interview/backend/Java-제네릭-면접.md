---
tags:
  - interview
  - java
created: 2026-01-17
difficulty: 최상
---

# Java 제네릭 (면접 Q&A)

## 질문 1
> 제네릭이 필요한 이유는?

## 핵심 답변 (3줄)
1. **타입 안전성** - 컴파일 시점에 타입 체크로 ClassCastException 방지
2. **형변환 제거** - 코드 간결성 향상, 가독성 증진
3. **코드 재사용** - 하나의 클래스로 여러 타입 처리 가능

## 상세 설명

제네릭 도입 전후의 차이를 보면 명확합니다:

**제네릭 없이 (Object 사용)**:
- 모든 타입을 Object로 받음
- 형변환 필요: `String str = (String) list.get(0)`
- 잘못된 형변환 시 런타임 에러 발생
- ClassCastException으로 늦게 발견

**제네릭 사용**:
- 타입 지정: `List<String> list`
- 형변환 불필요
- 컴파일 시점에 타입 체크
- 에러를 조기에 발견

이는 특히 대규모 프로젝트에서 런타임 버그를 사전에 방지하는 데 중요합니다.

## 코드 예시
```java
// ❌ Object 사용 (위험)
List list = new ArrayList();
list.add("Alice");
list.add(123);  // 타입 체크 없음
String name = (String) list.get(0);      // OK
String number = (String) list.get(1);    // ClassCastException!

// ✅ 제네릭 사용 (안전)
List<String> names = new ArrayList<>();
names.add("Alice");
names.add(123);  // 컴파일 에러!
String name = names.get(0);  // 형변환 불필요
```

## 꼬리 질문 예상
- "제네릭이 런타임에도 존재하나요?" → 아니요, 컴파일 후 타입 정보가 제거됩니다.
- "배열로는 제네릭을 쓸 수 없다고 들었는데?" → 맞습니다, `new T[10]`은 불가능하고 `List<T>`를 사용합니다.

## 참고
- [[Java-제네릭-완벽-가이드]]

---

## 질문 2
> ? extends vs ? super 언제 어떻게 쓰나요?

## 핵심 답변 (3줄)
1. **? extends T** - 리스트에서 T 타입의 데이터를 읽어올 때 (Producer)
2. **? super T** - 리스트에 T 타입의 데이터를 추가할 때 (Consumer)
3. **PECS 원칙** - Producer Extends, Consumer Super

## 상세 설명

와일드카드는 제네릭의 유연성을 제공하면서도 타입 안전성을 유지합니다:

**? extends T (상한 제한)**:
- 반환 타입이 T의 하위 클래스임을 보장
- 읽기는 안전 (T로 형변환 가능)
- 쓰기는 위험 (어떤 하위 타입인지 모르므로)
- 예: `List<? extends Number>`는 Integer, Double 등 모두 가능

**? super T (하한 제한)**:
- 받는 타입이 T의 상위 클래스임을 보장
- 쓰기는 안전 (T 타입을 상위 클래스에 저장 가능)
- 읽기는 제한적 (Object로만 안전)
- 예: `List<? super Integer>`는 Integer, Number, Object 모두 가능

**PECS 원칙** - Joshua Bloch의 Effective Java에서 제시:
```
Producer: 데이터를 꺼내는 용도 → extends
Consumer: 데이터를 넣는 용도 → super
```

## 코드 예시
```java
// Producer - extends (읽기)
public void processNumbers(List<? extends Number> list) {
    for (Number num : list) {
        System.out.println(num.doubleValue());
    }
}

// 사용
processNumbers(List.of(1, 2, 3));           // Integer OK
processNumbers(List.of(1.1, 2.2, 3.3));     // Double OK

// Consumer - super (쓰기)
public void addIntegers(List<? super Integer> list) {
    list.add(10);
    list.add(20);
    list.add(30);
}

// 사용
List<Integer> integers = new ArrayList<>();
addIntegers(integers);          // OK

List<Number> numbers = new ArrayList<>();
addIntegers(numbers);           // OK

List<Object> objects = new ArrayList<>();
addIntegers(objects);           // OK

// 쓰기 불가능
List<? extends Number> nums = new ArrayList<Integer>();
nums.add(10);  // 컴파일 에러! (어떤 타입이 있을지 모르므로)
```

## 꼬리 질문 예상
- "extends와 super를 섞어 쓸 수 있나요?" → 네, 복사 메서드 같이: `copy(List<? extends T> src, List<? super T> dest)`
- "? 만 쓰는 경우는?" → 읽기만 하고 쓰기를 하지 않을 때입니다.

## 참고
- [[Java-제네릭-완벽-가이드]]
- PECS (Producer Extends, Consumer Super)

---

## 질문 3
> 제네릭 타입 소거(Type Erasure)란?

## 핵심 답변 (3줄)
1. **컴파일 후 제거** - 컴파일 시점에는 제네릭 타입이 있지만, 런타임에는 제거됨
2. **호환성** - 레거시 코드와의 호환성을 위해 설계됨
3. **제약 발생** - `new T[10]` 불가, instanceof 제한 등

## 상세 설명

Java의 제네릭은 컴파일 타임 안전성을 위해 설계되었으며, 런타임에는 타입 정보가 제거됩니다. 이를 **타입 소거(Type Erasure)**라고 합니다.

**컴파일 과정**:
```
Box<String> → 컴파일러 → Box (런타임에는 타입 정보 없음)
Box<Integer> → 컴파일러 → Box (같은 클래스)
```

**왜 이렇게 설계되었나?**:
- Java 5 이전의 레거시 코드와 호환성 유지
- 바이트 코드 크기 증가 방지
- 런타임 오버헤드 제거

**결과**:
```java
Box<String> stringBox = new Box<>();
Box<Integer> intBox = new Box<>();

// 런타임에는 모두 Box!
System.out.println(stringBox.getClass() == intBox.getClass());  // true
```

**제약사항**:

1. **배열 생성 불가**:
```java
new T[10];        // ❌ 불가능
new List<T>[10];  // ❌ 불가능
```
해결책: `List<List<T>>` 사용

2. **instanceof 제한**:
```java
if (obj instanceof List<String>) {}  // ❌ 불가능
if (obj instanceof List) {}          // ✅ 가능 (타입 확인 불가)
```

3. **정적 필드 제약**:
```java
static T value;        // ❌ 불가능
static List<T> list;   // ❌ 불가능
```

## 코드 예시
```java
// 타입 소거 확인
List<String> stringList = new ArrayList<>();
List<Integer> intList = new ArrayList<>();

// 런타임 클래스는 동일
System.out.println(stringList.getClass());  // class java.util.ArrayList
System.out.println(intList.getClass());     // class java.util.ArrayList
System.out.println(stringList.getClass() == intList.getClass());  // true

// 타입 정보 접근 불가
List<String> list = new ArrayList<>();
// list의 제네릭 타입을 런타임에 가져올 수 없음
```

## 꼬리 질문 예상
- "그럼 리플렉션으로 제네릭 타입을 알 수 있나요?" → ParameterizedType이나 TypeToken 패턴으로 부분적으로 가능합니다.
- "타입 소거 때문에 문제가 많지 않나요?" → 대부분 설계적으로 회피 가능하며, Guava의 TypeToken 같은 라이브러리로 보완합니다.

## 참고
- [[Java-제네릭-완벽-가이드]]
- Java Type Erasure
