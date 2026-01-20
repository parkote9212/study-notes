# Java 함수형 프로그래밍: 람다와 Stream API

🏷️기술 카테고리: Functional, Java
💡핵심키워드: #함수형, #람다, #스트림
💼 면접 빈출도: 최상

# 1. Abstract: 핵심 요약

함수형 프로그래밍은 데이터를 변환하고 조작하는 선언적 방식입니다. Java 8부터 람다식과 Stream API로 함수형 패러다임을 지원합니다.

**핵심 개념**:
- 함수형 인터페이스 (@FunctionalInterface)
- 람다식 (Lambda Expression)
- Stream API (map, filter, reduce)
- 불변성

---

# 2. 함수형 인터페이스

```java
@FunctionalInterface
public interface MyFunction<T, R> {
    R apply(T t);
}

// 또는 표준 함수형 인터페이스 사용
Function<Integer, Integer> square = x -> x * x;
Predicate<String> isEmpty = String::isEmpty;
Consumer<String> print = System.out::println;
Supplier<String> supplier = () -> "Hello";
```

---

# 3. 람다식

```java
// 기존 방식
button.setOnClickListener(new ClickListener() {
    @Override
    public void onClick() {
        System.out.println("Clicked");
    }
});

// 람다식
button.setOnClickListener(() -> System.out.println("Clicked"));

// 람다식의 다양한 형태
x -> x * 2                    // 1개 인자
(x, y) -> x + y              // 여러 인자
(x, y) -> {                   // 블록
    int result = x + y;
    return result;
}
String::toUpperCase           // 메서드 레퍼런스
Integer::parseInt
list::add
```

---

# 4. Stream API

## 4.1 기본 연산

```java
// filter
List<Integer> numbers = List.of(1, 2, 3, 4, 5);
List<Integer> evens = numbers.stream()
        .filter(n -> n % 2 == 0)
        .collect(Collectors.toList());  // [2, 4]

// map
List<String> names = List.of("alice", "bob", "charlie");
List<String> upperNames = names.stream()
        .map(String::toUpperCase)
        .collect(Collectors.toList());  // [ALICE, BOB, CHARLIE]

// sorted
List<Integer> sorted = numbers.stream()
        .sorted()
        .collect(Collectors.toList());
```

## 4.2 집계 연산

```java
// reduce
Integer sum = numbers.stream()
        .reduce(0, (a, b) -> a + b);  // 15

// forEach
numbers.forEach(System.out::println);

// count
long count = numbers.stream()
        .filter(n -> n > 2)
        .count();  // 3

// anyMatch, allMatch, noneMatch
boolean hasEven = numbers.stream()
        .anyMatch(n -> n % 2 == 0);  // true
```

## 4.3 flatMap

```java
List<List<Integer>> lists = List.of(
    List.of(1, 2, 3),
    List.of(4, 5, 6)
);

List<Integer> flat = lists.stream()
        .flatMap(List::stream)
        .collect(Collectors.toList());  // [1,2,3,4,5,6]
```

---

# 5. 고급 활용

```java
// groupBy
Map<String, List<Student>> byGrade = students.stream()
        .collect(Collectors.groupingBy(Student::getGrade));

// partitioningBy
Map<Boolean, List<Integer>> partition = numbers.stream()
        .collect(Collectors.partitioningBy(n -> n % 2 == 0));

// 체인 연산
long result = students.stream()
        .filter(s -> s.getScore() > 80)
        .map(Student::getName)
        .sorted()
        .distinct()
        .count();
```

---

# 6. 면접 포인트

람다와 Stream은 현대 Java 개발의 필수 요소입니다. 선언적 코딩 스타일, 부작용 최소화, 성능 특성 등을 이해해야 합니다.

**작성일**: 2026년
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
