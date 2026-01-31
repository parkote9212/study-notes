---
tags:
  - study
  - database
  - redis
  - cache
created: 2026-01-31
---

# Redis 기본개념 - 인메모리 DB

## 한 줄 요약
> 메모리 기반 Key-Value 저장소로 초고속 캐싱과 실시간 데이터 처리에 최적화된 NoSQL 데이터베이스

## 상세 설명

### What - Redis란?
**Redis**(REmote DIctionary Server)는 오픈소스 인메모리 데이터 저장소입니다.
- **인메모리 기반**: 모든 데이터를 RAM에 저장하여 디스크 기반 DB 대비 100~1000배 빠른 응답속도
- **Key-Value 구조**: 단순하지만 강력한 키-값 쌍으로 데이터 관리
- **다목적 활용**: 캐시, 세션 저장소, 메시지 브로커, 실시간 분석 등 다양한 용도

### Why - 왜 Redis를 사용하는가?

**1. 압도적인 성능**
- 평균 읽기/쓰기 응답시간: 1ms 미만
- 초당 수백만 건의 요청 처리 가능
- MySQL 같은 디스크 DB보다 수백 배 빠름

**2. 데이터베이스 부하 감소**
```
사용자 요청 → Redis 캐시 확인 (Cache Hit: 0.5ms)
             ↓ Cache Miss
             → MySQL 조회 (200ms) → Redis에 저장
```

**3. 확장성**
- Redis Sentinel: 자동 장애 조치(Failover)
- Redis Cluster: 데이터 샤딩으로 수평 확장
- Master-Slave 복제로 읽기 성능 향상

### How - 동작 원리

**메모리 저장 구조**
```
RAM (주 메모리)
├── Hash Table (키 → 값 매핑)
├── 데이터 구조 저장 영역
└── 만료 키 관리 테이블
    ↓ (선택적)
디스크 (RDB/AOF 백업)
```

**데이터 영속성 옵션**
1. **RDB** (Redis Database): 특정 시점 스냅샷 저장
2. **AOF** (Append Only File): 모든 쓰기 작업 로그 기록
3. **Hybrid**: RDB + AOF 조합

### 실무 적용 사례

**1. 세션 저장소 (Spring Boot + Redis)**
```java
@Configuration
@EnableRedisHttpSession(maxInactiveIntervalInSeconds = 1800)
public class RedisSessionConfig {
    
    @Bean
    public RedisConnectionFactory connectionFactory() {
        return new LettuceConnectionFactory("localhost", 6379);
    }
}
```
- WAS가 여러 대여도 세션 공유 가능
- 서버 재시작 시에도 세션 유지

**2. API 응답 캐싱**
```java
@Cacheable(value = "products", key = "#id")
public Product getProduct(Long id) {
    return productRepository.findById(id)
        .orElseThrow(() -> new ProductNotFoundException(id));
}
```
- 첫 요청: DB 조회 (200ms) → Redis 저장
- 이후 요청: Redis 조회 (1ms)
- 캐시 히트율 80% 시 평균 응답속도 40배 향상

**3. 실시간 순위표 (Sorted Set 활용)**
```java
// 게임 점수 저장
redisTemplate.opsForZSet().add("leaderboard", "player1", 9500);

// 상위 10명 조회
Set<String> topPlayers = redisTemplate.opsForZSet()
    .reverseRange("leaderboard", 0, 9);
```

## 코드 예시

### Spring Boot Redis 설정

**의존성 추가 (build.gradle)**
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
    implementation 'io.lettuce:lettuce-core' // 비동기 Redis 클라이언트
}
```

**Redis 설정 클래스**
```java
@Configuration
public class RedisConfig {
    
    @Value("${spring.data.redis.host}")
    private String host;
    
    @Value("${spring.data.redis.port}")
    private int port;
    
    @Bean
    public RedisConnectionFactory redisConnectionFactory() {
        RedisStandaloneConfiguration config = new RedisStandaloneConfiguration();
        config.setHostName(host);
        config.setPort(port);
        // config.setPassword("your-password"); // 프로덕션 환경
        return new LettuceConnectionFactory(config);
    }
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate() {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(redisConnectionFactory());
        
        // JSON 직렬화 설정
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
        
        return template;
    }
}
```

**application.yml**
```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      # password: your-password
      timeout: 3000ms
      lettuce:
        pool:
          max-active: 10  # 최대 커넥션 수
          max-idle: 5
          min-idle: 2
```

### 캐시 서비스 구현
```java
@Service
@RequiredArgsConstructor
public class ProductCacheService {
    
    private final RedisTemplate<String, Object> redisTemplate;
    private static final String CACHE_KEY_PREFIX = "product:";
    private static final Duration CACHE_TTL = Duration.ofHours(1);
    
    public void cacheProduct(Product product) {
        String key = CACHE_KEY_PREFIX + product.getId();
        redisTemplate.opsForValue().set(key, product, CACHE_TTL);
    }
    
    public Product getProduct(Long id) {
        String key = CACHE_KEY_PREFIX + id;
        return (Product) redisTemplate.opsForValue().get(key);
    }
    
    public void evictProduct(Long id) {
        String key = CACHE_KEY_PREFIX + id;
        redisTemplate.delete(key);
    }
    
    // 패턴 매칭으로 여러 키 삭제
    public void evictProductsByCategory(String category) {
        Set<String> keys = redisTemplate.keys(CACHE_KEY_PREFIX + category + ":*");
        if (keys != null && !keys.isEmpty()) {
            redisTemplate.delete(keys);
        }
    }
}
```

## 주의사항 / 함정

### 1. 메모리 부족 문제
❌ **잘못된 접근**
```java
// TTL 없이 무한정 저장
redisTemplate.opsForValue().set("user:" + id, user);
```

✅ **올바른 접근**
```java
// 반드시 만료 시간 설정
redisTemplate.opsForValue().set("user:" + id, user, Duration.ofMinutes(30));
```

**대응 전략**
- Maxmemory 정책 설정: `volatile-lru`, `allkeys-lru`
- 메모리 모니터링 (Redis INFO 명령)
- 적절한 TTL 설정

### 2. Cache Stampede (캐시 갱신 폭주)
**문제 상황**: 인기 있는 캐시가 만료될 때 수천 개의 요청이 동시에 DB를 조회

✅ **해결: Lock 기반 갱신**
```java
public Product getProductWithLock(Long id) {
    String cacheKey = "product:" + id;
    String lockKey = "lock:product:" + id;
    
    // 1차: 캐시 조회
    Product cached = (Product) redisTemplate.opsForValue().get(cacheKey);
    if (cached != null) return cached;
    
    // 2차: 락 획득 시도
    Boolean acquired = redisTemplate.opsForValue()
        .setIfAbsent(lockKey, "LOCKED", Duration.ofSeconds(10));
    
    if (Boolean.TRUE.equals(acquired)) {
        try {
            // DB 조회 및 캐시 저장
            Product product = productRepository.findById(id)
                .orElseThrow(ProductNotFoundException::new);
            redisTemplate.opsForValue().set(cacheKey, product, Duration.ofHours(1));
            return product;
        } finally {
            redisTemplate.delete(lockKey);
        }
    } else {
        // 다른 스레드가 갱신 중 - 짧은 대기 후 재시도
        Thread.sleep(100);
        return getProductWithLock(id);
    }
}
```

### 3. 데이터 일관성 문제
**Write-Through vs Write-Behind**
```java
// ❌ Write-Behind (비동기 쓰기): 데이터 유실 위험
public void updateProduct(Product product) {
    productRepository.save(product);  // DB 저장
    // 비동기로 캐시 업데이트 (실패 시 불일치)
    asyncUpdateCache(product);
}

// ✅ Write-Through (동기 쓰기): 일관성 보장
@Transactional
public void updateProduct(Product product) {
    productRepository.save(product);  // DB 저장
    redisTemplate.delete("product:" + product.getId());  // 캐시 무효화
    // 또는 즉시 새 값으로 갱신
    redisTemplate.opsForValue().set(
        "product:" + product.getId(), 
        product, 
        Duration.ofHours(1)
    );
}
```

### 4. Redis Keys 명령 사용 금지 (프로덕션)
```java
// ❌ 절대 금지: 전체 키 검색은 서버를 멈출 수 있음
Set<String> allKeys = redisTemplate.keys("*");

// ✅ SCAN 명령 사용
ScanOptions options = ScanOptions.scanOptions()
    .match("product:*")
    .count(100)
    .build();
Cursor<byte[]> cursor = redisTemplate.executeWithStickyConnection(
    connection -> connection.scan(options)
);
```

## 관련 개념
- [[Redis-데이터구조-5가지타입]] (작성 예정)
- [[Redis-활용-캐싱전략]] (작성 예정)
- [[Redis-성능-최적화]] (작성 예정)

## 학습 로드맵 (TODO)
- Redis Cluster 샤딩 전략
- Redis Sentinel 고가용성 구성
- Redis vs Memcached 비교
- Redis Pub/Sub 메시징
- Redis Streams 이벤트 처리

## 면접 질문
1. [[Redis-기본개념-면접]]
2. Redis가 빠른 이유를 메모리 구조 관점에서 설명하시오
3. Redis 데이터 영속성을 보장하는 방법 2가지는?
4. Cache Stampede 문제와 해결 방법은?

## 참고 자료
- [Redis 공식 문서](https://redis.io/docs/)
- [Spring Data Redis 공식 문서](https://docs.spring.io/spring-data/redis/docs/current/reference/html/)
- [AWS ElastiCache for Redis](https://aws.amazon.com/ko/elasticache/redis/)
