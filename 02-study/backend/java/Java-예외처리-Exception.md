---
tags:
  - study
  - java
  - exception
  - error-handling
created: 2026-01-31
---

# Java 예외처리 (Exception)

## 한 줄 요약
> 프로그램 실행 중 발생하는 예상 가능한 비정상 상황을 처리하여 프로그램 안정성을 확보하는 메커니즘

## 상세 설명

### 1. 예외(Exception)란?

예외는 프로그램 실행 중 발생하는 **예상 가능한 비정상적인 상황**입니다. 적절히 처리하면 프로그램을 종료하지 않고 계속 실행할 수 있습니다.

**Error vs Exception**

| 구분 | Error | Exception |
|------|-------|-----------|
| 발생 원인 | 시스템 레벨 문제 | 프로그램 로직 문제 |
| 예시 | OutOfMemoryError, StackOverflowError | IOException, NullPointerException |
| 처리 가능 여부 | ❌ 개발자가 처리 불가 | ✅ try-catch로 처리 가능 |
| 프로그램 상태 | 강제 종료 | 처리하면 계속 실행 |

### 2. 예외 계층 구조

```
Throwable
├── Error (시스템 오류)
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── ...
└── Exception (예외)
    ├── IOException (Checked)
    ├── SQLException (Checked)
    └── RuntimeException (Unchecked)
        ├── NullPointerException
        ├── IllegalArgumentException
        ├── IndexOutOfBoundsException
        └── ...
```

### 3. Checked vs Unchecked Exception

#### Checked Exception (컴파일 타임 예외)

- `Exception`을 상속하지만 `RuntimeException`은 상속하지 않음
- **컴파일러가 예외 처리를 강제**함 (try-catch 또는 throws 필수)
- 주로 **외부 요인**으로 발생 (파일, 네트워크, DB 등)
- **복구 가능성**이 있는 경우

```java
// 반드시 처리해야 함 (컴파일 에러 발생)
public void readFile(String path) throws IOException {
    FileReader reader = new FileReader(path);  // Checked Exception
}

// 또는 try-catch로 처리
public void readFileSafe(String path) {
    try {
        FileReader reader = new FileReader(path);
    } catch (IOException e) {
        System.out.println("파일을 찾을 수 없습니다: " + e.getMessage());
    }
}
```

**대표 예제**
- `IOException`: 파일 입출력 오류
- `SQLException`: DB 연결/쿼리 오류
- `ClassNotFoundException`: 클래스를 찾을 수 없음

#### Unchecked Exception (런타임 예외)

- `RuntimeException`을 상속
- 컴파일러가 예외 처리를 **강제하지 않음**
- 주로 **프로그래밍 실수**로 발생
- **예방 가능**한 경우 (유효성 검증으로 방지)

```java
// 예외 처리 강제 없음
public int divide(int a, int b) {
    return a / b;  // b가 0이면 ArithmeticException 발생
}

// 예방 코드
public int divideSafe(int a, int b) {
    if (b == 0) {
        throw new IllegalArgumentException("0으로 나눌 수 없습니다");
    }
    return a / b;
}
```

**대표 예제**
- `NullPointerException`: null 참조 접근
- `IllegalArgumentException`: 부적절한 인자 전달
- `IndexOutOfBoundsException`: 배열/리스트 범위 초과
- `ArithmeticException`: 0으로 나누기

### 4. 예외 처리 방법

#### (1) try-catch-finally

```java
public void processFile(String path) {
    FileReader reader = null;
    try {
        reader = new FileReader(path);
        // 파일 처리 로직
        
    } catch (FileNotFoundException e) {
        System.out.println("파일을 찾을 수 없습니다: " + path);
        
    } catch (IOException e) {
        System.out.println("파일 읽기 오류: " + e.getMessage());
        
    } finally {
        // 예외 발생 여부와 관계없이 항상 실행
        if (reader != null) {
            try {
                reader.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
```

#### (2) try-with-resources (Java 7+)

`AutoCloseable` 인터페이스를 구현한 리소스는 자동으로 닫힙니다.

```java
// finally 블록 없이 자동으로 close() 호출
public void processFileModern(String path) {
    try (FileReader reader = new FileReader(path);
         BufferedReader br = new BufferedReader(reader)) {
        
        String line = br.readLine();
        System.out.println(line);
        
    } catch (IOException e) {
        System.out.println("파일 처리 오류: " + e.getMessage());
    }
    // reader, br 자동으로 닫힘
}
```

#### (3) throws (예외 전가)

메서드를 호출한 쪽에서 예외를 처리하도록 위임합니다.

```java
public class UserService {
    // 예외를 Controller로 전가
    public User findUser(Long id) throws UserNotFoundException {
        User user = userRepository.findById(id);
        if (user == null) {
            throw new UserNotFoundException("사용자를 찾을 수 없습니다: " + id);
        }
        return user;
    }
}

public class UserController {
    public void handleRequest(Long id) {
        try {
            User user = userService.findUser(id);  // 여기서 처리
            System.out.println(user.getName());
        } catch (UserNotFoundException e) {
            System.out.println("에러: " + e.getMessage());
        }
    }
}
```

### 5. 커스텀 예외 생성

실무에서는 비즈니스 로직에 맞는 **커스텀 예외**를 만들어 사용합니다.

```java
// Checked Exception
public class InsufficientBalanceException extends Exception {
    private final long requestedAmount;
    private final long currentBalance;
    
    public InsufficientBalanceException(long requestedAmount, long currentBalance) {
        super(String.format("잔액 부족: 요청 금액=%d, 현재 잔액=%d", 
                            requestedAmount, currentBalance));
        this.requestedAmount = requestedAmount;
        this.currentBalance = currentBalance;
    }
    
    public long getShortage() {
        return requestedAmount - currentBalance;
    }
}

// Unchecked Exception (더 일반적)
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String message) {
        super(message);
    }
    
    public UserNotFoundException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

**실무 사용 예시**

```java
@Service
public class BankAccountService {
    
    public void withdraw(Account account, long amount) {
        if (account.getBalance() < amount) {
            throw new InsufficientBalanceException(amount, account.getBalance());
        }
        account.setBalance(account.getBalance() - amount);
    }
}

@RestController
public class BankController {
    
    @PostMapping("/withdraw")
    public ResponseEntity<?> withdraw(@RequestBody WithdrawRequest request) {
        try {
            accountService.withdraw(account, request.getAmount());
            return ResponseEntity.ok("출금 완료");
            
        } catch (InsufficientBalanceException e) {
            return ResponseEntity.badRequest()
                .body("잔액이 " + e.getShortage() + "원 부족합니다");
        }
    }
}
```

### 6. 예외 처리 베스트 프랙티스

#### ✅ 좋은 예

```java
// 1. 구체적인 예외 처리
try {
    processData();
} catch (FileNotFoundException e) {
    log.error("파일을 찾을 수 없음: {}", e.getMessage());
} catch (IOException e) {
    log.error("파일 처리 오류: {}", e.getMessage());
}

// 2. 적절한 로깅
catch (Exception e) {
    log.error("사용자 생성 실패: userId={}", userId, e);  // 스택 트레이스 포함
    throw new UserCreationException("사용자 생성 실패", e);
}

// 3. 예외 체이닝 (원인 보존)
try {
    externalApiCall();
} catch (IOException e) {
    throw new ApiException("외부 API 호출 실패", e);  // 원인 예외 전달
}
```

#### ❌ 나쁜 예

```java
// 1. 예외 무시 (절대 금지!)
try {
    riskyOperation();
} catch (Exception e) {
    // 아무것도 안 함 - 버그 추적 불가능!
}

// 2. 너무 광범위한 예외 처리
try {
    complexOperation();
} catch (Exception e) {  // 모든 예외를 잡음
    System.out.println("에러 발생");  // 어떤 에러인지 모름
}

// 3. 예외로 로직 제어 (안티패턴)
try {
    int value = Integer.parseInt(input);
} catch (NumberFormatException e) {
    value = 0;  // 예외로 기본값 설정 - 비효율적
}

// 올바른 방법
if (input.matches("\\d+")) {
    value = Integer.parseInt(input);
} else {
    value = 0;
}
```

### 7. Spring에서의 예외 처리

#### @ExceptionHandler (컨트롤러 레벨)

```java
@RestController
public class UserController {
    
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);  // UserNotFoundException 발생 가능
    }
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        ErrorResponse error = new ErrorResponse("USER_NOT_FOUND", e.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
}
```

#### @ControllerAdvice (전역 예외 처리)

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("USER_NOT_FOUND", e.getMessage()));
    }
    
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleBadRequest(IllegalArgumentException e) {
        return ResponseEntity.badRequest()
            .body(new ErrorResponse("INVALID_ARGUMENT", e.getMessage()));
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneric(Exception e) {
        log.error("Unexpected error", e);
        return ResponseEntity.internalServerError()
            .body(new ErrorResponse("INTERNAL_ERROR", "서버 오류가 발생했습니다"));
    }
}
```

## 코드 예시

### 실무 예제: 은행 계좌 이체

```java
// 커스텀 예외 정의
public class AccountException extends RuntimeException {
    public AccountException(String message) {
        super(message);
    }
}

public class InsufficientFundsException extends AccountException {
    public InsufficientFundsException(long shortage) {
        super(shortage + "원이 부족합니다");
    }
}

public class AccountNotFoundException extends AccountException {
    public AccountNotFoundException(String accountNumber) {
        super("계좌를 찾을 수 없습니다: " + accountNumber);
    }
}

// 서비스 레이어
@Service
public class TransferService {
    
    @Transactional
    public void transfer(String fromAccount, String toAccount, long amount) {
        // 1. 계좌 조회
        Account from = accountRepository.findByNumber(fromAccount)
            .orElseThrow(() -> new AccountNotFoundException(fromAccount));
        Account to = accountRepository.findByNumber(toAccount)
            .orElseThrow(() -> new AccountNotFoundException(toAccount));
        
        // 2. 잔액 확인
        if (from.getBalance() < amount) {
            throw new InsufficientFundsException(amount - from.getBalance());
        }
        
        // 3. 이체 실행
        from.withdraw(amount);
        to.deposit(amount);
        
        // 4. 이체 기록 저장
        transferHistoryRepository.save(
            new TransferHistory(from, to, amount, LocalDateTime.now())
        );
    }
}

// 컨트롤러
@RestController
@RequestMapping("/api/transfer")
public class TransferController {
    
    @Autowired
    private TransferService transferService;
    
    @PostMapping
    public ResponseEntity<?> transfer(@RequestBody TransferRequest request) {
        try {
            transferService.transfer(
                request.getFromAccount(),
                request.getToAccount(),
                request.getAmount()
            );
            return ResponseEntity.ok("이체 완료");
            
        } catch (AccountNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(Map.of("error", "ACCOUNT_NOT_FOUND", "message", e.getMessage()));
                
        } catch (InsufficientFundsException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(Map.of("error", "INSUFFICIENT_FUNDS", "message", e.getMessage()));
                
        } catch (Exception e) {
            log.error("이체 중 오류 발생", e);
            return ResponseEntity.internalServerError()
                .body(Map.of("error", "INTERNAL_ERROR", "message", "이체 처리 중 오류가 발생했습니다"));
        }
    }
}
```

## 주의사항 / 함정

### 1. 예외 삼키기 (Exception Swallowing)

```java
// ❌ 절대 금지
try {
    dangerousOperation();
} catch (Exception e) {
    // 아무것도 안 함 - 디버깅 불가능!
}

// ✅ 최소한 로깅
try {
    dangerousOperation();
} catch (Exception e) {
    log.error("작업 실패", e);
    throw e;  // 또는 적절히 처리
}
```

### 2. 과도한 try-catch

```java
// ❌ 불필요한 예외 처리
public int add(int a, int b) {
    try {
        return a + b;  // 예외가 발생할 일이 없음
    } catch (Exception e) {
        return 0;
    }
}
```

### 3. Checked Exception 남용

```java
// ❌ 복구 불가능한 상황에 Checked Exception 사용
public void process() throws ProcessException {
    if (systemDown) {
        throw new ProcessException();  // 어차피 복구 불가능
    }
}

// ✅ RuntimeException 사용
public void process() {
    if (systemDown) {
        throw new SystemUnavailableException();  // Unchecked
    }
}
```

### 4. 예외를 플로우 제어에 사용

```java
// ❌ 예외를 로직 제어에 사용 (성능 저하)
try {
    while (true) {
        array[index++];
    }
} catch (IndexOutOfBoundsException e) {
    // 배열 끝 도달
}

// ✅ 정상적인 플로우 제어
for (int i = 0; i < array.length; i++) {
    array[i];
}
```

### 5. @Transactional과 예외

```java
// ⚠️ Checked Exception은 기본적으로 롤백하지 않음!
@Transactional
public void saveUser(User user) throws UserException {  // Checked
    userRepository.save(user);
    throw new UserException();  // 트랜잭션 롤백 안 됨!
}

// ✅ 명시적 롤백 지정
@Transactional(rollbackFor = UserException.class)
public void saveUser(User user) throws UserException {
    userRepository.save(user);
    throw new UserException();  // 롤백됨
}

// ✅ 또는 RuntimeException 사용 (자동 롤백)
@Transactional
public void saveUser(User user) {
    userRepository.save(user);
    throw new UserRuntimeException();  // 자동 롤백
}
```

## 관련 개념
- [[Java-Optional]]
- [[Java-예외처리-심화]]

## 학습 로드맵 (TODO)

- Java 8+ Optional과 예외 처리 비교 문서 작성 필요
- 비동기 환경(CompletableFuture)에서의 예외 처리 문서 필요
- Reactor/WebFlux 환경에서의 예외 처리 패턴 문서 필요

## 면접 질문

1. Checked Exception과 Unchecked Exception의 차이는 무엇인가요?
2. try-with-resources의 장점은 무엇인가요?
3. Spring에서 @Transactional 사용 시 어떤 예외가 롤백을 발생시키나요?
4. 커스텀 예외를 만들 때 Checked와 Unchecked 중 어떤 것을 선택해야 하나요?
5. 예외를 처리하지 않고 무시하면 어떤 문제가 발생하나요?

## 참고 자료

- Oracle Java Documentation - Exception Handling
- Effective Java (Joshua Bloch) - Chapter 10: Exceptions
- Spring Framework Reference - Exception Handling