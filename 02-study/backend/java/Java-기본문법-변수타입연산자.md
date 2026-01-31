---
tags:
  - study
  - java
  - basic
created: 2026-01-31
---

# Java 기본문법 - 변수, 타입, 연산자

## 한 줄 요약
> Java의 기본 자료형, 변수 선언, 타입 변환, 연산자를 이해하고 실무에서 안전하게 사용

## 상세 설명

### 변수와 자료형

**기본 타입 (Primitive Type)** - 8가지
```
정수형: byte(1), short(2), int(4), long(8)
실수형: float(4), double(8)
문자형: char(2)
논리형: boolean(1)
```

**참조 타입 (Reference Type)**
- String, 배열, 클래스, 인터페이스
- Heap 메모리에 저장, 변수는 주소값 보관

### 타입 변환

**자동 형변환 (Promotion)**
```
byte → short → int → long → float → double
         char → int
```

**강제 형변환 (Casting)**
- 큰 타입 → 작은 타입 변환 시 필요
- 데이터 손실 가능성 주의

### 연산자 우선순위
1. 단항: ++, --, !, ~
2. 산술: *, /, % → +, -
3. 비교: <, >, <=, >=, ==, !=
4. 논리: &&, ||
5. 삼항: ? :
6. 대입: =, +=, -=

## 코드 예시

```java
public class BasicSyntaxExample {
    public static void main(String[] args) {
        // 1. 변수 선언과 초기화
        int age = 25;
        double price = 19.99;
        char grade = 'A';
        boolean isActive = true;
        String name = "박철수";
        
        // 2. 자동 형변환
        int intNum = 100;
        long longNum = intNum;
        double doubleNum = intNum;
        
        // 3. 강제 형변환
        double pi = 3.14159;
        int intPi = (int) pi;  // 3
        
        // 4. 연산자 사용
        int a = 10, b = 3;
        System.out.println(a + b);  // 13
        System.out.println(a / b);  // 3
        System.out.println(a % b);  // 1
        
        // 5. String 비교 (실무 주의)
        String str1 = "Hello";
        String str2 = new String("Hello");
        System.out.println(str1 == str2);        // false
        System.out.println(str1.equals(str2));   // true ✅
    }
}
```

## 주의사항 / 함정

### 1. 정수 나눗셈
```java
int result = 5 / 2;  // 2 (정수)
double result = (double)5 / 2;  // 2.5 ✅
```

### 2. Long 리터럴
```java
long bigNum = 2147483648L;  // L 필수
```

### 3. String ==는 주소 비교
```java
if (s1.equals(s2)) { }  // ✅ 값 비교
```

## 관련 개념
- [[Java-제어문-배열-String]]
- [[Java-클래스-객체지향기초]]

## 면접 질문
1. int와 Integer의 차이점은?
2. == 연산자와 equals() 메서드의 차이는?
3. 오버플로우를 방지하는 방법은?

## 참고 자료
- Java Language Specification - Primitive Types
