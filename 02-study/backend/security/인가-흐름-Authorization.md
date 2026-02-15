---
tags:
  - study
  - spring
  - security
  - authorization
created: 2025-02-08
---

# 인가 흐름 Authorization

## 한 줄 요약
> 인가(Authorization)는 인증된 사용자가 특정 리소스에 접근할 권한이 있는지 확인하는 과정으로, FilterSecurityInterceptor가 URL 패턴과 권한을 매칭하여 접근을 제어한다.

## 상세 설명

### 인가란?
- **"무엇을 할 수 있는가?"**를 확인
- 인증 완료 후 권한(Authority/Role) 검사
- 접근 제어 결정 (Access Decision)

### 인증 vs 인가

```
인증 (Authentication)          인가 (Authorization)
     ↓                              ↓
  로그인                         권한 확인
     ↓                              ↓
SecurityContext 저장          접근 허용/거부
```

### 인가 방식

| 방식 | 설명 | 예시 |
|-----|------|------|
| **URL 기반** | 요청 URL로 권한 확인 | /admin/** → ROLE_ADMIN |
| **메서드 기반** | 메서드 실행 전/후 권한 확인 | @PreAuthorize |
| **도메인 기반** | 엔티티 소유자 확인 | 내 게시글만 수정 |

### 권한 표현 방식

```java
// Role (역할): ROLE_ 접두사
ROLE_USER, ROLE_ADMIN, ROLE_MANAGER

// Authority (권한): 접두사 없음
READ, WRITE, DELETE
ROLE_USER  // Authority로도 사용 가능
```

### 인가 흐름

```
1. 요청 → FilterSecurityInterceptor
   ↓
2. SecurityContext에서 Authentication 조회
   ↓
3. ConfigAttribute 조회 (URL 패턴 매칭)
   ↓
4. AccessDecisionManager에게 권한 검사 위임
   ↓
5. AccessDecisionVoter들이 투표
   ↓
6. 접근 허용/거부 결정
   ↓
7. 거부 시 AccessDeniedException 발생
```

### AccessDecisionVoter 투표 전략

| 전략 | 설명 |
|-----|------|
| **AffirmativeBased** (기본) | 1명이라도 허용하면 통과 |
| **ConsensusBased** | 과반수 허용 시 통과 |
| **UnanimousBased** | 만장일치 허용 시 통과 |

## 코드 예시

```java
// 1. URL 기반 인가 설정
@Configuration
@EnableWebSecurity
public class UrlSecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                // 공개 페이지
                .requestMatchers("/", "/public/**", "/login").permitAll()
                
                // 특정 Role 필요
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .requestMatchers("/manager/**").hasRole("MANAGER")
                
                // 여러 Role 중 하나
                .requestMatchers("/staff/**")
                    .hasAnyRole("ADMIN", "MANAGER", "STAFF")
                
                // 특정 Authority 필요
                .requestMatchers("/api/users/**").hasAuthority("USER_READ")
                .requestMatchers("/api/orders/**")
                    .hasAnyAuthority("ORDER_READ", "ORDER_WRITE")
                
                // HTTP 메서드별 권한
                .requestMatchers(HttpMethod.GET, "/api/**").hasAuthority("READ")
                .requestMatchers(HttpMethod.POST, "/api/**").hasAuthority("WRITE")
                .requestMatchers(HttpMethod.DELETE, "/api/**").hasAuthority("DELETE")
                
                // 나머지는 인증 필요
                .anyRequest().authenticated()
            );
        
        return http.build();
    }
}

// 2. 메서드 레벨 보안 (@PreAuthorize, @PostAuthorize)
@Configuration
@EnableMethodSecurity  // @EnableGlobalMethodSecurity는 deprecated
public class MethodSecurityConfig {
}

@Service
public class OrderService {
    
    // 실행 전 권한 확인
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteAllOrders() {
        // ADMIN만 실행 가능
    }
    
    // SpEL로 복잡한 조건
    @PreAuthorize("hasRole('ADMIN') or #order.userId == authentication.principal.id")
    public void updateOrder(Order order) {
        // ADMIN이거나 주문자 본인만 수정 가능
    }
    
    // 실행 후 반환값 검증
    @PostAuthorize("returnObject.userId == authentication.principal.id")
    public Order getOrder(Long orderId) {
        Order order = orderRepository.findById(orderId).get();
        // 자신의 주문만 조회 가능 (반환 전 검증)
        return order;
    }
    
    // 파라미터 검증
    @PreAuthorize("#userId == authentication.principal.id")
    public void cancelOrder(Long orderId, Long userId) {
        // userId가 본인 ID와 같을 때만 실행
    }
}

// 3. @Secured (단순한 역할 체크)
@Service
public class UserService {
    
    @Secured("ROLE_ADMIN")  // ROLE_ 접두사 필수
    public void deleteUser(Long userId) {
        // ADMIN만 실행 가능
    }
    
    @Secured({"ROLE_ADMIN", "ROLE_MANAGER"})
    public void updateUser(User user) {
        // ADMIN 또는 MANAGER
    }
}

// 4. 커스텀 권한 표현식
@Component("customSecurity")
public class CustomSecurityExpression {
    
    public boolean isOwner(Long userId) {
        Authentication auth = SecurityContextHolder.getContext()
                .getAuthentication();
        CustomUserDetails userDetails = (CustomUserDetails) auth.getPrincipal();
        return userDetails.getId().equals(userId);
    }
    
    public boolean hasPermission(String resource, String action) {
        Authentication auth = SecurityContextHolder.getContext()
                .getAuthentication();
        
        // 권한 테이블에서 조회
        return permissionRepository.existsByUserIdAndResourceAndAction(
            getUserId(auth), resource, action
        );
    }
}

// 사용
@PreAuthorize("@customSecurity.isOwner(#userId)")
public void updateProfile(Long userId, ProfileDto dto) {
    // 소유자만 수정 가능
}

@PreAuthorize("@customSecurity.hasPermission('ORDER', 'DELETE')")
public void deleteOrder(Long orderId) {
    // 동적 권한 체크
}

// 5. 계층적 권한 (Hierarchical Roles)
@Configuration
public class RoleHierarchyConfig {
    
    @Bean
    public RoleHierarchy roleHierarchy() {
        RoleHierarchyImpl hierarchy = new RoleHierarchyImpl();
        
        // ADMIN > MANAGER > USER
        hierarchy.setHierarchy(
            "ROLE_ADMIN > ROLE_MANAGER\n" +
            "ROLE_MANAGER > ROLE_USER"
        );
        
        return hierarchy;
    }
}

// ADMIN은 MANAGER, USER 권한도 자동으로 가짐
@PreAuthorize("hasRole('USER')")  // ADMIN도 통과

// 6. 도메인 객체 보안 (ACL - Access Control List)
@Service
public class PostService {
    
    // 게시글 작성자만 수정 가능
    @PreAuthorize("@postSecurity.isAuthor(#postId)")
    public void updatePost(Long postId, PostDto dto) {
        Post post = postRepository.findById(postId).get();
        post.update(dto);
    }
}

@Component("postSecurity")
@RequiredArgsConstructor
public class PostSecurity {
    
    private final PostRepository postRepository;
    
    public boolean isAuthor(Long postId) {
        Authentication auth = SecurityContextHolder.getContext()
                .getAuthentication();
        CustomUserDetails userDetails = (CustomUserDetails) auth.getPrincipal();
        
        Post post = postRepository.findById(postId)
                .orElse(null);
        
        if (post == null) {
            return false;
        }
        
        return post.getAuthorId().equals(userDetails.getId());
    }
}

// 7. AccessDeniedException 처리
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponse> handleAccessDenied(
            AccessDeniedException e) {
        
        return ResponseEntity
                .status(HttpStatus.FORBIDDEN)
                .body(new ErrorResponse("접근 권한이 없습니다."));
    }
}

// 8. 동적 권한 관리
@Entity
public class Permission {
    
    @Id
    @GeneratedValue
    private Long id;
    
    private Long userId;
    private String resource;  // ORDER, USER, PRODUCT
    private String action;    // READ, WRITE, DELETE
}

@Service
@RequiredArgsConstructor
public class DynamicAuthorizationService {
    
    private final PermissionRepository permissionRepository;
    
    public boolean hasPermission(Long userId, String resource, String action) {
        return permissionRepository.existsByUserIdAndResourceAndAction(
            userId, resource, action
        );
    }
}

// 사용
@PreAuthorize("@dynamicAuthorizationService.hasPermission(" +
              "authentication.principal.id, 'ORDER', 'DELETE')")
public void deleteOrder(Long orderId) {
    // 동적으로 권한 확인
}

// 9. IP 기반 접근 제어
@Configuration
public class IpSecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/admin/**")
                    .access(new WebExpressionAuthorizationManager(
                        "hasRole('ADMIN') and hasIpAddress('192.168.1.0/24')"
                    ))
            );
        
        return http.build();
    }
}

// 10. 시간 기반 접근 제어
@Component("timeSecurity")
public class TimeBasedSecurity {
    
    public boolean isBusinessHours() {
        LocalTime now = LocalTime.now();
        LocalTime start = LocalTime.of(9, 0);
        LocalTime end = LocalTime.of(18, 0);
        
        return now.isAfter(start) && now.isBefore(end);
    }
}

@PreAuthorize("@timeSecurity.isBusinessHours()")
public void businessHoursOnlyOperation() {
    // 업무 시간에만 실행
}

// 11. 커스텀 AccessDecisionVoter
public class CustomVoter implements AccessDecisionVoter<Object> {
    
    @Override
    public int vote(
            Authentication authentication,
            Object object,
            Collection<ConfigAttribute> attributes) {
        
        // 커스텀 투표 로직
        if (customCheck(authentication)) {
            return ACCESS_GRANTED;
        } else {
            return ACCESS_DENIED;
        }
    }
    
    @Override
    public boolean supports(ConfigAttribute attribute) {
        return true;
    }
    
    @Override
    public boolean supports(Class<?> clazz) {
        return true;
    }
}

// 12. 필터 레벨 권한 체크
public class CustomAuthorizationFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        Authentication auth = SecurityContextHolder.getContext()
                .getAuthentication();
        
        if (auth == null || !auth.isAuthenticated()) {
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }
        
        // 커스텀 권한 체크
        if (!hasRequiredPermission(auth, request)) {
            response.sendError(HttpServletResponse.SC_FORBIDDEN);
            return;
        }
        
        filterChain.doFilter(request, response);
    }
    
    private boolean hasRequiredPermission(
            Authentication auth, HttpServletRequest request) {
        // 권한 검증 로직
        return true;
    }
}
```

## 주의사항 / 함정

### 1. hasRole vs hasAuthority
```java
// ❌ hasRole에 ROLE_ 포함
.hasRole("ROLE_ADMIN")  // 실제로는 ROLE_ROLE_ADMIN

// ✅ hasRole은 접두사 자동 추가
.hasRole("ADMIN")  // ROLE_ADMIN

// ✅ hasAuthority는 그대로
.hasAuthority("ROLE_ADMIN")
```

### 2. URL 매칭 순서
```java
// ❌ anyRequest()가 먼저 오면 이후 무시
.anyRequest().authenticated()
.requestMatchers("/admin/**").hasRole("ADMIN")  // 무시됨!

// ✅ 구체적인 것부터 (순서 중요)
.requestMatchers("/admin/**").hasRole("ADMIN")
.anyRequest().authenticated()
```

### 3. @PreAuthorize 활성화 누락
```java
// ❌ @EnableMethodSecurity 없으면 동작 안 함
@PreAuthorize("hasRole('ADMIN')")
public void method() { }

// ✅ 반드시 활성화
@EnableMethodSecurity
@Configuration
public class SecurityConfig { }
```

### 4. SpEL 표현식 오타
```java
// ❌ 오타 → 런타임 에러
@PreAuthorize("hasRole('ADMON')")  // ADMIN 오타

// ✅ 테스트로 검증
@SpringBootTest
class SecurityTest {
    @Test
    void testAuthorization() {
        // 권한 체크 테스트
    }
}
```

### 5. 반환값 null 체크 누락
```java
// ❌ returnObject가 null이면 NullPointerException
@PostAuthorize("returnObject.userId == authentication.principal.id")
public Order getOrder(Long orderId) {
    return orderRepository.findById(orderId).orElse(null);  // null 가능!
}

// ✅ null 체크 추가
@PostAuthorize("returnObject != null and " +
               "returnObject.userId == authentication.principal.id")
public Order getOrder(Long orderId) {
    return orderRepository.findById(orderId).orElse(null);
}
```

### 6. 권한 계층 설정 누락
```java
// ❌ ADMIN이 USER 권한 없음
@PreAuthorize("hasRole('USER')")
public void userMethod() { }  // ADMIN도 막힘!

// ✅ RoleHierarchy 설정
@Bean
public RoleHierarchy roleHierarchy() {
    RoleHierarchyImpl hierarchy = new RoleHierarchyImpl();
    hierarchy.setHierarchy("ROLE_ADMIN > ROLE_USER");
    return hierarchy;
}
```

### 7. 메서드 시큐리티와 프록시
```java
// ❌ 같은 클래스 내부 호출 → 권한 체크 안 됨
@Service
public class OrderService {
    
    public void publicMethod() {
        this.securedMethod();  // 프록시 거치지 않음!
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    private void securedMethod() { }
}

// ✅ 다른 빈으로 분리
@Service
@RequiredArgsConstructor
public class OrderService {
    private final SecuredService securedService;
    
    public void publicMethod() {
        securedService.securedMethod();  // 프록시 적용됨
    }
}
```

## 관련 개념
- [[Spring-Security-아키텍처]]
- [[인증-흐름-Authentication]]
- [[필터체인-FilterChain]]

## 면접 질문

1. **인증과 인가의 차이는?**
   - 인증: 신원 확인 ("누구?")
   - 인가: 권한 확인 ("무엇을 할 수 있나?")

2. **hasRole과 hasAuthority의 차이는?**
   - hasRole: ROLE_ 접두사 자동 추가
   - hasAuthority: 입력한 그대로 사용

3. **@PreAuthorize와 @PostAuthorize의 차이는?**
   - @PreAuthorize: 메서드 실행 전 권한 확인
   - @PostAuthorize: 메서드 실행 후 반환값 기반 확인

4. **URL 기반 인가와 메서드 기반 인가의 차이는?**
   - URL 기반: FilterSecurityInterceptor, 요청 URL로 판단
   - 메서드 기반: @PreAuthorize, 메서드 파라미터/반환값으로 판단

5. **AccessDecisionManager의 투표 전략 3가지는?**
   - AffirmativeBased: 1명이라도 허용
   - ConsensusBased: 과반수 허용
   - UnanimousBased: 만장일치

6. **계층적 권한이 필요한 이유는?**
   - ADMIN이 USER 권한도 자동으로 가지도록
   - 권한 중복 설정 방지

7. **동적 권한은 어떻게 구현하나요?**
   - DB에 권한 테이블 관리
   - 커스텀 표현식(@customSecurity.hasPermission)

## 참고 자료
- Spring Security Reference - Authorization
- Baeldung Method Security
- https://docs.spring.io/spring-security/reference/servlet/authorization/index.html
