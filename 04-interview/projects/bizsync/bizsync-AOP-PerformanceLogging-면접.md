---
tags:
  - interview
  - aop
  - annotation
  - performance
  - bizsync
  - project
created: 2025-02-05
difficulty: 중상
---

# BizSync - AOP 커스텀 어노테이션으로 성능 로깅

## 질문
> AOP를 활용한 커스텀 어노테이션 구현 경험을 설명해주세요.

## 핵심 답변 (3줄)
1. **문제**: 배치 작업 및 서비스 메서드의 성능 측정이 필요했으나, 코드 중복과 비즈니스 로직 오염 우려
2. **해결**: `@PerformanceLogging` 커스텀 어노테이션 + AOP Aspect로 횡단 관심사 분리
3. **결과**: 메서드 시작/종료 시간 자동 로깅, 실행 시간 측정, 에러 발생 시에도 로깅

## 상세 설명

### 배경
Spring Batch의 Writer나 시간이 오래 걸리는 서비스 메서드의 성능을 모니터링하기 위해 실행 시간을 측정해야 했습니다. 하지만 매번 `System.currentTimeMillis()`를 호출하면 코드가 지저분해집니다.

### 해결 방법: AOP + 커스텀 어노테이션

**1단계: 어노테이션 정의**
```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface PerformanceLogging {
}
```

**2단계: Aspect 구현**
```java
@Slf4j
@Aspect
@Component
public class PerformanceLoggingAspect {

    @Around("@annotation(PerformanceLogging)")
    public Object logExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = joinPoint.getSignature().getName();
        String fullMethodName = className + "." + methodName;

        log.info("[시작] {}", fullMethodName);
        long startTime = System.currentTimeMillis();
        
        try {
            Object result = joinPoint.proceed();
            long executionTime = System.currentTimeMillis() - startTime;
            log.info("[완료] {} - 소요 시간: {}ms", fullMethodName, executionTime);
            return result;
        } catch (Exception e) {
            long executionTime = System.currentTimeMillis() - startTime;
            log.error("[실패] {} - 소요 시간: {}ms, 에러: {}", 
                     fullMethodName, executionTime, e.getMessage());
            throw e;
        }
    }
}
```

**3단계: 적용**
```java
@Bean
@PerformanceLogging  // 어노테이션 하나로 성능 로깅 활성화
public ItemWriter<Project> projectArchiveWriter() {
    return chunk -> {
        for (Project project : chunk) {
            project.archive();
            projectRepository.save(project);
        }
    };
}
```

### AOP의 장점
✅ **관심사의 분리**: 비즈니스 로직과 로깅 로직 분리
✅ **코드 재사용**: 어노테이션 하나로 여러 메서드에 적용
✅ **유지보수성**: 로깅 정책 변경 시 Aspect만 수정
✅ **가독성**: 핵심 로직에 집중 가능

### 주의사항
- `@Aspect`는 `@Component`로 등록해야 Spring Bean으로 관리됨
- `@Around`는 메서드 실행 전후를 모두 제어 가능 (다른 어드바이스: `@Before`, `@After`, `@AfterReturning`, `@AfterThrowing`)
- `ProceedingJoinPoint.proceed()`로 실제 메서드 실행
- Private 메서드에는 AOP 적용 불가 (프록시 기반)

## 코드 예시
```java
// 커스텀 어노테이션 정의
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface PerformanceLogging {
}

// Aspect 구현
@Slf4j
@Aspect
@Component
public class PerformanceLoggingAspect {

    @Around("@annotation(com.bizsync.backend.global.common.aop.PerformanceLogging)")
    public Object logExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        String fullMethodName = joinPoint.getTarget().getClass().getSimpleName() 
                               + "." + joinPoint.getSignature().getName();

        log.info("[시작] {}", fullMethodName);
        long startTime = System.currentTimeMillis();
        
        try {
            Object result = joinPoint.proceed();
            log.info("[완료] {} - 소요 시간: {}ms", 
                    fullMethodName, System.currentTimeMillis() - startTime);
            return result;
        } catch (Exception e) {
            log.error("[실패] {} - 소요 시간: {}ms, 에러: {}", 
                     fullMethodName, System.currentTimeMillis() - startTime, e.getMessage());
            throw e;
        }
    }
}

// 사용 예시
@Service
public class ExcelService {
    
    @PerformanceLogging  // 어노테이션만 추가
    public int uploadTasksFromExcel(Long projectId, MultipartFile file) throws IOException {
        // 비즈니스 로직만 집중
        // ...
    }
}
```

## 꼬리 질문 예상
- `@Around` 외에 다른 어드바이스는?
  → `@Before`, `@After`, `@AfterReturning`, `@AfterThrowing` 등
- AOP는 어떻게 동작하나?
  → 스프링은 프록시 패턴으로 AOP 구현 (JDK Dynamic Proxy 또는 CGLIB)
- 트랜잭션도 AOP로 구현되나?
  → 네, `@Transactional`도 AOP 기반 (`TransactionInterceptor`)

## 참고
- [[bizsync-SpringBatch-VirtualThread-면접]]
- Spring AOP 공식 문서
