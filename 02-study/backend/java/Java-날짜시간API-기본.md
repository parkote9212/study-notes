---
tags:
  - study
  - java
  - datetime
  - java-time
created: 2025-02-02
---

# Java 날짜시간API 기본

## 한 줄 요약
> Java 8에서 도입된 불변의 타입 안전한 날짜/시간 처리 API

## 상세 설명

### java.time 패키지 소개

Java 8에서 도입된 `java.time` 패키지는 기존 `Date`, `Calendar`의 문제점을 해결한 새로운 날짜/시간 API입니다.

**기존 API의 문제점**
- 가변 객체 (thread-unsafe)
- 직관적이지 않은 API (month가 0부터 시작)
- Date와 Calendar의 역할 불명확
- 타임존 처리 복잡

**java.time의 장점**
- 불변 객체 (thread-safe)
- 직관적이고 명확한 API
- 메서드 체이닝 지원
- 타임존 처리 간편
- ISO-8601 표준 준수

### 주요 클래스

1. **LocalDate** - 날짜만 (년/월/일)
2. **LocalTime** - 시간만 (시/분/초/나노초)
3. **LocalDateTime** - 날짜 + 시간
4. **ZonedDateTime** - 날짜 + 시간 + 타임존
5. **Instant** - 타임스탬프
6. **Period** - 날짜 기간
7. **Duration** - 시간 기간

## 코드 예시

### LocalDate - 날짜

```java
import java.time.LocalDate;

// 현재 날짜
LocalDate today = LocalDate.now();
System.out.println(today);  // 2025-02-02

// 특정 날짜 생성
LocalDate birthday = LocalDate.of(1990, 5, 15);
LocalDate date = LocalDate.of(2025, Month.FEBRUARY, 2);

// 날짜 파싱
LocalDate parsed = LocalDate.parse("2025-02-02");

// 필드 값 가져오기
int year = today.getYear();        // 2025
int month = today.getMonthValue(); // 2
int day = today.getDayOfMonth();   // 2
DayOfWeek dayOfWeek = today.getDayOfWeek();  // SUNDAY

// 윤년 확인
boolean isLeapYear = today.isLeapYear();
```

### LocalDate 날짜 조작

```java
LocalDate date = LocalDate.of(2025, 2, 2);

// 더하기
LocalDate nextWeek = date.plusWeeks(1);      // 2025-02-09
LocalDate nextMonth = date.plusMonths(1);    // 2025-03-02
LocalDate nextYear = date.plusYears(1);      // 2026-02-02
LocalDate after10Days = date.plusDays(10);   // 2025-02-12

// 빼기
LocalDate lastWeek = date.minusWeeks(1);     // 2025-01-26
LocalDate lastMonth = date.minusMonths(1);   // 2025-01-02

// 특정 필드 변경
LocalDate modified = date.withYear(2026);       // 2026-02-02
LocalDate firstDay = date.withDayOfMonth(1);    // 2025-02-01
LocalDate lastDay = date.withDayOfMonth(date.lengthOfMonth());  // 2025-02-28
```

### LocalDate 비교

```java
LocalDate date1 = LocalDate.of(2025, 2, 2);
LocalDate date2 = LocalDate.of(2025, 3, 1);

// 비교
boolean isBefore = date1.isBefore(date2);  // true
boolean isAfter = date1.isAfter(date2);    // false
boolean isEqual = date1.isEqual(date2);    // false

// compareTo
int comparison = date1.compareTo(date2);   // 음수 (date1이 이전)
```

### LocalTime - 시간

```java
import java.time.LocalTime;

// 현재 시간
LocalTime now = LocalTime.now();
System.out.println(now);  // 14:30:25.123456789

// 특정 시간 생성
LocalTime time1 = LocalTime.of(14, 30);           // 14:30
LocalTime time2 = LocalTime.of(14, 30, 25);       // 14:30:25
LocalTime time3 = LocalTime.of(14, 30, 25, 123);  // 14:30:25.000000123

// 시간 파싱
LocalTime parsed = LocalTime.parse("14:30:25");

// 필드 값 가져오기
int hour = now.getHour();      // 14
int minute = now.getMinute();  // 30
int second = now.getSecond();  // 25
int nano = now.getNano();      // 123456789
```

### LocalTime 시간 조작

```java
LocalTime time = LocalTime.of(14, 30, 0);

// 더하기
LocalTime after2Hours = time.plusHours(2);      // 16:30
LocalTime after30Mins = time.plusMinutes(30);   // 15:00
LocalTime after45Secs = time.plusSeconds(45);   // 14:30:45

// 빼기
LocalTime before1Hour = time.minusHours(1);     // 13:30

// 변경
LocalTime modified = time.withHour(10);         // 10:30
```

### LocalDateTime - 날짜와 시간

```java
import java.time.LocalDateTime;

// 현재 날짜와 시간
LocalDateTime now = LocalDateTime.now();
System.out.println(now);  // 2025-02-02T14:30:25

// 생성
LocalDateTime dt1 = LocalDateTime.of(2025, 2, 2, 14, 30);
LocalDateTime dt2 = LocalDateTime.of(2025, 2, 2, 14, 30, 25);

LocalDate date = LocalDate.of(2025, 2, 2);
LocalTime time = LocalTime.of(14, 30);
LocalDateTime dt3 = LocalDateTime.of(date, time);

// 파싱
LocalDateTime parsed = LocalDateTime.parse("2025-02-02T14:30:25");

// LocalDate, LocalTime 추출
LocalDate dateOnly = now.toLocalDate();
LocalTime timeOnly = now.toLocalTime();
```

### LocalDateTime 조작

```java
LocalDateTime dateTime = LocalDateTime.of(2025, 2, 2, 14, 30);

// 날짜 조작
LocalDateTime nextDay = dateTime.plusDays(1);
LocalDateTime nextMonth = dateTime.plusMonths(1);

// 시간 조작
LocalDateTime after2Hours = dateTime.plusHours(2);
LocalDateTime after30Mins = dateTime.plusMinutes(30);

// 혼합 조작
LocalDateTime future = dateTime
    .plusDays(7)
    .plusHours(3)
    .plusMinutes(30);

// 특정 필드 변경
LocalDateTime modified = dateTime
    .withYear(2026)
    .withMonth(3)
    .withDayOfMonth(15)
    .withHour(10)
    .withMinute(0)
    .withSecond(0);
```

### 실전 예시: 날짜 계산

```java
class DateCalculator {
    // D-Day 계산
    public long calculateDDay(LocalDate targetDate) {
        LocalDate today = LocalDate.now();
        return ChronoUnit.DAYS.between(today, targetDate);
    }
    
    // 나이 계산
    public int calculateAge(LocalDate birthDate) {
        LocalDate today = LocalDate.now();
        return Period.between(birthDate, today).getYears();
    }
    
    // 근무일 계산 (주말 제외)
    public long calculateWorkDays(LocalDate start, LocalDate end) {
        long totalDays = ChronoUnit.DAYS.between(start, end);
        long workDays = 0;
        
        LocalDate current = start;
        while (!current.isAfter(end)) {
            DayOfWeek day = current.getDayOfWeek();
            if (day != DayOfWeek.SATURDAY && day != DayOfWeek.SUNDAY) {
                workDays++;
            }
            current = current.plusDays(1);
        }
        
        return workDays;
    }
    
    // 월의 마지막 날
    public LocalDate getLastDayOfMonth(int year, int month) {
        return LocalDate.of(year, month, 1)
                       .with(TemporalAdjusters.lastDayOfMonth());
    }
}
```

### TemporalAdjusters 활용

```java
import java.time.temporal.TemporalAdjusters;

LocalDate date = LocalDate.of(2025, 2, 2);

// 월의 첫째 날
LocalDate firstDay = date.with(TemporalAdjusters.firstDayOfMonth());
// 2025-02-01

// 월의 마지막 날
LocalDate lastDay = date.with(TemporalAdjusters.lastDayOfMonth());
// 2025-02-28

// 다음 월요일
LocalDate nextMonday = date.with(TemporalAdjusters.next(DayOfWeek.MONDAY));

// 이번 달의 첫 번째 월요일
LocalDate firstMonday = date.with(TemporalAdjusters.firstInMonth(DayOfWeek.MONDAY));

// 이번 달의 마지막 금요일
LocalDate lastFriday = date.with(TemporalAdjusters.lastInMonth(DayOfWeek.FRIDAY));
```

### DateTimeFormatter - 포맷팅

```java
import java.time.format.DateTimeFormatter;

LocalDateTime dateTime = LocalDateTime.of(2025, 2, 2, 14, 30, 25);

// 기본 포맷터 사용
String iso = dateTime.format(DateTimeFormatter.ISO_DATE_TIME);
// 2025-02-02T14:30:25

// 커스텀 포맷
DateTimeFormatter formatter1 = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
String formatted1 = dateTime.format(formatter1);
// 2025-02-02 14:30:25

DateTimeFormatter formatter2 = DateTimeFormatter.ofPattern("yyyy년 MM월 dd일 HH시 mm분");
String formatted2 = dateTime.format(formatter2);
// 2025년 02월 02일 14시 30분

// 파싱
LocalDateTime parsed = LocalDateTime.parse(
    "2025-02-02 14:30:25",
    DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
);
```

### 자주 사용하는 패턴

```java
class DateTimePatterns {
    public static final DateTimeFormatter BASIC_DATE = 
        DateTimeFormatter.ofPattern("yyyy-MM-dd");
    
    public static final DateTimeFormatter BASIC_DATETIME = 
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    
    public static final DateTimeFormatter KOREAN_DATE = 
        DateTimeFormatter.ofPattern("yyyy년 M월 d일");
    
    public static final DateTimeFormatter TIME_ONLY = 
        DateTimeFormatter.ofPattern("HH:mm:ss");
    
    public static final DateTimeFormatter FILE_TIMESTAMP = 
        DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");
}

// 사용
LocalDateTime now = LocalDateTime.now();
String filename = "log_" + now.format(DateTimePatterns.FILE_TIMESTAMP) + ".txt";
// log_20250202_143025.txt
```

### 실전 예시: 회원가입 날짜 처리

```java
class User {
    private Long id;
    private String email;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    public User(String email) {
        this.email = email;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    public void update() {
        this.updatedAt = LocalDateTime.now();
    }
    
    public String getFormattedCreatedAt() {
        return createdAt.format(
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")
        );
    }
    
    public long getDaysSinceCreated() {
        return ChronoUnit.DAYS.between(
            createdAt.toLocalDate(),
            LocalDate.now()
        );
    }
}
```

### 실전 예시: 예약 시스템

```java
class Reservation {
    private LocalDateTime reservationTime;
    
    public boolean isWithinCancellationPeriod() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime cutoff = reservationTime.minusHours(24);
        return now.isBefore(cutoff);
    }
    
    public boolean isUpcoming() {
        LocalDateTime now = LocalDateTime.now();
        return reservationTime.isAfter(now);
    }
    
    public String getTimeUntilReservation() {
        LocalDateTime now = LocalDateTime.now();
        long hours = ChronoUnit.HOURS.between(now, reservationTime);
        long minutes = ChronoUnit.MINUTES.between(now, reservationTime) % 60;
        
        return String.format("%d시간 %d분 남음", hours, minutes);
    }
}
```

## 주의사항 / 함정

### 1. 불변 객체 이해

```java
LocalDate date = LocalDate.of(2025, 2, 2);

// ❌ 변경되지 않음
date.plusDays(1);
System.out.println(date);  // 2025-02-02 (변경 안됨!)

// ✅ 새로운 객체 반환
LocalDate newDate = date.plusDays(1);
System.out.println(newDate);  // 2025-02-03
```

### 2. null 처리

```java
// ❌ NullPointerException 위험
LocalDate date = null;
// date.plusDays(1);  // NPE

// ✅ Optional 사용
Optional<LocalDate> optionalDate = Optional.ofNullable(getDate());
LocalDate result = optionalDate
    .map(d -> d.plusDays(1))
    .orElse(LocalDate.now());
```

### 3. 월(Month) 인덱스

```java
// ✅ java.time은 1부터 시작 (직관적)
LocalDate date1 = LocalDate.of(2025, 2, 2);  // 2월

// ❌ 구 Calendar는 0부터 시작 (혼동 주의)
Calendar cal = Calendar.getInstance();
cal.set(2025, 1, 2);  // 2월 (1 = 2월)
```

### 4. 시간대 무시

```java
// ❌ LocalDateTime은 시간대 정보 없음
LocalDateTime seoul = LocalDateTime.now();
LocalDateTime london = LocalDateTime.now();
// 같은 값 반환 (시간대 고려 안함)

// ✅ 시간대 필요 시 ZonedDateTime 사용
ZonedDateTime seoulTime = ZonedDateTime.now(ZoneId.of("Asia/Seoul"));
ZonedDateTime londonTime = ZonedDateTime.now(ZoneId.of("Europe/London"));
```

### 5. 파싱 예외 처리

```java
// ❌ 예외 처리 없음
LocalDate date = LocalDate.parse("invalid");  // DateTimeParseException

// ✅ try-catch
try {
    LocalDate date = LocalDate.parse(input);
} catch (DateTimeParseException e) {
    // 기본값 또는 에러 처리
}
```

### 6. equals vs isEqual

```java
LocalDate date1 = LocalDate.of(2025, 2, 2);
LocalDate date2 = LocalDate.of(2025, 2, 2);

// equals() - 객체 비교
boolean result1 = date1.equals(date2);  // true

// isEqual() - 날짜 값만 비교 (권장)
boolean result2 = date1.isEqual(date2);  // true
```

## 관련 개념
- [[Java-날짜시간API-심화]]
- [[Java-Optional]]
- [[Java-불변객체-Immutable]]
- [[Java-람다-Stream]]

## 면접 질문
1. LocalDate, LocalTime, LocalDateTime의 차이점은?
2. java.time API가 기존 Date, Calendar보다 나은 이유는?

## 참고 자료
- Java SE 8 Date and Time
- DateTimeFormatter Documentation
- ISO-8601 Standard