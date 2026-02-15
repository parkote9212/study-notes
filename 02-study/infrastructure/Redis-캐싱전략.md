---
tags:
  - study
  - redis
  - cache
  - strategy
  - performance
created: 2026-02-15
---

# Redis 캐싱전략

## 한 줄 요약
> 캐싱 전략은 데이터 일관성과 성능 사이의 균형을 맞추는 방법으로, Cache-Aside, Write-Through, Write-Back, Read-Through 패턴과 적절한 Eviction 정책 선택이 핵심이다.

## 상세 설명

### 캐싱이 필요한 이유
1. **DB 부하 감소**: 반복적인 조회 쿼리를 캐시로 대체
2. **응답 속도 향상**: 밀리초 → 마이크로초 단위
3. **비용 절감**: DB 스케일링 비용보다 Redis가 저렴
4. **안정성**: DB 장애 시 캐시로 임시 대응

### 캐싱 전략 선택 기준
| 기준 | 고려사항 |
|------|---------|
| **읽기/쓰기 비율** | 읽기 많음 → Cache-Aside, 쓰기 많음 → Write-Through |
| **데이터 일관성** | 강한 일관성 → Write-Through, 느슨한 일관성 → Cache-Aside |
| **데이터 크기** | 큰 데이터 → Lazy Loading |
| **업데이트 빈도** | 자주 변경 → 짧은 TTL, 거의 변경 없음 → 긴 TTL |

## 1. Cache-Aside (Lazy Loading) ⭐ 가장 일반적

### 동작 방식
```
읽기:
1. 애플리케이션 → Redis 조회
2. 캐시 히트 → 즉시 반환
3. 캐시 미스 → DB 조회 → Redis 저장 → 반환

쓰기:
1. 애플리케이션 → DB 업데이트
2. Redis 캐시 삭제 (또는 갱신)
```

### 장점
✅ 캐시 장애 시에도 애플리케이션 동작 (DB로 폴백)  
✅ 필요한 데이터만 캐싱 (메모리 효율)  
✅ 구현이 간단하고 직관적

### 단점
❌ 최초 조회 시 느림 (Cache Miss)  
❌ 캐시 갱신 타이밍 이슈 (일관성 문제)  
❌ 코드 중복 (캐시 체크 로직 반복)

### 실무 코드 예시
```java
@Service
public class ProductService {
    
    private final ProductRepository productRepository;
    private final RedisTemplate<String, Product> redisTemplate;
    
    public Product getProduct(Long productId) {
        String cacheKey = "product:" + productId;
        
        // 1. 캐시 확인
        Product cached = (Product) redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {
            return cached; // 캐시 히트
        }
        
        // 2. 캐시 미스 → DB 조회
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new NotFoundException("상품 없음"));
        
        // 3. 캐시 저장 (TTL 1시간)
        redisTemplate.opsForValue().set(cacheKey, product, 1, TimeUnit.HOURS);
        
        return product;
    }
    
    @Transactional
    public void updateProduct(Long productId, ProductDto dto) {
        // 1. DB 업데이트
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new NotFoundException("상품 없음"));
        product.update(dto);
        productRepository.save(product);
        
        // 2. 캐시 무효화 (삭제)
        String cacheKey = "product:" + productId;
        redisTemplate.delete(cacheKey);
        
        // 또는 캐시 갱신
        // redisTemplate.opsForValue().set(cacheKey, product, 1, TimeUnit.HOURS);
    }
}
```

### Spring Cache 추상화로 간단하게
```java
@EnableCaching
@Configuration
public class CacheConfig {
    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory factory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofHours(1));
        return RedisCacheManager.builder(factory)
            .cacheDefaults(config)
            .build();
    }
}

@Service
public class ProductService {
    
    @Cacheable(value = "product", key = "#productId")
    public Product getProduct(Long productId) {
        // 캐시 미스 시에만 실행
        return productRepository.findById(productId)
            .orElseThrow(() -> new NotFoundException("상품 없음"));
    }
    
    @CacheEvict(value = "product", key = "#productId")
    @Transactional
    public void updateProduct(Long productId, ProductDto dto) {
        // DB 업데이트 후 자동으로 캐시 삭제
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new NotFoundException("상품 없음"));
        product.update(dto);
    }
    
    @CachePut(value = "product", key = "#result.id")
    @Transactional
    public Product createProduct(ProductDto dto) {
        // 생성 후 자동으로 캐시 저장
        return productRepository.save(new Product(dto));
    }
}
```

## 2. Write-Through (읽기 중심 + 강한 일관성)

### 동작 방식
```
쓰기:
1. 애플리케이션 → Redis 저장
2. Redis → DB 저장 (동기)
3. 성공 응답

읽기:
1. 애플리케이션 → Redis 조회
2. 항상 캐시에 있음 (일관성 보장)
```

### 장점
✅ 캐시와 DB가 항상 동기화 (강한 일관성)  
✅ Cache Miss가 거의 없음

### 단점
❌ 모든 쓰기가 느려짐 (Redis + DB 두 번)  
❌ 사용하지 않는 데이터도 캐싱 (메모리 낭비)  
❌ 캐시 장애 시 쓰기 실패

### 실무 코드 예시
```java
@Service
public class UserService {
    
    private final UserRepository userRepository;
    private final RedisTemplate<String, User> redisTemplate;
    
    @Transactional
    public User createUser(UserDto dto) {
        User user = new User(dto);
        
        // 1. Redis에 먼저 저장
        String cacheKey = "user:" + user.getId();
        redisTemplate.opsForValue().set(cacheKey, user);
        
        // 2. DB에 저장
        userRepository.save(user);
        
        return user;
    }
    
    public User getUser(Long userId) {
        String cacheKey = "user:" + userId;
        
        // 캐시에서 조회 (항상 있어야 함)
        User user = (User) redisTemplate.opsForValue().get(cacheKey);
        
        if (user == null) {
            // 캐시 미스 (비정상) → DB에서 복구
            user = userRepository.findById(userId)
                .orElseThrow(() -> new NotFoundException("사용자 없음"));
            redisTemplate.opsForValue().set(cacheKey, user);
        }
        
        return user;
    }
}
```

## 3. Write-Back (Write-Behind) (쓰기 중심)

### 동작 방식
```
쓰기:
1. 애플리케이션 → Redis 저장
2. 즉시 성공 응답
3. 백그라운드에서 배치로 DB 저장 (비동기)

읽기:
1. Redis에서 조회
```

### 장점
✅ 쓰기 성능이 매우 빠름  
✅ DB 쓰기를 배치 처리 (부하 분산)

### 단점
❌ 데이터 손실 위험 (Redis 장애 시)  
❌ 구현 복잡도 높음  
❌ 일관성 보장 어려움

### 사용 사례
- 로그 수집 시스템
- 실시간 통계 (나중에 집계)
- 조회수, 좋아요 등 정확성이 덜 중요한 카운터

### 실무 코드 예시
```java
@Service
public class ViewCountService {
    
    private final RedisTemplate<String, String> redisTemplate;
    private final ViewCountRepository viewCountRepository;
    
    // 조회수 증가 (즉시 Redis에만 저장)
    public void incrementViewCount(Long postId) {
        String key = "post:view:" + postId;
        redisTemplate.opsForValue().increment(key);
    }
    
    // 스케줄러로 주기적으로 DB 동기화
    @Scheduled(fixedRate = 60000) // 1분마다
    public void syncToDatabase() {
        Set<String> keys = redisTemplate.keys("post:view:*");
        
        for (String key : keys) {
            Long postId = Long.parseLong(key.split(":")[2]);
            String count = redisTemplate.opsForValue().get(key);
            
            if (count != null) {
                // DB 업데이트
                viewCountRepository.updateViewCount(postId, Long.parseLong(count));
                // Redis에서 삭제 (또는 초기화)
                redisTemplate.delete(key);
            }
        }
    }
}
```

## 4. Read-Through (캐시가 DB 관리)

### 동작 방식
```
읽기:
1. 애플리케이션 → 캐시 조회
2. 캐시가 DB에서 자동 로드
3. 반환
```

### 특징
- 애플리케이션은 캐시만 바라봄
- 캐시가 DB 로직 담당
- Spring에서는 잘 사용 안 함 (Cache-Aside로 충분)

## 캐시 Eviction (제거 정책)

### 메모리 부족 시 어떤 데이터를 삭제할까?

| 정책 | 설명 | 사용 사례 |
|------|------|----------|
| **noeviction** | 삭제 안 함, 에러 반환 | 모든 데이터 보존 필요 |
| **allkeys-lru** | 가장 오래 사용 안 한 키 삭제 | 일반적인 캐싱 |
| **allkeys-lfu** | 가장 적게 사용한 키 삭제 | 인기도 기반 |
| **volatile-lru** | TTL 있는 키 중 LRU 삭제 | 혼합 사용 |
| **volatile-ttl** | TTL 짧은 순서로 삭제 | TTL 기반 관리 |

### Redis 설정
```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### Spring 설정
```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      maxmemory: 2gb
      maxmemory-policy: allkeys-lru
```

## 캐시 일관성 문제 해결

### 문제 1: Stale Data (오래된 데이터)

**발생 상황:**
```
1. User A가 상품 조회 → Redis 캐싱
2. User B가 상품 가격 변경 → DB 업데이트
3. User A가 다시 조회 → 오래된 가격 반환
```

**해결 방법:**

1. **캐시 삭제** (추천)
```java
@Transactional
public void updatePrice(Long productId, int newPrice) {
    productRepository.updatePrice(productId, newPrice);
    redisTemplate.delete("product:" + productId); // 다음 조회 시 재캐싱
}
```

2. **캐시 갱신**
```java
@Transactional
public void updatePrice(Long productId, int newPrice) {
    Product product = productRepository.updatePrice(productId, newPrice);
    redisTemplate.opsForValue().set("product:" + productId, product, 1, TimeUnit.HOURS);
}
```

3. **짧은 TTL**
```java
// 자주 변경되는 데이터는 TTL을 짧게
redisTemplate.opsForValue().set(key, value, 5, TimeUnit.MINUTES);
```

### 문제 2: Cache Stampede (캐시 만료 순간 동시 요청)

**발생 상황:**
```
1. 캐시 만료
2. 동시에 1000개 요청
3. 모두 Cache Miss → 1000개 DB 조회 → DB 과부하
```

**해결 방법 1: 분산 락**
```java
public Product getProduct(Long productId) {
    String cacheKey = "product:" + productId;
    String lockKey = "lock:" + cacheKey;
    
    // 1. 캐시 확인
    Product cached = (Product) redisTemplate.opsForValue().get(cacheKey);
    if (cached != null) return cached;
    
    // 2. 락 획득 시도 (10초 대기)
    Boolean lockAcquired = redisTemplate.opsForValue()
        .setIfAbsent(lockKey, "1", 10, TimeUnit.SECONDS);
    
    if (Boolean.TRUE.equals(lockAcquired)) {
        try {
            // 3. 다시 한 번 캐시 확인 (다른 스레드가 저장했을 수 있음)
            cached = (Product) redisTemplate.opsForValue().get(cacheKey);
            if (cached != null) return cached;
            
            // 4. DB 조회 및 캐싱
            Product product = productRepository.findById(productId)
                .orElseThrow(() -> new NotFoundException("상품 없음"));
            redisTemplate.opsForValue().set(cacheKey, product, 1, TimeUnit.HOURS);
            return product;
        } finally {
            // 5. 락 해제
            redisTemplate.delete(lockKey);
        }
    } else {
        // 락 획득 실패 → 잠시 대기 후 재시도 또는 DB 조회
        Thread.sleep(100);
        return getProduct(productId); // 재귀 호출
    }
}
```

**해결 방법 2: TTL 분산**
```java
// 각 키마다 약간 다른 TTL 설정
int randomTtl = 3600 + new Random().nextInt(300); // 1시간 ± 5분
redisTemplate.opsForValue().set(key, value, randomTtl, TimeUnit.SECONDS);
```

## 주의사항 / 함정

### 1. 캐시 워밍 (Cache Warming)
애플리케이션 시작 시 인기 데이터를 미리 캐싱
```java
@PostConstruct
public void warmUpCache() {
    List<Product> popularProducts = productRepository.findTop100ByOrderBySalesDesc();
    for (Product product : popularProducts) {
        String key = "product:" + product.getId();
        redisTemplate.opsForValue().set(key, product, 1, TimeUnit.HOURS);
    }
}
```

### 2. 캐시 키 설계
```java
// ❌ 나쁜 예: 충돌 가능
String key = "product" + productId;

// ✅ 좋은 예: 명확한 네임스페이스
String key = "product:detail:" + productId;
String key = "product:price:" + productId;
String key = "user:session:" + userId;
```

### 3. 직렬화 설정
```java
@Bean
public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
    RedisTemplate<String, Object> template = new RedisTemplate<>();
    template.setConnectionFactory(factory);
    
    // JSON 직렬화 (권장)
    Jackson2JsonRedisSerializer<Object> serializer = 
        new Jackson2JsonRedisSerializer<>(Object.class);
    
    template.setKeySerializer(new StringRedisSerializer());
    template.setValueSerializer(serializer);
    template.setHashKeySerializer(new StringRedisSerializer());
    template.setHashValueSerializer(serializer);
    
    return template;
}
```

## 관련 개념
- [[Redis-기본개념]] - Redis 개요
- [[Redis-데이터타입과명령어]] - 자료구조
- [[Redis-Spring통합]] - Spring 캐싱 구현
- [[데이터베이스-인덱싱]] - DB 성능 최적화
- [[아키텍처-CDN]] - 정적 파일 캐싱

## 면접 질문

1. **Cache-Aside 패턴을 설명하고, 장단점을 말해보세요.**
   - 애플리케이션이 캐시와 DB를 직접 제어
   - 장점: 캐시 장애에도 동작, 메모리 효율
   - 단점: 최초 조회 느림, 일관성 이슈

2. **캐시 일관성 문제를 어떻게 해결하나요?**
   - DB 업데이트 시 캐시 삭제/갱신
   - TTL 설정으로 주기적 갱신
   - 분산 락으로 동시성 제어

3. **Cache Stampede가 무엇이며, 어떻게 방지하나요?**
   - 캐시 만료 시 동시 요청으로 DB 과부하
   - 분산 락으로 첫 요청만 DB 조회
   - TTL 분산 (각 키마다 다른 TTL)

4. **Redis Eviction 정책 중 allkeys-lru를 선택하는 이유는?**
   - 모든 키 중 가장 오래 사용 안 한 것 삭제
   - 일반적인 캐싱에 가장 적합
   - 메모리 효율적

5. **Write-Through와 Write-Back의 차이는?**
   - Write-Through: 캐시+DB 동기 저장 (일관성 강함)
   - Write-Back: 캐시만 저장, 나중에 DB 배치 (성능 좋음)

6. **프로젝트에서 캐싱을 어떻게 적용했나요? (BizSync 예시)**
   - 실시간 협업 시스템의 세션 정보 캐싱
   - 사용자 프로필을 Cache-Aside 패턴으로 저장
   - TTL 30분, 업데이트 시 캐시 삭제

## 참고 자료
- [Caching Strategies](https://aws.amazon.com/caching/best-practices/)
- [Spring Cache Abstraction](https://docs.spring.io/spring-framework/docs/current/reference/html/integration.html#cache)
- [Redis Eviction Policies](https://redis.io/docs/reference/eviction/)
