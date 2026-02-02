---
tags:
  - study
  - java
  - string
  - stringbuilder
  - regex
created: 2025-02-02
---

# Java 문자열처리심화

## 한 줄 요약
> String 성능 최적화와 고급 문자열 처리 기법

## 상세 설명

### 심화 주제

1. **StringBuilder vs StringBuffer**
2. **Text Blocks (Java 15+)**
3. **String 메서드 심화**
4. **정규표현식 기초**
5. **문자열 성능 최적화**

### String의 불변성 복습

String은 불변 객체이므로 문자열 조작 시마다 새로운 객체가 생성됩니다. 대량의 문자열 연산에서는 성능 문제가 발생할 수 있습니다.

## 코드 예시

### StringBuilder - 가변 문자열

```java
// ❌ String 연결 - 비효율적
String result = "";
for (int i = 0; i < 1000; i++) {
    result += i + ",";  // 매번 새 String 객체 생성
}

// ✅ StringBuilder - 효율적
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i).append(",");
}
String result = sb.toString();
```

### StringBuilder 주요 메서드

```java
StringBuilder sb = new StringBuilder();

// 1. append() - 끝에 추가
sb.append("Hello");
sb.append(" ");
sb.append("World");
System.out.println(sb);  // "Hello World"

// 2. insert() - 특정 위치에 삽입
sb.insert(5, " Java");
System.out.println(sb);  // "Hello Java World"

// 3. delete() - 범위 삭제
sb.delete(5, 10);
System.out.println(sb);  // "Hello World"

// 4. deleteCharAt() - 특정 위치 삭제
sb.deleteCharAt(5);
System.out.println(sb);  // "HelloWorld"

// 5. reverse() - 뒤집기
sb.reverse();
System.out.println(sb);  // "dlroWolleH"

// 6. replace() - 범위 교체
sb.replace(0, 5, "Java");
System.out.println(sb);  // "JavaolleH"

// 7. setCharAt() - 특정 위치 문자 변경
sb.setCharAt(0, 'j');
System.out.println(sb);  // "javaolleH"
```

### StringBuilder 메서드 체이닝

```java
String result = new StringBuilder()
    .append("Name: ")
    .append("홍길동")
    .append(", Age: ")
    .append(30)
    .append(", Email: ")
    .append("hong@example.com")
    .toString();

System.out.println(result);
// Name: 홍길동, Age: 30, Email: hong@example.com
```

### StringBuilder vs StringBuffer

```java
// StringBuilder - 단일 스레드 (빠름)
StringBuilder sb = new StringBuilder();
sb.append("Hello");

// StringBuffer - 멀티 스레드 안전 (느림)
StringBuffer sbf = new StringBuffer();
sbf.append("Hello");

// 성능 차이 테스트
long start = System.currentTimeMillis();

// StringBuilder - 약 10ms
StringBuilder builder = new StringBuilder();
for (int i = 0; i < 100000; i++) {
    builder.append(i);
}

// StringBuffer - 약 15ms (synchronized 오버헤드)
StringBuffer buffer = new StringBuffer();
for (int i = 0; i < 100000; i++) {
    buffer.append(i);
}
```

### 멀티스레드 환경에서 StringBuffer

```java
class Counter {
    private StringBuffer log = new StringBuffer();
    
    public void addLog(String message) {
        // 스레드 안전
        log.append("[")
           .append(Thread.currentThread().getName())
           .append("] ")
           .append(message)
           .append("\n");
    }
    
    public String getLog() {
        return log.toString();
    }
}

// 사용
Counter counter = new Counter();
Thread t1 = new Thread(() -> counter.addLog("Task 1"));
Thread t2 = new Thread(() -> counter.addLog("Task 2"));
t1.start();
t2.start();
```

### Text Blocks (Java 15+)

```java
// ❌ 기존 방식 - 이스케이프 문자 많음
String html = "<html>\n" +
              "  <body>\n" +
              "    <h1>Hello</h1>\n" +
              "  </body>\n" +
              "</html>";

// ✅ Text Block - 가독성 좋음
String htmlBlock = """
    <html>
      <body>
        <h1>Hello</h1>
      </body>
    </html>
    """;

// JSON 예시
String json = """
    {
      "name": "홍길동",
      "age": 30,
      "email": "hong@example.com"
    }
    """;

// SQL 예시
String sql = """
    SELECT u.id, u.name, o.order_date
    FROM users u
    JOIN orders o ON u.id = o.user_id
    WHERE u.status = 'ACTIVE'
    ORDER BY o.order_date DESC
    """;
```

### Text Block 포맷팅

```java
String name = "홍길동";
int age = 30;

// 변수 삽입
String message = """
    안녕하세요, %s님!
    나이: %d세
    환영합니다.
    """.formatted(name, age);

// String.format() 사용
String formatted = String.format("""
    Name: %s
    Age: %d
    Status: %s
    """, name, age, "ACTIVE");
```

### String 메서드 심화 (Java 11+)

```java
String str = "  Hello World  ";

// 1. strip() - 유니코드 공백 제거 (trim보다 강력)
String stripped = str.strip();
System.out.println("[" + stripped + "]");  // [Hello World]

// 2. stripLeading(), stripTrailing()
String leading = str.stripLeading();   // "Hello World  "
String trailing = str.stripTrailing(); // "  Hello World"

// 3. isBlank() - 비어있거나 공백만 있는지
System.out.println("   ".isBlank());   // true
System.out.println("  a  ".isBlank()); // false

// 4. lines() - 라인별로 Stream 생성
String multiLine = "Line1\nLine2\nLine3";
multiLine.lines().forEach(System.out::println);

// 5. repeat() - 반복
String repeated = "=".repeat(50);
System.out.println(repeated);  // ==================================================

// 6. indent() - 들여쓰기
String text = "Hello\nWorld";
String indented = text.indent(4);
System.out.println(indented);
//     Hello
//     World
```

### String 메서드 심화 (Java 12+)

```java
// transform() - 변환 체이닝
String result = "hello world"
    .transform(String::toUpperCase)
    .transform(s -> s.replace(" ", "_"));
System.out.println(result);  // HELLO_WORLD

// formatted() - 포맷팅
String formatted = "Name: %s, Age: %d".formatted("홍길동", 30);
```

### 정규표현식 기초

```java
import java.util.regex.Pattern;
import java.util.regex.Matcher;

// 1. 매칭 확인
String email = "hong@example.com";
boolean isEmail = email.matches("^[\\w.-]+@[\\w.-]+\\.[a-zA-Z]{2,}$");
System.out.println(isEmail);  // true

// 2. Pattern과 Matcher 사용
String text = "전화번호: 010-1234-5678, 010-9876-5432";
Pattern pattern = Pattern.compile("\\d{3}-\\d{4}-\\d{4}");
Matcher matcher = pattern.matcher(text);

while (matcher.find()) {
    System.out.println("찾음: " + matcher.group());
}
// 찾음: 010-1234-5678
// 찾음: 010-9876-5432

// 3. 문자열 교체
String replaced = text.replaceAll("\\d{3}-\\d{4}-\\d{4}", "***-****-****");
System.out.println(replaced);
// 전화번호: ***-****-****, ***-****-****
```

### 정규표현식 패턴 예시

```java
class RegexPatterns {
    // 이메일
    public static final String EMAIL = 
        "^[\\w.-]+@[\\w.-]+\\.[a-zA-Z]{2,}$";
    
    // 전화번호 (한국)
    public static final String PHONE = 
        "^01[0-9]-\\d{3,4}-\\d{4}$";
    
    // 비밀번호 (8자 이상, 영문+숫자+특수문자)
    public static final String PASSWORD = 
        "^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,}$";
    
    // URL
    public static final String URL = 
        "^https?://[\\w.-]+(:\\d+)?(/.*)?$";
    
    // IP 주소
    public static final String IP = 
        "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$";
}

// 사용
public boolean validateEmail(String email) {
    return email.matches(RegexPatterns.EMAIL);
}

public boolean validatePassword(String password) {
    return password.matches(RegexPatterns.PASSWORD);
}
```

### 정규표현식 그룹 추출

```java
String text = "이름: 홍길동, 나이: 30세";
Pattern pattern = Pattern.compile("이름: (\\S+), 나이: (\\d+)세");
Matcher matcher = pattern.matcher(text);

if (matcher.find()) {
    String name = matcher.group(1);  // 홍길동
    int age = Integer.parseInt(matcher.group(2));  // 30
    
    System.out.println("이름: " + name);
    System.out.println("나이: " + age);
}
```

### 실전 예시: 로그 파싱

```java
class LogParser {
    private static final Pattern LOG_PATTERN = Pattern.compile(
        "\\[(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})\\] " +
        "\\[(\\w+)\\] (.+)"
    );
    
    public LogEntry parse(String logLine) {
        Matcher matcher = LOG_PATTERN.matcher(logLine);
        
        if (matcher.find()) {
            String timestamp = matcher.group(1);
            String level = matcher.group(2);
            String message = matcher.group(3);
            
            return new LogEntry(timestamp, level, message);
        }
        
        return null;
    }
}

class LogEntry {
    private String timestamp;
    private String level;
    private String message;
    
    // constructor, getters
}

// 사용
String log = "[2025-02-02 14:30:25] [INFO] User logged in";
LogParser parser = new LogParser();
LogEntry entry = parser.parse(log);
```

### 실전 예시: CSV 파서

```java
class CsvParser {
    public List<String[]> parse(String csv) {
        List<String[]> result = new ArrayList<>();
        
        String[] lines = csv.split("\n");
        for (String line : lines) {
            // 쉼표로 분리 (간단한 경우)
            String[] fields = line.split(",");
            result.add(fields);
        }
        
        return result;
    }
    
    // 따옴표 내부의 쉼표 처리
    public List<String[]> parseAdvanced(String csv) {
        List<String[]> result = new ArrayList<>();
        Pattern pattern = Pattern.compile(
            ",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)"
        );
        
        String[] lines = csv.split("\n");
        for (String line : lines) {
            String[] fields = pattern.split(line);
            // 따옴표 제거
            for (int i = 0; i < fields.length; i++) {
                fields[i] = fields[i].replaceAll("^\"|\"$", "");
            }
            result.add(fields);
        }
        
        return result;
    }
}
```

### 성능 최적화: String Pool

```java
// String literal - String Pool에 저장
String s1 = "Hello";
String s2 = "Hello";
System.out.println(s1 == s2);  // true (같은 객체)

// new String() - Heap에 새 객체 생성
String s3 = new String("Hello");
System.out.println(s1 == s3);  // false (다른 객체)

// intern() - String Pool에 추가/조회
String s4 = s3.intern();
System.out.println(s1 == s4);  // true (같은 객체)
```

### 성능 최적화: StringBuilder 초기 용량

```java
// ❌ 기본 용량 (16) - 여러 번 확장됨
StringBuilder sb1 = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb1.append("text");
}

// ✅ 적절한 초기 용량 설정 - 확장 최소화
StringBuilder sb2 = new StringBuilder(4000);
for (int i = 0; i < 1000; i++) {
    sb2.append("text");
}
```

### 실전 예시: SQL 쿼리 빌더

```java
class QueryBuilder {
    private StringBuilder query;
    
    public QueryBuilder() {
        this.query = new StringBuilder();
    }
    
    public QueryBuilder select(String... columns) {
        query.append("SELECT ");
        query.append(String.join(", ", columns));
        return this;
    }
    
    public QueryBuilder from(String table) {
        query.append(" FROM ").append(table);
        return this;
    }
    
    public QueryBuilder where(String condition) {
        query.append(" WHERE ").append(condition);
        return this;
    }
    
    public QueryBuilder orderBy(String column) {
        query.append(" ORDER BY ").append(column);
        return this;
    }
    
    public String build() {
        return query.toString();
    }
}

// 사용
String sql = new QueryBuilder()
    .select("id", "name", "email")
    .from("users")
    .where("status = 'ACTIVE'")
    .orderBy("created_at DESC")
    .build();

System.out.println(sql);
// SELECT id, name, email FROM users WHERE status = 'ACTIVE' ORDER BY created_at DESC
```

## 주의사항 / 함정

### 1. String 연결 성능

```java
// ❌ 반복문에서 + 연산자
String result = "";
for (int i = 0; i < 10000; i++) {
    result += i;  // O(n²) 시간 복잡도
}

// ✅ StringBuilder 사용
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);  // O(n) 시간 복잡도
}
String result = sb.toString();
```

### 2. StringBuffer의 불필요한 사용

```java
// ❌ 단일 스레드에서 StringBuffer
StringBuffer sb = new StringBuffer();  // 불필요한 동기화 오버헤드

// ✅ StringBuilder 사용
StringBuilder sb = new StringBuilder();
```

### 3. 정규표현식 컴파일 최적화

```java
// ❌ 매번 컴파일
public boolean validate(String input) {
    return input.matches("^[a-z]+$");  // 매번 Pattern 컴파일
}

// ✅ Pattern 재사용
private static final Pattern PATTERN = Pattern.compile("^[a-z]+$");

public boolean validate(String input) {
    return PATTERN.matcher(input).matches();
}
```

### 4. split() vs Pattern.split()

```java
String text = "a,b,c,d,e";

// ❌ 반복 사용 시 비효율적
for (int i = 0; i < 10000; i++) {
    String[] parts = text.split(",");  // 매번 Pattern 컴파일
}

// ✅ Pattern 재사용
Pattern pattern = Pattern.compile(",");
for (int i = 0; i < 10000; i++) {
    String[] parts = pattern.split(text);
}
```

### 5. StringBuilder toString() 재사용

```java
StringBuilder sb = new StringBuilder("Hello");

// ❌ toString()은 매번 새 String 생성
String s1 = sb.toString();
String s2 = sb.toString();
System.out.println(s1 == s2);  // false

// StringBuilder 내용이 같아도 다른 객체
```

### 6. 정규표현식 복잡도

```java
// ❌ 과도하게 복잡한 정규표현식 (성능 저하)
String regex = "^(?=.*[A-Z])(?=.*[a-z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$";

// ✅ 간단한 검증으로 분리
public boolean isValidPassword(String password) {
    if (password.length() < 8) return false;
    
    boolean hasUpper = password.matches(".*[A-Z].*");
    boolean hasLower = password.matches(".*[a-z].*");
    boolean hasDigit = password.matches(".*\\d.*");
    boolean hasSpecial = password.matches(".*[@$!%*?&].*");
    
    return hasUpper && hasLower && hasDigit && hasSpecial;
}
```

## 관련 개념
- [[Java-String-불변성]]
- [[Java-정규표현식-고급]]
- [[Java-Stream-API]]
- [[Java-성능최적화]]

## 면접 질문
1. StringBuilder와 StringBuffer의 차이점은?
2. String + 연산자와 StringBuilder.append()의 성능 차이는?

## 참고 자료
- Effective Java 3/E - Item 63 (문자열 연결은 느리니 주의하라)
- Java String API Documentation
- Regular Expression Tutorial