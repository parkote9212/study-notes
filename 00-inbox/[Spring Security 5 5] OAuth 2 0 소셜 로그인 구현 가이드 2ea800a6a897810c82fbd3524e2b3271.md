# [Spring Security 5/5] OAuth 2.0 소셜 로그인 구현 가이드

🏷️기술 카테고리: Security, Spring
💡핵심키워드: #JWT, #설정관리, #환경변수
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 16일 오후 8:30
📅 다음 복습일: 2026년 1월 21일

# 1. Abstract: 핵심 요약

> **OAuth 2.0**은 사용자가 비밀번호를 공유하지 않고 제3자 애플리케이션에 리소스 접근 권한을 위임할 수 있는 **인가 프레임워크**입니다. 구글, 카카오, 네이버 등의 소셜 로그인을 구현할 수 있습니다.
> 

**핵심 개념**:

- 인증(Authentication)이 아닌 **인가(Authorization)** 프로토콜
- Access Token으로 리소스 접근
- Authorization Code Grant 방식이 가장 안전

---

# 2. OAuth 2.0 흐름

## 2.1 Authorization Code Grant

```
1. 사용자: "구글로 로그인" 클릭
    ↓
2. 애플리케이션: 구글 인증 페이지로 리다이렉트
    ↓
3. 사용자: 구글에 로그인 + 권한 승인
    ↓
4. 구글: Authorization Code 발급 (리다이렉트)
    ↓
5. 애플리케이션: Authorization Code로 Access Token 요청
    ↓
6. 구글: Access Token 발급
    ↓
7. 애플리케이션: Access Token으로 사용자 정보 조회
    ↓
8. 애플리케이션: 자체 JWT 발급 또는 세션 생성
```

---

# 3. Spring Boot 구현

## Step 1: 의존성

```
implementation 'org.springframework.boot:spring-boot-starter-oauth2-client'
```

## Step 2: application.yml

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: ${GOOGLE_CLIENT_ID}
            client-secret: ${GOOGLE_CLIENT_SECRET}
            scope:
              - email
              - profile
          kakao:
            client-id: ${KAKAO_CLIENT_ID}
            client-secret: ${KAKAO_CLIENT_SECRET}
            redirect-uri: "{baseUrl}/login/oauth2/code/kakao"
            authorization-grant-type: authorization_code
            scope:
              - profile_nickname
              - account_email
            client-name: Kakao
        provider:
          kakao:
            authorization-uri: [https://kauth.kakao.com/oauth/authorize](https://kauth.kakao.com/oauth/authorize)
            token-uri: [https://kauth.kakao.com/oauth/token](https://kauth.kakao.com/oauth/token)
            user-info-uri: [https://kapi.kakao.com/v2/user/me](https://kapi.kakao.com/v2/user/me)
            user-name-attribute: id
```

## Step 3: SecurityConfig

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .oauth2Login(oauth2 -> oauth2
            .userInfoEndpoint(userInfo -> userInfo
                .userService(customOAuth2UserService)
            )
            .successHandler(oAuth2SuccessHandler)
        );
    return [http.build](http://http.build)();
}
```

## Step 4: CustomOAuth2UserService

```java
@Service
@RequiredArgsConstructor
public class CustomOAuth2UserService 
    extends DefaultOAuth2UserService {

    private final UserRepository userRepository;

    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) {
        OAuth2User oAuth2User = super.loadUser(userRequest);
        
        String registrationId = userRequest.getClientRegistration()
            .getRegistrationId();
        String userNameAttributeName = userRequest
            .getClientRegistration()
            .getProviderDetails()
            .getUserInfoEndpoint()
            .getUserNameAttributeName();

        OAuth2Attributes attributes = OAuth2Attributes.of(
            registrationId,
            userNameAttributeName,
            oAuth2User.getAttributes()
        );

        User user = saveOrUpdate(attributes);
        
        return new CustomOAuth2User(
            Collections.singleton(
                new SimpleGrantedAuthority(user.getRole())),
            attributes.getAttributes(),
            attributes.getNameAttributeKey(),
            user
        );
    }

    private User saveOrUpdate(OAuth2Attributes attributes) {
        User user = userRepository
            .findByEmail(attributes.getEmail())
            .map(entity -> entity.update(
                attributes.getName(),
                attributes.getPicture()
            ))
            .orElse(attributes.toEntity());
        
        return [userRepository.save](http://userRepository.save)(user);
    }
}
```

---

# 4. Interview Readiness

## ▶ Q: OAuth와 JWT를 어떻게 함께 사용하나요?

**A**: OAuth로 사용자를 인증한 후, 자체 JWT를 발급합니다. OAuth Access Token은 외부 API 호출용이고, JWT는 자사 API 인증용입니다.

---

**작성일**: 2026-01-16  

**면접 빈출도**: ⭐⭐⭐⭐ (상)