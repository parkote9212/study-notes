---
tags:
  - study
  - spring
  - security
  - authentication
created: 2025-02-08
---

# 인증 흐름 Authentication

## 한 줄 요약
> 인증(Authentication)은 사용자의 신원을 확인하는 과정으로, Spring Security는 UsernamePasswordAuthenticationFilter를 통해 자격증명을 받아 AuthenticationManager가 검증한 후 SecurityContext에 저장한다.

## 상세 설명

### 인증이란?
- **"당신은 누구인가?"**를 확인
- 자격증명(Credentials) 검증: username + password, 토큰 등
- 인증 성공 → Authentication 객체 생성

### 인증 vs 인가

| 인증 (Authentication) | 인가 (Authorization) |
|---------------------|---------------------|
| 신원 확인 | 권한 확인 |
| "누구인가?" | "무엇을 할 수 있는가?" |
| 로그인 | 접근 제어 |

### Authentication 객체 구조
```java
public interface Authentication {
    String getName();                          // 사용자 이름
    Object getCredentials();                   // 자격증명 (비밀번호)
    Object getPrincipal();                     // 주체 (UserDetails)
    Collection<GrantedAuthority> getAuthorities();  // 권한 목록
    boolean isAuthenticated();                 // 인증 여부
}
```

### 인증 흐름

```
1. 사용자 로그인 (username, password)
   ↓
2. UsernamePasswordAuthenticationFilter
   ↓
3. Authentication 객체 생성 (미인증 상태)
   ↓
4. AuthenticationManager.authenticate()
   ↓
5. AuthenticationProvider 선택
   ↓
6. UserDetailsService.loadUserByUsername()
   ↓
7. 비밀번호 검증 (PasswordEncoder)
   ↓
8. Authentication 객체 갱신 (인증 완료)
   ↓
9. SecurityContext에 저장
   ↓
10. 인증 성공 핸들러 실행
```

## 코드 예시

```java
// 1. 기본 Form 로그인 설정
@Configuration
@EnableWebSecurity
public class FormLoginConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .formLogin(form -> form
                .loginPage("/login")               // 로그인 페이지
                .loginProcessingUrl("/login")      // 로그인 처리 URL
                .usernameParameter("email")        // 기본값: username
                .passwordParameter("pwd")          // 기본값: password
                .defaultSuccessUrl("/dashboard")   // 로그인 성공 시
                .failureUrl("/login?error=true")   // 로그인 실패 시
                .permitAll()
            );
        
        return http.build();
    }
}

// 2. UserDetailsService 구현 (DB 기반)
@Service
@RequiredArgsConstructor
public class UserDetailsServiceImpl implements UserDetailsService {
    
    private final UserRepository userRepository;
    
    @Override
    public UserDetails loadUserByUsername(String username) 
            throws UsernameNotFoundException {
        
        // 1. DB에서 사용자 조회
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> 
                    new UsernameNotFoundException("User not found: " + username));
        
        // 2. UserDetails로 변환
        return org.springframework.security.core.userdetails.User.builder()
                .username(user.getUsername())
                .password(user.getPassword())  // 이미 암호화된 비밀번호
                .roles(user.getRole())
                .accountLocked(!user.isActive())
                .build();
    }
}

// 3. 커스텀 UserDetails 구현
@Getter
public class CustomUserDetails implements UserDetails {
    
    private final Long id;
    private final String username;
    private final String password;
    private final String email;
    private final String role;
    private final boolean active;
    
    public CustomUserDetails(User user) {
        this.id = user.getId();
        this.username = user.getUsername();
        this.password = user.getPassword();
        this.email = user.getEmail();
        this.role = user.getRole();
        this.active = user.isActive();
    }
    
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.singleton(
            new SimpleGrantedAuthority("ROLE_" + role)
        );
    }
    
    @Override
    public String getPassword() {
        return password;
    }
    
    @Override
    public String getUsername() {
        return username;
    }
    
    @Override
    public boolean isAccountNonExpired() {
        return true;  // 계정 만료 체크
    }
    
    @Override
    public boolean isAccountNonLocked() {
        return active;  // 계정 잠김 체크
    }
    
    @Override
    public boolean isCredentialsNonExpired() {
        return true;  // 비밀번호 만료 체크
    }
    
    @Override
    public boolean isEnabled() {
        return active;  // 계정 활성화 체크
    }
}

// 4. 커스텀 AuthenticationProvider
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
        
        // 1. 사용자 정보 조회
        UserDetails userDetails = userDetailsService.loadUserByUsername(username);
        
        // 2. 비밀번호 검증
        if (!passwordEncoder.matches(password, userDetails.getPassword())) {
            throw new BadCredentialsException("Invalid password");
        }
        
        // 3. 계정 상태 확인
        if (!userDetails.isAccountNonLocked()) {
            throw new LockedException("Account is locked");
        }
        
        if (!userDetails.isEnabled()) {
            throw new DisabledException("Account is disabled");
        }
        
        // 4. 추가 검증 (예: IP 체크)
        // ...
        
        // 5. 인증 성공 - Authentication 객체 반환
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

// 5. 로그인 API (REST)
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {
    
    private final AuthenticationManager authenticationManager;
    
    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@RequestBody LoginRequest request) {
        try {
            // 1. Authentication 객체 생성 (미인증)
            Authentication authRequest = new UsernamePasswordAuthenticationToken(
                request.getUsername(),
                request.getPassword()
            );
            
            // 2. 인증 수행
            Authentication authResult = authenticationManager.authenticate(authRequest);
            
            // 3. SecurityContext에 저장
            SecurityContextHolder.getContext().setAuthentication(authResult);
            
            // 4. 응답
            return ResponseEntity.ok(new LoginResponse("Login successful"));
            
        } catch (BadCredentialsException e) {
            throw new UnauthorizedException("Invalid credentials");
        }
    }
}

// 6. 인증 성공/실패 핸들러
@Component
@Slf4j
public class LoginSuccessHandler implements AuthenticationSuccessHandler {
    
    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication) throws IOException {
        
        // 1. 로그 기록
        log.info("로그인 성공: {}", authentication.getName());
        
        // 2. 로그인 기록 저장
        LoginHistory history = LoginHistory.builder()
                .username(authentication.getName())
                .ipAddress(request.getRemoteAddr())
                .userAgent(request.getHeader("User-Agent"))
                .loginTime(LocalDateTime.now())
                .build();
        loginHistoryRepository.save(history);
        
        // 3. 세션에 정보 저장
        HttpSession session = request.getSession();
        session.setAttribute("user", authentication.getPrincipal());
        
        // 4. 리다이렉트
        String redirectUrl = determineTargetUrl(authentication);
        response.sendRedirect(redirectUrl);
    }
    
    private String determineTargetUrl(Authentication auth) {
        // 권한에 따라 다른 페이지로 리다이렉트
        if (auth.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"))) {
            return "/admin/dashboard";
        }
        return "/user/dashboard";
    }
}

@Component
@Slf4j
public class LoginFailureHandler implements AuthenticationFailureHandler {
    
    @Override
    public void onAuthenticationFailure(
            HttpServletRequest request,
            HttpServletResponse response,
            AuthenticationException exception) throws IOException {
        
        log.error("로그인 실패: {}", exception.getMessage());
        
        // 실패 원인별 처리
        String errorMessage;
        if (exception instanceof BadCredentialsException) {
            errorMessage = "아이디 또는 비밀번호가 잘못되었습니다.";
        } else if (exception instanceof LockedException) {
            errorMessage = "계정이 잠겨있습니다.";
        } else if (exception instanceof DisabledException) {
            errorMessage = "계정이 비활성화되었습니다.";
        } else {
            errorMessage = "로그인에 실패했습니다.";
        }
        
        response.sendRedirect("/login?error=" + 
                URLEncoder.encode(errorMessage, StandardCharsets.UTF_8));
    }
}

// 7. Remember Me 인증
@Configuration
public class RememberMeConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .rememberMe(remember -> remember
                .key("uniqueAndSecret")
                .tokenValiditySeconds(86400 * 7)  // 7일
                .userDetailsService(userDetailsService)
                .rememberMeParameter("remember")  // 체크박스 name
            );
        
        return http.build();
    }
}

// HTML 폼
// <input type="checkbox" name="remember" /> 로그인 상태 유지

// 8. 로그아웃 설정
@Configuration
public class LogoutConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .logout(logout -> logout
                .logoutUrl("/logout")                    // 로그아웃 URL
                .logoutSuccessUrl("/login?logout=true")  // 성공 시 이동
                .invalidateHttpSession(true)             // 세션 무효화
                .deleteCookies("JSESSIONID", "remember") // 쿠키 삭제
                .addLogoutHandler(customLogoutHandler)   // 커스텀 핸들러
                .logoutSuccessHandler(customSuccessHandler)
            );
        
        return http.build();
    }
}

@Component
@RequiredArgsConstructor
public class CustomLogoutHandler implements LogoutHandler {
    
    private final LogoutHistoryRepository logoutHistoryRepository;
    
    @Override
    public void logout(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication) {
        
        if (authentication != null) {
            // 로그아웃 기록
            LogoutHistory history = LogoutHistory.builder()
                    .username(authentication.getName())
                    .logoutTime(LocalDateTime.now())
                    .build();
            logoutHistoryRepository.save(history);
        }
    }
}

// 9. 프로그래밍 방식 인증
@Service
@RequiredArgsConstructor
public class AuthService {
    
    private final AuthenticationManager authenticationManager;
    private final UserDetailsService userDetailsService;
    
    // 수동 로그인
    public void manualLogin(String username, String password) {
        // 1. Authentication 객체 생성
        UsernamePasswordAuthenticationToken token = 
            new UsernamePasswordAuthenticationToken(username, password);
        
        // 2. 인증 수행
        Authentication authentication = authenticationManager.authenticate(token);
        
        // 3. SecurityContext에 저장
        SecurityContextHolder.getContext().setAuthentication(authentication);
    }
    
    // 비밀번호 없이 로그인 (소셜 로그인 등)
    public void loginWithoutPassword(String username) {
        UserDetails userDetails = userDetailsService.loadUserByUsername(username);
        
        // 인증된 토큰 생성 (비밀번호 null, 인증됨 표시)
        UsernamePasswordAuthenticationToken authentication = 
            new UsernamePasswordAuthenticationToken(
                userDetails,
                null,
                userDetails.getAuthorities()
            );
        
        SecurityContextHolder.getContext().setAuthentication(authentication);
    }
    
    // 로그아웃
    public void logout() {
        SecurityContextHolder.clearContext();
    }
}

// 10. 다중 AuthenticationProvider
@Configuration
public class MultiProviderConfig {
    
    @Bean
    public AuthenticationManager authenticationManager(
            HttpSecurity http,
            List<AuthenticationProvider> providers) throws Exception {
        
        AuthenticationManagerBuilder authBuilder = 
            http.getSharedObject(AuthenticationManagerBuilder.class);
        
        // 여러 Provider 등록
        providers.forEach(authBuilder::authenticationProvider);
        
        return authBuilder.build();
    }
}

// Provider 1: 일반 사용자
@Component
public class UserAuthenticationProvider implements AuthenticationProvider {
    // ...
}

// Provider 2: 관리자
@Component
public class AdminAuthenticationProvider implements AuthenticationProvider {
    // ...
}

// 11. 인증 이벤트 리스너
@Component
@Slf4j
public class AuthenticationEventListener {
    
    @EventListener
    public void onAuthenticationSuccess(
            AuthenticationSuccessEvent event) {
        
        String username = event.getAuthentication().getName();
        log.info("인증 성공: {}", username);
    }
    
    @EventListener
    public void onAuthenticationFailure(
            AbstractAuthenticationFailureEvent event) {
        
        String username = event.getAuthentication().getName();
        Exception exception = event.getException();
        log.error("인증 실패: {}, 원인: {}", username, exception.getMessage());
        
        // 로그인 실패 횟수 증가, 계정 잠금 등
    }
}

// 12. 현재 인증 정보 가져오기
@RestController
@RequestMapping("/api/user")
public class UserInfoController {
    
    // 방법 1: SecurityContextHolder
    @GetMapping("/me")
    public UserDto getCurrentUser() {
        Authentication auth = SecurityContextHolder.getContext()
                .getAuthentication();
        
        if (auth == null || !auth.isAuthenticated()) {
            throw new UnauthorizedException();
        }
        
        CustomUserDetails userDetails = (CustomUserDetails) auth.getPrincipal();
        return UserDto.from(userDetails);
    }
    
    // 방법 2: @AuthenticationPrincipal (권장)
    @GetMapping("/profile")
    public UserDto getProfile(
            @AuthenticationPrincipal CustomUserDetails userDetails) {
        
        return UserDto.from(userDetails);
    }
    
    // 방법 3: Principal
    @GetMapping("/name")
    public String getUsername(Principal principal) {
        return principal.getName();
    }
    
    // 방법 4: Authentication 직접 주입
    @GetMapping("/auth")
    public UserDto getUserAuth(Authentication authentication) {
        CustomUserDetails userDetails = 
            (CustomUserDetails) authentication.getPrincipal();
        return UserDto.from(userDetails);
    }
}
```

## 주의사항 / 함정

### 1. 비밀번호 평문 비교
```java
// ❌ 평문 비교
if (inputPassword.equals(user.getPassword())) {
    // 보안 취약!
}

// ✅ PasswordEncoder 사용
if (passwordEncoder.matches(inputPassword, user.getPassword())) {
    // 안전
}
```

### 2. UserDetails 캐스팅 오류
```java
// ❌ 바로 캐스팅
CustomUserDetails userDetails = (CustomUserDetails) auth.getPrincipal();
// OAuth2 로그인 시 ClassCastException!

// ✅ instanceof 체크
if (auth.getPrincipal() instanceof CustomUserDetails) {
    CustomUserDetails userDetails = (CustomUserDetails) auth.getPrincipal();
}
```

### 3. 인증 후 SecurityContext 저장 누락
```java
// ❌ 인증만 하고 저장 안 함
Authentication auth = authenticationManager.authenticate(token);
// 이후 요청에서 인증 정보 없음!

// ✅ SecurityContext에 저장
SecurityContextHolder.getContext().setAuthentication(auth);
```

### 4. 세션 고정 공격 방어 누락
```java
// ✅ 로그인 성공 시 세션 ID 변경 (기본 설정)
http.sessionManagement(session -> session
    .sessionFixation().changeSessionId()  // 기본값
);
```

### 5. Remember Me 키 노출
```java
// ❌ 하드코딩된 키
.rememberMe().key("mySecretKey")

// ✅ 환경변수 사용
.rememberMe().key(env.getProperty("remember.me.key"))
```

### 6. 로그아웃 시 쿠키 삭제 누락
```java
// ❌ 세션만 무효화
.logout()
.invalidateHttpSession(true)

// ✅ 쿠키도 삭제
.logout()
.invalidateHttpSession(true)
.deleteCookies("JSESSIONID", "remember")
```

### 7. 비동기 스레드에서 인증 정보 없음
```java
// ❌ @Async 메서드에서 SecurityContext 없음
@Async
public void asyncMethod() {
    Authentication auth = SecurityContextHolder.getContext()
            .getAuthentication();
    // auth == null!
}

// ✅ DelegatingSecurityContextAsyncTaskExecutor 사용
```

## 관련 개념
- [[Spring-Security-아키텍처]]
- [[인가-흐름-Authorization]]
- [[JWT-토큰-기반-인증]]
- [[OAuth2-기초]]

## 면접 질문

1. **인증(Authentication)과 인가(Authorization)의 차이는?**
   - 인증: 신원 확인 ("누구인가?")
   - 인가: 권한 확인 ("무엇을 할 수 있는가?")

2. **Spring Security의 인증 과정을 단계별로 설명하세요.**
   - Filter → Authentication 생성 → AuthenticationManager → Provider → UserDetailsService → 비밀번호 검증 → SecurityContext 저장

3. **UserDetailsService의 역할은?**
   - username으로 사용자 정보 조회
   - UserDetails 객체 반환

4. **AuthenticationProvider와 UserDetailsService의 차이는?**
   - AuthenticationProvider: 전체 인증 로직 담당
   - UserDetailsService: 사용자 정보만 조회

5. **Remember Me는 어떻게 동작하나요?**
   - 쿠키에 토큰 저장
   - 세션 만료 후에도 자동 로그인

6. **SecurityContext는 어디에 저장되나요?**
   - ThreadLocal (기본)
   - 세션과는 별개

7. **로그인 실패 시 계정 잠금은 어떻게 구현하나요?**
   - AuthenticationFailureHandler에서 실패 횟수 카운트
   - 일정 횟수 초과 시 User.accountLocked = true

## 참고 자료
- Spring Security Reference - Authentication
- Baeldung Authentication Tutorials
- https://docs.spring.io/spring-security/reference/servlet/authentication/index.html
