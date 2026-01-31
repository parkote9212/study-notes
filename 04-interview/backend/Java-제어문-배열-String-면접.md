---
tags:
  - interview
  - java
  - basic
created: 2026-01-31
difficulty: 하
---

# Java 제어문, 배열, String 면접

## 질문
> String이 불변(Immutable)인 이유와 장점을 설명하고, StringBuilder와의 차이점을 설명하세요.

## 핵심 답변 (3줄)
1. String은 불변 객체로 한번 생성되면 내용을 변경할 수 없으며, 변경 시 새로운 객체를 생성합니다.
2. 불변성의 장점은 ① String Pool 재사용으로 메모리 절약, ② Thread-Safe, ③ 해시코드 캐싱, ④ 보안(중요 데이터 변조 방지)입니다.
3. StringBuilder는 가변 객체로 내부 버퍼를 변경하므로 반복적인 문자열 연결 시 성능이 좋지만, Thread-Safe하지 않습니다.

## 상세 설명

### String 불변성의 이유

**1. String Pool 최적화**
- 리터럴 문자열은 Heap의 String Pool에 저장
- 같은 값은 하나의 객체만 생성하여 재사용
- 불변이기 때문에 안전하게 공유 가능

**2. Thread-Safety**
- 여러 스레드가 동시에 접근해도 안전
- 동기화 불필요 → 성능 향상

**3. 보안**
- 네트워크 연결, 파일 경로, 데이터베이스 URL 등 중요 데이터
- 불변이므로 변조 불가능

**4. 해시코드 캐싱**
- HashMap, HashSet 등에서 성능 향상
- hashCode() 한 번 계산 후 재사용

### String vs StringBuilder vs StringBuffer

| 특성 | String | StringBuilder | StringBuffer |
|-----|--------|--------------|--------------|
| 가변성 | 불변 | 가변 | 가변 |
| Thread-Safe | O | X | O |
| 성능 | 느림 | 빠름 | 중간 |
| 사용 상황 | 변경 없음 | 단일 스레드 | 멀티 스레드 |

## 코드 예시

```java
public class StringExample {
    public static void main(String[] args) {
        // 1. String 불변성
        String str1 = "Hello";
        String str2 = str1;
        str1 = str1 + " World";  // 새 객체 생성
        
        System.out.println(str1);  // Hello World
        System.out.println(str2);  // Hello (원본 유지)
        
        // 2. String Pool
        String s1 = "Java";        // Pool에 생성
        String s2 = "Java";        // Pool 재사용
        String s3 = new String("Java");  // Heap에 새 객체
        
        System.out.println(s1 == s2);  // true (같은 주소)
        System.out.println(s1 == s3);  // false (다른 주소)
        
        // 3. String 성능 문제
        long start = System.currentTimeMillis();
        String result = "";
        for (int i = 0; i < 10000; i++) {
            result += i;  // 10000개 객체 생성
        }
        long end = System.currentTimeMillis();
        System.out.println("String: " + (end - start) + "ms");  // ~500ms
        
        // 4. StringBuilder 성능
        start = System.currentTimeMillis();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 10000; i++) {
            sb.append(i);  // 내부 버퍼 수정
        }
        result = sb.toString();
        end = System.currentTimeMillis();
        System.out.println("StringBuilder: " + (end - start) + "ms");  // ~5ms
        
        // 5. 실무 사용 예시
        // JSON 만들기
        StringBuilder json = new StringBuilder();
        json.append("{")
            .append("\"name\":\"홍길동\",")
            .append("\"age\":20")
            .append("}");
        
        // SQL 동적 쿼리
        StringBuilder sql = new StringBuilder();
        sql.append("SELECT * FROM users WHERE 1=1");
        if (name != null) {
            sql.append(" AND name = '").append(name).append("'");
        }
    }
}
```

## 꼬리 질문 예상

### Q1. String + 연산자는 내부적으로 어떻게 동작하나요?
**답변:** Java 9 이전에는 컴파일러가 StringBuilder로 변환했지만, 반복문 안에서는 매번 새로운 StringBuilder를 생성했습니다. Java 9 이후부터는 invokedynamic과 StringConcatFactory를 사용하여 더 효율적으로 처리합니다. 하지만 반복문에서는 여전히 명시적으로 StringBuilder를 사용하는 것이 좋습니다.

### Q2. StringBuilder와 StringBuffer 중 어떤 것을 사용해야 하나요?
**답변:** 대부분의 경우 StringBuilder를 사용합니다. StringBuffer는 synchronized로 Thread-Safe하지만 단일 스레드 환경에서는 불필요한 오버헤드입니다. 멀티 스레드 환경에서 여러 스레드가 하나의 문자열을 공유하며 수정하는 경우에만 StringBuffer를 사용합니다.

### Q3. String.intern() 메서드는 무엇인가요?
**답변:** String Pool에 해당 문자열이 있으면 그 참조를 반환하고, 없으면 Pool에 추가 후 참조를 반환합니다. new String()으로 생성한 객체를 Pool에 넣어 메모리를 절약할 수 있지만, Pool 크기 제한과 GC 대상이 안 될 수 있어 신중히 사용해야 합니다.

### Q4. 배열과 ArrayList의 차이점은?
**답변:** 배열은 크기가 고정되고 primitive 타입 저장 가능하며 빠릅니다. ArrayList는 크기가 가변적이고 객체만 저장 가능하며, 내부적으로 배열을 사용하지만 add/remove 등 유연한 메서드를 제공합니다. 크기가 고정이면 배열, 동적으로 변하면 ArrayList를 사용합니다.

### Q5. for문과 while문은 언제 구분해서 사용하나요?
**답변:** 반복 횟수를 아는 경우 for문(배열 순회, 특정 횟수 반복), 조건에 따라 반복하는 경우 while문(사용자 입력, 파일 읽기 등)을 사용합니다. do-while은 최소 한 번은 실행이 보장되어야 할 때 사용합니다.

## 참고
- [[Java-제어문-배열-String]]
- [[Java-컬렉션-프레임워크]]
