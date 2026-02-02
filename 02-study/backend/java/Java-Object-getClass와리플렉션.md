---
tags:
  - study
  - java
  - object
  - reflection
  - getClass
created: 2025-02-02
---

# Java Object getClass와 리플렉션

## 한 줄 요약
> 런타임에 객체의 클래스 정보를 조회하고 조작하는 메서드와 리플렉션 API

## 상세 설명

### getClass() 메서드

`getClass()`는 객체의 런타임 클래스 정보를 반환하는 메서드입니다. Class<?> 타입을 반환하며, 이를 통해 클래스의 메타데이터에 접근할 수 있습니다.

**주요 특징**
- final 메서드로 오버라이딩 불가능
- 실제 객체의 타입 반환 (다형성 고려)
- 리플렉션의 시작점

**기본 사용**
```java
String str = "Hello";
Class<?> clazz = str.getClass();
System.out.println(clazz.getName());  // java.lang.String
```

### Class 객체 얻는 방법

**1. getClass() 메서드**
```java
String str = "Hello";
Class<?> clazz = str.getClass();
```

**2. .class 리터럴**
```java
Class<String> clazz = String.class;
```

**3. Class.forName()**
```java
Class<?> clazz = Class.forName("java.lang.String");
```

### 리플렉션 기초

리플렉션(Reflection)은 프로그램이 실행 중에 자기 자신의 구조를 분석하고 조작할 수 있는 기능입니다.

**리플렉션으로 할 수 있는 것**
1. 클래스 정보 조회 (필드, 메서드, 생성자)
2. 접근 제어자 무시하고 필드 접근
3. 런타임에 객체 생성
4. 메서드 동적 호출

## 코드 예시

### getClass() 기본 사용

```java
class Animal { }
class Dog extends Animal { }

// 다형성과 getClass()
Animal animal = new Dog();
System.out.println(animal.getClass().getName());  // Dog (실제 타입)
System.out.println(animal.getClass() == Dog.class);  // true
System.out.println(animal instanceof Animal);  // true
System.out.println(animal instanceof Dog);  // true
```

### Class 객체 정보 조회

```java
class Person {
    private String name;
    private int age;
    
    public void sayHello() {
        System.out.println("Hello!");
    }
}

// 클래스 정보 조회
Class<Person> clazz = Person.class;

// 클래스 이름
System.out.println(clazz.getName());  // Person
System.out.println(clazz.getSimpleName());  // Person

// 패키지 정보
System.out.println(clazz.getPackage().getName());

// 부모 클래스
System.out.println(clazz.getSuperclass().getName());  // java.lang.Object

// 인터페이스 확인
Class<?>[] interfaces = clazz.getInterfaces();
for (Class<?> iface : interfaces) {
    System.out.println(iface.getName());
}
```

### 필드 정보 조회

```java
import java.lang.reflect.Field;

class Person {
    private String name;
    public int age;
    protected String email;
}

Class<Person> clazz = Person.class;

// 모든 필드 조회 (public만)
Field[] publicFields = clazz.getFields();

// 선언된 모든 필드 조회 (private 포함)
Field[] allFields = clazz.getDeclaredFields();

for (Field field : allFields) {
    System.out.println("필드명: " + field.getName());
    System.out.println("타입: " + field.getType().getName());
    System.out.println("접근제어자: " + Modifier.toString(field.getModifiers()));
    System.out.println("---");
}
```

### 필드 값 읽기/쓰기

```java
import java.lang.reflect.Field;

class Person {
    private String name = "홍길동";
    private int age = 30;
}

Person person = new Person();
Class<?> clazz = person.getClass();

// private 필드 접근
Field nameField = clazz.getDeclaredField("name");
nameField.setAccessible(true);  // private 접근 허용

// 필드 값 읽기
String name = (String) nameField.get(person);
System.out.println("이름: " + name);  // 홍길동

// 필드 값 쓰기
nameField.set(person, "김철수");
System.out.println("변경된 이름: " + nameField.get(person));  // 김철수
```

### 메서드 정보 조회 및 호출

```java
import java.lang.reflect.Method;

class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    private String privateMethod() {
        return "Private!";
    }
}

Calculator calc = new Calculator();
Class<?> clazz = calc.getClass();

// 메서드 조회
Method addMethod = clazz.getMethod("add", int.class, int.class);

// 메서드 호출
Object result = addMethod.invoke(calc, 10, 20);
System.out.println("결과: " + result);  // 30

// private 메서드 호출
Method privateMethod = clazz.getDeclaredMethod("privateMethod");
privateMethod.setAccessible(true);
Object privateResult = privateMethod.invoke(calc);
System.out.println(privateResult);  // Private!
```

### 생성자를 통한 객체 생성

```java
import java.lang.reflect.Constructor;

class Person {
    private String name;
    private int age;
    
    public Person() { }
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}

// 기본 생성자로 객체 생성
Class<Person> clazz = Person.class;
Person person1 = clazz.newInstance();  // Deprecated (Java 9+)
Person person2 = clazz.getDeclaredConstructor().newInstance();  // 권장

// 매개변수 있는 생성자로 객체 생성
Constructor<Person> constructor = clazz.getConstructor(String.class, int.class);
Person person3 = constructor.newInstance("홍길동", 30);
```

### 어노테이션 정보 조회

```java
import java.lang.annotation.*;
import java.lang.reflect.*;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Column {
    String name();
    int length() default 255;
}

class User {
    @Column(name = "user_name", length = 100)
    private String name;
    
    @Column(name = "user_age")
    private int age;
}

// 어노테이션 정보 조회
Class<User> clazz = User.class;
Field[] fields = clazz.getDeclaredFields();

for (Field field : fields) {
    if (field.isAnnotationPresent(Column.class)) {
        Column column = field.getAnnotation(Column.class);
        System.out.println("필드: " + field.getName());
        System.out.println("컬럼명: " + column.name());
        System.out.println("길이: " + column.length());
        System.out.println("---");
    }
}
```

### 제네릭 타입 정보 조회

```java
import java.lang.reflect.*;
import java.util.*;

class Container {
    private List<String> items;
}

Field field = Container.class.getDeclaredField("items");
Type genericType = field.getGenericType();

if (genericType instanceof ParameterizedType) {
    ParameterizedType pType = (ParameterizedType) genericType;
    Type[] typeArgs = pType.getActualTypeArguments();
    
    System.out.println("제네릭 타입: " + typeArgs[0]);  // class java.lang.String
}
```

### 실무 활용: 간단한 JSON 변환

```java
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;

class SimpleJsonConverter {
    public static String toJson(Object obj) throws Exception {
        Class<?> clazz = obj.getClass();
        Field[] fields = clazz.getDeclaredFields();
        
        StringBuilder json = new StringBuilder("{");
        
        for (int i = 0; i < fields.length; i++) {
            Field field = fields[i];
            field.setAccessible(true);
            
            String fieldName = field.getName();
            Object fieldValue = field.get(obj);
            
            json.append("\"").append(fieldName).append("\":");
            
            if (fieldValue instanceof String) {
                json.append("\"").append(fieldValue).append("\"");
            } else {
                json.append(fieldValue);
            }
            
            if (i < fields.length - 1) {
                json.append(",");
            }
        }
        
        json.append("}");
        return json.toString();
    }
}

// 사용
class Person {
    private String name = "홍길동";
    private int age = 30;
}

Person person = new Person();
String json = SimpleJsonConverter.toJson(person);
System.out.println(json);  // {"name":"홍길동","age":30}
```

## 주의사항 / 함정

### 1. 성능 오버헤드

```java
// ❌ 성능 저하 (리플렉션 사용)
Method method = clazz.getMethod("getValue");
for (int i = 0; i < 1000000; i++) {
    method.invoke(obj);  // 느림
}

// ✅ 직접 호출
for (int i = 0; i < 1000000; i++) {
    obj.getValue();  // 빠름
}
```

리플렉션은 일반 메서드 호출보다 10~100배 느릴 수 있습니다.

### 2. 캡슐화 파괴

```java
class BankAccount {
    private double balance = 1000000;
    
    private void withdraw(double amount) {
        balance -= amount;
    }
}

// ❌ private 메서드에 접근
BankAccount account = new BankAccount();
Method method = account.getClass().getDeclaredMethod("withdraw", double.class);
method.setAccessible(true);
method.invoke(account, 500000);  // 캡슐화 위반!
```

### 3. 타입 안전성 상실

```java
Field field = clazz.getDeclaredField("age");
field.setAccessible(true);

// ❌ 런타임 에러 (컴파일 타임에 검출 불가)
field.set(obj, "thirty");  // IllegalArgumentException: 타입 불일치
```

### 4. 보안 문제

```java
// SecurityManager가 있는 환경에서
Field field = clazz.getDeclaredField("password");
field.setAccessible(true);  // SecurityException 발생 가능
```

### 5. 예외 처리 복잡성

```java
try {
    Class<?> clazz = Class.forName("NonExistentClass");
    Method method = clazz.getMethod("someMethod");
    Object result = method.invoke(obj, args);
} catch (ClassNotFoundException e) {
    // 클래스를 찾을 수 없음
} catch (NoSuchMethodException e) {
    // 메서드를 찾을 수 없음
} catch (IllegalAccessException e) {
    // 접근 권한 없음
} catch (InvocationTargetException e) {
    // 호출된 메서드에서 예외 발생
    Throwable cause = e.getCause();
}
```

### 6. 컴파일 타임 검증 불가

```java
// ❌ 메서드명 오타 - 런타임에만 발견
Method method = clazz.getMethod("getValue");  // 컴파일 성공
method.invoke(obj);  // NoSuchMethodException (런타임)

// ✅ 직접 호출 - 컴파일 타임에 검출
obj.getValeu();  // 컴파일 에러
```

## 관련 개념
- [[Java-어노테이션]]
- [[Java-프록시패턴]]
- [[Java-직렬화]]
- [[Spring-의존성주입]]

## 면접 질문
1. 리플렉션의 장점과 단점은 무엇인가요?
2. getClass()와 .class, Class.forName()의 차이점은?

## 참고 자료
- Effective Java 3/E - Item 65 (리플렉션보다는 인터페이스를 사용하라)
- Java API Documentation - Class
- Java Reflection API Documentation