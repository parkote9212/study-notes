---
tags:
  - study
  - java
  - lambda
  - stream
created: 2025-02-01
---

# Java 람다와 Stream API

## 한 줄 요약
> 함수형 프로그래밍으로 간결하고 선언적인 코드 작성

## 상세 설명

### What
**람다**: 익명 함수를 간결하게 표현
**Stream**: 컬렉션 데이터를 함수형으로 처리

### Why
- 코드 간결성
- 가독성 향상
- 병렬 처리 쉬움
- 불변성 지향

## 람다 표현식

### 기본 문법
```java
// 기존 방식
Comparator<String> comp = new Comparator<String>() {
    @Override
    public int compare(String s1, String s2) {
        return s1.compareTo(s2);
    }
};

// 람다
Comparator<String> comp = (s1, s2) -> s1.compareTo(s2);
```

### 람다 형태
```java
// 1. 매개변수 없음
() -> System.out.println("Hello")

// 2. 매개변수 1개
x -> x * x

// 3. 매개변수 여러 개
(x, y) -> x + y

// 4. 중괄호 사용 (여러 문장)
(x, y) -> {
    int sum = x + y;
    return sum;
}

// 5. 타입 명시
(String s) -> s.length()
```

## 함수형 인터페이스

### 주요 인터페이스
```java
// 1. Predicate<T> - 조건 검사
Predicate<Integer> isPositive = x -> x > 0;
System.out.println(isPositive.test(5)); // true

// 2. Function<T, R> - 변환
Function<String, Integer> strLen = s -> s.length();
System.out.println(strLen.apply("Hello")); // 5

// 3. Consumer<T> - 소비 (void)
Consumer<String> print = s -> System.out.println(s);
print.accept("Hello");

// 4. Supplier<T> - 공급
Supplier<Double> random = () -> Math.random();
System.out.println(random.get());

// 5. BiFunction<T, U, R> - 2개 매개변수
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
System.out.println(add.apply(3, 5)); // 8
```

### 커스텀 함수형 인터페이스
```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
}

Calculator add = (a, b) -> a + b;
Calculator multiply = (a, b) -> a * b;

System.out.println(add.calculate(3, 5)); // 8
System.out.println(multiply.calculate(3, 5)); // 15
```

## Stream API

### Stream 생성
```java
// 1. 컬렉션
List<String> list = Arrays.asList("a", "b", "c");
Stream<String> stream = list.stream();

// 2. 배열
String[] arr = {"a", "b", "c"};
Stream<String> stream = Arrays.stream(arr);

// 3. 직접 생성
Stream<String> stream = Stream.of("a", "b", "c");

// 4. 빌더
Stream<String> stream = Stream.<String>builder()
    .add("a").add("b").add("c").build();

// 5. 무한 스트림
Stream<Integer> infinite = Stream.iterate(0, n -> n + 1);
Stream<Double> random = Stream.generate(Math::random);
```

### 중간 연산 (Intermediate)

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// filter - 필터링
numbers.stream()
    .filter(n -> n % 2 == 0)
    .forEach(System.out::println); // 2, 4

// map - 변환
numbers.stream()
    .map(n -> n * n)
    .forEach(System.out::println); // 1, 4, 9, 16, 25

// distinct - 중복 제거
Arrays.asList(1, 2, 2, 3, 3).stream()
    .distinct()
    .forEach(System.out::println); // 1, 2, 3

// sorted - 정렬
Arrays.asList(3, 1, 2).stream()
    .sorted()
    .forEach(System.out::println); // 1, 2, 3

// limit - 개수 제한
Stream.iterate(0, n -> n + 1)
    .limit(5)
    .forEach(System.out::println); // 0, 1, 2, 3, 4

// skip - 건너뛰기
Arrays.asList(1, 2, 3, 4, 5).stream()
    .skip(2)
    .forEach(System.out::println); // 3, 4, 5

// flatMap - 평탄화
List<List<Integer>> nested = Arrays.asList(
    Arrays.asList(1, 2),
    Arrays.asList(3, 4)
);
nested.stream()
    .flatMap(List::stream)
    .forEach(System.out::println); // 1, 2, 3, 4
```

### 최종 연산 (Terminal)

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// forEach - 각 요소 처리
numbers.stream().forEach(System.out::println);

// collect - 수집
List<Integer> even = numbers.stream()
    .filter(n -> n % 2 == 0)
    .collect(Collectors.toList()); // [2, 4]

// count - 개수
long count = numbers.stream()
    .filter(n -> n > 2)
    .count(); // 3

// reduce - 축소
int sum = numbers.stream()
    .reduce(0, (a, b) -> a + b); // 15

int max = numbers.stream()
    .reduce(Integer.MIN_VALUE, Integer::max); // 5

// anyMatch, allMatch, noneMatch
boolean hasEven = numbers.stream()
    .anyMatch(n -> n % 2 == 0); // true

boolean allPositive = numbers.stream()
    .allMatch(n -> n > 0); // true

// findFirst, findAny
Optional<Integer> first = numbers.stream()
    .filter(n -> n > 3)
    .findFirst(); // Optional[4]

// min, max
Optional<Integer> min = numbers.stream()
    .min(Integer::compareTo); // Optional[1]
```

## 메서드 레퍼런스

```java
// 1. 정적 메서드 참조
Function<String, Integer> parse1 = s -> Integer.parseInt(s);
Function<String, Integer> parse2 = Integer::parseInt;

// 2. 인스턴스 메서드 참조
String str = "Hello";
Supplier<Integer> len1 = () -> str.length();
Supplier<Integer> len2 = str::length;

// 3. 특정 타입의 임의 객체 인스턴스 메서드
Function<String, Integer> len3 = String::length;
System.out.println(len3.apply("Hello")); // 5

// 4. 생성자 참조
Supplier<List<String>> list1 = () -> new ArrayList<>();
Supplier<List<String>> list2 = ArrayList::new;
```

## 코드 예시
```java
// 실전 예제: 학생 성적 처리
class Student {
    String name;
    int score;
    
    Student(String name, int score) {
        this.name = name;
        this.score = score;
    }
}

List<Student> students = Arrays.asList(
    new Student("Alice", 85),
    new Student("Bob", 92),
    new Student("Charlie", 78),
    new Student("David", 95)
);

// 1. 90점 이상 학생 이름 추출
List<String> topStudents = students.stream()
    .filter(s -> s.score >= 90)
    .map(s -> s.name)
    .collect(Collectors.toList());
// [Bob, David]

// 2. 평균 점수
double avg = students.stream()
    .mapToInt(s -> s.score)
    .average()
    .orElse(0.0);
// 87.5

// 3. 점수별 그룹핑
Map<Integer, List<Student>> byScore = students.stream()
    .collect(Collectors.groupingBy(s -> s.score / 10 * 10));
// {70=[Charlie], 80=[Alice], 90=[Bob, David]}

// 4. 최고 점수 학생
Optional<Student> top = students.stream()
    .max(Comparator.comparing(s -> s.score));
```

## 주의사항 / 함정

1. **Stream 재사용 불가**
   ```java
   Stream<Integer> stream = Stream.of(1, 2, 3);
   stream.forEach(System.out::println);
   stream.forEach(System.out::println); // IllegalStateException!
   ```

2. **병렬 스트림 남용**
   ```java
   // 작은 데이터는 오히려 느림
   List<Integer> small = Arrays.asList(1, 2, 3);
   small.parallelStream(); // 오버헤드
   
   // 큰 데이터에만 사용
   List<Integer> large = IntStream.range(0, 1000000)
       .boxed().collect(Collectors.toList());
   large.parallelStream(); // 효과적
   ```

3. **부작용 있는 람다**
   ```java
   // ❌ 외부 변수 변경
   int sum = 0;
   numbers.stream()
       .forEach(n -> sum += n); // 컴파일 에러!
   
   // ✅ reduce 사용
   int sum = numbers.stream()
       .reduce(0, Integer::sum);
   ```

4. **박싱/언박싱 비용**
   ```java
   // ❌ 비효율
   List<Integer> list = Arrays.asList(1, 2, 3);
   int sum = list.stream()
       .reduce(0, Integer::sum);
   
   // ✅ IntStream 사용
   int sum = IntStream.of(1, 2, 3).sum();
   ```

## 관련 개념
- [[Java-제네릭스-Generics]]
- [[Java-컬렉션-프레임워크]]
- [[Java-Optional]]

## 면접 질문
1. 람다 표현식이 무엇이며 왜 사용하나요?
2. Stream의 중간 연산과 최종 연산의 차이는?
3. map()과 flatMap()의 차이를 설명하세요.
4. 병렬 스트림을 사용할 때 주의사항은?
5. 메서드 레퍼런스의 장점은?

## 참고 자료
- Effective Java Item 42-48
- Modern Java in Action