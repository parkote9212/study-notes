---
tags:
  - interview
  - java
  - oop
  - inheritance
created: 2026-01-31
difficulty: 중
---

# Java 상속, 다형성, super 면접

## 질문 1: 상속의 장단점은?

### 핵심 답변 (3줄)
1. 장점은 코드 재사용성이 높아지고, 계층 구조를 통해 유지보수가 쉬워진다는 것입니다.
2. 단점은 부모-자식 클래스 간 결합도가 높아져 변경에 취약하고, 불필요한 메서드까지 상속받을 수 있다는 것입니다.
3. Effective Java에서는 상속보다 컴포지션을 우선하라고 권장합니다.

### 상세 설명

**상속의 장점**:
1. **코드 재사용**: 부모 클래스의 코드를 중복 작성하지 않음
2. **확장성**: 기존 코드 수정 없이 새로운 기능 추가 가능
3. **다형성 지원**: 부모 타입으로 여러 자식 객체 다룰 수 있음
4. **계층 구조**: is-a 관계를 명확하게 표현

```java
// 재사용 예시
public class Animal {
    protected String name;
    
    public void eat() {
        System.out.println(name + "이(가) 먹이를 먹습니다");
    }
}

public class Dog extends Animal {
    // eat() 메서드 재사용
    public void bark() {
        System.out.println("멍멍!");
    }
}
```

**상속의 단점**:
1. **높은 결합도**: 부모 변경 시 자식도 영향받음
2. **캡슐화 위반**: 부모의 내부 구현 노출
3. **불필요한 상속**: 필요 없는 메서드까지 상속
4. **다중 상속 불가**: Java는 단일 상속만 지원

```java
// 문제 예시
public class Stack extends ArrayList {
    // ArrayList의 add(index, element) 같은
    // Stack에 적합하지 않은 메서드까지 상속
}

// ✅ 컴포지션 사용 (더 나은 설계)
public class Stack {
    private List list = new ArrayList();
    
    public void push(Object item) {
        list.add(item);
    }
    
    public Object pop() {
        return list.remove(list.size() - 1);
    }
}
```

### 꼬리 질문 예상
- 컴포지션이 상속보다 나은 이유는? → 유연성과 낮은 결합도. has-a 관계로 필요한 기능만 위임.
- 언제 상속을 사용해야 하나? → 명확한 is-a 관계이고, 부모 클래스가 확장을 고려해 설계된 경우.
- Java가 다중 상속을 지원하지 않는 이유는? → 다이아몬드 문제(같은 메서드를 여러 부모에서 상속 시 충돌).

## 질문 2: 오버로딩과 오버라이딩의 차이는?

### 핵심 답변 (3줄)
1. 오버로딩은 같은 이름의 메서드를 매개변수를 다르게 하여 여러 개 정의하는 것입니다.
2. 오버라이딩은 부모 클래스의 메서드를 자식 클래스에서 재정의하는 것입니다.
3. 오버로딩은 컴파일 타임에 결정되고(정적 바인딩), 오버라이딩은 런타임에 결정됩니다(동적 바인딩).

### 상세 설명

**오버로딩(Overloading)**:
- 같은 클래스 내에서 사용
- 메서드 이름은 같지만 매개변수가 다름
- 반환 타입은 상관없음 (매개변수로만 구분)
- 컴파일 타임에 어떤 메서드를 호출할지 결정

```java
public class Calculator {
    // 매개변수 개수가 다름
    public int add(int a, int b) {
        return a + b;
    }
    
    public int add(int a, int b, int c) {
        return a + b + c;
    }
    
    // 매개변수 타입이 다름
    public double add(double a, double b) {
        return a + b;
    }
}

Calculator calc = new Calculator();
calc.add(1, 2);        // 첫 번째 메서드 호출
calc.add(1, 2, 3);     // 두 번째 메서드 호출
calc.add(1.5, 2.5);    // 세 번째 메서드 호출
```

**오버라이딩(Overriding)**:
- 상속 관계에서 사용
- 메서드 시그니처(이름, 매개변수)가 완전히 동일
- 반환 타입은 같거나 하위 타입
- 런타임에 실제 객체 타입에 따라 메서드 결정

```java
public class Animal {
    public void sound() {
        System.out.println("동물 소리");
    }
}

public class Dog extends Animal {
    @Override
    public void sound() {  // 완전히 동일한 시그니처
        System.out.println("멍멍!");
    }
}

Animal animal = new Dog();
animal.sound();  // "멍멍!" - 런타임에 Dog의 메서드 호출
```

**비교표**:

| 구분     | 오버로딩        | 오버라이딩      |
| ------ | ----------- | ---------- |
| 관계     | 같은 클래스      | 상속 관계      |
| 목적     | 다양한 입력 처리   | 부모 메서드 재정의 |
| 메서드 이름 | 동일          | 동일         |
| 매개변수   | **반드시 다름**  | **반드시 같음** |
| 반환 타입  | 상관없음        | 같거나 하위 타입  |
| 바인딩    | 컴파일 타임 (정적) | 런타임 (동적)   |

### 코드 예시

```java
// 오버로딩과 오버라이딩 동시 사용
public class Parent {
    public void print(String msg) {
        System.out.println("Parent: " + msg);
    }
}

public class Child extends Parent {
    // 오버라이딩
    @Override
    public void print(String msg) {
        System.out.println("Child: " + msg);
    }
    
    // 오버로딩
    public void print(String msg, int count) {
        for (int i = 0; i < count; i++) {
            System.out.println("Child: " + msg);
        }
    }
}

Child child = new Child();
child.print("Hello");        // 오버라이딩된 메서드
child.print("Hello", 3);     // 오버로딩된 메서드
```

### 꼬리 질문 예상
- 오버로딩 시 매개변수 순서만 바꿔도 되나? → 네, 타입이 다르면 가능. 하지만 가독성 떨어져 비추천.
- @Override 어노테이션은 왜 사용하나? → 컴파일 타임에 오버라이딩 검증. 오타 방지.
- private 메서드를 오버라이딩할 수 있나? → 불가능. 상속되지 않으므로 새로운 메서드 정의.

## 질문 3: super와 this의 차이는?

### 핵심 답변 (3줄)
1. this는 현재 객체 자신을, super는 부모 클래스를 가리키는 참조입니다.
2. this()는 같은 클래스의 다른 생성자를, super()는 부모 클래스의 생성자를 호출합니다.
3. 둘 다 생성자에서 사용 시 반드시 첫 줄에 위치해야 하며, 동시 사용은 불가능합니다.

### 상세 설명

**this vs super 비교**:

| 구분     | this       | super       |
| ------ | ---------- | ----------- |
| 의미     | 현재 객체      | 부모 객체       |
| 필드 접근  | this.필드명   | super.필드명   |
| 메서드 호출 | this.메서드() | super.메서드() |
| 생성자 호출 | this()     | super()     |
| 사용 위치  | 같은 클래스     | 부모 클래스      |

**1) 생성자 호출**:
```java
public class Parent {
    private String name;
    
    public Parent(String name) {
        this.name = name;
    }
}

public class Child extends Parent {
    private int age;
    
    // super() - 부모 생성자 호출
    public Child(String name, int age) {
        super(name);  // 반드시 첫 줄
        this.age = age;
    }
    
    // this() - 같은 클래스의 다른 생성자 호출
    public Child() {
        this("Unknown", 0);  // 반드시 첫 줄
    }
}
```

**2) 필드 접근**:
```java
public class Parent {
    protected String name = "부모";
}

public class Child extends Parent {
    private String name = "자식";
    
    public void printNames() {
        System.out.println(this.name);   // "자식"
        System.out.println(super.name);  // "부모"
        System.out.println(name);        // "자식" (this 생략)
    }
}
```

**3) 메서드 호출**:
```java
public class Parent {
    public void display() {
        System.out.println("부모 메서드");
    }
}

public class Child extends Parent {
    @Override
    public void display() {
        super.display();  // 부모 메서드 먼저 호출
        System.out.println("자식 메서드");
    }
}

// 출력:
// 부모 메서드
// 자식 메서드
```

**중요 규칙**:
```java
// ❌ 컴파일 에러: 둘 다 첫 줄에 와야 하므로 동시 사용 불가
public Child(String name, int age) {
    this();        // 첫 줄
    super(name);   // 에러!
}

// ❌ 컴파일 에러: 생성자 첫 줄이 아님
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

### 꼬리 질문 예상
- super()를 명시하지 않으면? → 컴파일러가 자동으로 super() 삽입 (부모의 기본 생성자 호출).
- 부모에 기본 생성자가 없으면? → 컴파일 에러. 반드시 super(매개변수)로 명시 필요.
- static 메서드에서 this/super 사용 가능한가? → 불가능. 객체 없이 호출되므로.

## 질문 4: 다형성이란 무엇이고 왜 중요한가?

### 핵심 답변 (3줄)
1. 다형성은 하나의 타입(부모 타입)으로 여러 종류의 객체(자식 객체)를 다루는 것입니다.
2. 코드의 유연성과 확장성을 높이고, 중복을 줄여 유지보수를 쉽게 합니다.
3. 런타임에 실제 객체 타입에 따라 메서드가 결정되는 동적 바인딩이 핵심입니다.

### 상세 설명

**다형성의 정의**:
- Polymorphism = Poly(많은) + Morph(형태)
- 같은 인터페이스로 다른 동작을 수행
- "하나의 타입, 여러 객체"

**다형성이 없을 때**:
```java
// ❌ 각 타입마다 별도 처리 필요
public void processAnimals() {
    Dog dog = new Dog();
    Cat cat = new Cat();
    Bird bird = new Bird();
    
    dog.sound();   // 멍멍
    cat.sound();   // 야옹
    bird.sound();  // 짹짹
}

// 새로운 동물 추가 시 코드 수정 필요
```

**다형성 사용**:
```java
// ✅ 부모 타입으로 통일된 처리
public void processAnimals() {
    Animal[] animals = {
        new Dog(),
        new Cat(),
        new Bird()
    };
    
    for (Animal animal : animals) {
        animal.sound();  // 각 객체의 메서드가 호출됨
    }
}

// 새로운 동물 추가해도 이 코드는 수정 불필요!
```

**실무 예제: 결제 시스템**:
```java
// 인터페이스
public interface PaymentMethod {
    boolean pay(long amount);
}

// 구현체들
public class CreditCard implements PaymentMethod {
    @Override
    public boolean pay(long amount) {
        System.out.println("신용카드로 " + amount + "원 결제");
        return true;
    }
}

public class KakaoPay implements PaymentMethod {
    @Override
    public boolean pay(long amount) {
        System.out.println("카카오페이로 " + amount + "원 결제");
        return true;
    }
}

// 다형성 활용 - 결제 수단에 무관한 코드
public class PaymentService {
    public void processPayment(PaymentMethod method, long amount) {
        if (method.pay(amount)) {
            System.out.println("결제 완료");
        }
    }
}

// 사용
PaymentService service = new PaymentService();
service.processPayment(new CreditCard(), 10000);
service.processPayment(new KakaoPay(), 20000);
// 네이버페이 추가해도 PaymentService 코드 수정 불필요
```

**다형성의 장점**:
1. **확장성**: 새로운 타입 추가 시 기존 코드 수정 최소화 (OCP 원칙)
2. **유연성**: 런타임에 동작 변경 가능
3. **코드 중복 제거**: 공통 처리 코드 재사용
4. **유지보수**: 변경 영향 범위 제한

### 꼬리 질문 예상
- 컴파일 타임 다형성과 런타임 다형성의 차이는? → 컴파일 타임은 오버로딩, 런타임은 오버라이딩.
- 다형성이 적용되지 않는 경우는? → final 메서드, private 메서드, static 메서드.
- LSP(리스코프 치환 원칙)과의 관계는? → 자식 객체는 부모 객체를 완전히 대체 가능해야 함.

## 질문 5: 업캐스팅과 다운캐스팅의 차이는?

### 핵심 답변 (3줄)
1. 업캐스팅은 자식 타입을 부모 타입으로 변환하는 것으로 자동 형변환되며 안전합니다.
2. 다운캐스팅은 부모 타입을 자식 타입으로 변환하는 것으로 명시적 형변환이 필요하고 위험합니다.
3. 다운캐스팅 전에는 instanceof로 타입을 확인하여 ClassCastException을 방지해야 합니다.

### 상세 설명

**업캐스팅(Upcasting)**:
- 자식 → 부모 방향
- 자동 형변환 (묵시적)
- 항상 안전
- 다형성의 기본

```java
Dog dog = new Dog();
Animal animal = dog;  // 자동 업캐스팅
// Animal animal = (Animal) dog;  // 형변환 생략 가능

animal.eat();    // ✅ Animal 메서드 호출 가능
animal.sound();  // ✅ 오버라이딩된 메서드 호출 (Dog의 sound)
// animal.bark();  // ❌ Dog만의 메서드는 호출 불가
```

**다운캐스팅(Downcasting)**:
- 부모 → 자식 방향
- 명시적 형변환 필요
- 잘못하면 런타임 에러 (ClassCastException)
- 자식 타입의 메서드 사용하려 할 때

```java
Animal animal = new Dog();  // 실제 객체는 Dog

// ✅ 올바른 다운캐스팅
Dog dog = (Dog) animal;
dog.bark();  // Dog의 메서드 호출 가능

// ❌ 잘못된 다운캐스팅
Animal animal2 = new Cat();
Dog dog2 = (Dog) animal2;  // ClassCastException 발생!
```

**안전한 다운캐스팅: instanceof 사용**:
```java
public void handleAnimal(Animal animal) {
    // instanceof로 타입 확인
    if (animal instanceof Dog) {
        Dog dog = (Dog) animal;
        dog.bark();
    } else if (animal instanceof Cat) {
        Cat cat = (Cat) animal;
        cat.meow();
    }
}

// Java 16+ Pattern Matching
public void handleAnimalModern(Animal animal) {
    if (animal instanceof Dog dog) {  // 타입 확인 + 캐스팅 동시
        dog.bark();
    } else if (animal instanceof Cat cat) {
        cat.meow();
    }
}
```

**실무 예제**:
```java
public class EventHandler {
    public void handleEvent(Event event) {
        // 다양한 이벤트 타입 처리
        if (event instanceof ClickEvent) {
            ClickEvent clickEvent = (ClickEvent) event;
            System.out.println("클릭 위치: " + clickEvent.getX() + ", " + clickEvent.getY());
        } else if (event instanceof KeyEvent) {
            KeyEvent keyEvent = (KeyEvent) event;
            System.out.println("눌린 키: " + keyEvent.getKeyCode());
        }
    }
}
```

**주의사항**:
```java
// ❌ 잘못된 패턴: 다운캐스팅 남발
public void processAnimal(Animal animal) {
    if (animal instanceof Dog) {
        ((Dog) animal).bark();
    } else if (animal instanceof Cat) {
        ((Cat) animal).meow();
    } else if (animal instanceof Bird) {
        ((Bird) animal).fly();
    }
    // → 타입 분기가 많으면 다형성 활용 실패
}

// ✅ 올바른 패턴: 다형성 활용
public void processAnimal(Animal animal) {
    animal.sound();  // 각 동물의 오버라이딩된 메서드 호출
}
```

### 꼬리 질문 예상
- instanceof 체크 없이 다운캐스팅하면? → ClassCastException 발생 가능 (런타임 에러).
- 업캐스팅된 객체는 자식 메서드를 잃어버리나? → 메서드는 존재하지만 부모 타입 변수로는 호출 불가.
- null을 instanceof로 체크하면? → 항상 false 반환 (NullPointerException 발생 안 함).

## 참고
- [[Java-상속-다형성-super]]
- [[Java-인터페이스-추상클래스]]
- [[Java-클래스-객체지향기초]]
