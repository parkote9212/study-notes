---
tags:
  - study
  - design-pattern
  - spring-core
  - di
  - ioc
  - solid
  - 빈생명주기
created: 2026-01-23
difficulty: 상
---
# Spring-핵심개념-IoC와DI

🏷️기술 카테고리: Design Pattern, Spring Core
💡핵심키워드: #DI, #IoC, #SOLID, #빈생명주기
💼 면접 빈출도: 최상

# 1. Abstract: 핵심 요약

객체의 생명주기와 의존관계 결정 권한을 개발자가 아닌 프레임워크(컨테이너)가 가져가는 설계 원칙(IoC)과, 이를 구현하기 위해 외부에서 의존 객체를 주입해주는 기술(DI)입니다.

**핵심 가치**:
- 객체 간의 결합도를 낮춤
- SOLID 원칙 중 DIP(의존관계 역전 원칙)와 OCP(개방-폐쇄 원칙) 실현
- 유지보수성 향상

# 2. IoC (Inversion of Control)

## 2.1 제어의 주도권 변경

**과거**:
```java
// 개발자가 직접 객체 생성
MemberService service = new MemberService();
MemberRepository repository = new MemoryMemberRepository();
```

**Spring**:
```java
// 스프링 컨테이너가 객체 생성 및 관리
@Service
public class MemberService {
    // 컨테이너가 주입
    private final MemberRepository repository;
}
```

## 2.2 스프링 컨테이너

`ApplicationContext`가 빈(Bean)을 생성하고 조립하는 역할을 수행합니다.

# 3. DI (Dependency Injection)

## 3.1 의존관계 주입

실행 시점(Runtime)에 외부에서 실제 구현 객체를 연결해 주는 것입니다.

## 3.2 주입 방식

### 생성자 주입 (권장)

```java
@Service
@RequiredArgsConstructor
public class MemberService {
    private final MemberRepository repository;  // final로 불변성 보장
}
```

**장점**:
- 불변성(Immutability) 보장
- 테스트 용이성
- 순환 참조 방지

### 필드 주입 (비권장)

```java
@Autowired
private MemberRepository repository;  // final 불가
```

**단점**:
- 테스트 어려움
- 불변성 보장 안 됨

## 3.3 수동 빈 등록 vs 자동 빈 등록

| 구분 | 수동 (@Bean) | 자동 (@Component) |
| --- | --- | --- |
| **설정 위치** | @Configuration 클래스 | 각 클래스 헤더 |
| **사용 시기** | 외부 라이브러리, 기술적 설정 | 비즈니스 로직 |
| **장점** | 빈 등록 과정 명확 | 코드량 감소, 생산성 향상 |

```java
// 수동 빈 등록 (외부 라이브러리)
@Configuration
public class AppConfig {
    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper();
    }
}

// 자동 빈 등록 (비즈니스 로직)
@Service
public class MemberService {
    // ...
}
```

# 4. SOLID 원칙과의 관계

## DIP (의존관계 역전 원칙)

```java
// ❌ DIP 위반
public class MemberService {
    private MemoryMemberRepository repository = new MemoryMemberRepository();
    // 구체 클래스에 직접 의존
}

// ✅ DIP 준수
public class MemberService {
    private final MemberRepository repository;  // 인터페이스에 의존
    
    public MemberService(MemberRepository repository) {
        this.repository = repository;
    }
}
```

## OCP (개방-폐쇄 원칙)

```java
// DB 기술 변경 시 Service 코드 수정 불필요
// AppConfig에서 구현체만 변경
@Configuration
public class AppConfig {
    @Bean
    public MemberRepository memberRepository() {
        // return new MemoryMemberRepository();
        return new JpaMemberRepository();  // 변경
    }
}
```

# 5. Interview Readiness

## Q1: IoC와 DI의 관계를 한 문장으로 설명한다면?

**A**: IoC는 프로그램의 제어권이 넘어간 상태를 의미하는 추상적인 설계 원칙이며, DI는 그 원칙을 실제로 구현하기 위해 의존 객체를 주입해 주는 구체적인 기술입니다.

## Q2: 생성자 주입을 권장하는 이유는?

**A**:
1. **불변성**: final 키워드로 객체 불변성 보장
2. **테스트 용이성**: new 키워드로 순수 자바 코드 테스트 가능
3. **순환 참조 방지**: 애플리케이션 실행 시점에 순환 참조 감지
4. **필수 의존성 명시**: 생성자 파라미터로 필수 의존성이 명확해짐

## Q3: DIP(의존관계 역전 원칙)를 스프링 없이 구현할 수 있나요?

**A**: 네, 순수 자바 코드로도 인터페이스를 통해 구현할 수 있으나 스프링을 사용하면 컨테이너가 이 과정을 자동화해 주어 대규모 프로젝트에서 훨씬 안전하고 편리하게 관리할 수 있습니다.

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
