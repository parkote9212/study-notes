---
tags:
  - study
  - spring
  - security
  - jwt
  - token
created: 2025-02-08
---

# JWT 토큰 기반 인증

## 한 줄 요약
> JWT(JSON Web Token)는 JSON 형식의 자가 검증 가능한 토큰으로, 서버가 상태를 저장하지 않는(Stateless) RESTful API 인증에 사용되며, Header.Payload.Signature 구조로 사용자 정보와 권한을 안전하게 전달한다.

## 상세 설명

### JWT란?
- **JSON Web Token**: JSON 기반 토큰
- **Stateless**: 서버가 세션 저장 안 함
- **자가 검증**: 토큰 자체에 정보 포함

### 왜 JWT가 필요한가?
```java
// ❌ 세션 기반: 서버에 세션 저장 (Stateful)
@PostMapping("/login")
public String login(HttpSession session) {
    session.setAttribute("user", user);  // 서버 메모리 사용
    // 서버 확장 시 세션 공유 문제!
}

// ✅ JWT 기반: 토큰만 주고받음 (Stateless)
@PostMapping("/login")
public TokenResponse login() {
    String token = jwtProvider.createToken(user);
    return new TokenResponse(token);  // 서버는 저장 안 함
}
```

### JWT 구조

```
Header.Payload.Signature

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### JWT 구성 요소

| 부분 | 설명 | 예시 |
|-----|------|------|
| **Header** | 알고리즘, 토큰 타입 | {"alg": "HS256", "typ": "JWT"} |
| **Payload** | 사용자 정보, 권한, 만료시간 | {"sub": "user123", "role": "ADMIN"} |
| **Signature** | 변조 방지 서명 | HMACSHA256(header.payload, secret) |

### Payload 클레임(Claim)

```json
{
  // 등록된 클레임 (Registered)
  "iss": "issuer",           // 발급자
  "sub": "user123",          // 주체 (사용자 ID)
  "aud": "audience",         // 대상
  "exp": 1735689600,         // 만료 시간
  "iat": 1735686000,         // 발급 시간
  
  // 커스텀 클레임 (Private)
  "username": "john",
  "role": "ADMIN",
  "email": "john@example.com"
}
```

### JWT 인증 흐름

```
1. 클라이언트 로그인 (username, password)
   ↓
2. 서버 인증 성공 → JWT 토큰 발급
   ↓
3. 클라이언트 토큰 저장 (LocalStorage, Cookie)
   ↓
4. API 요청 시 Header에 토큰 포함
   Authorization: Bearer eyJhbGc...
   ↓
5. 서버에서 토큰 검증
   - 서명 확인
   - 만료 시간 확인
   - 사용자 정보 추출
   ↓
6. SecurityContext에 Authentication 저장
   ↓
7. Controller 실행
```

## 코드 예시

```java
// 1. JWT 의존성
// build.gradle
// implementation 'io.jsonwebtoken:jjwt-api:0.12.3'
// runtimeOnly 'io.jsonwebtoken:jjwt-impl:0.12.3'
// runtimeOnly 'io.jsonwebtoken:jjwt-jackson:0.12.3'

// 2. JWT Provider (토큰 생성/검증)
@Component
public class JwtProvider {
    
    @Value("${jwt.secret}")
    private String secretKey;
    
    @Value("${jwt.expiration:3600000}")  // 1시간
    private long expirationTime;
    
    private Key key;
    
    @PostConstruct
    public void init() {
        // SecretKey 초기화
        byte[] keyBytes = Decoders.BASE64.decode(secretKey);
        this.key = Keys.hmacShaKeyFor(keyBytes);
    }
    
    // 토큰 생성
    public String createToken(Authentication authentication) {
        String username = authentication.getName();
        Collection<? extends GrantedAuthority> authorities = 
            authentication.getAuthorities();
        
        // 권한을 문자열로 변환
        String roles = authorities.stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.joining(","));
        
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expirationTime);
        
        return Jwts.builder()
                .setSubject(username)
                .claim("roles", roles)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(key, SignatureAlgorithm.HS256)
                .compact();
    }
    
    // 토큰에서 사용자 이름 추출
    public String getUsername(String token) {
        Claims claims = parseClaims(token);
        return claims.getSubject();
    }
    
    // 토큰에서 권한 추출
    public Collection<? extends GrantedAuthority> getAuthorities(String token) {
        Claims claims = parseClaims(token);
        String roles = claims.get("roles", String.class);
        
        return Arrays.stream(roles.split(","))
                .map(SimpleGrantedAuthority::new)
                .collect(Collectors.toList());
    }
    
    // 토큰 검증
    public boolean validateToken(String token) {
        try {
            parseClaims(token);
            return true;
        } catch (SecurityException | MalformedJwtException e) {
            log.error("잘못된 JWT 서명");
        } catch (ExpiredJwtException e) {
            log.error("만료된 JWT 토큰");
        } catch (UnsupportedJwtException e) {
            log.error("지원되지 않는 JWT 토큰");
        } catch (IllegalArgumentException e) {
            log.error("JWT 토큰이 잘못됨");
        }
        return false;
    }
    
    // Claims 파싱
    private Claims parseClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }
}

// 3. JWT 인증 필터
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    private final JwtProvider jwtProvider;
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        // 1. 토큰 추출
        String token = resolveToken(request);
        
        // 2. 토큰 검증
        if (token != null && jwtProvider.validateToken(token)) {
            // 3. 사용자 정보 추출
            String username = jwtProvider.getUsername(token);
            Collection<? extends GrantedAuthority> authorities = 
                jwtProvider.getAuthorities(token);
            
            // 4. Authentication 생성
            Authentication authentication = 
                new UsernamePasswordAuthenticationToken(
                    username, null, authorities
                );
            
            // 5. SecurityContext에 저장
            SecurityContextHolder.getContext().setAuthentication(authentication);
        }
        
        // 6. 다음 필터로
        filterChain.doFilter(request, response);
    }
    
    // Authorization 헤더에서 토큰 추출
    private String resolveToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        
        return null;
    }
}

// 4. Security 설정 (Stateless)
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class JwtSecurityConfig {
    
    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // CSRF 비활성화 (Stateless이므로 불필요)
            .csrf(csrf -> csrf.disable())
            
            // 세션 사용 안 함
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            
            // JWT 필터 추가
            .addFilterBefore(
                jwtAuthenticationFilter,
                UsernamePasswordAuthenticationFilter.class
            )
            
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .anyRequest().authenticated()
            );
        
        return http.build();
    }
}

// 5. 로그인 API
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {
    
    private final AuthenticationManager authenticationManager;
    private final JwtProvider jwtProvider;
    
    @PostMapping("/login")
    public ResponseEntity<TokenResponse> login(@RequestBody LoginRequest request) {
        try {
            // 1. 인증
            Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                    request.getUsername(),
                    request.getPassword()
                )
            );
            
            // 2. JWT 토큰 생성
            String token = jwtProvider.createToken(authentication);
            
            // 3. 응답
            return ResponseEntity.ok(new TokenResponse(token));
            
        } catch (BadCredentialsException e) {
            throw new UnauthorizedException("Invalid credentials");
        }
    }
}

@Data
public class LoginRequest {
    private String username;
    private String password;
}

@Data
@AllArgsConstructor
public class TokenResponse {
    private String accessToken;
    private String tokenType = "Bearer";
    
    public TokenResponse(String accessToken) {
        this.accessToken = accessToken;
    }
}

// 6. 현재 사용자 정보 가져오기
@RestController
@RequestMapping("/api/user")
public class UserController {
    
    @GetMapping("/me")
    public ResponseEntity<UserDto> getCurrentUser(Authentication authentication) {
        // JWT에서 추출한 username
        String username = authentication.getName();
        
        // authorities
        Collection<? extends GrantedAuthority> authorities = 
            authentication.getAuthorities();
        
        return ResponseEntity.ok(new UserDto(username, authorities));
    }
}

// 7. 커스텀 Claims 추가
@Component
public class CustomJwtProvider {
    
    public String createToken(User user) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", user.getId());
        claims.put("email", user.getEmail());
        claims.put("role", user.getRole());
        
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expirationTime);
        
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(user.getUsername())
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(key)
                .compact();
    }
    
    public Long getUserId(String token) {
        Claims claims = parseClaims(token);
        return claims.get("userId", Long.class);
    }
}

// 8. 토큰 만료 처리
@Component
public class JwtAuthenticationEntryPoint implements AuthenticationEntryPoint {
    
    @Override
    public void commence(
            HttpServletRequest request,
            HttpServletResponse response,
            AuthenticationException authException) throws IOException {
        
        response.setContentType("application/json");
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        
        Map<String, Object> error = new HashMap<>();
        error.put("error", "Unauthorized");
        error.put("message", "JWT token is missing or invalid");
        
        ObjectMapper mapper = new ObjectMapper();
        response.getWriter().write(mapper.writeValueAsString(error));
    }
}

// Security 설정에 추가
http.exceptionHandling(exception -> exception
    .authenticationEntryPoint(jwtAuthenticationEntryPoint)
);

// 9. 토큰 블랙리스트 (로그아웃)
@Service
@RequiredArgsConstructor
public class TokenBlacklistService {
    
    private final RedisTemplate<String, String> redisTemplate;
    private final JwtProvider jwtProvider;
    
    public void addToBlacklist(String token) {
        // 토큰 만료 시간 가져오기
        Claims claims = jwtProvider.parseClaims(token);
        Date expiration = claims.getExpiration();
        
        long ttl = expiration.getTime() - System.currentTimeMillis();
        
        // Redis에 저장 (TTL 설정)
        redisTemplate.opsForValue().set(
            "blacklist:" + token,
            "true",
            ttl,
            TimeUnit.MILLISECONDS
        );
    }
    
    public boolean isBlacklisted(String token) {
        return redisTemplate.hasKey("blacklist:" + token);
    }
}

// 필터에서 블랙리스트 체크
if (token != null && jwtProvider.validateToken(token)) {
    if (tokenBlacklistService.isBlacklisted(token)) {
        response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Token is invalidated");
        return;
    }
    // ...
}

// 10. 로그아웃 API
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {
    
    private final TokenBlacklistService tokenBlacklistService;
    
    @PostMapping("/logout")
    public ResponseEntity<Void> logout(HttpServletRequest request) {
        String token = resolveToken(request);
        
        if (token != null) {
            tokenBlacklistService.addToBlacklist(token);
        }
        
        return ResponseEntity.ok().build();
    }
    
    private String resolveToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}

// 11. 토큰 갱신 (Access Token 재발급)
@PostMapping("/refresh")
public ResponseEntity<TokenResponse> refresh(
        @RequestHeader("Authorization") String bearerToken) {
    
    String token = bearerToken.substring(7);
    
    if (jwtProvider.validateToken(token)) {
        String username = jwtProvider.getUsername(token);
        Collection<? extends GrantedAuthority> authorities = 
            jwtProvider.getAuthorities(token);
        
        // 새 토큰 생성
        Authentication authentication = 
            new UsernamePasswordAuthenticationToken(username, null, authorities);
        String newToken = jwtProvider.createToken(authentication);
        
        return ResponseEntity.ok(new TokenResponse(newToken));
    }
    
    throw new UnauthorizedException("Invalid token");
}

// 12. UserDetails 기반 토큰 생성
@Component
@RequiredArgsConstructor
public class UserDetailsJwtProvider {
    
    private final UserDetailsService userDetailsService;
    
    public Authentication getAuthentication(String token) {
        String username = getUsername(token);
        
        // UserDetailsService로 사용자 정보 조회
        UserDetails userDetails = userDetailsService.loadUserByUsername(username);
        
        return new UsernamePasswordAuthenticationToken(
            userDetails,
            "",
            userDetails.getAuthorities()
        );
    }
}
```

## 주의사항 / 함정

### 1. Secret Key 노출
```java
// ❌ 하드코딩된 Secret Key
private String secretKey = "mySecretKey123";

// ✅ 환경변수 사용
@Value("${jwt.secret}")
private String secretKey;

// application.yml에서도 환경변수
// jwt:
//   secret: ${JWT_SECRET}
```

### 2. 약한 Secret Key
```java
// ❌ 짧은 키 → 보안 취약
String secret = "secret";

// ✅ 최소 256비트 (32바이트) 이상
String secret = "myVeryLongSecretKeyThatIsAtLeast256BitsLong12345678";

// 또는 랜덤 생성
Key key = Keys.secretKeyFor(SignatureAlgorithm.HS256);
String encodedKey = Encoders.BASE64.encode(key.getEncoded());
```

### 3. 토큰 만료 시간 미설정
```java
// ❌ 만료 시간 없음 → 영구 유효
Jwts.builder()
    .setSubject(username)
    .signWith(key)
    .compact();

// ✅ 만료 시간 설정 (1시간)
Date expiryDate = new Date(System.currentTimeMillis() + 3600000);
Jwts.builder()
    .setExpiration(expiryDate)
```

### 4. 민감 정보 Payload에 저장
```java
// ❌ 비밀번호를 Payload에 저장
.claim("password", user.getPassword())  // JWT는 디코딩 가능!

// ✅ 민감 정보 제외
.claim("userId", user.getId())
.claim("role", user.getRole())
```

### 5. CSRF 보호 유지
```java
// ❌ JWT 사용 시에도 CSRF 활성화
http.csrf(Customizer.withDefaults());  // LocalStorage 사용 시 불필요

// ✅ Stateless API는 CSRF 비활성화
http.csrf(csrf -> csrf.disable());
```

### 6. 토큰 검증 누락
```java
// ❌ 토큰 검증 없이 바로 사용
String username = jwtProvider.getUsername(token);  // 위험!

// ✅ 검증 후 사용
if (jwtProvider.validateToken(token)) {
    String username = jwtProvider.getUsername(token);
}
```

### 7. 로그아웃 처리 안 함
```java
// ❌ JWT는 서버에 상태 저장 안 함 → 로그아웃 불가
// 토큰이 만료될 때까지 유효함!

// ✅ 블랙리스트 사용
tokenBlacklistService.addToBlacklist(token);
```

## 관련 개념
- [[Spring-Security-아키텍처]]
- [[인증-흐름-Authentication]]
- [[필터체인-FilterChain]]
- [[리프레시-토큰-전략]]

## 면접 질문

1. **JWT의 장점과 단점은?**
   - 장점: Stateless, 확장성, 서버 부하 감소
   - 단점: 토큰 크기, 강제 만료 어려움, Secret Key 관리

2. **JWT 구조 3가지는?**
   - Header: 알고리즘, 타입
   - Payload: 사용자 정보, 클레임
   - Signature: 변조 방지 서명

3. **Session 방식과 JWT 방식의 차이는?**
   - Session: Stateful, 서버 메모리 사용
   - JWT: Stateless, 토큰에 정보 포함

4. **JWT를 어디에 저장하나요?**
   - LocalStorage: XSS 위험
   - Cookie (httpOnly, secure): CSRF 위험
   - 상황에 따라 선택

5. **로그아웃은 어떻게 구현하나요?**
   - 블랙리스트: Redis 등에 토큰 저장
   - 만료 시간까지 유효하므로 강제 만료 필요

6. **JWT Secret Key는 어떻게 관리하나요?**
   - 환경변수 사용
   - 최소 256비트 이상
   - 주기적 변경

7. **Access Token vs Refresh Token?**
   - Access: 짧은 만료 시간 (1시간)
   - Refresh: 긴 만료 시간 (1주일), Access 재발급용

## 참고 자료
- JWT.io
- JJWT Library Documentation
- https://jwt.io/introduction
