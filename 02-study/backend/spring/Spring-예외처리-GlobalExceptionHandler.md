---
tags:
  - study
  - exception
  - spring
  - aop
  - 에러핸들링
  - 예외처리
  - 커스텀예외
created: 2026-01-23
difficulty: 상
---
# Spring-예외처리-GlobalExceptionHandler

🏷️기술 카테고리: Exception, Spring
💡핵심키워드: #AOP, #에러핸들링, #예외처리, #커스텀예외
💼 면접 빈출도: 상

# 1. Abstract: 핵심 요약

Spring Boot의 `@RestControllerAdvice`를 활용하여 애플리케이션 전역의 예외를 중앙에서 처리하고, 클라이언트에게 일관된 형식의 에러 응답을 제공합니다.

**핵심 가치**:
- 일관된 에러 응답 구조
- 중복 코드 제거
- 보안 강화 (민감 정보 노출 방지)

# 2. 기본 구조

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

# 3. 주요 예외 처리 패턴

## 3.1 커스텀 예외 사용 (권장)

```java
// ❌ 안좋은 예: IllegalArgumentException 남용
@ExceptionHandler(IllegalArgumentException.class)
public ResponseEntity<ErrorResponse> handleIllegalArgument(Exception e) {
    // 모든 IllegalArgumentException을 동일하게 처리
    return ResponseEntity.badRequest()
        .body(new ErrorResponse("BAD_REQUEST", e.getMessage()));
}

// ✅ 좋은 예: 커스텀 예외 사용
public class DuplicateEmailException extends RuntimeException {
    public DuplicateEmailException(String email) {
        super("이미 사용 중인 이메일입니다: " + email);
    }
}

@ExceptionHandler(DuplicateEmailException.class)
public ResponseEntity<ErrorResponse> handleDuplicateEmail(DuplicateEmailException e) {
    log.warn("Duplicate email: {}", e.getMessage());
    return ResponseEntity
        .status(HttpStatus.CONFLICT)  // 409
        .body(new ErrorResponse("DUPLICATE_EMAIL", e.getMessage()));
}
```

## 3.2 Validation 예외

```java
@ExceptionHandler(MethodArgumentNotValidException.class)
public ResponseEntity<ErrorResponse> handleValidation(
    MethodArgumentNotValidException ex) {
    
    Map<String, String> errors = new HashMap<>();
    ex.getBindingResult().getAllErrors().forEach((error) -> {
        String fieldName = ((FieldError) error).getField();
        String errorMessage = error.getDefaultMessage();
        errors.put(fieldName, errorMessage);
    });

    // 첫 번째 에러만 반환
    String firstError = errors.values().stream()
        .findFirst()
        .orElse("입력값이 올바르지 않습니다.");

    return ResponseEntity
        .status(HttpStatus.BAD_REQUEST)
        .body(new ErrorResponse("VALIDATION_ERROR", firstError));
}
```

## 3.3 인증/인가 예외

```java
// JWT 인증 실패
@ExceptionHandler({JwtException.class, AuthenticationException.class})
public ResponseEntity<ErrorResponse> handleAuth(Exception e) {
    log.warn("Authentication failed: {}", e.getMessage());
    return ResponseEntity
        .status(HttpStatus.UNAUTHORIZED)  // 401
        .body(new ErrorResponse("UNAUTHORIZED", "인증에 실패했습니다."));
}

// 권한 부족
@ExceptionHandler(AccessDeniedException.class)
public ResponseEntity<ErrorResponse> handleAccessDenied(AccessDeniedException e) {
    log.warn("Access denied: {}", e.getMessage());
    return ResponseEntity
        .status(HttpStatus.FORBIDDEN)  // 403
        .body(new ErrorResponse("ACCESS_DENIED", "접근 권한이 없습니다."));
}
```

## 3.4 폴백 예외 처리

```java
@ExceptionHandler(Exception.class)
public ResponseEntity<ErrorResponse> handleException(Exception e) {
    // 모든 예외의 스택 트레이스를 로깅
    log.error("Unhandled exception occurred", e);
    
    // 클라이언트에는 일반적인 메시지만 노출 (보안)
    return ResponseEntity
        .status(HttpStatus.INTERNAL_SERVER_ERROR)
        .body(new ErrorResponse("SERVER_ERROR", "서버 내부 오류가 발생했습니다."));
}
```

# 4. ErrorResponse 설계

## 4.1 기본 형태

```java
public record ErrorResponse(String code, String message) {}
```

## 4.2 확장 형태

```java
public record ErrorResponse(
    String code,
    String message,
    LocalDateTime timestamp,
    String path
) {
    public ErrorResponse(String code, String message) {
        this(code, message, LocalDateTime.now(), null);
    }
}

// 응답 예시
{
    "code": "DUPLICATE_EMAIL",
    "message": "이미 사용 중인 이메일입니다",
    "timestamp": "2026-01-23T15:30:45",
    "path": "/api/v1/auth/register"
}
```

# 5. HTTP 상태 코드 가이드

| 상태 코드 | 예외 상황 | 사용 예 |
| --- | --- | --- |
| 400 Bad Request | 잘못된 요청 | Validation 실패 |
| 401 Unauthorized | 인증 실패 | JWT 만료, 로그인 필요 |
| 403 Forbidden | 권한 부족 | ADMIN 권한 필요 |
| 404 Not Found | 리소스 없음 | 존재하지 않는 사용자 |
| 409 Conflict | 리소스 충돌 | 중복 이메일, 중복 예약 |
| 500 Internal Server Error | 서버 오류 | 예상치 못한 예외 |

# 6. 보안 고려사항

## 6.1 스택 트레이스 노출 방지

```java
// ❌ 위험: 스택 트레이스 노출
return new ErrorResponse("ERROR", e.toString());

// ✅ 안전: 일반적인 메시지만 제공
return new ErrorResponse("SERVER_ERROR", "서버 오류가 발생했습니다.");

// 서버 로그에는 전체 스택 기록
log.error("Error occurred", e);
```

## 6.2 환경별 처리

```java
@Value("${app.environment}")
private String environment;

private String getSafeMessage(Exception e) {
    if ("dev".equals(environment) || "local".equals(environment)) {
        return e.getMessage();  // 개발: 상세 메시지
    }
    return "서버 오류가 발생했습니다.";  // 프로덕션: 일반 메시지
}
```

# 7. 로깅 전략

```java
// WARN: 예상 가능한 비즈니스 예외
log.warn("User attempted duplicate registration: {}", email);

// ERROR: 예상치 못한 시스템 예외
log.error("Unexpected database error", e);

// DEBUG: 개발 디버깅용
log.debug("Validation errors: {}", validationErrors);
```

# 8. Best Practices 체크리스트

- [ ]  커스텀 예외 클래스 사용 (IllegalArgumentException 남용 금지)
- [ ]  적절한 HTTP 상태 코드 매핑
- [ ]  일관된 ErrorResponse 구조
- [ ]  민감 정보 노출 방지
- [ ]  구조화된 로깅
- [ ]  환경별 에러 메시지 분기
- [ ]  Exception 폴백 핸들러 구현
- [ ]  단위 테스트 작성

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐ (상)
