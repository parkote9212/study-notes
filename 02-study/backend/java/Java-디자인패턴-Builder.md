---
tags:
  - study
  - java
  - design-pattern
  - builder
  - creational-pattern
created: 2025-02-03
---

# Builder 패턴

## 한 줄 요약
> 복잡한 객체의 생성 과정을 단계별로 분리하여 가독성과 유연성을 높이는 생성 패턴

## 상세 설명

### Builder 패턴이란?

**목적**: 복잡한 객체 생성을 단계별로 구성

**사용 시기**
- 매개변수가 많은 생성자
- 선택적 매개변수가 많을 때
- 객체 생성 과정이 복잡할 때
- 불변 객체를 생성할 때

## 코드 예시

### 1. 기본 Builder 패턴

```java
// ❌ 문제: 생성자가 복잡함
class User {
    private String name;
    private int age;
    private String email;
    private String phone;
    private String address;
    
    public User(String name, int age, String email, String phone, String address) {
        this.name = name;
        this.age = age;
        this.email = email;
        this.phone = phone;
        this.address = address;
    }
}

// 사용 - 무엇이 무엇인지 헷갈림
User user = new User("홍길동", 25, "hong@example.com", "010-1234-5678", "서울");
```

```java
// ✅ Builder 패턴 적용
class User {
    private final String name;       // 필수
    private final int age;           // 필수
    private final String email;      // 선택
    private final String phone;      // 선택
    private final String address;    // 선택
    
    // private 생성자
    private User(Builder builder) {
        this.name = builder.name;
        this.age = builder.age;
        this.email = builder.email;
        this.phone = builder.phone;
        this.address = builder.address;
    }
    
    // 정적 내부 빌더 클래스
    public static class Builder {
        // 필수 매개변수
        private final String name;
        private final int age;
        
        // 선택 매개변수 - 기본값으로 초기화
        private String email = "";
        private String phone = "";
        private String address = "";
        
        // 필수 매개변수는 생성자로
        public Builder(String name, int age) {
            this.name = name;
            this.age = age;
        }
        
        // 선택 매개변수는 메서드로
        public Builder email(String email) {
            this.email = email;
            return this;
        }
        
        public Builder phone(String phone) {
            this.phone = phone;
            return this;
        }
        
        public Builder address(String address) {
            this.address = address;
            return this;
        }
        
        // 최종 객체 생성
        public User build() {
            return new User(this);
        }
    }
}

// 사용 - 명확하고 읽기 쉬움
User user = new User.Builder("홍길동", 25)
    .email("hong@example.com")
    .phone("010-1234-5678")
    .address("서울")
    .build();

// 선택적 매개변수 생략 가능
User simpleUser = new User.Builder("김철수", 30)
    .email("kim@example.com")
    .build();
```

### 2. 유효성 검증이 있는 Builder

```java
class User {
    private final String name;
    private final int age;
    private final String email;
    
    private User(Builder builder) {
        this.name = builder.name;
        this.age = builder.age;
        this.email = builder.email;
    }
    
    public static class Builder {
        private String name;
        private int age;
        private String email;
        
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
        
        public User build() {
            // 유효성 검증
            if (name == null || name.isEmpty()) {
                throw new IllegalStateException("이름은 필수입니다");
            }
            if (age < 0 || age > 150) {
                throw new IllegalStateException("나이는 0~150 사이여야 합니다");
            }
            if (email != null && !email.contains("@")) {
                throw new IllegalStateException("올바른 이메일 형식이 아닙니다");
            }
            
            return new User(this);
        }
    }
}
```

### 3. 실전 예시: HTTP Request

```java
class HttpRequest {
    private final String method;
    private final String url;
    private final Map<String, String> headers;
    private final String body;
    private final int timeout;
    
    private HttpRequest(Builder builder) {
        this.method = builder.method;
        this.url = builder.url;
        this.headers = builder.headers;
        this.body = builder.body;
        this.timeout = builder.timeout;
    }
    
    public static class Builder {
        // 필수
        private final String url;
        
        // 선택
        private String method = "GET";
        private Map<String, String> headers = new HashMap<>();
        private String body = "";
        private int timeout = 5000;
        
        public Builder(String url) {
            this.url = url;
        }
        
        public Builder method(String method) {
            this.method = method;
            return this;
        }
        
        public Builder header(String key, String value) {
            this.headers.put(key, value);
            return this;
        }
        
        public Builder body(String body) {
            this.body = body;
            return this;
        }
        
        public Builder timeout(int timeout) {
            this.timeout = timeout;
            return this;
        }
        
        public HttpRequest build() {
            return new HttpRequest(this);
        }
    }
    
    public void send() {
        System.out.println(method + " " + url);
        System.out.println("Headers: " + headers);
        System.out.println("Body: " + body);
        System.out.println("Timeout: " + timeout + "ms");
    }
}

// 사용
HttpRequest request = new HttpRequest.Builder("https://api.example.com/users")
    .method("POST")
    .header("Content-Type", "application/json")
    .header("Authorization", "Bearer token123")
    .body("{\"name\": \"홍길동\"}")
    .timeout(10000)
    .build();

request.send();
```

### 4. 실전 예시: SQL Query Builder

```java
class SqlQuery {
    private final String table;
    private final List<String> columns;
    private final String whereClause;
    private final String orderBy;
    private final Integer limit;
    
    private SqlQuery(Builder builder) {
        this.table = builder.table;
        this.columns = builder.columns;
        this.whereClause = builder.whereClause;
        this.orderBy = builder.orderBy;
        this.limit = builder.limit;
    }
    
    public static class Builder {
        private String table;
        private List<String> columns = new ArrayList<>();
        private String whereClause = "";
        private String orderBy = "";
        private Integer limit = null;
        
        public Builder from(String table) {
            this.table = table;
            return this;
        }
        
        public Builder select(String... columns) {
            this.columns.addAll(Arrays.asList(columns));
            return this;
        }
        
        public Builder where(String condition) {
            this.whereClause = condition;
            return this;
        }
        
        public Builder orderBy(String orderBy) {
            this.orderBy = orderBy;
            return this;
        }
        
        public Builder limit(int limit) {
            this.limit = limit;
            return this;
        }
        
        public SqlQuery build() {
            if (table == null) {
                throw new IllegalStateException("FROM 절은 필수입니다");
            }
            return new SqlQuery(this);
        }
    }
    
    public String toSql() {
        StringBuilder sql = new StringBuilder("SELECT ");
        
        if (columns.isEmpty()) {
            sql.append("*");
        } else {
            sql.append(String.join(", ", columns));
        }
        
        sql.append(" FROM ").append(table);
        
        if (!whereClause.isEmpty()) {
            sql.append(" WHERE ").append(whereClause);
        }
        
        if (!orderBy.isEmpty()) {
            sql.append(" ORDER BY ").append(orderBy);
        }
        
        if (limit != null) {
            sql.append(" LIMIT ").append(limit);
        }
        
        return sql.toString();
    }
}

// 사용
SqlQuery query = new SqlQuery.Builder()
    .from("users")
    .select("name", "email", "age")
    .where("age >= 20")
    .orderBy("name ASC")
    .limit(10)
    .build();

System.out.println(query.toSql());
// SELECT name, email, age FROM users WHERE age >= 20 ORDER BY name ASC LIMIT 10
```

### 5. Lombok @Builder

```java
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class User {
    private String name;
    private int age;
    private String email;
    private String phone;
    private String address;
}

// 사용 - Lombok이 자동으로 Builder 생성
User user = User.builder()
    .name("홍길동")
    .age(25)
    .email("hong@example.com")
    .build();
```

### 6. 실전 예시: 이메일 메시지

```java
class EmailMessage {
    private final String from;
    private final List<String> to;
    private final List<String> cc;
    private final List<String> bcc;
    private final String subject;
    private final String body;
    private final List<String> attachments;
    
    private EmailMessage(Builder builder) {
        this.from = builder.from;
        this.to = new ArrayList<>(builder.to);
        this.cc = new ArrayList<>(builder.cc);
        this.bcc = new ArrayList<>(builder.bcc);
        this.subject = builder.subject;
        this.body = builder.body;
        this.attachments = new ArrayList<>(builder.attachments);
    }
    
    public static class Builder {
        private String from;
        private List<String> to = new ArrayList<>();
        private List<String> cc = new ArrayList<>();
        private List<String> bcc = new ArrayList<>();
        private String subject;
        private String body;
        private List<String> attachments = new ArrayList<>();
        
        public Builder from(String from) {
            this.from = from;
            return this;
        }
        
        public Builder to(String... recipients) {
            this.to.addAll(Arrays.asList(recipients));
            return this;
        }
        
        public Builder cc(String... recipients) {
            this.cc.addAll(Arrays.asList(recipients));
            return this;
        }
        
        public Builder bcc(String... recipients) {
            this.bcc.addAll(Arrays.asList(recipients));
            return this;
        }
        
        public Builder subject(String subject) {
            this.subject = subject;
            return this;
        }
        
        public Builder body(String body) {
            this.body = body;
            return this;
        }
        
        public Builder attach(String... files) {
            this.attachments.addAll(Arrays.asList(files));
            return this;
        }
        
        public EmailMessage build() {
            if (from == null || from.isEmpty()) {
                throw new IllegalStateException("발신자는 필수입니다");
            }
            if (to.isEmpty()) {
                throw new IllegalStateException("수신자는 필수입니다");
            }
            return new EmailMessage(this);
        }
    }
    
    public void send() {
        System.out.println("From: " + from);
        System.out.println("To: " + to);
        if (!cc.isEmpty()) System.out.println("CC: " + cc);
        if (!bcc.isEmpty()) System.out.println("BCC: " + bcc);
        System.out.println("Subject: " + subject);
        System.out.println("Body: " + body);
        if (!attachments.isEmpty()) {
            System.out.println("Attachments: " + attachments);
        }
    }
}

// 사용
EmailMessage email = new EmailMessage.Builder()
    .from("sender@example.com")
    .to("user1@example.com", "user2@example.com")
    .cc("manager@example.com")
    .subject("월간 보고서")
    .body("첨부된 보고서를 확인해주세요.")
    .attach("report.pdf", "data.xlsx")
    .build();

email.send();
```

## 주의사항 / 함정

### 1. 과도한 사용

```java
// ❌ 간단한 객체에 Builder 사용
class Point {
    private int x;
    private int y;
    
    public static class Builder { ... }
}

// ✅ 간단한 경우 생성자 사용
class Point {
    private int x;
    private int y;
    
    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
}
```

### 2. 불변성 보장

```java
// ❌ 가변 컬렉션 반환
class User {
    private List<String> roles;
    
    public List<String> getRoles() {
        return roles;  // 외부에서 수정 가능!
    }
}

// ✅ 불변 컬렉션 반환
class User {
    private final List<String> roles;
    
    private User(Builder builder) {
        this.roles = new ArrayList<>(builder.roles);
    }
    
    public List<String> getRoles() {
        return Collections.unmodifiableList(roles);
    }
}
```

## 관련 개념
- [[Java-디자인패턴-Factory]]
- [[Java-불변객체]]
- [[Lombok-Builder]]

## 면접 질문
1. Builder 패턴의 장점은 무엇인가요?
2. 언제 Builder 패턴을 사용해야 하나요?

## 참고 자료
- Effective Java - Item 2: Builder Pattern
- Design Patterns - Gang of Four