---
tags:
  - study
  - java
  - jvm
  - memory
  - gc
created: 2025-02-08
---

# Java 메모리 구조

## 한 줄 요약
> JVM의 메모리 영역(Heap, Stack, Method Area)과 가비지 컬렉션 동작 원리

## 상세 설명

### JVM 메모리 구조

JVM(Java Virtual Machine)은 프로그램을 실행하기 위해 메모리를 여러 영역으로 나누어 관리합니다.

**주요 메모리 영역**
1. **Heap** - 객체와 배열이 저장되는 공간
2. **Stack** - 메서드 호출과 지역 변수가 저장되는 공간
3. **Method Area** - 클래스 메타데이터가 저장되는 공간
4. **PC Register** - 현재 실행 중인 명령어 주소
5. **Native Method Stack** - Native 메서드 실행 스택

**왜 중요한가?**
- 메모리 누수(Memory Leak) 이해 및 방지
- 성능 최적화
- OutOfMemoryError 대응
- 면접 단골 질문

## 코드 예시

### 1. Heap 영역 - 객체 저장소

Heap은 모든 객체와 배열이 저장되는 공간입니다. 모든 스레드가 공유합니다.

```java
class Person {
    String name;  // Heap에 저장될 String 객체 참조
    int age;      // 기본형 데이터
    
    public Person(String name, int age) {
        this.name = name;  // Heap에 새로운 String 객체 생성
        this.age = age;
    }
}

public class HeapExample {
    public static void main(String[] args) {
        // Heap에 Person 객체 생성
        Person p1 = new Person("Alice", 25);
        
        // Heap에 또 다른 Person 객체 생성
        Person p2 = new Person("Bob", 30);
        
        // Heap에 배열 객체 생성
        int[] numbers = new int[100];
        
        // p1과 p2는 Stack에 저장된 참조 변수
        // 실제 Person 객체는 Heap에 존재
    }
}
```

**Heap의 특징**
- 객체와 배열 저장
- GC(Garbage Collector)가 관리
- 크기가 크고 동적 할당
- 모든 스레드가 공유
- 느린 접근 속도 (Stack 대비)

### 2. Stack 영역 - 메서드 실행 공간

Stack은 메서드 호출 정보와 지역 변수를 저장합니다. 각 스레드마다 독립적인 Stack을 가집니다.

```java
public class StackExample {
    public static void main(String[] args) {
        int x = 10;           // Stack에 저장
        String str = "Hello"; // Stack에 참조 저장, Heap에 "Hello" 객체
        
        methodA(x);
    }
    
    public static void methodA(int a) {
        int b = 20;  // Stack에 저장
        methodB(a + b);
    }
    
    public static void methodB(int c) {
        int d = 30;  // Stack에 저장
        System.out.println(c + d);
    }
}
```

**Stack Frame 구조**
```
+------------------+
| methodB()        |  <- 가장 최근 호출
| - c = 30         |
| - d = 30         |
+------------------+
| methodA()        |
| - a = 10         |
| - b = 20         |
+------------------+
| main()           |
| - x = 10         |
| - str (참조)     |
+------------------+
```

**Stack의 특징**
- 메서드 호출 시 생성, 종료 시 제거
- LIFO (Last In First Out) 구조
- 지역 변수와 매개변수 저장
- 빠른 접근 속도
- 크기가 작음 (기본 1MB)
- 스레드마다 독립적

### 3. Stack vs Heap 비교

```java
public class MemoryComparison {
    public static void main(String[] args) {
        // Stack에 저장
        int primitiveValue = 100;
        
        // Stack에 참조 저장, Heap에 객체 저장
        Integer wrapperValue = 100;
        
        // Stack에 참조 저장, Heap에 배열 저장
        int[] array = {1, 2, 3};
        
        // 메서드 호출
        calculate(primitiveValue, wrapperValue);
        // calculate() 종료 후 해당 Stack Frame 제거
        
        System.out.println(primitiveValue);  // 100 (변경 안됨)
        System.out.println(wrapperValue);    // 100 (불변 객체)
    }
    
    public static void calculate(int a, Integer b) {
        a = 200;  // Stack의 복사본 변경
        b = 200;  // Stack의 참조만 변경 (원본 객체는 불변)
        
        // 메서드 종료 시 a, b는 Stack에서 제거
    }
}
```

### 4. Method Area (Metaspace in Java 8+)

클래스의 메타데이터, static 변수, 상수 등이 저장됩니다.

```java
public class MethodAreaExample {
    // Method Area에 저장
    private static int staticVar = 100;
    private static final String CONSTANT = "상수";
    
    // Method Area에 클래스 정보 저장
    // - 클래스 이름, 부모 클래스, 인터페이스
    // - 필드 정보, 메서드 정보
    // - 상수 풀 (Constant Pool)
    
    public static void main(String[] args) {
        // staticVar는 Method Area에 저장
        System.out.println(staticVar);
        
        // 리플렉션으로 Method Area의 클래스 정보 조회
        Class<?> clazz = MethodAreaExample.class;
        System.out.println(clazz.getName());
    }
}
```

**Method Area의 특징**
- 클래스 메타데이터 저장
- static 변수 저장
- 상수 풀 (Constant Pool)
- 모든 스레드가 공유
- Java 8부터 Metaspace로 변경 (Native Memory 사용)

### 5. String Pool (Heap 내부)

String 리터럴은 Heap의 String Pool에 저장됩니다.

```java
public class StringPoolExample {
    public static void main(String[] args) {
        // String Pool에 "Hello" 저장
        String s1 = "Hello";
        String s2 = "Hello";
        
        // String Pool의 같은 객체 참조
        System.out.println(s1 == s2);  // true
        
        // Heap에 새로운 String 객체 생성
        String s3 = new String("Hello");
        
        // 다른 객체
        System.out.println(s1 == s3);  // false
        
        // intern()으로 String Pool에 추가
        String s4 = s3.intern();
        System.out.println(s1 == s4);  // true
    }
}
```

## Garbage Collection (GC)

### GC의 역할

Heap 메모리에서 더 이상 사용되지 않는 객체를 자동으로 제거합니다.

```java
public class GCExample {
    public static void main(String[] args) {
        // Heap에 Person 객체 생성
        Person p1 = new Person("Alice", 25);
        
        // p1의 참조를 null로 변경
        p1 = null;  // 원래 Person 객체는 GC 대상
        
        // 새로운 객체 생성
        Person p2 = new Person("Bob", 30);
        
        // 메서드 호출
        createTemporaryObject();
        // 메서드 종료 후 temp 객체는 GC 대상
        
        // GC 실행 제안 (권장하지 않음)
        System.gc();
    }
    
    public static void createTemporaryObject() {
        Person temp = new Person("Temp", 0);
        // 메서드 종료 시 temp는 Stack에서 제거
        // Person 객체는 참조가 없으므로 GC 대상
    }
}
```

### Heap의 세대별 구조 (Generational GC)

```
+------------------------------------------------+
|                   Heap                         |
+------------------------------------------------+
|  Young Generation          | Old Generation   |
+---------------------------+-------------------+
| Eden | S0 | S1            |                   |
+---------------------------+-------------------+

Young Generation:
- Eden: 새로운 객체가 생성되는 공간
- S0, S1 (Survivor): Minor GC에서 살아남은 객체

Old Generation:
- Young에서 오래 살아남은 객체 이동
- Major GC (Full GC) 발생
```

### Minor GC vs Major GC

```java
public class GCTypeExample {
    public static void main(String[] args) {
        // Minor GC 발생 예시
        for (int i = 0; i < 1000000; i++) {
            // Eden 영역에 계속 객체 생성
            String temp = new String("Temp " + i);
            // temp는 즉시 참조 해제 → Minor GC 대상
        }
        
        // 오래 살아남는 객체 (Old Generation으로 이동)
        List<String> longLived = new ArrayList<>();
        for (int i = 0; i < 100000; i++) {
            longLived.add("Item " + i);
        }
        // longLived는 계속 참조되어 Old로 이동
        
        // Old Generation이 가득 차면 Major GC 발생
    }
}
```

### GC 알고리즘 종류

**1. Serial GC** - 단일 스레드
```
// -XX:+UseSerialGC
// 소형 애플리케이션, CPU 1개
```

**2. Parallel GC** - 멀티 스레드 (Default in Java 8)
```
// -XX:+UseParallelGC
// 처리량(Throughput) 중시
```

**3. CMS (Concurrent Mark Sweep)** - 낮은 지연시간
```
// -XX:+UseConcMarkSweepGC (Deprecated in Java 9)
// 응답 시간 중시
```

**4. G1 GC** - 대용량 Heap (Default in Java 9+)
```
// -XX:+UseG1GC
// 균형잡힌 성능
```

**5. ZGC** - 초저지연 (Java 11+)
```
// -XX:+UseZGC
// 대용량 Heap, 10ms 이하 지연
```

## 실무 예시

### 1. 메모리 누수 패턴

```java
// ❌ 메모리 누수 - static 컬렉션
public class MemoryLeakExample {
    private static List<Object> cache = new ArrayList<>();
    
    public void addToCache(Object obj) {
        cache.add(obj);  // 계속 누적, GC 불가
    }
}

// ✅ 해결: WeakHashMap 사용
public class FixedExample {
    private static Map<Object, Object> cache = new WeakHashMap<>();
    
    public void addToCache(Object key, Object value) {
        cache.put(key, value);  // 키가 GC되면 자동 제거
    }
}
```

### 2. StackOverflowError

```java
// ❌ 무한 재귀 - Stack 공간 초과
public class StackOverflowExample {
    public static void recursion() {
        recursion();  // 종료 조건 없음
    }
    
    public static void main(String[] args) {
        recursion();  // StackOverflowError
    }
}

// ✅ 해결: 종료 조건 추가
public class FixedRecursion {
    public static void recursion(int depth) {
        if (depth <= 0) return;  // 종료 조건
        recursion(depth - 1);
    }
    
    public static void main(String[] args) {
        recursion(10);  // 안전
    }
}
```

### 3. OutOfMemoryError: Heap space

```java
// ❌ Heap 메모리 부족
public class HeapOOMExample {
    public static void main(String[] args) {
        List<byte[]> list = new ArrayList<>();
        while (true) {
            list.add(new byte[1024 * 1024]);  // 1MB씩 추가
            // OutOfMemoryError: Java heap space
        }
    }
}

// ✅ 해결: 메모리 관리
public class FixedHeapExample {
    public static void main(String[] args) {
        List<byte[]> list = new ArrayList<>();
        
        for (int i = 0; i < 100; i++) {
            list.add(new byte[1024 * 1024]);
            
            // 주기적으로 정리
            if (i % 10 == 0) {
                list.clear();
            }
        }
    }
}
```

### 4. 메모리 효율적인 코드

```java
// ❌ 비효율적 - 불필요한 객체 생성
public class InefficientCode {
    public String concatenate(String[] words) {
        String result = "";
        for (String word : words) {
            result += word;  // 매번 새 String 객체 생성
        }
        return result;
    }
}

// ✅ 효율적 - StringBuilder 사용
public class EfficientCode {
    public String concatenate(String[] words) {
        StringBuilder sb = new StringBuilder();
        for (String word : words) {
            sb.append(word);  // 기존 객체 재사용
        }
        return sb.toString();
    }
}
```

### 5. 지역 변수 vs 인스턴스 변수

```java
public class VariableScope {
    // Heap (객체 생명주기 동안 유지)
    private List<String> instanceList = new ArrayList<>();
    
    public void process() {
        // Stack (메서드 종료 시 제거)
        List<String> localList = new ArrayList<>();
        
        for (int i = 0; i < 1000; i++) {
            localList.add("Item " + i);
        }
        
        // 메서드 종료 시 localList는 GC 대상
        // instanceList는 계속 유지
    }
}
```

### 6. Soft/Weak/Phantom Reference

```java
import java.lang.ref.*;

public class ReferenceExample {
    public static void main(String[] args) {
        // 강한 참조 (Strong Reference)
        Object strong = new Object();  // GC 대상 아님
        
        // 약한 참조 (Weak Reference)
        WeakReference<Object> weak = new WeakReference<>(new Object());
        System.out.println(weak.get());  // 객체 존재
        System.gc();
        System.out.println(weak.get());  // null (GC됨)
        
        // 부드러운 참조 (Soft Reference) - 캐시용
        SoftReference<Object> soft = new SoftReference<>(new Object());
        // 메모리 부족할 때만 GC
        
        // 유령 참조 (Phantom Reference) - 정리 작업용
        ReferenceQueue<Object> queue = new ReferenceQueue<>();
        PhantomReference<Object> phantom = 
            new PhantomReference<>(new Object(), queue);
        // 객체 제거 후 정리 작업
    }
}
```

## 주의사항 / 함정

### 1. finalize() 메서드 사용 지양

```java
// ❌ 사용하지 말 것 (Deprecated in Java 9)
public class BadFinalizer {
    @Override
    protected void finalize() throws Throwable {
        // GC 시점을 예측할 수 없음
        // 성능 저하
        // 리소스가 제때 정리 안될 수 있음
    }
}

// ✅ try-with-resources 사용
public class GoodCleanup implements AutoCloseable {
    @Override
    public void close() {
        // 확실한 리소스 정리
    }
    
    public static void main(String[] args) {
        try (GoodCleanup resource = new GoodCleanup()) {
            // 사용
        }  // 자동으로 close() 호출
    }
}
```

### 2. System.gc() 호출 지양

```java
// ❌ 명시적 GC 호출 (권장하지 않음)
public class BadGC {
    public void cleanup() {
        System.gc();  // JVM에게 제안일 뿐, 강제 아님
        // 성능 저하 가능
    }
}

// ✅ JVM이 알아서 관리하도록
public class GoodGC {
    public void cleanup() {
        // 참조 해제만 해주기
        largeObject = null;
        // JVM이 적절한 시점에 GC
    }
}
```

### 3. String 연결 최적화

```java
// ❌ 반복문에서 String 연결
public class BadStringConcat {
    public String concat(int n) {
        String result = "";
        for (int i = 0; i < n; i++) {
            result += i;  // O(n²) 성능, 많은 객체 생성
        }
        return result;
    }
}

// ✅ StringBuilder 사용
public class GoodStringConcat {
    public String concat(int n) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append(i);  // O(n) 성능
        }
        return sb.toString();
    }
}
```

### 4. 큰 컬렉션 주의

```java
// ❌ 크기 제한 없는 컬렉션
public class UnboundedCache {
    private static Map<String, byte[]> cache = new HashMap<>();
    
    public void add(String key, byte[] data) {
        cache.put(key, data);  // 무한정 증가 가능
    }
}

// ✅ 크기 제한
public class BoundedCache {
    private static final int MAX_SIZE = 1000;
    private LinkedHashMap<String, byte[]> cache = 
        new LinkedHashMap<>(MAX_SIZE, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry eldest) {
                return size() > MAX_SIZE;
            }
        };
}
```

### 5. ThreadLocal 정리

```java
// ❌ ThreadLocal 정리 안함
public class BadThreadLocal {
    private static ThreadLocal<byte[]> threadLocal = 
        ThreadLocal.withInitial(() -> new byte[1024 * 1024]);
    
    public void process() {
        byte[] data = threadLocal.get();
        // 사용 후 정리 안함 → 메모리 누수
    }
}

// ✅ 사용 후 정리
public class GoodThreadLocal {
    private static ThreadLocal<byte[]> threadLocal = 
        ThreadLocal.withInitial(() -> new byte[1024 * 1024]);
    
    public void process() {
        try {
            byte[] data = threadLocal.get();
            // 사용
        } finally {
            threadLocal.remove();  // 반드시 정리
        }
    }
}
```

## 관련 개념
- [[Java-static-final]]
- [[Java-제네릭스-Generics]]
- [[Java-문자열처리-String]]
- [[Java-예외처리-Exception]]

## 면접 질문
1. JVM의 메모리 구조를 설명하세요.
2. Stack과 Heap의 차이점은?
3. GC의 동작 원리는?
4. Minor GC와 Major GC의 차이는?
5. 메모리 누수를 방지하는 방법은?
6. String Pool이 무엇인가요?
7. OutOfMemoryError가 발생하는 경우와 해결 방법은?

## 참고 자료
- Effective Java 3/E - Item 7 (다 쓴 객체 참조를 해제하라)
- Java Performance: The Definitive Guide
- JVM Specification - Memory Management
