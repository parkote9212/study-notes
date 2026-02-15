---
tags:
  - study
  - spring
  - security
  - oauth2
  - social-login
created: 2025-02-08
---

# OAuth2 기초

## 한 줄 요약
> OAuth2는 제3자 애플리케이션이 사용자의 비밀번호 없이 Google, GitHub 등의 서비스에 제한적으로 접근할 수 있도록 권한을 위임하는 표준 프로토콜로, 소셜 로그인 구현의 기반이 된다.

## 상세 설명

### OAuth2란?
- **권한 위임** 표준 프로토콜
- **소셜 로그인**: Google, GitHub, Kakao 로그인
- **제3자 접근**: 비밀번호 없이 API 접근

### 왜 OAuth2가 필요한가?
```java
// ❌ 비밀번호 직접 요구
"Google 비밀번호를 입력하세요"
// 보안 위험! 제3자가 비밀번호 알게 됨

// ✅ OAuth2로 권한만 위임
"Google 계정으로 로그인 허용하시겠습니까?"
// 비밀번호 노출 없이 권한만 부여
```

### OAuth2 주요 용어

| 용어 | 설명 | 예시 |
|-----|------|------|
| **Resource Owner** | 자원 소유자 (사용자) | 구글 계정 소유자 |
| **Resource Server** | 자원 서버 | Google API 서버 |
| **Client** | 제3자 애플리케이션 | 우리 서비스 |
| **Authorization Server** | 인증 서버 | Google OAuth 서버 |
| **Access Token** | 접근 토큰 | API 호출용 토큰 |
| **Refresh Token** | 갱신 토큰 | Access Token 재발급용 |

### OAuth2 인증 흐름 (Authorization Code Grant)

```
1. 사용자 → Client: "Google로 로그인"
   ↓
2. Client → Authorization Server: 인증 요청
   GET https://accounts.google.com/o/oauth2/auth
   ?client_id=...
   &redirect_uri=...
   &scope=profile email
   ↓
3. 사용자 → Authorization Server: Google 로그인
   ↓
4. Authorization Server → Client: Authorization Code 발급
   redirect_uri?code=AUTHORIZATION_CODE
   ↓
5. Client → Authorization Server: Access Token 요청
   POST https://oauth2.googleapis.com/token
   code=AUTHORIZATION_CODE
   &client_id=...
   &client_secret=...
   ↓
6. Authorization Server → Client: Access Token 발급
   {
     "access_token": "ya29.a0...",
     "token_type": "Bearer",
     "expires_in": 3600
   }
   ↓
7. Client → Resource Server: API 호출
   GET https://www.googleapis.com/oauth2/v2/userinfo
   Authorization: Bearer ya29.a0...
   ↓
8. Resource Server → Client: 사용자 정보 응답
   {
     "id": "12345",
     "email": "user@gmail.com",
     "name": "John Doe"
   }
```

### OAuth2 Grant Types

| Grant Type | 설명 | 사용처 |
|-----------|------|--------|
| **Authorization Code** | 가장 안전 | 웹 애플리케이션 |
| **Implicit** | Client Secret 없음 | SPA (deprecated) |
| **Resource Owner Password** | 직접 비밀번호 입력 | 신뢰 가능한 앱 |
| **Client Credentials** | 서버 간 통신 | Backend to Backend |

## 코드 예시

```java
// 1. OAuth2 의존성
// build.gradle
// implementation 'org.springframework.boot:spring-boot-starter-oauth2-client'

// 2. application.yml 설정
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: ${GOOGLE_CLIENT_ID}
            client-secret: ${GOOGLE_CLIENT_SECRET}
            scope:
              - profile
              - email
          
          github:
            client-id: ${GITHUB_CLIENT_ID}
            client-secret: ${GITHUB_CLIENT_SECRET}
            scope:
              - read:user
              - user:email
          
          kakao:
            client-id: ${KAKAO_CLIENT_ID}
            client-secret: ${KAKAO_CLIENT_SECRET}
            redirect-uri: "{baseUrl}/login/oauth2/code/{registrationId}"
            authorization-grant-type: authorization_code
            client-authentication-method: POST
            scope:
              - profile_nickname
              - account_email
            client-name: Kakao
        
        provider:
          kakao:
            authorization-uri: https://kauth.kakao.com/oauth/authorize
            token-uri: https://kauth.kakao.com/oauth/token
            user-info-uri: https://kapi.kakao.com/v2/user/me
            user-name-attribute: id

// 3. OAuth2 Security 설정
@Configuration
@EnableWebSecurity
public class OAuth2SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/login/**", "/error").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2Login(oauth2 -> oauth2
                .loginPage("/login")
                .defaultSuccessUrl("/dashboard")
                .userInfoEndpoint(userInfo -> userInfo
                    .userService(customOAuth2UserService)
                )
                .successHandler(oAuth2SuccessHandler)
                .failureHandler(oAuth2FailureHandler)
            );
        
        return http.build();
    }
}

// 4. CustomOAuth2UserService
@Service
@RequiredArgsConstructor
@Slf4j
public class CustomOAuth2UserService 
        extends DefaultOAuth2UserService {
    
    private final UserRepository userRepository;
    
    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) 
            throws OAuth2AuthenticationException {
        
        // 1. OAuth2 사용자 정보 조회
        OAuth2User oAuth2User = super.loadUser(userRequest);
        
        // 2. Provider 정보
        String registrationId = userRequest.getClientRegistration()
                .getRegistrationId();  // google, github, kakao
        
        // 3. 사용자 정보 추출
        Map<String, Object> attributes = oAuth2User.getAttributes();
        
        // 4. Provider별 사용자 정보 파싱
        OAuth2UserInfo userInfo = OAuth2UserInfoFactory
                .getOAuth2UserInfo(registrationId, attributes);
        
        // 5. DB에서 사용자 조회 또는 생성
        User user = getOrCreateUser(userInfo, registrationId);
        
        // 6. CustomOAuth2User 반환
        return new CustomOAuth2User(user, attributes);
    }
    
    private User getOrCreateUser(OAuth2UserInfo userInfo, String provider) {
        return userRepository
                .findByProviderAndProviderId(provider, userInfo.getId())
                .orElseGet(() -> {
                    User newUser = User.builder()
                            .provider(provider)
                            .providerId(userInfo.getId())
                            .email(userInfo.getEmail())
                            .name(userInfo.getName())
                            .profileImage(userInfo.getImageUrl())
                            .role("USER")
                            .build();
                    return userRepository.save(newUser);
                });
    }
}

// 5. OAuth2UserInfo 인터페이스
public interface OAuth2UserInfo {
    String getId();
    String getName();
    String getEmail();
    String getImageUrl();
}

// Google 구현
public class GoogleOAuth2UserInfo implements OAuth2UserInfo {
    
    private final Map<String, Object> attributes;
    
    public GoogleOAuth2UserInfo(Map<String, Object> attributes) {
        this.attributes = attributes;
    }
    
    @Override
    public String getId() {
        return (String) attributes.get("sub");
    }
    
    @Override
    public String getName() {
        return (String) attributes.get("name");
    }
    
    @Override
    public String getEmail() {
        return (String) attributes.get("email");
    }
    
    @Override
    public String getImageUrl() {
        return (String) attributes.get("picture");
    }
}

// GitHub 구현
public class GitHubOAuth2UserInfo implements OAuth2UserInfo {
    
    private final Map<String, Object> attributes;
    
    @Override
    public String getId() {
        return String.valueOf(attributes.get("id"));
    }
    
    @Override
    public String getName() {
        return (String) attributes.get("name");
    }
    
    @Override
    public String getEmail() {
        return (String) attributes.get("email");
    }
    
    @Override
    public String getImageUrl() {
        return (String) attributes.get("avatar_url");
    }
}

// Kakao 구현
public class KakaoOAuth2UserInfo implements OAuth2UserInfo {
    
    private final Map<String, Object> attributes;
    
    @Override
    public String getId() {
        return String.valueOf(attributes.get("id"));
    }
    
    @Override
    public String getName() {
        Map<String, Object> properties = 
            (Map<String, Object>) attributes.get("properties");
        return (String) properties.get("nickname");
    }
    
    @Override
    public String getEmail() {
        Map<String, Object> kakaoAccount = 
            (Map<String, Object>) attributes.get("kakao_account");
        return (String) kakaoAccount.get("email");
    }
    
    @Override
    public String getImageUrl() {
        Map<String, Object> properties = 
            (Map<String, Object>) attributes.get("properties");
        return (String) properties.get("profile_image");
    }
}

// Factory
public class OAuth2UserInfoFactory {
    
    public static OAuth2UserInfo getOAuth2UserInfo(
            String registrationId,
            Map<String, Object> attributes) {
        
        return switch (registrationId) {
            case "google" -> new GoogleOAuth2UserInfo(attributes);
            case "github" -> new GitHubOAuth2UserInfo(attributes);
            case "kakao" -> new KakaoOAuth2UserInfo(attributes);
            default -> throw new OAuth2AuthenticationException(
                "Unsupported provider: " + registrationId
            );
        };
    }
}

// 6. User 엔티티 (소셜 로그인용)
@Entity
@Getter
@NoArgsConstructor
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column
    private String email;
    
    @Column
    private String name;
    
    @Column
    private String profileImage;
    
    @Column
    private String provider;  // google, github, kakao
    
    @Column
    private String providerId;  // Provider의 사용자 ID
    
    @Column
    private String role;
    
    @Builder
    public User(String email, String name, String profileImage, 
                String provider, String providerId, String role) {
        this.email = email;
        this.name = name;
        this.profileImage = profileImage;
        this.provider = provider;
        this.providerId = providerId;
        this.role = role;
    }
    
    public User update(String name, String profileImage) {
        this.name = name;
        this.profileImage = profileImage;
        return this;
    }
}

// 7. CustomOAuth2User
@Getter
public class CustomOAuth2User implements OAuth2User {
    
    private final User user;
    private final Map<String, Object> attributes;
    
    public CustomOAuth2User(User user, Map<String, Object> attributes) {
        this.user = user;
        this.attributes = attributes;
    }
    
    @Override
    public Map<String, Object> getAttributes() {
        return attributes;
    }
    
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.singleton(
            new SimpleGrantedAuthority("ROLE_" + user.getRole())
        );
    }
    
    @Override
    public String getName() {
        return user.getName();
    }
}

// 8. OAuth2 로그인 성공 핸들러
@Component
@RequiredArgsConstructor
@Slf4j
public class OAuth2SuccessHandler 
        implements AuthenticationSuccessHandler {
    
    private final JwtProvider jwtProvider;
    
    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication) throws IOException {
        
        // 1. OAuth2User 추출
        CustomOAuth2User oAuth2User = 
            (CustomOAuth2User) authentication.getPrincipal();
        
        // 2. JWT 토큰 생성
        String token = jwtProvider.createToken(authentication);
        
        // 3. 프론트엔드로 리다이렉트 (토큰 전달)
        String redirectUrl = UriComponentsBuilder
                .fromUriString("http://localhost:3000/oauth/redirect")
                .queryParam("token", token)
                .build()
                .toUriString();
        
        response.sendRedirect(redirectUrl);
    }
}

// 9. 일반 로그인 + OAuth2 로그인 통합
@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    // 일반 회원가입
    public User registerUser(String email, String password, String name) {
        User user = User.builder()
                .email(email)
                .password(passwordEncoder.encode(password))
                .name(name)
                .provider("local")  // 일반 로그인
                .role("USER")
                .build();
        
        return userRepository.save(user);
    }
    
    // 계정 연동 (일반 → OAuth2)
    public User linkOAuth2(Long userId, String provider, String providerId) {
        User user = userRepository.findById(userId)
                .orElseThrow();
        
        user.linkOAuth2(provider, providerId);
        return userRepository.save(user);
    }
}

// 10. REST API용 OAuth2 (토큰 방식)
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class OAuth2ApiController {
    
    private final OAuth2AuthorizedClientService authorizedClientService;
    
    @GetMapping("/oauth2/token")
    public ResponseEntity<OAuth2TokenResponse> getOAuth2Token(
            Authentication authentication) {
        
        // OAuth2 인증된 사용자
        OAuth2AuthenticationToken oAuth2Token = 
            (OAuth2AuthenticationToken) authentication;
        
        // OAuth2AuthorizedClient 조회
        OAuth2AuthorizedClient client = authorizedClientService
                .loadAuthorizedClient(
                    oAuth2Token.getAuthorizedClientRegistrationId(),
                    oAuth2Token.getName()
                );
        
        // Access Token
        String accessToken = client.getAccessToken().getTokenValue();
        
        return ResponseEntity.ok(new OAuth2TokenResponse(accessToken));
    }
}

// 11. OAuth2 로그아웃
@PostMapping("/logout")
public ResponseEntity<Void> logout(
        HttpServletRequest request,
        HttpServletResponse response,
        Authentication authentication) {
    
    // 1. Spring Security 로그아웃
    SecurityContextHolder.clearContext();
    
    // 2. 세션 무효화
    HttpSession session = request.getSession(false);
    if (session != null) {
        session.invalidate();
    }
    
    // 3. (선택) OAuth2 Provider에도 로그아웃 요청
    // Google: https://accounts.google.com/Logout
    // Kakao: https://kauth.kakao.com/oauth/logout
    
    return ResponseEntity.ok().build();
}

// 12. 여러 Provider로 로그인한 사용자 처리
@Entity
public class User {
    
    @ElementCollection
    @CollectionTable(name = "user_providers")
    private Set<UserProvider> providers = new HashSet<>();
}

@Embeddable
@Getter
@NoArgsConstructor
public class UserProvider {
    
    private String provider;  // google, github, kakao
    private String providerId;
    
    public UserProvider(String provider, String providerId) {
        this.provider = provider;
        this.providerId = providerId;
    }
}
```

## 주의사항 / 함정

### 1. Client Secret 노출
```java
// ❌ 하드코딩
client-secret: abc123...

// ✅ 환경변수 사용
client-secret: ${GOOGLE_CLIENT_SECRET}
```

### 2. Redirect URI 불일치
```
// ❌ OAuth Provider 설정과 다름
redirect-uri: http://localhost:8080/callback
// Google Console: http://localhost:8080/login/oauth2/code/google

// ✅ 정확히 일치
redirect-uri: "{baseUrl}/login/oauth2/code/{registrationId}"
```

### 3. Scope 과도 요청
```yaml
# ❌ 불필요한 권한 요청
scope:
  - profile
  - email
  - drive  # 필요 없는 권한

# ✅ 최소 권한
scope:
  - profile
  - email
```

### 4. CSRF 보호 비활성화
```java
// ❌ OAuth2에서도 CSRF 필요
http.csrf().disable();

// ✅ OAuth2는 CSRF 활성화 유지
http.csrf(Customizer.withDefaults());
```

### 5. 프론트엔드와 백엔드 분리 시 처리
```java
// ❌ 백엔드가 세션 기반 OAuth2 사용
// 프론트엔드는 토큰 기반 → 불일치!

// ✅ OAuth2 성공 후 JWT 발급
onAuthenticationSuccess() {
    String jwt = jwtProvider.createToken(authentication);
    response.sendRedirect("https://frontend.com?token=" + jwt);
}
```

### 6. Provider별 사용자 정보 구조 차이
```java
// ❌ 모든 Provider를 동일하게 처리
String email = (String) attributes.get("email");
// Kakao는 kakao_account.email!

// ✅ Provider별 구현
OAuth2UserInfoFactory.getOAuth2UserInfo(registrationId, attributes)
```

### 7. 이메일 미제공 Provider
```java
// ❌ 이메일 필수라고 가정
user.setEmail(oauth2User.getEmail());  // null 가능!

// ✅ null 체크
String email = oauth2User.getEmail();
if (email == null) {
    // 추가 정보 입력 페이지로 리다이렉트
}
```

## 관련 개념
- [[Spring-Security-아키텍처]]
- [[인증-흐름-Authentication]]
- [[JWT-토큰-기반-인증]]

## 면접 질문

1. **OAuth2란 무엇인가요?**
   - 권한 위임 표준 프로토콜
   - 제3자 앱이 비밀번호 없이 API 접근
   - 소셜 로그인 구현 기반

2. **OAuth2 주요 구성 요소 4가지는?**
   - Resource Owner (사용자)
   - Resource Server (API 서버)
   - Client (제3자 앱)
   - Authorization Server (인증 서버)

3. **Authorization Code Grant 흐름을 설명하세요.**
   - 인증 요청 → Authorization Code 발급 → Access Token 교환 → API 호출

4. **Access Token과 Refresh Token의 차이는?**
   - Access: API 호출용, 짧은 만료
   - Refresh: Access Token 재발급용, 긴 만료

5. **OAuth2와 JWT의 차이는?**
   - OAuth2: 권한 위임 프로토콜
   - JWT: 토큰 형식 (OAuth2에서 사용 가능)

6. **여러 Provider로 로그인한 사용자는 어떻게 처리하나요?**
   - email로 동일 사용자 식별
   - 또는 계정 연동 기능 제공

7. **OAuth2 로그인 후 JWT를 발급하는 이유는?**
   - Stateless API 구현
   - 프론트엔드와 백엔드 분리

## 참고 자료
- RFC 6749 - OAuth 2.0
- Spring Security OAuth2 Documentation
- https://docs.spring.io/spring-security/reference/servlet/oauth2/index.html
