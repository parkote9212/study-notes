# SpringSecurity-기초-아키텍처

🏷️기술 카테고리: Security, Spring
💡핵심키워드: #SpringSecurity, #아키텍처, #필터체인
💼 면접 빈출도: 최상

# 1. Abstract: 핵심 요약

**Spring Security**는 Spring 기반 애플리케이션의 인증(Authentication)과 인가(Authorization)를 담당하는 강력한 보안 프레임워크입니다. **서블릿 필터 체인**을 기반으로 동작하며, 선언적 방식으로 보안 정책을 설정할 수 있습니다.

**핵심 원칙**:
- 인증: "당신은 누구인가?" (로그인)
- 인가: "당신은 이 자원에 접근할 권한이 있는가?" (권한 검증)
- 필터 체인: 요청이 컨트롤러에 도달하기 전에 보안 검증

# 2. Spring Security 아키텍처

## 2.1 핵심 구조

```
[HTTP Request]
    ↓
[Servlet Filter Chain]
    ↓
[DelegatingFilterProxy] ← Spring Security 진입점
    ↓
[FilterChainProxy]
    ↓
[Security Filter Chain]
    ├─ SecurityContextPersistenceFilter
    ├─ UsernamePasswordAuthenticationFilter
    ├─ ExceptionTranslationFilter
    └─ FilterSecurityInterceptor
    ↓
[DispatcherServlet] → Controller
```

## 2.2 주요 컴포넌트

### SecurityContext
- 현재 인증된 사용자 정보를 저장
- ThreadLocal에 저장되어 같은 스레드 내에서 어디서든 접근 가능

```java
Authentication auth = SecurityContextHolder.getContext().getAuthentication();
String username = auth.getName();
```

### Authentication
- 인증 정보를 담는 인터페이스
- Principal(주체), Credentials(비밀번호), Authorities(권한) 포함

### AuthenticationManager
- 인증을 처리하는 핵심 인터페이스
- 일반적으로 ProviderManager가 구현체로 사용

### UserDetailsService
- 사용자 정보를 DB에서 조회하는 인터페이스

# 3. 기본 설정

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(Customizer.withDefaults());
        
        return http.build();
    }
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

# 4. UserDetailsService 구현

```java
@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String username) 
        throws UsernameNotFoundException {
        
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException("User not found"));
        
        return org.springframework.security.core.userdetails.User
            .withUsername(user.getUsername())
            .password(user.getPassword())
            .roles(user.getRole())
            .build();
    }
}
```

# 5. Interview Readiness

## Q1: Spring Security는 어떻게 동작하나요?

**A**: Spring Security는 서블릿 필터 체인을 기반으로 동작합니다. HTTP 요청이 들어오면 DispatcherServlet에 도달하기 전에 여러 보안 필터를 거치게 됩니다. 주요 필터로는 SecurityContextPersistenceFilter(컨텍스트 관리), UsernamePasswordAuthenticationFilter(로그인 처리), FilterSecurityInterceptor(권한 검증) 등이 있습니다.

## Q2: Authentication과 Authorization의 차이는?

**A**:
- Authentication(인증): "당신은 누구인가?"를 확인하는 과정
- Authorization(인가): "당신은 이 자원에 접근할 권한이 있는가?"를 확인하는 과정

로그인(인증)에 성공했더라도 관리자 페이지에 접근하려면 ADMIN 역할(인가)이 필요합니다.

## Q3: SecurityContext는 왜 ThreadLocal에 저장되나요?

**A**: 동일한 HTTP 요청을 처리하는 스레드 내에서 어디서든 인증 정보에 접근할 수 있도록 하기 위함입니다. 매번 파라미터로 인증 정보를 전달하지 않아도 되며, 서비스 계층에서도 현재 사용자 정보를 쉽게 가져올 수 있습니다.

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
