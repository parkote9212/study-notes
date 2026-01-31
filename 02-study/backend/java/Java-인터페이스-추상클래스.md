---
tags:
  - study
  - java
  - oop
  - interface
created: 2026-01-31
---

# Java 인터페이스와 추상클래스

## 한 줄 요약
> 인터페이스는 구현 강제 규칙이고, 추상클래스는 공통 기능을 가진 불완전한 클래스다.

## 상세 설명

### 1. 추상클래스(Abstract Class)

**추상클래스란**: 하나 이상의 추상 메서드를 포함하는 불완전한 클래스
- `abstract` 키워드로 선언
- 객체 생성 불가 (new로 인스턴스화 불가)
- 상속을 통해서만 사용 가능
- 일반 메서드와 추상 메서드를 모두 가질 수 있음

**기본 문법**:
```java
public abstract class Animal {
    // 일반 필드
    protected String name;
    
    // 생성자 (자식 클래스에서 super()로 호출)
    public Animal(String name) {
        this.name = name;
    }
    
    // 일반 메서드 (구현 포함)
    public void sleep() {
        System.out.println(name + "이(가) 잡니다");
    }
    
    // 추상 메서드 (구현 없음, 자식이 반드시 구현)
    public abstract void sound();
    public abstract void move();
}
```

**추상클래스 상속**:
```java
public class Dog extends Animal {
    public Dog(String name) {
        super(name);
    }
    
    // 추상 메서드 반드시 구현
    @Override
    public void sound() {
        System.out.println("멍멍!");
    }
    
    @Override
    public void move() {
        System.out.println("네 발로 달립니다");
    }
}

// 사용
Animal dog = new Dog("뽀삐");
dog.sleep();   // 일반 메서드
dog.sound();   // 오버라이딩된 메서드
```

### 2. 인터페이스(Interface)

**인터페이스란**: 구현 없이 메서드 시그니처만 정의한 완전 추상 타입
- 모든 메서드가 public abstract (Java 8 이전)
- 모든 필드가 public static final (상수)
- 다중 구현 가능 (`implements` 여러 개)
- Java 8+: default 메서드, static 메서드 지원

**기본 문법**:
```java
public interface Flyable {
    // 상수 (public static final 생략 가능)
    int MAX_HEIGHT = 10000;
    
    // 추상 메서드 (public abstract 생략 가능)
    void fly();
    void land();
    
    // Java 8+: default 메서드 (구현 포함)
    default void checkAltitude() {
        System.out.println("고도 확인 중...");
    }
    
    // Java 8+: static 메서드
    static void printInfo() {
        System.out.println("비행 가능한 객체");
    }
}
```

**인터페이스 구현**:
```java
public class Bird implements Flyable {
    @Override
    public void fly() {
        System.out.println("새가 날아갑니다");
    }
    
    @Override
    public void land() {
        System.out.println("새가 착륙합니다");
    }
    
    // default 메서드는 오버라이딩 선택 사항
}

// 사용
Flyable bird = new Bird();
bird.fly();
bird.checkAltitude();  // default 메서드
Flyable.printInfo();   // static 메서드
```

### 3. 다중 구현

**Java는 다중 상속은 불가능하지만, 다중 구현은 가능**:
```java
public interface Swimmable {
    void swim();
}

public interface Flyable {
    void fly();
}

// 여러 인터페이스 동시 구현
public class Duck implements Flyable, Swimmable {
    @Override
    public void fly() {
        System.out.println("오리가 날아갑니다");
    }
    
    @Override
    public void swim() {
        System.out.println("오리가 수영합니다");
    }
}

// 사용
Duck duck = new Duck();
duck.fly();
duck.swim();

Flyable flyable = duck;  // 업캐스팅
Swimmable swimmable = duck;  // 업캐스팅
```

### 4. 추상클래스 vs 인터페이스 비교

| 구분 | 추상클래스 | 인터페이스 |
|------|----------|----------|
| 키워드 | abstract class | interface |
| 다중 상속 | 불가능 (단일 상속) | 가능 (다중 구현) |
| 메서드 | 추상/일반 메서드 모두 | 추상/default/static |
| 필드 | 모든 종류 가능 | public static final만 |
| 생성자 | 가능 | 불가능 |
| 접근 제어자 | 모두 사용 가능 | public만 (생략 가능) |
| 목적 | is-a (상속 관계) | can-do (기능 구현) |

### 5. Java 8+ 인터페이스 기능

**default 메서드**:
- 인터페이스에 구현 포함 가능
- 기존 인터페이스에 새 기능 추가 시 하위 호환성 유지

```java
public interface Vehicle {
    void start();
    
    // default 메서드 - 구현체가 선택적으로 오버라이드
    default void stop() {
        System.out.println("차량 정지");
    }
}

public class Car implements Vehicle {
    @Override
    public void start() {
        System.out.println("시동 켜기");
    }
    // stop()은 오버라이드 안 해도 됨
}
```

**static 메서드**:
- 인터페이스명으로 직접 호출
- 유틸리티 메서드 제공

```java
public interface Calculator {
    static int add(int a, int b) {
        return a + b;
    }
}

// 사용
int result = Calculator.add(1, 2);
```

**private 메서드 (Java 9+)**:
- default/static 메서드의 중복 코드 제거

```java
public interface Logger {
    default void logInfo(String msg) {
        log("INFO", msg);
    }
    
    default void logError(String msg) {
        log("ERROR", msg);
    }
    
    // private 메서드 - 내부에서만 사용
    private void log(String level, String msg) {
        System.out.println("[" + level + "] " + msg);
    }
}
```

## 코드 예시

### 예제 1: 결제 시스템

```java
// 인터페이스: 결제 가능 기능
public interface Payable {
    boolean pay(long amount);
    void refund(long amount);
    
    // default 메서드
    default void printReceipt(long amount) {
        System.out.println("결제 금액: " + amount + "원");
    }
}

// 추상클래스: 카드 결제 공통 기능
public abstract class CardPayment implements Payable {
    protected String cardNumber;
    protected String cardHolder;
    
    public CardPayment(String cardNumber, String cardHolder) {
        this.cardNumber = cardNumber;
        this.cardHolder = cardHolder;
    }
    
    // 공통 검증 로직
    protected boolean validateCard() {
        return cardNumber != null && cardNumber.length() == 16;
    }
    
    // 추상 메서드 - 카드사마다 다름
    public abstract String getCardCompany();
}

// 구현 클래스 1: 신용카드
public class CreditCard extends CardPayment {
    private long creditLimit;
    
    public CreditCard(String cardNumber, String cardHolder, long creditLimit) {
        super(cardNumber, cardHolder);
        this.creditLimit = creditLimit;
    }
    
    @Override
    public boolean pay(long amount) {
        if (!validateCard()) {
            System.out.println("카드 정보 오류");
            return false;
        }
        if (amount > creditLimit) {
            System.out.println("한도 초과");
            return false;
        }
        System.out.println("신용카드 결제 성공: " + amount);
        return true;
    }
    
    @Override
    public void refund(long amount) {
        System.out.println("신용카드 환불: " + amount);
    }
    
    @Override
    public String getCardCompany() {
        return "신한카드";
    }
}

// 구현 클래스 2: 체크카드
public class DebitCard extends CardPayment {
    private long balance;
    
    public DebitCard(String cardNumber, String cardHolder, long balance) {
        super(cardNumber, cardHolder);
        this.balance = balance;
    }
    
    @Override
    public boolean pay(long amount) {
        if (!validateCard()) {
            System.out.println("카드 정보 오류");
            return false;
        }
        if (amount > balance) {
            System.out.println("잔액 부족");
            return false;
        }
        balance -= amount;
        System.out.println("체크카드 결제 성공: " + amount);
        return true;
    }
    
    @Override
    public void refund(long amount) {
        balance += amount;
        System.out.println("체크카드 환불: " + amount);
    }
    
    @Override
    public String getCardCompany() {
        return "국민은행";
    }
}

// 사용
public class Main {
    public static void main(String[] args) {
        Payable credit = new CreditCard("1234567890123456", "홍길동", 1000000);
        Payable debit = new DebitCard("9876543210987654", "김철수", 500000);
        
        credit.pay(50000);
        credit.printReceipt(50000);
        
        debit.pay(30000);
        debit.printReceipt(30000);
    }
}
```

### 예제 2: 도형 계산

```java
// 인터페이스: 면적 계산 가능
public interface Measurable {
    double getArea();
    double getPerimeter();
}

// 추상클래스: 도형 공통 속성
public abstract class Shape implements Measurable {
    protected String color;
    
    public Shape(String color) {
        this.color = color;
    }
    
    // 공통 메서드
    public void displayInfo() {
        System.out.println("색상: " + color);
        System.out.println("넓이: " + getArea());
        System.out.println("둘레: " + getPerimeter());
    }
    
    // 추상 메서드는 Measurable에서 상속
}

// 원
public class Circle extends Shape {
    private double radius;
    
    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }
    
    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }
    
    @Override
    public double getPerimeter() {
        return 2 * Math.PI * radius;
    }
}

// 직사각형
public class Rectangle extends Shape {
    private double width;
    private double height;
    
    public Rectangle(String color, double width, double height) {
        super(color);
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double getArea() {
        return width * height;
    }
    
    @Override
    public double getPerimeter() {
        return 2 * (width + height);
    }
}

// 사용
Shape circle = new Circle("빨강", 5.0);
Shape rectangle = new Rectangle("파랑", 4.0, 6.0);

circle.displayInfo();
rectangle.displayInfo();
```

## 주의사항 / 함정

### 1. 추상클래스는 객체 생성 불가

```java
public abstract class Animal {
    public abstract void sound();
}

// ❌ 컴파일 에러
Animal animal = new Animal();

// ✅ 익명 클래스로는 가능
Animal animal = new Animal() {
    @Override
    public void sound() {
        System.out.println("소리");
    }
};
```

### 2. 인터페이스의 필드는 자동으로 상수

```java
public interface Config {
    int MAX_SIZE = 100;  // public static final 자동 적용
}

// ❌ 컴파일 에러: 값 변경 불가
Config.MAX_SIZE = 200;
```

### 3. 추상 메서드 미구현 시 자식도 추상클래스

```java
public abstract class Animal {
    public abstract void sound();
    public abstract void move();
}

// ❌ 컴파일 에러: move()를 구현하지 않음
public class Dog extends Animal {
    @Override
    public void sound() {
        System.out.println("멍멍");
    }
}

// ✅ 해결 방법 1: 모든 추상 메서드 구현
public class Dog extends Animal {
    @Override
    public void sound() {
        System.out.println("멍멍");
    }
    
    @Override
    public void move() {
        System.out.println("달린다");
    }
}

// ✅ 해결 방법 2: 자식도 추상클래스로
public abstract class Dog extends Animal {
    @Override
    public void sound() {
        System.out.println("멍멍");
    }
    // move()는 여전히 추상 메서드
}
```

### 4. default 메서드 충돌

```java
public interface A {
    default void print() {
        System.out.println("A");
    }
}

public interface B {
    default void print() {
        System.out.println("B");
    }
}

// ❌ 컴파일 에러: 어떤 print()를 사용할지 모호
public class C implements A, B {
}

// ✅ 해결: 명시적으로 오버라이드
public class C implements A, B {
    @Override
    public void print() {
        A.super.print();  // A의 print() 사용
        // 또는 B.super.print();
        // 또는 새로운 구현
    }
}
```

### 5. 인터페이스 상속 시 주의

```java
public interface Animal {
    void sound();
}

public interface Pet extends Animal {
    void play();
}

// Pet을 구현하면 sound()와 play() 모두 구현 필요
public class Dog implements Pet {
    @Override
    public void sound() {
        System.out.println("멍멍");
    }
    
    @Override
    public void play() {
        System.out.println("놀기");
    }
}
```

## 관련 개념
- [[Java-상속-다형성-super]]
- [[Java-클래스-객체지향기초]]

## 학습 로드맵 (TODO)
- 함수형 인터페이스(@FunctionalInterface) 문서 필요
- 마커 인터페이스(Serializable, Cloneable) 문서 필요
- SOLID 원칙(특히 ISP, DIP) 문서 필요

## 면접 질문
1. 추상클래스와 인터페이스의 차이는?
2. 언제 추상클래스를 사용하고 언제 인터페이스를 사용하나?
3. Java 8의 default 메서드가 추가된 이유는?
4. 인터페이스에서 다중 구현이 가능한 이유는?
5. 추상클래스는 왜 객체 생성이 불가능한가?

## 참고 자료
- Effective Java Item 20: Prefer interfaces to abstract classes
- Java Language Specification - Interfaces
- Clean Code - Use Polymorphism
