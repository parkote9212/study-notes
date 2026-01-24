---
tags:
  - interview
  - spring-security
  - jwt
  - bizsync
  - project
created: 2025-01-23
difficulty: 중상
---

# BizSync - JWT Access Refresh Token 분리

## 질문
> JWT 기반 인증을 구현할 때 Access Token과 Refresh Token을 분리한 이유는 무엇인가요?

## 핵심 답변 (3줄)
1. Access Token은 짧은 만료시간(1시간)으로 보안성을 높이고, Refresh Token은 긴 만료시간(7일)으로 사용자 편의성을 제공합니다
2. Access Token이 탈취되어도 피해 범위를 제한할 수 있고, Refresh Token으로 재발급하여 지속적인 로그인 상태를 유지할 수 있습니다
3. Stateless 아키텍처를 유지하면서도 토큰 갱신 메커니즘을 통해 보안과 UX의 균형을 맞출 수 있습니다

## 상세 설명
BizSync에서는 JWT 토큰을 Access Token과 Refresh Token으로 분리하여 구현했습니다. Access Token은 API 요청 시 인증에 사용되며 1시간의 짧은 만료시간을 가집니다. 반면 Refresh Token은 7일의 긴 만료시간을 가지며 Access Token 재발급에만 사용됩니다.

이러한 설계의 핵심은 보안과 사용성의 균형입니다. Access Token의 짧은 수명은 토큰이 탈취되더라도 공격자가 사용할 수 있는 시간을 제한합니다.

JwtProvider 클래스에서 각 토큰의 타입을 claim에 명시("access", "refresh")하여 구분하고, 토큰 검증 시 isAccessToken()과 isRefreshToken() 메서드로 타입을 확인합니다.

## 코드 예시
```java
// JwtProvider.java
public String createToken(Long userId, Role role) {
    Date now = new Date();
    Date expirationDate = new Date(now.getTime() + expiration); // 1시간
    
    return Jwts.builder()
            .setSubject(String.valueOf(userId))
            .claim("role", role.name())
            .claim("type", "access")
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
            .claim("type", "refresh")
            .setIssuedAt(now)
            .setExpiration(expirationDate)
            .signWith(secretKey, SignatureAlgorithm.HS256)
            .compact();
}
```

## 꼬리 질문 예상
- Refresh Token을 어디에 저장하는 것이 안전한가요?
- RTR (Refresh Token Rotation) 방식은 무엇인가요?

## 참고
- [[JWT-토큰-보안-베스트프랙티스]]
- [[bizsync-SpringSecurity-Stateless-면접]]
