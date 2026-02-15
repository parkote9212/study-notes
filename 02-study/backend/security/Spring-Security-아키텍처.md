---
tags:
  - study
  - spring
  - security
  - architecture
created: 2025-02-08
---

# Spring Security 아키텍처

## 한 줄 요약
> Spring Security는 필터 체인 기반의 인증/인가 프레임워크로, SecurityFilterChain을 통해 요청을 가로채어 인증 정보를 검증하고 권한을 확인한다.

## 상세 설명

### Spring Security란?
- **인증(Authentication)**: 사용자가 누구인지 확인
- **인가(Authorization)**: 사용자가 무엇을 할 수 있는지 확인
- **필터 기반**: Servlet Filter로 요청 가로채기

### 왜 Spring Security가 필요한가?
```java
// ❌ 직접 구현: 보안 취약점, 유지보수 어려움
@GetMapping("/admin")
public String admin(HttpSession session) {
    User user = (User) session.getAttribute("user");
    if (user == null || !user.getRole().equals("ADMIN")) {
        throw new AccessDeniedException();
    }
    return "admin page";
}

// ✅ Spring Security: 선언적 보안
@GetMapping("/admin")
@PreAuthorize("hasRole('ADMIN')")
public String admin() {
    return "admin page";
}
```

### Spring Security 핵심 구조

```
클라이언트 요청
    ↓
DelegatingFilterProxy (Servlet Filter)
    ↓
FilterChainProxy
    ↓
SecurityFilterChain
    ↓
┌─────────────────────────────┐
│ UsernamePasswordAuthenticationFilter  │ → 인증
│ BasicAuthenticationFilter             │
│ BearerTokenAuthenticationFilter       │
│ ...                                    │
│ FilterSecurityInterceptor             │ → 인가
└─────────────────────────────┘
    ↓
Controller
```

### 핵심 컴포넌트

| 컴포넌트 | 역할 | 예시 |
|---------|------|------|
| **SecurityContext** | 인증 정보 저장소 | ThreadLocal 저장 |
| **Authentication** | 인증 정보 객체 | username, authorities |
| **AuthenticationManager** | 인증 처리 위임 | ProviderManager |
| **AuthenticationProvider** | 실제 인증 수행 | DaoAuthenticationProvider |
| **UserDetailsService** | 사용자 정보 조회 | loadUserByUsername() |
| **SecurityFilterChain** | 필터 체인 설정 | http.authorizeRequests() |

### Spring Security 동작 흐름

```
1. 요청 → UsernamePasswordAuthenticationFilter
   ↓
2. Authentication 객체 생성 (username, password)
   ↓
3. AuthenticationManager에게 인증 위임
   ↓
4. AuthenticationProvider가 실제 인증 수행
   ↓
5. UserDetailsService로 사용자 정보 조회
   ↓
6. 비밀번호 검증 (PasswordEncoder)
   ↓
7. 인증 성공 → SecurityContext에 저장
   ↓
8. FilterSecurityInterceptor가 권한 확인
   ↓
9. Controller 실행
```

## 코드 예시

```java
// 1. Spring Security 의존성
// build.gradle
// implementation 'org.springframework.boot:spring-boot-starter-security'

// 2. 기본 Security 설정
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/public/**").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login")
                .permitAll()
            )
            .logout(logout -> logout
                .permitAll()
            );
        
        return http.build();
    }
}

// 3. UserDetailsService 구현
@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {
    
    private final UserRepository userRepository;
    
    @Override
    public UserDetails loadUserByUsername(String username) 
            throws UsernameNotFoundException {
        
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> 
                    new UsernameNotFoundException("User not found: " + username));
        
        return org.springframework.security.core.userdetails.User.builder()
                .username(user.getUsername())
                .password(user.getPassword())
                .roles(user.getRole())
                .build();
    }
}

// 4. 커스텀 UserDetails 구현
@Getter
public class CustomUserDetails implements UserDetails {
    
    private final User user;
    
    public CustomUserDetails(User user) {
        this.user = user;
    }
    
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.singleton(
            new SimpleGrantedAuthority("ROLE_" + user.getRole())
        );
    }
    
    @Override
    public String getPassword() {
        return user.getPassword();
    }
    
    @Override
    public String getUsername() {
        return user.getUsername();
    }
    
    @Override
    public boolean isAccountNonExpired() {
        return true;
    }
    
    @Override
    public boolean isAccountNonLocked() {
        return true;
    }
    
    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }
    
    @Override
    public boolean isEnabled() {
        return user.isActive();
    }
}

// 5. PasswordEncoder 설정
@Configuration
public class PasswordEncoderConfig {
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}

// 회원가입 시 비밀번호 암호화
@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    public void registerUser(String username, String rawPassword) {
        String encodedPassword = passwordEncoder.encode(rawPassword);
        
        User user = User.builder()
                .username(username)
                .password(encodedPassword)
                .role("USER")
                .build();
        
        userRepository.save(user);
    }
}

// 6. 인증된 사용자 정보 가져오기
@RestController
public class UserController {
    
    // 방법 1: SecurityContextHolder 사용
    @GetMapping("/me")
    public String getCurrentUser() {
        Authentication auth = SecurityContextHolder
                .getContext()
                .getAuthentication();
        
        return auth.getName();  // username
    }
    
    // 방법 2: @AuthenticationPrincipal 사용 (권장)
    @GetMapping("/profile")
    public UserDto getProfile(
            @AuthenticationPrincipal CustomUserDetails userDetails) {
        
        User user = userDetails.getUser();
        return new UserDto(user);
    }
    
    // 방법 3: Principal 사용
    @GetMapping("/info")
    public String getInfo(Principal principal) {
        return principal.getName();
    }
}

// 7. 메서드 레벨 보안 (@PreAuthorize, @PostAuthorize)
@Configuration
@EnableMethodSecurity
public class MethodSecurityConfig {
}

@Service
public class OrderService {
    
    // 실행 전 권한 확인
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteOrder(Long orderId) {
        // ADMIN만 삭제 가능
    }
    
    // 실행 후 권한 확인 (반환값 기반)
    @PostAuthorize("returnObject.userId == authentication.principal.user.id")
    public Order getOrder(Long orderId) {
        // 자신의 주문만 조회 가능
        return orderRepository.findById(orderId).get();
    }
    
    // SpEL로 복잡한 조건
    @PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.user.id")
    public void updateUser(Long userId, UserDto dto) {
        // ADMIN이거나 본인만 수정 가능
    }
}

// 8. 커스텀 AuthenticationProvider
@Component
@RequiredArgsConstructor
public class CustomAuthenticationProvider implements AuthenticationProvider {
    
    private final UserDetailsService userDetailsService;
    private final PasswordEncoder passwordEncoder;
    
    @Override
    public Authentication authenticate(Authentication authentication) 
            throws AuthenticationException {
        
        String username = authentication.getName();
        String password = (String) authentication.getCredentials();
        
        // 사용자 정보 조회
        UserDetails userDetails = userDetailsService.loadUserByUsername(username);
        
        // 비밀번호 검증
        if (!passwordEncoder.matches(password, userDetails.getPassword())) {
            throw new BadCredentialsException("Invalid password");
        }
        
        // 추가 검증 (예: IP 체크, 로그인 시도 횟수 등)
        // ...
        
        // 인증 성공
        return new UsernamePasswordAuthenticationToken(
            userDetails,
            password,
            userDetails.getAuthorities()
        );
    }
    
    @Override
    public boolean supports(Class<?> authentication) {
        return UsernamePasswordAuthenticationToken.class
                .isAssignableFrom(authentication);
    }
}

// 9. SecurityContext 직접 조작
@Service
public class AuthService {
    
    public void manualLogin(String username, String password) {
        // Authentication 객체 생성
        UsernamePasswordAuthenticationToken token = 
            new UsernamePasswordAuthenticationToken(username, password);
        
        // AuthenticationManager로 인증
        Authentication auth = authenticationManager.authenticate(token);
        
        // SecurityContext에 저장
        SecurityContextHolder.getContext().setAuthentication(auth);
    }
    
    public void logout() {
        SecurityContextHolder.clearContext();
    }
}

// 10. 역할(Role) vs 권한(Authority)
@Configuration
public class RoleAuthorityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                // Role: ROLE_ 접두사 자동 추가
                .requestMatchers("/admin/**").hasRole("ADMIN")
                // Authority: 접두사 없음
                .requestMatchers("/users/**").hasAuthority("ROLE_USER")
                
                // 여러 Role
                .requestMatchers("/manager/**")
                    .hasAnyRole("ADMIN", "MANAGER")
                
                // 여러 Authority
                .requestMatchers("/api/**")
                    .hasAnyAuthority("ROLE_USER", "ROLE_ADMIN")
            );
        
        return http.build();
    }
}

// UserDetails에서 권한 설정
public class CustomUserDetails implements UserDetails {
    
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        List<GrantedAuthority> authorities = new ArrayList<>();
        
        // Role (ROLE_ 접두사 필요)
        authorities.add(new SimpleGrantedAuthority("ROLE_" + user.getRole()));
        
        // 추가 권한
        user.getPermissions().forEach(permission -> 
            authorities.add(new SimpleGrantedAuthority(permission))
        );
        
        return authorities;
    }
}

// 11. SecurityContextHolder 전략
@Configuration
public class SecurityContextConfig {
    
    @PostConstruct
    public void init() {
        // MODE_THREADLOCAL (기본): 같은 스레드 내에서만 공유
        SecurityContextHolder.setStrategyName(
            SecurityContextHolder.MODE_THREADLOCAL
        );
        
        // MODE_INHERITABLETHREADLOCAL: 자식 스레드에도 전파
        // SecurityContextHolder.setStrategyName(
        //     SecurityContextHolder.MODE_INHERITABLETHREADLOCAL
        // );
        
        // MODE_GLOBAL: 모든 스레드 공유 (멀티 테넌트 환경에서 위험)
    }
}

// 12. 커스텀 인증 성공/실패 핸들러
@Component
public class CustomAuthenticationSuccessHandler 
        implements AuthenticationSuccessHandler {
    
    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication) throws IOException {
        
        // 로그 기록
        log.info("로그인 성공: {}", authentication.getName());
        
        // 세션에 정보 저장
        request.getSession().setAttribute("user", authentication.getPrincipal());
        
        // 리다이렉트
        response.sendRedirect("/dashboard");
    }
}

@Component
public class CustomAuthenticationFailureHandler 
        implements AuthenticationFailureHandler {
    
    @Override
    public void onAuthenticationFailure(
            HttpServletRequest request,
            HttpServletResponse response,
            AuthenticationException exception) throws IOException {
        
        log.error("로그인 실패: {}", exception.getMessage());
        
        response.sendRedirect("/login?error=true");
    }
}

// Security 설정에 적용
@Configuration
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .formLogin(form -> form
                .successHandler(customSuccessHandler)
                .failureHandler(customFailureHandler)
            );
        
        return http.build();
    }
}
```

## 주의사항 / 함정

### 1. 순환 참조 문제
```java
// ❌ SecurityConfig에서 Service 주입 시 순환 참조
@Configuration
public class SecurityConfig {
    @Autowired
    private UserService userService;  // UserService가 SecurityConfig 필요
}

// ✅ 별도 Configuration으로 분리
@Configuration
public class PasswordEncoderConfig {
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### 2. ROLE_ 접두사 혼동
```java
// ❌ hasRole에 ROLE_ 포함
.hasRole("ROLE_ADMIN")  // 실제로는 ROLE_ROLE_ADMIN 됨!

// ✅ hasRole은 접두사 자동 추가
.hasRole("ADMIN")       // ROLE_ADMIN으로 변환

// ✅ hasAuthority는 그대로 사용
.hasAuthority("ROLE_ADMIN")
```

### 3. SecurityContext가 null
```java
// ❌ 비동기 스레드에서 SecurityContext 없음
@Async
public void asyncMethod() {
    Authentication auth = SecurityContextHolder.getContext()
            .getAuthentication();
    // auth == null!
}

// ✅ MODE_INHERITABLETHREADLOCAL 사용 또는 수동 전달
```

### 4. 비밀번호 평문 저장
```java
// ❌ 비밀번호 평문 저장
user.setPassword("password123");

// ✅ BCrypt로 암호화
String encoded = passwordEncoder.encode("password123");
user.setPassword(encoded);
```

### 5. permitAll() 위치
```java
// ❌ anyRequest() 먼저 오면 이후 설정 무시
http
    .authorizeRequests()
    .anyRequest().authenticated()
    .requestMatchers("/public/**").permitAll();  // 무시됨!

// ✅ 순서 중요 (구체적인 것부터)
http
    .authorizeRequests()
    .requestMatchers("/public/**").permitAll()
    .anyRequest().authenticated();
```

### 6. CSRF 비활성화 남용
```java
// ❌ 모든 환경에서 CSRF 비활성화
http.csrf().disable();  // 보안 취약!

// ✅ REST API만 비활성화
http.csrf(csrf -> csrf
    .ignoringRequestMatchers("/api/**")
);
```

### 7. 메모리 내 사용자 프로덕션 사용
```java
// ❌ 프로덕션에서 inMemoryAuthentication 사용
http.inMemoryAuthentication()
    .withUser("admin").password("1234").roles("ADMIN");

// ✅ DB 기반 UserDetailsService 구현
```

## 관련 개념
- [[인증-흐름-Authentication]]
- [[인가-흐름-Authorization]]
- [[필터체인-FilterChain]]
- [[JWT-토큰-기반-인증]]

## 면접 질문

1. **Spring Security의 인증 과정을 설명하세요.**
   - Filter → AuthenticationManager → Provider → UserDetailsService → 비밀번호 검증 → SecurityContext 저장

2. **SecurityContext는 어디에 저장되나요?**
   - ThreadLocal (기본 MODE_THREADLOCAL)
   - 같은 스레드 내에서만 공유

3. **hasRole과 hasAuthority의 차이는?**
   - hasRole: ROLE_ 접두사 자동 추가
   - hasAuthority: 입력한 그대로 사용

4. **UserDetailsService의 역할은?**
   - username으로 사용자 정보 조회
   - UserDetails 객체 반환

5. **@PreAuthorize와 @PostAuthorize의 차이는?**
   - @PreAuthorize: 메서드 실행 전 권한 확인
   - @PostAuthorize: 메서드 실행 후 반환값 기반 권한 확인

6. **Spring Security는 어떻게 요청을 가로채나요?**
   - Servlet Filter (DelegatingFilterProxy)
   - FilterChainProxy → SecurityFilterChain

7. **PasswordEncoder를 사용하는 이유는?**
   - 비밀번호 평문 저장 방지
   - BCrypt 등 단방향 암호화

## 참고 자료
- Spring Security Reference Documentation
- Baeldung Spring Security Tutorials
- https://docs.spring.io/spring-security/reference/
