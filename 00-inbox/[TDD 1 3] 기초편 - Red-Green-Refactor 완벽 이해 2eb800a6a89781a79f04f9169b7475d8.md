# [TDD 1/3] 기초편 - Red-Green-Refactor 완벽 이해

🏷️기술 카테고리: Java, Testing
💡핵심키워드: #Given-When-Then, #TDD, #테스트
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 17일 오후 5:54
📅 다음 복습일: 2026년 1월 25일

# 1. Abstract: 핵심 요약

> **TDD(Test-Driven Development)**는 테스트를 먼저 작성하고 코드를 나중에 작성하는 개발 방법론입니다. Red-Green-Refactor 사이클을 반복하여 버그를 줄이고, 유지보수성을 높이며, 자신감 있는 리팩토링을 가능하게 합니다.
> 

**핵심 원칙**:

- 🔴 Red: 실패하는 테스트를 먼저 작성
- 🟢 Green: 테스트를 통과하는 최소한의 코드 작성
- 🔵 Refactor: 코드 개선 (테스트는 통과 유지)
- 작은 단위로 반복 (5~10분 사이클)

---

# 2. TDD란 무엇인가?

## 2.1 전통적 개발 vs TDD

### 전통적 개발 방식

```
1. 요구사항 분석
    ↓
2. 설계
    ↓
3. 코드 작성
    ↓
4. 테스트 작성 (선택적)
    ↓
5. 디버깅
```

**문제점**:

- ❌ 테스트가 나중 → 안 쓰게 됨
- ❌ 버그를 나중에 발견 → 수정 비용 증가
- ❌ 리팩토링 두려움 → 레거시 코드 양산
- ❌ 과도한 설계 → 불필요한 복잡도

---

### TDD 개발 방식

```
1. 테스트 작성 (Red)
    ↓
2. 최소 코드 작성 (Green)
    ↓
3. 리팩토링 (Refactor)
    ↓
4. 반복
```

**장점**:

- ✅ 자동 회귀 테스트 확보
- ✅ 버그를 즉시 발견
- ✅ 안전한 리팩토링
- ✅ 심플한 설계 (YAGNI)
- ✅ 문서화 효과

---

## 2.2 TDD의 정의

**Kent Beck의 정의**:

> "테스트가 개발을 주도한다 (Test drives the development)"
> 

**핵심 규칙** (Kent Beck):

1. 실패하는 테스트를 작성하기 전에는 프로덕션 코드를 작성하지 않는다
2. 실패하는 테스트를 컴파일 단계에서 포함하여 딱 하나만 작성한다
3. 현재 실패하는 테스트를 통과시키기에 충분한 정도의 프로덕션 코드만 작성한다

---

# 3. Red-Green-Refactor 사이클

## 3.1 사이클 상세 설명

```
🔴 RED
  ↓
실패하는 테스트 작성
  ↓
🟢 GREEN
  ↓
테스트 통과하는 코드 작성
  ↓
🔵 REFACTOR
  ↓
코드 개선 (테스트 유지)
  ↓
(반복)
```

---

### 🔴 Red Phase (실패 단계)

**목표**: 실패하는 테스트 작성

```java
// 1단계: RED - 실패하는 테스트 작성
@Test
@DisplayName("두 수를 더하면 합을 반환해야 한다")
void add_TwoNumbers_ReturnsSum() {
    // given
    Calculator calculator = new Calculator();
    
    // when
    int result = calculator.add(2, 3);
    
    // then
    assertThat(result).isEqualTo(5);
}

// 컴파일 에러 발생!
// Calculator 클래스가 없음
// add 메서드가 없음
```

**중요 포인트**:

- 아직 구현이 없으므로 컴파일 에러 또는 테스트 실패
- 테스트가 정말 실패하는지 확인 (False Positive 방지)
- 한 번에 하나의 테스트만 작성

---

### 🟢 Green Phase (통과 단계)

**목표**: 테스트를 통과하는 최소한의 코드 작성

```java
// 2단계: GREEN - 최소한의 코드로 테스트 통과
public class Calculator {
    public int add(int a, int b) {
        return a + b;  // 가장 간단한 구현
    }
}

// ✅ 테스트 통과!
```

**중요 포인트**:

- "최소한"이 핵심 → 복잡한 로직 금지
- 일단 통과시키는 것이 목표
- 하드코딩도 OK (나중에 리팩토링)

**Fake It (가짜로 구현하기)**:

```java
// 극단적 예시: 하드코딩으로 일단 통과
public int add(int a, int b) {
    return 5;  // 테스트 케이스가 2+3만 있다면 이것도 통과
}

// → 추가 테스트 작성 → 일반화 유도
```

---

### 🔵 Refactor Phase (개선 단계)

**목표**: 코드 품질 개선 (테스트는 계속 통과)

```java
// 3단계: REFACTOR - 코드 개선
public class Calculator {
    
    // 예시 1: 메서드 추출
    public int add(int a, int b) {
        return sum(a, b);
    }
    
    private int sum(int a, int b) {
        return a + b;
    }
    
    // 예시 2: 변수명 개선
    public int multiply(int multiplier, int multiplicand) {
        return multiplier * multiplicand;
    }
}

// ✅ 테스트는 여전히 통과!
```

**리팩토링 항목**:

- 중복 코드 제거
- 변수/메서드명 개선
- 복잡한 조건문 단순화
- 긴 메서드 분리
- 매직 넘버 상수화

**중요**: 리팩토링 중에도 테스트는 항상 통과해야 함!

---

## 3.2 실전 예제: 로그인 기능 TDD

### Step 1: 🔴 RED - 테스트 작성

```java
@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @InjectMocks
    private AuthService authService;

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtProvider jwtProvider;

    @Test
    @DisplayName("로그인 성공 시 토큰을 반환해야 한다")
    void login_Success() {
        // given
        LoginRequestDTO request = new LoginRequestDTO(
            "[test@bizsync.com](mailto:test@bizsync.com)", 
            "1234"
        );

        User testUser = User.builder()
                .userId(1L)
                .email("[test@bizsync.com](mailto:test@bizsync.com)")
                .password("encoded_1234")
                .role(Role.MEMBER)
                .build();

        given(userRepository.findByEmail([request.email](http://request.email)()))
            .willReturn(Optional.of(testUser));
        given(passwordEncoder.matches(request.password(), testUser.getPassword()))
            .willReturn(true);
        given(jwtProvider.createToken(any(), any()))
            .willReturn("access_token_sample");
        given(jwtProvider.createRefreshToken(any()))
            .willReturn("refresh_token_sample");

        // when
        JwtTokenResponse token = authService.login(request);

        // then
        assertThat(token).isNotNull();
        assertThat(token.getAccessToken()).isEqualTo("access_token_sample");
        assertThat(token.getRefreshToken()).isEqualTo("refresh_token_sample");
    }
}

// ❌ 컴파일 에러: AuthService.login() 메서드가 없음
```

---

### Step 2: 🟢 GREEN - 최소 구현

```java
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtProvider jwtProvider;

    public JwtTokenResponse login(LoginRequestDTO request) {
        // 1. 사용자 조회
        User user = userRepository.findByEmail([request.email](http://request.email)())
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));

        // 2. 비밀번호 검증
        if (!passwordEncoder.matches(request.password(), user.getPassword())) {
            throw new IllegalArgumentException("비밀번호가 일치하지 않습니다.");
        }

        // 3. 토큰 생성
        String accessToken = jwtProvider.createToken(user.getUserId(), user.getRole());
        String refreshToken = jwtProvider.createRefreshToken(user.getUserId());

        // 4. 응답 반환
        return new JwtTokenResponse(accessToken, refreshToken);
    }
}

// ✅ 테스트 통과!
```

---

### Step 3: 추가 테스트 (예외 케이스)

```java
@Test
@DisplayName("비밀번호가 틀리면 예외가 발생해야 한다")
void login_WrongPassword_ThrowsException() {
    // given
    LoginRequestDTO request = new LoginRequestDTO(
        "[test@bizsync.com](mailto:test@bizsync.com)", 
        "wrong_password"
    );
    
    User testUser = User.builder()
            .email("[test@bizsync.com](mailto:test@bizsync.com)")
            .password("encoded_1234")
            .build();

    given(userRepository.findByEmail([request.email](http://request.email)()))
        .willReturn(Optional.of(testUser));
    given(passwordEncoder.matches(request.password(), testUser.getPassword()))
        .willReturn(false);

    // when & then
    assertThatThrownBy(() -> authService.login(request))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessage("비밀번호가 일치하지 않습니다.");
}

@Test
@DisplayName("존재하지 않는 사용자면 예외가 발생해야 한다")
void login_UserNotFound_ThrowsException() {
    // given
    LoginRequestDTO request = new LoginRequestDTO(
        "[nonexistent@bizsync.com](mailto:nonexistent@bizsync.com)", 
        "1234"
    );

    given(userRepository.findByEmail([request.email](http://request.email)()))
        .willReturn(Optional.empty());

    // when & then
    assertThatThrownBy(() -> authService.login(request))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessage("사용자를 찾을 수 없습니다.");
}
```

---

### Step 4: 🔵 REFACTOR - 개선

```java
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtProvider jwtProvider;

    public JwtTokenResponse login(LoginRequestDTO request) {
        User user = findUserByEmail([request.email](http://request.email)());
        validatePassword(request.password(), user.getPassword());
        return generateTokens(user);
    }

    // 메서드 추출로 가독성 개선
    private User findUserByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));
    }

    private void validatePassword(String rawPassword, String encodedPassword) {
        if (!passwordEncoder.matches(rawPassword, encodedPassword)) {
            throw new IllegalArgumentException("비밀번호가 일치하지 않습니다.");
        }
    }

    private JwtTokenResponse generateTokens(User user) {
        String accessToken = jwtProvider.createToken(user.getUserId(), user.getRole());
        String refreshToken = jwtProvider.createRefreshToken(user.getUserId());
        return new JwtTokenResponse(accessToken, refreshToken);
    }
}

// ✅ 모든 테스트 여전히 통과!
// ✅ 코드 가독성 향상
// ✅ 각 메서드의 책임이 명확함
```

---

# 4. TDD의 3가지 법칙 (Uncle Bob)

**Robert C. Martin(Uncle Bob)의 TDD 법칙**:

## 법칙 1: 실패하는 단위 테스트를 작성하기 전에는 프로덕션 코드를 작성하지 않는다

```java
// ❌ 잘못된 방식
public class Calculator {
    public int add(int a, int b) {  // 테스트 없이 작성
        return a + b;
    }
}

// ✅ 올바른 방식
@Test
void add_test() {  // 테스트 먼저!
    Calculator calc = new Calculator();
    assertThat(calc.add(2, 3)).isEqualTo(5);
}
// → 이제 Calculator 구현
```

---

## 법칙 2: 컴파일 실패를 포함해서 실패하는 단위 테스트를 하나 이상 작성하지 않는다

```java
// ❌ 한 번에 여러 테스트
@Test
void calculator_test() {
    Calculator calc = new Calculator();
    assertThat(calc.add(2, 3)).isEqualTo(5);        // 1
    assertThat(calc.subtract(5, 2)).isEqualTo(3);   // 2
    assertThat(calc.multiply(2, 3)).isEqualTo(6);   // 3
}

// ✅ 하나씩
@Test
void add_test() {
    Calculator calc = new Calculator();
    assertThat(calc.add(2, 3)).isEqualTo(5);
}
// 통과 후 다음

@Test
void subtract_test() {
    Calculator calc = new Calculator();
    assertThat(calc.subtract(5, 2)).isEqualTo(3);
}
```

---

## 법칙 3: 현재 실패하는 테스트를 통과시키기에 충분한 정도를 넘어서는 프로덕션 코드를 작성하지 않는다

```java
// 테스트
@Test
void add_test() {
    assertThat(new Calculator().add(2, 3)).isEqualTo(5);
}

// ❌ 과도한 구현
public class Calculator {
    private List<Integer> history = new ArrayList<>();  // 불필요
    
    public int add(int a, int b) {
        int result = a + b;
        history.add(result);  // 요구사항 없음
        return result;
    }
}

// ✅ 최소 구현
public class Calculator {
    public int add(int a, int b) {
        return a + b;  // 딱 필요한 만큼만
    }
}
```

---

# 5. TDD의 장단점

## 5.1 장점

### 1️⃣ 버그 감소

```
전통적 방식:
코드 작성 → 배포 → 버그 발견 → 긴급 패치

TDD:
테스트 작성 → 코드 작성 → 버그 즉시 발견 → 수정
```

**수치**:

- IBM: 40% 버그 감소
- Microsoft: 60-90% 결함 감소
- 초기 개발 시간 15-35% 증가
- 유지보수 시간 40-90% 감소

---

### 2️⃣ 설계 개선

```java
// TDD를 하면 자연스럽게 좋은 설계가 나옴

// ❌ TDD 없이 작성한 코드
public class OrderService {
    public void processOrder(Order order) {
        // DB 직접 접근
        Connection conn = DriverManager.getConnection("jdbc:...");
        // 결제 직접 호출
        PaymentGateway.charge(order.getAmount());
        // 이메일 직접 발송
        EmailSender.send(order.getUserEmail(), "주문 완료");
    }
}
// → 테스트 불가능한 강결합

// ✅ TDD로 작성한 코드
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentService paymentService;
    private final EmailService emailService;
    
    public void processOrder(Order order) {
        [orderRepository.save](http://orderRepository.save)(order);
        paymentService.charge(order.getAmount());
        emailService.sendOrderConfirmation(order);
    }
}
// → 테스트 가능한 느슨한 결합
```

---

### 3️⃣ 문서화 효과

```java
// 테스트 자체가 사용 예시
@Test
@DisplayName("프로젝트 생성 시 생성자가 자동으로 멤버로 등록된다")
void createProject_AutoAddCreatorAsMember() {
    // given
    Long userId = 1L;
    ProjectCreateRequestDTO request = new ProjectCreateRequestDTO(
        "프로젝트명", "설명", startDate, endDate, budget
    );
    
    // when
    Long projectId = projectService.createProject(userId, request);
    
    // then
    verify(projectMemberRepository).save(any());
}

// → 이 테스트를 보면 createProject의 동작을 알 수 있음
// → 주석보다 정확하고, 코드와 동기화됨
```

---

### 4️⃣ 리팩토링 안전망

```java
// 리팩토링 전
public BigDecimal calculateDiscount(Order order) {
    if (order.getAmount().compareTo(new BigDecimal("100000")) > 0) {
        return order.getAmount().multiply(new BigDecimal("0.1"));
    }
    return [BigDecimal.ZERO](http://BigDecimal.ZERO);
}

// 리팩토링 후
private static final BigDecimal DISCOUNT_THRESHOLD = new BigDecimal("100000");
private static final BigDecimal DISCOUNT_RATE = new BigDecimal("0.1");

public BigDecimal calculateDiscount(Order order) {
    return isEligibleForDiscount(order) 
        ? applyDiscount(order.getAmount()) 
        : [BigDecimal.ZERO](http://BigDecimal.ZERO);
}

private boolean isEligibleForDiscount(Order order) {
    return order.getAmount().compareTo(DISCOUNT_THRESHOLD) > 0;
}

private BigDecimal applyDiscount(BigDecimal amount) {
    return amount.multiply(DISCOUNT_RATE);
}

// ✅ 테스트가 통과하면 리팩토링 성공!
```

---

## 5.2 단점 및 극복 방법

### 단점 1: 초기 개발 속도 느림

**극복**:

- 장기적으로는 더 빠름 (버그 수정 시간 감소)
- 숙련도가 높아지면 속도 증가
- 테스트 작성 시간 < 버그 수정 시간

---

### 단점 2: 러닝 커브

**극복**:

- 작은 프로젝트부터 시작
- 페어 프로그래밍으로 학습
- 팀 전체가 함께 학습

---

### 단점 3: 모든 것을 테스트할 수 없음

**극복**:

- UI는 E2E 테스트
- 핵심 비즈니스 로직에 집중
- 테스트 피라미드 준수

```
      /\
     /E2E\      10% (느리고 비쌈)
    /------\
   /통합테스트\    20% (중간)
  /----------\
 /  단위테스트  \  70% (빠르고 저렴)
/--------------\
```

---

# 6. Interview Readiness

## ▶ Q1: TDD란 무엇이며 왜 사용하나요?

**A**: TDD(Test-Driven Development)는 테스트를 먼저 작성하고 그 테스트를 통과하는 코드를 나중에 작성하는 개발 방법론입니다.

**사용 이유**:

1. **품질 향상**: 테스트가 자동으로 작성되어 버그가 40-60% 감소합니다
2. **설계 개선**: 테스트 가능한 코드를 작성하다 보면 자연스럽게 느슨한 결합과 높은 응집도를 가진 설계가 나옵니다
3. **안전한 리팩토링**: 기존 기능이 깨지지 않았음을 테스트로 보장하므로 자신감 있게 코드를 개선할 수 있습니다
4. **문서화**: 테스트 코드 자체가 코드의 사용법을 보여주는 살아있는 문서가 됩니다

**실무 경험**: 저희 팀에서 TDD를 도입한 결과, 초기에는 개발 시간이 20% 증가했지만, 버그 수정 시간이 60% 감소하여 전체적으로 생산성이 향상되었습니다.

---

## ▶ Q2: Red-Green-Refactor 사이클을 설명해주세요

**A**: Red-Green-Refactor는 TDD의 핵심 개발 사이클입니다.

**🔴 Red (실패)**:

- 실패하는 테스트를 먼저 작성합니다
- 컴파일 에러도 "실패"에 포함됩니다
- 예: 아직 없는 메서드를 호출하는 테스트 작성

**🟢 Green (성공)**:

- 테스트를 통과하는 최소한의 코드만 작성합니다
- "최소한"이 핵심입니다. 하드코딩도 괜찮습니다
- 예: `return 5;` 처럼 특정 케이스만 통과시키기

**🔵 Refactor (개선)**:

- 중복 제거, 명확한 이름 사용 등으로 코드를 개선합니다
- 단, 테스트는 계속 통과해야 합니다
- 예: 메서드 추출, 매직 넘버 상수화

이 사이클을 5-10분 단위로 빠르게 반복하며, 점진적으로 기능을 완성해나갑니다.

---

## ▶ Q3: TDD의 단점은 무엇이며 어떻게 극복하나요?

**A**: TDD의 주요 단점과 극복 방법은 다음과 같습니다:

**단점 1: 초기 개발 속도 감소**

- 극복: 장기적으로는 버그 수정 시간이 줄어 총 개발 시간이 감소합니다. IBM 연구에 따르면 초기 15-35% 시간 증가, 유지보수 40-90% 시간 감소

**단점 2: 러닝 커브**

- 극복: 작은 유틸리티 함수부터 시작하여 점진적으로 적용 범위를 넓힙니다. 팀 전체가 함께 학습하고 코드 리뷰로 피드백을 주고받습니다

**단점 3: 모든 것을 테스트할 수 없음**

- 극복: 테스트 피라미드를 따릅니다. 단위 테스트(70%) > 통합 테스트(20%) > E2E 테스트(10%). UI는 E2E로, 핵심 비즈니스 로직은 단위 테스트로 커버합니다

---

## 🔑 핵심 체크리스트

- [ ]  TDD는 테스트를 먼저 작성하는 방법론
- [ ]  Red-Green-Refactor 사이클 이해
- [ ]  Red: 실패하는 테스트 먼저
- [ ]  Green: 최소한의 코드로 통과
- [ ]  Refactor: 테스트 유지하며 개선
- [ ]  5-10분 단위 빠른 반복
- [ ]  Uncle Bob의 3가지 법칙
- [ ]  TDD 장점: 버그 감소, 설계 개선, 문서화, 리팩토링 안전망
- [ ]  단점을 극복하는 방법 숙지

---

**작성일**: 2026-01-17  

**시리즈**: TDD 완벽 정복 (1/3)  

**다음 편**: TDD 실전편 - Spring Boot 테스트 작성법