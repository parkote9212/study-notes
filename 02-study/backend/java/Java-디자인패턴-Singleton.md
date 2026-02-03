---
tags:
  - study
  - java
  - design-pattern
  - singleton
  - creational-pattern
created: 2025-02-03
---

# Singleton 패턴

## 한 줄 요약
> 클래스의 인스턴스가 오직 하나만 생성되도록 보장하는 생성 패턴

## 상세 설명

### Singleton 패턴이란?

**목적**: 애플리케이션 전체에서 단 하나의 인스턴스만 존재하도록 보장

**사용 시기**
- 설정 관리자 (Configuration Manager)
- 로거 (Logger)
- 데이터베이스 연결 풀
- 캐시
- 스레드 풀

## 코드 예시

### 1. Eager Initialization (이른 초기화)

```java
public class Singleton {
    // 클래스 로딩 시점에 인스턴스 생성
    private static final Singleton INSTANCE = new Singleton();
    
    private Singleton() {
        // private 생성자로 외부 생성 차단
    }
    
    public static Singleton getInstance() {
        return INSTANCE;
    }
}

// 장점: 스레드 안전, 구현 간단
// 단점: 사용하지 않아도 메모리 차지
```

### 2. Lazy Initialization (늦은 초기화)

```java
public class Singleton {
    private static Singleton instance;
    
    private Singleton() {}
    
    // ❌ 스레드 안전하지 않음
    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}

// 장점: 필요할 때만 생성
// 단점: 멀티스레드 환경에서 여러 인스턴스 생성 가능
```

### 3. Thread-Safe Lazy Initialization

```java
public class Singleton {
    private static Singleton instance;
    
    private Singleton() {}
    
    // ✅ synchronized로 스레드 안전 보장
    public static synchronized Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}

// 장점: 스레드 안전
// 단점: 매번 synchronized 오버헤드 (성능 저하)
```

### 4. Double-Checked Locking

```java
public class Singleton {
    // volatile로 가시성 보장
    private static volatile Singleton instance;
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        // 첫 번째 체크 (락 없이)
        if (instance == null) {
            synchronized (Singleton.class) {
                // 두 번째 체크 (락 안에서)
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}

// 장점: 성능 개선, 스레드 안전
// 단점: 복잡한 구현
```

### 5. Bill Pugh Solution (권장)

```java
public class Singleton {
    private Singleton() {}
    
    // static 내부 클래스는 getInstance() 호출 시에만 로딩
    private static class SingletonHolder {
        private static final Singleton INSTANCE = new Singleton();
    }
    
    public static Singleton getInstance() {
        return SingletonHolder.INSTANCE;
    }
}

// 장점: Lazy loading, 스레드 안전, 성능 우수
// 단점: 없음 (가장 권장되는 방법)
```

### 6. Enum Singleton (최고의 방법)

```java
public enum Singleton {
    INSTANCE;
    
    public void doSomething() {
        System.out.println("작업 수행");
    }
}

// 사용
Singleton.INSTANCE.doSomething();

// 장점: 
// - 직렬화 안전
// - 리플렉션 공격 방지
// - 스레드 안전
// - 코드 간결
// 단점: Enum이므로 상속 불가
```

### 실전 예시: Configuration Manager

```java
public class ConfigurationManager {
    private static volatile ConfigurationManager instance;
    private Properties properties;
    
    private ConfigurationManager() {
        properties = new Properties();
        loadConfiguration();
    }
    
    public static ConfigurationManager getInstance() {
        if (instance == null) {
            synchronized (ConfigurationManager.class) {
                if (instance == null) {
                    instance = new ConfigurationManager();
                }
            }
        }
        return instance;
    }
    
    private void loadConfiguration() {
        // 설정 파일 로드
        properties.setProperty("db.url", "jdbc:mysql://localhost:3306/mydb");
        properties.setProperty("db.username", "admin");
    }
    
    public String getProperty(String key) {
        return properties.getProperty(key);
    }
}

// 사용
String dbUrl = ConfigurationManager.getInstance().getProperty("db.url");
```

### 실전 예시: Logger

```java
public enum Logger {
    INSTANCE;
    
    public void log(String message) {
        System.out.println("[" + java.time.LocalTime.now() + "] " + message);
    }
    
    public void error(String message) {
        System.err.println("[" + java.time.LocalTime.now() + "] ERROR: " + message);
    }
}

// 사용
Logger.INSTANCE.log("애플리케이션 시작");
Logger.INSTANCE.error("오류 발생");
```

### 실전 예시: Database Connection Pool

```java
public class ConnectionPool {
    private static volatile ConnectionPool instance;
    private List<Connection> availableConnections;
    private List<Connection> usedConnections;
    private static final int INITIAL_POOL_SIZE = 10;
    
    private ConnectionPool() {
        availableConnections = new ArrayList<>();
        usedConnections = new ArrayList<>();
        
        for (int i = 0; i < INITIAL_POOL_SIZE; i++) {
            availableConnections.add(createConnection());
        }
    }
    
    public static ConnectionPool getInstance() {
        if (instance == null) {
            synchronized (ConnectionPool.class) {
                if (instance == null) {
                    instance = new ConnectionPool();
                }
            }
        }
        return instance;
    }
    
    public synchronized Connection getConnection() {
        if (availableConnections.isEmpty()) {
            availableConnections.add(createConnection());
        }
        
        Connection connection = availableConnections.remove(
            availableConnections.size() - 1
        );
        usedConnections.add(connection);
        return connection;
    }
    
    public synchronized void releaseConnection(Connection connection) {
        usedConnections.remove(connection);
        availableConnections.add(connection);
    }
    
    private Connection createConnection() {
        // 실제 DB 연결 생성
        return new MockConnection();
    }
    
    private static class MockConnection implements Connection {
        // Connection 구현...
    }
}

// 사용
Connection conn = ConnectionPool.getInstance().getConnection();
try {
    // DB 작업
} finally {
    ConnectionPool.getInstance().releaseConnection(conn);
}
```

## 주의사항 / 함정

### 1. 리플렉션으로 파괴

```java
public class Singleton {
    private static final Singleton INSTANCE = new Singleton();
    
    private Singleton() {
        // 리플렉션 방어
        if (INSTANCE != null) {
            throw new RuntimeException("Singleton 인스턴스가 이미 존재합니다");
        }
    }
    
    public static Singleton getInstance() {
        return INSTANCE;
    }
}

// ❌ 리플렉션 공격
Constructor<Singleton> constructor = Singleton.class.getDeclaredConstructor();
constructor.setAccessible(true);
Singleton instance2 = constructor.newInstance();  // 새 인스턴스 생성됨!

// ✅ Enum은 자동으로 방어됨
```

### 2. 직렬화 문제

```java
public class Singleton implements Serializable {
    private static final Singleton INSTANCE = new Singleton();
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        return INSTANCE;
    }
    
    // ✅ 역직렬화 시 새 인스턴스 생성 방지
    protected Object readResolve() {
        return INSTANCE;
    }
}
```

### 3. 클론 방지

```java
public class Singleton implements Cloneable {
    private static final Singleton INSTANCE = new Singleton();
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        return INSTANCE;
    }
    
    // ✅ 클론 방지
    @Override
    protected Object clone() throws CloneNotSupportedException {
        throw new CloneNotSupportedException();
    }
}
```

### 4. 테스트 어려움

```java
// ❌ Singleton은 테스트하기 어려움
public class UserService {
    public void createUser(String name) {
        Logger.INSTANCE.log("사용자 생성: " + name);
        // 테스트에서 Logger를 Mock으로 교체할 수 없음!
    }
}

// ✅ 의존성 주입으로 해결
public class UserService {
    private Logger logger;
    
    public UserService(Logger logger) {
        this.logger = logger;
    }
    
    public void createUser(String name) {
        logger.log("사용자 생성: " + name);
    }
}
```

## 관련 개념
- [[Java-열거형Enum]]
- [[Java-멀티스레드]]
- [[Java-디자인패턴-Factory]]

## 면접 질문
1. Singleton 패턴의 장단점은?
2. Double-Checked Locking에서 volatile이 필요한 이유는?

## 참고 자료
- Effective Java - Item 3: Singleton
- Design Patterns - Gang of Four