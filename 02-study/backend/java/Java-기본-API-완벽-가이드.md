---
tags:
  - study
  - java
  - standard-api
  - 불변성
  - 캐싱
created: 2026-01-17
difficulty: 상
---
# Java 기본 API 완벽 가이드 (Object, String, 날짜)

🏷️기술 카테고리: Java, Standard API
💡핵심키워드: #불변성, #캐싱
💼 면접 빈출도: 최상

# 1. Abstract: 핵심 요약

자바 기본 API는 모든 객체의 조상인 `Object`, 불변의 특성을 가진 `String`, 그리고 정확한 시점을 다루는 `java.time` 패키지입니다. 메모리 효율성과 데이터 정합성을 확보하는 개발자의 기본기입니다.

**핵심 원칙**:
- Object: 모든 클래스의 최상위 부모 클래스
- String: 불변(Immutable) 객체로 안전한 공유 가능
- java.time: Java 8+의 현대적 날짜/시간 API

---

# 2. Technical Deep Dive: Object 클래스

## 2.1 핵심 메서드

**1. equals() - 논리적 동등성 비교**

```java
// 기본 구현 (Object)
public boolean equals(Object obj) {
    return (this == obj);  // 주소값 비교
}

// 올바른 재정의 (Member 클래스)
@Override
public boolean equals(Object obj) {
    if (this == obj) return true;
    if (!(obj instanceof Member)) return false;
    Member other = (Member) obj;
    return this.id.equals(other.id);  // ID로 비교
}
```

**2. hashCode() - 해시값 반환**

```java
// equals()를 재정의하면 hashCode()도 함께 재정의 필수!
@Override
public int hashCode() {
    return Objects.hash(id);  // Java 7+
}
```

⚠️ **중요**: equals()와 hashCode()는 항상 함께 재정의해야 합니다!
- HashMap, HashSet 등에서 객체를 올바르게 찾으려면 필수
- equals()가 true면 hashCode()도 같아야 함

**3. toString() - 객체의 문자열 표현**

```java
// 기본 구현 (클래스명@해시코드)
public String toString() {
    return getClass().getName() + "@" + 
           Integer.toHexString(hashCode());
}

// 유용한 재정의
@Override
public String toString() {
    return "Member{id=" + id + ", name=" + name + "}";
}
```

---

# 3. String의 불변성

## 3.1 왜 String은 불변(Immutable)인가?

**1. 보안성**
```java
String password = "secret123";
// password는 절대 변경되지 않음
// 새 String 객체가 생성될 뿐
```

**2. String Pool (메모리 효율)**
```java
String s1 = "Hello";  // String Pool에 저장
String s2 = "Hello";  // 같은 객체 참조
System.out.println(s1 == s2);  // true

String s3 = new String("Hello");  // Heap에 새로 생성
System.out.println(s1 == s3);  // false
```

**3. 스레드 안전성**
- 여러 스레드가 동시에 접근해도 안전
- 값이 변하지 않으므로 동기화 불필요

---

## 3.2 String vs StringBuilder vs StringBuffer

```java
// ❌ Bad - 루프에서 String 연결
String result = "";
for (int i = 0; i < 10000; i++) {
    result += i;  // 매번 새 객체 생성! O(n²)
}

// ✅ Good - StringBuilder 사용
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);  // 같은 객체에 추가! O(n)
}
String result = sb.toString();
```

| 클래스 | 가변성 | 스레드 안전 | 성능 | 사용 시기 |
| --- | --- | --- | --- | --- |
| **String** | 불변 | 안전 | 느림 | 변경이 거의 없을 때 |
| **StringBuilder** | 가변 | 불안전 | 빠름 | 단일 스레드 문자열 연산 |
| **StringBuffer** | 가변 | 안전 | 중간 | 멀티 스레드 환경 |

---

# 4. java.time 패키지 (Java 8+)

## 4.1 왜 Date/Calendar 대신 java.time을 쓰나?

**기존 API의 문제점**:
- Date: 가변 객체 (스레드 불안전)
- Calendar: 복잡한 API
- Month가 0부터 시작 (혼란)

**java.time의 장점**:
- 불변 객체 (스레드 안전)
- 명확한 API
- 타임존 처리 개선

## 4.2 주요 클래스

```java
// 1. LocalDate - 날짜만
LocalDate date = LocalDate.now();
LocalDate birthday = LocalDate.of(1990, 5, 15);

// 2. LocalTime - 시간만
LocalTime time = LocalTime.now();
LocalTime meetingTime = LocalTime.of(14, 30);

// 3. LocalDateTime - 날짜 + 시간
LocalDateTime now = LocalDateTime.now();
LocalDateTime event = LocalDateTime.of(2025, 3, 15, 10, 30);

// 4. ZonedDateTime - 타임존 포함
ZonedDateTime seoul = ZonedDateTime.now(ZoneId.of("Asia/Seoul"));
ZonedDateTime ny = ZonedDateTime.now(ZoneId.of("America/New_York"));

// 5. Duration - 시간 간격
Duration duration = Duration.between(time1, time2);
long seconds = duration.getSeconds();

// 6. Period - 날짜 간격
Period period = Period.between(date1, date2);
int days = period.getDays();
```

---

# 5. 실무 팁

## String 성능 최적화
- 루프에서 문자열 연결: StringBuilder 사용
- 멀티스레드 환경: StringBuffer 사용 (다만 대부분 StringBuilder로 충분)
- 고정된 문자열: String 사용 (String Pool 활용)

## java.time 활용
```java
// 현재 시간 기준 계산
LocalDate tomorrow = LocalDate.now().plusDays(1);
LocalDate nextMonth = LocalDate.now().plusMonths(1);

// 특정 시점 기준
LocalDate deadline = LocalDate.of(2026, 12, 31);
long daysUntil = ChronoUnit.DAYS.between(LocalDate.now(), deadline);

// 타임존 변환
ZonedDateTime utc = ZonedDateTime.now(ZoneId.of("UTC"));
ZonedDateTime kst = utc.withZoneSameInstant(ZoneId.of("Asia/Seoul"));
```

---

**작성일**: 2026-01-17  
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
