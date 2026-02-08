---
tags:
  - study
  - java
  - reflection
  - annotation
  - advanced
created: 2025-02-08
---

# Java 리플렉션 심화

## 한 줄 요약
> 런타임에 클래스 구조를 분석하고 조작하는 강력한 기능 (Spring/JPA의 핵심)

## 상세 설명

### 리플렉션이란?

리플렉션(Reflection)은 **런타임에 클래스, 메서드, 필드 등의 정보를 동적으로 조회하고 조작**할 수 있는 Java의 기능입니다.

**주요 활용**
- Spring의 의존성 주입 (@Autowired)
- JPA의 엔티티 매핑
- JSON 직렬화/역직렬화 (Jackson, Gson)
- 테스트 프레임워크 (JUnit)
- 프록시 패턴 구현

**왜 중요한가?**
1. 프레임워크 동작 원리 이해
2. 동적 객체 생성/조작
3. 어노테이션 기반 프로그래밍
4. 라이브러리/프레임워크 개발

## 코드 예시

### 1. Class 객체 얻기

```java
public class GettingClass {
    public static void main(String[] args) throws ClassNotFoundException {
        // 방법 1: .class 리터럴
        Class<String> clazz1 = String.class;
        
        // 방법 2: Object.getClass()
        String str = "Hello";
        Class<? extends String> clazz2 = str.getClass();
        
        // 방법 3: Class.forName() - 동적 로딩
        Class<?> clazz3 = Class.forName("java.lang.String");
        
        // 모두 같은 Class 객체
        System.out.println(clazz1 == clazz2);  // true
        System.out.println(clazz2 == clazz3);  // true
        
        // 클래스 정보 조회
        System.out.println(clazz1.getName());          // java.lang.String
        System.out.println(clazz1.getSimpleName());    // String
        System.out.println(clazz1.getPackage());       // package java.lang
    }
}
```

### 2. 생성자 정보 조회 및 객체 생성

```java
import java.lang.reflect.*;

class Person {
    private String name;
    private int age;
    
    public Person() {
        this.name = "Unknown";
        this.age = 0;
    }
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
}

public class ConstructorReflection {
    public static void main(String[] args) throws Exception {
        Class<Person> clazz = Person.class;
        
        // 모든 public 생성자 조회
        Constructor<?>[] constructors = clazz.getConstructors();
        for (Constructor<?> constructor : constructors) {
            System.out.println(constructor);
        }
        
        // 기본 생성자로 객체 생성
        Constructor<Person> defaultConstructor = clazz.getConstructor();
        Person person1 = defaultConstructor.newInstance();
        System.out.println(person1);  // Person{name='Unknown', age=0}
        
        // 파라미터 있는 생성자로 객체 생성
        Constructor<Person> paramConstructor = 
            clazz.getConstructor(String.class, int.class);
        Person person2 = paramConstructor.newInstance("Alice", 25);
        System.out.println(person2);  // Person{name='Alice', age=25}
    }
}
```

### 3. 필드 정보 조회 및 접근

```java
import java.lang.reflect.*;

class User {
    public String username;
    private String password;
    protected String email;
    
    public User(String username, String password, String email) {
        this.username = username;
        this.password = password;
        this.email = email;
    }
}

public class FieldReflection {
    public static void main(String[] args) throws Exception {
        User user = new User("alice", "secret123", "alice@example.com");
        Class<? extends User> clazz = user.getClass();
        
        // public 필드만 조회
        Field[] publicFields = clazz.getFields();
        System.out.println("Public fields: " + publicFields.length);
        
        // 모든 필드 조회 (private 포함)
        Field[] allFields = clazz.getDeclaredFields();
        for (Field field : allFields) {
            System.out.println(field.getName() + " (" + 
                             Modifier.toString(field.getModifiers()) + ")");
        }
        
        // private 필드 접근
        Field passwordField = clazz.getDeclaredField("password");
        passwordField.setAccessible(true);  // private 접근 허용
        
        String password = (String) passwordField.get(user);
        System.out.println("Password: " + password);  // secret123
        
        // 값 변경
        passwordField.set(user, "newPassword");
        System.out.println("New password: " + passwordField.get(user));
    }
}
```

### 4. 메서드 정보 조회 및 호출

```java
import java.lang.reflect.*;

class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    private String privateMethod(String msg) {
        return "Private: " + msg;
    }
    
    public static String staticMethod() {
        return "Static method";
    }
}

public class MethodReflection {
    public static void main(String[] args) throws Exception {
        Calculator calc = new Calculator();
        Class<? extends Calculator> clazz = calc.getClass();
        
        // 모든 public 메서드 조회
        Method[] methods = clazz.getMethods();
        for (Method method : methods) {
            System.out.println(method.getName());
        }
        
        // 특정 메서드 호출
        Method addMethod = clazz.getMethod("add", int.class, int.class);
        Object result = addMethod.invoke(calc, 5, 3);
        System.out.println("5 + 3 = " + result);  // 8
        
        // private 메서드 호출
        Method privateMethod = clazz.getDeclaredMethod("privateMethod", String.class);
        privateMethod.setAccessible(true);
        Object privateResult = privateMethod.invoke(calc, "Hello");
        System.out.println(privateResult);  // Private: Hello
        
        // static 메서드 호출 (객체 불필요)
        Method staticMethod = clazz.getMethod("staticMethod");
        Object staticResult = staticMethod.invoke(null);
        System.out.println(staticResult);  // Static method
    }
}
```

### 5. 어노테이션과 리플렉션

```java
import java.lang.annotation.*;
import java.lang.reflect.*;

// 커스텀 어노테이션
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Validate {
    int min() default 0;
    int max() default Integer.MAX_VALUE;
    String message() default "Invalid value";
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Required {
    String message() default "Field is required";
}

class UserForm {
    @Required(message = "Username is required")
    private String username;
    
    @Validate(min = 18, max = 120, message = "Age must be between 18 and 120")
    private int age;
    
    @Required
    @Validate(min = 8, max = 20, message = "Password length must be 8-20")
    private String password;
    
    public UserForm(String username, int age, String password) {
        this.username = username;
        this.age = age;
        this.password = password;
    }
}

public class AnnotationReflection {
    public static void main(String[] args) throws Exception {
        UserForm form = new UserForm("", 15, "123");
        
        Class<? extends UserForm> clazz = form.getClass();
        Field[] fields = clazz.getDeclaredFields();
        
        for (Field field : fields) {
            field.setAccessible(true);
            Object value = field.get(form);
            
            // @Required 검증
            if (field.isAnnotationPresent(Required.class)) {
                Required required = field.getAnnotation(Required.class);
                if (value == null || value.toString().isEmpty()) {
                    System.out.println(field.getName() + ": " + 
                                     required.message());
                }
            }
            
            // @Validate 검증
            if (field.isAnnotationPresent(Validate.class)) {
                Validate validate = field.getAnnotation(Validate.class);
                if (value instanceof Integer) {
                    int intValue = (Integer) value;
                    if (intValue < validate.min() || intValue > validate.max()) {
                        System.out.println(field.getName() + ": " + 
                                         validate.message());
                    }
                } else if (value instanceof String) {
                    String strValue = (String) value;
                    if (strValue.length() < validate.min() || 
                        strValue.length() > validate.max()) {
                        System.out.println(field.getName() + ": " + 
                                         validate.message());
                    }
                }
            }
        }
        // 출력:
        // username: Username is required
        // age: Age must be between 18 and 120
        // password: Password length must be 8-20
    }
}
```

## 실무 예시

### 1. 간단한 의존성 주입 (DI) 구현

```java
import java.lang.annotation.*;
import java.lang.reflect.*;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Inject {
}

class UserRepository {
    public String findUser(String id) {
        return "User " + id;
    }
}

class UserService {
    @Inject
    private UserRepository userRepository;
    
    public String getUser(String id) {
        return userRepository.findUser(id);
    }
}

public class SimpleDI {
    public static <T> T createInstance(Class<T> clazz) throws Exception {
        // 객체 생성
        T instance = clazz.getDeclaredConstructor().newInstance();
        
        // @Inject 필드 찾기
        Field[] fields = clazz.getDeclaredFields();
        for (Field field : fields) {
            if (field.isAnnotationPresent(Inject.class)) {
                field.setAccessible(true);
                
                // 의존성 객체 생성 및 주입
                Object dependency = field.getType()
                    .getDeclaredConstructor()
                    .newInstance();
                field.set(instance, dependency);
            }
        }
        
        return instance;
    }
    
    public static void main(String[] args) throws Exception {
        UserService service = createInstance(UserService.class);
        String result = service.getUser("123");
        System.out.println(result);  // User 123
    }
}
```

### 2. JSON 직렬화 (간단 버전)

```java
import java.lang.reflect.*;

class Product {
    private String name;
    private int price;
    private boolean available;
    
    public Product(String name, int price, boolean available) {
        this.name = name;
        this.price = price;
        this.available = available;
    }
}

public class SimpleJsonSerializer {
    public static String toJson(Object obj) throws Exception {
        Class<?> clazz = obj.getClass();
        Field[] fields = clazz.getDeclaredFields();
        
        StringBuilder json = new StringBuilder("{");
        
        for (int i = 0; i < fields.length; i++) {
            Field field = fields[i];
            field.setAccessible(true);
            
            String fieldName = field.getName();
            Object value = field.get(obj);
            
            json.append("\"").append(fieldName).append("\":");
            
            if (value instanceof String) {
                json.append("\"").append(value).append("\"");
            } else {
                json.append(value);
            }
            
            if (i < fields.length - 1) {
                json.append(",");
            }
        }
        
        json.append("}");
        return json.toString();
    }
    
    public static void main(String[] args) throws Exception {
        Product product = new Product("Laptop", 1200000, true);
        String json = toJson(product);
        System.out.println(json);
        // {"name":"Laptop","price":1200000,"available":true}
    }
}
```

### 3. ORM 매핑 (간단 버전)

```java
import java.lang.annotation.*;
import java.lang.reflect.*;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface Table {
    String name();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Column {
    String name();
}

@Table(name = "users")
class UserEntity {
    @Column(name = "user_id")
    private Long id;
    
    @Column(name = "user_name")
    private String name;
    
    @Column(name = "user_age")
    private int age;
    
    public UserEntity(Long id, String name, int age) {
        this.id = id;
        this.name = name;
        this.age = age;
    }
}

public class SimpleORM {
    public static String generateInsertSQL(Object entity) throws Exception {
        Class<?> clazz = entity.getClass();
        
        // 테이블 이름
        Table table = clazz.getAnnotation(Table.class);
        String tableName = table.name();
        
        // 컬럼과 값
        StringBuilder columns = new StringBuilder();
        StringBuilder values = new StringBuilder();
        
        Field[] fields = clazz.getDeclaredFields();
        for (int i = 0; i < fields.length; i++) {
            Field field = fields[i];
            Column column = field.getAnnotation(Column.class);
            
            if (column != null) {
                field.setAccessible(true);
                Object value = field.get(entity);
                
                columns.append(column.name());
                
                if (value instanceof String) {
                    values.append("'").append(value).append("'");
                } else {
                    values.append(value);
                }
                
                if (i < fields.length - 1) {
                    columns.append(", ");
                    values.append(", ");
                }
            }
        }
        
        return String.format("INSERT INTO %s (%s) VALUES (%s)",
                           tableName, columns, values);
    }
    
    public static void main(String[] args) throws Exception {
        UserEntity user = new UserEntity(1L, "Alice", 25);
        String sql = generateInsertSQL(user);
        System.out.println(sql);
        // INSERT INTO users (user_id, user_name, user_age) VALUES (1, 'Alice', 25)
    }
}
```

### 4. 동적 프록시

```java
import java.lang.reflect.*;

interface UserService {
    String getUser(String id);
    void deleteUser(String id);
}

class UserServiceImpl implements UserService {
    @Override
    public String getUser(String id) {
        return "User " + id;
    }
    
    @Override
    public void deleteUser(String id) {
        System.out.println("Deleting user " + id);
    }
}

public class DynamicProxyExample {
    public static void main(String[] args) {
        UserService realService = new UserServiceImpl();
        
        // 프록시 생성
        UserService proxy = (UserService) Proxy.newProxyInstance(
            UserService.class.getClassLoader(),
            new Class<?>[] { UserService.class },
            new InvocationHandler() {
                @Override
                public Object invoke(Object proxy, Method method, Object[] args) 
                        throws Throwable {
                    // 메서드 호출 전
                    System.out.println("Before: " + method.getName());
                    long start = System.currentTimeMillis();
                    
                    // 실제 메서드 호출
                    Object result = method.invoke(realService, args);
                    
                    // 메서드 호출 후
                    long end = System.currentTimeMillis();
                    System.out.println("After: " + method.getName() + 
                                     " (took " + (end - start) + "ms)");
                    
                    return result;
                }
            }
        );
        
        // 프록시를 통한 호출
        String user = proxy.getUser("123");
        System.out.println(user);
        
        proxy.deleteUser("456");
        
        // 출력:
        // Before: getUser
        // After: getUser (took 0ms)
        // User 123
        // Before: deleteUser
        // Deleting user 456
        // After: deleteUser (took 0ms)
    }
}
```

### 5. 테스트 유틸리티

```java
import java.lang.reflect.*;

public class ReflectionTestUtils {
    // private 필드 값 설정
    public static void setField(Object target, String fieldName, Object value) 
            throws Exception {
        Field field = target.getClass().getDeclaredField(fieldName);
        field.setAccessible(true);
        field.set(target, value);
    }
    
    // private 필드 값 조회
    public static Object getField(Object target, String fieldName) 
            throws Exception {
        Field field = target.getClass().getDeclaredField(fieldName);
        field.setAccessible(true);
        return field.get(target);
    }
    
    // private 메서드 호출
    public static Object invokeMethod(Object target, String methodName, 
                                     Class<?>[] paramTypes, Object... args) 
            throws Exception {
        Method method = target.getClass().getDeclaredMethod(methodName, paramTypes);
        method.setAccessible(true);
        return method.invoke(target, args);
    }
    
    public static void main(String[] args) throws Exception {
        User user = new User("alice", "password", "alice@example.com");
        
        // private 필드 테스트
        setField(user, "password", "newPassword");
        String password = (String) getField(user, "password");
        System.out.println("Password: " + password);  // newPassword
    }
}
```

## 주의사항 / 함정

### 1. 성능 오버헤드

```java
// ❌ 성능 저하 - 반복적인 리플렉션
public void badPerformance() throws Exception {
    for (int i = 0; i < 1000000; i++) {
        Class<?> clazz = Class.forName("java.lang.String");
        Method method = clazz.getMethod("length");
        // 매우 느림
    }
}

// ✅ 캐싱
private static final Method LENGTH_METHOD;
static {
    try {
        LENGTH_METHOD = String.class.getMethod("length");
    } catch (Exception e) {
        throw new RuntimeException(e);
    }
}

public void goodPerformance() throws Exception {
    for (int i = 0; i < 1000000; i++) {
        // 빠름
    }
}
```

### 2. 접근 제어 우회 주의

```java
// ⚠️ private 접근은 신중하게
public class PrivateAccess {
    public static void main(String[] args) throws Exception {
        String str = "Hello";
        
        // String의 private 필드 변경 (위험!)
        Field valueField = String.class.getDeclaredField("value");
        valueField.setAccessible(true);
        
        // ❌ 절대 하지 말 것
        // 불변성 깨짐, 예측 불가능한 동작
    }
}
```

### 3. 보안 관리자

```java
// SecurityManager가 활성화되면 리플렉션 제한
public class SecurityExample {
    public static void main(String[] args) {
        try {
            Field field = System.class.getDeclaredField("security");
            field.setAccessible(true);  // SecurityException 발생 가능
        } catch (SecurityException e) {
            System.out.println("Access denied by SecurityManager");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### 4. 타입 안전성 상실

```java
// ❌ 컴파일 타임 체크 불가
public void unsafeType() throws Exception {
    Object obj = "String";
    Method method = obj.getClass().getMethod("intValue");  // 런타임 에러
    method.invoke(obj);  // NoSuchMethodException
}

// ✅ 타입 체크
public void safeType() throws Exception {
    Object obj = "String";
    if (obj instanceof String) {
        String str = (String) obj;
        // 안전한 메서드 호출
    }
}
```

### 5. 예외 처리

```java
public class ExceptionHandling {
    public static void main(String[] args) {
        try {
            // ClassNotFoundException
            Class<?> clazz = Class.forName("NonExistentClass");
        } catch (ClassNotFoundException e) {
            System.out.println("Class not found");
        }
        
        try {
            Class<?> clazz = String.class;
            // NoSuchMethodException
            Method method = clazz.getMethod("nonExistentMethod");
        } catch (NoSuchMethodException e) {
            System.out.println("Method not found");
        }
        
        try {
            Class<?> clazz = String.class;
            // IllegalAccessException
            Field field = clazz.getDeclaredField("value");
            field.get("Hello");  // setAccessible(true) 없음
        } catch (Exception e) {
            System.out.println("Access error");
        }
    }
}
```

## 관련 개념
- [[Java-Object-getClass와리플렉션]]
- [[Java-어노테이션]]
- [[Java-제네릭스-Generics]]
- [[Java-디자인패턴-Proxy]]

## 면접 질문
1. 리플렉션이란 무엇이며 언제 사용하나요?
2. 리플렉션의 장단점은?
3. Spring에서 리플렉션이 어떻게 사용되나요?
4. 동적 프록시란 무엇인가요?
5. 리플렉션 성능 문제를 어떻게 개선할 수 있나요?
6. setAccessible(true)의 의미는?

## 참고 자료
- Effective Java 3/E - Item 65 (리플렉션보다는 인터페이스를 사용하라)
- Java Reflection API Documentation
- Spring Framework 소스 코드
- Pro Spring 5 - Reflection and AOP
