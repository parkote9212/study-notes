---
tags:
  - study
  - java
  - inner-class
  - nested-class
created: 2025-02-02
---

# Java 내부 클래스

## 한 줄 요약
> 클래스 내부에 정의된 클래스로 캡슐화와 코드 구조화를 돕는 기능

## 상세 설명

### 내부 클래스의 종류

Java는 4가지 종류의 내부 클래스를 제공합니다:

1. **멤버 내부 클래스 (Member Inner Class)** - 인스턴스 멤버
2. **정적 내부 클래스 (Static Nested Class)** - static 멤버
3. **로컬 내부 클래스 (Local Inner Class)** - 메서드 내부
4. **익명 내부 클래스 (Anonymous Inner Class)** - 이름 없는 클래스

### 내부 클래스를 사용하는 이유

1. **논리적 그룹화**: 관련된 클래스를 한 곳에 모음
2. **캡슐화 강화**: 외부 클래스의 private 멤버 접근 가능
3. **코드 가독성**: 관련 기능을 가까이 배치
4. **이벤트 처리**: GUI 프로그래밍에서 유용

## 코드 예시

### 1. 멤버 내부 클래스

```java
class Outer {
    private String outerField = "외부 필드";
    
    // 멤버 내부 클래스
    class Inner {
        private String innerField = "내부 필드";
        
        public void printFields() {
            // 외부 클래스의 private 멤버 접근 가능
            System.out.println(outerField);
            System.out.println(innerField);
        }
        
        public void accessOuterThis() {
            // 외부 클래스의 this 참조
            System.out.println(Outer.this.outerField);
        }
    }
    
    public void createInner() {
        Inner inner = new Inner();
        inner.printFields();
    }
}

// 사용
Outer outer = new Outer();
outer.createInner();

// 외부에서 내부 클래스 인스턴스 생성
Outer.Inner inner = outer.new Inner();
inner.printFields();
```

### 멤버 내부 클래스 실전 예시: LinkedList Node

```java
class MyLinkedList<T> {
    private Node<T> head;
    private int size;
    
    // 멤버 내부 클래스 - Node는 LinkedList에서만 의미 있음
    private class Node<T> {
        T data;
        Node<T> next;
        
        Node(T data) {
            this.data = data;
            this.next = null;
        }
    }
    
    public void add(T data) {
        Node<T> newNode = new Node<>(data);
        if (head == null) {
            head = newNode;
        } else {
            Node<T> current = head;
            while (current.next != null) {
                current = current.next;
            }
            current.next = newNode;
        }
        size++;
    }
    
    public void printAll() {
        Node<T> current = head;
        while (current != null) {
            System.out.print(current.data + " -> ");
            current = current.next;
        }
        System.out.println("null");
    }
}

// 사용
MyLinkedList<String> list = new MyLinkedList<>();
list.add("A");
list.add("B");
list.add("C");
list.printAll();  // A -> B -> C -> null
```

### 2. 정적 내부 클래스

```java
class Outer {
    private static String staticField = "static 필드";
    private String instanceField = "instance 필드";
    
    // 정적 내부 클래스
    static class StaticNested {
        public void print() {
            // ✅ 외부 클래스의 static 멤버 접근 가능
            System.out.println(staticField);
            
            // ❌ 외부 클래스의 인스턴스 멤버 접근 불가
            // System.out.println(instanceField);  // 컴파일 에러
        }
    }
}

// 사용 - 외부 클래스 인스턴스 없이 생성 가능
Outer.StaticNested nested = new Outer.StaticNested();
nested.print();
```

### 정적 내부 클래스 실전 예시: Builder 패턴

```java
class Person {
    private final String name;
    private final int age;
    private final String email;
    private final String phone;
    
    // private 생성자
    private Person(Builder builder) {
        this.name = builder.name;
        this.age = builder.age;
        this.email = builder.email;
        this.phone = builder.phone;
    }
    
    // 정적 내부 클래스로 Builder 구현
    public static class Builder {
        private String name;
        private int age;
        private String email;
        private String phone;
        
        public Builder name(String name) {
            this.name = name;
            return this;
        }
        
        public Builder age(int age) {
            this.age = age;
            return this;
        }
        
        public Builder email(String email) {
            this.email = email;
            return this;
        }
        
        public Builder phone(String phone) {
            this.phone = phone;
            return this;
        }
        
        public Person build() {
            return new Person(this);
        }
    }
    
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + 
               ", email='" + email + "', phone='" + phone + "'}";
    }
}

// 사용
Person person = new Person.Builder()
    .name("홍길동")
    .age(30)
    .email("hong@example.com")
    .phone("010-1234-5678")
    .build();

System.out.println(person);
```

### 정적 내부 클래스: Entry 클래스

```java
class MyHashMap<K, V> {
    private Entry<K, V>[] table;
    
    // 정적 내부 클래스 - Map.Entry 패턴
    static class Entry<K, V> {
        final K key;
        V value;
        Entry<K, V> next;
        
        Entry(K key, V value, Entry<K, V> next) {
            this.key = key;
            this.value = value;
            this.next = next;
        }
        
        public K getKey() {
            return key;
        }
        
        public V getValue() {
            return value;
        }
        
        public void setValue(V value) {
            this.value = value;
        }
    }
}
```

### 3. 로컬 내부 클래스

```java
class Outer {
    private String field = "외부 필드";
    
    public void method() {
        final String localVar = "로컬 변수";  // effectively final
        
        // 로컬 내부 클래스
        class LocalInner {
            public void print() {
                System.out.println(field);      // 외부 클래스 필드 접근
                System.out.println(localVar);   // 로컬 변수 접근 (final)
            }
        }
        
        LocalInner inner = new LocalInner();
        inner.print();
    }
}

// 사용
Outer outer = new Outer();
outer.method();
```

### 로컬 내부 클래스 실전 예시

```java
class DataProcessor {
    public void processData(List<String> data) {
        String prefix = "[처리됨] ";  // effectively final
        
        // 로컬 내부 클래스로 Comparator 구현
        class LengthComparator implements Comparator<String> {
            @Override
            public int compare(String s1, String s2) {
                return Integer.compare(s1.length(), s2.length());
            }
        }
        
        // 정렬
        data.sort(new LengthComparator());
        
        // 출력
        data.forEach(item -> System.out.println(prefix + item));
    }
}
```

### 4. 익명 내부 클래스

```java
interface Greeting {
    void sayHello(String name);
}

class AnonymousExample {
    public void createGreeting() {
        // 익명 내부 클래스
        Greeting greeting = new Greeting() {
            @Override
            public void sayHello(String name) {
                System.out.println("안녕하세요, " + name + "님!");
            }
        };
        
        greeting.sayHello("홍길동");
    }
}
```

### 익명 내부 클래스 실전 예시

```java
class ButtonExample {
    public void setupButton() {
        // 익명 내부 클래스로 이벤트 리스너 구현
        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("버튼 클릭됨!");
            }
        });
    }
}

// Thread 생성
Thread thread = new Thread(new Runnable() {
    @Override
    public void run() {
        System.out.println("스레드 실행");
    }
});
thread.start();

// Comparator
List<String> names = Arrays.asList("홍길동", "김철수", "이영희");
Collections.sort(names, new Comparator<String>() {
    @Override
    public int compare(String s1, String s2) {
        return s2.compareTo(s1);  // 역순 정렬
    }
});
```

### 익명 내부 클래스 vs 람다

```java
// 익명 내부 클래스
Runnable runnable1 = new Runnable() {
    @Override
    public void run() {
        System.out.println("익명 내부 클래스");
    }
};

// ✅ 람다 (Java 8+) - 더 간결
Runnable runnable2 = () -> System.out.println("람다");

// Comparator
// 익명 내부 클래스
list.sort(new Comparator<String>() {
    @Override
    public int compare(String s1, String s2) {
        return s1.length() - s2.length();
    }
});

// ✅ 람다
list.sort((s1, s2) -> s1.length() - s2.length());

// ✅ 메서드 레퍼런스
list.sort(Comparator.comparingInt(String::length));
```

### 람다로 대체 불가능한 경우

```java
// 1. 여러 메서드 구현 필요
interface MultiMethod {
    void method1();
    void method2();  // 람다는 단일 메서드만 가능
}

// ❌ 람다 사용 불가
// ✅ 익명 내부 클래스 사용
MultiMethod obj = new MultiMethod() {
    @Override
    public void method1() {
        System.out.println("method1");
    }
    
    @Override
    public void method2() {
        System.out.println("method2");
    }
};

// 2. 상태를 가져야 하는 경우
class Counter {
    public Runnable createCounter() {
        return new Runnable() {
            private int count = 0;  // 상태 유지
            
            @Override
            public void run() {
                count++;
                System.out.println("Count: " + count);
            }
        };
    }
}
```

### 내부 클래스 종류별 비교

```java
class ComparisonExample {
    private String field = "외부 필드";
    private static String staticField = "static 필드";
    
    // 1. 멤버 내부 클래스 - 외부 인스턴스 참조 보유
    class MemberInner {
        void print() {
            System.out.println(field);        // ✅
            System.out.println(staticField);  // ✅
        }
    }
    
    // 2. 정적 내부 클래스 - 외부 인스턴스 참조 없음
    static class StaticNested {
        void print() {
            // System.out.println(field);     // ❌
            System.out.println(staticField);  // ✅
        }
    }
    
    // 3. 로컬 내부 클래스 - 메서드 내부
    void method() {
        final int localVar = 100;
        
        class LocalInner {
            void print() {
                System.out.println(field);      // ✅
                System.out.println(localVar);   // ✅ (effectively final)
            }
        }
        
        new LocalInner().print();
    }
    
    // 4. 익명 내부 클래스
    Runnable createRunnable() {
        return new Runnable() {
            @Override
            public void run() {
                System.out.println(field);  // ✅
            }
        };
    }
}
```

## 주의사항 / 함정

### 1. 멤버 내부 클래스의 메모리 누수

```java
class Activity {
    private byte[] data = new byte[1024 * 1024];  // 1MB
    
    // ❌ 멤버 내부 클래스 - Activity 참조 유지
    class AsyncTask {
        void doWork() {
            // 외부 클래스 참조를 암묵적으로 보유
            // Activity가 종료되어도 AsyncTask가 살아있으면 메모리 누수
        }
    }
}

// ✅ 정적 내부 클래스 사용
class Activity {
    private byte[] data = new byte[1024 * 1024];
    
    static class AsyncTask {
        private WeakReference<Activity> activityRef;
        
        AsyncTask(Activity activity) {
            this.activityRef = new WeakReference<>(activity);
        }
        
        void doWork() {
            Activity activity = activityRef.get();
            if (activity != null) {
                // 작업 수행
            }
        }
    }
}
```

### 2. effectively final 위반

```java
class Example {
    void method() {
        int count = 0;
        
        Runnable runnable = new Runnable() {
            @Override
            public void run() {
                // ❌ count는 effectively final이어야 함
                // count++;  // 컴파일 에러
            }
        };
        
        count++;  // 이것 때문에 effectively final 아님
    }
}

// ✅ 해결: 배열이나 객체 사용
void method() {
    final int[] count = {0};
    
    Runnable runnable = () -> {
        count[0]++;  // ✅ OK
    };
}
```

### 3. 정적 내부 클래스 vs 멤버 내부 클래스 선택

```java
// ❌ 외부 인스턴스가 필요 없는데 멤버 내부 클래스 사용
class Outer {
    class Utility {  // 외부 인스턴스 참조를 불필요하게 보유
        static int calculate(int a, int b) {  // 컴파일 에러
            return a + b;
        }
    }
}

// ✅ 정적 내부 클래스 사용
class Outer {
    static class Utility {
        static int calculate(int a, int b) {
            return a + b;
        }
    }
}
```

### 4. 익명 클래스에서 this 참조

```java
class Outer {
    void method() {
        String field = "outer";
        
        Runnable runnable = new Runnable() {
            String field = "inner";
            
            @Override
            public void run() {
                System.out.println(this.field);    // "inner" (익명 클래스)
                System.out.println(Outer.this.field);  // 컴파일 에러 (메서드의 로컬 변수)
            }
        };
    }
}
```

### 5. 직렬화 문제

```java
class Outer implements Serializable {
    private String field = "data";
    
    // ❌ 멤버 내부 클래스는 직렬화 문제 발생 가능
    class Inner implements Serializable {
        void print() {
            System.out.println(field);
        }
    }
}

// ✅ 정적 내부 클래스 사용
class Outer implements Serializable {
    static class Inner implements Serializable {
        // 외부 클래스와 독립적
    }
}
```

### 6. 과도한 중첩

```java
// ❌ 너무 많은 중첩 - 가독성 저하
class A {
    class B {
        class C {
            class D {
                class E {
                    // ...
                }
            }
        }
    }
}

// ✅ 적절한 분리
class A {
    static class B { }
    static class C { }
}
```

## 관련 개념
- [[Java-람다-Stream]]
- [[Java-함수형인터페이스]]
- [[Java-디자인패턴-Builder]]

## 면접 질문
1. 멤버 내부 클래스와 정적 내부 클래스의 차이점은?
2. 익명 내부 클래스를 람다로 대체할 수 없는 경우는?

## 참고 자료
- Effective Java 3/E - Item 24 (멤버 클래스는 되도록 static으로 만들라)
- Java Language Specification - Nested Classes