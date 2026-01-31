---
tags:
  - interview
  - database
  - redis
  - cache
created: 2026-01-31
difficulty: 중
---

# Redis 기본개념 면접

## 질문
> Redis가 무엇이며, 왜 사용하는지 설명해주세요.

## 핵심 답변 (3줄)
1. Redis는 인메모리 Key-Value 저장소로, 모든 데이터를 RAM에 보관하여 디스크 기반 DB 대비 100~1000배 빠른 응답속도를 제공합니다.
2. 주로 캐싱, 세션 관리, 실시간 순위표 등에 활용되며, DB 부하를 줄이고 응답 속도를 획기적으로 개선할 수 있습니다.
3. Redis Sentinel과 Cluster를 통해 고가용성과 수평 확장을 지원하며, RDB/AOF로 데이터 영속성을 보장합니다.

## 상세 설명

### Redis의 핵심 특징

**1. 인메모리 기반 성능**
- 평균 응답시간: 1ms 미만 (MySQL: 수십~수백 ms)
- RAM에서 직접 읽기/쓰기, 디스크 I/O 없음
- 초당 수백만 건 요청 처리 가능

**2. 다양한 데이터 구조**
- String, List, Set, Hash, Sorted Set 등
- 각 구조에 최적화된 명령어 제공
- Sorted Set으로 순위표를 O(log N) 성능으로 구현

**3. 영속성 옵션**
- RDB: 특정 시점 스냅샷 저장
- AOF: 모든 쓰기 작업 로그 기록
- Hybrid: 두 방식 조합 가능

## 코드 예시

### Spring Boot Redis 캐싱

```java
@Service
@RequiredArgsConstructor
public class ProductService {
    
    private final ProductRepository productRepository;
    private final RedisTemplate<String, Object> redisTemplate;
    
    public Product getProduct(Long id) {
        String cacheKey = "product:" + id;
        
        // 캐시 조회
        Product cached = (Product) redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) return cached;
        
        // DB 조회 및 캐시 저장
        Product product = productRepository.findById(id)
            .orElseThrow(() -> new ProductNotFoundException(id));
        redisTemplate.opsForValue().set(cacheKey, product, Duration.ofHours(1));
        
        return product;
    }
}
```

## 꼬리 질문 예상

### Q1: Redis는 왜 빠른가요?
- 메모리 기반: RAM 접근속도(ns)는 SSD(μs)보다 1000배 빠름
- 싱글 스레드: Context Switching 오버헤드 없음
- Hash Table 기반: O(1) 조회 성능

### Q2: 데이터 유실 방지 방법은?
- RDB: 특정 시점 스냅샷 (빠른 복구)
- AOF: 모든 쓰기 로그 기록 (손실 최소화)
- Hybrid: RDB + AOF 조합 (프로덕션 권장)

### Q3: Cache Stampede 문제 해결법은?
분산 락으로 첫 요청만 DB 조회하도록 제어
```java
Boolean acquired = redisTemplate.opsForValue()
    .setIfAbsent(lockKey, "LOCKED", Duration.ofSeconds(10));
```

### Q4: Redis vs Memcached 차이는?
- Redis: 다양한 데이터 구조, 영속성, 복제 지원
- Memcached: String만, 영속성 없음, 단순 캐싱

### Q5: 메모리 부족 시 동작은?
Maxmemory Policy에 따라:
- allkeys-lru: 가장 오래 사용 안 된 키 삭제
- volatile-lru: 만료시간 있는 키 중 삭제
- noeviction: 쓰기 거부

## 참고
- [[Redis-기본개념-인메모리DB]]
