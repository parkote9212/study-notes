# [Spring Security 3/5] JWT 토큰 구조와 동작 원리

🏷️기술 카테고리: Security, Spring
💡핵심키워드: #JWT, #설정관리, #환경변수
💼 면접 빈출도: 최상
⚖️ 의사결정(A vs B): Yes
날짜: 2026년 1월 16일 오후 8:27
📅 다음 복습일: 2026년 1월 21일

# 1. Abstract: 핵심 요약

> **JWT(JSON Web Token)**는 당사자 간에 정보를 안전하게 전달하기 위한 **자체 포함형 (Self-contained)** 토큰입니다. 세션 없이 **Stateless** 인증을 구현할 수 있어 REST API와 마이크로서비스 환경에 적합합니다.
> 

**핵심 원칙**:

- 토큰 자체에 모든 정보 포함 (DB 조회 불필요)
- 서명으로 무결성 보장 (위변조 방지)
- Stateless 서버 구축 (수평 확장 용이)

---

# 2. Technical Deep Dive: JWT 구조

## 2.1 3부분 구조

```
Header.Payload.Signature
```

### Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload

```json
{
  "sub": "user123",
  "name": "John Doe",
  "iat": 1516239022,
  "exp": 1516242622
}
```

### Signature

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

---

## 2.2 동작 원리

### 로그인 흐름

```
1. 클라이언트: POST /login {username, password}
    ↓
2. 서버: 인증 처리
    ↓
3. 서버: JWT 생성 (Header + Payload + Signature)
    ↓
4. 서버: 토큰 반환
    ↓
5. 클라이언트: localStorage 또는 메모리에 저장
```

### API 요청 흐름

```
1. 클라이언트: GET /api/users
   Authorization: Bearer <JWT>
    ↓
2. 서버: JWT 추출
    ↓
3. 서버: 서명 검증 (Secret Key로)
    ↓
4. 서버: Payload 파싱 (sub, exp 확인)
    ↓
5. 서버: 인증 성공 → API 응답
```

---

# 3. Critical Thinking: 의사결정

## ⚖️ JWT vs Session

| 구분 | JWT | Session |
| --- | --- | --- |
| **저장 위치** | 클라이언트 | 서버 |
| **확장성** | 높음 | 낮음 |
| **보안** | XSS 취약 | CSRF 취약 |
| **서버 부하** | 낮음 | 높음 (메모리) |

**Decision**: REST API는 **JWT**, SSR 웹은 **Session**

---

## ⚖️ Access Token vs Refresh Token

**Access Token**:

- 짧은 수명 (15분)
- API 요청 시 사용

**Refresh Token**:

- 긴 수명 (7일)
- Access Token 재발급용
- DB에 저장 권장

---

# 4. 보안 모범 사례

## 4.1 Secret Key 관리

```yaml
# ❌ Bad
jwt:
  secret: mySecretKey123

# ✅ Good
jwt:
  secret: ${JWT_SECRET}  # 환경변수
```

## 4.2 토큰 만료 시간

```java
long ACCESS_TOKEN_VALIDITY = 15 * 60 * 1000;   // 15분
long REFRESH_TOKEN_VALIDITY = 7 * 24 * 60 * 60 * 1000;  // 7일
```

## 4.3 HttpOnly Cookie

```java
response.addCookie(createCookie("refreshToken", token, true));

private Cookie createCookie(String name, String value, boolean httpOnly) {
    Cookie cookie = new Cookie(name, value);
    cookie.setHttpOnly(httpOnly);  // XSS 방어
    cookie.setSecure(true);        // HTTPS만
    cookie.setPath("/");
    return cookie;
}
```

---

# 5. Interview Readiness

## ▶ Q1: JWT는 어떻게 동작하나요?

**A**: JWT는 Header, Payload, Signature 3부분으로 구성됩니다. 클라이언트가 로그인하면 서버는 사용자 정보를 Payload에 담고, Secret Key로 Signature를 생성하여 JWT를 발급합니다. 이후 클라이언트는 API 요청 시 Authorization 헤더에 JWT를 포함하고, 서버는 Signature를 검증하여 인증합니다. DB 조회 없이 토큰만으로 인증이 가능하므로 Stateless하고 확장성이 높습니다.

---

## ▶ Q2: JWT의 단점은?

**A**:

1. **토큰 탈취 시 대응 어려움**: 토큰이 탈취되면 만료될 때까지 악용 가능
2. **Payload 크기**: 모든 정보를 포함하므로 크기가 콤
3. **즉각적인 권한 변경 불가**: 토큰에 권한이 고정되어 있어서 동적 변경 어려움

**해결책**:

- Access Token 짧게, Refresh Token 길게
- Refresh Token은 DB에 저장하여 취소 가능
- Redis로 Blacklist 관리

---

**작성일**: 2026-01-16  

**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)