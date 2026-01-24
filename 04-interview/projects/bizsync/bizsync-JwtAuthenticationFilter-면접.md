---
tags:
  - interview
  - spring-security
  - jwt
  - filter
  - bizsync
  - project
created: 2025-01-23
difficulty: 중상
---

# BizSync - JwtAuthenticationFilter 구현

## 질문
> JwtAuthenticationFilter의 역할과 구현 방법을 설명해주세요.

## 핵심 답변 (3줄)
1. **요청 인터셉트** - 모든 HTTP 요청의 Authorization 헤더에서 JWT 추출
2. **토큰 검증 및 인증 설정** - 유효한 토큰이면 SecurityContext에 인증 정보 저장
3. **필터 체인 진행** - 인증 완료 후 다음 필터로 요청 전달

## 상세 설명
```java
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    private final JwtProvider jwtProvider;
    
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) 
            throws ServletException, IOException {
        
        // 1. Authorization 헤더에서 JWT 추출
        String token = extractToken(request);
        
        // 2. 토큰 검증 및 인증 설정
        if (token != null && jwtProvider.validateToken(token)) {
            // 3. 토큰에서 사용자 정보 추출
            Long userId = jwtProvider.getUserId(token);
            String role = jwtProvider.getRole(token);
            
            // 4. Authentication 객체 생성
            UsernamePasswordAuthenticationToken authentication =
                new UsernamePasswordAuthenticationToken(
                    userId,  // principal
                    null,    // credentials (JWT 사용 시 불필요)
                    List.of(new SimpleGrantedAuthority("ROLE_" + role))
                );
            
            // 5. SecurityContext에 인증 정보 저장
            SecurityContextHolder.getContext().setAuthentication(authentication);
        }
        
        // 6. 다음 필터로 진행
        filterChain.doFilter(request, response);
    }
    
    private String extractToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
```

## 꼬리 질문 예상
- OncePerRequestFilter를 상속한 이유는?
- 토큰이 유효하지 않을 때 어떻게 처리하나요?

## 참고
- [[Spring-Security-필터체인]]
- [[bizsync-JWT-AccessRefreshToken-면접]]
