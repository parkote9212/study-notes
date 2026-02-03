---
tags:
  - study
  - java
  - annotation
  - metadata
created: 2025-02-03
---

# Java 어노테이션 (Annotation)

## 한 줄 요약
> 코드에 메타데이터를 추가하여 컴파일러와 런타임에 정보를 제공하는 기능

## 상세 설명

### 어노테이션의 기본 개념

어노테이션은 `@` 기호로 시작하는 메타데이터로, 코드에 추가 정보를 제공합니다.

**주요 용도**
1. **컴파일러 정보 제공**: @Override, @Deprecated
2. **컴파일 시점 처리**: Lombok의 @Getter, @Setter
3. **런타임 처리**: Spring의 @Component, @Autowired
4. **문서화**: @param, @return

**어노테이션 종류**
- **내장 어노테이션**: Java가 기본 제공
- **메타 어노테이션**: 어노테이션을 정의하는 어노테이션
- **커스텀 어노테이션**: 직접 정의한 어노테이션

## 코드 예시

### 1. 내장 어노테이션

#### @Override

```java
class Parent {
    public void display() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    // ✅ 컴파일러가 오버라이딩 검증
    @Override
    public void display() {
        System.out.println("Child");
    }
    
    // ❌ 컴파일 에러 - 메서드명 오타 발견
    @Override
    public void displya() {  // 오타!
        System.out.println("Child");
    }
}
```

#### @Deprecated

```java
class OldApi {
    // 더 이상 사용하지 않는 메서드 표시
    @Deprecated(since = "2.0", forRemoval = true)
    public void oldMethod() {
        System.out.println("구식 메서드");
    }
    
    public void newMethod() {
        System.out.println("새로운 메서드");
    }
}

// 사용 시 경고 발생
OldApi api = new OldApi();
api.oldMethod();  // 경고: 'oldMethod()' is deprecated and marked for removal
```

#### @SuppressWarnings

```java
@SuppressWarnings("unchecked")  // unchecked 경고 무시
public void useRawType() {
    List list = new ArrayList();  // Raw type 사용
    list.add("String");
}

@SuppressWarnings({"unchecked", "deprecation"})  // 여러 경고 무시
public void multipleWarnings() {
    List list = new ArrayList();
    oldMethod();
}
```

#### @FunctionalInterface

```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
    
    // ❌ 컴파일 에러 - 추상 메서드가 2개
    // int subtract(int a, int b);
    
    // ✅ default/static 메서드는 OK
    default void printResult(int result) {
        System.out.println("결과: " + result);
    }
}

// 람다로 구현
Calculator add = (a, b) -> a + b;
```

### 2. 메타 어노테이션

#### @Retention - 어노테이션 유지 범위

```java
import java.lang.annotation.*;

// SOURCE: 소스 코드에만 유지 (컴파일 후 제거)
@Retention(RetentionPolicy.SOURCE)
@interface CompileTimeCheck {}

// CLASS: 클래스 파일까지 유지 (런타임에는 사용 불가, 기본값)
@Retention(RetentionPolicy.CLASS)
@interface BytecodeInfo {}

// RUNTIME: 런타임까지 유지 (리플렉션으로 접근 가능)
@Retention(RetentionPolicy.RUNTIME)
@interface RuntimeInfo {}
```

#### @Target - 어노테이션 적용 대상

```java
// 메서드에만 적용 가능
@Target(ElementType.METHOD)
@interface MethodOnly {}

// 필드에만 적용 가능
@Target(ElementType.FIELD)
@interface FieldOnly {}

// 여러 대상에 적용 가능
@Target({ElementType.TYPE, ElementType.METHOD})
@interface TypeAndMethod {}

// 모든 대상
@Target(ElementType.TYPE_USE)
@interface AnyUse {}
```

**ElementType 종류**
- `TYPE`: 클래스, 인터페이스, enum
- `FIELD`: 필드
- `METHOD`: 메서드
- `PARAMETER`: 매개변수
- `CONSTRUCTOR`: 생성자
- `LOCAL_VARIABLE`: 지역 변수
- `ANNOTATION_TYPE`: 어노테이션 타입
- `PACKAGE`: 패키지

#### @Documented

```java
// JavaDoc에 포함됨
@Documented
@interface ApiInfo {
    String value();
}
```

#### @Inherited

```java
// 하위 클래스가 어노테이션을 상속받음
@Inherited
@interface ParentAnnotation {}

@ParentAnnotation
class Parent {}

class Child extends Parent {}  // @ParentAnnotation 상속됨
```

### 3. 커스텀 어노테이션 만들기

#### 마커 어노테이션 (값 없음)

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Test {
}

// 사용
class Calculator {
    @Test
    public void testAddition() {
        // 테스트 코드
    }
}
```

#### 값을 가진 어노테이션

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Author {
    String name();           // 필수 값
    String date();
    int version() default 1; // 기본값
}

// 사용
@Author(name = "박철수", date = "2025-02-03")
public void method1() {}

@Author(name = "김영희", date = "2025-02-03", version = 2)
public void method2() {}
```

#### 배열 값을 가진 어노테이션

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface Roles {
    String[] value();  // value 이름이면 생략 가능
}

// 사용
@Roles({"ADMIN", "USER"})
class AdminService {}

@Roles(value = {"USER"})  // 하나만 있어도 배열
class UserService {}
```

### 4. 리플렉션으로 어노테이션 읽기

```java
import java.lang.reflect.*;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Benchmark {
    int warmup() default 1000;
    int iterations() default 10000;
}

class Performance {
    @Benchmark(iterations = 5000)
    public void fastMethod() {
        // 빠른 메서드
    }
    
    @Benchmark(warmup = 2000, iterations = 20000)
    public void slowMethod() {
        // 느린 메서드
    }
}

// 어노테이션 읽기
public class BenchmarkRunner {
    public static void main(String[] args) throws Exception {
        Class<?> clazz = Performance.class;
        
        for (Method method : clazz.getDeclaredMethods()) {
            if (method.isAnnotationPresent(Benchmark.class)) {
                Benchmark benchmark = method.getAnnotation(Benchmark.class);
                
                System.out.println("메서드: " + method.getName());
                System.out.println("  워밍업: " + benchmark.warmup());
                System.out.println("  반복: " + benchmark.iterations());
                
                // 실제 벤치마크 실행
                runBenchmark(method, benchmark);
            }
        }
    }
    
    private static void runBenchmark(Method method, Benchmark benchmark) 
            throws Exception {
        Object obj = method.getDeclaringClass().getDeclaredConstructor().newInstance();
        
        // 워밍업
        for (int i = 0; i < benchmark.warmup(); i++) {
            method.invoke(obj);
        }
        
        // 측정
        long start = System.nanoTime();
        for (int i = 0; i < benchmark.iterations(); i++) {
            method.invoke(obj);
        }
        long end = System.nanoTime();
        
        System.out.println("  실행 시간: " + (end - start) / 1_000_000 + "ms");
    }
}
```

### 5. 실전 예시: 유효성 검증

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface NotNull {
    String message() default "필드는 null일 수 없습니다";
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Min {
    int value();
    String message() default "최소값보다 작습니다";
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Max {
    int value();
    String message() default "최대값보다 큽니다";
}

// 사용
class User {
    @NotNull(message = "이름은 필수입니다")
    private String name;
    
    @Min(value = 0, message = "나이는 0 이상이어야 합니다")
    @Max(value = 150, message = "나이는 150 이하여야 합니다")
    private int age;
    
    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String getName() { return name; }
    public int getAge() { return age; }
}

// 검증기
class Validator {
    public static void validate(Object obj) throws Exception {
        Class<?> clazz = obj.getClass();
        
        for (Field field : clazz.getDeclaredFields()) {
            field.setAccessible(true);
            Object value = field.get(obj);
            
            // @NotNull 검증
            if (field.isAnnotationPresent(NotNull.class)) {
                if (value == null) {
                    NotNull annotation = field.getAnnotation(NotNull.class);
                    throw new IllegalArgumentException(
                        field.getName() + ": " + annotation.message()
                    );
                }
            }
            
            // @Min 검증
            if (field.isAnnotationPresent(Min.class)) {
                Min annotation = field.getAnnotation(Min.class);
                if (value instanceof Integer) {
                    int intValue = (Integer) value;
                    if (intValue < annotation.value()) {
                        throw new IllegalArgumentException(
                            field.getName() + ": " + annotation.message()
                        );
                    }
                }
            }
            
            // @Max 검증
            if (field.isAnnotationPresent(Max.class)) {
                Max annotation = field.getAnnotation(Max.class);
                if (value instanceof Integer) {
                    int intValue = (Integer) value;
                    if (intValue > annotation.value()) {
                        throw new IllegalArgumentException(
                            field.getName() + ": " + annotation.message()
                        );
                    }
                }
            }
        }
    }
}

// 테스트
public class Main {
    public static void main(String[] args) {
        try {
            User user1 = new User("홍길동", 25);
            Validator.validate(user1);  // 통과
            System.out.println("user1 검증 성공");
            
            User user2 = new User(null, 25);
            Validator.validate(user2);  // 예외 발생
        } catch (Exception e) {
            System.out.println("검증 실패: " + e.getMessage());
        }
    }
}
```

### 6. 실전 예시: 간단한 DI 컨테이너

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface Component {
    String value() default "";
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Inject {
}

// 컴포넌트들
@Component("userService")
class UserService {
    public void createUser(String name) {
        System.out.println("User created: " + name);
    }
}

@Component("userController")
class UserController {
    @Inject
    private UserService userService;
    
    public void register(String name) {
        userService.createUser(name);
    }
}

// DI 컨테이너
class DIContainer {
    private Map<String, Object> beans = new HashMap<>();
    
    public void scan(String packageName) throws Exception {
        // 실제로는 클래스패스 스캔 필요
        // 여기서는 하드코딩
        registerBean(UserService.class);
        registerBean(UserController.class);
        
        // 의존성 주입
        injectDependencies();
    }
    
    private void registerBean(Class<?> clazz) throws Exception {
        if (clazz.isAnnotationPresent(Component.class)) {
            Component component = clazz.getAnnotation(Component.class);
            String beanName = component.value();
            Object instance = clazz.getDeclaredConstructor().newInstance();
            beans.put(beanName, instance);
            System.out.println("Bean registered: " + beanName);
        }
    }
    
    private void injectDependencies() throws Exception {
        for (Object bean : beans.values()) {
            Class<?> clazz = bean.getClass();
            
            for (Field field : clazz.getDeclaredFields()) {
                if (field.isAnnotationPresent(Inject.class)) {
                    // 필드 타입으로 bean 찾기
                    Class<?> fieldType = field.getType();
                    Object dependency = findBean(fieldType);
                    
                    if (dependency != null) {
                        field.setAccessible(true);
                        field.set(bean, dependency);
                        System.out.println("Injected: " + fieldType.getSimpleName() +
                                         " into " + clazz.getSimpleName());
                    }
                }
            }
        }
    }
    
    private Object findBean(Class<?> type) {
        for (Object bean : beans.values()) {
            if (type.isInstance(bean)) {
                return bean;
            }
        }
        return null;
    }
    
    public <T> T getBean(String name, Class<T> type) {
        return type.cast(beans.get(name));
    }
}

// 사용
public class Main {
    public static void main(String[] args) throws Exception {
        DIContainer container = new DIContainer();
        container.scan("com.example");
        
        UserController controller = container.getBean("userController", UserController.class);
        controller.register("홍길동");
    }
}
```

### 7. Spring 주요 어노테이션

```java
// 컴포넌트 스캔
@Component
@Service
@Repository
@Controller
@RestController

// 의존성 주입
@Autowired
@Qualifier("beanName")
@Value("${property.key}")

// 설정
@Configuration
@Bean
@ComponentScan
@PropertySource

// 웹
@RequestMapping
@GetMapping
@PostMapping
@PathVariable
@RequestParam
@RequestBody

// 트랜잭션
@Transactional
```

## 주의사항 / 함정

### 1. Retention 정책

```java
// ❌ SOURCE 정책은 런타임에 사용 불가
@Retention(RetentionPolicy.SOURCE)
@interface MyAnnotation {}

// 런타임에 접근 시도
if (method.isAnnotationPresent(MyAnnotation.class)) {
    // 항상 false - SOURCE는 컴파일 후 제거됨
}

// ✅ 런타임 사용 시 RUNTIME 필요
@Retention(RetentionPolicy.RUNTIME)
@interface MyAnnotation {}
```

### 2. value() 특별 처리

```java
@interface MyAnnotation {
    String value();  // value라는 이름은 특별
}

// 단일 속성이고 이름이 value면 생략 가능
@MyAnnotation("test")  // value= 생략

// 다른 이름은 생략 불가
@interface OtherAnnotation {
    String name();
}

@OtherAnnotation(name = "test")  // name= 생략 불가
```

### 3. 기본값 제한

```java
// ❌ null은 기본값으로 사용 불가
@interface MyAnnotation {
    String value() default null;  // 컴파일 에러
}

// ✅ 빈 문자열 또는 다른 값 사용
@interface MyAnnotation {
    String value() default "";
}
```

## 관련 개념
- [[Java-Object-getClass와리플렉션]]

## 면접 질문
1. @Override 어노테이션의 역할은?
2. Retention 정책 3가지는 무엇이고 차이점은?

## 참고 자료
- Java Annotation Documentation
- Effective Java - Annotations
- Spring Framework Annotations