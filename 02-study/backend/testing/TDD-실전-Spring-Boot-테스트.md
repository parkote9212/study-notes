---
tags:
  - study
  - TDD
  - Testing
  - spring-boot
created: 2026-01-24
---

# TDD 실전 Spring Boot 테스트

## 한 줄 요약
> Spring Boot 테스트는 JUnit 5, Mockito, AssertJ를 사용하며, 테스트 피라미드(70-20-10)를 준수하여 단위/통합/E2E 테스트를 작성

## 상세 설명

Spring Boot 테스트는 @SpringBootTest로 전체 컨텍스트를 로드하거나, @WebMvcTest/@DataJpaTest 등으로 특정 레이어만 테스트합니다.

### 주요 어노테이션

**@SpringBootTest**:
- 전체 Spring Context 로드
- 통합 테스트에 사용
- 느린 실행 속도

**@WebMvcTest**:
- Controller 레이어만 테스트
- MockMvc 자동 설정
- Service는 @MockBean으로 주입

**@DataJpaTest**:
- JPA 레이어만 테스트
- 내장 DB(H2) 자동 설정
- @Transactional 자동 적용

**@ExtendWith(MockitoExtension.class)**:
- 순수 단위 테스트
- Spring Context 없음
- 가장 빠름

### 테스트 피라미드

```
      E2E (10%)
    통합 테스트 (20%)
  단위 테스트 (70%)
```

**단위 테스트**: 가장 많이, 가장 빠르게
**통합 테스트**: 컴포넌트 연동 확인
**E2E 테스트**: 전체 시나리오 검증

### Given-When-Then 패턴

```java
// given - 준비
// when - 실행
// then - 검증
```

## 코드 예시

```java
// 1. 단위 테스트 (Service Layer)
@ExtendWith(MockitoExtension.class)
class AuthServiceTest {
    @InjectMocks
    private AuthService authService;
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private PasswordEncoder passwordEncoder;
    
    @Test
    @DisplayName("로그인 성공")
    void login_Success() {
        // given
        LoginRequestDTO request = new LoginRequestDTO("test@example.com", "1234");
        User user = User.builder()
            .email("test@example.com")
            .password("encoded_1234")
            .build();
        
        given(userRepository.findByEmail(request.email()))
            .willReturn(Optional.of(user));
        given(passwordEncoder.matches(request.password(), user.getPassword()))
            .willReturn(true);
        
        // when
        JwtTokenResponse token = authService.login(request);
        
        // then
        assertThat(token).isNotNull();
        assertThat(token.getAccessToken()).isNotEmpty();
        
        verify(userRepository, times(1)).findByEmail(request.email());
    }
}

// 2. Controller 테스트
@WebMvcTest(UserController.class)
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private UserService userService;
    
    @Test
    @DisplayName("사용자 조회 API")
    void getUser() throws Exception {
        // given
        UserResponseDTO user = new UserResponseDTO(1L, "test@example.com");
        given(userService.getUser(1L)).willReturn(user);
        
        // when & then
        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.email").value("test@example.com"));
    }
}

// 3. Repository 테스트
@DataJpaTest
class UserRepositoryTest {
    @Autowired
    private UserRepository userRepository;
    
    @Test
    @DisplayName("이메일로 사용자 조회")
    void findByEmail() {
        // given
        User user = User.builder()
            .email("test@example.com")
            .password("1234")
            .build();
        userRepository.save(user);
        
        // when
        Optional<User> found = userRepository.findByEmail("test@example.com");
        
        // then
        assertThat(found).isPresent();
        assertThat(found.get().getEmail()).isEqualTo("test@example.com");
    }
}

// 4. 통합 테스트
@SpringBootTest
@AutoConfigureMockMvc
class IntegrationTest {
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private UserRepository userRepository;
    
    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }
    
    @Test
    @DisplayName("사용자 생성 전체 흐름")
    void createUser_FullFlow() throws Exception {
        // when & then
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"email\":\"test@example.com\",\"password\":\"1234\"}"))
            .andExpect(status().isCreated());
        
        // 검증
        assertThat(userRepository.findByEmail("test@example.com")).isPresent();
    }
}
```

## 주의사항 / 함정

1. **@Mock vs @MockBean**: Mock은 Mockito, MockBean은 Spring
2. **given vs when**: BDD 스타일은 given(), Mockito 스타일은 when()
3. **테스트 격리**: @BeforeEach로 데이터 초기화
4. **트랜잭션 롤백**: @DataJpaTest는 자동, @SpringBootTest는 수동 설정

## 관련 개념
- [[TDD-기초-Red-Green-Refactor]]
- [[JUnit5]]
- [[Mockito]]
- [[AssertJ]]

## 면접 질문
1. @Mock과 @MockBean의 차이는?
2. 테스트 피라미드란?
3. given-when-then 패턴을 설명하세요

## 참고 자료
- Spring Boot Test 공식 문서
