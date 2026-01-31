---
tags:
  - study
  - java
  - oop
created: 2026-01-31
---

# Java 클래스와 객체지향 기초

## 한 줄 요약
> 클래스는 객체를 만드는 설계도이고, 객체는 클래스를 바탕으로 생성된 실체다.

## 상세 설명

### 1. 클래스와 객체의 개념

**클래스(Class)**: 객체를 만들기 위한 설계도 또는 틀
- 속성(필드)과 동작(메서드)을 정의
- 사용자 정의 타입

**객체(Object)**: 클래스를 바탕으로 만들어진 실체(인스턴스)
- 메모리에 실제로 할당된 데이터
- 클래스 하나로 여러 객체 생성 가능

### 2. 클래스 구성 요소

```java
public class Person {
    // 1. 필드(Field) - 객체의 속성
    private String name;
    private int age;
    
    // 2. 생성자(Constructor) - 객체 초기화
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // 3. 메서드(Method) - 객체의 동작
    public void introduce() {
        System.out.println("이름: " + name + ", 나이: " + age);
    }
    
    // 4. Getter/Setter
    public String getName() {
        return name;
    }
    
    public void setAge(int age) {
        if (age > 0) {
            this.age = age;
        }
    }
}
```

### 3. 생성자(Constructor)

**기본 생성자**: 매개변수가 없는 생성자
```java
public Person() {
    // 명시하지 않으면 컴파일러가 자동 생성
}
```

**매개변수가 있는 생성자**: 초기값을 받아 객체 초기화
```java
public Person(String name, int age) {
    this.name = name;
    this.age = age;
}
```

**생성자 오버로딩**: 여러 개의 생성자 정의
```java
public class Person {
    private String name;
    private int age;
    
    public Person() {
        this("Unknown", 0);  // 다른 생성자 호출
    }
    
    public Person(String name) {
        this(name, 0);
    }
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

### 4. this 키워드

**this의 의미**: 현재 객체 자신을 가리키는 참조

**용도 1 - 필드와 매개변수 구분**
```java
public Person(String name, int age) {
    this.name = name;  // this.name은 필드, name은 매개변수
    this.age = age;
}
```

**용도 2 - 다른 생성자 호출**
```java
public Person() {
    this("Unknown", 0);  // 반드시 첫 줄에 위치
}
```

**용도 3 - 메서드 체이닝**
```java
public Person setName(String name) {
    this.name = name;
    return this;  // 자기 자신 반환
}

// 사용
person.setName("홍길동").setAge(20);
```

### 5. 객체 생성과 메모리

```java
Person p1 = new Person("홍길동", 20);
Person p2 = new Person("홍길동", 20);
Person p3 = p1;

System.out.println(p1 == p2);  // false (다른 객체)
System.out.println(p1 == p3);  // true (같은 객체)
```

**메모리 구조**:
- **스택(Stack)**: 참조 변수 p1, p2, p3 저장
- **힙(Heap)**: 실제 객체 데이터 저장
- p1과 p3는 같은 힙 메모리 주소를 참조

## 코드 예시

### 예제 1: 은행 계좌 클래스

```java
public class BankAccount {
    private String accountNumber;
    private String owner;
    private long balance;
    
    // 생성자
    public BankAccount(String accountNumber, String owner) {
        this.accountNumber = accountNumber;
        this.owner = owner;
        this.balance = 0;
    }
    
    // 입금
    public void deposit(long amount) {
        if (amount > 0) {
            balance += amount;
            System.out.println(amount + "원 입금 완료. 잔액: " + balance);
        }
    }
    
    // 출금
    public boolean withdraw(long amount) {
        if (amount > 0 && balance >= amount) {
            balance -= amount;
            System.out.println(amount + "원 출금 완료. 잔액: " + balance);
            return true;
        }
        System.out.println("잔액 부족");
        return false;
    }
    
    // 잔액 조회
    public long getBalance() {
        return balance;
    }
}

// 사용 예시
public class Main {
    public static void main(String[] args) {
        BankAccount account = new BankAccount("1234-5678", "홍길동");
        
        account.deposit(10000);   // 10000원 입금
        account.withdraw(3000);   // 3000원 출금
        account.withdraw(8000);   // 잔액 부족
        
        System.out.println("현재 잔액: " + account.getBalance());
    }
}
```

### 예제 2: 학생 성적 관리

```java
public class Student {
    private String name;
    private int korScore;
    private int engScore;
    private int mathScore;
    
    public Student(String name, int kor, int eng, int math) {
        this.name = name;
        this.korScore = kor;
        this.engScore = eng;
        this.mathScore = math;
    }
    
    // 총점 계산
    public int getTotalScore() {
        return korScore + engScore + mathScore;
    }
    
    // 평균 계산
    public double getAverage() {
        return getTotalScore() / 3.0;
    }
    
    // 성적표 출력
    public void printReport() {
        System.out.println("=== 성적표 ===");
        System.out.println("이름: " + name);
        System.out.println("국어: " + korScore);
        System.out.println("영어: " + engScore);
        System.out.println("수학: " + mathScore);
        System.out.println("총점: " + getTotalScore());
        System.out.printf("평균: %.2f\n", getAverage());
    }
}

// 사용 예시
Student student = new Student("김철수", 85, 90, 88);
student.printReport();
```

## 주의사항 / 함정

### 1. 생성자를 하나라도 정의하면 기본 생성자는 자동 생성 안 됨

```java
public class Person {
    private String name;
    
    public Person(String name) {
        this.name = name;
    }
}

// ❌ 컴파일 에러
Person p = new Person();  // 기본 생성자가 없음

// ✅ 해결 방법: 명시적으로 기본 생성자 추가
public Person() {
    this("Unknown");
}
```

### 2. this()는 반드시 생성자 첫 줄에

```java
// ❌ 컴파일 에러
public Person(String name) {
    System.out.println("생성자 호출");
    this();  // 첫 줄이 아니므로 에러
}

// ✅ 올바른 사용
public Person(String name) {
    this();  // 반드시 첫 줄
    System.out.println("생성자 호출");
}
```

### 3. 참조 타입 비교 시 == vs equals()

```java
Person p1 = new Person("홍길동", 20);
Person p2 = new Person("홍길동", 20);

System.out.println(p1 == p2);  // false (주소 비교)
// equals()를 오버라이드하지 않으면 == 과 동일하게 동작
```

### 4. 캡슐화 위반 주의

```java
// ❌ 나쁜 예: 필드를 public으로 노출
public class Person {
    public String name;  // 외부에서 직접 접근 가능
    public int age;
}

// ✅ 좋은 예: private + getter/setter
public class Person {
    private String name;
    private int age;
    
    public void setAge(int age) {
        if (age > 0 && age < 150) {  // 유효성 검증
            this.age = age;
        }
    }
}
```

## 관련 개념
- [[Java-상속-다형성-super]]
- [[Java-인터페이스-추상클래스]]

## 학습 로드맵 (TODO)
- 접근 제어자(public, private, protected, default) 상세 문서 필요
- 캡슐화(Encapsulation) 원칙 문서 필요
- static 키워드와 클래스 변수/메서드 문서 필요

## 면접 질문
1. 클래스와 객체의 차이는?
2. 생성자의 역할과 특징은?
3. this 키워드는 언제 사용하나?
4. == 과 equals()의 차이는?
5. 캡슐화가 왜 중요한가?

## 참고 자료
- Java Language Specification - Classes
- Effective Java Item 1: Consider static factory methods instead of constructors
