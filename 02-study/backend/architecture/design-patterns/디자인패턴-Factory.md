---
tags:
  - study
  - design-pattern
  - factory
  - creational-pattern
created: 2025-02-03
---

# Factory 패턴

## 한 줄 요약
> 객체 생성 로직을 캡슐화하여 클라이언트 코드와 구체적인 클래스 결합을 줄이는 생성 패턴

## 상세 설명

### Factory 패턴이란?

**목적**: 객체 생성을 서브클래스나 별도 팩토리 클래스에 위임

**종류**
1. Simple Factory (간단한 팩토리)
2. Factory Method Pattern (팩토리 메서드 패턴)
3. Abstract Factory Pattern (추상 팩토리 패턴)

## 코드 예시

### 1. Simple Factory

```java
// 제품 인터페이스
interface Shape {
    void draw();
}

// 구체적인 제품들
class Circle implements Shape {
    @Override
    public void draw() {
        System.out.println("원 그리기");
    }
}

class Rectangle implements Shape {
    @Override
    public void draw() {
        System.out.println("사각형 그리기");
    }
}

class Triangle implements Shape {
    @Override
    public void draw() {
        System.out.println("삼각형 그리기");
    }
}

// Simple Factory
class ShapeFactory {
    public static Shape createShape(String type) {
        return switch (type.toUpperCase()) {
            case "CIRCLE" -> new Circle();
            case "RECTANGLE" -> new Rectangle();
            case "TRIANGLE" -> new Triangle();
            default -> throw new IllegalArgumentException("알 수 없는 도형: " + type);
        };
    }
}

// 사용
Shape circle = ShapeFactory.createShape("CIRCLE");
circle.draw();
```

### 2. Factory Method Pattern

```java
// 제품 인터페이스
interface Pizza {
    void prepare();
    void bake();
    void cut();
    void box();
}

// 구체적인 제품들
class CheesePizza implements Pizza {
    @Override
    public void prepare() {
        System.out.println("치즈 피자 준비");
    }
    
    @Override
    public void bake() {
        System.out.println("치즈 피자 굽기");
    }
    
    @Override
    public void cut() {
        System.out.println("치즈 피자 자르기");
    }
    
    @Override
    public void box() {
        System.out.println("치즈 피자 포장");
    }
}

class PepperoniPizza implements Pizza {
    @Override
    public void prepare() {
        System.out.println("페퍼로니 피자 준비");
    }
    
    @Override
    public void bake() {
        System.out.println("페퍼로니 피자 굽기");
    }
    
    @Override
    public void cut() {
        System.out.println("페퍼로니 피자 자르기");
    }
    
    @Override
    public void box() {
        System.out.println("페퍼로니 피자 포장");
    }
}

// 추상 Creator
abstract class PizzaStore {
    // Template Method
    public Pizza orderPizza(String type) {
        Pizza pizza = createPizza(type);  // Factory Method 호출
        
        pizza.prepare();
        pizza.bake();
        pizza.cut();
        pizza.box();
        
        return pizza;
    }
    
    // Factory Method - 서브클래스에서 구현
    protected abstract Pizza createPizza(String type);
}

// 구체적인 Creator들
class NYPizzaStore extends PizzaStore {
    @Override
    protected Pizza createPizza(String type) {
        return switch (type) {
            case "cheese" -> new NYStyleCheesePizza();
            case "pepperoni" -> new NYStylePepperoniPizza();
            default -> throw new IllegalArgumentException("Unknown type");
        };
    }
}

class ChicagoPizzaStore extends PizzaStore {
    @Override
    protected Pizza createPizza(String type) {
        return switch (type) {
            case "cheese" -> new ChicagoStyleCheesePizza();
            case "pepperoni" -> new ChicagoStylePepperoniPizza();
            default -> throw new IllegalArgumentException("Unknown type");
        };
    }
}

// 사용
PizzaStore nyStore = new NYPizzaStore();
Pizza pizza = nyStore.orderPizza("cheese");
```

### 3. Abstract Factory Pattern

```java
// 추상 제품들
interface Button {
    void render();
}

interface Checkbox {
    void render();
}

// Windows 제품군
class WindowsButton implements Button {
    @Override
    public void render() {
        System.out.println("Windows 버튼 렌더링");
    }
}

class WindowsCheckbox implements Checkbox {
    @Override
    public void render() {
        System.out.println("Windows 체크박스 렌더링");
    }
}

// Mac 제품군
class MacButton implements Button {
    @Override
    public void render() {
        System.out.println("Mac 버튼 렌더링");
    }
}

class MacCheckbox implements Checkbox {
    @Override
    public void render() {
        System.out.println("Mac 체크박스 렌더링");
    }
}

// 추상 팩토리
interface GUIFactory {
    Button createButton();
    Checkbox createCheckbox();
}

// 구체적인 팩토리들
class WindowsFactory implements GUIFactory {
    @Override
    public Button createButton() {
        return new WindowsButton();
    }
    
    @Override
    public Checkbox createCheckbox() {
        return new WindowsCheckbox();
    }
}

class MacFactory implements GUIFactory {
    @Override
    public Button createButton() {
        return new MacButton();
    }
    
    @Override
    public Checkbox createCheckbox() {
        return new MacCheckbox();
    }
}

// 클라이언트
class Application {
    private Button button;
    private Checkbox checkbox;
    
    public Application(GUIFactory factory) {
        button = factory.createButton();
        checkbox = factory.createCheckbox();
    }
    
    public void render() {
        button.render();
        checkbox.render();
    }
}

// 사용
String os = System.getProperty("os.name").toLowerCase();
GUIFactory factory = os.contains("win") 
    ? new WindowsFactory() 
    : new MacFactory();

Application app = new Application(factory);
app.render();
```

### 실전 예시: 알림 시스템

```java
// 알림 인터페이스
interface Notification {
    void send(String message);
}

// 구체적인 알림들
class EmailNotification implements Notification {
    private String email;
    
    public EmailNotification(String email) {
        this.email = email;
    }
    
    @Override
    public void send(String message) {
        System.out.println("이메일 발송 (" + email + "): " + message);
    }
}

class SMSNotification implements Notification {
    private String phoneNumber;
    
    public SMSNotification(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }
    
    @Override
    public void send(String message) {
        System.out.println("SMS 발송 (" + phoneNumber + "): " + message);
    }
}

class PushNotification implements Notification {
    private String deviceToken;
    
    public PushNotification(String deviceToken) {
        this.deviceToken = deviceToken;
    }
    
    @Override
    public void send(String message) {
        System.out.println("푸시 알림 (" + deviceToken + "): " + message);
    }
}

// 팩토리
class NotificationFactory {
    public static Notification createNotification(String type, String recipient) {
        return switch (type.toUpperCase()) {
            case "EMAIL" -> new EmailNotification(recipient);
            case "SMS" -> new SMSNotification(recipient);
            case "PUSH" -> new PushNotification(recipient);
            default -> throw new IllegalArgumentException("지원하지 않는 타입: " + type);
        };
    }
}

// 사용
Notification notification = NotificationFactory.createNotification(
    "EMAIL", "user@example.com"
);
notification.send("환영합니다!");
```

### 실전 예시: 데이터베이스 연결

```java
// 연결 인터페이스
interface DatabaseConnection {
    void connect();
    void executeQuery(String sql);
    void disconnect();
}

// 구체적인 연결들
class MySQLConnection implements DatabaseConnection {
    private String connectionString;
    
    public MySQLConnection(String connectionString) {
        this.connectionString = connectionString;
    }
    
    @Override
    public void connect() {
        System.out.println("MySQL 연결: " + connectionString);
    }
    
    @Override
    public void executeQuery(String sql) {
        System.out.println("MySQL 쿼리 실행: " + sql);
    }
    
    @Override
    public void disconnect() {
        System.out.println("MySQL 연결 종료");
    }
}

class PostgreSQLConnection implements DatabaseConnection {
    private String connectionString;
    
    public PostgreSQLConnection(String connectionString) {
        this.connectionString = connectionString;
    }
    
    @Override
    public void connect() {
        System.out.println("PostgreSQL 연결: " + connectionString);
    }
    
    @Override
    public void executeQuery(String sql) {
        System.out.println("PostgreSQL 쿼리 실행: " + sql);
    }
    
    @Override
    public void disconnect() {
        System.out.println("PostgreSQL 연결 종료");
    }
}

// 팩토리
class DatabaseConnectionFactory {
    public static DatabaseConnection createConnection(
            String dbType, String host, int port, String database) {
        String connectionString = String.format("%s:%d/%s", host, port, database);
        
        return switch (dbType.toUpperCase()) {
            case "MYSQL" -> new MySQLConnection(connectionString);
            case "POSTGRESQL" -> new PostgreSQLConnection(connectionString);
            default -> throw new IllegalArgumentException("지원하지 않는 DB: " + dbType);
        };
    }
}

// 사용
DatabaseConnection conn = DatabaseConnectionFactory.createConnection(
    "MYSQL", "localhost", 3306, "mydb"
);
conn.connect();
conn.executeQuery("SELECT * FROM users");
conn.disconnect();
```

### 실전 예시: 결제 처리기

```java
interface PaymentProcessor {
    void processPayment(double amount);
    void refund(double amount);
}

class CreditCardProcessor implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        System.out.println("신용카드 결제: " + amount);
    }
    
    @Override
    public void refund(double amount) {
        System.out.println("신용카드 환불: " + amount);
    }
}

class PayPalProcessor implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        System.out.println("PayPal 결제: " + amount);
    }
    
    @Override
    public void refund(double amount) {
        System.out.println("PayPal 환불: " + amount);
    }
}

class BitcoinProcessor implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        System.out.println("Bitcoin 결제: " + amount);
    }
    
    @Override
    public void refund(double amount) {
        System.out.println("Bitcoin 환불: " + amount);
    }
}

class PaymentProcessorFactory {
    public static PaymentProcessor create(String paymentMethod) {
        return switch (paymentMethod.toUpperCase()) {
            case "CREDIT_CARD" -> new CreditCardProcessor();
            case "PAYPAL" -> new PayPalProcessor();
            case "BITCOIN" -> new BitcoinProcessor();
            default -> throw new IllegalArgumentException("지원하지 않는 결제수단");
        };
    }
}
```

## 주의사항 / 함정

### 1. Simple Factory의 OCP 위반

```java
// ❌ 새로운 타입 추가 시 팩토리 수정 필요
class ShapeFactory {
    public Shape createShape(String type) {
        switch (type) {
            case "CIRCLE": return new Circle();
            case "RECTANGLE": return new Rectangle();
            // 새 타입 추가 시 여기 수정!
        }
    }
}

// ✅ Factory Method로 해결
abstract class ShapeFactory {
    abstract Shape createShape();
}

class CircleFactory extends ShapeFactory {
    Shape createShape() { return new Circle(); }
}
```

### 2. 과도한 팩토리 사용

```java
// ❌ 단순한 객체 생성에 팩토리 사용
String text = StringFactory.create("Hello");

// ✅ 직접 생성이 더 간단
String text = "Hello";
```

## 관련 개념
- [[SOLID원칙]]
- [[디자인패턴-Singleton]]
- [[디자인패턴-Builder]]

## 면접 질문
1. Factory Method와 Abstract Factory의 차이는?
2. Simple Factory의 단점과 해결방법은?

## 참고 자료
- Design Patterns - Gang of Four
- Head First Design Patterns