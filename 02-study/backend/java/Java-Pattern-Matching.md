---
tags:
  - study
  - java
  - pattern-matching
  - java17
  - switch
created: 2025-02-03
---

# Java Pattern Matching

## 한 줄 요약
> 타입 체크와 캐스팅을 간결하게 처리하는 Java 17+ 신기능

## 상세 설명

### Pattern Matching의 기본 개념

Pattern Matching은 객체의 타입과 구조를 검사하고 추출하는 과정을 간결하게 만들어주는 기능입니다.

**주요 기능**
1. **Pattern Matching for instanceof** (Java 16)
2. **Pattern Matching for switch** (Java 21)
3. **Record Patterns** (Java 21)
4. **Guarded Patterns** (Java 21)

## 코드 예시

### 1. instanceof Pattern Matching (Java 16)

#### 기존 방식 vs 새로운 방식

```java
// ❌ 기존 방식 - 타입 체크 후 캐스팅
if (obj instanceof String) {
    String str = (String) obj;  // 수동 캐스팅
    System.out.println(str.length());
}

// ✅ Pattern Matching - 타입 체크와 동시에 변수 선언
if (obj instanceof String str) {
    System.out.println(str.length());  // 바로 사용 가능
}
```

#### 실무 예시: 도형 면적 계산

```java
class Shape {}
class Circle extends Shape {
    private double radius;
    public Circle(double radius) { this.radius = radius; }
    public double getRadius() { return radius; }
}
class Rectangle extends Shape {
    private double width, height;
    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }
    public double getWidth() { return width; }
    public double getHeight() { return height; }
}

// ❌ 기존 방식
public double calculateArea(Shape shape) {
    if (shape instanceof Circle) {
        Circle circle = (Circle) shape;
        return Math.PI * circle.getRadius() * circle.getRadius();
    } else if (shape instanceof Rectangle) {
        Rectangle rect = (Rectangle) shape;
        return rect.getWidth() * rect.getHeight();
    }
    return 0;
}

// ✅ Pattern Matching
public double calculateArea(Shape shape) {
    if (shape instanceof Circle c) {
        return Math.PI * c.getRadius() * c.getRadius();
    } else if (shape instanceof Rectangle r) {
        return r.getWidth() * r.getHeight();
    }
    return 0;
}
```

#### 논리 연산자와 함께 사용

```java
// && 연산자와 함께
if (obj instanceof String str && str.length() > 5) {
    System.out.println("긴 문자열: " + str);
}

// || 연산자 - 주의: 변수 스코프 문제
if (obj instanceof String str || obj instanceof Integer num) {
    // str은 첫 번째 조건에서만 사용 가능
}
```

### 2. switch Pattern Matching (Java 21)

#### 기본 타입 패턴

```java
// ✅ switch에서 타입 패턴 사용
public String formatValue(Object obj) {
    return switch (obj) {
        case Integer i -> "정수: " + i;
        case String s -> "문자열: " + s;
        case Double d -> String.format("실수: %.2f", d);
        case null -> "null 값";
        default -> "알 수 없는 타입";
    };
}

// 사용
System.out.println(formatValue(42));        // 정수: 42
System.out.println(formatValue("Hello"));   // 문자열: Hello
System.out.println(formatValue(3.14));      // 실수: 3.14
```

#### Guarded Patterns (조건부 패턴)

```java
public String classifyNumber(Object obj) {
    return switch (obj) {
        case Integer i when i < 0 -> "음수";
        case Integer i when i == 0 -> "영";
        case Integer i when i > 0 -> "양수";
        case Double d when d < 0 -> "음수 실수";
        case Double d when d >= 0 -> "양수 실수";
        case null -> "null";
        default -> "숫자가 아님";
    };
}

// 사용
System.out.println(classifyNumber(-5));    // 음수
System.out.println(classifyNumber(0));     // 영
System.out.println(classifyNumber(10));    // 양수
System.out.println(classifyNumber(-3.14)); // 음수 실수
```

#### 실무 예시: HTTP 응답 처리

```java
sealed interface ApiResponse {}
record Success(String data) implements ApiResponse {}
record Error(int code, String message) implements ApiResponse {}
record Loading() implements ApiResponse {}

public void handleResponse(ApiResponse response) {
    switch (response) {
        case Success(String data) -> 
            System.out.println("성공: " + data);
        case Error(int code, String msg) when code >= 500 -> 
            System.out.println("서버 오류: " + msg);
        case Error(int code, String msg) when code >= 400 -> 
            System.out.println("클라이언트 오류: " + msg);
        case Loading() -> 
            System.out.println("로딩 중...");
    }
}
```

### 3. Record Patterns (Java 21)

#### 기본 Record Pattern

```java
record Point(int x, int y) {}

// ✅ Record 패턴으로 분해
public void printPoint(Object obj) {
    if (obj instanceof Point(int x, int y)) {
        System.out.println("x=" + x + ", y=" + y);
    }
}

// switch에서도 사용 가능
public String describePoint(Point p) {
    return switch (p) {
        case Point(0, 0) -> "원점";
        case Point(int x, 0) -> "X축 위의 점 (" + x + ")";
        case Point(0, int y) -> "Y축 위의 점 (" + y + ")";
        case Point(int x, int y) -> "일반 점 (" + x + ", " + y + ")";
    };
}
```

#### 중첩 Record Pattern

```java
record Address(String city, String street) {}
record Person(String name, Address address) {}

// 중첩 패턴 매칭
public void printPerson(Person person) {
    if (person instanceof Person(String name, Address(String city, String street))) {
        System.out.println(name + "님은 " + city + " " + street + "에 삽니다");
    }
}

// switch에서 중첩 패턴
public String getLocation(Person person) {
    return switch (person) {
        case Person(String name, Address(String city, _)) 
            when city.equals("서울") -> name + "님은 서울 거주";
        case Person(String name, Address(String city, _)) -> 
            name + "님은 " + city + " 거주";
    };
}
```

### 4. 실전 예시: JSON 파싱 결과 처리

```java
sealed interface JsonValue {}
record JsonObject(Map<String, JsonValue> fields) implements JsonValue {}
record JsonArray(List<JsonValue> elements) implements JsonValue {}
record JsonString(String value) implements JsonValue {}
record JsonNumber(double value) implements JsonValue {}
record JsonBoolean(boolean value) implements JsonValue {}
record JsonNull() implements JsonValue {}

public void processJson(JsonValue json) {
    switch (json) {
        case JsonObject(var fields) -> {
            System.out.println("객체 필드 수: " + fields.size());
            fields.forEach((key, value) -> 
                System.out.println(key + ": " + value));
        }
        case JsonArray(var elements) -> {
            System.out.println("배열 크기: " + elements.size());
            elements.forEach(this::processJson);
        }
        case JsonString(String s) -> 
            System.out.println("문자열: " + s);
        case JsonNumber(double n) -> 
            System.out.println("숫자: " + n);
        case JsonBoolean(boolean b) -> 
            System.out.println("불린: " + b);
        case JsonNull() -> 
            System.out.println("null");
    }
}
```

### 5. 실전 예시: 이벤트 처리

```java
sealed interface Event {}
record MouseClick(int x, int y, String button) implements Event {}
record KeyPress(String key, boolean ctrl, boolean shift) implements Event {}
record Scroll(int delta) implements Event {}

public void handleEvent(Event event) {
    switch (event) {
        case MouseClick(int x, int y, String btn) when btn.equals("left") -> 
            System.out.println("좌클릭: (" + x + ", " + y + ")");
        
        case MouseClick(int x, int y, String btn) when btn.equals("right") -> 
            showContextMenu(x, y);
        
        case KeyPress(String key, true, _) -> 
            System.out.println("단축키: Ctrl+" + key);
        
        case KeyPress(String key, false, false) -> 
            System.out.println("일반 키: " + key);
        
        case Scroll(int delta) when delta > 0 -> 
            System.out.println("위로 스크롤");
        
        case Scroll(int delta) when delta < 0 -> 
            System.out.println("아래로 스크롤");
        
        default -> 
            System.out.println("알 수 없는 이벤트");
    }
}
```

### 6. 실전 예시: AST (추상 구문 트리) 평가

```java
sealed interface Expr {}
record Const(int value) implements Expr {}
record Add(Expr left, Expr right) implements Expr {}
record Mul(Expr left, Expr right) implements Expr {}
record Neg(Expr expr) implements Expr {}

public int eval(Expr expr) {
    return switch (expr) {
        case Const(int value) -> value;
        case Add(Expr left, Expr right) -> eval(left) + eval(right);
        case Mul(Expr left, Expr right) -> eval(left) * eval(right);
        case Neg(Expr e) -> -eval(e);
    };
}

// 사용
Expr expr = new Add(
    new Const(10),
    new Mul(new Const(5), new Const(3))
);
System.out.println(eval(expr));  // 10 + (5 * 3) = 25
```

### 7. null 처리

```java
// switch에서 null 처리
public String processValue(String value) {
    return switch (value) {
        case null -> "null 값입니다";
        case String s when s.isEmpty() -> "빈 문자열";
        case String s when s.length() < 5 -> "짧은 문자열: " + s;
        case String s -> "긴 문자열: " + s;
    };
}

// instanceof에서 null 체크
if (obj instanceof String str && str != null) {
    // str은 null이 아님이 보장됨
}
```

### 8. 패턴의 우선순위

```java
public String classify(Object obj) {
    return switch (obj) {
        // 구체적인 패턴이 먼저 와야 함
        case String s when s.length() > 10 -> "긴 문자열";
        case String s -> "일반 문자열";  // 더 일반적인 패턴
        
        case Integer i when i < 0 -> "음수";
        case Integer i -> "정수";
        
        case null -> "null";
        default -> "기타";
    };
}
```

## 주의사항 / 함정

### 1. 변수 스코프

```java
// ✅ 조건문 내에서만 사용 가능
if (obj instanceof String str) {
    System.out.println(str.length());
} else {
    // str 사용 불가
}

// ❌ && 조건에서 주의
if (obj instanceof String str && str.length() > 5) {
    // OK - str 사용 가능
}

// ⚠️ || 조건에서는 복잡
if (obj instanceof String str || obj instanceof Integer num) {
    // str, num 모두 사용 불가 (어느 타입인지 불명확)
}
```

### 2. null 처리 주의

```java
Object obj = null;

// ❌ NPE 발생하지 않음 - false 반환
if (obj instanceof String str) {
    // 실행 안됨
}

// ✅ switch는 null case 필요
switch (obj) {
    case null -> System.out.println("null");
    case String s -> System.out.println(s);
}
```

### 3. 패턴 순서

```java
// ❌ 컴파일 에러 - 도달 불가능한 코드
public String test(Object obj) {
    return switch (obj) {
        case Object o -> "모든 객체";  // 모든 경우를 잡음
        case String s -> "문자열";     // 컴파일 에러!
    };
}

// ✅ 구체적인 패턴을 먼저
public String test(Object obj) {
    return switch (obj) {
        case String s -> "문자열";
        case Integer i -> "정수";
        case Object o -> "기타 객체";
    };
}
```

### 4. Sealed 클래스와 함께 사용 시 완전성

```java
sealed interface Result permits Success, Failure {}
record Success(String data) implements Result {}
record Failure(String error) implements Result {}

// ✅ 모든 경우를 커버하면 default 불필요
public void handle(Result result) {
    switch (result) {
        case Success(String data) -> System.out.println(data);
        case Failure(String error) -> System.out.println(error);
        // default 불필요 - 컴파일러가 완전성 검증
    }
}

// ❌ 새로운 타입 추가 시 컴파일 에러 발생
record Pending() implements Result {}  // sealed 위반
```

### 5. when 절의 부작용

```java
// ⚠️ when 절에서 부작용 있는 코드 사용 주의
int counter = 0;

public String test(Object obj) {
    return switch (obj) {
        case Integer i when counter++ < 5 -> "카운터: " + counter;
        default -> "기타";
    };
}

// counter의 값이 예측 불가능하게 변할 수 있음
```

## 관련 개념
- [[Java-Record]]
- [[Java-Sealed-Classes]]
- [[Java-제어문-배열-String]]

## 면접 질문
1. Pattern Matching for instanceof의 장점은?
2. switch의 Pattern Matching에서 when 절은 어떤 역할을 하나요?

## 참고 자료
- JEP 394: Pattern Matching for instanceof
- JEP 441: Pattern Matching for switch
- Java 21 Documentation