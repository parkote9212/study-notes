---
tags:
  - study
  - TDD
  - Testing
  - java
created: 2026-01-24
---

# TDD 기초 Red-Green-Refactor

## 한 줄 요약
> TDD는 테스트를 먼저 작성하고 코드를 나중에 작성하는 개발 방법론으로 Red-Green-Refactor 사이클을 5-10분 단위로 반복

## 상세 설명

TDD(Test-Driven Development)는 버그를 줄이고 유지보수성을 높이며 자신감 있는 리팩토링을 가능하게 합니다.

### Red-Green-Refactor 사이클

**🔴 Red (실패)**: 실패하는 테스트를 먼저 작성
- 컴파일 에러도 "실패"에 포함
- 테스트가 정말 실패하는지 확인 (False Positive 방지)

**🟢 Green (성공)**: 테스트를 통과하는 최소한의 코드 작성
- "최소한"이 핵심, 하드코딩도 OK
- 일단 통과시키는 것이 목표

**🔵 Refactor (개선)**: 코드 품질 개선 (테스트는 계속 통과)
- 중복 코드 제거, 변수/메서드명 개선
- 테스트는 항상 통과 유지

### TDD의 3가지 법칙 (Uncle Bob)

1. 실패하는 테스트를 작성하기 전에는 프로덕션 코드를 작성하지 않는다
2. 컴파일 실패를 포함해서 실패하는 테스트를 하나 이상 작성하지 않는다
3. 현재 실패하는 테스트를 통과시키기에 충분한 정도를 넘어서는 프로덕션 코드를 작성하지 않는다

### TDD의 장단점

**장점**:
- 버그 40-60% 감소 (IBM, Microsoft 연구)
- 자연스럽게 좋은 설계 (테스트 가능한 코드 = 느슨한 결합)
- 안전한 리팩토링 (테스트가 보장)
- 살아있는 문서화 (테스트 코드가 사용 예시)

**단점 및 극복**:
- 초기 개발 속도 15-35% 증가 → 장기적으로 유지보수 40-90% 감소
- 러닝 커브 → 작은 프로젝트부터 시작
- 모든 것 테스트 불가 → 테스트 피라미드 준수 (단위 70%, 통합 20%, E2E 10%)

## 코드 예시

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
// 컴파일 에러! Calculator 클래스가 없음

// 2단계: GREEN - 최소한의 코드로 테스트 통과
public class Calculator {
    public int add(int a, int b) {
        return a + b;  // 가장 간단한 구현
    }
}
// ✅ 테스트 통과!

// 3단계: REFACTOR - 코드 개선
public class Calculator {
    public int add(int a, int b) {
        return sum(a, b);
    }
    
    private int sum(int a, int b) {
        return a + b;
    }
}
// ✅ 테스트 여전히 통과!

// 실전 예제: 로그인 기능
@ExtendWith(MockitoExtension.class)
class AuthServiceTest {
    @InjectMocks
    private AuthService authService;
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private PasswordEncoder passwordEncoder;
    
    @Test
    @DisplayName("로그인 성공 시 토큰을 반환해야 한다")
    void login_Success() {
        // given
        LoginRequestDTO request = new LoginRequestDTO("test@example.com", "1234");
        User testUser = User.builder()
            .email("test@example.com")
            .password("encoded_1234")
            .build();
        
        given(userRepository.findByEmail(request.email()))
            .willReturn(Optional.of(testUser));
        given(passwordEncoder.matches(request.password(), testUser.getPassword()))
            .willReturn(true);
        
        // when
        JwtTokenResponse token = authService.login(request);
        
        // then
        assertThat(token).isNotNull();
        assertThat(token.getAccessToken()).isNotEmpty();
    }
}
```

## 주의사항 / 함정

1. **테스트를 나중에 작성**: TDD의 핵심은 "테스트 먼저"
2. **한 번에 여러 테스트 작성**: 하나씩 작성하고 통과시키기
3. **과도한 구현**: 테스트 통과에 필요한 최소한만 작성
4. **리팩토링 생략**: Green 단계 후 반드시 Refactor

## 관련 개념
- [[TDD-실전편]]
- [[JUnit5]]
- [[Mockito]]
- [[테스트-피라미드]]

## 면접 질문
1. TDD란 무엇이며 왜 사용하나요?
2. Red-Green-Refactor 사이클을 설명해주세요
3. TDD의 단점은 무엇이며 어떻게 극복하나요?

## 참고 자료
- Kent Beck, "Test Driven Development"
- Uncle Bob, "Clean Code"
