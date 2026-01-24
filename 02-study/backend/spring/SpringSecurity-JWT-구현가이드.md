---
tags:
  - study
  - security
  - spring
  - jwt
  - springsecurity
  - 필터
created: 2026-01-23
difficulty: 상
---
# SpringSecurity-JWT-구현가이드

🏷️기술 카테고리: Security, Spring
💡핵심키워드: #JWT, #SpringSecurity, #필터
💼 면접 빈출도: 상

# 1. Abstract: 핵심 요약

Spring Security와 JWT를 결합하여 **Stateless REST API 인증 시스템**을 구축합니다. JWT 필터를 Security Filter Chain에 추가하여 토큰 기반 인증을 처리합니다.

**핵심 구성요소**:
- JwtTokenProvider: JWT 생성/검증
- JwtAuthenticationFilter: 요청마다 토큰 검증
- SecurityConfig: JWT 방식으로 설정
- AuthController: 로그인/토큰 재발급 API

# 2. 구현 단계

## Step 1: 의존성 추가

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-security'
    implementation 'io.jsonwebtoken:jjwt-api:0.12.3'
    runtimeOnly 'io.jsonwebtoken:jjwt-impl:0.12.3'
    runtimeOnly 'io.jsonwebtoken:jjwt-jackson:0.12.3'
}
```

## Step 2: JWT 설정

```yaml
jwt:
  secret: ${JWT_SECRET}
  access-token-validity: 900000      # 15분
  refresh-token-validity: 604800000  # 7일
```

## Step 3: JwtTokenProvider

```java
@Component
public class JwtTokenProvider {

    private final SecretKey secretKey;
    private final long accessTokenValidity;

    public JwtTokenProvider(
        @Value("${jwt.secret}") String secret,
        @Value("${jwt.access-token-validity}") long accessValidity) {
        
        this.secretKey = Keys.hmacShaKeyFor(Decoders.BASE64.decode(secret));
        this.accessTokenValidity = accessValidity;
    }

    // Access Token 생성
    public String createAccessToken(Authentication authentication) {
        String authorities = authentication.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .collect(Collectors.joining(","));

        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + accessTokenValidity);

        return Jwts.builder()
            .subject(authentication.getName())
            .claim("auth", authorities)
            .issuedAt(now)
            .expiration(expiryDate)
            .signWith(secretKey)
            .compact();
    }

    // 토큰에서 인증 정보 추출
    public Authentication getAuthentication(String token) {
        Claims claims = parseClaims(token);
        
        Collection<? extends GrantedAuthority> authorities =
            Arrays.stream(claims.get("auth").toString().split(","))
                .map(SimpleGrantedAuthority::new)
                .collect(Collectors.toList());

        UserDetails principal = new User(
            claims.getSubject(), "", authorities);
        
        return new UsernamePasswordAuthenticationToken(
            principal, token, authorities);
    }

    // 토큰 검증
    public boolean validateToken(String token) {
        try {
            parseClaims(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    private Claims parseClaims(String token) {
        return Jwts.parser()
            .verifyWith(secretKey)
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }
}
```

## Step 4: JwtAuthenticationFilter

```java
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtTokenProvider jwtTokenProvider;

    @Override
    protected void doFilterInternal(
        HttpServletRequest request,
        HttpServletResponse response,
        FilterChain filterChain) throws ServletException, IOException {
        
        // 1. 헤더에서 JWT 추출
        String token = resolveToken(request);
        
        // 2. 토큰 검증
        if (token != null && jwtTokenProvider.validateToken(token)) {
            // 3. 인증 정보 생성
            Authentication auth = jwtTokenProvider.getAuthentication(token);
            
            // 4. SecurityContext에 저장
            SecurityContextHolder.getContext().setAuthentication(auth);
        }
        
        filterChain.doFilter(request, response);
    }

    private String resolveToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
```

## Step 5: SecurityConfig

```java
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(
                jwtAuthenticationFilter,
                UsernamePasswordAuthenticationFilter.class
            );

        return http.build();
    }
}
```

## Step 6: AuthController

```java
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;

    @PostMapping("/login")
    public ResponseEntity<TokenResponse> login(@RequestBody LoginRequest request) {
        // 1. 인증 처리
        Authentication authentication = authenticationManager
            .authenticate(new UsernamePasswordAuthenticationToken(
                request.getUsername(),
                request.getPassword()
            ));

        // 2. 토큰 생성
        String accessToken = jwtTokenProvider.createAccessToken(authentication);

        return ResponseEntity.ok(new TokenResponse(accessToken));
    }
}
```

# 3. Refresh Token 관리

```java
@Entity
public class RefreshToken {
    @Id @GeneratedValue
    private Long id;
    private String username;
    private String token;
    private LocalDateTime expiryDate;
}

@PostMapping("/refresh")
public ResponseEntity<TokenResponse> refresh(@RequestBody TokenRefreshRequest request) {
    String refreshToken = request.getRefreshToken();

    // 1. Refresh Token 검증
    if (!jwtTokenProvider.validateToken(refreshToken)) {
        throw new InvalidTokenException();
    }

    // 2. DB에서 확인
    if (!refreshTokenService.exists(refreshToken)) {
        throw new InvalidTokenException();
    }

    // 3. 새로운 Access Token 발급
    Authentication auth = jwtTokenProvider.getAuthentication(refreshToken);
    String newAccessToken = jwtTokenProvider.createAccessToken(auth);

    return ResponseEntity.ok(new TokenResponse(newAccessToken));
}
```

# 4. Interview Readiness

## Q: JWT 필터는 왜 UsernamePasswordAuthenticationFilter 이전에 추가하나요?

**A**: JWT 필터가 먼저 실행되어 토큰을 검증하고 SecurityContext에 인증 정보를 저장하면, 이후 필터들은 이미 인증된 것으로 간주합니다. UsernamePasswordAuthenticationFilter는 폼 로그인용이므로 JWT 방식에서는 실행될 필요가 없습니다.

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐ (상)
