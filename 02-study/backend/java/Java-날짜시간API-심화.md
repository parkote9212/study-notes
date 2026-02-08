---
tags:
  - study
  - java
  - datetime
  - timezone
  - instant
created: 2025-02-02
---

# Java 날짜시간API 심화

## 한 줄 요약
> 타임존, 타임스탬프, 기간 계산을 다루는 고급 날짜/시간 API

## 상세 설명

### 심화 주제

이 문서는 java.time API의 심화 기능을 다룹니다:

1. **ZonedDateTime** - 타임존이 포함된 날짜/시간
2. **Instant** - 타임스탬프 (UTC 기준)
3. **Period** - 날짜 기반 기간
4. **Duration** - 시간 기반 기간
5. **타임존 변환**
6. **레거시 API 변환**

## 코드 예시

### ZonedDateTime - 타임존

```java
import java.time.ZonedDateTime;
import java.time.ZoneId;

// 현재 시스템 타임존
ZonedDateTime now = ZonedDateTime.now();
System.out.println(now);
// 2025-02-02T14:30:25.123+09:00[Asia/Seoul]

// 특정 타임존
ZonedDateTime seoul = ZonedDateTime.now(ZoneId.of("Asia/Seoul"));
ZonedDateTime london = ZonedDateTime.now(ZoneId.of("Europe/London"));
ZonedDateTime newYork = ZonedDateTime.now(ZoneId.of("America/New_York"));

System.out.println("서울: " + seoul);
System.out.println("런던: " + london);
System.out.println("뉴욕: " + newYork);

// LocalDateTime에서 ZonedDateTime 생성
LocalDateTime localDateTime = LocalDateTime.of(2025, 2, 2, 14, 30);
ZonedDateTime zonedDateTime = localDateTime.atZone(ZoneId.of("Asia/Seoul"));
```

### 타임존 변환

```java
// 서울 시간을 뉴욕 시간으로 변환
ZonedDateTime seoulTime = ZonedDateTime.of(
    2025, 2, 2, 14, 30, 0, 0,
    ZoneId.of("Asia/Seoul")
);

ZonedDateTime newYorkTime = seoulTime.withZoneSameInstant(
    ZoneId.of("America/New_York")
);

System.out.println("서울: " + seoulTime);    // 2025-02-02T14:30+09:00
System.out.println("뉴욕: " + newYorkTime);  // 2025-02-02T00:30-05:00
```

### 사용 가능한 타임존 조회

```java
import java.time.ZoneId;
import java.util.Set;

// 모든 타임존 ID 조회
Set<String> availableZoneIds = ZoneId.getAvailableZoneIds();

// 주요 타임존 출력
availableZoneIds.stream()
    .filter(id -> id.startsWith("Asia/") || id.startsWith("America/"))
    .sorted()
    .limit(10)
    .forEach(System.out::println);

// 타임존 정보 조회
ZoneId zoneId = ZoneId.of("Asia/Seoul");
System.out.println("Zone ID: " + zoneId);
System.out.println("Display Name: " + zoneId.getDisplayName(
    TextStyle.FULL, Locale.KOREAN
));
```

### Instant - 타임스탬프

```java
import java.time.Instant;

// 현재 Instant (UTC 기준)
Instant now = Instant.now();
System.out.println(now);  // 2025-02-02T05:30:25.123Z

// epoch time (1970-01-01 00:00:00 UTC)
Instant epoch = Instant.EPOCH;
System.out.println(epoch);  // 1970-01-01T00:00:00Z

// epoch milliseconds로 생성
long millis = System.currentTimeMillis();
Instant fromMillis = Instant.ofEpochMilli(millis);

// epoch seconds로 생성
long seconds = System.currentTimeMillis() / 1000;
Instant fromSeconds = Instant.ofEpochSecond(seconds);

// Instant에서 epoch 값 가져오기
long epochSecond = now.getEpochSecond();
long epochMilli = now.toEpochMilli();
```

### Instant 변환

```java
// Instant → ZonedDateTime
Instant instant = Instant.now();
ZonedDateTime zonedDateTime = instant.atZone(ZoneId.of("Asia/Seoul"));

// ZonedDateTime → Instant
ZonedDateTime zdt = ZonedDateTime.now();
Instant instantFromZdt = zdt.toInstant();

// LocalDateTime → Instant (타임존 필요)
LocalDateTime localDateTime = LocalDateTime.now();
Instant instantFromLocal = localDateTime
    .atZone(ZoneId.systemDefault())
    .toInstant();
```

### Period - 날짜 기간

```java
import java.time.Period;

// Period 생성
Period period1 = Period.ofDays(10);       // 10일
Period period2 = Period.ofWeeks(2);       // 2주 (14일)
Period period3 = Period.ofMonths(3);      // 3개월
Period period4 = Period.ofYears(1);       // 1년

// 복합 기간
Period period5 = Period.of(1, 2, 15);     // 1년 2개월 15일

// 두 날짜 사이의 기간
LocalDate startDate = LocalDate.of(2024, 1, 1);
LocalDate endDate = LocalDate.of(2025, 2, 2);
Period between = Period.between(startDate, endDate);

System.out.println(between.getYears());   // 1
System.out.println(between.getMonths());  // 1
System.out.println(between.getDays());    // 2

// Period 적용
LocalDate date = LocalDate.of(2025, 2, 2);
LocalDate future = date.plus(Period.ofMonths(3));  // 2025-05-02
```

### Duration - 시간 기간

```java
import java.time.Duration;

// Duration 생성
Duration duration1 = Duration.ofHours(2);      // 2시간
Duration duration2 = Duration.ofMinutes(30);   // 30분
Duration duration3 = Duration.ofSeconds(45);   // 45초

// 복합 시간
Duration duration4 = Duration.ofHours(2).plusMinutes(30);  // 2시간 30분

// 두 시간 사이의 Duration
LocalTime start = LocalTime.of(10, 0);
LocalTime end = LocalTime.of(14, 30);
Duration between = Duration.between(start, end);

System.out.println(between.toHours());    // 4
System.out.println(between.toMinutes());  // 270

// LocalDateTime 사이
LocalDateTime dt1 = LocalDateTime.of(2025, 2, 2, 10, 0);
LocalDateTime dt2 = LocalDateTime.of(2025, 2, 2, 14, 30);
Duration duration = Duration.between(dt1, dt2);
```

### Period vs Duration

```java
// Period - 날짜 단위 (년/월/일)
LocalDate date1 = LocalDate.of(2025, 1, 1);
LocalDate date2 = date1.plus(Period.ofMonths(1));
System.out.println(date2);  // 2025-02-01

// Duration - 시간 단위 (시/분/초)
LocalTime time1 = LocalTime.of(10, 0);
LocalTime time2 = time1.plus(Duration.ofHours(2));
System.out.println(time2);  // 12:00

// ❌ LocalDate에 Duration 사용 불가
// date1.plus(Duration.ofHours(2));  // UnsupportedTemporalTypeException

// ❌ LocalTime에 Period 사용 불가
// time1.plus(Period.ofDays(1));  // UnsupportedTemporalTypeException
```

### ChronoUnit - 단위 계산

```java
import java.time.temporal.ChronoUnit;

LocalDate start = LocalDate.of(2025, 1, 1);
LocalDate end = LocalDate.of(2025, 12, 31);

// 두 날짜 사이의 일수
long days = ChronoUnit.DAYS.between(start, end);
System.out.println(days + "일");  // 364일

// 두 날짜 사이의 주수
long weeks = ChronoUnit.WEEKS.between(start, end);
System.out.println(weeks + "주");  // 52주

// 두 날짜 사이의 개월수
long months = ChronoUnit.MONTHS.between(start, end);
System.out.println(months + "개월");  // 11개월

// 시간 계산
LocalDateTime dt1 = LocalDateTime.of(2025, 2, 2, 10, 0);
LocalDateTime dt2 = LocalDateTime.of(2025, 2, 2, 14, 30);

long hours = ChronoUnit.HOURS.between(dt1, dt2);    // 4
long minutes = ChronoUnit.MINUTES.between(dt1, dt2);  // 270
long seconds = ChronoUnit.SECONDS.between(dt1, dt2);  // 16200
```

### 실전 예시: 회의 시간 관리

```java
class Meeting {
    private ZonedDateTime startTime;
    private Duration duration;
    
    public Meeting(ZonedDateTime startTime, Duration duration) {
        this.startTime = startTime;
        this.duration = duration;
    }
    
    public ZonedDateTime getEndTime() {
        return startTime.plus(duration);
    }
    
    public boolean isOverlapping(Meeting other) {
        ZonedDateTime thisEnd = this.getEndTime();
        ZonedDateTime otherEnd = other.getEndTime();
        
        return this.startTime.isBefore(otherEnd) && 
               other.startTime.isBefore(thisEnd);
    }
    
    public String getTimeInZone(ZoneId targetZone) {
        ZonedDateTime converted = startTime.withZoneSameInstant(targetZone);
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern(
            "yyyy-MM-dd HH:mm z"
        );
        return converted.format(formatter);
    }
}

// 사용
ZonedDateTime seoulTime = ZonedDateTime.of(
    2025, 2, 3, 10, 0, 0, 0,
    ZoneId.of("Asia/Seoul")
);

Meeting meeting = new Meeting(seoulTime, Duration.ofHours(1));

System.out.println("서울: " + meeting.getTimeInZone(ZoneId.of("Asia/Seoul")));
System.out.println("뉴욕: " + meeting.getTimeInZone(ZoneId.of("America/New_York")));
```

### 실전 예시: 구독 서비스

```java
class Subscription {
    private LocalDate startDate;
    private Period subscriptionPeriod;
    
    public Subscription(LocalDate startDate, Period period) {
        this.startDate = startDate;
        this.subscriptionPeriod = period;
    }
    
    public LocalDate getEndDate() {
        return startDate.plus(subscriptionPeriod);
    }
    
    public boolean isActive() {
        LocalDate today = LocalDate.now();
        LocalDate endDate = getEndDate();
        return !today.isAfter(endDate);
    }
    
    public long getDaysRemaining() {
        LocalDate today = LocalDate.now();
        LocalDate endDate = getEndDate();
        
        if (today.isAfter(endDate)) {
            return 0;
        }
        
        return ChronoUnit.DAYS.between(today, endDate);
    }
    
    public boolean isExpiringSoon() {
        return getDaysRemaining() <= 7 && getDaysRemaining() > 0;
    }
}

// 사용
Subscription monthly = new Subscription(
    LocalDate.of(2025, 1, 1),
    Period.ofMonths(1)
);

System.out.println("활성 상태: " + monthly.isActive());
System.out.println("남은 일수: " + monthly.getDaysRemaining());
```

### 레거시 API 변환

```java
import java.util.Date;
import java.util.Calendar;

// Date → Instant
Date date = new Date();
Instant instant = date.toInstant();

// Instant → Date
Instant instant2 = Instant.now();
Date dateFromInstant = Date.from(instant2);

// Date → LocalDateTime
Date date2 = new Date();
LocalDateTime localDateTime = date2.toInstant()
    .atZone(ZoneId.systemDefault())
    .toLocalDateTime();

// LocalDateTime → Date
LocalDateTime ldt = LocalDateTime.now();
Date dateFromLdt = Date.from(
    ldt.atZone(ZoneId.systemDefault()).toInstant()
);

// Calendar → ZonedDateTime
Calendar calendar = Calendar.getInstance();
ZonedDateTime zonedDateTime = calendar.toInstant()
    .atZone(calendar.getTimeZone().toZoneId());

// ZonedDateTime → Calendar
ZonedDateTime zdt = ZonedDateTime.now();
Calendar calendarFromZdt = GregorianCalendar.from(zdt);
```

### 실전 예시: 로그 타임스탬프

```java
class LogEntry {
    private Instant timestamp;
    private String message;
    private String level;
    
    public LogEntry(String level, String message) {
        this.timestamp = Instant.now();
        this.level = level;
        this.message = message;
    }
    
    public String getFormattedTimestamp() {
        ZonedDateTime zdt = timestamp.atZone(ZoneId.systemDefault());
        return zdt.format(
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS")
        );
    }
    
    public boolean isRecent() {
        Instant fiveMinutesAgo = Instant.now().minus(Duration.ofMinutes(5));
        return timestamp.isAfter(fiveMinutesAgo);
    }
    
    public long getAgeInSeconds() {
        return Duration.between(timestamp, Instant.now()).getSeconds();
    }
}
```

### 실전 예시: 이벤트 스케줄러

```java
class Event {
    private String name;
    private ZonedDateTime eventTime;
    private Duration reminderBefore;
    
    public ZonedDateTime getReminderTime() {
        return eventTime.minus(reminderBefore);
    }
    
    public boolean shouldSendReminder() {
        ZonedDateTime now = ZonedDateTime.now();
        ZonedDateTime reminderTime = getReminderTime();
        
        // 리마인더 시간이 지금으로부터 5분 이내
        Duration untilReminder = Duration.between(now, reminderTime);
        return untilReminder.toMinutes() >= 0 && 
               untilReminder.toMinutes() <= 5;
    }
    
    public String getCountdown() {
        ZonedDateTime now = ZonedDateTime.now();
        Duration until = Duration.between(now, eventTime);
        
        long days = until.toDays();
        long hours = until.toHours() % 24;
        long minutes = until.toMinutes() % 60;
        
        return String.format("%d일 %d시간 %d분", days, hours, minutes);
    }
}
```

## 주의사항 / 함정

### 1. 타임존 변환 실수

```java
// ❌ withZoneSameLocal - 시각만 변경 (시간 자체는 변하지 않음)
ZonedDateTime seoul = ZonedDateTime.of(
    2025, 2, 2, 14, 0, 0, 0,
    ZoneId.of("Asia/Seoul")
);
ZonedDateTime wrong = seoul.withZoneSameLocal(ZoneId.of("America/New_York"));
// 뉴욕 14:00 - 틀림!

// ✅ withZoneSameInstant - 같은 시점을 다른 타임존으로
ZonedDateTime correct = seoul.withZoneSameInstant(ZoneId.of("America/New_York"));
// 뉴욕 00:00 - 맞음!
```

### 2. Instant와 LocalDateTime 혼용

```java
// ❌ Instant는 타임존 정보 없음
Instant instant = Instant.now();
// instant.getHour();  // UnsupportedTemporalTypeException

// ✅ ZonedDateTime으로 변환
ZonedDateTime zdt = instant.atZone(ZoneId.systemDefault());
int hour = zdt.getHour();
```

### 3. Period와 Duration 혼동

```java
LocalDate date = LocalDate.of(2025, 1, 31);

// ❌ 1개월 후가 2월 31일? → 2월 28일로 조정됨
LocalDate nextMonth = date.plus(Period.ofMonths(1));
System.out.println(nextMonth);  // 2025-02-28

// 30일 후는 정확히 30일
LocalDate after30Days = date.plusDays(30);
System.out.println(after30Days);  // 2025-03-02
```

### 4. 서머타임 (DST) 주의

```java
// 서머타임 전환 시점
ZonedDateTime beforeDst = ZonedDateTime.of(
    2025, 3, 9, 1, 30, 0, 0,
    ZoneId.of("America/New_York")
);

// 1시간 더하면 3:30 (2:00~3:00이 건너뛰어짐)
ZonedDateTime afterDst = beforeDst.plusHours(1);
System.out.println(afterDst);  // 2025-03-09T03:30-04:00
```

### 5. Instant 비교 시 주의

```java
// Instant는 항상 UTC 기준
Instant instant1 = Instant.parse("2025-02-02T05:00:00Z");
Instant instant2 = Instant.parse("2025-02-02T14:00:00+09:00");

// 같은 시점!
System.out.println(instant1.equals(instant2));  // true
```

### 6. null 체크

```java
// ❌ null 처리 안함
public Duration getWorkingHours(LocalDateTime start, LocalDateTime end) {
    return Duration.between(start, end);  // NPE 위험
}

// ✅ null 체크
public Duration getWorkingHours(LocalDateTime start, LocalDateTime end) {
    if (start == null || end == null) {
        return Duration.ZERO;
    }
    return Duration.between(start, end);
}
```

## 관련 개념
- [[Java-날짜시간API-기본]]
- [[Java-람다-Stream]]
- [[Java-불변객체-Immutable]]

## 면접 질문
1. ZonedDateTime과 LocalDateTime의 차이점은?
2. Period와 Duration은 언제 각각 사용하나요?

## 참고 자료
- Java SE 8 Date and Time
- Time Zone Database
- ISO-8601 Standard