---
tags:
  - interview
  - java
  - basic
created: 2026-01-31
difficulty: 하
---

# Java 기본문법 면접

## 질문
> Java의 기본 타입(Primitive Type)과 참조 타입(Reference Type)의 차이를 설명하고, == 연산자와 equals() 메서드의 차이를 설명하세요.

## 핵심 답변 (3줄)
1. 기본 타입은 실제 값을 Stack에 저장하고 (int, double 등 8가지), 참조 타입은 Heap의 주소를 Stack에 저장합니다.
2. == 연산자는 기본 타입은 값을 비교하지만, 참조 타입은 주소(참조)를 비교합니다.
3. equals()는 Object의 메서드로 객체의 내용(값)을 비교하며, String 같은 클래스에서 오버라이딩되어 있습니다.

## 상세 설명

### 기본 타입 vs 참조 타입

**기본 타입 (8가지)**
- 정수: byte, short, int, long
- 실수: float, double
- 문자: char
- 논리: boolean
- Stack 메모리에 실제 값 저장
- null 불가능

**참조 타입**
- 클래스, 인터페이스, 배열, String
- Heap 메모리에 객체 저장, Stack에는 주소만 저장
- null 가능
- Garbage Collection 대상

### == vs equals()

**== 연산자**
- 기본 타입: 값 비교
- 참조 타입: 주소(참조값) 비교

**equals() 메서드**
- Object의 기본 구현은 == 와 동일 (주소 비교)
- String, Integer 등은 오버라이딩하여 값 비교
- 사용자 정의 클래스는 필요시 오버라이딩 필요

## 코드 예시

```java
public class ComparisonExample {
    public static void main(String[] args) {
        // 1. 기본 타입 비교
        int a = 10;
        int b = 10;
        System.out.println(a == b);  // true (값 비교)
        
        // 2. String 비교
        String s1 = "hello";        // 리터럴 (String Pool)
        String s2 = "hello";        // 같은 Pool 참조
        String s3 = new String("hello");  // Heap에 새 객체
        
        System.out.println(s1 == s2);       // true (같은 주소)
        System.out.println(s1 == s3);       // false (다른 주소)
        System.out.println(s1.equals(s3));  // true (값 비교) ✅
        
        // 3. Wrapper 클래스 비교
        Integer i1 = 127;           // -128~127 캐싱
        Integer i2 = 127;
        Integer i3 = 128;
        Integer i4 = 128;
        
        System.out.println(i1 == i2);       // true (캐싱)
        System.out.println(i3 == i4);       // false (범위 초과)
        System.out.println(i3.equals(i4));  // true ✅
        
        // 4. 사용자 정의 클래스
        Person p1 = new Person("홍길동", 20);
        Person p2 = new Person("홍길동", 20);
        
        System.out.println(p1 == p2);       // false (다른 객체)
        System.out.println(p1.equals(p2));  // equals() 오버라이딩 여부에 따라
    }
}

class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // equals() 오버라이딩 (올바른 비교)
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

## 꼬리 질문 예상

### Q1. int와 Integer의 차이는?
**답변:** int는 기본 타입으로 Stack에 값 저장, Integer는 참조 타입(Wrapper 클래스)으로 Heap에 객체 저장합니다. Integer는 null 가능하고 컬렉션에 사용 가능하지만, 성능은 int가 더 빠릅니다. Java 5부터 Auto Boxing/Unboxing으로 자동 변환됩니다.

### Q2. String을 ==로 비교하면 안 되는 이유는?
**답변:** String은 참조 타입이므로 ==는 주소를 비교합니다. "hello" 리터럴은 String Pool에서 재사용되어 같은 주소를 가질 수 있지만, new String()은 항상 새 객체를 만듭니다. 따라서 값 비교를 원하면 반드시 equals()를 사용해야 합니다.

### Q3. equals()를 오버라이딩할 때 hashCode()도 함께 오버라이딩해야 하는 이유는?
**답변:** equals()가 true인 두 객체는 hashCode()도 같아야 한다는 계약(contract) 때문입니다. HashMap, HashSet 등 해시 기반 컬렉션은 hashCode()로 버킷을 찾고 equals()로 동등성을 판단하므로, 둘 중 하나만 오버라이딩하면 컬렉션에서 올바르게 동작하지 않습니다.

### Q4. 오버플로우가 발생하는 경우와 해결 방법은?
**답변:** 타입의 최대값을 초과하면 발생합니다 (int max + 1 = min). 해결 방법은 ① 더 큰 타입 사용 (int → long), ② BigInteger/BigDecimal 사용, ③ Math.addExact() 등 예외 발생 메서드 사용입니다.

## 참고
- [[Java-기본문법-변수타입연산자]]
- [[Java-클래스-객체지향기초]]
