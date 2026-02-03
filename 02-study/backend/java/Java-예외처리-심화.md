---
tags:
  - study
  - java
  - exception
  - advanced
  - reactive
created: 2025-02-03
---

# Java 예외처리 심화

## 한 줄 요약
> 멀티스레드, 비동기, 리액티브 환경에서의 고급 예외 처리 기법

## 상세 설명

### 1. 예외 처리 고급 주제

**심화 학습 범위**
1. 멀티스레드 환경 예외 처리
2. CompletableFuture 예외 처리
3. Stream API 예외 처리
4. 예외 변환 패턴
5. Suppressed Exceptions

## 코드 예시

### 1. 멀티스레드 예외 처리

#### ExecutorService에서의 예외

```java
ExecutorService executor = Executors.newFixedThreadPool(3);

// ❌ 예외가 사라짐
executor.submit(() -> {
    throw new RuntimeException("스레드 내부 예외");
    // 예외가 콘솔에 출력되지 않음!
});

// ✅ Future로 예외 확인
Future<?> future = executor.submit(() -> {
    throw new RuntimeException("스레드 내부 예외");
});

try {
    future.get();  // 여기서 예외 발생
} catch (ExecutionException e) {
    System.out.println("원인: " + e.getCause());
}

executor.shutdown();
```

#### Thread.UncaughtExceptionHandler 사용

```java
Thread.setDefaultUncaughtExceptionHandler((thread, throwable) -> {
    System.err.println("스레드 " + thread.getName() + "에서 예외 발생");
    throwable.printStackTrace();
});

Thread thread = new Thread(() -> {
    throw new RuntimeException("처리되지 않은 예외");
});
thread.start();
```

#### ThreadPoolExecutor 커스텀

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    2, 4, 60L, TimeUnit.SECONDS,
    new LinkedBlockingQueue<>()
) {
    @Override
    protected void afterExecute(Runnable r, Throwable t) {
        super.afterExecute(r, t);
        
        if (t == null && r instanceof Future<?>) {
            try {
                Future<?> future = (Future<?>) r;
                if (future.isDone()) {
                    future.get();
                }
            } catch (CancellationException ce) {
                t = ce;
            } catch (ExecutionException ee) {
                t = ee.getCause();
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
            }
        }
        
        if (t != null) {
            System.err.println("작업 실행 중 예외 발생: " + t.getMessage());
        }
    }
};
```

### 2. CompletableFuture 예외 처리

#### 기본 예외 처리

```java
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> {
        if (Math.random() > 0.5) {
            throw new RuntimeException("랜덤 실패");
        }
        return "성공";
    })
    .exceptionally(ex -> {
        System.out.println("예외 처리: " + ex.getMessage());
        return "기본값";
    });

System.out.println(future.join());
```

#### handle()로 정상/예외 모두 처리

```java
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> {
        if (Math.random() > 0.5) {
            throw new RuntimeException("실패");
        }
        return "성공";
    })
    .handle((result, ex) -> {
        if (ex != null) {
            return "예외 발생: " + ex.getMessage();
        }
        return "정상: " + result;
    });
```

#### whenComplete()로 부수 효과 처리

```java
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> "작업 결과")
    .whenComplete((result, ex) -> {
        if (ex != null) {
            System.err.println("실패: " + ex.getMessage());
        } else {
            System.out.println("성공: " + result);
        }
    });
```

#### 실전 예시: API 호출 재시도

```java
public CompletableFuture<String> callApiWithRetry(String url, int maxRetries) {
    return callApi(url)
        .handle((result, ex) -> {
            if (ex != null && maxRetries > 0) {
                System.out.println("재시도 남은 횟수: " + maxRetries);
                return callApiWithRetry(url, maxRetries - 1);
            } else if (ex != null) {
                throw new CompletionException("최대 재시도 횟수 초과", ex);
            }
            return CompletableFuture.completedFuture(result);
        })
        .thenCompose(f -> f);
}

private CompletableFuture<String> callApi(String url) {
    return CompletableFuture.supplyAsync(() -> {
        // API 호출 로직
        if (Math.random() > 0.7) {
            throw new RuntimeException("API 호출 실패");
        }
        return "API 응답";
    });
}
```

### 3. Stream API 예외 처리

#### Checked Exception을 Unchecked로 변환

```java
@FunctionalInterface
interface ThrowingFunction<T, R> {
    R apply(T t) throws Exception;
}

public static <T, R> Function<T, R> wrap(ThrowingFunction<T, R> f) {
    return t -> {
        try {
            return f.apply(t);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    };
}

// 사용
List<String> urls = Arrays.asList("url1", "url2", "url3");

List<String> results = urls.stream()
    .map(wrap(url -> readUrl(url)))  // IOException을 던지는 메서드
    .collect(Collectors.toList());

// readUrl 메서드
String readUrl(String url) throws IOException {
    // URL 읽기
    return "content";
}
```

#### Either 패턴으로 예외 처리

```java
sealed interface Either<L, R> {}
record Left<L, R>(L value) implements Either<L, R> {}
record Right<L, R>(R value) implements Either<L, R> {}

public Either<Exception, String> readFileSafe(String path) {
    try {
        String content = Files.readString(Path.of(path));
        return new Right<>(content);
    } catch (Exception e) {
        return new Left<>(e);
    }
}

// Stream에서 사용
List<String> files = Arrays.asList("file1.txt", "file2.txt");

List<Either<Exception, String>> results = files.stream()
    .map(this::readFileSafe)
    .toList();

// 성공한 것만 필터링
List<String> successResults = results.stream()
    .filter(either -> either instanceof Right)
    .map(either -> ((Right<Exception, String>) either).value())
    .toList();
```

### 4. try-with-resources 심화

#### 다중 리소스 관리

```java
try (FileInputStream fis = new FileInputStream("input.txt");
     BufferedInputStream bis = new BufferedInputStream(fis);
     FileOutputStream fos = new FileOutputStream("output.txt");
     BufferedOutputStream bos = new BufferedOutputStream(fos)) {
    
    byte[] buffer = new byte[1024];
    int length;
    while ((length = bis.read(buffer)) > 0) {
        bos.write(buffer, 0, length);
    }
    
} catch (IOException e) {
    System.err.println("파일 처리 실패: " + e.getMessage());
}
// 모든 리소스가 역순으로 자동 close됨
```

#### 커스텀 AutoCloseable

```java
class DatabaseConnection implements AutoCloseable {
    private final String connectionId;
    private boolean closed = false;
    
    public DatabaseConnection(String connectionId) {
        this.connectionId = connectionId;
        System.out.println("연결 생성: " + connectionId);
    }
    
    public void executeQuery(String query) {
        if (closed) {
            throw new IllegalStateException("연결이 이미 닫혔습니다");
        }
        System.out.println("쿼리 실행: " + query);
    }
    
    @Override
    public void close() {
        if (!closed) {
            System.out.println("연결 종료: " + connectionId);
            closed = true;
        }
    }
}

// 사용
try (DatabaseConnection conn = new DatabaseConnection("DB-001")) {
    conn.executeQuery("SELECT * FROM users");
} // 자동으로 close() 호출
```

### 5. Suppressed Exceptions

#### Suppressed Exception이란?

```java
class Resource implements AutoCloseable {
    private final String name;
    
    public Resource(String name) throws Exception {
        this.name = name;
        if (name.equals("bad")) {
            throw new Exception("리소스 생성 실패");
        }
        System.out.println(name + " 생성됨");
    }
    
    public void use() throws Exception {
        throw new Exception(name + " 사용 중 예외");
    }
    
    @Override
    public void close() throws Exception {
        throw new Exception(name + " 종료 중 예외");
    }
}

try (Resource r = new Resource("test")) {
    r.use();
} catch (Exception e) {
    System.out.println("주 예외: " + e.getMessage());
    
    // Suppressed exceptions 확인
    Throwable[] suppressed = e.getSuppressed();
    for (Throwable t : suppressed) {
        System.out.println("억제된 예외: " + t.getMessage());
    }
}

// 출력:
// test 생성됨
// 주 예외: test 사용 중 예외
// 억제된 예외: test 종료 중 예외
```

### 6. 예외 변환 패턴

#### 계층별 예외 변환

```java
// DAO 계층
class UserDao {
    public User findById(Long id) throws SQLException {
        // DB 조회
        throw new SQLException("DB 연결 실패");
    }
}

// Service 계층
class UserService {
    private UserDao userDao;
    
    public User getUser(Long id) {
        try {
            return userDao.findById(id);
        } catch (SQLException e) {
            // SQL 예외를 비즈니스 예외로 변환
            throw new UserServiceException("사용자 조회 실패: " + id, e);
        }
    }
}

// Controller 계층
class UserController {
    private UserService userService;
    
    public ResponseEntity<?> getUser(Long id) {
        try {
            User user = userService.getUser(id);
            return ResponseEntity.ok(user);
        } catch (UserServiceException e) {
            // 비즈니스 예외를 HTTP 응답으로 변환
            return ResponseEntity.internalServerError()
                .body(Map.of("error", e.getMessage()));
        }
    }
}
```

### 7. 실전 예시: 분산 트랜잭션 롤백

```java
@Service
public class OrderService {
    
    @Autowired
    private PaymentService paymentService;
    
    @Autowired
    private InventoryService inventoryService;
    
    @Autowired
    private NotificationService notificationService;
    
    public void createOrder(Order order) {
        String paymentId = null;
        String inventoryId = null;
        
        try {
            // 1. 결제 처리
            paymentId = paymentService.processPayment(order);
            
            // 2. 재고 차감
            inventoryId = inventoryService.decreaseStock(order);
            
            // 3. 알림 전송
            notificationService.sendConfirmation(order);
            
        } catch (PaymentException e) {
            log.error("결제 실패", e);
            throw new OrderException("주문 실패: 결제 오류", e);
            
        } catch (InventoryException e) {
            log.error("재고 차감 실패", e);
            
            // 결제 롤백
            if (paymentId != null) {
                try {
                    paymentService.refund(paymentId);
                } catch (Exception rollbackEx) {
                    log.error("결제 롤백 실패", rollbackEx);
                }
            }
            
            throw new OrderException("주문 실패: 재고 부족", e);
            
        } catch (NotificationException e) {
            log.warn("알림 전송 실패 (주문은 성공)", e);
            // 알림 실패는 주문을 실패시키지 않음
            
        } catch (Exception e) {
            log.error("예상치 못한 오류", e);
            
            // 모든 작업 롤백
            if (inventoryId != null) {
                try {
                    inventoryService.restoreStock(inventoryId);
                } catch (Exception ex) {
                    log.error("재고 복구 실패", ex);
                }
            }
            
            if (paymentId != null) {
                try {
                    paymentService.refund(paymentId);
                } catch (Exception ex) {
                    log.error("결제 롤백 실패", ex);
                }
            }
            
            throw new OrderException("주문 처리 중 오류 발생", e);
        }
    }
}
```

### 8. 실전 예시: Circuit Breaker 패턴

```java
public class CircuitBreaker {
    private final int failureThreshold;
    private final long timeout;
    private int failureCount = 0;
    private long lastFailureTime = 0;
    private State state = State.CLOSED;
    
    enum State {
        CLOSED,  // 정상 작동
        OPEN,    // 차단됨 (빠른 실패)
        HALF_OPEN // 복구 시도 중
    }
    
    public CircuitBreaker(int failureThreshold, long timeout) {
        this.failureThreshold = failureThreshold;
        this.timeout = timeout;
    }
    
    public <T> T call(Callable<T> operation) throws Exception {
        if (state == State.OPEN) {
            if (System.currentTimeMillis() - lastFailureTime > timeout) {
                state = State.HALF_OPEN;
            } else {
                throw new CircuitBreakerOpenException("서비스가 일시적으로 중단되었습니다");
            }
        }
        
        try {
            T result = operation.call();
            reset();
            return result;
            
        } catch (Exception e) {
            recordFailure();
            throw e;
        }
    }
    
    private void recordFailure() {
        failureCount++;
        lastFailureTime = System.currentTimeMillis();
        
        if (failureCount >= failureThreshold) {
            state = State.OPEN;
        }
    }
    
    private void reset() {
        failureCount = 0;
        state = State.CLOSED;
    }
}

// 사용
CircuitBreaker breaker = new CircuitBreaker(5, 60000);  // 5회 실패 시 60초 차단

try {
    String result = breaker.call(() -> callExternalApi());
    System.out.println("API 호출 성공: " + result);
} catch (CircuitBreakerOpenException e) {
    System.out.println("서비스 차단됨, 캐시 사용");
} catch (Exception e) {
    System.out.println("API 호출 실패: " + e.getMessage());
}
```

## 주의사항 / 함정

### 1. 스레드 풀에서 예외 무시

```java
// ❌ 예외가 사라짐
ExecutorService executor = Executors.newFixedThreadPool(2);
executor.execute(() -> {
    throw new RuntimeException("예외");  // 로그도 안 남음!
});

// ✅ Future 사용 또는 afterExecute 오버라이드
```

### 2. CompletableFuture 체이닝 중 예외

```java
// ❌ 중간 예외가 전파 안됨
CompletableFuture.supplyAsync(() -> "data")
    .thenApply(s -> {
        throw new RuntimeException("중간 예외");
    })
    .thenAccept(System.out::println);  // 실행 안됨

// ✅ exceptionally 또는 handle 사용
```

### 3. try-with-resources 생성자 예외

```java
// ⚠️ 첫 번째 리소스 생성 성공 후 두 번째 실패 시
try (R1 r1 = new R1();  // 성공
     R2 r2 = new R2()) { // 실패
    // r1.close()가 호출되지 않을 수 있음!
}

// ✅ 중첩 try 사용
try (R1 r1 = new R1()) {
    try (R2 r2 = new R2()) {
        // 안전
    }
}
```

## 관련 개념
- [[Java-예외처리-Exception]]
- [[Java-CompletableFuture]]
- [[Java-멀티스레드]]

## 면접 질문
1. ExecutorService에서 예외가 사라지는 이유는?
2. Suppressed Exception은 언제 발생하나요?

## 참고 자료
- Java Concurrency in Practice
- Effective Java - Exception Handling
- CompletableFuture Documentation