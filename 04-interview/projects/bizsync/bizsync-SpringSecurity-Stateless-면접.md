---
tags:
  - interview
  - spring-security
  - stateless
  - jwt
  - bizsync
  - project
created: 2025-01-23
difficulty: 중상
---

# BizSync - Spring Security Stateless 설정

## 질문
> SecurityConfig에서 SessionCreationPolicy를 STATELESS로 설정한 이유와 이것이 JWT 인증에 미치는 영향을 설명해주세요.

## 핵심 답변 (3줄)
1. STATELESS 정책은 서버가 세션을 생성하거나 유지하지 않아 서버 메모리 부담을 줄이고 수평 확장이 용이합니다
2. JWT는 자체적으로 인증 정보를 포함하므로 서버 측 세션 저장소가 필요 없어 Stateless 아키텍처와 완벽하게 호환됩니다
3. 로드 밸런서 뒤에 여러 인스턴스가 있어도 세션 공유 문제 없이 어느 서버든 요청을 처리할 수 있습니다

## 상세 설명
Spring Security의 SessionCreationPolicy.STATELESS는 서버가 HTTP 세션을 생성하지 않도록 지시합니다. 

전통적인 세션 기반 인증에서는 서버가 세션 ID를 쿠키로 클라이언트에 전달하고, 서버 메모리나 세션 저장소에 사용자 정보를 보관합니다. 하지만 이는 서버의 메모리를 소비하고, 다중 서버 환경에서 세션 동기화 문제를 야기합니다.

BizSync에서는 JWT를 사용하므로 모든 인증 정보가 토큰 자체에 포함됩니다. 서버는 토큰의 서명만 검증하면 되므로 별도의 세션 저장이 불필요합니다.

## 코드 예시
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
- 로그아웃 기능을 구현할 때 어떤 전략을 사용해야 하나요?

## 참고
- [[bizsync-JWT-AccessRefreshToken-면접]]
- [[bizsync-JwtAuthenticationFilter-면접]]
