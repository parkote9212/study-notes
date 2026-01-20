---
tags: interview, java
created: 2026-01-17
difficulty: 최상
---

# Java 기본 API (면접 Q&A)

## 질문 1
> String이 불변 객체인 이유는?

## 핵심 답변 (3줄)
1. **보안성** - 값이 변하지 않아 암호화된 비밀번호 같은 민감한 데이터 안전
2. **메모리 효율** - String Pool에서 같은 문자열 재사용으로 메모리 절약
3. **스레드 안전** - 동기화 없이 여러 스레드에서 안전하게 공유 가능

## 상세 설명

String이 불변으로 설계된 이유는 다음과 같습니다:

1. **보안성**: 비밀번호나 암호화된 데이터 같은 민감한 정보를 String으로 저장할 때, 누군가가 값을 변경할 수 없도록 보장합니다. 만약 String이 가변이었다면 메모리의 비밀번호 값을 임의로 변경할 수 있는 보안 위험이 발생합니다.

2. **String Pool - 메모리 효율성**: JVM은 String Pool이라는 메모리 영역을 관리합니다. 같은 문자열 리터럴이 여러 번 생성될 때, 하나의 String 객체를 재사용합니다. 이것이 가능한 이유는 String이 불변이므로 여러 참조가 같은 객체를 안전하게 공유할 수 있기 때문입니다.

3. **스레드 안전성**: 불변 객체는 여러 스레드가 동시에 접근해도 값이 변하지 않으므로 동기화(synchronization)가 불필요합니다. 만약 String이 가변이었다면, HashMap이나 ConcurrentHashMap 같은 스레드 안전 컬렉션에서도 String을 키로 사용할 때 동기화를 고려해야 합니다.

4. **해시코드 캐싱**: 불변이므로 한 번 계산한 hashCode를 재사용할 수 있습니다.

## 코드 예시
```java
String s1 = "Hello";
String s2 = "Hello";
System.out.println(s1 == s2);  // true (같은 객체 참조)

String s3 = new String("Hello");
System.out.println(s1 == s3);  // false (새로운 객체)

// String은 불변이므로
s1 = s1 + " World";  // 새 String 객체 생성, s1 참조 변경
// 기존 "Hello" 객체는 변경되지 않음
```

## 꼬리 질문 예상
- "그럼 StringBuffer와 StringBuilder는 뭐가 다르나요?" → StringBuffer는 스레드 안전하고, StringBuilder는 단일 스레드에서 더 빠릅니다.
- "String을 + 로 연결하면 성능이 떨어진다는데?" → 매번 새 String 객체가 생성되므로 O(n²) 시간복잡도가 발생합니다.

## 참고
- [[Java-기본-API-완벽-가이드]]
- Java String documentation

---

## 질문 2
> equals()만 재정의하고 hashCode()를 하지 않으면?

## 핵심 답변 (3줄)
1. **HashMap/HashSet에서 찾을 수 없음** - hashCode()로 먼저 버킷 위치를 찾기 때문
2. **equals() 재정의 계약 위반** - equals()가 같으면 hashCode()도 같아야 함
3. **버그 발생** - 논리적으로 같은 객체가 다르게 처리됨

## 상세 설명

HashMap과 HashSet 같은 해시 기반 컬렉션의 동작 원리를 이해하면 명확합니다:

**해시 기반 컬렉션 검색 프로세스**:
1. `hashCode()`를 호출하여 객체가 저장될 버킷의 위치 계산
2. 해당 버킷 내에서 `equals()`를 사용하여 실제 객체 비교
3. equals()가 true인 객체를 반환

따라서 equals()만 재정의하고 hashCode()를 하지 않으면:
- 두 객체가 equals() 기준으로 같더라도
- hashCode()가 다르면 다른 버킷에 저장됨
- 결과적으로 찾을 수 없음

**Java 계약**:
- `equals(a, b) == true`이면 `hashCode(a) == hashCode(b)`여야 함
- 역은 성립하지 않음 (다른 해시코드가 같은 객체일 수 있음 - 충돌)

## 코드 예시
```java
@Override
public boolean equals(Object obj) {  // ✅ 재정의
    if (!(obj instanceof User)) return false;
    User other = (User) obj;
    return this.id.equals(other.id);
}

// ❌ hashCode()를 재정의하지 않음
public int hashCode() {
    return super.hashCode();  // Object의 기본 구현 (주소 기반)
}

// 사용하면
Map<User, String> map = new HashMap<>();
User u1 = new User(1L);
map.put(u1, "data");

User u2 = new User(1L);
map.get(u2);  // null 반환! (u1과 u2는 equals()로 같지만 hashCode()는 다름)
```

## 꼬리 질문 예상
- "역은 성립하나요?" → 아니요, 다른 객체가 같은 해시코드를 가질 수 있습니다(충돌).
- "hashCode()만 재정의하면?" → 더 위험합니다. equals()가 다른데 hashCode()가 같으면 비교가 제대로 되지 않습니다.

## 참고
- [[Java-기본-API-완벽-가이드]]
- hashCode() vs equals() contract

---

## 질문 3
> String vs StringBuilder 언제 뭘 쓰나요?

## 핵심 답변 (3줄)
1. **String** - 문자열이 변경되지 않을 때 (불변성, 스레드 안전)
2. **StringBuilder** - 루프나 반복적인 연결 (성능 O(n))
3. **StringBuffer** - 멀티스레드 환경 (스레드 안전, 하지만 대부분 StringBuilder로 충분)

## 상세 설명

성능 관점에서의 차이:

**String 연결의 문제점 - O(n²) 시간복잡도**:
```
result = ""           // 길이 0
result += "a"         // 새 String 생성, 길이 1
result += "b"         // 새 String 생성, 길이 2
result += "c"         // 새 String 생성, 길이 3
...
// n번 반복 시 총 연산: 0 + 1 + 2 + ... + n = O(n²)
```

**StringBuilder의 효율성 - O(n) 시간복잡도**:
```
StringBuilder sb = new StringBuilder();
sb.append("a");  // 내부 char[] 배열에 추가
sb.append("b");  // 같은 배열에 추가
sb.append("c");  // 같은 배열에 추가
// 배열이 가득 차면 크기를 2배로 늘림 (amortized O(1))
```

**실제 성능 비교**:
- 10,000번 연결: String은 약 수초, StringBuilder는 1ms 이하

**스레드 안전성**:
- **StringBuilder**: 동기화되지 않음, 빠르지만 단일 스레드에서만 사용
- **StringBuffer**: 모든 메서드가 동기화됨, 느리지만 멀티스레드 안전

실제로는 대부분 멀티스레드 환경에서도 StringBuilder를 로컬 변수로 사용하므로 StringBuffer는 거의 사용되지 않습니다.

## 코드 예시
```java
// ❌ String 연결 (성능 나쁨)
String result = "";
for (int i = 0; i < 10000; i++) {
    result += i;  // 매번 새 객체 생성
}

// ✅ StringBuilder 사용 (성능 좋음)
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);
}
String result = sb.toString();
```

## 꼬리 질문 예상
- "StringBuilder는 스레드 안전하지 않으면 왜 사용하나요?" → 대부분의 경우 로컬 변수로 단일 스레드에서만 접근하기 때문입니다.
- "StringBuffer는 언제 쓰나요?" → 요즘에는 거의 사용하지 않습니다. 성능 때문에 StringBuilder가 더 낫고, 스레드 안전이 필요하면 다른 방식을 사용합니다.

## 참고
- [[Java-기본-API-완벽-가이드]]
- String concatenation performance

---

## 질문 4
> Date 대신 LocalDateTime을 써야 하는 이유는?

## 핵심 답변 (3줄)
1. **불변성** - Date는 가변 (setMonth() 호출 가능), LocalDateTime은 불변
2. **명확한 API** - Date는 복잡하고 직관적이지 않음, LocalDateTime은 명확함
3. **타임존 처리** - ZonedDateTime으로 명시적 타임존 관리 가능

## 상세 설명

Java의 날짜/시간 API는 역사적으로 여러 버전을 거쳐 발전했습니다:

**Date의 문제점** (Java 1.0):
1. **가변성**: `date.setMonth(5)`로 값을 변경할 수 있어서 멀티스레드 환경에서 위험
2. **혼란스러운 API**:
   - Month는 0부터 11 (5월은 4)
   - Year는 1900부터의 오프셋
   - `getDay()`는 요일을 반환하는데 메서드명이 명확하지 않음
3. **타임존 처리 미흡**: 타임존 정보가 제한적

**Calendar의 문제점** (Java 1.1):
1. 복잡한 API
2. 여전히 가변 객체
3. 스레드 불안전

**java.time의 장점** (Java 8+):
1. **불변성**: 모든 클래스가 불변이므로 스레드 안전
2. **명확한 API**:
   - `LocalDate.of(2025, 3, 15)` - 직관적
   - `LocalTime.of(14, 30)` - 명확함
   - Month는 1부터 12 (자연스러움)
3. **타임존 처리**: `ZonedDateTime`으로 명시적 관리
4. **함수형 API**: 체인 가능한 메서드들

**SimpleDateFormat 문제**:
- Date와 함께 사용되는 SimpleDateFormat은 스레드 불안전
- java.time의 DateTimeFormatter는 불변이므로 스레드 안전

## 코드 예시
```java
// ❌ Old (Date)
Date date = new Date();
date.setMonth(5);  // 가변! 위험!
SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");  // 스레드 불안전

// ✅ New (java.time)
LocalDate date = LocalDate.now();
LocalDate newDate = date.plusMonths(1);  // 새 객체 반환, 불변
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");  // 불변, 스레드 안전

// 타임존 처리
ZonedDateTime seoulTime = ZonedDateTime.now(ZoneId.of("Asia/Seoul"));
ZonedDateTime nyTime = seoulTime.withZoneSameInstant(ZoneId.of("America/New_York"));
```

## 꼬리 질문 예상
- "Legacy 코드에서 Date를 쓸 수밖에 없으면?" → `Date.toInstant()`, `Instant.atZone()`로 변환 가능
- "Joda-Time은?" → java.time이 Joda-Time에 기반하여 만들어졌으므로 java.time을 사용하세요.

## 참고
- [[Java-기본-API-완벽-가이드]]
- Why Java 8 java.time
