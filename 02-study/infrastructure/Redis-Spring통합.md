---
tags:
  - study
  - redis
  - spring
  - spring-boot
  - spring-data-redis
created: 2026-02-15
---

# Redis Spring 통합

## 한 줄 요약
> Spring Data Redis는 RedisTemplate, @Cacheable, RedisRepository를 제공하여 Redis를 쉽게 통합하며, Lettuce와 Jedis 클라이언트를 지원한다.

## 상세 설명

### Spring Data Redis란?
- **Spring의 Redis 통합 라이브러리**
- 저수준 Redis 명령어를 고수준 API로 추상화
- 캐싱, 세션 관리, 메시징을 간편하게 구현

### 주요 구성 요소
1. **RedisTemplate**: 저수준 Redis 작업
2. **Cache Abstraction**: `@Cacheable` 등 선언적 캐싱
3. **RedisRepository**: JPA처럼 Repository 패턴
4. **Redis Message Listener**: Pub/Sub 구독

## 1. 프로젝트 설정

### Gradle 의존성
```gradle
dependencies {
    // Spring Data Redis
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
    
    // Lettuce (기본 클라이언트, 비동기 지원)
    // 이미 spring-boot-starter-data-redis에 포함됨
    
    // 또는 Jedis (동기 전용)
    // implementation 'redis.clients:jedis'
    
    // JSON 직렬화
    implementation 'com.fasterxml.jackson.core:jackson-databind'
}
```

### application.yml 설정
```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password: # 옵션
      database: 0 # 0~15 (기본 0)
      timeout: 3000ms
      
      # Lettuce 설정 (기본)
      lettuce:
        pool:
          max-active: 8   # 최대 연결 수
          max-idle: 8     # 최대 유휴 연결 수
          min-idle: 0     # 최소 유휴 연결 수
          max-wait: -1ms  # 연결 대기 시간
      
      # Jedis 설정 (사용 시)
      # jedis:
      #   pool:
      #     max-active: 8
```

### Redis 클라이언트 선택

| 항목 | Lettuce (권장) | Jedis |
|------|---------------|-------|
| 비동기 | ✅ 지원 | ❌ 미지원 |
| Reactive | ✅ 지원 | ❌ 미지원 |
| 성능 | 더 빠름 (Netty 기반) | 느림 (블로킹) |
| 기본값 | Spring Boot 2.x+ | Spring Boot 1.x |

**→ 특별한 이유 없으면 Lettuce 사용 (기본값)**

## 2. RedisTemplate 설정

### 기본 설정
```java
@Configuration
public class RedisConfig {
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate(
            RedisConnectionFactory connectionFactory) {
        
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        
        // JSON 직렬화 설정 (권장)
        Jackson2JsonRedisSerializer<Object> serializer = 
            new Jackson2JsonRedisSerializer<>(Object.class);
        
        ObjectMapper mapper = new ObjectMapper();
        mapper.setVisibility(PropertyAccessor.ALL, JsonAutoDetect.Visibility.ANY);
        mapper.activateDefaultTyping(
            LaissezFaireSubTypeValidator.instance,
            ObjectMapper.DefaultTyping.NON_FINAL,
            JsonTypeInfo.As.PROPERTY
        );
        serializer.setObjectMapper(mapper);
        
        // 키는 String, 값은 JSON
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(serializer);
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(serializer);
        
        template.afterPropertiesSet();
        return template;
    }
    
    // String 전용 Template (선택)
    @Bean
    public RedisTemplate<String, String> stringRedisTemplate(
            RedisConnectionFactory connectionFactory) {
        
        StringRedisTemplate template = new StringRedisTemplate();
        template.setConnectionFactory(connectionFactory);
        return template;
    }
}
```

### 직렬화 방식 비교

| 직렬화 방식 | 장점 | 단점 | 용도 |
|-----------|------|------|------|
| **JdkSerializationRedisSerializer** | 기본값 | 사람이 읽을 수 없음, 크기 큼 | 비추천 |
| **StringRedisSerializer** | 간단, 읽기 쉬움 | String만 가능 | String 값 |
| **Jackson2JsonRedisSerializer** | JSON, 읽기 쉬움, 언어 독립적 | 타입 정보 필요 | 객체 저장 (권장) |
| **GenericJackson2JsonRedisSerializer** | 타입 정보 자동 | 메타데이터 포함 | 여러 타입 혼용 |

## 3. RedisTemplate 사용법

### 기본 Operations
```java
@Service
public class RedisService {
    
    private final RedisTemplate<String, Object> redisTemplate;
    
    // String 작업
    public void setString(String key, String value, long ttl) {
        redisTemplate.opsForValue().set(key, value, ttl, TimeUnit.SECONDS);
    }
    
    public String getString(String key) {
        return (String) redisTemplate.opsForValue().get(key);
    }
    
    // Hash 작업
    public void setHash(String key, String field, Object value) {
        redisTemplate.opsForHash().put(key, field, value);
    }
    
    public Object getHash(String key, String field) {
        return redisTemplate.opsForHash().get(key, field);
    }
    
    // List 작업
    public void addToList(String key, Object value) {
        redisTemplate.opsForList().rightPush(key, value);
    }
    
    public List<Object> getList(String key, long start, long end) {
        return redisTemplate.opsForList().range(key, start, end);
    }
    
    // Set 작업
    public void addToSet(String key, Object... values) {
        redisTemplate.opsForSet().add(key, values);
    }
    
    public Set<Object> getSet(String key) {
        return redisTemplate.opsForSet().members(key);
    }
    
    // Sorted Set 작업
    public void addToSortedSet(String key, Object value, double score) {
        redisTemplate.opsForZSet().add(key, value, score);
    }
    
    public Set<Object> getTopN(String key, long count) {
        return redisTemplate.opsForZSet().reverseRange(key, 0, count - 1);
    }
    
    // 키 관리
    public boolean hasKey(String key) {
        return Boolean.TRUE.equals(redisTemplate.hasKey(key));
    }
    
    public boolean delete(String key) {
        return Boolean.TRUE.equals(redisTemplate.delete(key));
    }
    
    public boolean expire(String key, long timeout, TimeUnit unit) {
        return Boolean.TRUE.equals(redisTemplate.expire(key, timeout, unit));
    }
}
```

### 복잡한 객체 저장
```java
@Service
public class UserCacheService {
    
    private final RedisTemplate<String, Object> redisTemplate;
    
    // 사용자 정보 캐싱
    public void cacheUser(User user) {
        String key = "user:" + user.getId();
        redisTemplate.opsForValue().set(key, user, 1, TimeUnit.HOURS);
    }
    
    public User getUser(Long userId) {
        String key = "user:" + userId;
        Object cached = redisTemplate.opsForValue().get(key);
        
        if (cached instanceof LinkedHashMap) {
            // JSON 역직렬화
            return new ObjectMapper().convertValue(cached, User.class);
        }
        
        return (User) cached;
    }
    
    // 여러 필드를 Hash로 저장
    public void cacheUserAsHash(User user) {
        String key = "user:hash:" + user.getId();
        
        Map<String, String> fields = Map.of(
            "name", user.getName(),
            "email", user.getEmail(),
            "age", String.valueOf(user.getAge())
        );
        
        redisTemplate.opsForHash().putAll(key, fields);
        redisTemplate.expire(key, 1, TimeUnit.HOURS);
    }
}
```

## 4. Spring Cache Abstraction (선언적 캐싱) ⭐ 추천

### 설정
```java
@EnableCaching
@Configuration
public class CacheConfig {
    
    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        
        // 기본 캐시 설정
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofHours(1))  // 기본 TTL 1시간
            .serializeKeysWith(
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new StringRedisSerializer())
            )
            .serializeValuesWith(
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new GenericJackson2JsonRedisSerializer())
            )
            .disableCachingNullValues();  // null 캐싱 안 함
        
        // 캐시별 개별 설정
        Map<String, RedisCacheConfiguration> cacheConfigurations = Map.of(
            "products", defaultConfig.entryTtl(Duration.ofHours(2)),
            "users", defaultConfig.entryTtl(Duration.ofMinutes(30)),
            "sessions", defaultConfig.entryTtl(Duration.ofMinutes(15))
        );
        
        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(defaultConfig)
            .withInitialCacheConfigurations(cacheConfigurations)
            .build();
    }
}
```

### 사용법
```java
@Service
public class ProductService {
    
    private final ProductRepository productRepository;
    
    // 조회 시 자동 캐싱
    @Cacheable(value = "products", key = "#productId")
    public Product getProduct(Long productId) {
        // 캐시 미스 시에만 실행
        return productRepository.findById(productId)
            .orElseThrow(() -> new NotFoundException("상품 없음"));
    }
    
    // 조회 + 조건부 캐싱
    @Cacheable(value = "products", key = "#productId", unless = "#result == null")
    public Product getProductIfExists(Long productId) {
        return productRepository.findById(productId).orElse(null);
    }
    
    // 업데이트 시 캐시 갱신
    @CachePut(value = "products", key = "#result.id")
    @Transactional
    public Product updateProduct(Long productId, ProductDto dto) {
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new NotFoundException("상품 없음"));
        product.update(dto);
        return productRepository.save(product);
    }
    
    // 삭제 시 캐시 제거
    @CacheEvict(value = "products", key = "#productId")
    @Transactional
    public void deleteProduct(Long productId) {
        productRepository.deleteById(productId);
    }
    
    // 전체 캐시 삭제
    @CacheEvict(value = "products", allEntries = true)
    public void clearAllProductCache() {
        // 메서드 실행 전 캐시 전체 삭제
    }
    
    // 여러 캐시 동시 제거
    @Caching(evict = {
        @CacheEvict(value = "products", key = "#productId"),
        @CacheEvict(value = "productList", allEntries = true)
    })
    @Transactional
    public void updateProductAndClearList(Long productId, ProductDto dto) {
        // ...
    }
}
```

### SpEL 표현식 활용
```java
@Service
public class OrderService {
    
    // 복잡한 키 생성
    @Cacheable(value = "orders", 
               key = "#userId + ':' + #status + ':' + #page")
    public List<Order> getOrders(Long userId, String status, int page) {
        return orderRepository.findByUserIdAndStatus(userId, status, 
            PageRequest.of(page, 20));
    }
    
    // 조건부 캐싱
    @Cacheable(value = "orders", 
               key = "#orderId",
               condition = "#orderId > 100")  // orderId > 100일 때만 캐싱
    public Order getOrder(Long orderId) {
        return orderRepository.findById(orderId)
            .orElseThrow(() -> new NotFoundException("주문 없음"));
    }
    
    // 반환값 기반 조건
    @Cacheable(value = "orders",
               key = "#orderId",
               unless = "#result.status == 'CANCELLED'")  // 취소 주문은 캐싱 안 함
    public Order getOrderUnlessCancelled(Long orderId) {
        return orderRepository.findById(orderId)
            .orElseThrow(() -> new NotFoundException("주문 없음"));
    }
}
```

## 5. Redis Session Management

### 설정
```gradle
dependencies {
    implementation 'org.springframework.session:spring-session-data-redis'
}
```

```yaml
spring:
  session:
    store-type: redis
    timeout: 30m  # 세션 타임아웃
    redis:
      namespace: spring:session  # 키 접두사
```

```java
@EnableRedisHttpSession(maxInactiveIntervalInSeconds = 1800)
public class SessionConfig {
    // 자동 설정으로 세션이 Redis에 저장됨
}
```

### 사용법
```java
@RestController
public class SessionController {
    
    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginDto dto, 
                                   HttpSession session) {
        // 인증 로직
        User user = authService.authenticate(dto);
        
        // 세션에 저장 (자동으로 Redis에 저장됨)
        session.setAttribute("userId", user.getId());
        session.setAttribute("username", user.getUsername());
        session.setAttribute("role", user.getRole());
        
        return ResponseEntity.ok("로그인 성공");
    }
    
    @GetMapping("/me")
    public ResponseEntity<?> getCurrentUser(HttpSession session) {
        Long userId = (Long) session.getAttribute("userId");
        
        if (userId == null) {
            return ResponseEntity.status(401).body("로그인 필요");
        }
        
        User user = userService.getUser(userId);
        return ResponseEntity.ok(user);
    }
    
    @PostMapping("/logout")
    public ResponseEntity<?> logout(HttpSession session) {
        session.invalidate();  // Redis에서도 삭제됨
        return ResponseEntity.ok("로그아웃 성공");
    }
}
```

## 6. RedisRepository (JPA 스타일)

### 엔티티 정의
```java
@RedisHash(value = "user", timeToLive = 3600)  // 1시간 TTL
public class UserCache {
    
    @Id
    private Long id;
    
    @Indexed  // 이 필드로 검색 가능
    private String email;
    
    private String name;
    private int age;
    
    // getter, setter, constructor
}
```

### Repository 정의
```java
public interface UserCacheRepository extends CrudRepository<UserCache, Long> {
    
    // 이메일로 조회 (@Indexed 필요)
    Optional<UserCache> findByEmail(String email);
    
    // 나이 범위 조회
    List<UserCache> findByAgeBetween(int minAge, int maxAge);
}
```

### 사용법
```java
@Service
public class UserCacheService {
    
    private final UserCacheRepository userCacheRepository;
    
    public void cacheUser(User user) {
        UserCache cache = UserCache.builder()
            .id(user.getId())
            .email(user.getEmail())
            .name(user.getName())
            .age(user.getAge())
            .build();
        
        userCacheRepository.save(cache);  // Redis에 저장
    }
    
    public UserCache getUser(Long userId) {
        return userCacheRepository.findById(userId).orElse(null);
    }
    
    public UserCache getUserByEmail(String email) {
        return userCacheRepository.findByEmail(email).orElse(null);
    }
}
```

## 7. BizSync 프로젝트 실전 예시

### 실시간 협업 세션 관리
```java
@RedisHash(value = "collaboration:session", timeToLive = 1800)
public class CollaborationSession {
    
    @Id
    private String sessionId;
    
    @Indexed
    private Long documentId;
    
    private List<String> activeUsers;
    private Map<String, LocalDateTime> lastActivity;
    
    // getter, setter
}

@Service
public class CollaborationService {
    
    private final RedisTemplate<String, Object> redisTemplate;
    
    // 사용자가 문서에 접속
    public void joinDocument(Long documentId, String userId) {
        String key = "document:users:" + documentId;
        
        // Set에 사용자 추가
        redisTemplate.opsForSet().add(key, userId);
        
        // 마지막 활동 시간 기록
        String activityKey = "document:activity:" + documentId;
        redisTemplate.opsForHash().put(activityKey, userId, 
            LocalDateTime.now().toString());
        
        // 30분 TTL
        redisTemplate.expire(key, 30, TimeUnit.MINUTES);
        redisTemplate.expire(activityKey, 30, TimeUnit.MINUTES);
    }
    
    // 현재 접속 중인 사용자 목록
    public Set<String> getActiveUsers(Long documentId) {
        String key = "document:users:" + documentId;
        Set<Object> users = redisTemplate.opsForSet().members(key);
        return users.stream()
            .map(Object::toString)
            .collect(Collectors.toSet());
    }
    
    // WebSocket 메시지 브로드캐스트
    public void broadcastEdit(Long documentId, EditEvent event) {
        String channel = "document:edit:" + documentId;
        redisTemplate.convertAndSend(channel, event);
    }
}
```

## 주의사항 / 함정

### 1. 직렬화 문제
❌ **문제**: 기본 JDK 직렬화는 사람이 읽을 수 없음
```
redis-cli> GET user:1
"\xac\xed\x00\x05sr\x00..."  # 읽을 수 없음
```

✅ **해결**: JSON 직렬화 사용
```java
template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
```

### 2. @Cacheable 중복 호출
❌ **문제**: 같은 클래스 내부에서 @Cacheable 메서드 호출 시 캐싱 안 됨
```java
@Service
public class ProductService {
    
    @Cacheable("products")
    public Product getProduct(Long id) { /* ... */ }
    
    public void someMethod(Long id) {
        Product p = getProduct(id);  // 캐싱 안 됨 (프록시 우회)
    }
}
```

✅ **해결**: 다른 빈에서 호출하거나 self-injection

### 3. TTL 설정 누락
항상 TTL 설정하여 메모리 누수 방지

### 4. 키 네이밍 일관성
```java
// ✅ 좋은 예
String key = "user:profile:" + userId;
String key = "product:detail:" + productId;

// ❌ 나쁜 예
String key = "user" + userId;  // 충돌 가능
```

## 관련 개념
- [[Redis-기본개념]] - Redis 개요
- [[Redis-캐싱전략]] - 캐싱 패턴
- [[Spring-AOP]] - @Cacheable 동작 원리
- [[Spring-Boot-자동설정]] - Auto Configuration

## 면접 질문

1. **Spring Data Redis에서 Lettuce와 Jedis의 차이는?**
   - Lettuce: 비동기, Reactive, Netty 기반 (권장)
   - Jedis: 동기 전용, 블로킹, 레거시

2. **@Cacheable이 같은 클래스 내부에서 작동하지 않는 이유는?**
   - Spring AOP 프록시 우회
   - 자기 자신 호출 시 프록시 거치지 않음
   - 해결: 다른 빈에서 호출

3. **RedisTemplate vs Spring Cache Abstraction 중 무엇을 선택하나요?**
   - 간단한 캐싱: @Cacheable (선언적, 간편)
   - 복잡한 로직: RedisTemplate (세밀한 제어)
   - 혼용 가능

4. **Redis 세션 관리의 장점은?**
   - 여러 서버 간 세션 공유 (분산 환경)
   - 서버 재시작해도 세션 유지
   - 스케일 아웃 용이

5. **직렬화 방식을 JSON으로 선택하는 이유는?**
   - 사람이 읽을 수 있음 (디버깅 용이)
   - 언어 독립적 (다른 시스템과 호환)
   - JDK 직렬화보다 크기 작음

6. **프로젝트에서 Spring Data Redis를 어떻게 활용했나요? (BizSync 예시)**
   - 실시간 협업 세션 관리 (RedisTemplate)
   - WebSocket 연결 정보 저장
   - Pub/Sub으로 다중 서버 간 이벤트 동기화

## 참고 자료
- [Spring Data Redis 공식 문서](https://docs.spring.io/spring-data/redis/docs/current/reference/html/)
- [Spring Cache Abstraction](https://docs.spring.io/spring-framework/docs/current/reference/html/integration.html#cache)
- [Spring Session with Redis](https://docs.spring.io/spring-session/docs/current/reference/html5/#httpsession-redis)
- [Baeldung - Spring Data Redis Tutorial](https://www.baeldung.com/spring-data-redis-tutorial)
