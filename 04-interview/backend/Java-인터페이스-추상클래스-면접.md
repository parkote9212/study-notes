---
tags:
  - interview
  - java
  - oop
  - interface
created: 2026-01-31
difficulty: 중
---

# Java 인터페이스와 추상클래스 면접

## 질문 1: 추상클래스와 인터페이스의 차이는?

### 핵심 답변 (3줄)
1. 추상클래스는 is-a 관계의 상속 구조에서 공통 기능을 제공하고, 인터페이스는 can-do 관계의 기능 명세입니다.
2. 추상클래스는 단일 상속만 가능하지만 일반 메서드와 필드를 가질 수 있고, 인터페이스는 다중 구현이 가능하지만 상수만 가질 수 있습니다.
3. 추상클래스는 생성자를 가질 수 있지만, 인터페이스는 생성자를 가질 수 없습니다.

### 상세 설명

**비교표**:
| 구분 | 추상클래스 | 인터페이스 |
|------|----------|----------|
| 키워드 | `abstract class` | `interface` |
| 상속/구현 | 단일 상속 (`extends`) | 다중 구현 (`implements`) |
| 메서드 | 추상/일반 메서드 모두 | 추상/default/static (Java 8+) |
| 필드 | 모든 종류 가능 | `public static final`만 (상수) |
| 생성자 | 가능 | 불가능 |
| 접근 제어자 | 모두 가능 | `public`만 (생략 가능) |
| 관계 | is-a (상속) | can-do (기능) |

**코드 예시**:
```java
// 추상클래스: 공통 속성과 기능
public abstract class Animal {
    protected String name;  // 일반 필드
    
    public Animal(String name) {  // 생성자
        this.name = name;
    }
    
    public void sleep() {  // 일반 메서드 (구현 포함)
        System.out.println(name + " 잡니다");
    }
    
    public abstract void sound();  // 추상 메서드
}

// 인터페이스: 기능 명세
public interface Flyable {
    int MAX_HEIGHT = 10000;  // 상수 (자동으로 public static final)
    
    void fly();  // 추상 메서드 (자동으로 public abstract)
    
    default void land() {  // Java 8+ default 메서드
        System.out.println("착륙합니다");
    }
}

// 사용: 추상클래스는 단일 상속, 인터페이스는 다중 구현
public class Bird extends Animal implements Flyable, Swimmable {
    public Bird(String name) {
        super(name);
    }
    
    @Override
    public void sound() {
        System.out.println("짹짹");
    }
    
    @Override
    public void fly() {
        System.out.println("날아갑니다");
    }
    
    @Override
    public void swim() {
        System.out.println("수영합니다");
    }
}
```

### 꼬리 질문 예상
- Java 8 이후 인터페이스에 default 메서드가 추가되면서 추상클래스와의 차이가 줄어들었는데, 추상클래스는 여전히 필요한가? → 네, 생성자와 상태(필드)를 가질 수 있어서 여전히 유용.
- 다중 상속의 문제점은? → 다이아몬드 문제 (같은 메서드를 여러 부모에서 상속 시 충돌).
- 추상클래스 없이 인터페이스만 사용할 수 있나? → 가능하지만 코드 중복 발생. 공통 로직은 추상클래스가 유리.

## 질문 2: 언제 추상클래스를 사용하고 언제 인터페이스를 사용하나?

### 핵심 답변 (3줄)
1. 추상클래스는 관련된 클래스들 간에 공통 코드를 공유할 때 사용합니다.
2. 인터페이스는 서로 관련 없는 클래스들이 같은 기능을 구현할 때 사용합니다.
3. 변경 가능성이 있으면 추상클래스, 확장 가능성이 중요하면 인터페이스를 선택합니다.

### 상세 설명

**추상클래스 사용 시기**:

**1) 공통 코드 공유가 필요할 때**:
```java
// ✅ 좋은 예: 공통 로직을 추상클래스에
public abstract class HttpServlet {
    // 공통 필드
    protected HttpRequest request;
    protected HttpResponse response;
    
    // 공통 메서드 (모든 서블릿이 사용)
    public void service() {
        init();
        doProcess();
        destroy();
    }
    
    protected void init() {
        // 공통 초기화 로직
    }
    
    // 자식이 구현할 부분만 추상 메서드로
    protected abstract void doProcess();
}

public class LoginServlet extends HttpServlet {
    @Override
    protected void doProcess() {
        // 로그인 로직만 구현
    }
}
```

**2) 상태(필드)를 가져야 할 때**:
```java
public abstract class BaseEntity {
    protected Long id;
    protected LocalDateTime createdAt;
    protected LocalDateTime updatedAt;
    
    public void onCreate() {
        this.createdAt = LocalDateTime.now();
    }
    
    public abstract void validate();
}
```

**3) 생성자가 필요할 때**:
```java
public abstract class Game {
    protected String title;
    protected int playerCount;
    
    public Game(String title, int playerCount) {
        this.title = title;
        this.playerCount = playerCount;
    }
    
    public abstract void start();
}
```

**인터페이스 사용 시기**:

**1) 관련 없는 클래스들이 같은 기능 구현**:
```java
// Comparable: String, Integer, Date 등 서로 관련 없지만 모두 비교 가능
public interface Comparable<T> {
    int compareTo(T o);
}

public class Person implements Comparable<Person> {
    @Override
    public int compareTo(Person o) {
        return this.age - o.age;
    }
}
```

**2) 다중 구현이 필요할 때**:
```java
// ✅ 좋은 예: 여러 기능을 조합
public class SmartPhone implements Callable, Messageable, Photographable {
    @Override
    public void call() { }
    
    @Override
    public void sendMessage() { }
    
    @Override
    public void takePhoto() { }
}
```

**3) API 명세 정의 (구현과 분리)**:
```java
// 결제 API 명세
public interface PaymentGateway {
    PaymentResult process(PaymentRequest request);
    void refund(String transactionId);
}

// 여러 구현체 (카카오페이, 토스페이 등)
public class KakaoPayGateway implements PaymentGateway { }
public class TossPayGateway implements PaymentGateway { }
```

**실무 판단 기준**:
```java
// ❌ 나쁜 예: 인터페이스에 공통 코드 없음
public interface Vehicle {
    void start();
    void stop();
    void accelerate();
}
// → 모든 구현체에서 start/stop 로직 중복

// ✅ 좋은 예: 공통 로직은 추상클래스에
public abstract class AbstractVehicle {
    protected boolean isRunning;
    
    public void start() {  // 공통 로직
        if (!isRunning) {
            startEngine();
            isRunning = true;
        }
    }
    
    protected abstract void startEngine();  // 차량마다 다른 부분만
}
```

### 꼬리 질문 예상
- 둘 다 사용할 수 있는 상황이라면? → 인터페이스 우선 (유연성). 공통 코드가 많으면 추상클래스 추가.
- Template Method 패턴과의 관계는? → 추상클래스의 대표적인 활용 패턴 (공통 흐름 정의, 세부 구현은 자식에게).
- Strategy 패턴과의 관계는? → 인터페이스의 대표적인 활용 패턴 (다양한 알고리즘 교체 가능).

## 질문 3: Java 8의 default 메서드가 추가된 이유는?

### 핵심 답변 (3줄)
1. 기존 인터페이스에 새로운 메서드를 추가할 때 하위 호환성을 유지하기 위해서입니다.
2. default 메서드가 없으면 인터페이스에 메서드를 추가할 때 모든 구현 클래스를 수정해야 합니다.
3. Collection 인터페이스에 stream(), forEach() 같은 새 메서드를 추가하면서 도입되었습니다.

### 상세 설명

**문제 상황 (Java 8 이전)**:
```java
// Java 7까지의 Collection 인터페이스
public interface Collection<E> {
    boolean add(E e);
    boolean remove(Object o);
    // ... 기존 메서드들
}

// 수많은 구현체들
public class ArrayList<E> implements Collection<E> { }
public class HashSet<E> implements Collection<E> { }
// ... 수백 개의 구현체

// ❌ 문제: 새로운 메서드 추가 불가
public interface Collection<E> {
    void forEach(Consumer<? super E> action);  // 추가하면?
    // → 모든 구현체에서 컴파일 에러!
}
```

**해결: default 메서드**:
```java
// Java 8의 Collection 인터페이스
public interface Collection<E> {
    boolean add(E e);
    boolean remove(Object o);
    
    // ✅ default 메서드로 추가
    default void forEach(Consumer<? super E> action) {
        for (E e : this) {
            action.accept(e);
        }
    }
    
    default Stream<E> stream() {
        return StreamSupport.stream(spliterator(), false);
    }
}

// 기존 구현체들은 수정 불필요!
ArrayList<String> list = new ArrayList<>();
list.forEach(System.out::println);  // 바로 사용 가능
```

**실무 예제**:
```java
// 버전 1: 초기 인터페이스
public interface Logger {
    void log(String message);
}

public class FileLogger implements Logger {
    @Override
    public void log(String message) {
        // 파일에 로그 기록
    }
}

// 버전 2: 새 기능 추가 필요
public interface Logger {
    void log(String message);
    
    // ✅ default 메서드로 추가 (기존 구현체 수정 불필요)
    default void logWithTimestamp(String message) {
        String timestamp = LocalDateTime.now().toString();
        log("[" + timestamp + "] " + message);
    }
    
    default void logError(String message) {
        log("ERROR: " + message);
    }
}

// FileLogger는 수정 없이도 새 메서드 사용 가능
FileLogger logger = new FileLogger();
logger.logWithTimestamp("시스템 시작");  // 바로 사용!
```

**default 메서드의 특징**:
1. 구현 포함 가능
2. 오버라이드 선택 사항
3. 인터페이스 간 상속 가능
4. 다중 구현 시 충돌 가능 (명시적 해결 필요)

```java
public interface A {
    default void print() {
        System.out.println("A");
    }
}

public interface B {
    default void print() {
        System.out.println("B");
    }
}

// ❌ 컴파일 에러: 충돌
public class C implements A, B {
}

// ✅ 해결: 명시적 오버라이드
public class C implements A, B {
    @Override
    public void print() {
        A.super.print();  // A의 print 사용
        // 또는 B.super.print();
        // 또는 새로운 구현
    }
}
```

### 꼬리 질문 예상
- default 메서드 때문에 인터페이스가 추상클래스와 비슷해진 것 아닌가? → 비슷하지만 차이 있음 (상태 없음, 생성자 없음).
- 모든 메서드를 default로 만들면? → 인터페이스의 의미 퇴색. 강제성 사라짐.
- private 메서드는 왜 추가됐나? (Java 9+) → default/static 메서드 간 코드 중복 제거 목적.

## 질문 4: 인터페이스에서 다중 구현이 가능한 이유는?

### 핵심 답변 (3줄)
1. 인터페이스는 구현이 없는 명세만 정의하므로 다이아몬드 문제가 발생하지 않기 때문입니다.
2. 추상클래스는 상태와 구현을 가지므로 다중 상속 시 충돌이 발생할 수 있습니다.
3. Java 8의 default 메서드는 예외적으로 충돌 가능하지만, 명시적 오버라이드로 해결합니다.

### 상세 설명

**다이아몬드 문제 (Diamond Problem)**:
```java
// C++처럼 다중 상속이 가능하다면...
class A {
    void method() {
        System.out.println("A");
    }
}

class B extends A {
    @Override
    void method() {
        System.out.println("B");
    }
}

class C extends A {
    @Override
    void method() {
        System.out.println("C");
    }
}

// ❌ 문제: D는 B와 C 중 누구의 method()를 상속?
class D extends B, C {  // Java는 불가능
    // method()를 호출하면 B의 것? C의 것?
}
```

**인터페이스는 다중 구현 가능**:
```java
// 인터페이스는 구현이 없으므로 충돌 없음
public interface Flyable {
    void fly();  // 구현 없음
}

public interface Swimmable {
    void swim();  // 구현 없음
}

// ✅ 가능: 구현은 Duck이 직접 하므로 충돌 없음
public class Duck implements Flyable, Swimmable {
    @Override
    public void fly() {
        System.out.println("오리가 날아갑니다");
    }
    
    @Override
    public void swim() {
        System.out.println("오리가 수영합니다");
    }
}
```

**default 메서드의 충돌 해결**:
```java
public interface A {
    default void method() {
        System.out.println("A");
    }
}

public interface B {
    default void method() {
        System.out.println("B");
    }
}

// ❌ 컴파일 에러: 충돌 발생
public class C implements A, B {
}

// ✅ 해결 1: 명시적 선택
public class C implements A, B {
    @Override
    public void method() {
        A.super.method();  // A의 구현 사용
    }
}

// ✅ 해결 2: 새로운 구현
public class C implements A, B {
    @Override
    public void method() {
        System.out.println("C - 새로운 구현");
    }
}

// ✅ 해결 3: 둘 다 호출
public class C implements A, B {
    @Override
    public void method() {
        A.super.method();
        B.super.method();
    }
}
```

**충돌 우선순위 규칙**:
1. **클래스가 최우선**: 클래스의 메서드 > 인터페이스의 default 메서드
2. **서브 인터페이스 우선**: 더 구체적인 인터페이스 > 상위 인터페이스
3. **명시적 선택 필요**: 같은 레벨의 인터페이스는 명시적으로 선택

```java
public interface A {
    default void method() {
        System.out.println("A");
    }
}

public interface B extends A {
    default void method() {
        System.out.println("B");
    }
}

public class C implements A, B {
    // B가 A의 서브 인터페이스이므로 B의 method() 사용
    // 오버라이드 안 해도 됨
}
```

### 꼬리 질문 예상
- Trait(Scala, PHP) vs Interface의 차이는? → Trait는 상태도 가질 수 있음.
- Mixin 패턴과의 관계는? → 인터페이스 다중 구현이 Mixin 패턴의 Java 구현 방식.
- 언어마다 다중 상속 정책이 다른 이유는? → 언어 설계 철학 차이 (안전성 vs 유연성).

## 질문 5: 추상클래스는 왜 객체 생성이 불가능한가?

### 핵심 답변 (3줄)
1. 추상클래스는 미완성 설계도이므로 그 자체로는 완전한 객체를 만들 수 없습니다.
2. 추상 메서드는 구현이 없어서 호출하면 실행할 코드가 없기 때문입니다.
3. 추상클래스는 상속을 통해 자식 클래스가 완성한 후에야 객체화가 가능합니다.

### 상세 설명

**추상클래스는 불완전한 설계도**:
```java
public abstract class Animal {
    protected String name;
    
    public Animal(String name) {
        this.name = name;
    }
    
    // 구현된 메서드
    public void sleep() {
        System.out.println(name + " 잡니다");
    }
    
    // 구현 없는 추상 메서드
    public abstract void sound();  // 어떻게 실행?
}

// ❌ 컴파일 에러: 객체 생성 불가
Animal animal = new Animal("동물");
animal.sound();  // 실행할 코드가 없음!
```

**생성자는 있지만 직접 호출은 불가**:
```java
public abstract class Animal {
    protected String name;
    
    // 생성자 존재 (자식 클래스에서 super()로 호출)
    public Animal(String name) {
        this.name = name;
        System.out.println("Animal 생성자 호출");
    }
    
    public abstract void sound();
}

// ❌ 직접 인스턴스화 불가
Animal animal = new Animal("동물");

// ✅ 자식 클래스에서 생성자 활용
public class Dog extends Animal {
    public Dog(String name) {
        super(name);  // 부모 생성자 호출은 가능
    }
    
    @Override
    public void sound() {
        System.out.println("멍멍");
    }
}

Animal dog = new Dog("뽀삐");  // 가능
```

**익명 클래스로는 객체 생성 가능**:
```java
// ✅ 익명 클래스: 즉석에서 추상 메서드 구현
Animal animal = new Animal("동물") {
    @Override
    public void sound() {
        System.out.println("소리");
    }
};

animal.sound();  // "소리" 출력

// 실제로는 익명의 자식 클래스를 만들어서 인스턴스화
// Animal$1.class 파일 생성됨
```

**추상 메서드가 없어도 abstract 선언 가능**:
```java
// 추상 메서드 없지만 abstract로 선언 가능
public abstract class BaseController {
    public void execute() {
        System.out.println("실행");
    }
}

// ❌ 여전히 객체 생성 불가
BaseController controller = new BaseController();

// 목적: 직접 사용 방지, 상속만 강제
public class UserController extends BaseController {
    // BaseController의 메서드 활용
}
```

**실무 활용 예시**:
```java
// 템플릿 메서드 패턴
public abstract class DataProcessor {
    // 전체 흐름 정의 (변경 불가)
    public final void process() {
        readData();
        validateData();
        saveData();
    }
    
    // 자식이 구현할 부분
    protected abstract void readData();
    protected abstract void validateData();
    protected abstract void saveData();
}

// 구현 클래스
public class CsvDataProcessor extends DataProcessor {
    @Override
    protected void readData() {
        System.out.println("CSV 파일 읽기");
    }
    
    @Override
    protected void validateData() {
        System.out.println("CSV 데이터 검증");
    }
    
    @Override
    protected void saveData() {
        System.out.println("DB에 저장");
    }
}

// 사용
DataProcessor processor = new CsvDataProcessor();
processor.process();  // 템플릿 메서드 호출
```

### 꼬리 질문 예상
- 추상 메서드가 하나도 없어도 abstract 선언하는 이유는? → 직접 인스턴스화를 막고 상속만 강제하려고.
- final class와 abstract class는 모순인가? → 네, 불가능. final은 상속 불가, abstract는 상속 필수.
- 인터페이스도 객체 생성이 불가능한 이유는? → 추상클래스와 동일. 구현이 없는 메서드만 있으므로.

## 참고
- [[Java-인터페이스-추상클래스]]
- [[Java-상속-다형성-super]]
- [[Java-람다-Stream-함수형]]
