---
tags: interview, spring-security, jwt, bizsync
created: 2026-01-23
difficulty: 중상
---

# BizSync - Spring Security + JWT 인증 면접질문

## 질문 1
> BizSync에서 JWT 기반 인증을 구현할 때 Access Token과 Refresh Token을 분리한 이유는 무엇인가요?

## 핵심 답변 (3줄)
1. Access Token은 짧은 만료시간(1시간)으로 보안성을 높이고, Refresh Token은 긴 만료시간(7일)으로 사용자 편의성을 제공합니다
2. Access Token이 탈취되어도 피해 범위를 제한할 수 있고, Refresh Token으로 재발급하여 지속적인 로그인 상태를 유지할 수 있습니다
3. Stateless 아키텍처를 유지하면서도 토큰 갱신 메커니즘을 통해 보안과 UX의 균형을 맞출 수 있습니다

## 상세 설명
BizSync 프로젝트에서는 JWT 토큰을 Access Token과 Refresh Token으로 분리하여 구현했습니다. Access Token은 API 요청 시 인증에 사용되며 1시간의 짧은 만료시간을 가집니다. 반면 Refresh Token은 7일의 긴 만료시간을 가지며 Access Token 재발급에만 사용됩니다.

이러한 설계의 핵심은 보안과 사용성의 균형입니다. Access Token의 짧은 수명은 토큰이 탈취되더라도 공격자가 사용할 수 있는 시간을 제한합니다. 동시에 Refresh Token을 통해 사용자가 매번 로그인할 필요 없이 자동으로 Access Token을 갱신받을 수 있어 사용자 경험을 개선합니다.

JwtProvider 클래스에서 각 토큰의 타입을 claim에 명시("access", "refresh")하여 구분하고, 토큰 검증 시 isAccessToken()과 isRefreshToken() 메서드로 타입을 확인합니다.

## 코드 예시 (필요시)
```java
// JwtProvider.java
public String createToken(Long userId, Role role) {
    Date now = new Date();
    Date expirationDate = new Date(now.getTime() + expiration); // 1시간
    
    return Jwts.builder()
            .setSubject(String.valueOf(userId))
            .claim("role", role.name())
            .claim("type", "access")  // 토큰 타입 명시
            .setIssuedAt(now)
            .setExpiration(expirationDate)
            .signWith(secretKey, SignatureAlgorithm.HS256)
            .compact();
}

public String createRefreshToken(Long userId) {
    Date now = new Date();
    Date expirationDate = new Date(now.getTime() + refreshExpiration); // 7일
    
    return Jwts.builder()
            .setSubject(String.valueOf(userId))
            .claim("type", "refresh")  // Refresh 토큰 표시
            .setIssuedAt(now)
            .setExpiration(expirationDate)
            .signWith(secretKey, SignatureAlgorithm.HS256)
            .compact();
}
```

## 꼬리 질문 예상
- Refresh Token을 어디에 저장하는 것이 안전한가요? (쿠키 vs LocalStorage)
- Refresh Token도 탈취될 수 있는데, 이를 방지하기 위한 추가 보안 전략은 무엇인가요?
- RTR (Refresh Token Rotation) 방식을 적용한다면 어떻게 구현하시겠습니까?

## 참고
- [[Spring Security 인증 아키텍처]]
- [[JWT 토큰 보안 베스트 프랙티스]]

---

## 질문 2
> SecurityConfig에서 SessionCreationPolicy를 STATELESS로 설정한 이유와 이것이 JWT 인증에 미치는 영향을 설명해주세요.

## 핵심 답변 (3줄)
1. STATELESS 정책은 서버가 세션을 생성하거나 유지하지 않아 서버 메모리 부담을 줄이고 수평 확장이 용이합니다
2. JWT는 자체적으로 인증 정보를 포함하므로 서버 측 세션 저장소가 필요 없어 Stateless 아키텍처와 완벽하게 호환됩니다
3. 로드 밸런서 뒤에 여러 인스턴스가 있어도 세션 공유 문제 없이 어느 서버든 요청을 처리할 수 있습니다

## 상세 설명
Spring Security의 SessionCreationPolicy.STATELESS는 서버가 HTTP 세션을 생성하지 않도록 지시합니다. 전통적인 세션 기반 인증에서는 서버가 세션 ID를 쿠키로 클라이언트에 전달하고, 서버 메모리나 세션 저장소에 사용자 정보를 보관합니다. 하지만 이는 서버의 메모리를 소비하고, 다중 서버 환경에서 세션 동기화 문제를 야기합니다.

BizSync에서는 JWT를 사용하므로 모든 인증 정보가 토큰 자체에 포함됩니다. 서버는 토큰의 서명만 검증하면 되므로 별도의 세션 저장이 불필요합니다. 이로 인해 서버 인스턴스를 자유롭게 추가하거나 제거할 수 있으며, 특정 서버에 종속되지 않는 진정한 RESTful API를 구현할 수 있습니다.

## 코드 예시 (필요시)
```java
// SecurityConfig.java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .csrf(AbstractHttpConfigurer::disable)
        .sessionManagement(session -> session.sessionCreationPolicy(
            SessionCreationPolicy.STATELESS))  // 세션 미사용
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/auth/**").permitAll()
            .anyRequest().authenticated()
        )
        .addFilterBefore(jwtAuthenticationFilter, 
            UsernamePasswordAuthenticationFilter.class);
    
    return http.build();
}
```

## 꼬리 질문 예상
- Stateless 방식의 단점은 무엇이며, 어떻게 보완할 수 있나요?
- 로그아웃 기능을 구현할 때 Stateless 방식에서는 어떤 전략을 사용해야 하나요?
- Redis를 사용한 토큰 블랙리스트 방식은 Stateless 원칙에 위배되는 것이 아닌가요?

## 참고
- [[Spring Security Session 관리]]
- [[RESTful API 설계 원칙]]

---

## 질문 3
> JwtAuthenticationFilter에서 토큰 검증이 실패했을 때의 처리 흐름을 설명하고, SecurityConfig의 exceptionHandling과 어떻게 연계되는지 설명해주세요.

## 핵심 답변 (3줄)
1. JwtAuthenticationFilter는 토큰 검증 실패 시 SecurityContext에 인증 정보를 설정하지 않고 다음 필터로 전달합니다
2. 인증이 필요한 엔드포인트에 접근할 때 SecurityContext가 비어있으면 AuthenticationEntryPoint가 호출됩니다
3. SecurityConfig에서 설정한 authenticationEntryPoint가 401 Unauthorized 응답을 JSON 형태로 반환합니다

## 상세 설명
BizSync의 JWT 인증 흐름에서 예외 처리는 여러 레이어에서 이루어집니다. JwtAuthenticationFilter는 요청 헤더에서 JWT를 추출하고 JwtProvider로 검증합니다. 검증 실패 시 필터에서 예외를 던지지 않고 조용히 다음 필터로 넘어갑니다. 이는 인증이 필요 없는 엔드포인트도 같은 필터를 거치기 때문입니다.

실제 인증이 필요한 엔드포인트에 도달했을 때, SecurityContext에 Authentication 객체가 없으면 Spring Security가 자동으로 AuthenticationException을 발생시킵니다. 이때 SecurityConfig에서 설정한 authenticationEntryPoint가 호출되어 클라이언트에게 구조화된 JSON 에러 응답을 반환합니다.

또한 accessDeniedHandler는 인증은 되었지만 권한이 부족한 경우(403 Forbidden)를 처리합니다. 이러한 계층적 예외 처리 구조는 보안과 사용자 경험을 모두 만족시킵니다.

## 코드 예시 (필요시)
```java
// SecurityConfig.java - 예외 처리 설정
.exceptionHandling(exception -> exception
    .authenticationEntryPoint((request, response, authException) -> {
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("error", "Unauthorized");
        errorResponse.put("message", "인증이 필요합니다. 로그인 후 다시 시도해주세요.");
        errorResponse.put("path", request.getRequestURI());
        
        ObjectMapper objectMapper = new ObjectMapper();
        response.getWriter().write(objectMapper.writeValueAsString(errorResponse));
    })
    .accessDeniedHandler((request, response, accessDeniedException) -> {
        response.setStatus(HttpServletResponse.SC_FORBIDDEN);
        // ... 403 에러 처리
    })
);
```

## 꼬리 질문 예상
- Filter에서 발생한 예외와 Controller에서 발생한 예외의 처리 방식이 다른 이유는 무엇인가요?
- @ControllerAdvice로 통합된 예외 처리를 할 수 없는 이유는 무엇인가요?
- 토큰 만료와 토큰 변조를 구분하여 다른 에러 메시지를 반환하려면 어떻게 해야 하나요?

## 참고
- [[Spring Security Filter Chain]]
- [[Exception Handling in Spring]]

---

## 질문 4
> BizSync에서 CORS 설정을 allowedOrigins로 환경변수화한 이유와 allowCredentials를 true로 설정한 의미를 설명해주세요.

## 핵심 답변 (3줄)
1. allowedOrigins를 환경변수로 관리하면 개발/운영 환경별로 다른 도메인을 허용할 수 있어 보안과 유연성이 향상됩니다
2. allowCredentials: true는 쿠키와 인증 헤더를 포함한 요청을 허용하여 JWT 토큰을 Authorization 헤더로 전송할 수 있게 합니다
3. Credentials 옵션 활성화 시 와일드카드(*) 대신 명시적인 Origin 목록을 사용해야 보안이 강화됩니다

## 상세 설명
CORS(Cross-Origin Resource Sharing)는 브라우저 보안 정책으로, 다른 도메인의 리소스 접근을 제한합니다. BizSync는 프론트엔드(React)와 백엔드(Spring Boot)가 분리되어 다른 포트에서 실행되므로 CORS 설정이 필수입니다.

allowedOrigins를 환경변수(`app.cors.allowed-origins`)로 분리한 것은 개발 환경에서는 localhost:5173을, 운영 환경에서는 실제 도메인을 허용하기 위함입니다. 쉼표로 구분하여 여러 도메인을 등록할 수 있습니다.

allowCredentials를 true로 설정하면 클라이언트가 withCredentials 옵션으로 인증 정보를 포함한 요청을 보낼 수 있습니다. 이는 JWT 토큰을 Authorization 헤더에 담아 전송하는 데 필수적입니다. 단, 보안을 위해 allowedOrigins를 와일드카드(*)로 설정할 수 없으며 명시적인 도메인 목록을 제공해야 합니다.

## 코드 예시 (필요시)
```java
// SecurityConfig.java
@Value("${app.cors.allowed-origins:http://localhost:5173,http://localhost:3000}")
private String allowedOrigins;

@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(Arrays.asList(allowedOrigins.split(",")));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"));
    config.setAllowedHeaders(List.of("*"));
    config.setAllowCredentials(true); // 인증 정보 포함 허용
    
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}
```

## 꼬리 질문 예상
- Preflight 요청은 무엇이며 언제 발생하나요?
- allowedHeaders를 "*"로 설정하는 것과 명시적으로 나열하는 것의 차이는 무엇인가요?
- SameSite 쿠키 속성과 CORS의 관계는 무엇인가요?

## 참고
- [[CORS 동작 원리]]
- [[Spring Boot CORS 설정]]

---

## 질문 5
> BizSync에서 JWT 서명 알고리즘으로 HS256을 선택한 이유와 다른 알고리즘(RS256 등)과의 차이점을 설명해주세요.

## 핵심 답변 (3줄)
1. HS256은 대칭키 방식으로 단일 서버 환경에서 빠른 성능과 간단한 구현이 가능합니다
2. 같은 Secret Key로 토큰 생성과 검증을 모두 수행하므로 키 관리가 단순하지만, 키 노출 시 위험이 큽니다
3. RS256은 비대칭키 방식으로 Public Key를 공개할 수 있어 마이크로서비스 환경에 적합하지만, 성능이 상대적으로 느립니다

## 상세 설명
JWT 서명 알고리즘은 크게 대칭키(HMAC) 방식과 비대칭키(RSA, ECDSA) 방식으로 나뉩니다. BizSync는 HS256(HMAC-SHA256)을 사용하는데, 이는 단일 Secret Key로 서명과 검증을 모두 수행하는 대칭키 방식입니다.

HS256의 장점은 성능이 빠르고 구현이 간단하다는 것입니다. 모놀리식 아키텍처에서 토큰 발급과 검증이 같은 서버에서 이루어지므로 대칭키로 충분합니다. 키를 environment variable로 안전하게 관리하면 보안성도 확보됩니다.

반면 RS256은 Private Key로 서명하고 Public Key로 검증하는 비대칭키 방식입니다. Public Key를 공개해도 토큰을 위조할 수 없으므로, 마이크로서비스 환경에서 여러 서비스가 토큰을 독립적으로 검증해야 할 때 유용합니다. 하지만 계산 비용이 높아 성능이 HS256보다 느립니다.

BizSync는 현재 단일 백엔드 서버 구조이므로 HS256이 적합한 선택입니다. 향후 마이크로서비스로 전환한다면 RS256 도입을 고려할 수 있습니다.

## 코드 예시 (필요시)
```java
// JwtProvider.java - HS256 사용
public JwtProvider(@Value("${app.jwt.secret}") String secret,
                   @Value("${app.jwt.expiration-ms}") long expiration,
                   @Value("${app.jwt.refresh-expiration-ms}") long refreshExpiration) {
    // Secret Key를 HMAC-SHA256용 키로 변환
    this.secretKey = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    this.expiration = expiration;
    this.refreshExpiration = refreshExpiration;
}

public String createToken(Long userId, Role role) {
    return Jwts.builder()
            .setSubject(String.valueOf(userId))
            .claim("role", role.name())
            .setExpiration(new Date(System.currentTimeMillis() + expiration))
            .signWith(secretKey, SignatureAlgorithm.HS256)  // HS256 명시
            .compact();
}
```

## 꼬리 질문 예상
- JWT Secret Key의 최소 길이 요구사항은 무엇이며, 그 이유는 무엇인가요?
- 키 로테이션(Key Rotation)을 구현한다면 어떤 전략을 사용하시겠습니까?
- JWE(JSON Web Encryption)와 JWS(JSON Web Signature)의 차이는 무엇인가요?

## 참고
- [[JWT 서명 알고리즘 비교]]
- [[대칭키 vs 비대칭키 암호화]]

---

## 질문 6
> @RequireProjectLeader와 @RequireProjectMember 커스텀 어노테이션을 만든 이유와 AOP를 활용한 권한 검증 방식을 설명해주세요.

## 핵심 답변 (3줄)
1. 메서드 레벨에서 선언적으로 프로젝트 권한을 검증하여 비즈니스 로직과 권한 검증 로직을 분리할 수 있습니다
2. AOP를 통해 중복 코드를 제거하고, 여러 메서드에서 일관된 권한 검증 로직을 재사용할 수 있습니다
3. Spring Security의 @PreAuthorize보다 도메인 특화된 권한 체계를 명확하게 표현할 수 있습니다

## 상세 설명
BizSync에서는 프로젝트별 권한 체계(LEADER, MEMBER)가 중요한 도메인 로직입니다. 예를 들어 칸반 컬럼 생성은 프로젝트 리더만 가능하고, 일반 업무 생성은 멤버도 가능합니다.

이러한 권한 검증을 매번 서비스 메서드 내에서 구현하면 코드 중복이 심하고 가독성이 떨어집니다. 커스텀 어노테이션과 AOP Aspect를 활용하면 권한 검증 로직을 한 곳에서 관리하고, 메서드에 어노테이션만 붙여서 선언적으로 권한을 명시할 수 있습니다.

@RequireProjectLeader는 메서드 파라미터에서 projectId를 추출하고, 현재 인증된 사용자가 해당 프로젝트의 리더인지 검증합니다. 검증 실패 시 커스텀 예외를 던져 GlobalExceptionHandler에서 일관되게 처리할 수 있습니다.

이 방식은 Spring Security의 @PreAuthorize와 유사하지만, 프로젝트 도메인에 특화된 권한 체계를 더 명확하게 표현할 수 있다는 장점이 있습니다.

## 코드 예시 (필요시)
```java
// RequireProjectLeader.java - 커스텀 어노테이션
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequireProjectLeader {
}

// KanbanService.java - 사용 예시
@Service
@RequiredArgsConstructor
@Transactional
public class KanbanService {
    
    @RequireProjectLeader  // 리더 권한 필요
    public Long createColumn(Long projectId, ColumnCreateRequestDTO dto) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new IllegalArgumentException("프로젝트가 없습니다."));
        
        // 권한 검증은 AOP에서 자동으로 처리되므로 비즈니스 로직에만 집중
        KanbanColumn column = KanbanColumn.builder()
                .project(project)
                .name(dto.name())
                .build();
        
        return kanbanColumnRepository.save(column).getColumnId();
    }
}
```

## 꼬리 질문 예상
- Aspect의 실행 순서를 제어하려면 어떻게 해야 하나요? (@Order 어노테이션)
- AOP를 사용하지 않고 Interceptor나 Filter로도 구현할 수 있지 않나요? 차이점은 무엇인가요?
- Spring Security의 Method Security(@Secured, @RolesAllowed)와 커스텀 어노테이션 중 어떤 것을 선택해야 할까요?

## 참고
- [[Spring AOP 개념과 활용]]
- [[커스텀 어노테이션 만들기]]

---

## 질문 7
> JWT 토큰에 role 정보를 claim으로 포함시킨 이유와 SecurityContext에 저장하는 방식을 설명해주세요.

## 핵심 답변 (3줄)
1. Role을 토큰에 포함시키면 매 요청마다 DB 조회 없이 사용자 권한을 확인할 수 있어 성능이 향상됩니다
2. JwtAuthenticationFilter에서 토큰의 role을 추출하여 GrantedAuthority로 변환해 SecurityContext에 저장합니다
3. Spring Security는 SecurityContext의 Authentication 객체를 통해 권한 기반 접근 제어를 수행합니다

## 상세 설명
JWT는 자체 포함(self-contained) 토큰이므로 인증에 필요한 모든 정보를 포함할 수 있습니다. BizSync에서는 userId와 함께 role(ADMIN, MEMBER)을 claim에 포함시켰습니다.

이렇게 하면 API 요청이 들어올 때마다 DB에서 사용자 권한을 조회할 필요가 없어 성능이 크게 향상됩니다. JwtAuthenticationFilter는 토큰에서 role을 추출하고, Spring Security의 GrantedAuthority 형태로 변환하여 UsernamePasswordAuthenticationToken에 담아 SecurityContext에 저장합니다.

이후 @PreAuthorize("hasRole('ADMIN')") 같은 Spring Security의 권한 체크 기능을 그대로 사용할 수 있습니다. 또한 SecurityUtil.getCurrentUser()로 현재 인증된 사용자 정보를 편리하게 가져올 수 있습니다.

단, role이 변경되면 기존 토큰은 여전히 옛 권한을 가지므로, 토큰이 만료되기 전까지는 변경사항이 반영되지 않는다는 단점이 있습니다. 중요한 권한 변경 시 토큰을 무효화하는 전략이 필요할 수 있습니다.

## 코드 예시 (필요시)
```java
// JwtProvider.java - role을 claim에 포함
public String createToken(Long userId, Role role) {
    return Jwts.builder()
            .setSubject(String.valueOf(userId))
            .claim("role", role.name())  // role 정보 포함
            .claim("type", "access")
            .setExpiration(new Date(System.currentTimeMillis() + expiration))
            .signWith(secretKey, SignatureAlgorithm.HS256)
            .compact();
}

// JwtAuthenticationFilter.java - SecurityContext에 저장
String role = jwtProvider.getRole(token);
Collection<GrantedAuthority> authorities = 
    Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + role));

UsernamePasswordAuthenticationToken authentication = 
    new UsernamePasswordAuthenticationToken(userId, null, authorities);

SecurityContextHolder.getContext().setAuthentication(authentication);
```

## 꼬리 질문 예상
- JWT에 민감한 정보(이메일, 개인정보 등)를 넣으면 안 되는 이유는 무엇인가요?
- Role이 변경되었을 때 기존 토큰을 무효화하는 방법은 무엇인가요?
- RBAC(Role-Based Access Control)와 ABAC(Attribute-Based Access Control)의 차이는 무엇인가요?

## 참고
- [[Spring Security Authentication]]
- [[JWT Claims 설계 가이드]]

---

## 질문 8
> BizSync에서 /api/auth/** 엔드포인트를 permitAll()로 설정한 이유와 인증 없이 접근 가능한 엔드포인트 설계 전략을 설명해주세요.

## 핵심 답변 (3줄)
1. 로그인과 회원가입은 인증 전에 수행되어야 하므로 인증 필터를 우회해야 합니다
2. /api/auth/** 패턴을 permitAll()로 설정하면 해당 엔드포인트는 Spring Security 필터는 거치지만 인증 없이 접근 가능합니다
3. 토큰 갱신(refresh) 엔드포인트도 인증 없이 접근 가능해야 하며, 내부에서 Refresh Token 검증을 별도로 수행합니다

## 상세 설명
Spring Security의 기본 동작은 모든 요청에 인증을 요구하는 것입니다. 하지만 로그인, 회원가입, 토큰 갱신 같은 엔드포인트는 인증 없이 접근 가능해야 합니다.

authorizeHttpRequests()에서 permitAll()로 설정된 경로는 Spring Security 필터 체인을 거치지만, 인증 여부와 관계없이 접근이 허용됩니다. BizSync에서는 /api/auth/** 패턴으로 인증 관련 엔드포인트를 그룹화했습니다.

중요한 점은 permitAll()이 보안 검증을 완전히 생략하는 것이 아니라는 것입니다. 예를 들어 /api/auth/refresh 엔드포인트는 Spring Security 인증을 우회하지만, AuthService 내부에서 Refresh Token의 유효성을 직접 검증합니다. 이렇게 엔드포인트별로 적절한 보안 레벨을 설계하는 것이 중요합니다.

또한 Swagger UI(/swagger-ui/**), 헬스체크(/actuator/health), WebSocket(/ws/**)도 인증 없이 접근 가능하도록 설정되어 있습니다.

## 코드 예시 (필요시)
```java
// SecurityConfig.java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/auth/**").permitAll()  // 인증 관련
            .requestMatchers("/v3/api-docs/**", "/swagger-ui/**").permitAll()  // Swagger
            .requestMatchers("/actuator/health").permitAll()  // 헬스체크
            .requestMatchers("/ws/**").permitAll()  // WebSocket
            .anyRequest().authenticated()  // 나머지는 인증 필요
        )
        .addFilterBefore(jwtAuthenticationFilter, 
            UsernamePasswordAuthenticationFilter.class);
    
    return http.build();
}

// AuthController.java
@RestController
@RequestMapping("/api/auth")
public class AuthController {
    
    @PostMapping("/login")  // permitAll 적용
    public ResponseEntity<LoginResponseDTO> login(@RequestBody LoginRequestDTO dto) {
        // 인증 로직
    }
    
    @PostMapping("/refresh")  // permitAll 적용, 하지만 내부에서 토큰 검증
    public ResponseEntity<JwtTokenResponse> refresh(@RequestBody RefreshTokenRequest dto) {
        // Refresh Token 검증 로직
    }
}
```

## 꼬리 질문 예상
- permitAll()과 anonymous()의 차이는 무엇인가요?
- Swagger UI를 프로덕션 환경에서도 공개하는 것이 안전한가요?
- 헬스체크 엔드포인트를 인증 없이 공개하는 것의 보안 위험은 무엇인가요?

## 참고
- [[Spring Security 요청 매칭 전략]]
- [[API 보안 설계 베스트 프랙티스]]

---

## 질문 9
> JwtAuthenticationFilter를 UsernamePasswordAuthenticationFilter 앞에 배치한 이유와 Filter Chain의 실행 순서를 설명해주세요.

## 핵심 답변 (3줄)
1. JWT 인증이 성공하면 UsernamePasswordAuthenticationFilter를 실행할 필요가 없으므로 앞에 배치하여 불필요한 처리를 건너뜁니다
2. JwtAuthenticationFilter에서 SecurityContext에 인증 정보를 설정하면 이후 필터들은 이미 인증된 요청으로 처리합니다
3. Spring Security의 Filter Chain은 순서가 중요하며, 커스텀 필터의 위치에 따라 인증 흐름이 달라집니다

## 상세 설명
Spring Security는 여러 필터가 체인 형태로 연결된 구조입니다. 각 필터는 특정 책임을 가지며, 정해진 순서대로 실행됩니다.

UsernamePasswordAuthenticationFilter는 전통적인 폼 로그인 방식을 처리하는 필터입니다. BizSync는 JWT 기반 인증을 사용하므로 이 필터가 필요 없지만, Spring Security에 기본 포함되어 있습니다.

JwtAuthenticationFilter를 UsernamePasswordAuthenticationFilter 앞에 배치하면, JWT 토큰이 있는 요청은 JWT 필터에서 먼저 처리되고, SecurityContext에 인증 정보가 설정됩니다. 이후 UsernamePasswordAuthenticationFilter에 도달해도 이미 인증이 완료된 상태이므로 아무 동작도 하지 않고 통과합니다.

반대로 JWT 필터를 뒤에 배치하면 불필요한 필터를 먼저 거쳐야 하므로 비효율적입니다. addFilterBefore() 메서드를 사용하여 정확한 위치에 커스텀 필터를 삽입할 수 있습니다.

## 코드 예시 (필요시)
```java
// SecurityConfig.java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .sessionManagement(session -> session
            .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/auth/**").permitAll()
            .anyRequest().authenticated()
        )
        // JwtAuthenticationFilter를 UsernamePasswordAuthenticationFilter 앞에 배치
        .addFilterBefore(jwtAuthenticationFilter, 
            UsernamePasswordAuthenticationFilter.class);
    
    return http.build();
}

// Spring Security Filter Chain 순서 (일부)
// 1. SecurityContextPersistenceFilter
// 2. LogoutFilter
// 3. JwtAuthenticationFilter ← 여기에 삽입
// 4. UsernamePasswordAuthenticationFilter
// 5. AnonymousAuthenticationFilter
// 6. ExceptionTranslationFilter
// 7. FilterSecurityInterceptor
```

## 꼬리 질문 예상
- addFilterBefore(), addFilterAfter(), addFilterAt()의 차이는 무엇인가요?
- OncePerRequestFilter를 상속받는 이유는 무엇인가요?
- Filter와 Interceptor의 차이점은 무엇이며, 언제 어떤 것을 사용해야 하나요?

## 참고
- [[Spring Security Filter Chain 아키텍처]]
- [[커스텀 필터 구현 가이드]]

---

## 질문 10
> BCryptPasswordEncoder를 사용한 비밀번호 암호화 방식과 Salt 개념, 그리고 Rainbow Table 공격 방어 메커니즘을 설명해주세요.

## 핵심 답변 (3줄)
1. BCrypt는 Blowfish 암호화 알고리즘 기반의 단방향 해시 함수로, 비밀번호를 복호화할 수 없는 형태로 저장합니다
2. 각 비밀번호마다 랜덤한 Salt를 생성하여 같은 비밀번호라도 다른 해시값을 가지게 함으로써 Rainbow Table 공격을 무력화합니다
3. Work Factor(라운드 수)를 조정하여 연산 시간을 늘릴 수 있어 Brute Force 공격에 대한 저항력을 높입니다

## 상세 설명
BCryptPasswordEncoder는 Spring Security에서 권장하는 비밀번호 암호화 방식입니다. 일반 해시 함수(MD5, SHA-1)와 달리 의도적으로 느리게 설계되어 Brute Force 공격을 어렵게 만듭니다.

BCrypt의 핵심은 Salt입니다. Salt는 비밀번호에 추가되는 랜덤 문자열로, 같은 비밀번호라도 다른 해시값을 생성하게 합니다. 예를 들어 "password123"이라는 같은 비밀번호를 두 사용자가 사용해도, Salt가 다르므로 DB에 저장되는 해시값은 완전히 다릅니다.

Rainbow Table은 미리 계산된 해시값 데이터베이스로, 역방향 조회를 통해 원본 비밀번호를 찾는 공격 기법입니다. 하지만 Salt가 있으면 공격자가 모든 가능한 Salt 조합에 대한 Rainbow Table을 만들어야 하므로 사실상 불가능해집니다.

BizSync에서는 BCryptPasswordEncoder를 Bean으로 등록하여, 회원가입 시 passwordEncoder.encode()로 암호화하고, 로그인 시 passwordEncoder.matches()로 검증합니다.

## 코드 예시 (필요시)
```java
// SecurityConfig.java
@Bean
public BCryptPasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();  // 기본 strength: 10
}

// AuthService.java - 회원가입
public void signup(SignupRequestDTO dto) {
    String encodedPassword = passwordEncoder.encode(dto.password());
    
    User user = User.builder()
            .email(dto.email())
            .password(encodedPassword)  // 암호화된 비밀번호 저장
            .build();
    
    userRepository.save(user);
}

// AuthService.java - 로그인
public LoginResponseDTO login(LoginRequestDTO dto) {
    User user = userRepository.findByEmail(dto.email())
            .orElseThrow(() -> new IllegalArgumentException("사용자가 없습니다"));
    
    if (!passwordEncoder.matches(dto.password(), user.getPassword())) {
        throw new IllegalArgumentException("비밀번호가 일치하지 않습니다");
    }
    
    // JWT 토큰 생성 및 반환
}

// BCrypt 해시 예시 (같은 비밀번호, 다른 Salt)
// $2a$10$N9qo8uLOickgx2ZMRZoMye IIJZhroxRXQJj6lUdQfhxDiIp6W
// $2a$10$92IXUNpkjO0rOQ5byMi.Ye 4oKoEa3Ro9llC/.og/at2uheWG/igi
```

## 꼬리 질문 예상
- BCrypt의 Work Factor(strength)를 높이면 어떤 장단점이 있나요?
- Argon2, SCrypt와 BCrypt를 비교했을 때 각각의 장단점은 무엇인가요?
- 비밀번호 변경 시 재암호화가 필요한 이유는 무엇인가요?

## 참고
- [[비밀번호 암호화 알고리즘 비교]]
- [[Salt와 Rainbow Table 공격]]
