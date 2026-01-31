---
tags:
  - study
  - java
  - oop
  - inheritance
created: 2026-01-31
---

# Java 상속, 다형성, super

## 한 줄 요약
> 상속은 기존 클래스를 재사용하고, 다형성은 하나의 타입으로 여러 객체를 다루는 객체지향 핵심 개념이다.

## 상세 설명

### 1. 상속(Inheritance)

**상속이란**: 기존 클래스(부모 클래스)의 필드와 메서드를 새로운 클래스(자식 클래스)가 물려받는 것

**문법**: `extends` 키워드 사용
```java
public class Parent {
    protected String name;
    
    public void display() {
        System.out.println("부모 클래스");
    }
}

public class Child extends Parent {
    private int age;
    
    public void showInfo() {
        System.out.println(name + ", " + age);  // 부모의 name 사용 가능
    }
}
```

**상속의 장점**:
- 코드 재사용성 증가
- 유지보수 용이
- 계층 구조 표현 가능

**Java 상속의 특징**:
- **단일 상속만 지원**: 하나의 부모 클래스만 상속 가능
- **다중 상속 불가**: `class Child extends Parent1, Parent2` ❌
- **Object 클래스**: 모든 클래스는 암묵적으로 Object 상속

### 2. 메서드 오버라이딩(Overriding)

**오버라이딩**: 부모 클래스의 메서드를 자식 클래스에서 재정의

**규칙**:
- 메서드 시그니처(이름, 매개변수)가 동일해야 함
- 접근 제어자는 부모보다 넓거나 같아야 함
- 반환 타입은 같거나 하위 타입이어야 함

```java
public class Animal {
    public void sound() {
        System.out.println("동물 소리");
    }
}

public class Dog extends Animal {
    @Override  // 오버라이딩 명시 (권장)
    public void sound() {
        System.out.println("멍멍!");
    }
}

public class Cat extends Animal {
    @Override
    public void sound() {
        System.out.println("야옹!");
    }
}
```

### 3. super 키워드

**super의 의미**: 부모 클래스를 가리키는 참조

**용도 1 - 부모 클래스의 생성자 호출**
```java
public class Parent {
    private String name;
    
    public Parent(String name) {
        this.name = name;
    }
}

public class Child extends Parent {
    private int age;
    
    public Child(String name, int age) {
        super(name);  // 부모 생성자 호출 (반드시 첫 줄)
        this.age = age;
    }
}
```

**용도 2 - 부모 클래스의 메서드 호출**
```java
public class Parent {
    public void display() {
        System.out.println("부모 메서드");
    }
}

public class Child extends Parent {
    @Override
    public void display() {
        super.display();  // 부모 메서드 호출
        System.out.println("자식 메서드");
    }
}
```

**용도 3 - 부모 클래스의 필드 접근**
```java
public class Parent {
    protected String name = "부모";
}

public class Child extends Parent {
    private String name = "자식";
    
    public void printNames() {
        System.out.println(this.name);   // "자식"
        System.out.println(super.name);  // "부모"
    }
}
```

### 4. 다형성(Polymorphism)

**다형성이란**: 하나의 타입(부모 타입)으로 여러 종류의 객체(자식 객체)를 다루는 것

**업캐스팅(Upcasting)**: 자식 → 부모 타입으로 자동 형변환
```java
Animal animal = new Dog();  // 자동 형변환 (업캐스팅)
animal.sound();  // "멍멍!" - 실제 객체(Dog)의 메서드 호출
```

**다운캐스팅(Downcasting)**: 부모 → 자식 타입으로 명시적 형변환
```java
Animal animal = new Dog();
Dog dog = (Dog) animal;  // 명시적 형변환 (다운캐스팅)
dog.bark();  // Dog만의 메서드 호출 가능
```

**instanceof 연산자**: 객체의 실제 타입 확인
```java
Animal animal = new Dog();

if (animal instanceof Dog) {
    Dog dog = (Dog) animal;
    dog.bark();
}
```

### 5. 메서드 오버로딩 vs 오버라이딩

| 구분 | 오버로딩(Overloading) | 오버라이딩(Overriding) |
|------|----------------------|---------------------|
| 정의 | 같은 이름, 다른 매개변수 | 부모 메서드 재정의 |
| 관계 | 같은 클래스 내 | 상속 관계 |
| 매개변수 | 반드시 달라야 함 | 반드시 같아야 함 |
| 반환 타입 | 상관없음 | 같거나 하위 타입 |
| 시점 | 컴파일 타임 (정적 바인딩) | 런타임 (동적 바인딩) |

```java
// 오버로딩
public class Calculator {
    public int add(int a, int b) { return a + b; }
    public double add(double a, double b) { return a + b; }
    public int add(int a, int b, int c) { return a + b + c; }
}

// 오버라이딩
public class Parent {
    public void method() { }
}
public class Child extends Parent {
    @Override
    public void method() { }  // 재정의
}
```

## 코드 예시

### 예제 1: 직원 관리 시스템

```java
// 부모 클래스
public class Employee {
    protected String name;
    protected int empId;
    protected double baseSalary;
    
    public Employee(String name, int empId, double baseSalary) {
        this.name = name;
        this.empId = empId;
        this.baseSalary = baseSalary;
    }
    
    // 급여 계산 (오버라이딩 대상)
    public double calculateSalary() {
        return baseSalary;
    }
    
    public void displayInfo() {
        System.out.println("사원명: " + name);
        System.out.println("사번: " + empId);
        System.out.println("급여: " + calculateSalary());
    }
}

// 정규직
public class FullTimeEmployee extends Employee {
    private double bonus;
    
    public FullTimeEmployee(String name, int empId, double baseSalary, double bonus) {
        super(name, empId, baseSalary);
        this.bonus = bonus;
    }
    
    @Override
    public double calculateSalary() {
        return baseSalary + bonus;  // 기본급 + 보너스
    }
}

// 계약직
public class ContractEmployee extends Employee {
    private int workDays;
    private double dailyRate;
    
    public ContractEmployee(String name, int empId, int workDays, double dailyRate) {
        super(name, empId, 0);  // 기본급 없음
        this.workDays = workDays;
        this.dailyRate = dailyRate;
    }
    
    @Override
    public double calculateSalary() {
        return workDays * dailyRate;  // 일당 * 근무일수
    }
}

// 사용 예시
public class Main {
    public static void main(String[] args) {
        Employee[] employees = {
            new FullTimeEmployee("홍길동", 1001, 3000000, 500000),
            new ContractEmployee("김철수", 1002, 20, 100000),
            new FullTimeEmployee("이영희", 1003, 3500000, 700000)
        };
        
        // 다형성 활용: 모든 직원을 동일한 방식으로 처리
        for (Employee emp : employees) {
            emp.displayInfo();
            System.out.println("---");
        }
    }
}
```

### 예제 2: 도형 계산

```java
public abstract class Shape {
    protected String color;
    
    public Shape(String color) {
        this.color = color;
    }
    
    // 추상 메서드 (자식이 반드시 구현)
    public abstract double getArea();
    public abstract double getPerimeter();
    
    public void displayInfo() {
        System.out.println("색상: " + color);
        System.out.println("넓이: " + getArea());
        System.out.println("둘레: " + getPerimeter());
    }
}

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

### 1. super()는 반드시 생성자 첫 줄에

```java
// ❌ 컴파일 에러
public Child(String name, int age) {
    this.age = age;
    super(name);  // 첫 줄이 아니므로 에러
}

// ✅ 올바른 사용
public Child(String name, int age) {
    super(name);  // 반드시 첫 줄
    this.age = age;
}
```

### 2. private 멤버는 상속되지만 접근 불가

```java
public class Parent {
    private String secret = "비밀";
}

public class Child extends Parent {
    public void show() {
        // System.out.println(secret);  // ❌ 컴파일 에러
        // private은 상속되지만 직접 접근 불가
    }
}
```

### 3. 다운캐스팅 시 ClassCastException 주의

```java
Animal animal = new Cat();

// ❌ 런타임 에러
Dog dog = (Dog) animal;  // Cat을 Dog로 캐스팅 불가

// ✅ instanceof로 확인 후 캐스팅
if (animal instanceof Dog) {
    Dog dog = (Dog) animal;
}
```

### 4. 오버라이딩 시 @Override 어노테이션 권장

```java
// ❌ 오타로 새로운 메서드 생성 (오버라이딩 실패)
public class Child extends Parent {
    public void displya() {  // display 오타
        // 부모 메서드가 호출되지 않음
    }
}

// ✅ @Override로 컴파일 타임 체크
public class Child extends Parent {
    @Override
    public void displya() {  // 컴파일 에러 발생
        
    }
}
```

### 5. 생성자는 상속되지 않음

```java
public class Parent {
    public Parent(String name) {
        // ...
    }
}

public class Child extends Parent {
    // 컴파일러가 기본 생성자를 만들려 하지만
    // 부모에 기본 생성자가 없으므로 에러
    
    // ✅ 명시적으로 부모 생성자 호출 필요
    public Child(String name) {
        super(name);
    }
}
```

## 관련 개념
- [[Java-클래스-객체지향기초]]
- [[Java-인터페이스-추상클래스]]

## 학습 로드맵 (TODO)
- Object 클래스와 공통 메서드(equals, hashCode, toString) 문서 필요
- final 키워드(클래스, 메서드, 변수) 문서 필요
- 추상 클래스 vs 인터페이스 비교 문서 필요

## 면접 질문
1. 상속의 장단점은?
2. 오버로딩과 오버라이딩의 차이는?
3. super와 this의 차이는?
4. 다형성이란 무엇이고 왜 중요한가?
5. 업캐스팅과 다운캐스팅의 차이는?

## 참고 자료
- Effective Java Item 18: Favor composition over inheritance
- Java Language Specification - Inheritance
