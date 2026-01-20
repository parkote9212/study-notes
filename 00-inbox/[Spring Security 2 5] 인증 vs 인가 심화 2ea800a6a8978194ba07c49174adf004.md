# [Spring Security 2/5] 인증 vs 인가 심화

🏷️기술 카테고리: Security, Spring
💡핵심키워드: #디자인패턴, #아키텍처
💼 면접 빈출도: 최상
⚖️ 의사결정(A vs B): Yes
날짜: 2026년 1월 16일 오후 8:26
📅 다음 복습일: 2026년 1월 21일

# 1. Abstract: 핵심 요약

> Spring Security의 **인증(Authentication)**과 **인가(Authorization)**는 보안의 양대 축입니다. 인증은 "누구인가"를, 인가는 "무엇을 할 수 있는가"를 결정합니다.
> 

**핵심 원칙**:

- 인증 없이 인가는 불가능 (먼저 누구인지 알아야 권한 확인 가능)
- 인증은 한 번, 인가는 여러 번 (요청마다 권한 검증)
- 최소 권한 원칙 (Principle of Least Privilege)

---

# 2. Technical Deep Dive: 인증 메커니즘

## 2.1 AuthenticationManager 동작 원리

```java
public interface AuthenticationManager {
    Authentication authenticate(Authentication authentication)
        throws AuthenticationException;
}
```

### 인증 흐름

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

---

## 2.2 UserDetailsService 구현 전략

### 기본 구현

```java
@Service
@RequiredArgsConstructor
public class UserDetailsServiceImpl implements UserDetailsService {

    private final UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String username)
        throws UsernameNotFoundException {
        
        // 1. DB에서 사용자 조회
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException(
                "User not found: " + username));
        
        // 2. Spring Security의 UserDetails 객체로 변환
        return [org.springframework.security](http://org.springframework.security).core.userdetails.User
            .withUsername(user.getUsername())
            .password(user.getPassword())  // 이미 암호화된 비밀번호
            .authorities(getAuthorities(user.getRoles()))
            .accountExpired(false)
            .accountLocked(false)
            .credentialsExpired(false)
            .disabled(false)
            .build();
    }

    private Collection<? extends GrantedAuthority> getAuthorities(
        Set<Role> roles) {
        return [roles.stream](http://roles.stream)()
            .map(role -> new SimpleGrantedAuthority(
                "ROLE_" + role.getName()))
            .collect(Collectors.toList());
    }
}
```

### 커스텀 UserDetails 구현

```java
@Getter
public class CustomUserDetails implements UserDetails {

    private final User user;

    public CustomUserDetails(User user) {
        this.user = user;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return user.getRoles().stream()
            .map(role -> new SimpleGrantedAuthority("ROLE_" + role))
            .collect(Collectors.toList());
    }

    @Override
    public String getPassword() {
        return user.getPassword();
    }

    @Override
    public String getUsername() {
        return user.getUsername();
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return !user.isLocked();
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return user.isEnabled();
    }

    // 추가적인 비즈니스 로직
    public Long getUserId() {
        return user.getId();
    }

    public String getEmail() {
        return user.getEmail();
    }
}
```

---

## 2.3 PasswordEncoder 사용법

### BCrypt 암호화

```java
@Configuration
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### 회원가입 시 비밀번호 암호화

```java
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public void registerUser(SignUpRequest request) {
        // ❌ 잘못된 방법
        // User user = new User(request.getUsername(), 
        //                       request.getPassword());

        // ✅ 올바른 방법
        User user = User.builder()
            .username(request.getUsername())
            .password(passwordEncoder.encode(request.getPassword()))
            .email(request.getEmail())
            .role("USER")
            .build();

        [userRepository.save](http://userRepository.save)(user);
    }
}
```

### 비밀번호 검증

```java
// Spring Security가 자동으로 처리하지만, 수동 검증이 필요한 경우:

public boolean checkPassword(String rawPassword, String encodedPassword) {
    return passwordEncoder.matches(rawPassword, encodedPassword);
}

// 예: 비밀번호 변경 시 기존 비밀번호 확인
@PutMapping("/password")
public ResponseEntity<Void> changePassword(
    @RequestBody PasswordChangeRequest request) {
    
    User user = getCurrentUser();
    
    if (!passwordEncoder.matches(
        request.getOldPassword(), 
        user.getPassword())) {
        throw new BadCredentialsException("기존 비밀번호가 일치하지 않습니다");
    }
    
    user.changePassword(passwordEncoder.encode(request.getNewPassword()));
    [userRepository.save](http://userRepository.save)(user);
    
    return ResponseEntity.ok().build();
}
```

---

# 3. Critical Thinking: 인가 전략 비교

## ⚖️ 의사결정 1: Role vs Authority

### Role 기반 (RBAC - Role Based Access Control)

```java
.authorizeHttpRequests(auth -> auth
    .requestMatchers("/admin/**").hasRole("ADMIN")
    .requestMatchers("/manager/**").hasRole("MANAGER")
    .requestMatchers("/user/**").hasRole("USER")
)
```

**장점**:

- 간단하고 직관적
- 대부분의 애플리케이션에 적합

**단점**:

- 세밀한 권한 제어 어려움
- 역할이 많아지면 관리 복잡

---

### Authority 기반 (Fine-grained Control)

```java
.authorizeHttpRequests(auth -> auth
    .requestMatchers([HttpMethod.POST](http://HttpMethod.POST), "/api/posts")
        .hasAuthority("WRITE_PRIVILEGE")
    .requestMatchers(HttpMethod.DELETE, "/api/posts/**")
        .hasAuthority("DELETE_PRIVILEGE")
    .requestMatchers(HttpMethod.GET, "/api/posts")
        .hasAuthority("READ_PRIVILEGE")
)
```

**장점**:

- 세밀한 권한 제어
- HTTP 메서드별 권한 분리

**단점**:

- 설정이 복잡
- 권한이 많아지면 관리 어려움

---

### 하이브리드 전략 (Role + Authority)

```java
@Entity
public class User {
    @ManyToMany
    private Set<Role> roles;  // ADMIN, MANAGER, USER
}

@Entity
public class Role {
    private String name;
    
    @ManyToMany
    private Set<Privilege> privileges;  // READ, WRITE, DELETE
}

@Entity
public class Privilege {
    private String name;  // READ_PRIVILEGE, WRITE_PRIVILEGE
}
```

```java
// UserDetailsService 구현
@Override
public UserDetails loadUserByUsername(String username) {
    User user = userRepository.findByUsername(username)
        .orElseThrow(...);
    
    return [org.springframework.security](http://org.springframework.security).core.userdetails.User
        .withUsername(user.getUsername())
        .password(user.getPassword())
        .authorities(getAuthorities(user))  // Role + Privilege
        .build();
}

private Collection<? extends GrantedAuthority> getAuthorities(User user) {
    List<GrantedAuthority> authorities = new ArrayList<>();
    
    // 1. Role 추가
    for (Role role : user.getRoles()) {
        authorities.add(new SimpleGrantedAuthority(
            "ROLE_" + role.getName()));
        
        // 2. 각 Role에 포함된 Privilege 추가
        for (Privilege privilege : role.getPrivileges()) {
            authorities.add(new SimpleGrantedAuthority(
                privilege.getName()));
        }
    }
    
    return authorities;
}
```

**장점**:

- Role로 대분류, Privilege로 세분화
- 유연하고 확장 가능

**결론**: 소규모 프로젝트는 **Role**, 대규모는 **Role + Privilege**

---

## ⚖️ 의사결정 2: URL 기반 vs 메서드 기반 보안

### URL 기반 (SecurityFilterChain)

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) {
    http.authorizeHttpRequests(auth -> auth
        .requestMatchers("/admin/**").hasRole("ADMIN")
        .requestMatchers("/api/**").authenticated()
        .anyRequest().permitAll()
    );
    return [http.build](http://http.build)();
}
```

**장점**:

- 한 곳에서 전체 보안 정책 관리
- URL 패턴 기반 일괄 설정

**단점**:

- 복잡한 URL 패턴 관리 어려움
- 비즈니스 로직과 분리

---

### 메서드 기반 (@PreAuthorize, @Secured)

```java
@RestController
@RequestMapping("/api/posts")
public class PostController {

    @PreAuthorize("hasRole('USER')")
    @PostMapping
    public ResponseEntity<Post> createPost(@RequestBody PostRequest request) {
        // ...
    }

    @PreAuthorize("hasRole('ADMIN') or @postService.isOwner(#id, principal)")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePost(@PathVariable Long id) {
        // ...
    }

    @PreAuthorize("hasAuthority('READ_PRIVILEGE')")
    @GetMapping
    public ResponseEntity<List<Post>> getPosts() {
        // ...
    }
}
```

```java
// SecurityConfig에 활성화 필요
@Configuration
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {
    // ...
}
```

```java
// 커스텀 권한 검증 서비스
@Service
public class PostService {

    public boolean isOwner(Long postId, Principal principal) {
        Post post = postRepository.findById(postId)
            .orElseThrow(...);
        return post.getAuthor().getUsername()
            .equals(principal.getName());
    }
}
```

**장점**:

- 비즈니스 로직과 가까운 곳에 보안 설정
- SpEL로 복잡한 조건 표현 가능
- 메서드별 세밀한 제어

**단점**:

- 보안 설정이 코드 전체에 분산
- 전체 보안 정책 파악 어려움

**결론**: **URL 기반 + 메서드 기반 병행** (이중 방어)

---

# 4. Project Case Study: 실무 적용

## 🏗️ 블로그 플랫폼 - 다단계 권한 체계

**S (Situation)**:

- 일반 사용자, 작성자, 에디터, 관리자 4단계 권한
- 게시글 CRUD 권한이 각각 다름

**T (Task)**:

- Role 기반 기본 보안 + 메서드 레벨 세밀 제어

**A (Action)**:

```java
// 1. Entity 설계
@Entity
public class User {
    @Id @GeneratedValue
    private Long id;
    
    private String username;
    private String password;
    
    @Enumerated(EnumType.STRING)
    private UserRole role;  // USER, AUTHOR, EDITOR, ADMIN
}

public enum UserRole {
    USER,     // 읽기만
    AUTHOR,   // 작성 + 자기 글 수정/삭제
    EDITOR,   // 모든 글 수정
    ADMIN     // 전체 관리
}
```

```java
// 2. SecurityConfig
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) {
    http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/", "/posts").permitAll()
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().authenticated()
        );
    return [http.build](http://http.build)();
}
```

```java
// 3. Controller + Method Security
@RestController
@RequestMapping("/api/posts")
public class PostController {

    @GetMapping
    public List<Post> getPosts() {
        return postService.findAll();
    }

    @PreAuthorize("hasAnyRole('AUTHOR', 'EDITOR', 'ADMIN')")
    @PostMapping
    public Post createPost(@RequestBody PostRequest request) {
        return postService.create(request);
    }

    @PreAuthorize(
        "hasRole('ADMIN') or " +
        "hasRole('EDITOR') or " +
        "(hasRole('AUTHOR') and @postService.isAuthor(#id, principal))"
    )
    @PutMapping("/{id}")
    public Post updatePost(
        @PathVariable Long id,
        @RequestBody PostRequest request) {
        return postService.update(id, request);
    }

    @PreAuthorize(
        "hasRole('ADMIN') or " +
        "(hasRole('AUTHOR') and @postService.isAuthor(#id, principal))"
    )
    @DeleteMapping("/{id}")
    public void deletePost(@PathVariable Long id) {
        postService.delete(id);
    }
}
```

```java
// 4. Custom Authorization Service
@Service
public class PostService {

    public boolean isAuthor(Long postId, Principal principal) {
        Post post = postRepository.findById(postId)
            .orElseThrow(() -> new PostNotFoundException(postId));
        
        return post.getAuthor().getUsername()
            .equals(principal.getName());
    }
}
```

**R (Result)**:

- ✅ 4단계 권한체계 성공적 구현
- ✅ URL 기반 + 메서드 기반 이중 방어
- ✅ 자기 글만 수정/삭제 가능하도록 세밀한 제어

---

# 5. Interview Readiness

## ▶ Q1: 인증과 인가를 분리해야 하는 이유는?

**A**: 인증과 인가는 분리되어야 하는 다섯 가지 이유가 있습니다:

1. **관심사의 분리**: 인증은 "누구인가"를 확인하고, 인가는 "무엇을 할 수 있는가"를 결정합니다. 이 두 가지는 서로 다른 책임입니다.
2. **재사용성**: 한 번 인증된 사용자는 여러 리소스에 접근할 때마다 다시 인증할 필요가 없습니다. 인가만 각 요청마다 확인하면 됩니다.
3. **세밀한 제어**: 같은 사용자라도 리소스별로 다른 권한을 가질 수 있습니다.
4. **보안**: 인증이 성공해도 권한이 없으면 접근을 차단할 수 있습니다.

---

## ▶ Q2: hasRole vs hasAuthority 차이는?

**A**:

| 구분 | hasRole | hasAuthority |
| --- | --- | --- |
| **Prefix** | 자동 추가 (ROLE_) | 없음 |
| **사용법** | hasRole("ADMIN") | hasAuthority("ROLE_ADMIN") |
| **의도** | 대분류 (역할) | 세분류 (권한) |

```java
// 내부적으로는 동일하게 동작
hasRole("ADMIN")  // → "ROLE_ADMIN" 권한 확인
hasAuthority("ROLE_ADMIN")  // → "ROLE_ADMIN" 권한 확인

// 권장 사항
hasRole("역할")  // 큰 분류
hasAuthority("세부_권한")  // 세부 제어
```

---

## ▶ Q3: @PreAuthorize vs @Secured 차이는?

**A**:

| 기능 | @PreAuthorize | @Secured |
| --- | --- | --- |
| **SpEL 지원** | O (hasRole, and, or 등) | X |
| **복잡한 조건** | O | X |
| **활성화** | @EnableMethodSecurity | @EnableGlobalMethodSecurity |

```java
// @PreAuthorize (추천)
@PreAuthorize("hasRole('ADMIN') or @postService.isOwner(#id, principal)")
public void deletePost(Long id) {}

// @Secured (레거시)
@Secured({"ROLE_ADMIN", "ROLE_EDITOR"})
public void editPost() {}
```

**결론**: **@PreAuthorize 사용 추천** (SpEL 지원, 더 유연)

---

## 🔑 핵심 체크리스트

- [ ]  인증은 한 번, 인가는 여러 번
- [ ]  UserDetailsService로 사용자 조회
- [ ]  PasswordEncoder로 회원가입 시 암호화
- [ ]  hasRole은 자동으로 ROLE_ 추가
- [ ]  Role + Privilege 하이브리드 전략 추천
- [ ]  URL 기반 + 메서드 기반 이중 방어
- [ ]  @PreAuthorize가 @Secured보다 강력

---

**작성일**: 2026-01-16  

**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)