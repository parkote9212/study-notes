---
tags:
  - study
  - java
  - object
  - equals
  - hashcode
created: 2025-02-02
---

# Java Object equals와 hashCode

## 한 줄 요약
> 객체 동등성 비교와 해시 기반 컬렉션 사용을 위한 필수 메서드 쌍

## 상세 설명

### equals() 메서드

`equals()`는 두 객체가 논리적으로 동등한지 비교하는 메서드입니다. Object 클래스의 기본 구현은 `==` 연산자와 동일하게 참조 비교만 수행하므로, 대부분의 경우 오버라이딩이 필요합니다.

**equals() 규약 (Contract)**
1. **반사성(Reflexive)**: `x.equals(x)`는 항상 true
2. **대칭성(Symmetric)**: `x.equals(y)`가 true면 `y.equals(x)`도 true
3. **추이성(Transitive)**: `x.equals(y)`와 `y.equals(z)`가 true면 `x.equals(z)`도 true
4. **일관성(Consistent)**: 객체가 변경되지 않으면 항상 같은 결과 반환
5. **null 비교**: `x.equals(null)`은 항상 false

### hashCode() 메서드

`hashCode()`는 객체의 해시 코드 값을 반환합니다. HashMap, HashSet 등 해시 기반 컬렉션에서 객체를 빠르게 검색하기 위해 사용됩니다.

**hashCode() 규약**
1. **일관성**: 객체가 변경되지 않으면 항상 같은 해시 코드 반환
2. **equals-hashCode 일치**: `equals()`가 true인 두 객체는 반드시 같은 hashCode 반환
3. **권장사항**: `equals()`가 false인 객체는 다른 hashCode를 반환하는 것이 성능에 유리 (필수 아님)

### equals()와 hashCode()를 함께 오버라이딩해야 하는 이유

HashMap, HashSet 같은 컬렉션은 다음 순서로 객체를 비교합니다:
1. hashCode() 비교 → 다르면 다른 객체로 판단
2. hashCode()가 같으면 → equals()로 최종 확인

따라서 equals()만 오버라이딩하고 hashCode()를 오버라이딩하지 않으면, 논리적으로 같은 객체가 해시 컬렉션에서 다른 객체로 취급됩니다.

## 코드 예시

### 잘못된 예시 (equals만 오버라이딩)

```java
class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        Person person = (Person) obj;
        return age == person.age && 
               Objects.equals(name, person.name);
    }
    
    // hashCode() 오버라이딩 안함 - 문제 발생!
}

// 사용 예시
Set<Person> set = new HashSet<>();
Person p1 = new Person("홍길동", 30);
Person p2 = new Person("홍길동", 30);

set.add(p1);
set.add(p2);

System.out.println(set.size());  // 2 출력 (기대: 1)
System.out.println(p1.equals(p2));  // true
```

### 올바른 예시 (equals + hashCode 모두 오버라이딩)

```java
class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
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

// 사용 예시
Set<Person> set = new HashSet<>();
Person p1 = new Person("홍길동", 30);
Person p2 = new Person("홍길동", 30);

set.add(p1);
set.add(p2);

System.out.println(set.size());  // 1 출력 (정상)
System.out.println(set.contains(p1));  // true
System.out.println(set.contains(p2));  // true
```

### equals() 구현 패턴

```java
@Override
public boolean equals(Object obj) {
    // 1. 참조 비교 (성능 최적화)
    if (this == obj) return true;
    
    // 2. null 체크
    if (obj == null) return false;
    
    // 3. 타입 체크
    if (getClass() != obj.getClass()) return false;
    
    // 4. 타입 캐스팅
    Person other = (Person) obj;
    
    // 5. 필드 비교
    return age == other.age && 
           Objects.equals(name, other.name);
}
```

### hashCode() 구현 방법

**방법 1: Objects.hash() 사용 (권장)**
```java
@Override
public int hashCode() {
    return Objects.hash(name, age, email);
}
```

**방법 2: 직접 계산 (성능 최적화가 필요한 경우)**
```java
@Override
public int hashCode() {
    int result = name != null ? name.hashCode() : 0;
    result = 31 * result + age;
    result = 31 * result + (email != null ? email.hashCode() : 0);
    return result;
}
```

### IDE 자동 생성 활용

```java
class Product {
    private String id;
    private String name;
    private int price;
    
    // IntelliJ: Alt + Insert → equals() and hashCode()
    // Eclipse: Source → Generate hashCode() and equals()
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Product product = (Product) o;
        return price == product.price && 
               Objects.equals(id, product.id) && 
               Objects.equals(name, product.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(id, name, price);
    }
}
```

### 불변 객체에서의 hashCode 캐싱

```java
class ImmutablePerson {
    private final String name;
    private final int age;
    private int hashCode;  // 캐싱용
    
    public ImmutablePerson(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public int hashCode() {
        int result = hashCode;
        if (result == 0) {
            result = Objects.hash(name, age);
            hashCode = result;
        }
        return result;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        ImmutablePerson that = (ImmutablePerson) obj;
        return age == that.age && Objects.equals(name, that.name);
    }
}
```

## 주의사항 / 함정

### 1. equals() 오버라이딩 시 매개변수 타입 실수

```java
// ❌ 잘못된 예시 - 오버라이딩이 아니라 오버로딩
public boolean equals(Person other) {
    return this.name.equals(other.name);
}

// ✅ 올바른 예시 - 반드시 Object 타입
@Override  // 컴파일러가 검증
public boolean equals(Object obj) {
    if (!(obj instanceof Person)) return false;
    Person other = (Person) obj;
    return this.name.equals(other.name);
}
```

### 2. null 필드 처리 누락

```java
// ❌ NullPointerException 발생 가능
@Override
public boolean equals(Object obj) {
    Person other = (Person) obj;
    return name.equals(other.name);  // name이 null이면 예외
}

// ✅ Objects.equals() 사용
@Override
public boolean equals(Object obj) {
    Person other = (Person) obj;
    return Objects.equals(name, other.name);  // null 안전
}
```

### 3. mutable 필드 사용 시 문제

```java
class MutableKey {
    private String value;
    
    public void setValue(String value) {
        this.value = value;
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(value);
    }
}

// 문제 상황
Map<MutableKey, String> map = new HashMap<>();
MutableKey key = new MutableKey();
key.setValue("original");

map.put(key, "data");
System.out.println(map.get(key));  // "data" 출력

key.setValue("changed");  // hashCode 변경됨!
System.out.println(map.get(key));  // null 출력 - 찾을 수 없음!
```

**해결책**: HashMap/HashSet의 키는 불변 객체 사용 권장

### 4. 상속 관계에서의 equals() 구현

```java
class Point {
    private int x, y;
    
    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof Point)) return false;
        Point p = (Point) obj;
        return x == p.x && y == p.y;
    }
}

class ColorPoint extends Point {
    private String color;
    
    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof ColorPoint)) return false;
        ColorPoint cp = (ColorPoint) obj;
        return super.equals(obj) && color.equals(cp.color);
    }
}

// 대칭성 위반!
Point p = new Point(1, 2);
ColorPoint cp = new ColorPoint(1, 2, "RED");

System.out.println(p.equals(cp));   // true
System.out.println(cp.equals(p));   // false - 대칭성 위반!
```

**해결책**: 상속보다는 컴포지션 사용 권장

### 5. float/double 비교 시 주의

```java
class Measurement {
    private double value;
    
    @Override
    public boolean equals(Object obj) {
        Measurement other = (Measurement) obj;
        // ❌ 부동소수점 오차로 인한 문제
        return value == other.value;
        
        // ✅ Double.compare() 사용
        return Double.compare(value, other.value) == 0;
    }
    
    @Override
    public int hashCode() {
        // ✅ Double.hashCode() 사용
        return Double.hashCode(value);
    }
}
```

## 관련 개념
- [[Java-Object-toString]]
- [[Java-컬렉션-HashMap]]
- [[Java-컬렉션-HashSet]]
- [[Java-불변객체]]

## 면접 질문
1. equals()와 hashCode()를 함께 오버라이딩해야 하는 이유는 무엇인가요?
2. hashCode()가 같은데 equals()가 false인 경우가 있을 수 있나요? 반대의 경우는요?

## 참고 자료
- Effective Java 3/E - Item 10, 11 (equals, hashCode)
- Java API Documentation - Object class