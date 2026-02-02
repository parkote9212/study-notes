---
tags:
  - study
  - java
  - object
  - clone
  - cloneable
created: 2025-02-02
---

# Java Object clone

## 한 줄 요약
> 객체의 복사본을 생성하는 메서드와 Cloneable 인터페이스

## 상세 설명

### clone() 메서드 기본 개념

`clone()`은 객체의 복사본을 생성하는 메서드입니다. Object 클래스에 protected로 정의되어 있으며, 사용하려면 Cloneable 인터페이스를 구현하고 clone()을 오버라이딩해야 합니다.

**기본 특징**
- 새로운 객체를 생성하여 원본 객체의 필드 값을 복사
- 기본적으로 얕은 복사(Shallow Copy) 수행
- Cloneable 미구현 시 CloneNotSupportedException 발생

### 얕은 복사 vs 깊은 복사

**얕은 복사 (Shallow Copy)**
- 객체의 필드 값을 그대로 복사
- 참조 타입 필드는 같은 객체를 가리킴
- 기본 타입 필드만 있는 경우 문제 없음

**깊은 복사 (Deep Copy)**
- 참조 타입 필드가 가리키는 객체까지 복사
- 완전히 독립적인 복사본 생성
- 중첩된 객체 구조에서 필요

### Cloneable 인터페이스

```java
public interface Cloneable {
    // 메서드 없음 (마커 인터페이스)
}
```

Cloneable은 마커 인터페이스로, clone() 호출이 가능함을 표시하는 역할만 합니다.

## 코드 예시

### 기본 clone() 구현

```java
class Person implements Cloneable {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public Person clone() {
        try {
            return (Person) super.clone();
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();  // Cloneable 구현했으므로 발생 안함
        }
    }
    
    // getter, setter
}

// 사용
Person original = new Person("홍길동", 30);
Person copy = original.clone();

copy.setAge(31);
System.out.println(original.getAge());  // 30 (영향 없음)
System.out.println(copy.getAge());      // 31
```

### 얕은 복사의 문제점

```java
class Team implements Cloneable {
    private String name;
    private List<String> members;  // 참조 타입
    
    public Team(String name, List<String> members) {
        this.name = name;
        this.members = members;
    }
    
    @Override
    public Team clone() {
        try {
            return (Team) super.clone();  // 얕은 복사
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}

// 문제 발생
List<String> originalMembers = new ArrayList<>(Arrays.asList("김철수", "이영희"));
Team original = new Team("개발팀", originalMembers);
Team copy = original.clone();

// ❌ members는 같은 List를 참조!
copy.getMembers().add("박민수");
System.out.println(original.getMembers().size());  // 3 (영향 받음!)
System.out.println(copy.getMembers().size());      // 3
```

### 깊은 복사 구현

```java
class Team implements Cloneable {
    private String name;
    private List<String> members;
    
    public Team(String name, List<String> members) {
        this.name = name;
        this.members = members;
    }
    
    @Override
    public Team clone() {
        try {
            Team cloned = (Team) super.clone();
            // List를 새로 생성하여 깊은 복사
            cloned.members = new ArrayList<>(this.members);
            return cloned;
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}

// 정상 동작
Team original = new Team("개발팀", new ArrayList<>(Arrays.asList("김철수", "이영희")));
Team copy = original.clone();

copy.getMembers().add("박민수");
System.out.println(original.getMembers().size());  // 2 (영향 없음)
System.out.println(copy.getMembers().size());      // 3
```

### 복잡한 객체의 깊은 복사

```java
class Address implements Cloneable {
    private String city;
    private String street;
    
    @Override
    public Address clone() {
        try {
            return (Address) super.clone();
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}

class Employee implements Cloneable {
    private String name;
    private Address address;  // 참조 타입
    private List<String> skills;  // 컬렉션
    
    @Override
    public Employee clone() {
        try {
            Employee cloned = (Employee) super.clone();
            
            // Address 깊은 복사
            cloned.address = this.address.clone();
            
            // List 깊은 복사
            cloned.skills = new ArrayList<>(this.skills);
            
            return cloned;
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}
```

### 복사 생성자 사용 (권장)

```java
class Person {
    private String name;
    private int age;
    private Address address;
    
    // 복사 생성자
    public Person(Person other) {
        this.name = other.name;
        this.age = other.age;
        this.address = new Address(other.address);  // 깊은 복사
    }
    
    // 일반 생성자
    public Person(String name, int age, Address address) {
        this.name = name;
        this.age = age;
        this.address = address;
    }
}

// 사용
Person original = new Person("홍길동", 30, new Address("서울", "강남구"));
Person copy = new Person(original);  // 명확하고 안전
```

### 정적 팩토리 메서드 사용 (권장)

```java
class Product {
    private String id;
    private String name;
    private int price;
    
    private Product(String id, String name, int price) {
        this.id = id;
        this.name = name;
        this.price = price;
    }
    
    // 정적 팩토리 메서드
    public static Product copyOf(Product original) {
        return new Product(
            original.id,
            original.name,
            original.price
        );
    }
}

// 사용
Product original = new Product("P001", "노트북", 1000000);
Product copy = Product.copyOf(original);
```

### 배열 복사

```java
// 배열은 clone()이 잘 동작함
int[] original = {1, 2, 3, 4, 5};
int[] copy = original.clone();

copy[0] = 100;
System.out.println(original[0]);  // 1 (영향 없음)
System.out.println(copy[0]);      // 100

// 객체 배열의 경우 얕은 복사
Person[] people = {new Person("홍길동", 30), new Person("김철수", 25)};
Person[] copyPeople = people.clone();

copyPeople[0].setAge(31);
System.out.println(people[0].getAge());  // 31 (영향 받음!)
```

## 주의사항 / 함정

### 1. Cloneable 미구현 시 예외

```java
class NotCloneable {
    // Cloneable 구현 안함
    
    @Override
    public NotCloneable clone() throws CloneNotSupportedException {
        return (NotCloneable) super.clone();
    }
}

// ❌ CloneNotSupportedException 발생
NotCloneable obj = new NotCloneable();
NotCloneable copy = obj.clone();  // 예외 발생!
```

### 2. final 필드 문제

```java
class ImmutablePerson implements Cloneable {
    private final String name;
    private final List<String> hobbies;  // final + 가변 객체
    
    @Override
    public ImmutablePerson clone() {
        try {
            ImmutablePerson cloned = (ImmutablePerson) super.clone();
            // ❌ final 필드는 재할당 불가능!
            // cloned.hobbies = new ArrayList<>(this.hobbies);  // 컴파일 에러
            return cloned;
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}
```

**해결책**: 복사 생성자 사용
```java
class ImmutablePerson {
    private final String name;
    private final List<String> hobbies;
    
    public ImmutablePerson(ImmutablePerson other) {
        this.name = other.name;
        this.hobbies = new ArrayList<>(other.hobbies);  // 가능
    }
}
```

### 3. 상속 관계에서의 문제

```java
class Animal implements Cloneable {
    private String species;
    
    @Override
    public Animal clone() {
        try {
            return (Animal) super.clone();
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}

class Dog extends Animal {
    private String breed;
    
    @Override
    public Dog clone() {
        // ⚠️ 부모의 clone()이 Dog 타입을 반환하지 않음
        return (Dog) super.clone();  // ClassCastException 위험
    }
}
```

### 4. 생성자를 거치지 않음

```java
class ValidatedPerson implements Cloneable {
    private String email;
    
    public ValidatedPerson(String email) {
        if (!isValidEmail(email)) {
            throw new IllegalArgumentException("Invalid email");
        }
        this.email = email;
    }
    
    @Override
    public ValidatedPerson clone() {
        try {
            // ⚠️ 생성자의 유효성 검사를 거치지 않음!
            return (ValidatedPerson) super.clone();
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}
```

### 5. 스레드 안전성

```java
class Counter implements Cloneable {
    private int count;
    
    public synchronized void increment() {
        count++;
    }
    
    @Override
    public Counter clone() {
        try {
            // ⚠️ clone된 객체는 동기화 상태가 복사되지 않음
            return (Counter) super.clone();
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}
```

## 관련 개념
- [[Java-Object-equals와hashCode]]
- [[Java-불변객체]]
- [[Java-디자인패턴-프로토타입]]
- [[Java-직렬화]]

## 면접 질문
1. 얕은 복사와 깊은 복사의 차이점은 무엇인가요?
2. clone() 대신 복사 생성자나 정적 팩토리 메서드를 권장하는 이유는?

## 참고 자료
- Effective Java 3/E - Item 13 (clone 재정의는 주의해서 진행하라)
- Java API Documentation - Object.clone()
- Java API Documentation - Cloneable interface