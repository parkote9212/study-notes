---
tags:
  - interview
  - java
  - oop
created: 2026-01-31
difficulty: 하
---

# Java 클래스와 객체지향 기초 면접

## 질문 1: 클래스와 객체의 차이는?

### 핵심 답변 (3줄)
1. 클래스는 객체를 만들기 위한 설계도이고, 객체는 그 설계도로 만든 실체입니다.
2. 클래스는 필드와 메서드를 정의하고, 객체는 메모리에 실제로 할당되어 동작합니다.
3. 하나의 클래스로 여러 개의 객체를 생성할 수 있습니다.

### 상세 설명

**클래스(Class)**는 객체의 구조를 정의하는 틀입니다. 붕어빵 틀에 비유할 수 있으며, 어떤 데이터(필드)를 가질지, 어떤 동작(메서드)을 할지를 정의합니다.

**객체(Object/Instance)**는 클래스를 기반으로 실제로 생성된 개체입니다. 붕어빵 틀로 만든 실제 붕어빵에 해당하며, 메모리(힙)에 실제로 할당되어 독립적인 상태를 가집니다.

```java
// 클래스 정의 (설계도)
public class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}

// 객체 생성 (실체)
Person p1 = new Person("홍길동", 20);  // 첫 번째 객체
Person p2 = new Person("김철수", 25);  // 두 번째 객체
// p1과 p2는 서로 다른 메모리 공간에 존재하는 독립적인 객체
```

### 꼬리 질문 예상
- 인스턴스와 객체의 차이는? → 거의 같은 의미로 사용됨. 객체가 더 일반적인 용어.
- 클래스 없이 객체를 만들 수 있나? → Java는 불가능. 클래스 기반 언어이기 때문.
- static 멤버는 객체와 어떤 관계인가? → 객체가 아닌 클래스에 속함.

## 질문 2: 생성자의 역할과 특징은?

### 핵심 답변 (3줄)
1. 생성자는 객체가 생성될 때 호출되어 객체를 초기화하는 특수한 메서드입니다.
2. 클래스명과 동일하고 반환 타입이 없으며, new 키워드로 객체 생성 시 자동 호출됩니다.
3. 명시하지 않으면 기본 생성자가 자동 생성되지만, 하나라도 정의하면 자동 생성되지 않습니다.

### 상세 설명

**생성자의 역할**:
- 객체의 필드를 초기화
- 객체 생성 시 필요한 초기 설정 수행
- 유효성 검증을 통해 올바른 객체만 생성

**생성자의 특징**:
1. 메서드명이 클래스명과 동일
2. 반환 타입이 없음 (void도 쓰지 않음)
3. 오버로딩 가능 (매개변수를 다르게 여러 개 정의)
4. this()로 다른 생성자 호출 가능 (반드시 첫 줄)

```java
public class Person {
    private String name;
    private int age;
    
    // 기본 생성자
    public Person() {
        this("Unknown", 0);
    }
    
    // 매개변수 1개 생성자
    public Person(String name) {
        this(name, 0);
    }
    
    // 매개변수 2개 생성자
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

**기본 생성자 자동 생성 규칙**:
```java
// 생성자를 하나도 안 만들면 → 기본 생성자 자동 생성
public class A { }  
// A a = new A(); ✅ 가능

// 생성자를 하나라도 만들면 → 기본 생성자 자동 생성 안 됨
public class B {
    public B(String name) { }
}
// B b = new B(); ❌ 에러
// B b = new B("이름"); ✅ 가능
```

### 꼬리 질문 예상
- 생성자와 일반 메서드의 차이는? → 생성자는 반환 타입 없고, 객체 생성 시에만 호출됨.
- this()와 super()의 차이는? → this()는 같은 클래스의 다른 생성자 호출, super()는 부모 클래스 생성자 호출.
- 생성자를 private으로 만들면? → 외부에서 객체 생성 불가 (싱글톤 패턴에 활용).

## 질문 3: this 키워드는 언제 사용하나?

### 핵심 답변 (3줄)
1. this는 현재 객체 자신을 가리키는 참조 변수입니다.
2. 필드와 매개변수 이름이 같을 때 구분하거나, 다른 생성자를 호출할 때 사용합니다.
3. 메서드 체이닝을 구현할 때 자기 자신을 반환하는 용도로도 사용합니다.

### 상세 설명

**this의 3가지 용도**:

**1) 필드와 매개변수 구분**
```java
public class Person {
    private String name;
    
    public Person(String name) {
        this.name = name;  // this.name은 필드, name은 매개변수
    }
    
    public void setName(String name) {
        this.name = name;
    }
}
```

**2) 다른 생성자 호출**
```java
public class Person {
    private String name;
    private int age;
    
    public Person() {
        this("Unknown", 0);  // 다른 생성자 호출 (반드시 첫 줄)
    }
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

**3) 메서드 체이닝**
```java
public class Person {
    private String name;
    private int age;
    
    public Person setName(String name) {
        this.name = name;
        return this;  // 자기 자신 반환
    }
    
    public Person setAge(int age) {
        this.age = age;
        return this;
    }
}

// 사용
Person person = new Person()
    .setName("홍길동")
    .setAge(20);
```

### 꼬리 질문 예상
- this를 생략할 수 있나? → 필드와 지역변수 이름이 다르면 생략 가능하지만, 명시하는 것이 가독성에 좋음.
- this()는 왜 생성자 첫 줄에만 올 수 있나? → 객체 초기화가 완료되기 전에 다른 코드가 실행되면 안 되기 때문.
- static 메서드에서 this를 사용할 수 있나? → 불가능. static은 객체 없이 호출되므로 this가 존재하지 않음.

## 질문 4: == 과 equals()의 차이는?

### 핵심 답변 (3줄)
1. ==은 참조 타입에서 메모리 주소를 비교하고, equals()는 객체의 내용(값)을 비교합니다.
2. 기본적으로 equals()는 ==과 동일하게 동작하지만, String 등은 내용 비교로 오버라이드되어 있습니다.
3. 커스텀 클래스에서 내용 비교를 원하면 equals()를 오버라이드해야 합니다.

### 상세 설명

**== 연산자**:
- 기본 타입: 값 비교
- 참조 타입: 메모리 주소(참조) 비교

```java
// 기본 타입
int a = 10;
int b = 10;
System.out.println(a == b);  // true (값 비교)

// 참조 타입
String s1 = new String("Hello");
String s2 = new String("Hello");
System.out.println(s1 == s2);  // false (주소 비교)

Person p1 = new Person("홍길동", 20);
Person p2 = new Person("홍길동", 20);
System.out.println(p1 == p2);  // false (다른 객체)

Person p3 = p1;
System.out.println(p1 == p3);  // true (같은 객체)
```

**equals() 메서드**:
- Object 클래스의 메서드 (모든 클래스가 상속)
- 기본 구현은 == 과 동일 (주소 비교)
- String, Integer 등은 내용 비교로 오버라이드

```java
String s1 = new String("Hello");
String s2 = new String("Hello");
System.out.println(s1.equals(s2));  // true (내용 비교)

// 커스텀 클래스에서 equals() 오버라이드
public class Person {
    private String name;
    private int age;
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        Person person = (Person) obj;
        return age == person.age && 
               Objects.equals(name, person.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}
```

### 꼬리 질문 예상
- equals()를 오버라이드할 때 주의사항은? → hashCode()도 함께 오버라이드해야 함 (Hash 기반 컬렉션에서 정상 동작).
- String의 == 비교가 가끔 true가 나오는 이유는? → String Pool 때문. 리터럴로 생성하면 같은 객체 재사용.
- null과 비교할 때 주의점은? → equals()는 NullPointerException 발생 가능. Objects.equals() 사용 권장.

## 질문 5: 캡슐화가 왜 중요한가?

### 핵심 답변 (3줄)
1. 캡슐화는 데이터(필드)를 외부로부터 보호하고, 메서드를 통해서만 접근하도록 하는 것입니다.
2. 데이터 무결성을 보장하고, 내부 구현을 숨겨 변경에 유연하게 대응할 수 있습니다.
3. 객체지향의 핵심 원칙으로, 유지보수성과 재사용성을 높입니다.

### 상세 설명

**캡슐화의 정의**:
- 데이터와 메서드를 하나로 묶고
- 외부에서 직접 접근하지 못하도록 숨김 (정보 은닉)
- 공개된 인터페이스(메서드)를 통해서만 접근 허용

**캡슐화를 하지 않은 경우**:
```java
// ❌ 나쁜 예: 필드를 public으로 노출
public class BankAccount {
    public long balance;  // 직접 접근 가능
}

// 문제점
BankAccount account = new BankAccount();
account.balance = -1000000;  // 음수 잔액 가능 (데이터 무결성 깨짐)
account.balance = 999999999;  // 검증 없이 임의 변경
```

**캡슐화를 적용한 경우**:
```java
// ✅ 좋은 예: private + getter/setter
public class BankAccount {
    private long balance;  // 외부 접근 차단
    
    public long getBalance() {
        return balance;
    }
    
    public void deposit(long amount) {
        if (amount > 0) {  // 유효성 검증
            balance += amount;
        } else {
            throw new IllegalArgumentException("입금액은 0보다 커야 합니다");
        }
    }
    
    public boolean withdraw(long amount) {
        if (amount > 0 && balance >= amount) {  // 검증
            balance -= amount;
            return true;
        }
        return false;
    }
}

// 사용
BankAccount account = new BankAccount();
account.deposit(10000);      // ✅ 검증된 방법으로만 변경
account.withdraw(3000);       // ✅ 잔액 확인 후 출금
// account.balance = -1000;   // ❌ 컴파일 에러 (직접 접근 불가)
```

**캡슐화의 장점**:
1. **데이터 보호**: 잘못된 값 설정 방지
2. **유연성**: 내부 구현 변경 시 외부 코드 영향 최소화
3. **재사용성**: 잘 설계된 클래스는 다른 프로젝트에서도 사용 가능
4. **유지보수**: 변경 범위를 클래스 내부로 제한

**실무 예시**:
```java
public class User {
    private String email;
    private String password;
    
    public void setEmail(String email) {
        // 이메일 형식 검증
        if (email.matches("^[A-Za-z0-9+_.-]+@(.+)$")) {
            this.email = email;
        } else {
            throw new IllegalArgumentException("잘못된 이메일 형식");
        }
    }
    
    public void setPassword(String password) {
        // 비밀번호 복잡도 검증
        if (password.length() >= 8) {
            this.password = hashPassword(password);  // 암호화 저장
        } else {
            throw new IllegalArgumentException("비밀번호는 8자 이상");
        }
    }
    
    private String hashPassword(String password) {
        // 해싱 로직 (외부에서 접근 불가)
        return password; // 실제로는 SHA-256 등 사용
    }
}
```

### 꼬리 질문 예상
- 모든 필드에 getter/setter를 만들어야 하나? → 아니오. 필요한 것만. 특히 setter는 신중하게 (불변 객체 고려).
- protected는 캡슐화를 위반하나? → 같은 패키지나 상속 관계에서 접근 가능하므로 public보다는 낫지만 완벽한 캡슐화는 아님.
- DTO는 왜 getter/setter를 모두 public으로 하나? → 데이터 전달이 목적이므로 캡슐화보다 편의성 우선. 단, 불변 DTO 선호 추세.

## 참고
- [[Java-클래스-객체지향기초]]
- [[Java-상속-다형성-super]]
