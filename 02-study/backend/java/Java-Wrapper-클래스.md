---
tags:
  - study
  - java
  - wrapper
  - boxing
  - autoboxing
created: 2025-02-03
---

# Wrapper 클래스

## 한 줄 요약
> 기본 타입을 객체로 감싸서 객체처럼 다룰 수 있게 해주는 클래스

## 상세 설명

### Wrapper 클래스란?

**기본 타입과 Wrapper 클래스 매핑**
- `byte` → `Byte`
- `short` → `Short`
- `int` → `Integer`
- `long` → `Long`
- `float` → `Float`
- `double` → `Double`
- `char` → `Character`
- `boolean` → `Boolean`

### 왜 필요한가?

1. **컬렉션 사용**: 제네릭은 객체만 허용
2. **null 처리**: 기본 타입은 null 불가
3. **유틸리티 메서드**: 변환, 파싱 등
4. **객체 필요 상황**: 메서드 인자, 리플렉션 등

## 코드 예시

### 1. Boxing과 Unboxing

```java
// Boxing - 기본 타입 → Wrapper
int primitiveInt = 10;
Integer wrapperInt = Integer.valueOf(primitiveInt);  // 명시적 boxing

// Unboxing - Wrapper → 기본 타입
Integer wrapperInt2 = 20;
int primitiveInt2 = wrapperInt2.intValue();  // 명시적 unboxing

// Autoboxing & Auto-unboxing (Java 5+)
Integer auto1 = 10;        // 자동 boxing
int auto2 = auto1;         // 자동 unboxing
```

### 2. 컬렉션에서 사용

```java
// ❌ 기본 타입은 컬렉션에 사용 불가
// List<int> numbers = new ArrayList<>();  // 컴파일 에러

// ✅ Wrapper 클래스 사용
List<Integer> numbers = new ArrayList<>();
numbers.add(10);        // Autoboxing
numbers.add(20);
numbers.add(30);

int first = numbers.get(0);  // Auto-unboxing
System.out.println(first);   // 10
```

### 3. null 처리

```java
// 기본 타입은 null 불가
int primitive = null;  // 컴파일 에러

// Wrapper 클래스는 null 가능
Integer wrapper = null;  // OK

// null 체크 필요
Integer value = null;
if (value != null) {
    int result = value + 10;  // NullPointerException 방지
}
```

### 4. 유틸리티 메서드

```java
// 문자열 → 숫자 변환
int num1 = Integer.parseInt("123");
double num2 = Double.parseDouble("3.14");
boolean bool = Boolean.parseBoolean("true");

// 숫자 → 문자열 변환
String str1 = Integer.toString(123);
String str2 = String.valueOf(123);

// 진법 변환
String binary = Integer.toBinaryString(10);    // "1010"
String hex = Integer.toHexString(255);         // "ff"
String octal = Integer.toOctalString(8);       // "10"

int fromBinary = Integer.parseInt("1010", 2);  // 10
int fromHex = Integer.parseInt("ff", 16);      // 255

// 최대/최소값
System.out.println(Integer.MAX_VALUE);  // 2147483647
System.out.println(Integer.MIN_VALUE);  // -2147483648
System.out.println(Double.MAX_VALUE);   // 1.7976931348623157E308
```

### 5. 캐싱 (-128 ~ 127)

```java
// Integer 캐싱 (-128 ~ 127)
Integer a = 127;
Integer b = 127;
System.out.println(a == b);  // true (같은 객체)

Integer c = 128;
Integer d = 128;
System.out.println(c == d);  // false (다른 객체)

// ✅ 항상 equals() 사용
System.out.println(c.equals(d));  // true
```

### 6. 비교 메서드

```java
Integer a = 10;
Integer b = 20;

// compare - 음수/0/양수 반환
int result = Integer.compare(a, b);  // -1 (a < b)

// compareTo - Comparable 인터페이스
int result2 = a.compareTo(b);  // -1

// equals
boolean equal = a.equals(b);  // false
```

### 7. 실전 예시: 유효성 검증

```java
public class Validator {
    public static boolean isValidAge(String input) {
        try {
            Integer age = Integer.valueOf(input);
            return age >= 0 && age <= 150;
        } catch (NumberFormatException e) {
            return false;
        }
    }
    
    public static boolean isValidPrice(String input) {
        try {
            Double price = Double.valueOf(input);
            return price >= 0;
        } catch (NumberFormatException e) {
            return false;
        }
    }
}

// 사용
System.out.println(Validator.isValidAge("25"));     // true
System.out.println(Validator.isValidAge("abc"));    // false
System.out.println(Validator.isValidPrice("9.99")); // true
```

### 8. 실전 예시: 설정 파일 파싱

```java
class Configuration {
    private Map<String, String> properties = new HashMap<>();
    
    public void load(String filePath) {
        // 설정 파일 로드
        properties.put("max.connections", "100");
        properties.put("timeout", "5000");
        properties.put("retry.enabled", "true");
        properties.put("threshold", "0.75");
    }
    
    public Integer getInt(String key, Integer defaultValue) {
        String value = properties.get(key);
        if (value == null) {
            return defaultValue;
        }
        try {
            return Integer.valueOf(value);
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }
    
    public Double getDouble(String key, Double defaultValue) {
        String value = properties.get(key);
        if (value == null) {
            return defaultValue;
        }
        try {
            return Double.valueOf(value);
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }
    
    public Boolean getBoolean(String key, Boolean defaultValue) {
        String value = properties.get(key);
        if (value == null) {
            return defaultValue;
        }
        return Boolean.valueOf(value);
    }
}

// 사용
Configuration config = new Configuration();
config.load("app.properties");

int maxConn = config.getInt("max.connections", 10);
double threshold = config.getDouble("threshold", 0.5);
boolean retryEnabled = config.getBoolean("retry.enabled", false);
```

### 9. Stream API와 함께 사용

```java
List<String> numbers = Arrays.asList("1", "2", "3", "4", "5");

// 문자열 → Integer → 계산
int sum = numbers.stream()
    .map(Integer::valueOf)  // Wrapper 사용
    .mapToInt(Integer::intValue)  // Unboxing
    .sum();

System.out.println(sum);  // 15

// Optional과 함께
Optional<Integer> max = numbers.stream()
    .map(Integer::valueOf)
    .max(Integer::compareTo);

max.ifPresent(System.out::println);  // 5
```

## 주의사항 / 함정

### 1. NullPointerException

```java
// ❌ NPE 위험
Integer value = null;
int result = value + 10;  // NullPointerException!

// ✅ null 체크
Integer value = getUserAge();
if (value != null) {
    int age = value;
}

// ✅ Optional 사용
Optional<Integer> value = Optional.ofNullable(getUserAge());
value.ifPresent(age -> System.out.println(age + 10));
```

### 2. == vs equals()

```java
// ⚠️ == 비교 주의
Integer a = 1000;
Integer b = 1000;
System.out.println(a == b);        // false
System.out.println(a.equals(b));   // true

// ✅ 항상 equals() 사용
if (a.equals(b)) {
    System.out.println("같음");
}
```

### 3. 성능 이슈

```java
// ❌ 불필요한 Boxing/Unboxing
Integer sum = 0;
for (int i = 0; i < 1000000; i++) {
    sum += i;  // 매번 boxing/unboxing 발생!
}

// ✅ 기본 타입 사용
int sum = 0;
for (int i = 0; i < 1000000; i++) {
    sum += i;  // 빠름
}
```

### 4. 불변 객체

```java
// Wrapper 클래스는 불변
Integer a = 10;
Integer b = a;
a = 20;

System.out.println(a);  // 20
System.out.println(b);  // 10 (변경 안됨)
```

### 5. 컬렉션 요소 제거

```java
List<Integer> list = new ArrayList<>(Arrays.asList(1, 2, 3));

// ⚠️ 인덱스로 제거? 값으로 제거?
list.remove(1);  // 인덱스 1 제거 → [1, 3]

// ✅ 값으로 제거하려면 Integer 객체 전달
list.remove(Integer.valueOf(1));  // 값 1 제거 → [2, 3]
```

## 관련 개념
- [[Java-Comparable-Comparator]]
- [[Java-Optional]]
- [[Java-제네릭스-Generics]]

## 면접 질문
1. Autoboxing과 Unboxing의 성능 영향은?
2. Integer 캐싱 범위와 이유는?

## 참고 자료
- Java Documentation - Wrapper Classes
- Effective Java - Item 61: Prefer primitive types