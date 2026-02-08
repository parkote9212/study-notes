---
tags:
  - study
  - spring
  - core
  - ioc
  - di
created: 2025-02-08
---

# IoC/DI 컨테이너

## 한 줄 요약
> Spring IoC 컨테이너는 객체의 생성과 의존관계 설정을 개발자 대신 관리하여, 느슨한 결합과 테스트 용이성을 제공하는 핵심 메커니즘이다.

## 상세 설명

### IoC (Inversion of Control)란?
- **제어의 역전**: 프로그램의 흐름을 개발자가 아닌 프레임워크가 제어
- 전통적 방식: 개발자가 직접 객체 생성 및 메서드 호출
- IoC 방식: 프레임워크가 객체 생명주기와 메서드 호출 시점을 결정

### DI (Dependency Injection)란?
- **의존성 주입**: 외부에서 객체의 의존관계를 설정
- 객체 간 결합도를 낮추고 유연성 향상
- 3가지 주입 방식:
  1. **생성자 주입** (권장): 불변성 보장, 순환참조 컴파일 시점 감지
  2. **세터 주입**: 선택적 의존성에 사용
  3. **필드 주입**: 테스트 어려움, 사용 비권장

### Spring IoC 컨테이너 종류
1. **BeanFactory**
   - 가장 기본적인 컨테이너
   - Lazy Loading (실제 사용 시점에 빈 생성)
   
2. **ApplicationContext** (실무 사용)
   - BeanFactory의 확장 버전
   - Eager Loading (컨테이너 시작 시 모든 빈 생성)
   - 국제화, 이벤트 발행, 리소스 로딩 등 추가 기능

### 빈(Bean) 등록 방법
1. **XML 설정** (레거시)
2. **@Component 계열 애노테이션** (컴포넌트 스캔)
3. **@Bean 메서드** (Java Config)

## 코드 예시

```java
// 1. 생성자 주입 (권장)
@Service
public class OrderService {
    private final MemberRepository memberRepository;
    private final DiscountPolicy discountPolicy;
    
    @Autowired  // 생성자가 하나면 생략 가능
    public OrderService(MemberRepository memberRepository, 
                       DiscountPolicy discountPolicy) {
        this.memberRepository = memberRepository;
        this.discountPolicy = discountPolicy;
    }
}

// 2. Java Config로 빈 등록
@Configuration
public class AppConfig {
    
    @Bean
    public MemberRepository memberRepository() {
        return new MemoryMemberRepository();
    }
    
    @Bean
    public DiscountPolicy discountPolicy() {
        return new RateDiscountPolicy();
    }
    
    @Bean
    public OrderService orderService() {
        return new OrderService(memberRepository(), discountPolicy());
    }
}

// 3. 인터페이스 기반 설계로 DI 활용
public interface DiscountPolicy {
    int discount(Member member, int price);
}

@Component
public class RateDiscountPolicy implements DiscountPolicy {
    private int discountPercent = 10;
    
    @Override
    public int discount(Member member, int price) {
        if (member.getGrade() == Grade.VIP) {
            return price * discountPercent / 100;
        }
        return 0;
    }
}

// 4. @Primary로 기본 빈 지정
@Component
@Primary  // 같은 타입의 빈이 여러개일 때 우선순위
public class RateDiscountPolicy implements DiscountPolicy { }

@Component
public class FixDiscountPolicy implements DiscountPolicy { }

// 5. @Qualifier로 특정 빈 선택
@Service
public class OrderService {
    private final DiscountPolicy discountPolicy;
    
    public OrderService(@Qualifier("rateDiscountPolicy") 
                       DiscountPolicy discountPolicy) {
        this.discountPolicy = discountPolicy;
    }
}
```

## 주의사항 / 함정

### 1. 필드 주입 지양
```java
// ❌ 나쁜 예: 필드 주입
@Service
public class OrderService {
    @Autowired
    private MemberRepository memberRepository;  // 테스트 어려움
}

// ✅ 좋은 예: 생성자 주입
@Service
public class OrderService {
    private final MemberRepository memberRepository;
    
    public OrderService(MemberRepository memberRepository) {
        this.memberRepository = memberRepository;
    }
}
```

### 2. 순환 참조 문제
- 생성자 주입 사용 시 순환 참조를 컴파일 시점에 발견 가능
- 필드/세터 주입은 런타임에 순환 참조 발생 → 늦은 발견

### 3. 같은 타입의 빈이 2개 이상일 때
- `@Primary`: 우선순위 지정
- `@Qualifier`: 명시적 빈 선택
- 구체적인 타입으로 주입 (비권장)

### 4. 빈 생명주기 콜백
- `@PostConstruct`, `@PreDestroy` 사용
- InitializingBean, DisposableBean 인터페이스 (레거시)

## 관련 개념
- [[빈-생명주기와-스코프]]
- [[컴포넌트-스캔]]
- [[AOP-개념과-활용]]

## 면접 질문

1. **IoC와 DI의 차이점은 무엇인가요?**
   - IoC는 제어의 역전이라는 큰 개념이고, DI는 IoC를 구현하는 구체적인 방법 중 하나입니다.

2. **생성자 주입을 권장하는 이유는?**
   - 불변성 보장 (final 키워드 사용 가능)
   - 순환 참조 컴파일 시점 감지
   - 테스트 코드 작성 용이 (new 키워드로 직접 생성 가능)
   - NPE 방지

3. **BeanFactory와 ApplicationContext의 차이는?**
   - BeanFactory는 Lazy Loading, ApplicationContext는 Eager Loading
   - ApplicationContext가 국제화, 이벤트, 리소스 로딩 등 추가 기능 제공
   - 실무에서는 거의 항상 ApplicationContext 사용

4. **같은 타입의 빈이 2개 이상일 때 해결 방법은?**
   - @Primary로 우선순위 지정
   - @Qualifier로 명시적 선택
   - 필드명이나 파라미터명을 빈 이름과 일치시키기

5. **@Autowired의 동작 원리는?**
   - 타입으로 먼저 조회
   - 타입이 여러 개면 필드명/파라미터명으로 매칭
   - @Qualifier, @Primary로 우선순위 조정 가능

## 참고 자료
- 김영한의 스프링 핵심 원리 - 기본편
- Spring Framework Reference Documentation - IoC Container
- https://docs.spring.io/spring-framework/reference/core/beans.html
