---
tags:
  - study
  - spring
  - core
  - aop
  - proxy
created: 2025-02-08
---

# AOP 개념과 활용

## 한 줄 요약
> AOP(Aspect Oriented Programming)는 횡단 관심사를 모듈화하여 핵심 비즈니스 로직과 분리함으로써 코드 중복을 제거하고 유지보수성을 향상시키는 프로그래밍 기법이다.

## 상세 설명

### AOP란?
- **관점 지향 프로그래밍**: 여러 클래스에 걸쳐 나타나는 공통 관심사를 분리
- **핵심 관심사(Core Concerns)**: 비즈니스 로직
- **횡단 관심사(Cross-cutting Concerns)**: 로깅, 트랜잭션, 보안, 캐싱 등

### 왜 AOP를 사용하는가?
```java
// AOP 적용 전
public class UserService {
    public void createUser(User user) {
        long start = System.currentTimeMillis();  // 로깅
        log.info("createUser 시작");              // 로깅
        
        try {
            // 핵심 비즈니스 로직
            userRepository.save(user);
            
            long end = System.currentTimeMillis();  // 로깅
            log.info("createUser 종료: " + (end - start) + "ms");
        } catch (Exception e) {
            log.error("에러 발생", e);              // 로깅
            throw e;
        }
    }
}
```
→ 모든 메서드에 로깅 코드가 중복!

### AOP 핵심 용어

1. **Aspect (관점)**
   - 횡단 관심사의 모듈
   - 어드바이스 + 포인트컷

2. **Join Point (조인 포인트)**
   - 어드바이스가 적용될 수 있는 위치
   - 메서드 실행, 생성자 호출, 필드 값 접근 등
   - Spring AOP는 **메서드 실행**만 지원

3. **Pointcut (포인트컷)**
   - 조인 포인트 중 실제로 어드바이스를 적용할 위치를 선별
   - 표현식으로 지정

4. **Advice (어드바이스)**
   - 실제 부가 기능 로직
   - 종류: @Before, @AfterReturning, @AfterThrowing, @After, @Around

5. **Target (타겟)**
   - 어드바이스를 받는 대상 객체

6. **Weaving (위빙)**
   - Aspect를 타겟 객체에 적용하는 과정
   - 컴파일 시점, 클래스 로딩 시점, 런타임 시점

### Spring AOP 특징
- **프록시 기반**: 런타임에 프록시 객체 생성
- **메서드 실행 지점만 지원**
- **스프링 빈에만 적용 가능**
- JDK Dynamic Proxy 또는 CGLIB 사용

### 어드바이스 종류

| 어드바이스 | 설명 | 사용 시기 |
|-----------|------|-----------|
| **@Before** | 메서드 실행 전 | 파라미터 검증, 로깅 |
| **@AfterReturning** | 정상 종료 후 | 결과값 변환, 로깅 |
| **@AfterThrowing** | 예외 발생 시 | 예외 로깅, 알림 |
| **@After** | 메서드 종료 후 (finally) | 리소스 정리 |
| **@Around** | 메서드 실행 전후 제어 | 트랜잭션, 성능 측정 |

## 코드 예시

```java
// 1. 기본 AOP 설정
@Aspect
@Component
@Slf4j
public class LoggingAspect {
    
    // 포인트컷 정의
    @Pointcut("execution(* com.example.service..*(..))")
    private void allService() {}
    
    @Pointcut("execution(* com.example.controller..*(..))")
    private void allController() {}
    
    // Before 어드바이스
    @Before("allService()")
    public void logBefore(JoinPoint joinPoint) {
        log.info("메서드 실행: {}", joinPoint.getSignature());
    }
    
    // AfterReturning 어드바이스
    @AfterReturning(pointcut = "allService()", returning = "result")
    public void logAfterReturning(JoinPoint joinPoint, Object result) {
        log.info("메서드 완료: {}, 반환값: {}", 
                 joinPoint.getSignature(), result);
    }
    
    // AfterThrowing 어드바이스
    @AfterThrowing(pointcut = "allService()", throwing = "ex")
    public void logAfterThrowing(JoinPoint joinPoint, Exception ex) {
        log.error("예외 발생: {}, 예외: {}", 
                  joinPoint.getSignature(), ex.getMessage());
    }
}

// 2. Around 어드바이스 (가장 강력)
@Aspect
@Component
@Slf4j
public class PerformanceAspect {
    
    @Around("execution(* com.example.service..*(..))")
    public Object measureExecutionTime(ProceedingJoinPoint joinPoint) 
            throws Throwable {
        long start = System.currentTimeMillis();
        
        try {
            // 실제 메서드 실행
            Object result = joinPoint.proceed();
            return result;
        } finally {
            long end = System.currentTimeMillis();
            log.info("{} 실행 시간: {}ms", 
                     joinPoint.getSignature(), (end - start));
        }
    }
}

// 3. 파라미터 접근
@Aspect
@Component
@Slf4j
public class ParameterLoggingAspect {
    
    @Before("execution(* com.example.service..create*(..)) && args(entity,..)")
    public void logCreate(JoinPoint joinPoint, Object entity) {
        log.info("생성 요청: {}", entity);
    }
}

// 4. 커스텀 애노테이션 기반 AOP
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface TrackTime {
}

@Aspect
@Component
@Slf4j
public class TrackTimeAspect {
    
    @Around("@annotation(TrackTime)")
    public Object trackTime(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = joinPoint.proceed();
        long end = System.currentTimeMillis();
        
        log.info("{} 실행 시간: {}ms", 
                 joinPoint.getSignature().getName(), (end - start));
        return result;
    }
}

// 사용
@Service
public class UserService {
    
    @TrackTime
    public void createUser(User user) {
        // 비즈니스 로직
    }
}

// 5. 트랜잭션 AOP 예시
@Aspect
@Component
public class TransactionAspect {
    
    private final PlatformTransactionManager transactionManager;
    
    @Around("@annotation(Transactional)")
    public Object executeInTransaction(ProceedingJoinPoint joinPoint) 
            throws Throwable {
        TransactionStatus status = 
            transactionManager.getTransaction(new DefaultTransactionDefinition());
        
        try {
            Object result = joinPoint.proceed();
            transactionManager.commit(status);
            return result;
        } catch (Exception e) {
            transactionManager.rollback(status);
            throw e;
        }
    }
}

// 6. 포인트컷 표현식 예시
@Aspect
@Component
public class PointcutExamples {
    
    // 특정 패키지의 모든 메서드
    @Pointcut("execution(* com.example.service..*(..))")
    private void serviceLayer() {}
    
    // 특정 애노테이션이 붙은 메서드
    @Pointcut("@annotation(org.springframework.transaction.annotation.Transactional)")
    private void transactionalMethod() {}
    
    // 반환 타입이 특정 타입인 메서드
    @Pointcut("execution(com.example.dto.UserDto com.example..*(..))")
    private void returnsUserDto() {}
    
    // 파라미터가 특정 타입인 메서드
    @Pointcut("execution(* *(.., String))")
    private void lastParamIsString() {}
    
    // 조합 사용
    @Before("serviceLayer() && transactionalMethod()")
    public void beforeServiceTransaction() {
        // ...
    }
}
```

## 주의사항 / 함정

### 1. 프록시 방식의 한계
```java
@Service
public class UserService {
    
    public void outerMethod() {
        this.innerMethod();  // ❌ AOP가 적용되지 않음!
    }
    
    @TrackTime
    public void innerMethod() {
        // ...
    }
}
```
- 같은 클래스 내부 메서드 호출은 프록시를 거치지 않음
- 해결: 클래스 분리 또는 self-injection

### 2. Around 어드바이스의 proceed() 호출
```java
@Around("execution(* com.example..*(..))")
public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
    // ❌ proceed()를 호출하지 않으면 원본 메서드가 실행되지 않음!
    log.info("Before");
    return null;  // 항상 null 반환
}

// ✅ 올바른 사용
@Around("execution(* com.example..*(..))")
public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
    log.info("Before");
    Object result = joinPoint.proceed();  // 반드시 호출!
    log.info("After");
    return result;  // 반드시 반환!
}
```

### 3. 포인트컷 표현식 성능
```java
// ❌ 느림: 모든 패키지를 검사
@Pointcut("execution(* *(..))")

// ✅ 빠름: 특정 패키지만 검사
@Pointcut("execution(* com.example.service..*(..))")
```

### 4. 어드바이스 실행 순서
- 여러 Aspect가 같은 조인 포인트에 적용될 때 순서 불확실
- `@Order(1)` 애노테이션으로 순서 지정 (숫자가 작을수록 먼저 실행)

### 5. 예외 처리 주의
```java
@Around("execution(* com.example..*(..))")
public Object around(ProceedingJoinPoint joinPoint) {
    try {
        return joinPoint.proceed();  // ❌ throws Throwable 처리 안 함
    } catch (Exception e) {
        // 예외 처리
    }
}

// ✅ 올바른 예외 처리
@Around("execution(* com.example..*(..))")
public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
    return joinPoint.proceed();
}
```

## 관련 개념
- [[IoC-DI-컨테이너]]
- [[트랜잭션-관리]]
- [[예외처리-전략]]

## 면접 질문

1. **AOP란 무엇이고 왜 사용하나요?**
   - 관점 지향 프로그래밍으로, 횡단 관심사(로깅, 트랜잭션, 보안)를 핵심 로직과 분리
   - 코드 중복 제거, 유지보수성 향상, 비즈니스 로직에 집중 가능

2. **Spring AOP와 AspectJ의 차이는?**
   - Spring AOP: 프록시 기반, 런타임 위빙, 메서드 실행만 지원, 스프링 빈만 가능
   - AspectJ: 바이트코드 조작, 컴파일/로딩 시점 위빙, 필드 접근 등 모든 조인 포인트 지원

3. **@Around 어드바이스와 다른 어드바이스의 차이는?**
   - @Around는 메서드 실행 전후를 완전히 제어 가능 (proceed() 호출 여부 결정)
   - 다른 어드바이스는 특정 시점에만 실행되고 메서드 흐름 제어 불가

4. **프록시 기반 AOP의 한계는?**
   - 같은 클래스 내부 메서드 호출 시 AOP 미적용
   - final 클래스/메서드에 적용 불가
   - private 메서드에 적용 불가

5. **포인트컷 표현식에서 execution과 @annotation의 차이는?**
   - execution: 메서드 시그니처(패키지, 클래스, 메서드명)로 선별
   - @annotation: 특정 애노테이션이 붙은 메서드만 선별

6. **JoinPoint와 ProceedingJoinPoint의 차이는?**
   - JoinPoint: 현재 실행 중인 메서드 정보 조회만 가능
   - ProceedingJoinPoint: proceed() 메서드로 타겟 메서드 실행 제어 가능 (@Around에서만 사용)

## 참고 자료
- 김영한의 스프링 핵심 원리 - 고급편
- Spring Framework Reference - AOP
- https://docs.spring.io/spring-framework/reference/core/aop.html
