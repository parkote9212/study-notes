---
tags:
  - study
  - java
  - enum
  - enumeration
created: 2025-02-02
---

# Java 열거형 Enum

## 한 줄 요약
> 관련된 상수들을 타입 안전하게 그룹화하는 특수한 클래스

## 상세 설명

### Enum의 기본 개념

Enum(열거형)은 서로 관련된 상수들의 집합을 정의하는 특수한 클래스입니다. Java 5부터 도입되었으며, 타입 안전성을 제공하고 가독성을 높입니다.

**Enum의 특징**
- 암묵적으로 `java.lang.Enum`을 상속 (다른 클래스 상속 불가)
- 암묵적으로 final 클래스 (상속 불가)
- 인터페이스 구현 가능
- 필드, 메서드, 생성자 가지기 가능
- 싱글톤 패턴 자동 보장

### Enum을 사용하는 이유

**Enum 이전 방식의 문제점**
```java
// ❌ 문자열 상수 - 타입 안전성 없음
public static final String MONDAY = "MONDAY";
public static final String TUESDAY = "TUESDAY";

// ❌ 정수 상수 - 의미 불명확
public static final int SPRING = 0;
public static final int SUMMER = 1;
```

**Enum의 장점**
1. 타입 안전성 보장
2. 코드 가독성 향상
3. IDE 자동완성 지원
4. 리팩토링 안전성
5. 추가 기능 구현 가능

## 코드 예시

### 기본 Enum 선언

```java
enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}

// 사용
Day today = Day.MONDAY;
System.out.println(today);  // MONDAY

// switch문에서 사용
switch (today) {
    case MONDAY:
        System.out.println("월요일입니다");
        break;
    case FRIDAY:
        System.out.println("금요일입니다");
        break;
    default:
        System.out.println("주중입니다");
}
```

### Enum 기본 메서드

```java
enum Season {
    SPRING, SUMMER, FALL, WINTER
}

// 1. name() - 상수 이름 반환
System.out.println(Season.SPRING.name());  // "SPRING"

// 2. ordinal() - 선언 순서 (0부터 시작)
System.out.println(Season.SPRING.ordinal());  // 0
System.out.println(Season.SUMMER.ordinal());  // 1

// 3. valueOf() - 문자열로 Enum 상수 찾기
Season season = Season.valueOf("SPRING");

// 4. values() - 모든 상수를 배열로 반환
Season[] seasons = Season.values();
for (Season s : seasons) {
    System.out.println(s.name());
}
```

### 필드와 생성자가 있는 Enum

```java
enum HttpStatus {
    OK(200, "성공"),
    BAD_REQUEST(400, "잘못된 요청"),
    NOT_FOUND(404, "찾을 수 없음"),
    SERVER_ERROR(500, "서버 오류");
    
    private final int code;
    private final String message;
    
    // Enum 생성자는 private (생략 가능)
    HttpStatus(int code, String message) {
        this.code = code;
        this.message = message;
    }
    
    public int getCode() {
        return code;
    }
    
    public String getMessage() {
        return message;
    }
}

// 사용
HttpStatus status = HttpStatus.OK;
System.out.println(status.getCode());     // 200
System.out.println(status.getMessage());  // 성공
```

### Enum에 메서드 추가

```java
enum Operation {
    PLUS("+") {
        @Override
        public double apply(double x, double y) {
            return x + y;
        }
    },
    MINUS("-") {
        @Override
        public double apply(double x, double y) {
            return x - y;
        }
    },
    MULTIPLY("*") {
        @Override
        public double apply(double x, double y) {
            return x * y;
        }
    },
    DIVIDE("/") {
        @Override
        public double apply(double x, double y) {
            return x / y;
        }
    };
    
    private final String symbol;
    
    Operation(String symbol) {
        this.symbol = symbol;
    }
    
    public abstract double apply(double x, double y);
    
    public String getSymbol() {
        return symbol;
    }
}

// 사용
double result1 = Operation.PLUS.apply(10, 5);   // 15.0
double result2 = Operation.MULTIPLY.apply(10, 5);  // 50.0
```

### Enum 비교

```java
enum Color {
    RED, GREEN, BLUE
}

Color color1 = Color.RED;
Color color2 = Color.RED;
Color color3 = Color.BLUE;

// == 연산자 사용 (권장)
System.out.println(color1 == color2);  // true
System.out.println(color1 == color3);  // false

// equals() 사용 가능 (하지만 == 권장)
System.out.println(color1.equals(color2));  // true
```

### 역방향 조회 (코드로 Enum 찾기)

```java
enum Status {
    ACTIVE("A", "활성"),
    INACTIVE("I", "비활성"),
    PENDING("P", "대기중");
    
    private final String code;
    private final String description;
    
    Status(String code, String description) {
        this.code = code;
        this.description = description;
    }
    
    public String getCode() {
        return code;
    }
    
    // 코드로 Enum 찾기
    public static Status fromCode(String code) {
        for (Status status : values()) {
            if (status.code.equals(code)) {
                return status;
            }
        }
        throw new IllegalArgumentException("Invalid code: " + code);
    }
}

// 사용
Status status = Status.fromCode("A");
System.out.println(status);  // ACTIVE
```

### Map을 이용한 빠른 역방향 조회

```java
enum ErrorCode {
    INVALID_INPUT(1001, "입력값 오류"),
    DUPLICATE_DATA(1002, "중복 데이터"),
    NOT_FOUND(1003, "데이터 없음");
    
    private final int code;
    private final String message;
    
    // static Map으로 캐싱
    private static final Map<Integer, ErrorCode> CODE_MAP = 
        Stream.of(values())
              .collect(Collectors.toMap(ErrorCode::getCode, e -> e));
    
    ErrorCode(int code, String message) {
        this.code = code;
        this.message = message;
    }
    
    public int getCode() {
        return code;
    }
    
    public String getMessage() {
        return message;
    }
    
    // O(1) 조회
    public static ErrorCode fromCode(int code) {
        ErrorCode errorCode = CODE_MAP.get(code);
        if (errorCode == null) {
            throw new IllegalArgumentException("Invalid code: " + code);
        }
        return errorCode;
    }
}
```

### EnumSet 활용

```java
import java.util.EnumSet;

enum Permission {
    READ, WRITE, DELETE, EXECUTE
}

// EnumSet - 비트 필드보다 안전하고 효율적
EnumSet<Permission> userPermissions = EnumSet.of(Permission.READ, Permission.WRITE);

// 권한 확인
if (userPermissions.contains(Permission.WRITE)) {
    System.out.println("쓰기 권한 있음");
}

// 모든 권한
EnumSet<Permission> allPermissions = EnumSet.allOf(Permission.class);

// 빈 EnumSet
EnumSet<Permission> noPermissions = EnumSet.noneOf(Permission.class);

// 범위 지정
EnumSet<Permission> readAndWrite = EnumSet.range(Permission.READ, Permission.WRITE);
```

### EnumMap 활용

```java
import java.util.EnumMap;

enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}

// EnumMap - HashMap보다 빠르고 메모리 효율적
EnumMap<Day, String> schedule = new EnumMap<>(Day.class);

schedule.put(Day.MONDAY, "회의");
schedule.put(Day.WEDNESDAY, "발표");
schedule.put(Day.FRIDAY, "회식");

// 조회
String mondaySchedule = schedule.get(Day.MONDAY);
System.out.println("월요일: " + mondaySchedule);  // 월요일: 회의
```

### 실무 예시: 주문 상태 관리

```java
enum OrderStatus {
    ORDERED("주문완료") {
        @Override
        public boolean canCancel() {
            return true;
        }
    },
    PAYMENT_COMPLETED("결제완료") {
        @Override
        public boolean canCancel() {
            return true;
        }
    },
    PREPARING("상품준비중") {
        @Override
        public boolean canCancel() {
            return true;
        }
    },
    SHIPPED("배송중") {
        @Override
        public boolean canCancel() {
            return false;
        }
    },
    DELIVERED("배송완료") {
        @Override
        public boolean canCancel() {
            return false;
        }
    },
    CANCELLED("취소됨") {
        @Override
        public boolean canCancel() {
            return false;
        }
    };
    
    private final String description;
    
    OrderStatus(String description) {
        this.description = description;
    }
    
    public String getDescription() {
        return description;
    }
    
    public abstract boolean canCancel();
    
    // 다음 상태로 전이 가능 여부
    public boolean canTransitionTo(OrderStatus next) {
        if (this == ORDERED && next == PAYMENT_COMPLETED) return true;
        if (this == PAYMENT_COMPLETED && next == PREPARING) return true;
        if (this == PREPARING && next == SHIPPED) return true;
        if (this == SHIPPED && next == DELIVERED) return true;
        return false;
    }
}

// 사용
OrderStatus status = OrderStatus.ORDERED;
if (status.canCancel()) {
    System.out.println("주문 취소 가능");
}
```

### 실무 예시: 결제 수단

```java
enum PaymentMethod {
    CREDIT_CARD("신용카드", 0.03),
    BANK_TRANSFER("계좌이체", 0.01),
    MOBILE("휴대폰결제", 0.05),
    POINT("포인트", 0.0);
    
    private final String displayName;
    private final double feeRate;
    
    PaymentMethod(String displayName, double feeRate) {
        this.displayName = displayName;
        this.feeRate = feeRate;
    }
    
    public String getDisplayName() {
        return displayName;
    }
    
    public int calculateFee(int amount) {
        return (int) (amount * feeRate);
    }
    
    public int calculateTotalAmount(int amount) {
        return amount + calculateFee(amount);
    }
}

// 사용
PaymentMethod method = PaymentMethod.CREDIT_CARD;
int amount = 10000;
int fee = method.calculateFee(amount);
int total = method.calculateTotalAmount(amount);

System.out.println("결제수단: " + method.getDisplayName());  // 신용카드
System.out.println("수수료: " + fee);      // 300
System.out.println("총액: " + total);      // 10300
```

### 인터페이스 구현

```java
interface Describable {
    String getDescription();
}

enum Priority implements Describable {
    HIGH("높음", 1),
    MEDIUM("보통", 2),
    LOW("낮음", 3);
    
    private final String displayName;
    private final int level;
    
    Priority(String displayName, int level) {
        this.displayName = displayName;
        this.level = level;
    }
    
    @Override
    public String getDescription() {
        return displayName + " (레벨: " + level + ")";
    }
    
    public int getLevel() {
        return level;
    }
}
```

### JSON 변환 활용

```java
enum UserRole {
    ADMIN("ADMIN", "관리자"),
    USER("USER", "일반사용자"),
    GUEST("GUEST", "게스트");
    
    private final String code;
    private final String displayName;
    
    UserRole(String code, String displayName) {
        this.code = code;
        this.displayName = displayName;
    }
    
    public String getCode() {
        return code;
    }
    
    // Jackson 등 JSON 라이브러리에서 사용
    @JsonValue
    public String toJson() {
        return code;
    }
    
    // JSON에서 Enum으로 변환
    @JsonCreator
    public static UserRole fromJson(String code) {
        for (UserRole role : values()) {
            if (role.code.equals(code)) {
                return role;
            }
        }
        throw new IllegalArgumentException("Unknown role: " + code);
    }
}
```

## 주의사항 / 함정

### 1. ordinal() 사용 지양

```java
enum Priority {
    LOW, MEDIUM, HIGH
}

// ❌ ordinal() 의존 - 순서 변경 시 문제
int level = Priority.HIGH.ordinal();  // 2
if (level == 2) {
    System.out.println("높은 우선순위");
}

// ✅ 명시적 필드 사용
enum Priority {
    LOW(1), MEDIUM(2), HIGH(3);
    
    private final int level;
    
    Priority(int level) {
        this.level = level;
    }
    
    public int getLevel() {
        return level;
    }
}
```

### 2. valueOf() 예외 처리

```java
// ❌ 예외 처리 없음
String input = "INVALID";
Season season = Season.valueOf(input);  // IllegalArgumentException

// ✅ 안전한 처리
public static Season safeValueOf(String name) {
    try {
        return Season.valueOf(name);
    } catch (IllegalArgumentException e) {
        return null;  // 또는 기본값 반환
    }
}

// ✅ Optional 사용
public static Optional<Season> findByName(String name) {
    try {
        return Optional.of(Season.valueOf(name));
    } catch (IllegalArgumentException e) {
        return Optional.empty();
    }
}
```

### 3. Enum과 싱글톤

```java
// ✅ Enum을 이용한 싱글톤 (가장 안전한 방법)
enum Singleton {
    INSTANCE;
    
    private int value;
    
    public void setValue(int value) {
        this.value = value;
    }
    
    public int getValue() {
        return value;
    }
}

// 사용
Singleton.INSTANCE.setValue(100);
System.out.println(Singleton.INSTANCE.getValue());  // 100
```

### 4. Enum 직렬화 주의

```java
// Enum은 자동으로 직렬화 가능
// 하지만 역직렬화 시 주의 필요

enum Status {
    ACTIVE, INACTIVE
}

// ❌ 나중에 ACTIVE를 삭제하면 역직렬화 실패
// ✅ deprecated 처리하고 유지하거나, 버전 관리 필요
```

### 5. 생성자 호출 제한

```java
enum Color {
    RED, GREEN, BLUE;
    
    // ❌ public 생성자 불가
    // public Color() { }  // 컴파일 에러
    
    // ✅ private만 가능 (생략 시 자동 private)
    private Color() {
        System.out.println("Color 생성");
    }
}
```

### 6. 과도한 로직 포함

```java
// ❌ Enum에 너무 많은 비즈니스 로직
enum OrderProcessor {
    PAYMENT {
        @Override
        public void process(Order order) {
            // 100줄의 결제 처리 로직
        }
    },
    DELIVERY {
        @Override
        public void process(Order order) {
            // 100줄의 배송 처리 로직
        }
    };
    
    public abstract void process(Order order);
}

// ✅ 전략 패턴 등으로 분리
enum OrderType {
    PAYMENT, DELIVERY;
    
    public OrderProcessor getProcessor() {
        switch (this) {
            case PAYMENT: return new PaymentProcessor();
            case DELIVERY: return new DeliveryProcessor();
            default: throw new IllegalStateException();
        }
    }
}
```

## 관련 개념
- [[Java-static]]
- [[Java-final]]
- [[Java-Sealed-Classes]]

## 면접 질문
1. Enum을 사용하는 이유와 장점은 무엇인가요?
2. ordinal() 메서드 사용을 지양해야 하는 이유는?

## 참고 자료
- Effective Java 3/E - Item 34~38 (Enum 관련)
- Java Enum Documentation
- EnumSet, EnumMap Documentation