# [Spring]GlobalExceptionHandler 설계 가이드

🏷️기술 카테고리: Exception, Spring
💡핵심키워드: #AOP, #에러핸들링, #예외처리, #커스텀예외
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 15일 오후 11:38

전역 예외 처리를 통한 일관된 에러 응답 구조 설계

---

## 📋 개요

Spring Boot의 `@RestControllerAdvice`를 활용하여 애플리케이션 전역의 예외를 중앙에서 처리하고, 클라이언트에게 일관된 형식의 에러 응답을 제공합니다.

---

## 🎯 핵심 개념

### @RestControllerAdvice

- 모든 `@RestController`에서 발생하는 예외를 한 곳에서 처리
- `@ControllerAdvice` + `@ResponseBody`의 조합
- AOP 기반으로 동작

### 계층적 예외 처리

```
구체적 예외 (DuplicateEmailException)
    ↓
중간 예외 (IllegalArgumentException)
    ↓
일반 예외 (Exception)
```

---

## 🏗️ 기본 구조

```java
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(SpecificException.class)
    public ResponseEntity<ErrorResponse> handleSpecific(SpecificException e) {
        log.warn("Specific error: {}", e.getMessage());
        return ResponseEntity
            .status(HttpStatus.BAD_REQUEST)
            .body(new ErrorResponse("ERROR_CODE", e.getMessage()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(Exception e) {
        log.error("Unexpected error", e);
        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("SERVER_ERROR", "서버 오류"));
    }

    public record ErrorResponse(String code, String message) {}
}
```

---

## 🔑 주요 예외 처리 패턴

### 1. 비즈니스 예외

**❌ 안좋은 예 (IllegalArgumentException 남용)**

```java
@ExceptionHandler(IllegalArgumentException.class)
public ResponseEntity<ErrorResponse> handleIllegalArgument(IllegalArgumentException e) {
    // 문제: 모든 IllegalArgumentException을 동일하게 처리
    return ResponseEntity
        .status(HttpStatus.BAD_REQUEST)
        .body(new ErrorResponse("BAD_REQUEST", e.getMessage()));
}
```

**✅ 좋은 예 (커스텀 예외 사용)**

```java
// 커스텀 예외 정의
public class DuplicateEmailException extends RuntimeException {
    public DuplicateEmailException(String email) {
        super("이미 사용 중인 이메일입니다: " + email);
    }
}

public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String resource, String id) {
        super(String.format("%s를 찾을 수 없습니다. (ID: %s)", resource, id));
    }
}

// 핸들러
@ExceptionHandler(DuplicateEmailException.class)
public ResponseEntity<ErrorResponse> handleDuplicateEmail(DuplicateEmailException e) {
    log.warn("Duplicate email attempt: {}", e.getMessage());
    return ResponseEntity
        .status(HttpStatus.CONFLICT) // 409
        .body(new ErrorResponse("DUPLICATE_EMAIL", e.getMessage()));
}

@ExceptionHandler(ResourceNotFoundException.class)
public ResponseEntity<ErrorResponse> handleNotFound(ResourceNotFoundException e) {
    log.warn("Resource not found: {}", e.getMessage());
    return ResponseEntity
        .status(HttpStatus.NOT_FOUND) // 404
        .body(new ErrorResponse("NOT_FOUND", e.getMessage()));
}
```

**장점:**

- 예외 의도가 명확함
- HTTP 상태 코드를 정확하게 매핑 가능
- 예외 추적 및 모니터링 용이

---

### 2. Validation 예외 (@Valid)

```java
@ExceptionHandler(MethodArgumentNotValidException.class)
public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException ex) {
    Map<String, String> errors = new HashMap<>();
    ex.getBindingResult().getAllErrors().forEach((error) -> {
        String fieldName = ((FieldError) error).getField();
        String errorMessage = error.getDefaultMessage();
        errors.put(fieldName, errorMessage);
    });

    // 옵션 1: 첫 번째 에러만 반환 (단순한 UI)
    String firstError = errors.values().stream()
        .findFirst()
        .orElse("입력값이 올바르지 않습니다.");

    // 옵션 2: 모든 에러 반환 (상세한 피드백)
    // return new ErrorResponse("VALIDATION_ERROR", errors.toString());

    log.debug("Validation errors: {}", errors);
    return ResponseEntity
        .status(HttpStatus.BAD_REQUEST)
        .body(new ErrorResponse("VALIDATION_ERROR", firstError));
}
```

---

### 3. 인증/인가 예외

```java
// JWT 인증 실패
@ExceptionHandler({JwtException.class, AuthenticationException.class})
public ResponseEntity<ErrorResponse> handleAuth(Exception e) {
    log.warn("Authentication failed: {}", e.getMessage());
    return ResponseEntity
        .status(HttpStatus.UNAUTHORIZED) // 401
        .body(new ErrorResponse("UNAUTHORIZED", "인증에 실패했습니다."));
}

// 권한 부족
@ExceptionHandler(AccessDeniedException.class)
public ResponseEntity<ErrorResponse> handleAccessDenied(AccessDeniedException e) {
    log.warn("Access denied: {}", e.getMessage());
    return ResponseEntity
        .status(HttpStatus.FORBIDDEN) // 403
        .body(new ErrorResponse("ACCESS_DENIED", "접근 권한이 없습니다."));
}
```

---

### 4. 폴백 예외 처리

```java
@ExceptionHandler(Exception.class)
public ResponseEntity<ErrorResponse> handleException(Exception e) {
    // ⚠️ 중요: 모든 예외의 스택 트레이스를 로깅
    log.error("Unhandled exception occurred", e);
    
    // 🔒 보안: 클라이언트에는 일반적인 메시지만 노출
    String message = "서버 내부 오류가 발생했습니다.";
    
    // 개발 환경에서만 상세 메시지 (옵션)
    // if (environment.acceptsProfiles(Profiles.of("dev"))) {
    //     message = e.getMessage();
    // }
    
    return ResponseEntity
        .status(HttpStatus.INTERNAL_SERVER_ERROR)
        .body(new ErrorResponse("SERVER_ERROR", message));
}
```

---

## 📦 ErrorResponse 설계

### 기본 형태

```java
public record ErrorResponse(String code, String message) {}
```

### 확장 형태

```java
public record ErrorResponse(
    String code,
    String message,
    LocalDateTime timestamp,
    String path
) {
    public ErrorResponse(String code, String message) {
        this(code, message, [LocalDateTime.now](http://LocalDateTime.now)(), null);
    }
}

// 사용 예
{
    "code": "DUPLICATE_EMAIL",
    "message": "이미 사용 중인 이메일입니다: [test@example.com](mailto:test@example.com)",
    "timestamp": "2026-01-15T15:30:45",
    "path": "/api/v1/auth/register"
}
```

### 상세 에러 정보 포함

```java
public record ErrorResponse(
    String code,
    String message,
    LocalDateTime timestamp,
    Map<String, String> details // validation 에러 등
) {}
```

---

## 🎨 HTTP 상태 코드 가이드

| 상태 코드 | 예외 상황 | 사용 예 |
| --- | --- | --- |
| **400 Bad Request** | 잘못된 요청 | Validation 실패, 잘못된 파라미터 |
| **401 Unauthorized** | 인증 실패 | JWT 만료, 로그인 필요 |
| **403 Forbidden** | 권한 부족 | ADMIN 권한 필요, 리소스 접근 불가 |
| **404 Not Found** | 리소스 없음 | 존재하지 않는 사용자, 물건 |
| **409 Conflict** | 리소스 충돌 | 중복 이메일, 중복 예약 |
| **500 Internal Server Error** | 서버 오류 | 예상치 못한 예외, DB 연결 실패 |

---

## 🔐 보안 고려사항

### 1. 스택 트레이스 노출 방지

```java
// ❌ 위험: 클라이언트에 스택 트레이스 노출
return new ErrorResponse("ERROR", e.toString());

// ✅ 안전: 일반적인 메시지만 제공
return new ErrorResponse("SERVER_ERROR", "서버 오류가 발생했습니다.");

// 서버 로그에는 전체 스택 기록
log.error("Error occurred", e);
```

### 2. 민감 정보 필터링

```java
// ❌ 위험: DB 연결 정보 노출
return new ErrorResponse("DB_ERROR", e.getMessage());
// "Connection refused to database at 192.168.1.100:3306"

// ✅ 안전: 추상화된 메시지
return new ErrorResponse("DB_ERROR", "데이터베이스 연결에 실패했습니다.");
```

### 3. 환경별 처리

```java
@Value("${app.environment}")
private String environment;

private String getSafeMessage(Exception e) {
    if ("dev".equals(environment) || "local".equals(environment)) {
        return e.getMessage(); // 개발 환경: 상세 메시지
    }
    return "서버 오류가 발생했습니다."; // 프로덕션: 일반 메시지
}
```

---

## 📊 로깅 전략

### 로그 레벨 가이드

```java
// WARN: 예상 가능한 비즈니스 예외
log.warn("User attempted duplicate registration: {}", email);

// ERROR: 예상치 못한 시스템 예외
log.error("Unexpected database error", e);

// DEBUG: 개발 디버깅용 (프로덕션에서는 비활성화)
log.debug("Validation errors: {}", validationErrors);
```

### 구조화된 로깅

```java
log.error(
    "Exception occurred - Type: {}, Message: {}, User: {}",
    e.getClass().getSimpleName(),
    e.getMessage(),
    SecurityContextHolder.getContext().getAuthentication().getName()
);
```

---

## 🧪 테스트 예시

### 1. 예외 핸들러 단위 테스트

```java
@Test
void handleDuplicateEmail_ShouldReturn409() {
    // given
    DuplicateEmailException exception = 
        new DuplicateEmailException("[test@example.com](mailto:test@example.com)");
    
    // when
    ResponseEntity<ErrorResponse> response = 
        handler.handleDuplicateEmail(exception);
    
    // then
    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CONFLICT);
    assertThat(response.getBody().code()).isEqualTo("DUPLICATE_EMAIL");
}
```

### 2. 통합 테스트

```java
@SpringBootTest
@AutoConfigureMockMvc
class GlobalExceptionHandlerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void register_WithDuplicateEmail_ShouldReturn409() throws Exception {
        mockMvc.perform(post("/api/v1/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"email\":\"[test@example.com](mailto:test@example.com)\"}"))
            .andExpect(status().isConflict())
            .andExpect(jsonPath("$.code").value("DUPLICATE_EMAIL"));
    }
}
```

---

## ✅ Best Practices 체크리스트

- [ ]  커스텀 예외 클래스 사용 (IllegalArgumentException 남용 금지)
- [ ]  적절한 HTTP 상태 코드 매핑
- [ ]  일관된 ErrorResponse 구조
- [ ]  민감 정보 노출 방지
- [ ]  구조화된 로깅
- [ ]  환경별 에러 메시지 분기
- [ ]  Exception 폴백 핸들러 구현
- [ ]  단위 테스트 작성

---

## 📚 참고 자료

- [Spring @RestControllerAdvice 공식 문서](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/bind/annotation/RestControllerAdvice.html)
- [HTTP 상태 코드 - MDN](https://developer.mozilla.org/ko/docs/Web/HTTP/Status)
- [Spring Boot Error Handling](https://www.baeldung.com/exception-handling-for-rest-with-spring)

---

**작성일:** 2026-01-15  

**카테고리:** Spring Boot, Error Handling, REST API