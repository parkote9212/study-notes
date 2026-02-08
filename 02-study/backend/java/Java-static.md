---
tags:
  - study
  - java
  - static
  - class-member
created: 2025-02-02
---

# Java static

## 한 줄 요약
> 클래스 레벨에서 공유되는 멤버를 정의하는 키워드

## 상세 설명

### static의 기본 개념

`static`은 클래스 레벨의 멤버(필드, 메서드)를 정의하는 키워드입니다. static 멤버는 객체가 아닌 클래스 자체에 속하며, 모든 인스턴스가 공유합니다.

**주요 특징**
- 클래스 로딩 시점에 메모리에 할당 (Method Area)
- 객체 생성 없이 접근 가능
- 모든 인스턴스가 동일한 값 공유
- 클래스명으로 직접 접근 권장

### static vs non-static

**static 멤버**
- 클래스에 속함
- 클래스명.멤버명으로 접근
- 힙 메모리가 아닌 메소드 영역에 저장
- 프로그램 종료까지 메모리에 유지

**non-static (인스턴스) 멤버**
- 객체에 속함
- 객체 생성 후 접근
- 힙 메모리에 저장
- 객체 소멸 시 함께 제거

## 코드 예시

### static 변수 (클래스 변수)

```java
class Counter {
    static int count = 0;  // static 변수
    int instanceCount = 0;  // 인스턴스 변수
    
    public Counter() {
        count++;
        instanceCount++;
    }
}

// 사용
Counter c1 = new Counter();
Counter c2 = new Counter();
Counter c3 = new Counter();

System.out.println(Counter.count);  // 3 (모든 인스턴스가 공유)
System.out.println(c1.instanceCount);  // 1 (각 인스턴스마다 별도)
System.out.println(c2.instanceCount);  // 1
System.out.println(c3.instanceCount);  // 1
```

### static 메서드

```java
class MathUtils {
    // static 메서드
    public static int add(int a, int b) {
        return a + b;
    }
    
    public static int multiply(int a, int b) {
        return a * b;
    }
}

// 사용 - 객체 생성 없이 호출
int result1 = MathUtils.add(10, 20);  // 30
int result2 = MathUtils.multiply(5, 6);  // 30

// ❌ 객체 생성해서 호출 가능하지만 비권장
MathUtils util = new MathUtils();
int result3 = util.add(1, 2);  // 가능하지만 권장 안함
```

### static 블록 (초기화 블록)

```java
class DatabaseConfig {
    static String url;
    static String username;
    static String password;
    
    // static 블록 - 클래스 로딩 시 한 번만 실행
    static {
        System.out.println("DatabaseConfig 클래스 로딩 시작");
        url = "jdbc:mysql://localhost:3306/mydb";
        username = "admin";
        password = loadPasswordFromFile();
        System.out.println("DatabaseConfig 초기화 완료");
    }
    
    private static String loadPasswordFromFile() {
        // 파일에서 비밀번호 로드
        return "secret123";
    }
}

// 사용
System.out.println(DatabaseConfig.url);  // static 블록 실행됨
```

### 여러 static 블록

```java
class InitExample {
    static int value1;
    static int value2;
    
    // 첫 번째 static 블록
    static {
        System.out.println("첫 번째 블록 실행");
        value1 = 100;
    }
    
    // 두 번째 static 블록 (순서대로 실행)
    static {
        System.out.println("두 번째 블록 실행");
        value2 = value1 + 50;
    }
}

// 출력 순서:
// 첫 번째 블록 실행
// 두 번째 블록 실행
```

### static 메서드 제약사항

```java
class Student {
    String name;  // 인스턴스 변수
    static int studentCount = 0;  // static 변수
    
    public static void printCount() {
        System.out.println("학생 수: " + studentCount);  // ✅ OK
        
        // ❌ static 메서드는 인스턴스 멤버 접근 불가
        // System.out.println(name);  // 컴파일 에러
        // printName();  // 컴파일 에러
    }
    
    public void printName() {
        System.out.println(name);  // ✅ OK
        System.out.println(studentCount);  // ✅ OK (인스턴스 메서드는 static 접근 가능)
    }
    
    public static void main(String[] args) {
        // ❌ this, super 사용 불가
        // System.out.println(this.name);  // 컴파일 에러
    }
}
```

### static import

```java
import static java.lang.Math.*;

class Calculator {
    public double calculateArea(double radius) {
        // Math.PI, Math.pow 대신 직접 사용
        return PI * pow(radius, 2);
    }
}
```

### 싱글톤 패턴 구현

```java
class Singleton {
    // static 인스턴스
    private static Singleton instance;
    
    // private 생성자
    private Singleton() {
        System.out.println("Singleton 객체 생성");
    }
    
    // static 메서드로 인스턴스 반환
    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}

// 사용
Singleton s1 = Singleton.getInstance();
Singleton s2 = Singleton.getInstance();
System.out.println(s1 == s2);  // true (같은 인스턴스)
```

### 스레드 안전한 싱글톤

```java
class ThreadSafeSingleton {
    // static final로 선언하여 초기화와 동시에 생성
    private static final ThreadSafeSingleton INSTANCE = new ThreadSafeSingleton();
    
    private ThreadSafeSingleton() { }
    
    public static ThreadSafeSingleton getInstance() {
        return INSTANCE;
    }
}
```

### 유틸리티 클래스

```java
class StringUtils {
    // 인스턴스화 방지
    private StringUtils() {
        throw new AssertionError("유틸리티 클래스는 인스턴스화할 수 없습니다");
    }
    
    public static boolean isEmpty(String str) {
        return str == null || str.trim().isEmpty();
    }
    
    public static String reverse(String str) {
        if (isEmpty(str)) return str;
        return new StringBuilder(str).reverse().toString();
    }
    
    public static String capitalize(String str) {
        if (isEmpty(str)) return str;
        return str.substring(0, 1).toUpperCase() + str.substring(1).toLowerCase();
    }
}

// 사용
System.out.println(StringUtils.isEmpty(""));  // true
System.out.println(StringUtils.reverse("hello"));  // olleh
System.out.println(StringUtils.capitalize("java"));  // Java
```

### static 중첩 클래스

```java
class OuterClass {
    private static String staticField = "Static Field";
    private String instanceField = "Instance Field";
    
    // static 중첩 클래스
    static class StaticNested {
        public void print() {
            System.out.println(staticField);  // ✅ OK
            // System.out.println(instanceField);  // ❌ 에러
        }
    }
}

// 사용 - 외부 클래스 인스턴스 없이 생성 가능
OuterClass.StaticNested nested = new OuterClass.StaticNested();
nested.print();
```

### 실무 예시: 설정 관리

```java
class AppConfig {
    private static final String APP_NAME = "MyApplication";
    private static final String VERSION = "1.0.0";
    private static final int MAX_CONNECTIONS = 100;
    
    private static boolean debugMode = false;
    
    static {
        // 환경 변수에서 디버그 모드 설정
        String debug = System.getenv("DEBUG_MODE");
        if ("true".equalsIgnoreCase(debug)) {
            debugMode = true;
        }
    }
    
    public static String getAppInfo() {
        return APP_NAME + " v" + VERSION;
    }
    
    public static boolean isDebugMode() {
        return debugMode;
    }
}

// 사용
System.out.println(AppConfig.getAppInfo());  // MyApplication v1.0.0
if (AppConfig.isDebugMode()) {
    System.out.println("디버그 모드 활성화");
}
```

### 카운터 예시

```java
class VisitorCounter {
    private static int totalVisitors = 0;
    private static int currentOnline = 0;
    
    public static synchronized void enter() {
        totalVisitors++;
        currentOnline++;
    }
    
    public static synchronized void exit() {
        currentOnline--;
    }
    
    public static int getTotalVisitors() {
        return totalVisitors;
    }
    
    public static int getCurrentOnline() {
        return currentOnline;
    }
}

// 사용
VisitorCounter.enter();
VisitorCounter.enter();
VisitorCounter.enter();
System.out.println("총 방문자: " + VisitorCounter.getTotalVisitors());  // 3
System.out.println("현재 접속: " + VisitorCounter.getCurrentOnline());  // 3

VisitorCounter.exit();
System.out.println("현재 접속: " + VisitorCounter.getCurrentOnline());  // 2
```

## 주의사항 / 함정

### 1. 메모리 누수 위험

```java
class DataCache {
    // ❌ static 컬렉션은 프로그램 종료까지 메모리 유지
    private static List<byte[]> cache = new ArrayList<>();
    
    public static void addData(byte[] data) {
        cache.add(data);  // 계속 쌓임, GC 안됨
    }
}

// 해결책: 필요 시 clear() 호출
public static void clearCache() {
    cache.clear();
}
```

### 2. 멀티스레드 환경에서의 동시성 문제

```java
class UnsafeCounter {
    private static int count = 0;
    
    // ❌ 스레드 안전하지 않음
    public static void increment() {
        count++;  // 여러 스레드가 동시 접근 시 문제
    }
}

// ✅ 동기화 적용
class SafeCounter {
    private static int count = 0;
    
    public static synchronized void increment() {
        count++;
    }
}

// ✅ AtomicInteger 사용 (더 나은 성능)
class BetterCounter {
    private static AtomicInteger count = new AtomicInteger(0);
    
    public static void increment() {
        count.incrementAndGet();
    }
}
```

### 3. static 변수 초기화 순서

```java
class InitOrder {
    // ❌ 초기화 순서 주의
    static int value1 = getValue2();  // 0 반환 (value2가 아직 초기화 안됨)
    static int value2 = 100;
    
    static int getValue2() {
        return value2;
    }
}

System.out.println(InitOrder.value1);  // 0 (예상과 다름!)
```

### 4. 테스트 어려움

```java
class UserService {
    private static UserRepository repository = new UserRepository();
    
    // ❌ 테스트 시 Mock 객체로 교체 어려움
    public static User getUser(Long id) {
        return repository.findById(id);
    }
}

// ✅ 인스턴스 메서드로 변경하여 DI 적용
class UserService {
    private UserRepository repository;
    
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
    
    public User getUser(Long id) {
        return repository.findById(id);
    }
}
```

### 5. 상속과 static

```java
class Parent {
    static void print() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    static void print() {
        System.out.println("Child");
    }
}

// ⚠️ static 메서드는 오버라이딩이 아니라 숨김(hiding)
Parent p = new Child();
p.print();  // "Parent" 출력 (실제 타입이 아닌 참조 타입 기준)

Child c = new Child();
c.print();  // "Child" 출력
```

### 6. static 변수의 생명주기

```java
class Session {
    static Map<String, User> userSessions = new HashMap<>();
    
    // ❌ 프로그램 종료까지 메모리에 유지
    // 웹 애플리케이션에서 재배포 시에도 남아있을 수 있음
}

// ✅ 인스턴스 변수로 변경하거나 적절한 제거 로직 필요
```

## 관련 개념
- [[Java-final]]
- [[Java-메모리구조]]

## 면접 질문
1. static 변수와 인스턴스 변수의 차이점은 무엇인가요?
2. static 메서드에서 인스턴스 변수에 접근할 수 없는 이유는?

## 참고 자료
- Effective Java 3/E - Item 4 (인스턴스화를 막으려거든 private 생성자를 사용하라)
- Java Language Specification - Static Members