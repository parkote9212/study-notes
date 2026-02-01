---
tags:
  - study
  - java
  - object
created: 2025-02-01
---

# Java Object 클래스 메서드

## 한 줄 요약
> 모든 클래스의 부모, equals/hashCode/toString 제공

## 상세 설명

### What
Object는 모든 클래스의 최상위 부모

### Why
객체 비교, 해시 컬렉션 사용, 문자열 표현

## equals()

```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;
    Person p = (Person) o;
    return age == p.age && Objects.equals(name, p.name);
}
```

**규약:** 반사성, 대칭성, 추이성, 일관성, null 처리

## hashCode()

```java
@Override
public int hashCode() {
    return Objects.hash(name, age);
}
```

**규칙:** equals() true면 hashCode() 동일

## toString()

```java
@Override
public String toString() {
    return "Person{name='" + name + "', age=" + age + "}";
}
```

## clone() vs 복사 생성자

```java
// ✅ 권장
public Person(Person other) {
    this.name = other.name;
}
```

## 코드 예시
```java
class Person {
    String name;
    int age;
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Person p = (Person) o;
        return Objects.equals(name, p.name) && age == p.age;
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}
```

## 주의사항 / 함정

1. equals 구현 시 hashCode도 필수
2. 가변 필드로 hashCode 계산 위험
3. clone() 대신 복사 생성자 사용

## 면접 질문
1. equals()와 hashCode()를 함께 구현하는 이유?
2. equals() 규약 5가지는?

## 참고 자료
- Effective Java Item 10-13