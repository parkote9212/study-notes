---
tags:
  - study
  - spring
  - advanced
  - async
  - concurrency
created: 2025-02-08
---

# 비동기처리 Async

## 한 줄 요약
> Spring의 @Async는 메서드를 별도의 스레드에서 비동기로 실행하여, 시간이 오래 걸리는 작업을 논블로킹 방식으로 처리하고 응답 시간을 개선한다.

## 상세 설명

### 비동기 처리란?
- **메서드 호출 즉시 반환**, 작업은 백그라운드에서 실행
- **논블로킹(Non-blocking)**: 메인 스레드가 대기하지 않음
- **병렬 처리**: 여러 작업을 동시에 수행

### 왜 비동기 처리가 필요한가?
```java
// ❌ 동기 처리: 각 작업이 순차 실행 (총 6초)
public void process() {
    sendEmail();        // 2초
    callExternalAPI();  // 3초
    updateCache();      // 1초
}  // 총 6초 소요

// ✅ 비동기 처리: 동시 실행 (최대 3초)
public void process() {
    asyncSendEmail();        // 비동기
    asyncCallExternalAPI();  // 비동기
    asyncUpdateCache();      // 비동기
}  // 거의 즉시 반환, 백그라운드에서 실행
```

### @Async 사용 시나리오
- 이메일/SMS 발송
- 외부 API 호출
- 파일 처리 (업로드, 다운로드)
- 로그 기록
- 알림 발송
- 대용량 데이터 처리

### @Async 동작 원리
```
1. @EnableAsync 활성화
   ↓
2. @Async 메서드 호출
   ↓
3. Spring AOP 프록시가 가로챔
   ↓
4. TaskExecutor에 작업 전달
   ↓
5. 별도 스레드에서 실행
   ↓
6. 호출한 메서드는 즉시 반환
```

### 반환 타입
- **void**: 결과 불필요
- **Future\<T\>**: 미래 결과 조회 가능
- **CompletableFuture\<T\>**: 콜백, 조합 가능 (권장)

## 코드 예시

```java
// 1. @EnableAsync 활성화
@EnableAsync
@Configuration
public class AsyncConfig {
    
    @Bean(name = "taskExecutor")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);      // 기본 스레드 수
        executor.setMaxPoolSize(10);      // 최대 스레드 수
        executor.setQueueCapacity(100);   // 큐 크기
        executor.setThreadNamePrefix("async-");
        executor.initialize();
        return executor;
    }
}

// 2. 기본 @Async (void 반환)
@Service
@Slf4j
public class EmailService {
    
    @Async
    public void sendEmail(String to, String subject, String body) {
        log.info("이메일 발송 시작: {}", to);
        
        try {
            Thread.sleep(2000);  // 이메일 발송 시뮬레이션
            log.info("이메일 발송 완료: {}", to);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

// 사용
@RestController
@RequiredArgsConstructor
public class UserController {
    
    private final EmailService emailService;
    
    @PostMapping("/users")
    public ResponseEntity<String> createUser(@RequestBody User user) {
        // 사용자 저장
        userService.save(user);
        
        // 이메일 비동기 발송 (즉시 반환)
        emailService.sendEmail(user.getEmail(), "환영합니다", "가입 완료");
        
        // 이메일 발송 완료를 기다리지 않고 즉시 응답
        return ResponseEntity.ok("회원가입 완료");
    }
}

// 3. Future 반환 (결과 조회 가능)
@Service
public class DataService {
    
    @Async
    public Future<String> processData(String data) {
        try {
            Thread.sleep(1000);
            String result = data.toUpperCase();
            return new AsyncResult<>(result);  // Future로 감싸서 반환
        } catch (Exception e) {
            return new AsyncResult<>(null);
        }
    }
}

// 사용
public void useWithFuture() throws Exception {
    Future<String> future = dataService.processData("hello");
    
    // 다른 작업 수행
    doOtherWork();
    
    // 결과가 필요할 때 대기
    String result = future.get();  // 블로킹 (결과가 올 때까지 대기)
    System.out.println(result);
}

// 4. CompletableFuture 반환 (권장)
@Service
public class ApiService {
    
    @Async
    public CompletableFuture<String> callExternalAPI(String endpoint) {
        try {
            Thread.sleep(2000);
            String response = restTemplate.getForObject(endpoint, String.class);
            return CompletableFuture.completedFuture(response);
        } catch (Exception e) {
            return CompletableFuture.failedFuture(e);
        }
    }
}

// 사용
public void useWithCompletableFuture() {
    CompletableFuture<String> future = apiService.callExternalAPI("/api/data");
    
    // 콜백 등록
    future.thenAccept(result -> {
        System.out.println("결과: " + result);
    }).exceptionally(ex -> {
        System.err.println("에러: " + ex.getMessage());
        return null;
    });
    
    // 즉시 다음 코드 실행 (논블로킹)
}

// 5. 여러 비동기 작업 병렬 실행
@Service
@RequiredArgsConstructor
public class ReportService {
    
    private final UserDataService userDataService;
    private final OrderDataService orderDataService;
    private final ProductDataService productDataService;
    
    public CompletableFuture<Report> generateReport() {
        // 세 작업을 병렬로 실행
        CompletableFuture<UserData> userFuture = 
            userDataService.getUserData();
        CompletableFuture<OrderData> orderFuture = 
            orderDataService.getOrderData();
        CompletableFuture<ProductData> productFuture = 
            productDataService.getProductData();
        
        // 모든 작업 완료 대기 후 결합
        return CompletableFuture.allOf(userFuture, orderFuture, productFuture)
            .thenApply(v -> {
                UserData userData = userFuture.join();
                OrderData orderData = orderFuture.join();
                ProductData productData = productFuture.join();
                
                return new Report(userData, orderData, productData);
            });
    }
}

// 6. TaskExecutor 지정
@Configuration
public class AsyncConfig {
    
    @Bean(name = "emailExecutor")
    public Executor emailExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(5);
        executor.setThreadNamePrefix("email-");
        executor.initialize();
        return executor;
    }
    
    @Bean(name = "apiExecutor")
    public Executor apiExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(20);
        executor.setThreadNamePrefix("api-");
        executor.initialize();
        return executor;
    }
}

@Service
public class AsyncService {
    
    @Async("emailExecutor")  // 특정 Executor 사용
    public void sendEmail(String to) {
        // emailExecutor로 실행
    }
    
    @Async("apiExecutor")
    public CompletableFuture<String> callAPI(String url) {
        // apiExecutor로 실행
        return CompletableFuture.completedFuture("response");
    }
}

// 7. 예외 처리
@Service
@Slf4j
public class AsyncExceptionService {
    
    @Async
    public CompletableFuture<String> processWithException() {
        try {
            if (someCondition) {
                throw new CustomException("에러 발생");
            }
            return CompletableFuture.completedFuture("성공");
        } catch (Exception e) {
            log.error("비동기 작업 실패", e);
            return CompletableFuture.failedFuture(e);
        }
    }
}

// 예외 핸들러
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {
    
    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return new AsyncExceptionHandler();
    }
}

public class AsyncExceptionHandler implements AsyncUncaughtExceptionHandler {
    
    @Override
    public void handleUncaughtException(Throwable ex, Method method, Object... params) {
        log.error("비동기 메서드 예외 발생: {}", method.getName(), ex);
        // 알림 발송, 로깅 등
    }
}

// 8. 타임아웃 설정
@Service
public class TimeoutService {
    
    @Async
    public CompletableFuture<String> processWithTimeout() {
        CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(5000);
                return "완료";
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        });
        
        // 3초 타임아웃
        return future.orTimeout(3, TimeUnit.SECONDS);
    }
}

// 9. 비동기 체이닝
@Service
public class ChainService {
    
    @Async
    public CompletableFuture<User> getUser(Long id) {
        return CompletableFuture.completedFuture(userRepository.findById(id).get());
    }
    
    @Async
    public CompletableFuture<List<Order>> getOrders(User user) {
        return CompletableFuture.completedFuture(
            orderRepository.findByUserId(user.getId())
        );
    }
    
    public CompletableFuture<OrderSummary> getUserOrderSummary(Long userId) {
        return getUser(userId)
            .thenCompose(user -> getOrders(user))  // 순차 실행
            .thenApply(orders -> new OrderSummary(orders));
    }
}

// 10. 동기 메서드와 혼용
@Service
@RequiredArgsConstructor
public class MixedService {
    
    private final AsyncService asyncService;
    
    public void processOrder(Order order) {
        // 1. 주문 저장 (동기)
        orderRepository.save(order);
        
        // 2. 재고 감소 (동기)
        inventoryService.decrease(order.getProductId(), order.getQuantity());
        
        // 3. 이메일 발송 (비동기)
        asyncService.sendOrderConfirmationEmail(order);
        
        // 4. 알림 발송 (비동기)
        asyncService.sendPushNotification(order);
        
        // 5. 즉시 응답 (이메일, 알림 완료 기다리지 않음)
    }
}

// 11. @Transactional과 @Async 함께 사용
@Service
public class TransactionalAsyncService {
    
    // ❌ 같은 클래스 내부: 트랜잭션 전파 안 됨
    @Transactional
    public void outerMethod() {
        this.innerAsyncMethod();  // @Async 동작 안 함!
    }
    
    @Async
    @Transactional
    public void innerAsyncMethod() {
        // 트랜잭션도 시작 안 됨
    }
}

// ✅ 해결: 다른 빈으로 분리
@Service
@RequiredArgsConstructor
public class OrderService {
    
    private final AsyncOrderService asyncOrderService;
    
    @Transactional
    public void createOrder(Order order) {
        orderRepository.save(order);
        
        // 다른 빈 호출 → @Async 동작
        asyncOrderService.processAfterOrder(order);
    }
}

@Service
public class AsyncOrderService {
    
    @Async
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void processAfterOrder(Order order) {
        // 새 트랜잭션에서 비동기 실행
        logRepository.save(new OrderLog(order.getId()));
    }
}

// 12. 실무 패턴: 배치 처리
@Service
@Slf4j
public class BatchEmailService {
    
    @Async
    public CompletableFuture<Void> sendBulkEmails(List<String> recipients) {
        log.info("배치 이메일 발송 시작: {} 명", recipients.size());
        
        List<CompletableFuture<Void>> futures = recipients.stream()
            .map(recipient -> CompletableFuture.runAsync(() -> {
                sendEmail(recipient);
            }))
            .collect(Collectors.toList());
        
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]));
    }
    
    private void sendEmail(String recipient) {
        // 이메일 발송 로직
    }
}
```

## 주의사항 / 함정

### 1. 같은 클래스 내부 호출
```java
@Service
public class AsyncService {
    
    public void outerMethod() {
        this.innerAsyncMethod();  // ❌ @Async 동작 안 함!
    }
    
    @Async
    public void innerAsyncMethod() {
        // 프록시를 거치지 않아 비동기 실행 안 됨
    }
}

// ✅ 해결: 다른 빈으로 분리
@Service
@RequiredArgsConstructor
public class OuterService {
    private final AsyncService asyncService;
    
    public void outerMethod() {
        asyncService.innerAsyncMethod();  // 다른 빈 호출
    }
}
```

### 2. @Transactional과 함께 사용
```java
// ❌ 트랜잭션이 다른 스레드로 전파 안 됨
@Transactional
@Async
public void method() {
    // 비동기 스레드에서 트랜잭션 없음!
}

// ✅ 비동기 메서드 내부에서 새 트랜잭션 시작
@Async
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void method() {
    // 새 트랜잭션
}
```

### 3. 스레드 풀 고갈
```java
// ❌ 스레드 풀 설정 없이 무한 생성
@EnableAsync
@Configuration
public class AsyncConfig {
    // 기본 SimpleAsyncTaskExecutor 사용
    // → 요청마다 새 스레드 생성 → 메모리 고갈!
}

// ✅ ThreadPoolTaskExecutor 사용
@Bean
public Executor taskExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(10);
    executor.setMaxPoolSize(20);
    executor.setQueueCapacity(100);
    executor.initialize();
    return executor;
}
```

### 4. void 반환의 예외 처리
```java
@Async
public void method() {
    throw new RuntimeException();  // ❌ 예외가 호출자에게 전달 안 됨!
}

// ✅ CompletableFuture 사용
@Async
public CompletableFuture<Void> method() {
    try {
        // 작업
        return CompletableFuture.completedFuture(null);
    } catch (Exception e) {
        return CompletableFuture.failedFuture(e);
    }
}
```

### 5. Future.get() 블로킹
```java
// ❌ get() 호출 시 블로킹 (비동기 의미 없음)
Future<String> future = asyncService.process();
String result = future.get();  // 여기서 대기

// ✅ CompletableFuture의 thenAccept 사용
CompletableFuture<String> future = asyncService.process();
future.thenAccept(result -> {
    // 결과 처리 (논블로킹)
});
```

### 6. 스레드 로컬 값 전파 안 됨
```java
@Async
public void method() {
    // SecurityContext, RequestContext 등이 전파 안 됨!
    Authentication auth = SecurityContextHolder.getContext().getAuthentication();
    // auth == null
}

// ✅ TaskDecorator로 전파
@Bean
public Executor taskExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setTaskDecorator(new ContextCopyingDecorator());
    return executor;
}
```

### 7. private 메서드에 @Async
```java
// ❌ private은 프록시 적용 안 됨
@Async
private void method() {
    // 비동기 실행 안 됨
}

// ✅ public만 가능
@Async
public void method() {
    // 비동기 실행
}
```

## 관련 개념
- [[이벤트-기반-아키텍처]]
- [[스케줄링]]
- [[AOP-개념과-활용]]

## 면접 질문

1. **@Async의 동작 원리는?**
   - Spring AOP 프록시가 메서드 호출을 가로채서 TaskExecutor에 위임
   - 별도 스레드에서 실행

2. **@Async를 사용할 때 주의사항은?**
   - 같은 클래스 내부 호출 불가 (프록시 거치지 않음)
   - private 메서드 불가
   - 트랜잭션 전파 안 됨

3. **Future와 CompletableFuture의 차이는?**
   - Future: get()으로 블로킹 조회만 가능
   - CompletableFuture: 콜백, 체이닝, 조합 가능 (논블로킹)

4. **ThreadPoolTaskExecutor 설정 값의 의미는?**
   - corePoolSize: 기본 스레드 수
   - maxPoolSize: 최대 스레드 수
   - queueCapacity: 대기 큐 크기

5. **@Async에서 예외가 발생하면?**
   - void 반환: 예외가 호출자에게 전달 안 됨
   - Future/CompletableFuture: get() 호출 시 ExecutionException

6. **비동기 메서드에서 트랜잭션을 사용하려면?**
   - REQUIRES_NEW로 새 트랜잭션 시작
   - 트랜잭션은 스레드에 바인딩되어 전파 안 됨

7. **언제 @Async를 사용하나요?**
   - 이메일 발송, 외부 API 호출, 파일 처리 등
   - 시간이 오래 걸리고 즉시 결과가 필요 없는 작업

## 참고 자료
- Spring Framework Reference - Task Execution and Scheduling
- Java CompletableFuture Guide
- https://docs.spring.io/spring-framework/reference/integration/scheduling.html
