---
tags:
  - study
  - security
  - spring
  - springsecurity
  - rbac
  - 권한관리
created: 2026-01-23
difficulty: 상
---
# SpringSecurity-인증인가-Role기반권한

🏷️기술 카테고리: Security, Spring
💡핵심키워드: #SpringSecurity, #RBAC, #권한관리
💼 면접 빈출도: 최상

# 1. Abstract: 핵심 요약

Spring Security의 **인증(Authentication)**과 **인가(Authorization)**는 보안의 양대 축입니다. 인증은 "누구인가"를, 인가는 "무엇을 할 수 있는가"를 결정합니다.

**핵심 원칙**:
- 인증 없이 인가는 불가능
- 인증은 한 번, 인가는 여러 번
- 최소 권한 원칙 (Principle of Least Privilege)

# 2. 인증 메커니즘

## 2.1 AuthenticationManager 동작 원리

```
1. 사용자 로그인 시도 (username + password)
    ↓
2. UsernamePasswordAuthenticationToken 생성
    ↓
3. AuthenticationManager.authenticate() 호출
    ↓
4. ProviderManager가 적절한 AuthenticationProvider 선택
    ↓
5. DaoAuthenticationProvider가 UserDetailsService 호출
    ↓
6. DB에서 사용자 정보 조회
    ↓
7. PasswordEncoder로 비밀번호 검증
    ↓
8. 성공 시 Authentication 객체 반환 (authorities 포함)
    ↓
9. SecurityContext에 저장
```

## 2.2 PasswordEncoder

```java
@Configuration
public class SecurityConfig {
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}

// 회원가입 시
@Service
@RequiredArgsConstructor
public class UserService {
    private final PasswordEncoder passwordEncoder;
    
    public void registerUser(SignUpRequest request) {
        User user = User.builder()
            .username(request.getUsername())
            .password(passwordEncoder.encode(request.getPassword()))
            .role("USER")
            .build();
        userRepository.save(user);
    }
}
```

# 3. 인가 전략

## 3.1 Role 기반 (RBAC)

```java
.authorizeHttpRequests(auth -> auth
    .requestMatchers("/admin/**").hasRole("ADMIN")
    .requestMatchers("/manager/**").hasRole("MANAGER")
    .requestMatchers("/user/**").hasRole("USER")
)
```

**장점**: 간단하고 직관적
**단점**: 세밀한 권한 제어 어려움

## 3.2 Authority 기반 (세밀한 제어)

```java
.authorizeHttpRequests(auth -> auth
    .requestMatchers(HttpMethod.POST, "/api/posts")
        .hasAuthority("WRITE_PRIVILEGE")
    .requestMatchers(HttpMethod.DELETE, "/api/posts/**")
        .hasAuthority("DELETE_PRIVILEGE")
)
```

## 3.3 하이브리드 전략 (Role + Authority)

```java
@Entity
public class User {
    @ManyToMany
    private Set<Role> roles;  // ADMIN, USER
}

@Entity
public class Role {
    private String name;
    
    @ManyToMany
    private Set<Privilege> privileges;  // READ, WRITE, DELETE
}
```

# 4. 메서드 보안

```java
@Configuration
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {
    // ...
}

@RestController
public class PostController {

    @PreAuthorize("hasRole('USER')")
    @PostMapping
    public Post createPost(@RequestBody PostRequest request) {
        // ...
    }

    @PreAuthorize("hasRole('ADMIN') or @postService.isOwner(#id, principal)")
    @DeleteMapping("/{id}")
    public void deletePost(@PathVariable Long id) {
        // ...
    }
}
```

# 5. Interview Readiness

## Q1: hasRole vs hasAuthority 차이는?

**A**:
- `hasRole("ADMIN")`: 자동으로 "ROLE_ADMIN" 권한 확인
- `hasAuthority("ROLE_ADMIN")`: 그대로 "ROLE_ADMIN" 권한 확인

내부적으로는 동일하게 동작하지만, hasRole은 대분류(역할), hasAuthority는 세밀한 권한 제어에 사용합니다.

## Q2: @PreAuthorize vs @Secured 차이는?

**A**:
- `@PreAuthorize`: SpEL 지원, 복잡한 조건 표현 가능
- `@Secured`: SpEL 미지원, 단순 역할만

`@PreAuthorize` 사용을 권장합니다.

## Q3: URL 기반 vs 메서드 기반 보안?

**A**: 두 가지를 병행하는 것이 가장 안전합니다.
- URL 기반: 전체 보안 정책을 한 곳에서 관리
- 메서드 기반: 비즈니스 로직과 가까운 곳에서 세밀하게 제어

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
