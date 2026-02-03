---
tags:
  - study
  - java
  - comparable
  - comparator
  - sorting
created: 2025-02-03
---

# Comparable & Comparator

## 한 줄 요약
> 객체 정렬을 위한 두 가지 인터페이스: 기본 정렬(Comparable)과 다양한 정렬(Comparator)

## 상세 설명

### Comparable vs Comparator

| 구분 | Comparable | Comparator |
|------|-----------|-----------|
| 패키지 | java.lang | java.util |
| 메서드 | compareTo(T o) | compare(T o1, T o2) |
| 정렬 기준 | **자연스러운 순서** (1개) | **다양한 순서** (여러 개) |
| 구현 위치 | 클래스 자체 | 별도 클래스 |
| 사용 | Collections.sort(list) | Collections.sort(list, comparator) |

## 코드 예시

### 1. Comparable - 기본 정렬

```java
class Student implements Comparable<Student> {
    private String name;
    private int score;
    
    public Student(String name, int score) {
        this.name = name;
        this.score = score;
    }
    
    // 점수 기준 오름차순
    @Override
    public int compareTo(Student other) {
        return Integer.compare(this.score, other.score);
    }
    
    @Override
    public String toString() {
        return name + "(" + score + ")";
    }
}

// 사용
List<Student> students = Arrays.asList(
    new Student("김철수", 85),
    new Student("이영희", 92),
    new Student("박민수", 78)
);

Collections.sort(students);  // Comparable 사용
System.out.println(students);
// [박민수(78), 김철수(85), 이영희(92)]
```

### 2. Comparator - 다양한 정렬

```java
class Student {
    private String name;
    private int score;
    private int age;
    
    public Student(String name, int score, int age) {
        this.name = name;
        this.score = score;
        this.age = age;
    }
    
    public String getName() { return name; }
    public int getScore() { return score; }
    public int getAge() { return age; }
    
    @Override
    public String toString() {
        return name + "(" + score + ", " + age + "세)";
    }
}

// 점수 기준 비교자
class ScoreComparator implements Comparator<Student> {
    @Override
    public int compare(Student s1, Student s2) {
        return Integer.compare(s1.getScore(), s2.getScore());
    }
}

// 이름 기준 비교자
class NameComparator implements Comparator<Student> {
    @Override
    public int compare(Student s1, Student s2) {
        return s1.getName().compareTo(s2.getName());
    }
}

// 나이 기준 비교자
class AgeComparator implements Comparator<Student> {
    @Override
    public int compare(Student s1, Student s2) {
        return Integer.compare(s1.getAge(), s2.getAge());
    }
}

// 사용
List<Student> students = Arrays.asList(
    new Student("김철수", 85, 20),
    new Student("이영희", 92, 19),
    new Student("박민수", 78, 21)
);

// 점수순 정렬
Collections.sort(students, new ScoreComparator());
System.out.println("점수순: " + students);

// 이름순 정렬
Collections.sort(students, new NameComparator());
System.out.println("이름순: " + students);

// 나이순 정렬
Collections.sort(students, new AgeComparator());
System.out.println("나이순: " + students);
```

### 3. 람다 표현식으로 간결하게

```java
List<Student> students = Arrays.asList(
    new Student("김철수", 85, 20),
    new Student("이영희", 92, 19),
    new Student("박민수", 78, 21)
);

// 점수순 (오름차순)
students.sort((s1, s2) -> Integer.compare(s1.getScore(), s2.getScore()));

// 점수순 (내림차순)
students.sort((s1, s2) -> Integer.compare(s2.getScore(), s1.getScore()));

// Comparator 정적 메서드 사용
students.sort(Comparator.comparingInt(Student::getScore));

// 내림차순
students.sort(Comparator.comparingInt(Student::getScore).reversed());

// 이름순
students.sort(Comparator.comparing(Student::getName));
```

### 4. 다중 조건 정렬

```java
// 점수순 → 같으면 나이순
students.sort(
    Comparator.comparingInt(Student::getScore)
              .thenComparingInt(Student::getAge)
);

// 점수 내림차순 → 이름 오름차순
students.sort(
    Comparator.comparingInt(Student::getScore).reversed()
              .thenComparing(Student::getName)
);
```

### 5. null 처리

```java
List<Student> students = Arrays.asList(
    new Student("김철수", 85, 20),
    null,
    new Student("이영희", 92, 19)
);

// null을 마지막으로
students.sort(Comparator.nullsLast(
    Comparator.comparingInt(Student::getScore)
));

// null을 처음으로
students.sort(Comparator.nullsFirst(
    Comparator.comparing(Student::getName)
));
```

### 6. 실전 예시: 상품 정렬

```java
class Product {
    private String name;
    private double price;
    private int stock;
    private double rating;
    
    public Product(String name, double price, int stock, double rating) {
        this.name = name;
        this.price = price;
        this.stock = stock;
        this.rating = rating;
    }
    
    public String getName() { return name; }
    public double getPrice() { return price; }
    public int getStock() { return stock; }
    public double getRating() { return rating; }
    
    @Override
    public String toString() {
        return String.format("%s (₩%.0f, 재고:%d, ★%.1f)", 
            name, price, stock, rating);
    }
}

List<Product> products = Arrays.asList(
    new Product("노트북", 1500000, 10, 4.5),
    new Product("마우스", 30000, 50, 4.3),
    new Product("키보드", 80000, 30, 4.7),
    new Product("모니터", 300000, 15, 4.6)
);

// 가격순 (저렴한 것부터)
products.sort(Comparator.comparingDouble(Product::getPrice));
System.out.println("가격순: " + products);

// 평점순 (높은 것부터)
products.sort(Comparator.comparingDouble(Product::getRating).reversed());
System.out.println("평점순: " + products);

// 재고 적은 순 → 같으면 평점 높은 순
products.sort(
    Comparator.comparingInt(Product::getStock)
              .thenComparingDouble(Product::getRating).reversed()
);
System.out.println("재고+평점: " + products);
```

### 7. 실전 예시: 날짜 정렬

```java
class Event {
    private String name;
    private LocalDateTime dateTime;
    
    public Event(String name, LocalDateTime dateTime) {
        this.name = name;
        this.dateTime = dateTime;
    }
    
    public String getName() { return name; }
    public LocalDateTime getDateTime() { return dateTime; }
    
    @Override
    public String toString() {
        return name + " @ " + dateTime;
    }
}

List<Event> events = Arrays.asList(
    new Event("회의", LocalDateTime.of(2025, 2, 5, 14, 0)),
    new Event("점심", LocalDateTime.of(2025, 2, 5, 12, 0)),
    new Event("발표", LocalDateTime.of(2025, 2, 5, 16, 0))
);

// 시간순 정렬
events.sort(Comparator.comparing(Event::getDateTime));
System.out.println(events);
```

### 8. String 정렬

```java
List<String> names = Arrays.asList("홍길동", "김철수", "이영희", "박민수");

// 기본 정렬 (사전순)
Collections.sort(names);
System.out.println(names);

// 길이순
names.sort(Comparator.comparingInt(String::length));
System.out.println(names);

// 길이순 → 같으면 사전순
names.sort(
    Comparator.comparingInt(String::length)
              .thenComparing(Comparator.naturalOrder())
);
```

### 9. 대소문자 무시 정렬

```java
List<String> words = Arrays.asList("apple", "Banana", "cherry", "Date");

// 기본 정렬 (대소문자 구분)
Collections.sort(words);
System.out.println(words);  // [Banana, Date, apple, cherry]

// 대소문자 무시
words.sort(String.CASE_INSENSITIVE_ORDER);
System.out.println(words);  // [apple, Banana, cherry, Date]

// 또는
words.sort(Comparator.comparing(String::toLowerCase));
```

### 10. 역순 정렬

```java
List<Integer> numbers = Arrays.asList(5, 2, 8, 1, 9);

// 오름차순
Collections.sort(numbers);
System.out.println(numbers);  // [1, 2, 5, 8, 9]

// 내림차순 방법 1
Collections.sort(numbers, Collections.reverseOrder());
System.out.println(numbers);  // [9, 8, 5, 2, 1]

// 내림차순 방법 2
Collections.sort(numbers, Comparator.reverseOrder());

// 내림차순 방법 3
numbers.sort(Comparator.naturalOrder().reversed());
```

## 주의사항 / 함정

### 1. compareTo/compare 반환값

```java
// ✅ 올바른 구현
public int compareTo(Student other) {
    return Integer.compare(this.score, other.score);
}

// ❌ 잘못된 구현 - 오버플로우 위험
public int compareTo(Student other) {
    return this.score - other.score;  // score가 크면 오버플로우!
}

// 예: score1 = 2000000000, score2 = -2000000000
// 결과: 음수 (잘못된 결과)
```

### 2. equals와 일관성

```java
class Student implements Comparable<Student> {
    private String name;
    private int score;
    
    @Override
    public int compareTo(Student other) {
        return Integer.compare(this.score, other.score);
    }
    
    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof Student)) return false;
        Student other = (Student) obj;
        // compareTo와 일관성 유지
        return this.score == other.score && 
               this.name.equals(other.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, score);
    }
}
```

### 3. null 처리

```java
// ❌ NPE 위험
public int compareTo(Student other) {
    return this.name.compareTo(other.name);  // name이 null이면?
}

// ✅ null 체크
public int compareTo(Student other) {
    if (this.name == null && other.name == null) return 0;
    if (this.name == null) return -1;
    if (other.name == null) return 1;
    return this.name.compareTo(other.name);
}

// ✅ Comparator.nullsFirst 사용
Comparator<Student> comparator = 
    Comparator.comparing(Student::getName, 
                        Comparator.nullsFirst(Comparator.naturalOrder()));
```

## 관련 개념
- [[Java-Wrapper클래스]]
- [[Java-컬렉션-프레임워크]]
- [[Java-람다-Stream]]

## 면접 질문
1. Comparable과 Comparator의 차이점은?
2. compareTo에서 뺄셈 대신 Integer.compare를 사용해야 하는 이유는?

## 참고 자료
- Java Documentation - Comparable, Comparator
- Effective Java - Item 14: Consider implementing Comparable