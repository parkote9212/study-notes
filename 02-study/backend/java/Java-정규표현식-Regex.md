---
tags:
  - study
  - java
  - regex
  - pattern
  - validation
created: 2025-02-08
---

# Java 정규표현식 (Regular Expression)

## 한 줄 요약
> 문자열 패턴 매칭, 검증, 추출, 치환을 위한 강력한 도구

## 상세 설명

### 정규표현식이란?

정규표현식(Regular Expression, Regex)은 **문자열의 패턴을 표현하는 형식 언어**입니다. Java에서는 `java.util.regex` 패키지의 `Pattern`과 `Matcher` 클래스를 사용합니다.

**주요 용도**
1. **검증**: 이메일, 전화번호, 비밀번호 형식 확인
2. **추출**: 문자열에서 특정 패턴 찾기
3. **치환**: 패턴에 맞는 문자열 교체
4. **분할**: 패턴을 기준으로 문자열 나누기

**왜 필요한가?**
- 복잡한 문자열 처리를 간결하게
- 입력 데이터 유효성 검증
- 로그 파일 파싱
- 웹 스크래핑

## 코드 예시

### 기본 사용법

```java
import java.util.regex.*;

public class RegexBasic {
    public static void main(String[] args) {
        // 방법 1: Pattern & Matcher
        Pattern pattern = Pattern.compile("Java");
        Matcher matcher = pattern.matcher("I love Java");
        
        if (matcher.find()) {
            System.out.println("패턴 찾음!");
        }
        
        // 방법 2: String.matches() - 전체 매칭
        String text = "12345";
        boolean isNumber = text.matches("\\d+");  // \d+ = 숫자 1개 이상
        System.out.println(isNumber);  // true
        
        // 방법 3: Pattern.matches() - 빠른 검증
        boolean valid = Pattern.matches("[0-9]+", "12345");
        System.out.println(valid);  // true
    }
}
```

### 기본 메타 문자

```java
public class MetaCharacters {
    public static void main(String[] args) {
        // . (점) - 임의의 한 문자
        System.out.println("abc".matches("a.c"));    // true
        System.out.println("a c".matches("a.c"));    // true
        System.out.println("ac".matches("a.c"));     // false
        
        // * (별표) - 0개 이상
        System.out.println("ac".matches("ab*c"));    // true (b가 0개)
        System.out.println("abc".matches("ab*c"));   // true (b가 1개)
        System.out.println("abbbc".matches("ab*c")); // true (b가 3개)
        
        // + (플러스) - 1개 이상
        System.out.println("ac".matches("ab+c"));    // false (b가 0개)
        System.out.println("abc".matches("ab+c"));   // true (b가 1개)
        System.out.println("abbc".matches("ab+c"));  // true (b가 2개)
        
        // ? (물음표) - 0개 또는 1개
        System.out.println("ac".matches("ab?c"));    // true
        System.out.println("abc".matches("ab?c"));   // true
        System.out.println("abbc".matches("ab?c"));  // false
        
        // ^ (캐럿) - 시작
        System.out.println("abc".matches("^a.*"));   // true
        System.out.println("bac".matches("^a.*"));   // false
        
        // $ (달러) - 끝
        System.out.println("abc".matches(".*c$"));   // true
        System.out.println("acb".matches(".*c$"));   // false
    }
}
```

### 문자 클래스

```java
public class CharacterClasses {
    public static void main(String[] args) {
        // [abc] - a, b, c 중 하나
        System.out.println("a".matches("[abc]"));    // true
        System.out.println("d".matches("[abc]"));    // false
        
        // [^abc] - a, b, c가 아닌 문자
        System.out.println("d".matches("[^abc]"));   // true
        System.out.println("a".matches("[^abc]"));   // false
        
        // [a-z] - a부터 z까지
        System.out.println("m".matches("[a-z]"));    // true
        System.out.println("M".matches("[a-z]"));    // false
        
        // [A-Za-z] - 모든 영문자
        System.out.println("Hello".matches("[A-Za-z]+")); // true
        
        // [0-9] - 숫자
        System.out.println("5".matches("[0-9]"));    // true
        
        // \d - 숫자 [0-9]와 동일
        System.out.println("123".matches("\\d+"));   // true
        
        // \D - 숫자가 아닌 것
        System.out.println("abc".matches("\\D+"));   // true
        
        // \w - 단어 문자 [a-zA-Z0-9_]
        System.out.println("abc_123".matches("\\w+")); // true
        
        // \W - 단어 문자가 아닌 것
        System.out.println("!@#".matches("\\W+"));   // true
        
        // \s - 공백 문자 (space, tab, newline)
        System.out.println(" \t\n".matches("\\s+"));  // true
        
        // \S - 공백이 아닌 문자
        System.out.println("abc".matches("\\S+"));   // true
    }
}
```

### 수량자 (Quantifiers)

```java
public class Quantifiers {
    public static void main(String[] args) {
        // {n} - 정확히 n개
        System.out.println("aaa".matches("a{3}"));    // true
        System.out.println("aa".matches("a{3}"));     // false
        
        // {n,} - n개 이상
        System.out.println("aaaa".matches("a{2,}"));  // true
        System.out.println("a".matches("a{2,}"));     // false
        
        // {n,m} - n개 이상 m개 이하
        System.out.println("aaa".matches("a{2,4}"));  // true
        System.out.println("a".matches("a{2,4}"));    // false
        System.out.println("aaaaa".matches("a{2,4}")); // false
        
        // 실전 예시: 비밀번호 (8-20자)
        String password = "MyPass123!";
        boolean valid = password.matches(".{8,20}");
        System.out.println(valid);  // true
    }
}
```

## 실전 예시

### 1. 이메일 검증

```java
public class EmailValidation {
    public static boolean isValidEmail(String email) {
        // 간단한 이메일 패턴
        String pattern = "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$";
        return email.matches(pattern);
    }
    
    // 더 엄격한 이메일 검증
    public static boolean isValidEmailStrict(String email) {
        String pattern = "^[a-zA-Z0-9_+&*-]+(?:\\.[a-zA-Z0-9_+&*-]+)*" +
                        "@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,7}$";
        return email.matches(pattern);
    }
    
    public static void main(String[] args) {
        System.out.println(isValidEmail("user@example.com"));     // true
        System.out.println(isValidEmail("user.name@example.co.kr")); // true
        System.out.println(isValidEmail("user@"));                // false
        System.out.println(isValidEmail("@example.com"));         // false
    }
}
```

### 2. 전화번호 검증

```java
public class PhoneValidation {
    // 01X-XXXX-XXXX 형식
    public static boolean isValidPhone(String phone) {
        String pattern = "^01[0-9]-\\d{4}-\\d{4}$";
        return phone.matches(pattern);
    }
    
    // 하이픈 있거나 없거나
    public static boolean isValidPhoneFlexible(String phone) {
        String pattern = "^01[0-9]-?\\d{3,4}-?\\d{4}$";
        return phone.matches(pattern);
    }
    
    // 010-1234-5678 또는 02-123-4567 (지역번호 포함)
    public static boolean isValidPhoneAll(String phone) {
        String pattern = "^(01[0-9]|02|0[3-9]{1}[0-9]{1})-?" +
                        "\\d{3,4}-?\\d{4}$";
        return phone.matches(pattern);
    }
    
    public static void main(String[] args) {
        System.out.println(isValidPhone("010-1234-5678"));  // true
        System.out.println(isValidPhone("01012345678"));    // false
        
        System.out.println(isValidPhoneFlexible("010-1234-5678"));  // true
        System.out.println(isValidPhoneFlexible("01012345678"));    // true
        
        System.out.println(isValidPhoneAll("02-123-4567"));   // true
        System.out.println(isValidPhoneAll("031-123-4567"));  // true
    }
}
```

### 3. 비밀번호 검증

```java
public class PasswordValidation {
    // 최소 8자, 대문자/소문자/숫자/특수문자 각 1개 이상
    public static boolean isValidPassword(String password) {
        // 개별 조건 체크
        boolean hasMinLength = password.length() >= 8;
        boolean hasUppercase = password.matches(".*[A-Z].*");
        boolean hasLowercase = password.matches(".*[a-z].*");
        boolean hasDigit = password.matches(".*\\d.*");
        boolean hasSpecial = password.matches(".*[!@#$%^&*(),.?\":{}|<>].*");
        
        return hasMinLength && hasUppercase && hasLowercase && 
               hasDigit && hasSpecial;
    }
    
    // 한 줄로 검증 (복잡)
    public static boolean isValidPasswordOneLine(String password) {
        String pattern = "^(?=.*[A-Z])(?=.*[a-z])(?=.*\\d)" +
                        "(?=.*[!@#$%^&*]).{8,}$";
        return password.matches(pattern);
    }
    
    public static void main(String[] args) {
        System.out.println(isValidPassword("Pass123!"));    // true
        System.out.println(isValidPassword("password"));    // false (조건 부족)
        System.out.println(isValidPassword("Pass123"));     // false (특수문자 없음)
    }
}
```

### 4. URL 검증

```java
public class UrlValidation {
    public static boolean isValidUrl(String url) {
        String pattern = "^(https?://)?" +                // 프로토콜 (선택)
                        "([a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,}" + // 도메인
                        "(/.*)?$";                          // 경로 (선택)
        return url.matches(pattern);
    }
    
    public static void main(String[] args) {
        System.out.println(isValidUrl("https://www.example.com"));  // true
        System.out.println(isValidUrl("http://example.com/path"));  // true
        System.out.println(isValidUrl("www.example.com"));          // true
        System.out.println(isValidUrl("example"));                  // false
    }
}
```

### 5. 주민등록번호 형식 검증

```java
public class SsnValidation {
    // 000000-0000000 형식
    public static boolean isValidSsn(String ssn) {
        String pattern = "^\\d{6}-[1-4]\\d{6}$";
        return ssn.matches(pattern);
    }
    
    public static void main(String[] args) {
        System.out.println(isValidSsn("900101-1234567"));  // true
        System.out.println(isValidSsn("900101-5234567"));  // false (5는 유효하지 않음)
    }
}
```

### 6. Pattern & Matcher 활용

```java
import java.util.regex.*;

public class PatternMatcherExample {
    public static void main(String[] args) {
        String text = "My email is user@example.com and " +
                     "backup is admin@test.org";
        
        // 패턴 컴파일 (재사용 가능)
        Pattern pattern = Pattern.compile(
            "[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
        );
        Matcher matcher = pattern.matcher(text);
        
        // find() - 패턴 찾기
        while (matcher.find()) {
            String email = matcher.group();
            int start = matcher.start();
            int end = matcher.end();
            System.out.println("Found: " + email + 
                             " at [" + start + ", " + end + ")");
        }
        // Found: user@example.com at [13, 29)
        // Found: admin@test.org at [43, 57)
    }
}
```

### 7. 그룹 캡처 (Group Capture)

```java
public class GroupCapture {
    public static void main(String[] args) {
        String text = "My phone is 010-1234-5678";
        
        // 그룹 지정: (패턴)
        Pattern pattern = Pattern.compile(
            "(\\d{3})-(\\d{4})-(\\d{4})"
        );
        Matcher matcher = pattern.matcher(text);
        
        if (matcher.find()) {
            System.out.println("전체: " + matcher.group(0));  // 010-1234-5678
            System.out.println("앞자리: " + matcher.group(1)); // 010
            System.out.println("중간: " + matcher.group(2));   // 1234
            System.out.println("뒷자리: " + matcher.group(3)); // 5678
        }
        
        // 이름 있는 그룹 (Java 7+)
        String text2 = "홍길동의 나이는 30세입니다";
        Pattern pattern2 = Pattern.compile(
            "(?<name>[가-힣]+)의 나이는 (?<age>\\d+)세"
        );
        Matcher matcher2 = pattern2.matcher(text2);
        
        if (matcher2.find()) {
            System.out.println("이름: " + matcher2.group("name")); // 홍길동
            System.out.println("나이: " + matcher2.group("age"));  // 30
        }
    }
}
```

### 8. 문자열 치환 (Replace)

```java
public class RegexReplace {
    public static void main(String[] args) {
        String text = "전화번호: 010-1234-5678";
        
        // replaceAll - 모든 매칭 치환
        String masked = text.replaceAll("\\d{4}-\\d{4}", "****-****");
        System.out.println(masked);  // 전화번호: 010-****-****
        
        // replaceFirst - 첫 매칭만 치환
        String text2 = "010-1234-5678, 010-9876-5432";
        String result = text2.replaceFirst("\\d{3}-\\d{4}-\\d{4}", "XXX-XXXX-XXXX");
        System.out.println(result);  // XXX-XXXX-XXXX, 010-9876-5432
        
        // 그룹 참조로 치환
        String date = "2025-02-08";
        String formatted = date.replaceAll(
            "(\\d{4})-(\\d{2})-(\\d{2})", 
            "$3/$2/$1"  // $1, $2, $3은 그룹 참조
        );
        System.out.println(formatted);  // 08/02/2025
    }
}
```

### 9. 문자열 분할 (Split)

```java
public class RegexSplit {
    public static void main(String[] args) {
        // 쉼표로 분할
        String csv = "Apple,Banana,Cherry";
        String[] fruits = csv.split(",");
        System.out.println(Arrays.toString(fruits));
        // [Apple, Banana, Cherry]
        
        // 공백(여러 개)으로 분할
        String text = "Hello    World   Java";
        String[] words = text.split("\\s+");
        System.out.println(Arrays.toString(words));
        // [Hello, World, Java]
        
        // 특수문자로 분할
        String path = "C:\\Users\\Documents\\file.txt";
        String[] parts = path.split("\\\\");  // \\ = \
        System.out.println(Arrays.toString(parts));
        // [C:, Users, Documents, file.txt]
        
        // 여러 구분자
        String mixed = "Apple,Banana;Cherry:Orange";
        String[] items = mixed.split("[,;:]");
        System.out.println(Arrays.toString(items));
        // [Apple, Banana, Cherry, Orange]
    }
}
```

### 10. 로그 파싱

```java
public class LogParsing {
    public static void main(String[] args) {
        String logLine = "[2025-02-08 10:30:45] ERROR: Connection failed at server.java:42";
        
        Pattern pattern = Pattern.compile(
            "\\[(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})\\] " +
            "(\\w+): (.+?) at (.+):(\\d+)"
        );
        Matcher matcher = pattern.matcher(logLine);
        
        if (matcher.find()) {
            String timestamp = matcher.group(1);
            String level = matcher.group(2);
            String message = matcher.group(3);
            String file = matcher.group(4);
            String line = matcher.group(5);
            
            System.out.println("시간: " + timestamp);
            System.out.println("레벨: " + level);
            System.out.println("메시지: " + message);
            System.out.println("파일: " + file + ":" + line);
        }
    }
}
```

## 주의사항 / 함정

### 1. 백슬래시 이스케이프

```java
// ❌ 잘못된 사용
String pattern1 = "\d+";  // 컴파일 에러

// ✅ 올바른 사용
String pattern2 = "\\d+";  // Java 문자열에서 \\ = \

// 이스케이프가 필요한 문자들
String dot = "\\.";        // .
String star = "\\*";       // *
String plus = "\\+";       // +
String question = "\\?";   // ?
String backslash = "\\\\"; // \
```

### 2. matches() vs find()

```java
public class MatchesVsFind {
    public static void main(String[] args) {
        String text = "I love Java";
        
        // matches() - 전체 문자열이 패턴과 일치해야 함
        System.out.println(text.matches("Java"));      // false
        System.out.println(text.matches(".*Java.*"));  // true
        
        // find() - 부분 매칭
        Pattern pattern = Pattern.compile("Java");
        Matcher matcher = pattern.matcher(text);
        System.out.println(matcher.find());  // true
    }
}
```

### 3. 성능 고려

```java
// ❌ 비효율적 - 매번 컴파일
public boolean validate(String input) {
    return input.matches("\\d+");  // 매번 Pattern 객체 생성
}

// ✅ 효율적 - Pattern 재사용
private static final Pattern NUMBER_PATTERN = Pattern.compile("\\d+");

public boolean validateEfficient(String input) {
    return NUMBER_PATTERN.matcher(input).matches();
}
```

### 4. 탐욕적 vs 게으른 수량자

```java
public class GreedyVsLazy {
    public static void main(String[] args) {
        String html = "<div>Hello</div><div>World</div>";
        
        // 탐욕적 (Greedy) - 최대한 많이
        System.out.println(html.replaceAll("<div>.*</div>", ""));
        // 출력: (전체 삭제)
        
        // 게으른 (Lazy) - 최소한만
        System.out.println(html.replaceAll("<div>.*?</div>", ""));
        // 출력: (각각 삭제)
        
        // 설명:
        // .*  = 탐욕적 (최대한 길게)
        // .*? = 게으른 (최소한만)
        // .+? = 게으른 (1개 이상, 최소한만)
    }
}
```

### 5. null 체크

```java
public class NullCheck {
    public static boolean isValidEmail(String email) {
        // ❌ NullPointerException 위험
        // return email.matches("...");
        
        // ✅ null 체크
        if (email == null) {
            return false;
        }
        return email.matches("^[A-Za-z0-9+_.-]+@.+\\..+$");
    }
}
```

## 관련 개념
- [[Java-문자열처리-String]]
- [[Java-예외처리-Exception]]
- [[Java-컬렉션-프레임워크]]

## 면접 질문
1. 정규표현식이란 무엇인가요?
2. matches()와 find()의 차이는?
3. Pattern과 Matcher의 역할은?
4. 탐욕적 수량자와 게으른 수량자의 차이는?
5. 이메일 검증 정규표현식을 작성해보세요.

## 참고 자료
- Java Documentation - java.util.regex
- Regular Expressions Cookbook
- regex101.com (정규표현식 테스트 사이트)
