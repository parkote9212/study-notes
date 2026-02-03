---
tags:
  - study
  - java
  - sealed
  - java17
  - inheritance
created: 2025-02-03
---

# Java Sealed Classes

## 한 줄 요약
> 클래스 계층을 명시적으로 제한하는 Java 17 신기능

## 상세 설명

### Sealed Classes의 기본 개념

Sealed Classes는 Java 17에서 정식 도입된 기능으로, **어떤 클래스가 자신을 상속할 수 있는지 명시적으로 제한**할 수 있습니다.

**주요 키워드**
- `sealed` - 봉인된 클래스/인터페이스
- `permits` - 허용된 하위 클래스 목록
- `non-sealed` - 봉인 해제 (자유로운 상속 허용)
- `final` - 더 이상 상속 불가

### Sealed Classes를 사용하는 이유

1. **제한된 계층 구조**: 예측 가능한 타입 시스템
2. **패턴 매칭 최적화**: 모든 경우를 컴파일러가 검증
3. **도메인 모델링**: 명확한 상속 관계 표현
4. **안전성**: 의도하지 않은 상속 방지

## 코드 예시

### 기본 Sealed Class

```java
// sealed class - permits로 허용된 클래스만 상속 가능
public sealed class Shape 
    permits Circle, Rectangle, Triangle {
    
    public abstract double area();
}

// final - 더 이상 상속 불가
final class Circle extends Shape {
    private final double radius;
    
    public Circle(double radius) {
        this.radius = radius;
    }
    
    @Override
    public double area() {
        return Math.PI * radius * radius;
    }
}

// final
final class Rectangle extends Shape {
    private final double width;
    private final double height;
    
    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double area() {
        return width * height;
    }
}

// non-sealed - 자유로운 상속 허용
non-sealed class Triangle extends Shape {
    private final double base;
    private final double height;
    
    public Triangle(double base, double height) {
        this.base = base;
        this.height = height;
    }
    
    @Override
    public double area() {
        return 0.5 * base * height;
    }
}

// ❌ 허용되지 않은 상속
// class Pentagon extends Shape {}  // 컴파일 에러

// ✅ Triangle은 non-sealed이므로 상속 가능
class IsoscelesTriangle extends Triangle {
    public IsoscelesTriangle(double base, double height) {
        super(base, height);
    }
}
```

### 같은 파일에 있는 경우 permits 생략

```java
// permits 생략 가능 (같은 파일 내)
public sealed class Result {
    record Success(String data) extends Result {}
    record Failure(String error) extends Result {}
}
```

### Sealed Interface

```java
public sealed interface Payment 
    permits CreditCard, BankTransfer, Cash {
    
    void process();
}

final class CreditCard implements Payment {
    private String cardNumber;
    
    @Override
    public void process() {
        System.out.println("신용카드 결제 처리");
    }
}

final class BankTransfer implements Payment {
    private String accountNumber;
    
    @Override
    public void process() {
        System.out.println("계좌이체 처리");
    }
}

final class Cash implements Payment {
    private int amount;
    
    @Override
    public void process() {
        System.out.println("현금 결제 처리");
    }
}
```

### 실전 예시: 결과 타입 (Result)

```java
public sealed interface Result<T, E> {
    record Success<T, E>(T value) implements Result<T, E> {}
    record Failure<T, E>(E error) implements Result<T, E> {}
}

// 사용
class UserService {
    public Result<User, String> findUser(Long id) {
        User user = repository.findById(id);
        
        if (user != null) {
            return new Result.Success<>(user);
        } else {
            return new Result.Failure<>("User not found: " + id);
        }
    }
}

// 패턴 매칭과 함께 사용 (Java 21+)
Result<User, String> result = userService.findUser(1L);

switch (result) {
    case Result.Success<User, String> s -> 
        System.out.println("User: " + s.value().getName());
    case Result.Failure<User, String> f -> 
        System.out.println("Error: " + f.error());
}
```

### 실전 예시: HTTP 응답

```java
public sealed interface HttpResponse 
    permits Ok, BadRequest, NotFound, ServerError {
    
    int statusCode();
    String message();
}

record Ok(String data) implements HttpResponse {
    @Override
    public int statusCode() { return 200; }
    
    @Override
    public String message() { return "OK"; }
}

record BadRequest(String error) implements HttpResponse {
    @Override
    public int statusCode() { return 400; }
    
    @Override
    public String message() { return error; }
}

record NotFound(String resource) implements HttpResponse {
    @Override
    public int statusCode() { return 404; }
    
    @Override
    public String message() { 
        return resource + " not found"; 
    }
}

record ServerError(String detail) implements HttpResponse {
    @Override
    public int statusCode() { return 500; }
    
    @Override
    public String message() { return detail; }
}

// 사용
public HttpResponse handleRequest(Request request) {
    try {
        String data = processRequest(request);
        return new Ok(data);
    } catch (ValidationException e) {
        return new BadRequest(e.getMessage());
    } catch (NotFoundException e) {
        return new NotFound(e.getResource());
    } catch (Exception e) {
        return new ServerError(e.getMessage());
    }
}
```

### 실전 예시: 주문 상태

```java
public sealed interface OrderStatus 
    permits Pending, Confirmed, Shipped, Delivered, Cancelled {
    
    boolean canCancel();
}

record Pending() implements OrderStatus {
    @Override
    public boolean canCancel() { return true; }
}

record Confirmed() implements OrderStatus {
    @Override
    public boolean canCancel() { return true; }
}

record Shipped(String trackingNumber) implements OrderStatus {
    @Override
    public boolean canCancel() { return false; }
}

record Delivered(LocalDateTime deliveredAt) implements OrderStatus {
    @Override
    public boolean canCancel() { return false; }
}

record Cancelled(String reason) implements OrderStatus {
    @Override
    public boolean canCancel() { return false; }
}

// 사용
class Order {
    private OrderStatus status;
    
    public void cancel(String reason) {
        if (status.canCancel()) {
            this.status = new Cancelled(reason);
        } else {
            throw new IllegalStateException("Cannot cancel order");
        }
    }
    
    public String getStatusMessage() {
        return switch (status) {
            case Pending p -> "주문 대기 중";
            case Confirmed c -> "주문 확인됨";
            case Shipped s -> "배송 중: " + s.trackingNumber();
            case Delivered d -> "배송 완료: " + d.deliveredAt();
            case Cancelled c -> "취소됨: " + c.reason();
        };
    }
}
```

### 계층 구조 제한

```java
// 2단계 계층
public sealed interface Animal permits Mammal, Bird {}

public sealed interface Mammal extends Animal 
    permits Dog, Cat {}

public sealed interface Bird extends Animal 
    permits Eagle, Sparrow {}

final class Dog implements Mammal {}
final class Cat implements Mammal {}
final class Eagle implements Bird {}
final class Sparrow implements Bird {}
```

### non-sealed 활용

```java
public sealed class Vehicle 
    permits Car, Truck, Motorcycle {
}

// non-sealed - 플러그인이나 확장 가능
non-sealed class Car extends Vehicle {
    // 다른 개발자가 Car를 상속할 수 있음
}

final class Truck extends Vehicle {}
final class Motorcycle extends Vehicle {}

// 가능
class ElectricCar extends Car {}
class SportsCar extends Car {}
```

### 실전 예시: AST (추상 구문 트리)

```java
public sealed interface Expression {
    record Constant(int value) implements Expression {}
    record Add(Expression left, Expression right) implements Expression {}
    record Multiply(Expression left, Expression right) implements Expression {}
    record Negate(Expression expr) implements Expression {}
}

// 평가기
class Evaluator {
    public int eval(Expression expr) {
        return switch (expr) {
            case Expression.Constant c -> c.value();
            case Expression.Add a -> eval(a.left()) + eval(a.right());
            case Expression.Multiply m -> eval(m.left()) * eval(m.right());
            case Expression.Negate n -> -eval(n.expr());
        };
    }
}

// 사용
Expression expr = new Expression.Add(
    new Expression.Constant(10),
    new Expression.Multiply(
        new Expression.Constant(5),
        new Expression.Constant(3)
    )
);

Evaluator evaluator = new Evaluator();
System.out.println(evaluator.eval(expr));  // 10 + (5 * 3) = 25
```

## 주의사항 / 함정

### 1. permits 목록 유지 관리

```java
// ❌ 새 하위 타입 추가 시 permits 업데이트 필요
public sealed class Animal permits Dog, Cat {
    // Bird 추가하려면 permits에 추가해야 함
}

// ✅ 같은 파일에서는 permits 생략 가능
public sealed class Animal {
    final class Dog extends Animal {}
    final class Cat extends Animal {}
    final class Bird extends Animal {}  // 자동으로 허용
}
```

### 2. 하위 클래스는 반드시 sealed, non-sealed, final 중 하나

```java
public sealed class Shape permits Circle {}

// ❌ 아무 키워드도 없으면 컴파일 에러
// class Circle extends Shape {}

// ✅ 반드시 하나 선택
final class Circle extends Shape {}
// 또는
sealed class Circle extends Shape permits SmallCircle {}
// 또는
non-sealed class Circle extends Shape {}
```

### 3. 같은 모듈/패키지 제약

```java
// Shape.java (com.example.shapes 패키지)
public sealed class Shape permits Circle, Rectangle {}

// Circle.java - 같은 패키지여야 함
package com.example.shapes;
final class Circle extends Shape {}

// ❌ 다른 패키지에서는 불가능
package com.example.other;
// final class Pentagon extends Shape {}  // 컴파일 에러
```

## 관련 개념
- [[Java-Record]]
- [[Java-Pattern-Matching]]
- [[Java-열거형Enum]]
- [[Java-상속과다형성]]

## 면접 질문
1. Sealed Classes를 사용하는 이유는 무엇인가요?
2. sealed, non-sealed, final의 차이점은?

## 참고 자료
- JEP 409: Sealed Classes
- Java 17 Documentation