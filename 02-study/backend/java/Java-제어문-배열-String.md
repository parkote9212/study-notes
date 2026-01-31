---
tags:
  - study
  - java
  - basic
created: 2026-01-31
---

# Java 제어문, 배열, String

## 한 줄 요약
> 조건문/반복문으로 로직 제어, 배열로 데이터 집합 관리, String 특성 이해

## 상세 설명

### 조건문

**if-else**
```java
if (조건1) {
    // 조건1이 true
} else if (조건2) {
    // 조건2가 true
} else {
    // 모두 false
}
```

**switch**
```java
switch (변수) {
    case 값1:
        // 실행
        break;
    case 값2:
        // 실행
        break;
    default:
        // 일치하는 case 없을 때
}
```

**Java 14+ Switch Expression**
```java
String result = switch (day) {
    case "MON", "TUE" -> "평일";
    case "SAT", "SUN" -> "주말";
    default -> "기타";
};
```

### 반복문

**for**
```java
for (int i = 0; i < 10; i++) {
    // 10번 반복
}

// 향상된 for (for-each)
for (String item : array) {
    // 배열/컬렉션 순회
}
```

**while / do-while**
```java
while (조건) {
    // 조건이 true인 동안
}

do {
    // 최소 1번 실행
} while (조건);
```

**break / continue**
- break: 반복문 즉시 종료
- continue: 현재 반복 건너뛰고 다음 반복

### 배열 (Array)

**특징**
- 같은 타입의 데이터를 연속된 메모리에 저장
- 크기 고정 (생성 후 변경 불가)
- 인덱스 0부터 시작

**선언과 초기화**
```java
int[] arr = new int[5];              // 크기 5, 기본값 0
int[] arr = {1, 2, 3, 4, 5};        // 선언과 동시 초기화
int[] arr = new int[]{1, 2, 3};     // 명시적 초기화

// 2차원 배열
int[][] matrix = new int[3][4];     // 3행 4열
int[][] matrix = {{1,2}, {3,4}};
```

### String

**불변성 (Immutable)**
- String 객체는 한 번 생성되면 내용 변경 불가
- 변경 시 새로운 객체 생성
- String Pool에서 리터럴 재사용

**주요 메서드**
```java
length()           // 문자열 길이
charAt(index)      // 특정 위치 문자
substring(start, end) // 부분 문자열
indexOf(str)       // 문자열 위치 찾기
contains(str)      // 포함 여부
replace(old, new)  // 문자열 치환
split(regex)       // 분리
trim()             // 공백 제거
equals(str)        // 값 비교
```

## 코드 예시

```java
public class ControlFlowExample {
    public static void main(String[] args) {
        // 1. 조건문
        int score = 85;
        
        if (score >= 90) {
            System.out.println("A");
        } else if (score >= 80) {
            System.out.println("B");  // 출력
        } else {
            System.out.println("C");
        }
        
        // 2. Switch Expression (Java 14+)
        String grade = switch (score / 10) {
            case 10, 9 -> "A";
            case 8 -> "B";
            case 7 -> "C";
            default -> "F";
        };
        
        // 3. 반복문
        for (int i = 0; i < 5; i++) {
            System.out.print(i + " ");  // 0 1 2 3 4
        }
        
        // 4. 배열 선언과 사용
        int[] numbers = {10, 20, 30, 40, 50};
        
        System.out.println(numbers.length);    // 5
        System.out.println(numbers[0]);        // 10
        
        // 향상된 for문
        for (int num : numbers) {
            System.out.print(num + " ");
        }
        
        // 5. 2차원 배열
        int[][] matrix = {
            {1, 2, 3},
            {4, 5, 6}
        };
        
        for (int i = 0; i < matrix.length; i++) {
            for (int j = 0; j < matrix[i].length; j++) {
                System.out.print(matrix[i][j] + " ");
            }
            System.out.println();
        }
        
        // 6. String 활용
        String text = "Hello Java World";
        
        System.out.println(text.length());           // 16
        System.out.println(text.charAt(0));          // H
        System.out.println(text.substring(6, 10));   // Java
        System.out.println(text.indexOf("Java"));    // 6
        System.out.println(text.contains("Java"));   // true
        System.out.println(text.replace("Java", "Python")); 
        
        String[] words = text.split(" ");
        for (String word : words) {
            System.out.println(word);  // Hello, Java, World
        }
        
        // 7. String 불변성
        String str1 = "Hello";
        String str2 = str1;         // 같은 객체 참조
        str1 = str1 + " World";     // 새 객체 생성
        
        System.out.println(str1);   // Hello World
        System.out.println(str2);   // Hello (원본 변경 안됨)
        
        // 8. StringBuilder (가변)
        StringBuilder sb = new StringBuilder("Hello");
        sb.append(" World");        // 같은 객체에 추가
        System.out.println(sb.toString());  // Hello World
    }
}
```

## 주의사항 / 함정

### 1. 배열 인덱스 범위
```java
int[] arr = new int[5];
System.out.println(arr[5]);  // ❌ ArrayIndexOutOfBoundsException
System.out.println(arr[4]);  // ✅ 마지막 요소
```

### 2. 배열 기본값
```java
int[] nums = new int[3];      // {0, 0, 0}
boolean[] flags = new boolean[3];  // {false, false, false}
String[] strs = new String[3];     // {null, null, null}
```

### 3. String 연결 성능
```java
// ❌ 반복문에서 + 사용 (매번 새 객체)
String result = "";
for (int i = 0; i < 1000; i++) {
    result += i;  // 1000개 객체 생성
}

// ✅ StringBuilder 사용
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i);  // 하나의 객체만
}
String result = sb.toString();
```

### 4. String 비교
```java
String s1 = "hello";
String s2 = new String("hello");

if (s1 == s2) { }          // ❌ 주소 비교
if (s1.equals(s2)) { }     // ✅ 값 비교
```

### 5. null 체크
```java
String str = null;
System.out.println(str.length());  // ❌ NullPointerException

if (str != null && str.length() > 0) {  // ✅
    System.out.println(str);
}
```

### 6. switch의 break 누락
```java
int day = 1;
switch (day) {
    case 1:
        System.out.println("월요일");
        // break 없음
    case 2:
        System.out.println("화요일");  // 함께 출력됨
        break;
}

// Java 14+ Switch Expression은 break 불필요
```

### 7. 배열 복사
```java
int[] arr1 = {1, 2, 3};
int[] arr2 = arr1;         // ❌ 얕은 복사 (같은 주소)
arr2[0] = 99;
System.out.println(arr1[0]);  // 99 (원본도 변경)

int[] arr3 = arr1.clone();    // ✅ 깊은 복사
int[] arr4 = Arrays.copyOf(arr1, arr1.length);  // ✅
```

## 관련 개념
- [[Java-기본문법-변수타입연산자]]
- [[Java-클래스-객체지향기초]]
- [[Java-컬렉션-프레임워크]]

## 면접 질문
1. for문과 while문의 차이점과 각각 언제 사용하나요?
2. String이 불변(Immutable)인 이유는?
3. String, StringBuilder, StringBuffer의 차이는?
4. 배열과 ArrayList의 차이점은?

## 참고 자료
- Effective Java Item 63: 문자열 연결은 느리니 주의하라
- Java String Pool 동작 원리
