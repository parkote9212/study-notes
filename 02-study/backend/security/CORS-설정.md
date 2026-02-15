---
tags:
  - study
  - spring
  - security
  - cors
  - cross-origin
created: 2025-02-08
---

# CORS 설정

## 한 줄 요약
> CORS(Cross-Origin Resource Sharing)는 다른 도메인의 리소스에 접근할 수 있도록 허용하는 메커니즘으로, Spring Security에서 특정 출처(Origin)의 요청만 허용하도록 설정하여 안전한 API 통신을 구현한다.

## 상세 설명

### CORS란?
- **Cross-Origin Resource Sharing**: 교차 출처 리소스 공유
- **브라우저 보안 정책**: Same-Origin Policy 완화
- **다른 도메인 API 호출** 허용

### 왜 CORS가 필요한가?
```javascript
// ❌ CORS 미설정 시
// 프론트엔드: http://localhost:3000
// 백엔드: http://localhost:8080
fetch('http://localhost:8080/api/users')
// ❌ CORS Error!

// ✅ CORS 설정 후
fetch('http://localhost:8080/api/users')
// ✅ 정상 응답
```

### Origin (출처)

```
https://example.com:8080/path?query=value

프로토콜: https
도메인: example.com
포트: 8080

→ Origin: https://example.com:8080
```

### Same-Origin vs Cross-Origin

| URL | Same-Origin? |
|-----|-------------|
| http://example.com:8080 | ✅ |
| http://example.com:8081 | ❌ (포트 다름) |
| https://example.com:8080 | ❌ (프로토콜 다름) |
| http://sub.example.com:8080 | ❌ (도메인 다름) |

### CORS 동작 흐름

```
1. 브라우저가 Preflight Request 전송 (OPTIONS)
   Origin: http://localhost:3000
   Access-Control-Request-Method: POST
   Access-Control-Request-Headers: Content-Type
   ↓
2. 서버가 CORS 헤더로 응답
   Access-Control-Allow-Origin: http://localhost:3000
   Access-Control-Allow-Methods: GET, POST, PUT, DELETE
   Access-Control-Allow-Headers: Content-Type, Authorization
   Access-Control-Max-Age: 3600
   ↓
3. 브라우저가 실제 요청 전송 (POST)
   ↓
4. 서버 응답
```

## 코드 예시

```java
// 1. Spring Security CORS 설정 (권장)
@Configuration
@EnableWebSecurity
public class CorsSecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .cors(Customizer.withDefaults())  // CORS 활성화
            .csrf(csrf -> csrf.disable());     // REST API는 CSRF 비활성화
        
        return http.build();
    }
    
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        
        // 허용할 Origin
        configuration.setAllowedOrigins(Arrays.asList(
            "http://localhost:3000",
            "http://localhost:3001",
            "https://example.com"
        ));
        
        // 허용할 HTTP 메서드
        configuration.setAllowedMethods(Arrays.asList(
            "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"
        ));
        
        // 허용할 헤더
        configuration.setAllowedHeaders(Arrays.asList(
            "Authorization",
            "Content-Type",
            "X-Requested-With"
        ));
        
        // 인증 정보 포함 허용
        configuration.setAllowCredentials(true);
        
        // Preflight 결과 캐시 시간 (초)
        configuration.setMaxAge(3600L);
        
        // 노출할 헤더 (클라이언트에서 읽을 수 있는 헤더)
        configuration.setExposedHeaders(Arrays.asList(
            "Authorization"
        ));
        
        UrlBasedCorsConfigurationSource source = 
            new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        
        return source;
    }
}

// 2. 모든 Origin 허용 (개발 환경용)
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration configuration = new CorsConfiguration();
    
    configuration.addAllowedOriginPattern("*");  // 모든 Origin 허용
    configuration.addAllowedMethod("*");         // 모든 메서드 허용
    configuration.addAllowedHeader("*");         // 모든 헤더 허용
    configuration.setAllowCredentials(true);
    
    UrlBasedCorsConfigurationSource source = 
        new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", configuration);
    
    return source;
}

// 3. 환경별 CORS 설정
@Configuration
public class CorsConfig {
    
    @Value("${cors.allowed-origins}")
    private String[] allowedOrigins;
    
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        
        // 환경변수로 관리
        configuration.setAllowedOrigins(Arrays.asList(allowedOrigins));
        configuration.setAllowedMethods(Arrays.asList("*"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = 
            new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        
        return source;
    }
}

// application-dev.yml
// cors:
//   allowed-origins: http://localhost:3000,http://localhost:3001

// application-prod.yml
// cors:
//   allowed-origins: https://example.com,https://www.example.com

// 4. @CrossOrigin 어노테이션 (Controller 레벨)
@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "http://localhost:3000")
public class UserController {
    
    @GetMapping
    public List<User> getUsers() {
        return userService.findAll();
    }
}

// 5. @CrossOrigin (메서드 레벨)
@RestController
@RequestMapping("/api/posts")
public class PostController {
    
    @CrossOrigin(
        origins = "http://localhost:3000",
        methods = {RequestMethod.GET, RequestMethod.POST},
        allowedHeaders = {"Authorization", "Content-Type"},
        exposedHeaders = {"X-Total-Count"},
        allowCredentials = "true",
        maxAge = 3600
    )
    @GetMapping
    public List<Post> getPosts() {
        return postService.findAll();
    }
}

// 6. WebMvcConfigurer로 CORS 설정 (전역)
@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("http://localhost:3000")
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
        
        // 다른 경로는 다른 설정
        registry.addMapping("/public/**")
                .allowedOrigins("*")
                .allowedMethods("GET");
    }
}

// 7. CORS 필터 (가장 먼저 실행)
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class CorsFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        String origin = request.getHeader("Origin");
        
        // 허용할 Origin 체크
        if (isAllowedOrigin(origin)) {
            response.setHeader("Access-Control-Allow-Origin", origin);
            response.setHeader("Access-Control-Allow-Methods", 
                              "GET, POST, PUT, DELETE, OPTIONS");
            response.setHeader("Access-Control-Allow-Headers", 
                              "Authorization, Content-Type");
            response.setHeader("Access-Control-Allow-Credentials", "true");
            response.setHeader("Access-Control-Max-Age", "3600");
        }
        
        // Preflight 요청 처리
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            response.setStatus(HttpServletResponse.SC_OK);
            return;
        }
        
        filterChain.doFilter(request, response);
    }
    
    private boolean isAllowedOrigin(String origin) {
        List<String> allowedOrigins = Arrays.asList(
            "http://localhost:3000",
            "https://example.com"
        );
        return allowedOrigins.contains(origin);
    }
}

// 8. 동적 Origin 검증
@Component
public class DynamicCorsConfigurationSource 
        implements CorsConfigurationSource {
    
    @Autowired
    private AllowedOriginRepository allowedOriginRepository;
    
    @Override
    public CorsConfiguration getCorsConfiguration(HttpServletRequest request) {
        String origin = request.getHeader("Origin");
        
        // DB에서 허용된 Origin 조회
        if (isOriginAllowed(origin)) {
            CorsConfiguration config = new CorsConfiguration();
            config.addAllowedOrigin(origin);
            config.addAllowedMethod("*");
            config.addAllowedHeader("*");
            config.setAllowCredentials(true);
            return config;
        }
        
        return null;  // 허용되지 않음
    }
    
    private boolean isOriginAllowed(String origin) {
        return allowedOriginRepository.existsByOrigin(origin);
    }
}

// 9. Credentials 포함 요청 (쿠키, 인증 헤더)
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration configuration = new CorsConfiguration();
    
    // allowCredentials: true 시
    // allowedOrigins에 "*" 사용 불가!
    configuration.setAllowedOrigins(Arrays.asList(
        "http://localhost:3000"  // 명시적으로 지정
    ));
    
    configuration.setAllowCredentials(true);  // 쿠키 허용
    
    // ...
}

// 프론트엔드 (JavaScript)
// fetch('http://localhost:8080/api/users', {
//   credentials: 'include'  // 쿠키 포함
// });

// 10. CORS Preflight 최적화
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration configuration = new CorsConfiguration();
    
    // ...
    
    // Preflight 결과를 1시간 캐시
    configuration.setMaxAge(3600L);
    // → 1시간 동안 Preflight 요청 안 보냄
    
    UrlBasedCorsConfigurationSource source = 
        new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", configuration);
    
    return source;
}

// 11. 경로별 다른 CORS 설정
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    UrlBasedCorsConfigurationSource source = 
        new UrlBasedCorsConfigurationSource();
    
    // /api/** → 인증 필요
    CorsConfiguration apiConfig = new CorsConfiguration();
    apiConfig.setAllowedOrigins(Arrays.asList("http://localhost:3000"));
    apiConfig.setAllowedMethods(Arrays.asList("*"));
    apiConfig.setAllowedHeaders(Arrays.asList("*"));
    apiConfig.setAllowCredentials(true);
    source.registerCorsConfiguration("/api/**", apiConfig);
    
    // /public/** → 모든 Origin 허용
    CorsConfiguration publicConfig = new CorsConfiguration();
    publicConfig.addAllowedOriginPattern("*");
    publicConfig.setAllowedMethods(Arrays.asList("GET"));
    source.registerCorsConfiguration("/public/**", publicConfig);
    
    return source;
}

// 12. CORS 오류 디버깅
@RestControllerAdvice
public class CorsErrorHandler {
    
    @ExceptionHandler(CorsException.class)
    public ResponseEntity<ErrorResponse> handleCorsError(
            CorsException e,
            HttpServletRequest request) {
        
        String origin = request.getHeader("Origin");
        log.error("CORS Error - Origin: {}, Message: {}", origin, e.getMessage());
        
        return ResponseEntity
                .status(HttpStatus.FORBIDDEN)
                .body(new ErrorResponse("CORS policy violation"));
    }
}
```

## 주의사항 / 함정

### 1. allowCredentials + allowedOrigins("*")
```java
// ❌ 동시 사용 불가
configuration.setAllowedOrigins(Arrays.asList("*"));
configuration.setAllowCredentials(true);
// Error!

// ✅ 명시적 Origin 지정
configuration.setAllowedOrigins(Arrays.asList("http://localhost:3000"));
configuration.setAllowCredentials(true);
```

### 2. CORS 순서 문제
```java
// ❌ Security Filter가 먼저 → CORS 차단
http
    .authorizeRequests()
    .anyRequest().authenticated()
    .and()
    .cors();  // 늦음!

// ✅ CORS가 먼저
http
    .cors(Customizer.withDefaults())
    .authorizeRequests()
    .anyRequest().authenticated();
```

### 3. Preflight OPTIONS 차단
```java
// ❌ OPTIONS도 인증 필요
http.authorizeRequests()
    .anyRequest().authenticated();
// Preflight 차단!

// ✅ OPTIONS 허용
http.authorizeRequests()
    .requestMatchers(HttpMethod.OPTIONS).permitAll()
    .anyRequest().authenticated();
```

### 4. exposedHeaders 누락
```java
// ❌ 응답 헤더를 클라이언트가 못 읽음
response.setHeader("X-Total-Count", "100");
// JavaScript에서 읽을 수 없음!

// ✅ exposedHeaders 설정
configuration.setExposedHeaders(Arrays.asList("X-Total-Count"));
```

### 5. 프로덕션에서 모든 Origin 허용
```java
// ❌ 프로덕션에서 "*" 사용
configuration.addAllowedOriginPattern("*");
// 보안 취약!

// ✅ 명시적 Origin만 허용
configuration.setAllowedOrigins(Arrays.asList(
    "https://example.com"
));
```

### 6. http vs https 혼용
```
// ❌ 프로토콜 불일치
프론트엔드: https://example.com
백엔드: http://api.example.com
// CORS 에러!

// ✅ 프로토콜 통일
둘 다 https 사용
```

### 7. 로컬 개발 시 포트 변경
```java
// ❌ 하드코딩된 포트
configuration.setAllowedOrigins(Arrays.asList(
    "http://localhost:3000"
));
// 포트 변경 시 수정 필요

// ✅ 환경변수 사용
configuration.setAllowedOrigins(Arrays.asList(
    allowedOrigins  // application.yml에서 관리
));
```

## 관련 개념
- [[Spring-Security-아키텍처]]
- [[필터체인-FilterChain]]
- [[JWT-토큰-기반-인증]]

## 면접 질문

1. **CORS란 무엇인가요?**
   - Cross-Origin Resource Sharing
   - 다른 도메인의 리소스 접근 허용
   - Same-Origin Policy 완화

2. **Same-Origin이 아닌 경우는?**
   - 프로토콜, 도메인, 포트 중 하나라도 다르면 Cross-Origin

3. **Preflight Request란?**
   - 실제 요청 전 OPTIONS 요청으로 CORS 확인
   - 서버가 허용하면 실제 요청 전송

4. **allowCredentials의 역할은?**
   - 쿠키, 인증 헤더 포함 허용
   - true 시 allowedOrigins("*") 불가

5. **CORS 설정 방법 3가지는?**
   - SecurityFilterChain + CorsConfigurationSource (권장)
   - @CrossOrigin 어노테이션
   - WebMvcConfigurer

6. **OPTIONS 요청이 차단되는 이유는?**
   - Spring Security가 인증 요구
   - OPTIONS는 permitAll() 필요

7. **exposedHeaders의 용도는?**
   - 클라이언트가 읽을 수 있는 응답 헤더 지정
   - 기본적으로 일부 헤더만 노출

## 참고 자료
- MDN CORS Documentation
- Spring Security CORS Reference
- https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
