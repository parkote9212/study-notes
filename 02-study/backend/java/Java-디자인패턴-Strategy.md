---
tags:
  - study
  - java
  - design-pattern
  - strategy
  - behavioral-pattern
created: 2025-02-03
---

# Strategy 패턴

## 한 줄 요약
> 알고리즘을 캡슐화하여 런타임에 동적으로 교체 가능하게 만드는 행위 패턴

## 상세 설명

### Strategy 패턴이란?

**목적**: 알고리즘군을 정의하고 캡슐화하여 서로 교환 가능하게 만듦

**구성 요소**
- **Strategy**: 알고리즘 인터페이스
- **ConcreteStrategy**: 구체적인 알고리즘 구현
- **Context**: 전략을 사용하는 클래스

## 코드 예시

### 1. 기본 Strategy 패턴

```java
// ❌ if-else로 알고리즘 선택
class PaymentService {
    public void processPayment(String type, double amount) {
        if (type.equals("CREDIT_CARD")) {
            System.out.println("신용카드 결제: " + amount);
        } else if (type.equals("PAYPAL")) {
            System.out.println("PayPal 결제: " + amount);
        } else if (type.equals("BITCOIN")) {
            System.out.println("Bitcoin 결제: " + amount);
        }
        // 새로운 결제수단 추가 시 이 메서드 수정 필요!
    }
}
```

```java
// ✅ Strategy 패턴 적용
// 전략 인터페이스
interface PaymentStrategy {
    void pay(double amount);
}

// 구체적인 전략들
class CreditCardStrategy implements PaymentStrategy {
    private String cardNumber;
    
    public CreditCardStrategy(String cardNumber) {
        this.cardNumber = cardNumber;
    }
    
    @Override
    public void pay(double amount) {
        System.out.println("신용카드(" + cardNumber + ")로 " + amount + "원 결제");
    }
}

class PayPalStrategy implements PaymentStrategy {
    private String email;
    
    public PayPalStrategy(String email) {
        this.email = email;
    }
    
    @Override
    public void pay(double amount) {
        System.out.println("PayPal(" + email + ")로 " + amount + "원 결제");
    }
}

class BitcoinStrategy implements PaymentStrategy {
    private String walletAddress;
    
    public BitcoinStrategy(String walletAddress) {
        this.walletAddress = walletAddress;
    }
    
    @Override
    public void pay(double amount) {
        System.out.println("Bitcoin(" + walletAddress + ")로 " + amount + "원 결제");
    }
}

// Context
class PaymentService {
    private PaymentStrategy strategy;
    
    public void setStrategy(PaymentStrategy strategy) {
        this.strategy = strategy;
    }
    
    public void processPayment(double amount) {
        strategy.pay(amount);
    }
}

// 사용
PaymentService service = new PaymentService();

service.setStrategy(new CreditCardStrategy("1234-5678-9012-3456"));
service.processPayment(10000);

service.setStrategy(new PayPalStrategy("user@example.com"));
service.processPayment(20000);

service.setStrategy(new BitcoinStrategy("1A2B3C4D5E6F"));
service.processPayment(30000);
```

### 2. 실전 예시: 정렬 전략

```java
// 전략 인터페이스
interface SortStrategy<T> {
    void sort(List<T> list);
}

// 구체적인 전략들
class BubbleSortStrategy<T extends Comparable<T>> implements SortStrategy<T> {
    @Override
    public void sort(List<T> list) {
        System.out.println("버블 정렬 실행");
        // 버블 정렬 알고리즘
        for (int i = 0; i < list.size(); i++) {
            for (int j = 0; j < list.size() - 1 - i; j++) {
                if (list.get(j).compareTo(list.get(j + 1)) > 0) {
                    T temp = list.get(j);
                    list.set(j, list.get(j + 1));
                    list.set(j + 1, temp);
                }
            }
        }
    }
}

class QuickSortStrategy<T extends Comparable<T>> implements SortStrategy<T> {
    @Override
    public void sort(List<T> list) {
        System.out.println("퀵 정렬 실행");
        quickSort(list, 0, list.size() - 1);
    }
    
    private void quickSort(List<T> list, int low, int high) {
        if (low < high) {
            int pi = partition(list, low, high);
            quickSort(list, low, pi - 1);
            quickSort(list, pi + 1, high);
        }
    }
    
    private int partition(List<T> list, int low, int high) {
        T pivot = list.get(high);
        int i = low - 1;
        
        for (int j = low; j < high; j++) {
            if (list.get(j).compareTo(pivot) <= 0) {
                i++;
                T temp = list.get(i);
                list.set(i, list.get(j));
                list.set(j, temp);
            }
        }
        
        T temp = list.get(i + 1);
        list.set(i + 1, list.get(high));
        list.set(high, temp);
        
        return i + 1;
    }
}

// Context
class Sorter<T extends Comparable<T>> {
    private SortStrategy<T> strategy;
    
    public void setStrategy(SortStrategy<T> strategy) {
        this.strategy = strategy;
    }
    
    public void sort(List<T> list) {
        strategy.sort(list);
    }
}

// 사용
List<Integer> numbers = Arrays.asList(5, 2, 8, 1, 9, 3);
Sorter<Integer> sorter = new Sorter<>();

sorter.setStrategy(new BubbleSortStrategy<>());
sorter.sort(numbers);
System.out.println(numbers);

sorter.setStrategy(new QuickSortStrategy<>());
sorter.sort(numbers);
System.out.println(numbers);
```

### 3. 실전 예시: 할인 전략

```java
interface DiscountStrategy {
    double calculateDiscount(double price);
}

class NoDiscountStrategy implements DiscountStrategy {
    @Override
    public double calculateDiscount(double price) {
        return price;
    }
}

class PercentageDiscountStrategy implements DiscountStrategy {
    private final double percentage;
    
    public PercentageDiscountStrategy(double percentage) {
        this.percentage = percentage;
    }
    
    @Override
    public double calculateDiscount(double price) {
        return price * (1 - percentage / 100);
    }
}

class FixedAmountDiscountStrategy implements DiscountStrategy {
    private final double amount;
    
    public FixedAmountDiscountStrategy(double amount) {
        this.amount = amount;
    }
    
    @Override
    public double calculateDiscount(double price) {
        return Math.max(0, price - amount);
    }
}

class BuyTwoGetOneDiscountStrategy implements DiscountStrategy {
    @Override
    public double calculateDiscount(double price) {
        // 2개 구매 시 1개 무료
        return price * 2 / 3;
    }
}

// Context
class ShoppingCart {
    private List<Double> prices = new ArrayList<>();
    private DiscountStrategy discountStrategy;
    
    public void addItem(double price) {
        prices.add(price);
    }
    
    public void setDiscountStrategy(DiscountStrategy strategy) {
        this.discountStrategy = strategy;
    }
    
    public double calculateTotal() {
        double total = prices.stream().mapToDouble(Double::doubleValue).sum();
        
        if (discountStrategy != null) {
            total = discountStrategy.calculateDiscount(total);
        }
        
        return total;
    }
}

// 사용
ShoppingCart cart = new ShoppingCart();
cart.addItem(10000);
cart.addItem(20000);
cart.addItem(15000);

System.out.println("할인 없음: " + cart.calculateTotal());  // 45000

cart.setDiscountStrategy(new PercentageDiscountStrategy(20));
System.out.println("20% 할인: " + cart.calculateTotal());  // 36000

cart.setDiscountStrategy(new FixedAmountDiscountStrategy(10000));
System.out.println("10000원 할인: " + cart.calculateTotal());  // 35000
```

### 4. 실전 예시: 압축 전략

```java
interface CompressionStrategy {
    byte[] compress(byte[] data);
    byte[] decompress(byte[] data);
}

class ZipCompressionStrategy implements CompressionStrategy {
    @Override
    public byte[] compress(byte[] data) {
        System.out.println("ZIP 압축 실행");
        // ZIP 압축 로직
        return data;  // 실제로는 압축된 데이터 반환
    }
    
    @Override
    public byte[] decompress(byte[] data) {
        System.out.println("ZIP 압축 해제");
        return data;
    }
}

class GzipCompressionStrategy implements CompressionStrategy {
    @Override
    public byte[] compress(byte[] data) {
        System.out.println("GZIP 압축 실행");
        return data;
    }
    
    @Override
    public byte[] decompress(byte[] data) {
        System.out.println("GZIP 압축 해제");
        return data;
    }
}

class Compressor {
    private CompressionStrategy strategy;
    
    public void setStrategy(CompressionStrategy strategy) {
        this.strategy = strategy;
    }
    
    public byte[] compress(byte[] data) {
        return strategy.compress(data);
    }
    
    public byte[] decompress(byte[] data) {
        return strategy.decompress(data);
    }
}
```

### 5. 람다를 이용한 Strategy

```java
// 함수형 인터페이스
@FunctionalInterface
interface ValidationStrategy {
    boolean isValid(String value);
}

class Validator {
    private ValidationStrategy strategy;
    
    public void setStrategy(ValidationStrategy strategy) {
        this.strategy = strategy;
    }
    
    public boolean validate(String value) {
        return strategy.isValid(value);
    }
}

// 사용 - 람다로 간결하게
Validator validator = new Validator();

// 이메일 검증
validator.setStrategy(value -> value.contains("@"));
System.out.println(validator.validate("user@example.com"));  // true

// 숫자만 검증
validator.setStrategy(value -> value.matches("\\d+"));
System.out.println(validator.validate("12345"));  // true

// 최소 길이 검증
validator.setStrategy(value -> value.length() >= 5);
System.out.println(validator.validate("abc"));  // false
```

### 6. 실전 예시: 알림 전송 전략

```java
interface NotificationStrategy {
    void send(String message, String recipient);
}

class EmailNotificationStrategy implements NotificationStrategy {
    @Override
    public void send(String message, String recipient) {
        System.out.println("이메일 발송");
        System.out.println("수신: " + recipient);
        System.out.println("내용: " + message);
    }
}

class SMSNotificationStrategy implements NotificationStrategy {
    @Override
    public void send(String message, String recipient) {
        System.out.println("SMS 발송");
        System.out.println("수신: " + recipient);
        System.out.println("내용: " + message);
    }
}

class PushNotificationStrategy implements NotificationStrategy {
    @Override
    public void send(String message, String recipient) {
        System.out.println("푸시 알림");
        System.out.println("수신: " + recipient);
        System.out.println("내용: " + message);
    }
}

// Context
class NotificationService {
    private NotificationStrategy strategy;
    
    public NotificationService(NotificationStrategy strategy) {
        this.strategy = strategy;
    }
    
    public void setStrategy(NotificationStrategy strategy) {
        this.strategy = strategy;
    }
    
    public void notify(String message, String recipient) {
        strategy.send(message, recipient);
    }
}

// 사용
NotificationService service = new NotificationService(
    new EmailNotificationStrategy()
);

service.notify("환영합니다!", "user@example.com");

// 런타임에 전략 변경
service.setStrategy(new SMSNotificationStrategy());
service.notify("인증번호: 123456", "010-1234-5678");
```

## 주의사항 / 함정

### 1. 전략이 너무 많아질 때

```java
// ❌ 전략 클래스가 너무 많음
class Strategy1 implements Strategy {}
class Strategy2 implements Strategy {}
class Strategy3 implements Strategy {}
// ... 100개의 전략

// ✅ 람다나 설정으로 해결
Map<String, ValidationStrategy> strategies = Map.of(
    "email", value -> value.contains("@"),
    "number", value -> value.matches("\\d+"),
    "minLength5", value -> value.length() >= 5
);
```

### 2. Context와 Strategy의 결합

```java
// ❌ Strategy가 Context에 의존
class BadStrategy implements PaymentStrategy {
    public void pay(PaymentService service, double amount) {
        // service에 직접 접근 - 결합도 증가
    }
}

// ✅ 인터페이스를 통한 소통
class GoodStrategy implements PaymentStrategy {
    public void pay(double amount) {
        // Context와 독립적
    }
}
```

## 관련 개념
- [[Java-SOLID원칙]]
- [[Java-디자인패턴-Factory]]
- [[Java-함수형인터페이스]]

## 면접 질문
1. Strategy 패턴과 if-else의 차이점은?
2. Strategy 패턴의 장단점은 무엇인가요?

## 참고 자료
- Design Patterns - Gang of Four
- Head First Design Patterns