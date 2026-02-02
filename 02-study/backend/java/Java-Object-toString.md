---
tags:
  - study
  - java
  - object
  - toString
created: 2025-02-02
---

# Java Object toString

## 한 줄 요약
> 객체를 문자열로 표현하여 디버깅과 로깅에 활용하는 메서드

## 상세 설명

### toString() 기본 개념

`toString()`은 객체의 문자열 표현을 반환하는 메서드입니다. Object 클래스의 기본 구현은 "클래스명@해시코드" 형태로 반환하지만, 대부분의 경우 의미 있는 정보를 제공하도록 오버라이딩합니다.

**기본 구현**
```java
public String toString() {
    return getClass().getName() + "@" + Integer.toHexString(hashCode());
}
// 예: "Person@15db9742"
```

### toString() 오버라이딩의 필요성

1. **디버깅 편의성**: 객체 상태를 쉽게 확인
2. **로그 가독성**: 로그에 의미 있는 정보 출력
3. **자동 호출**: `System.out.println()`, 문자열 연결 시 자동 호출
4. **개발 생산성**: IDE 디버거에서 객체 내용 바로 확인

### 주요 사용 시나리오

1. **로깅 및 디버깅**
```java
logger.info("사용자 정보: {}", user);  // toString() 자동 호출
```

2. **문자열 연결**
```java
String message = "현재 상태: " + order;  // toString() 자동 호출
```

3. **컬렉션 출력**
```java
List<Product> products = getProducts();
System.out.println(products);  // 각 요소의 toString() 호출
```

## 코드 예시

### 기본 toString() 오버라이딩

```java
class Person {
    private String name;
    private int age;
    private String email;
    
    public Person(String name, int age, String email) {
        this.name = name;
        this.age = age;
        this.email = email;
    }
    
    @Override
    public String toString() {
        return "Person{" +
                "name='" + name + '\'' +
                ", age=" + age +
                ", email='" + email + '\'' +
                '}';
    }
}

// 사용
Person person = new Person("홍길동", 30, "hong@example.com");
System.out.println(person);
// 출력: Person{name='홍길동', age=30, email='hong@example.com'}
```

### StringBuilder를 사용한 성능 최적화

```java
class Order {
    private String orderId;
    private List<String> items;
    private double totalPrice;
    
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("Order{");
        sb.append("orderId='").append(orderId).append('\'');
        sb.append(", items=").append(items);
        sb.append(", totalPrice=").append(totalPrice);
        sb.append('}');
        return sb.toString();
    }
}
```

### IDE 자동 생성 활용

```java
class Product {
    private Long id;
    private String name;
    private int price;
    private String category;
    
    // IntelliJ: Alt + Insert → toString()
    // Eclipse: Source → Generate toString()
    
    @Override
    public String toString() {
        return "Product{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", price=" + price +
                ", category='" + category + '\'' +
                '}';
    }
}
```

### 상속 관계에서의 toString()

```java
class Animal {
    private String species;
    
    @Override
    public String toString() {
        return "Animal{species='" + species + "'}";
    }
}

class Dog extends Animal {
    private String breed;
    private int age;
    
    @Override
    public String toString() {
        return "Dog{" +
                "breed='" + breed + '\'' +
                ", age=" + age +
                ", parent=" + super.toString() +
                '}';
    }
}

// 출력 예시
Dog dog = new Dog("진돗개", 3);
System.out.println(dog);
// Dog{breed='진돗개', age=3, parent=Animal{species='개'}}
```

### 민감 정보 숨기기

```java
class User {
    private String username;
    private String password;
    private String email;
    
    @Override
    public String toString() {
        return "User{" +
                "username='" + username + '\'' +
                ", password='****'" +  // 비밀번호 숨김
                ", email='" + email + '\'' +
                '}';
    }
}
```

### 컬렉션 필드 포함

```java
class Team {
    private String name;
    private List<String> members;
    
    @Override
    public String toString() {
        return "Team{" +
                "name='" + name + '\'' +
                ", members=" + members +  // List의 toString() 호출
                '}';
    }
}

// 사용
Team team = new Team("개발팀", Arrays.asList("김철수", "이영희", "박민수"));
System.out.println(team);
// Team{name='개발팀', members=[김철수, 이영희, 박민수]}
```

### 조건부 필드 표시

```java
class OrderDetail {
    private String orderId;
    private String status;
    private String cancelReason;  // 취소 시에만 값 존재
    
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("OrderDetail{");
        sb.append("orderId='").append(orderId).append('\'');
        sb.append(", status='").append(status).append('\'');
        
        if (cancelReason != null) {
            sb.append(", cancelReason='").append(cancelReason).append('\'');
        }
        
        sb.append('}');
        return sb.toString();
    }
}
```

### 포맷팅된 출력

```java
class Transaction {
    private LocalDateTime timestamp;
    private String type;
    private double amount;
    
    @Override
    public String toString() {
        return String.format(
            "Transaction{timestamp=%s, type='%s', amount=%.2f}",
            timestamp.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME),
            type,
            amount
        );
    }
}

// 출력: Transaction{timestamp=2025-02-02T14:30:00, type='입금', amount=50000.00}
```

### JSON 형태 toString()

```java
class ApiResponse {
    private int statusCode;
    private String message;
    private Object data;
    
    @Override
    public String toString() {
        return "{\n" +
                "  \"statusCode\": " + statusCode + ",\n" +
                "  \"message\": \"" + message + "\",\n" +
                "  \"data\": " + data + "\n" +
                "}";
    }
}
```

## 주의사항 / 함정

### 1. 순환 참조 문제

```java
class Parent {
    private String name;
    private Child child;
    
    @Override
    public String toString() {
        return "Parent{name='" + name + "', child=" + child + "}";
    }
}

class Child {
    private String name;
    private Parent parent;
    
    @Override
    public String toString() {
        return "Child{name='" + name + "', parent=" + parent + "}";
    }
}

// ❌ StackOverflowError 발생!
Parent parent = new Parent("아빠");
Child child = new Child("아들");
parent.setChild(child);
child.setParent(parent);
System.out.println(parent);  // 무한 재귀 호출
```

**해결책**
```java
class Child {
    private String name;
    private Parent parent;
    
    @Override
    public String toString() {
        return "Child{name='" + name + 
               "', parent=" + (parent != null ? parent.getName() : null) + "}";
    }
}
```

### 2. 성능 문제

```java
// ❌ 반복문에서 문자열 연결 (비효율적)
@Override
public String toString() {
    String result = "Items{";
    for (String item : items) {
        result += item + ", ";  // 매번 새로운 String 객체 생성
    }
    result += "}";
    return result;
}

// ✅ StringBuilder 사용
@Override
public String toString() {
    StringBuilder sb = new StringBuilder("Items{");
    for (String item : items) {
        sb.append(item).append(", ");
    }
    sb.append("}");
    return sb.toString();
}
```

### 3. null 체크 누락

```java
// ❌ NullPointerException 위험
@Override
public String toString() {
    return "Person{name='" + name.toUpperCase() + "'}";
}

// ✅ null 안전 처리
@Override
public String toString() {
    return "Person{name='" + (name != null ? name : "N/A") + "'}";
}
```

### 4. 민감 정보 노출

```java
// ❌ 보안 위험
class Account {
    private String accountNumber;
    private String password;
    
    @Override
    public String toString() {
        return "Account{accountNumber='" + accountNumber + 
               "', password='" + password + "'}";  // 패스워드 노출!
    }
}

// ✅ 민감 정보 마스킹
@Override
public String toString() {
    return "Account{accountNumber='" + accountNumber + 
           "', password='****'}";
}
```

### 5. 과도한 정보 포함

```java
// ❌ 너무 많은 정보 (가독성 저하)
@Override
public String toString() {
    return "User{id=" + id + 
           ", username='" + username + '\'' +
           ", password='****'" +
           ", email='" + email + '\'' +
           ", firstName='" + firstName + '\'' +
           ", lastName='" + lastName + '\'' +
           ", phoneNumber='" + phoneNumber + '\'' +
           ", address='" + address + '\'' +
           ", city='" + city + '\'' +
           ", country='" + country + '\'' +
           ", zipCode='" + zipCode + '\'' +
           // ... 20개 이상의 필드
           '}';
}

// ✅ 핵심 정보만 포함
@Override
public String toString() {
    return "User{id=" + id + ", username='" + username + "'}";
}
```

### 6. equals()와의 혼동

```java
// toString()은 동등성 비교에 사용하면 안됨
Person p1 = new Person("홍길동", 30);
Person p2 = new Person("홍길동", 30);

// ❌ 잘못된 비교
if (p1.toString().equals(p2.toString())) {  // 우연히 같을 수 있지만 부적절
    // ...
}

// ✅ 올바른 비교
if (p1.equals(p2)) {  // equals() 사용
    // ...
}
```

## 관련 개념
- [[Java-Object-equals와hashCode]]
- [[Java-문자열처리심화]]
- [[Java-StringBuilder와StringBuffer]]
- [[Java-로깅]]

## 면접 질문
1. toString() 메서드를 오버라이딩하는 이유는 무엇인가요?
2. toString()에서 순환 참조가 발생할 수 있는 상황과 해결 방법은?

## 참고 자료
- Effective Java 3/E - Item 12 (toString)
- Java API Documentation - Object.toString()