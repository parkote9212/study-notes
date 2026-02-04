---
tags:
  - study
  - solid
  - oop
  - design-principles
created: 2025-02-03
---

# SOLID 원칙

## 한 줄 요약
> 객체지향 설계의 5가지 핵심 원칙으로 유지보수와 확장이 쉬운 코드 작성 지침

## 상세 설명

### SOLID 원칙이란?

Robert C. Martin(Uncle Bob)이 제시한 객체지향 설계 5대 원칙입니다.

**SOLID 구성**
1. **S**RP - Single Responsibility Principle (단일 책임 원칙)
2. **O**CP - Open/Closed Principle (개방-폐쇄 원칙)
3. **L**SP - Liskov Substitution Principle (리스코프 치환 원칙)
4. **I**SP - Interface Segregation Principle (인터페이스 분리 원칙)
5. **D**IP - Dependency Inversion Principle (의존관계 역전 원칙)

## 코드 예시

### 1. SRP - 단일 책임 원칙

**정의**: 클래스는 하나의 책임만 가져야 하며, 변경 이유도 하나여야 한다.

#### ❌ 위반 사례

```java
// 여러 책임을 가진 클래스
class User {
    private String name;
    private String email;
    
    // 책임 1: 사용자 데이터 관리
    public void setName(String name) {
        this.name = name;
    }
    
    // 책임 2: 데이터 검증
    public boolean isValidEmail() {
        return email.contains("@");
    }
    
    // 책임 3: 데이터베이스 저장
    public void save() {
        // DB 저장 로직
        System.out.println("DB에 저장");
    }
    
    // 책임 4: 이메일 발송
    public void sendEmail(String message) {
        // 이메일 발송 로직
        System.out.println("이메일 발송: " + message);
    }
}
```

#### ✅ 개선된 코드

```java
// 책임 1: 사용자 데이터
class User {
    private String name;
    private String email;
    
    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }
    
    public String getName() { return name; }
    public String getEmail() { return email; }
}

// 책임 2: 데이터 검증
class UserValidator {
    public boolean isValidEmail(String email) {
        return email != null && email.contains("@");
    }
    
    public boolean isValidName(String name) {
        return name != null && !name.isEmpty();
    }
}

// 책임 3: 데이터베이스 저장
class UserRepository {
    public void save(User user) {
        System.out.println("DB에 저장: " + user.getName());
    }
}

// 책임 4: 이메일 발송
class EmailService {
    public void sendWelcomeEmail(User user) {
        System.out.println("환영 이메일 발송: " + user.getEmail());
    }
}
```

### 2. OCP - 개방-폐쇄 원칙

**정의**: 확장에는 열려 있고, 수정에는 닫혀 있어야 한다.

#### ❌ 위반 사례

```java
class DiscountCalculator {
    public double calculate(String customerType, double price) {
        if (customerType.equals("REGULAR")) {
            return price * 0.9;  // 10% 할인
        } else if (customerType.equals("VIP")) {
            return price * 0.8;  // 20% 할인
        } else if (customerType.equals("VVIP")) {
            return price * 0.7;  // 30% 할인
        }
        return price;
    }
    // 새 고객 타입 추가 시 이 메서드를 수정해야 함!
}
```

#### ✅ 개선된 코드

```java
// 추상화
interface DiscountPolicy {
    double calculateDiscount(double price);
}

// 구체적인 정책들
class RegularDiscount implements DiscountPolicy {
    @Override
    public double calculateDiscount(double price) {
        return price * 0.9;
    }
}

class VipDiscount implements DiscountPolicy {
    @Override
    public double calculateDiscount(double price) {
        return price * 0.8;
    }
}

class VVipDiscount implements DiscountPolicy {
    @Override
    public double calculateDiscount(double price) {
        return price * 0.7;
    }
}

// 새로운 정책 추가 시 기존 코드 수정 없이 확장만 하면 됨
class PlatinumDiscount implements DiscountPolicy {
    @Override
    public double calculateDiscount(double price) {
        return price * 0.6;
    }
}

// 사용
class Customer {
    private DiscountPolicy discountPolicy;
    
    public Customer(DiscountPolicy discountPolicy) {
        this.discountPolicy = discountPolicy;
    }
    
    public double calculatePrice(double price) {
        return discountPolicy.calculateDiscount(price);
    }
}
```

### 3. LSP - 리스코프 치환 원칙

**정의**: 하위 타입은 상위 타입을 대체할 수 있어야 한다.

#### ❌ 위반 사례

```java
class Rectangle {
    protected int width;
    protected int height;
    
    public void setWidth(int width) {
        this.width = width;
    }
    
    public void setHeight(int height) {
        this.height = height;
    }
    
    public int getArea() {
        return width * height;
    }
}

// 정사각형은 직사각형의 특수한 형태? NO!
class Square extends Rectangle {
    @Override
    public void setWidth(int width) {
        this.width = width;
        this.height = width;  // 정사각형이므로 높이도 같이 변경
    }
    
    @Override
    public void setHeight(int height) {
        this.width = height;  // 정사각형이므로 너비도 같이 변경
        this.height = height;
    }
}

// 문제 발생
void test(Rectangle rect) {
    rect.setWidth(5);
    rect.setHeight(10);
    assert rect.getArea() == 50;  // Rectangle은 성공, Square는 실패!
}
```

#### ✅ 개선된 코드

```java
// 추상화
interface Shape {
    int getArea();
}

class Rectangle implements Shape {
    private final int width;
    private final int height;
    
    public Rectangle(int width, int height) {
        this.width = width;
        this.height = height;
    }
    
    @Override
    public int getArea() {
        return width * height;
    }
}

class Square implements Shape {
    private final int side;
    
    public Square(int side) {
        this.side = side;
    }
    
    @Override
    public int getArea() {
        return side * side;
    }
}

// 모든 Shape는 대체 가능
void test(Shape shape) {
    System.out.println("넓이: " + shape.getArea());
}
```

### 4. ISP - 인터페이스 분리 원칙

**정의**: 클라이언트는 자신이 사용하지 않는 메서드에 의존하지 않아야 한다.

#### ❌ 위반 사례

```java
// 너무 많은 기능을 가진 인터페이스
interface Worker {
    void work();
    void eat();
    void sleep();
    void attendMeeting();
    void writeReport();
}

// 로봇은 먹거나 자지 않음!
class Robot implements Worker {
    @Override
    public void work() {
        System.out.println("일함");
    }
    
    @Override
    public void eat() {
        // 로봇은 먹지 않음 - 불필요한 구현
        throw new UnsupportedOperationException();
    }
    
    @Override
    public void sleep() {
        // 로봇은 자지 않음 - 불필요한 구현
        throw new UnsupportedOperationException();
    }
    
    @Override
    public void attendMeeting() {
        System.out.println("회의 참석");
    }
    
    @Override
    public void writeReport() {
        System.out.println("보고서 작성");
    }
}
```

#### ✅ 개선된 코드

```java
// 인터페이스 분리
interface Workable {
    void work();
}

interface Eatable {
    void eat();
}

interface Sleepable {
    void sleep();
}

interface MeetingAttendable {
    void attendMeeting();
}

interface ReportWritable {
    void writeReport();
}

// 로봇은 필요한 인터페이스만 구현
class Robot implements Workable, MeetingAttendable, ReportWritable {
    @Override
    public void work() {
        System.out.println("일함");
    }
    
    @Override
    public void attendMeeting() {
        System.out.println("회의 참석");
    }
    
    @Override
    public void writeReport() {
        System.out.println("보고서 작성");
    }
}

// 사람은 모든 인터페이스 구현
class Human implements Workable, Eatable, Sleepable, 
                      MeetingAttendable, ReportWritable {
    @Override
    public void work() {
        System.out.println("일함");
    }
    
    @Override
    public void eat() {
        System.out.println("식사");
    }
    
    @Override
    public void sleep() {
        System.out.println("수면");
    }
    
    @Override
    public void attendMeeting() {
        System.out.println("회의 참석");
    }
    
    @Override
    public void writeReport() {
        System.out.println("보고서 작성");
    }
}
```

### 5. DIP - 의존관계 역전 원칙

**정의**: 구체화가 아닌 추상화에 의존해야 한다.

#### ❌ 위반 사례

```java
// 구체적인 클래스에 직접 의존
class MySQLDatabase {
    public void save(String data) {
        System.out.println("MySQL에 저장: " + data);
    }
}

class UserService {
    private MySQLDatabase database = new MySQLDatabase();
    
    public void createUser(String name) {
        // MySQL에 강하게 결합됨
        database.save(name);
    }
    // PostgreSQL로 변경하려면 UserService 코드 수정 필요!
}
```

#### ✅ 개선된 코드

```java
// 추상화
interface Database {
    void save(String data);
}

// 구체적인 구현들
class MySQLDatabase implements Database {
    @Override
    public void save(String data) {
        System.out.println("MySQL에 저장: " + data);
    }
}

class PostgreSQLDatabase implements Database {
    @Override
    public void save(String data) {
        System.out.println("PostgreSQL에 저장: " + data);
    }
}

class MongoDatabase implements Database {
    @Override
    public void save(String data) {
        System.out.println("MongoDB에 저장: " + data);
    }
}

// 추상화에 의존
class UserService {
    private Database database;
    
    // 의존성 주입
    public UserService(Database database) {
        this.database = database;
    }
    
    public void createUser(String name) {
        database.save(name);
    }
}

// 사용 - 런타임에 구현체 선택
UserService service1 = new UserService(new MySQLDatabase());
UserService service2 = new UserService(new PostgreSQLDatabase());
UserService service3 = new UserService(new MongoDatabase());
```

### 6. 실전 예시: 결제 시스템

```java
// DIP & OCP 적용
interface PaymentProcessor {
    void processPayment(double amount);
}

class CreditCardProcessor implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        System.out.println("신용카드 결제: " + amount);
    }
}

class KakaoPayProcessor implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        System.out.println("카카오페이 결제: " + amount);
    }
}

// SRP 적용 - 주문 처리만 담당
class Order {
    private PaymentProcessor paymentProcessor;
    private double totalAmount;
    
    public Order(PaymentProcessor paymentProcessor, double totalAmount) {
        this.paymentProcessor = paymentProcessor;
        this.totalAmount = totalAmount;
    }
    
    public void complete() {
        paymentProcessor.processPayment(totalAmount);
    }
}

// 새로운 결제수단 추가 - OCP
class NaverPayProcessor implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        System.out.println("네이버페이 결제: " + amount);
    }
}
```

## 주의사항 / 함정

### 1. 과도한 추상화

```java
// ❌ 너무 많은 추상화
interface Animal {}
interface Movable {}
interface Eatable {}
interface Soundable {}

class Dog implements Animal, Movable, Eatable, Soundable {
    // 구현...
}

// ✅ 적절한 수준의 추상화
interface Pet {
    void move();
    void eat();
    void makeSound();
}

class Dog implements Pet {
    // 구현...
}
```

### 2. SOLID 원칙 간 균형

```java
// SRP와 OCP를 동시에 고려
// 너무 SRP에 치우치면 클래스가 너무 많아짐
// 너무 OCP에 치우치면 불필요한 추상화 증가

// 실용적인 접근이 중요!
```

## 관련 개념
- [[디자인패턴-Strategy]]
- [[디자인패턴-Factory]]
- [[Spring-의존성주입]]

## 면접 질문
1. SOLID 원칙을 설명하고 실무에서 어떻게 적용했나요?
2. OCP와 DIP의 차이점은 무엇인가요?

## 참고 자료
- Clean Architecture - Robert C. Martin
- Agile Software Development - Robert C. Martin
- SOLID Principles in Java