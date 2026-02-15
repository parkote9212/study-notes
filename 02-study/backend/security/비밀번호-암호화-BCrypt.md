---
tags:
  - study
  - spring
  - security
  - bcrypt
  - password
  - encryption
created: 2025-02-08
---

# 비밀번호 암호화 BCrypt

## 한 줄 요약
> BCrypt는 단방향 해시 함수로 비밀번호를 암호화하며, Salt와 Cost Factor를 통해 무차별 대입 공격(Brute Force)을 방어하고, Spring Security의 기본 PasswordEncoder로 사용된다.

## 상세 설명

### BCrypt란?
- **단방향 해시 함수**: 암호화만 가능, 복호화 불가
- **Salt 자동 생성**: 같은 비밀번호도 다른 해시값
- **Cost Factor**: 연산 시간 조절 (느리게 = 안전)

### 왜 BCrypt가 필요한가?
```java
// ❌ 평문 저장: DB 유출 시 모든 비밀번호 노출
user.setPassword("password123");

// ❌ MD5, SHA-1: 빠른 연산 → 무차별 대입 공격 취약
String hash = md5("password123");  // 레인보우 테이블 공격 가능

// ✅ BCrypt: 느린 연산 + Salt → 안전
String hash = BCrypt.hashpw("password123", BCrypt.gensalt());
// $2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
```

### BCrypt 해시 구조

```
$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
│  │ │   │                                                    │
│  │ │   └─ Salt (22자)                                      └─ Hash (31자)
│  │ └─ Cost Factor (10 = 2^10 = 1024번 반복)
│  └─ BCrypt 버전 (2a)
└─ 알고리즘 식별자 ($)
```

### BCrypt 특징

| 특징 | 설명 | 장점 |
|-----|------|------|
| **단방향** | 복호화 불가 | 탈취돼도 원본 알 수 없음 |
| **Salt** | 랜덤 값 추가 | 같은 비밀번호도 다른 해시 |
| **Cost Factor** | 반복 횟수 증가 | 무차별 대입 공격 방어 |
| **느린 연산** | 의도적으로 느림 | 대량 해시 생성 어려움 |

### Cost Factor

```
Cost 4  → 2^4  = 16번 반복   → 0.001초
Cost 10 → 2^10 = 1024번 반복 → 0.1초
Cost 12 → 2^12 = 4096번 반복 → 0.3초
Cost 15 → 2^15 = 32768번 반복 → 3초
```

## 코드 예시

```java
// 1. BCryptPasswordEncoder 빈 등록
@Configuration
public class PasswordEncoderConfig {
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
        // 기본 Cost Factor: 10
    }
}

// 2. Cost Factor 지정
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12);
    // Cost Factor: 12 (더 안전하지만 느림)
}

// 3. 회원가입 시 비밀번호 암호화
@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    public User registerUser(String username, String rawPassword) {
        // 1. 비밀번호 암호화
        String encodedPassword = passwordEncoder.encode(rawPassword);
        
        // 2. 사용자 저장
        User user = User.builder()
                .username(username)
                .password(encodedPassword)  // 암호화된 비밀번호
                .build();
        
        return userRepository.save(user);
    }
}

// 4. 로그인 시 비밀번호 검증
@Service
@RequiredArgsConstructor
public class AuthService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    public boolean login(String username, String rawPassword) {
        // 1. 사용자 조회
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));
        
        // 2. 비밀번호 검증
        return passwordEncoder.matches(rawPassword, user.getPassword());
        // matches(평문, 암호화된 비밀번호)
    }
}

// 5. UserDetailsService에서 자동 검증
@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {
    
    private final UserRepository userRepository;
    
    @Override
    public UserDetails loadUserByUsername(String username) 
            throws UsernameNotFoundException {
        
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));
        
        return org.springframework.security.core.userdetails.User.builder()
                .username(user.getUsername())
                .password(user.getPassword())  // 암호화된 비밀번호
                .roles(user.getRole())
                .build();
        // Spring Security가 자동으로 passwordEncoder.matches() 호출
    }
}

// 6. 비밀번호 변경
@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    public void changePassword(Long userId, String oldPassword, String newPassword) {
        User user = userRepository.findById(userId)
                .orElseThrow();
        
        // 1. 기존 비밀번호 확인
        if (!passwordEncoder.matches(oldPassword, user.getPassword())) {
            throw new BadCredentialsException("Wrong password");
        }
        
        // 2. 새 비밀번호 암호화
        String encodedNewPassword = passwordEncoder.encode(newPassword);
        
        // 3. 업데이트
        user.updatePassword(encodedNewPassword);
        userRepository.save(user);
    }
}

// 7. 비밀번호 재설정 (이메일 인증)
@Service
@RequiredArgsConstructor
public class PasswordResetService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final EmailService emailService;
    
    public void requestPasswordReset(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow();
        
        // 1. 랜덤 토큰 생성
        String resetToken = UUID.randomUUID().toString();
        
        // 2. 토큰 저장 (만료 시간: 1시간)
        user.setResetToken(resetToken);
        user.setResetTokenExpiry(LocalDateTime.now().plusHours(1));
        userRepository.save(user);
        
        // 3. 이메일 발송
        String resetLink = "https://example.com/reset-password?token=" + resetToken;
        emailService.sendPasswordResetEmail(email, resetLink);
    }
    
    public void resetPassword(String token, String newPassword) {
        // 1. 토큰으로 사용자 조회
        User user = userRepository.findByResetToken(token)
                .orElseThrow(() -> new IllegalArgumentException("Invalid token"));
        
        // 2. 토큰 만료 확인
        if (user.getResetTokenExpiry().isBefore(LocalDateTime.now())) {
            throw new IllegalArgumentException("Token expired");
        }
        
        // 3. 비밀번호 변경
        String encodedPassword = passwordEncoder.encode(newPassword);
        user.updatePassword(encodedPassword);
        
        // 4. 토큰 삭제
        user.setResetToken(null);
        user.setResetTokenExpiry(null);
        
        userRepository.save(user);
    }
}

// 8. 비밀번호 강도 검증
@Component
public class PasswordValidator {
    
    private static final int MIN_LENGTH = 8;
    private static final String PASSWORD_PATTERN = 
        "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$";
    
    public void validate(String password) {
        if (password == null || password.length() < MIN_LENGTH) {
            throw new IllegalArgumentException(
                "비밀번호는 최소 " + MIN_LENGTH + "자 이상이어야 합니다."
            );
        }
        
        if (!password.matches(PASSWORD_PATTERN)) {
            throw new IllegalArgumentException(
                "비밀번호는 대문자, 소문자, 숫자, 특수문자를 포함해야 합니다."
            );
        }
        
        // 일반적인 비밀번호 체크
        if (isCommonPassword(password)) {
            throw new IllegalArgumentException(
                "너무 흔한 비밀번호입니다."
            );
        }
    }
    
    private boolean isCommonPassword(String password) {
        List<String> commonPasswords = Arrays.asList(
            "password", "12345678", "qwerty", "admin"
        );
        return commonPasswords.contains(password.toLowerCase());
    }
}

// 9. 비밀번호 히스토리 (재사용 방지)
@Entity
public class PasswordHistory {
    
    @Id
    @GeneratedValue
    private Long id;
    
    @ManyToOne
    private User user;
    
    @Column(nullable = false)
    private String password;
    
    @Column(nullable = false)
    private LocalDateTime createdAt;
}

@Service
@RequiredArgsConstructor
public class PasswordHistoryService {
    
    private final PasswordHistoryRepository passwordHistoryRepository;
    private final PasswordEncoder passwordEncoder;
    
    private static final int HISTORY_SIZE = 5;  // 최근 5개 저장
    
    public void checkPasswordHistory(User user, String newPassword) {
        List<PasswordHistory> histories = passwordHistoryRepository
                .findTop5ByUserOrderByCreatedAtDesc(user);
        
        for (PasswordHistory history : histories) {
            if (passwordEncoder.matches(newPassword, history.getPassword())) {
                throw new IllegalArgumentException(
                    "최근 " + HISTORY_SIZE + "개 비밀번호는 재사용할 수 없습니다."
                );
            }
        }
    }
    
    public void addPasswordHistory(User user, String encodedPassword) {
        PasswordHistory history = new PasswordHistory();
        history.setUser(user);
        history.setPassword(encodedPassword);
        history.setCreatedAt(LocalDateTime.now());
        
        passwordHistoryRepository.save(history);
        
        // 오래된 히스토리 삭제
        deleteOldHistories(user);
    }
    
    private void deleteOldHistories(User user) {
        List<PasswordHistory> histories = passwordHistoryRepository
                .findByUserOrderByCreatedAtDesc(user);
        
        if (histories.size() > HISTORY_SIZE) {
            List<PasswordHistory> toDelete = histories.subList(
                HISTORY_SIZE, histories.size()
            );
            passwordHistoryRepository.deleteAll(toDelete);
        }
    }
}

// 10. 비밀번호 만료 정책
@Entity
public class User {
    
    @Column
    private LocalDateTime passwordChangedAt;
    
    @Column
    private int passwordExpirationDays = 90;  // 90일마다 변경
    
    public boolean isPasswordExpired() {
        if (passwordChangedAt == null) {
            return false;
        }
        
        LocalDateTime expiryDate = passwordChangedAt
                .plusDays(passwordExpirationDays);
        
        return LocalDateTime.now().isAfter(expiryDate);
    }
}

@Component
public class PasswordExpiryChecker {
    
    @EventListener
    public void checkPasswordExpiry(AuthenticationSuccessEvent event) {
        Authentication auth = event.getAuthentication();
        
        if (auth.getPrincipal() instanceof CustomUserDetails) {
            CustomUserDetails userDetails = 
                (CustomUserDetails) auth.getPrincipal();
            
            if (userDetails.getUser().isPasswordExpired()) {
                throw new PasswordExpiredException(
                    "비밀번호가 만료되었습니다. 변경해주세요."
                );
            }
        }
    }
}

// 11. 다중 PasswordEncoder (마이그레이션)
@Configuration
public class MultiPasswordEncoderConfig {
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        // 기본 Encoder (새 비밀번호용)
        String idForEncode = "bcrypt";
        
        // 여러 Encoder 지원 (기존 비밀번호용)
        Map<String, PasswordEncoder> encoders = new HashMap<>();
        encoders.put(idForEncode, new BCryptPasswordEncoder());
        encoders.put("noop", NoOpPasswordEncoder.getInstance());  // 평문 (마이그레이션용)
        encoders.put("sha256", new StandardPasswordEncoder());    // SHA-256
        
        return new DelegatingPasswordEncoder(idForEncode, encoders);
    }
}

// 저장 형식:
// {bcrypt}$2a$10$... (BCrypt)
// {noop}password123 (평문)
// {sha256}abc123... (SHA-256)

// 12. Cost Factor 성능 테스트
@SpringBootTest
class PasswordEncoderTest {
    
    @Test
    void testEncodingPerformance() {
        String password = "password123";
        
        // Cost Factor 10
        BCryptPasswordEncoder encoder10 = new BCryptPasswordEncoder(10);
        long start = System.currentTimeMillis();
        String encoded = encoder10.encode(password);
        long duration = System.currentTimeMillis() - start;
        System.out.println("Cost 10: " + duration + "ms");
        
        // Cost Factor 12
        BCryptPasswordEncoder encoder12 = new BCryptPasswordEncoder(12);
        start = System.currentTimeMillis();
        encoded = encoder12.encode(password);
        duration = System.currentTimeMillis() - start;
        System.out.println("Cost 12: " + duration + "ms");
        
        // Cost Factor 15
        BCryptPasswordEncoder encoder15 = new BCryptPasswordEncoder(15);
        start = System.currentTimeMillis();
        encoded = encoder15.encode(password);
        duration = System.currentTimeMillis() - start;
        System.out.println("Cost 15: " + duration + "ms");
    }
}
```

## 주의사항 / 함정

### 1. 평문 비밀번호 저장
```java
// ❌ 평문 저장
user.setPassword("password123");
userRepository.save(user);

// ✅ 암호화 후 저장
String encoded = passwordEncoder.encode("password123");
user.setPassword(encoded);
```

### 2. encode() vs matches() 혼동
```java
// ❌ encode()로 비교
if (passwordEncoder.encode(input).equals(user.getPassword())) {
    // 매번 다른 Salt → 항상 false!
}

// ✅ matches() 사용
if (passwordEncoder.matches(input, user.getPassword())) {
    // 올바른 비교
}
```

### 3. 같은 비밀번호도 다른 해시
```java
String password = "password123";
String hash1 = passwordEncoder.encode(password);
String hash2 = passwordEncoder.encode(password);

System.out.println(hash1.equals(hash2));  // false!
// Salt가 다르기 때문
```

### 4. Cost Factor 너무 높음
```java
// ❌ Cost 20 → 너무 느림 (약 100초)
new BCryptPasswordEncoder(20);
// 로그인 시 사용자 대기 시간 증가!

// ✅ Cost 10-12 권장
new BCryptPasswordEncoder(12);
```

### 5. PasswordEncoder Bean 없음
```java
// ❌ Bean 등록 안 함
passwordEncoder.encode(password);
// NullPointerException!

// ✅ @Configuration에서 @Bean 등록
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();
}
```

### 6. 비밀번호 검증 누락
```java
// ❌ 비밀번호 강도 검증 없음
String password = "123";  // 약한 비밀번호도 허용!

// ✅ 검증 추가
passwordValidator.validate(password);
```

### 7. 비밀번호 재사용 허용
```java
// ❌ 같은 비밀번호 계속 사용 가능
user.setPassword(passwordEncoder.encode(newPassword));

// ✅ 히스토리 체크
passwordHistoryService.checkPasswordHistory(user, newPassword);
```

## 관련 개념
- [[Spring-Security-아키텍처]]
- [[인증-흐름-Authentication]]
- [[보안-취약점-대응]]

## 면접 질문

1. **BCrypt를 사용하는 이유는?**
   - 단방향 해시 (복호화 불가)
   - Salt 자동 생성 (같은 비밀번호도 다른 해시)
   - Cost Factor (무차별 대입 공격 방어)

2. **Salt란 무엇인가요?**
   - 비밀번호에 추가하는 랜덤 값
   - 같은 비밀번호도 다른 해시값 생성
   - 레인보우 테이블 공격 방어

3. **Cost Factor의 역할은?**
   - 해시 연산 반복 횟수 (2^n)
   - 높을수록 안전하지만 느림
   - 권장: 10-12

4. **encode()와 matches()의 차이는?**
   - encode(): 비밀번호 암호화
   - matches(): 평문과 암호화된 비밀번호 비교

5. **같은 비밀번호를 두 번 encode()하면?**
   - 다른 해시값 생성
   - Salt가 매번 다르기 때문

6. **MD5, SHA-1 대신 BCrypt를 쓰는 이유는?**
   - MD5, SHA-1: 빠름 → 무차별 대입 공격 취약
   - BCrypt: 느림 → 대량 해시 생성 어려움

7. **비밀번호 재설정 토큰은 어떻게 관리하나요?**
   - UUID 랜덤 생성
   - DB에 저장 + 만료 시간 설정
   - 1회용 토큰 (사용 후 삭제)

## 참고 자료
- BCrypt Wikipedia
- Spring Security PasswordEncoder Documentation
- https://docs.spring.io/spring-security/reference/features/authentication/password-storage.html
