---
tags:
  - study
  - spring
  - security
  - filter-chain
created: 2025-02-08
---

# 필터체인 FilterChain

## 한 줄 요약
> Spring Security의 필터 체인은 DelegatingFilterProxy를 통해 서블릿 필터를 Spring 빈으로 연결하며, SecurityFilterChain에 등록된 여러 필터가 순서대로 요청을 가로채어 인증과 인가를 수행한다.

## 상세 설명

### 필터 체인이란?
- **Servlet Filter** 기반의 보안 처리
- **체인 패턴**: 여러 필터가 순서대로 실행
- **요청 가로채기**: Controller 도달 전 보안 검사

### 왜 필터 체인이 필요한가?
```java
// ❌ Controller에서 보안 처리: 중복 코드, 누락 위험
@GetMapping("/admin")
public String admin(HttpSession session) {
    if (!isAuthenticated(session)) {
        throw new UnauthorizedException();
    }
    if (!hasRole(session, "ADMIN")) {
        throw new AccessDeniedException();
    }
    return "admin";
}

// ✅ 필터 체인: 자동으로 인증/인가 처리
@GetMapping("/admin")
@PreAuthorize("hasRole('ADMIN')")
public String admin() {
    return "admin";
}
```

### Spring Security 필터 체인 구조

```
클라이언트 요청
    ↓
Servlet Container
    ↓
DelegatingFilterProxy (서블릿 필터)
    ↓
FilterChainProxy (Spring 빈)
    ↓
SecurityFilterChain (필터 목록)
    ↓
┌─────────────────────────────────────┐
│ 1. SecurityContextPersistenceFilter │
│ 2. LogoutFilter                     │
│ 3. UsernamePasswordAuthenticationFilter │
│ 4. BasicAuthenticationFilter        │
│ 5. BearerTokenAuthenticationFilter  │
│ 6. FilterSecurityInterceptor        │
│ ...                                  │
└─────────────────────────────────────┘
    ↓
DispatcherServlet
    ↓
Controller
```

### 주요 필터 목록 (순서대로)

| 필터 | 역할 | 우선순위 |
|-----|------|---------|
| **SecurityContextPersistenceFilter** | SecurityContext 로드/저장 | 1 |
| **LogoutFilter** | 로그아웃 처리 | 2 |
| **UsernamePasswordAuthenticationFilter** | Form 로그인 인증 | 3 |
| **BasicAuthenticationFilter** | HTTP Basic 인증 | 4 |
| **BearerTokenAuthenticationFilter** | JWT 토큰 인증 | 5 |
| **SessionManagementFilter** | 세션 관리 | 6 |
| **ExceptionTranslationFilter** | 예외 처리 | 7 |
| **FilterSecurityInterceptor** | 인가 처리 | 8 (마지막) |

## 코드 예시

```java
// 1. 기본 필터 체인 구조 확인
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .anyRequest().authenticated()
            )
            .formLogin(Customizer.withDefaults());
        
        return http.build();
    }
}

// 필터 체인 로그 확인
// 애플리케이션 시작 시 자동으로 출력됨:
// Security filter chain: [
//   SecurityContextPersistenceFilter
//   LogoutFilter
//   UsernamePasswordAuthenticationFilter
//   ...
// ]

// 2. 커스텀 필터 추가
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        // 1. JWT 토큰 추출
        String token = extractToken(request);
        
        if (token != null && validateToken(token)) {
            // 2. 인증 정보 생성
            Authentication auth = getAuthentication(token);
            
            // 3. SecurityContext에 저장
            SecurityContextHolder.getContext().setAuthentication(auth);
        }
        
        // 4. 다음 필터로 전달
        filterChain.doFilter(request, response);
    }
    
    private String extractToken(HttpServletRequest request) {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            return header.substring(7);
        }
        return null;
    }
}

// 필터 등록
@Configuration
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // UsernamePasswordAuthenticationFilter 앞에 추가
            .addFilterBefore(
                jwtAuthenticationFilter(),
                UsernamePasswordAuthenticationFilter.class
            );
        
        return http.build();
    }
    
    @Bean
    public JwtAuthenticationFilter jwtAuthenticationFilter() {
        return new JwtAuthenticationFilter();
    }
}

// 3. 필터 추가 위치 지정
@Configuration
public class CustomFilterConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // 특정 필터 앞에 추가
            .addFilterBefore(customFilter1, UsernamePasswordAuthenticationFilter.class)
            
            // 특정 필터 뒤에 추가
            .addFilterAfter(customFilter2, BasicAuthenticationFilter.class)
            
            // 특정 필터 위치에 추가 (기존 필터 대체)
            .addFilterAt(customFilter3, UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }
}

// 4. OncePerRequestFilter 사용 (권장)
@Component
@Slf4j
public class LoggingFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        long startTime = System.currentTimeMillis();
        
        log.info("Request: {} {}", request.getMethod(), request.getRequestURI());
        
        try {
            // 다음 필터 실행
            filterChain.doFilter(request, response);
        } finally {
            long duration = System.currentTimeMillis() - startTime;
            log.info("Response: {} ({}ms)", response.getStatus(), duration);
        }
    }
    
    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        // 특정 경로는 필터링 제외
        String path = request.getRequestURI();
        return path.startsWith("/public") || path.startsWith("/health");
    }
}

// 5. IP 체크 필터
public class IpCheckFilter extends OncePerRequestFilter {
    
    private final List<String> allowedIps = Arrays.asList(
        "127.0.0.1",
        "192.168.1.0/24"
    );
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        String clientIp = getClientIp(request);
        
        if (!isAllowedIp(clientIp)) {
            response.sendError(
                HttpServletResponse.SC_FORBIDDEN,
                "IP not allowed: " + clientIp
            );
            return;  // 체인 중단
        }
        
        filterChain.doFilter(request, response);
    }
    
    private String getClientIp(HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty()) {
            ip = request.getRemoteAddr();
        }
        return ip;
    }
}

// 6. Rate Limiting 필터
@Component
@RequiredArgsConstructor
public class RateLimitFilter extends OncePerRequestFilter {
    
    private final RateLimiter rateLimiter;
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        String clientId = getClientId(request);
        
        if (!rateLimiter.tryAcquire(clientId)) {
            response.sendError(
                HttpServletResponse.SC_TOO_MANY_REQUESTS,
                "Rate limit exceeded"
            );
            return;
        }
        
        filterChain.doFilter(request, response);
    }
    
    private String getClientId(HttpServletRequest request) {
        // IP 또는 사용자 ID
        Authentication auth = SecurityContextHolder.getContext()
                .getAuthentication();
        
        if (auth != null && auth.isAuthenticated()) {
            return auth.getName();
        }
        
        return request.getRemoteAddr();
    }
}

// 7. 요청/응답 로깅 필터
public class RequestResponseLoggingFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        // Request Wrapper로 Body 읽기 가능하게
        ContentCachingRequestWrapper requestWrapper = 
            new ContentCachingRequestWrapper(request);
        ContentCachingResponseWrapper responseWrapper = 
            new ContentCachingResponseWrapper(response);
        
        try {
            filterChain.doFilter(requestWrapper, responseWrapper);
        } finally {
            // 요청 로깅
            logRequest(requestWrapper);
            
            // 응답 로깅
            logResponse(responseWrapper);
            
            // 응답 복사 (중요!)
            responseWrapper.copyBodyToResponse();
        }
    }
    
    private void logRequest(ContentCachingRequestWrapper request) {
        String body = new String(request.getContentAsByteArray());
        log.info("Request Body: {}", body);
    }
    
    private void logResponse(ContentCachingResponseWrapper response) {
        String body = new String(response.getContentAsByteArray());
        log.info("Response Body: {}", body);
    }
}

// 8. CORS 필터 (Spring Security 이전)
public class CorsFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        response.setHeader("Access-Control-Allow-Origin", "*");
        response.setHeader("Access-Control-Allow-Methods", 
                          "GET, POST, PUT, DELETE, OPTIONS");
        response.setHeader("Access-Control-Allow-Headers", 
                          "Authorization, Content-Type");
        response.setHeader("Access-Control-Max-Age", "3600");
        
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            response.setStatus(HttpServletResponse.SC_OK);
            return;
        }
        
        filterChain.doFilter(request, response);
    }
}

// 9. 다중 SecurityFilterChain
@Configuration
@EnableWebSecurity
public class MultiSecurityConfig {
    
    // API 전용 필터 체인 (JWT)
    @Bean
    @Order(1)
    public SecurityFilterChain apiFilterChain(HttpSecurity http) throws Exception {
        http
            .securityMatcher("/api/**")
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
            .authorizeHttpRequests(auth -> auth
                .anyRequest().authenticated()
            );
        
        return http.build();
    }
    
    // 웹 전용 필터 체인 (Form Login)
    @Bean
    @Order(2)
    public SecurityFilterChain webFilterChain(HttpSecurity http) throws Exception {
        http
            .securityMatcher("/**")
            .formLogin(Customizer.withDefaults())
            .authorizeHttpRequests(auth -> auth
                .anyRequest().authenticated()
            );
        
        return http.build();
    }
}

// 10. 필터 체인 디버깅
@Component
@Slf4j
public class FilterChainDebugger implements Filter {
    
    @Override
    public void doFilter(
            ServletRequest request,
            ServletResponse response,
            FilterChain chain) throws IOException, ServletException {
        
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        
        log.debug("=== Filter Chain Start ===");
        log.debug("URI: {}", httpRequest.getRequestURI());
        log.debug("Method: {}", httpRequest.getMethod());
        
        // SecurityContext 확인
        Authentication auth = SecurityContextHolder.getContext()
                .getAuthentication();
        if (auth != null) {
            log.debug("Authenticated: {}", auth.getName());
            log.debug("Authorities: {}", auth.getAuthorities());
        } else {
            log.debug("Not authenticated");
        }
        
        chain.doFilter(request, response);
        
        log.debug("=== Filter Chain End ===");
    }
}

// 11. 필터 비활성화
@Configuration
public class DisableFilterConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // CSRF 필터 비활성화
            .csrf(csrf -> csrf.disable())
            
            // 세션 관리 비활성화 (Stateless)
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            
            // HTTP Basic 비활성화
            .httpBasic(basic -> basic.disable())
            
            // Form Login 비활성화
            .formLogin(form -> form.disable());
        
        return http.build();
    }
}

// 12. 필터 예외 처리
public class ExceptionHandlingFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        try {
            filterChain.doFilter(request, response);
            
        } catch (JwtException e) {
            // JWT 예외
            sendErrorResponse(response, 
                HttpServletResponse.SC_UNAUTHORIZED, 
                "Invalid token");
            
        } catch (AccessDeniedException e) {
            // 권한 없음
            sendErrorResponse(response, 
                HttpServletResponse.SC_FORBIDDEN, 
                "Access denied");
            
        } catch (Exception e) {
            // 기타 예외
            sendErrorResponse(response, 
                HttpServletResponse.SC_INTERNAL_SERVER_ERROR, 
                "Internal error");
        }
    }
    
    private void sendErrorResponse(
            HttpServletResponse response,
            int status,
            String message) throws IOException {
        
        response.setStatus(status);
        response.setContentType("application/json");
        response.getWriter().write(
            "{\"error\": \"" + message + "\"}"
        );
    }
}
```

## 주의사항 / 함정

### 1. 필터 체인 순서 중요
```java
// ❌ 인증 필터보다 인가 필터가 먼저 실행
.addFilterBefore(authorizationFilter, authenticationFilter)
// 인증 안 된 상태에서 인가 체크 → 실패!

// ✅ 인증 → 인가 순서
.addFilterAfter(authorizationFilter, authenticationFilter)
```

### 2. OncePerRequestFilter 미사용
```java
// ❌ Filter 직접 구현 → 요청당 여러 번 실행 가능
public class MyFilter implements Filter {
    @Override
    public void doFilter(...) {
        // Forward/Include 시 여러 번 실행!
    }
}

// ✅ OncePerRequestFilter 사용
public class MyFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(...) {
        // 요청당 1번만 실행 보장
    }
}
```

### 3. filterChain.doFilter() 호출 누락
```java
// ❌ 다음 필터 호출 안 함 → 요청 멈춤
@Override
public void doFilter(...) {
    // 검증 로직
    if (!isValid()) {
        return;  // 여기서 끝!
    }
    // filterChain.doFilter() 누락!
}

// ✅ 반드시 호출
filterChain.doFilter(request, response);
```

### 4. SecurityContext 설정 위치
```java
// ❌ SecurityContext 설정 후 filterChain 호출 안 함
Authentication auth = getAuthentication(token);
SecurityContextHolder.getContext().setAuthentication(auth);
return;  // 여기서 끝나면 Controller 실행 안 됨!

// ✅ 설정 후 체인 계속 진행
SecurityContextHolder.getContext().setAuthentication(auth);
filterChain.doFilter(request, response);
```

### 5. Response Body 중복 읽기
```java
// ❌ Response Body는 한 번만 읽을 수 있음
response.getWriter().write("error");
filterChain.doFilter(request, response);  // 에러!

// ✅ ContentCachingResponseWrapper 사용
ContentCachingResponseWrapper wrapper = 
    new ContentCachingResponseWrapper(response);
filterChain.doFilter(request, wrapper);
wrapper.copyBodyToResponse();  // 복사 필수
```

### 6. 필터에서 Bean 주입 문제
```java
// ❌ @Component 없이 new로 생성
.addFilterBefore(new MyFilter(), ...)
// MyFilter 내부의 @Autowired 동작 안 함!

// ✅ Bean으로 등록
@Bean
public MyFilter myFilter() {
    return new MyFilter();
}

.addFilterBefore(myFilter(), ...)
```

### 7. CORS 필터 순서
```java
// ❌ CORS 필터가 나중에 → OPTIONS 요청 차단
.addFilterAfter(corsFilter, SecurityFilter.class)

// ✅ CORS 필터를 가장 먼저
.addFilterBefore(corsFilter, SecurityContextPersistenceFilter.class)
```

## 관련 개념
- [[Spring-Security-아키텍처]]
- [[인증-흐름-Authentication]]
- [[JWT-토큰-기반-인증]]
- [[CORS-설정]]

## 면접 질문

1. **Spring Security의 필터 체인 동작 과정을 설명하세요.**
   - DelegatingFilterProxy → FilterChainProxy → SecurityFilterChain → 각 필터 순서대로 실행

2. **커스텀 필터를 추가하는 방법은?**
   - addFilterBefore, addFilterAfter, addFilterAt 사용
   - OncePerRequestFilter 상속 권장

3. **OncePerRequestFilter를 사용하는 이유는?**
   - 요청당 1번만 실행 보장
   - Forward/Include 시에도 중복 실행 방지

4. **필터 체인에서 요청을 중단하려면?**
   - filterChain.doFilter() 호출하지 않고 return
   - 또는 response.sendError() 후 return

5. **여러 SecurityFilterChain을 사용하는 이유는?**
   - API와 웹을 다르게 보안 설정
   - @Order로 우선순위 지정

6. **주요 Security 필터 3가지와 역할은?**
   - UsernamePasswordAuthenticationFilter: Form 로그인
   - BearerTokenAuthenticationFilter: JWT 인증
   - FilterSecurityInterceptor: 인가 처리

7. **필터와 인터셉터의 차이는?**
   - 필터: Servlet 레벨, DispatcherServlet 이전
   - 인터셉터: Spring 레벨, Controller 이전

## 참고 자료
- Spring Security Filter Chain Documentation
- Baeldung Custom Filters
- https://docs.spring.io/spring-security/reference/servlet/architecture.html
