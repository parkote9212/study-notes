---
tags:
  - study
  - redis
  - cache
  - nosql
  - in-memory
created: 2026-02-15
---

# Redis 기본개념

## 한 줄 요약
> Redis는 In-Memory 기반의 Key-Value 저장소로, 빠른 읽기/쓰기가 필요한 캐싱, 세션 관리, 실시간 데이터 처리에 사용되는 NoSQL 데이터베이스이다.

## 상세 설명

### Redis란?
**REmote DIctionary Server**의 약자로, 메모리 기반의 오픈소스 데이터 저장소입니다.

**핵심 특징:**
1. **In-Memory 기반**: 모든 데이터를 RAM에 저장하여 초고속 읽기/쓰기 가능
2. **Key-Value 구조**: 간단한 데이터 모델로 빠른 접근
3. **다양한 자료구조**: String, List, Set, Hash, Sorted Set 등 지원
4. **영속성 옵션**: RDB, AOF를 통해 데이터 보존 가능
5. **단일 스레드**: 원자성 보장, Race Condition 방지

### 왜 사용하는가?

**1. 성능 향상**
- DB 조회보다 100배 이상 빠른 응답 속도
- 네트워크 I/O 감소

**2. 서버 부하 감소**
- 반복적인 DB 쿼리를 캐싱으로 대체
- DB 병목 현상 완화

**3. 실시간 처리**
- 실시간 랭킹, 좋아요 수, 조회수 등
- Pub/Sub을 통한 메시징

### 실무 사용 사례

**1. 캐싱 (가장 일반적)**
```
사용자 → API 서버 → Redis 확인 → (캐시 있으면) 즉시 반환
                  → (캐시 없으면) DB 조회 → Redis 저장 → 반환
```

**2. 세션 관리**
- 로그인 세션 정보 저장 (JWT 토큰, 사용자 정보)
- 여러 서버 간 세션 공유 (분산 환경)

**3. 실시간 랭킹/카운터**
- 게시글 조회수, 좋아요 수
- 실시간 검색어 순위

**4. 분산 락 (Distributed Lock)**
- 여러 서버에서 동시 작업 방지
- 재고 관리, 중복 요청 방지

**5. 메시징 (Pub/Sub)**
- 실시간 알림, 채팅
- 이벤트 브로드캐스팅

## 코드 예시

### Spring Boot 의존성 추가
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
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
```

### Redis 기본 사용 (Java)
```java
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import java.util.concurrent.TimeUnit;

@Service
public class CacheService {
    
    private final RedisTemplate<String, Object> redisTemplate;
    
    public CacheService(RedisTemplate<String, Object> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }
    
    // 데이터 저장 (TTL 30분)
    public void setCache(String key, Object value) {
        redisTemplate.opsForValue().set(key, value, 30, TimeUnit.MINUTES);
    }
    
    // 데이터 조회
    public Object getCache(String key) {
        return redisTemplate.opsForValue().get(key);
    }
    
    // 데이터 삭제
    public void deleteCache(String key) {
        redisTemplate.delete(key);
    }
    
    // 존재 여부 확인
    public boolean hasKey(String key) {
        return Boolean.TRUE.equals(redisTemplate.hasKey(key));
    }
}
```

### 실무 적용 예시: 상품 정보 캐싱
```java
@Service
public class ProductService {
    
    private final ProductRepository productRepository;
    private final RedisTemplate<String, Product> redisTemplate;
    
    public Product getProduct(Long productId) {
        String cacheKey = "product:" + productId;
        
        // 1. Redis에서 먼저 확인
        Product cachedProduct = (Product) redisTemplate.opsForValue().get(cacheKey);
        if (cachedProduct != null) {
            return cachedProduct; // 캐시 히트
        }
        
        // 2. 캐시 미스 → DB 조회
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new NotFoundException("상품 없음"));
        
        // 3. Redis에 저장 (1시간 TTL)
        redisTemplate.opsForValue().set(cacheKey, product, 1, TimeUnit.HOURS);
        
        return product;
    }
}
```

## 주의사항 / 함정

### 1. 메모리 관리
❌ **문제**: Redis는 메모리 기반이므로 메모리 부족 시 서비스 장애
✅ **해결**: 
- Eviction 정책 설정 (maxmemory-policy)
- TTL을 반드시 설정하여 자동 삭제
- 모니터링으로 메모리 사용량 추적

### 2. 캐시 일관성 문제
❌ **문제**: DB 업데이트 후 Redis 캐시가 업데이트되지 않아 오래된 데이터 반환
✅ **해결**:
- DB 업데이트 시 Redis 캐시도 함께 삭제/갱신
- TTL을 짧게 설정하여 주기적으로 갱신

```java
@Transactional
public void updateProduct(Long productId, ProductDto dto) {
    // 1. DB 업데이트
    productRepository.update(productId, dto);
    
    // 2. Redis 캐시 삭제 (다음 조회 시 재캐싱)
    redisTemplate.delete("product:" + productId);
}
```

### 3. 단일 장애점 (Single Point of Failure)
❌ **문제**: Redis 서버 다운 시 전체 서비스 영향
✅ **해결**:
- Redis Sentinel (자동 장애 조치)
- Redis Cluster (데이터 분산)
- 캐시 실패 시 DB로 폴백

### 4. 대용량 데이터 저장 금지
- Redis는 빠른 접근이 필요한 "작은 데이터"에 적합
- 큰 파일, 이미지는 S3 등 별도 저장소 사용

### 5. 직렬화 문제
- 객체를 Redis에 저장 시 직렬화 필요
- JSON 직렬화 설정 권장 (Jackson2JsonRedisSerializer)

## 관련 개념
- [[Redis-데이터타입과명령어]] - String, Hash, List, Set 등
- [[Redis-캐싱전략]] - Cache-Aside, Write-Through, Eviction
- [[Redis-PubSub과트랜잭션]] - 메시징과 트랜잭션 처리
- [[Redis-Spring통합]] - Spring Data Redis, RedisTemplate
- [[Kafka-기본개념]] - 메시징 시스템 비교

## 면접 질문

1. **Redis가 무엇이며, 왜 사용하나요?**
   - In-Memory 기반 Key-Value 저장소
   - DB 조회 성능 향상(캐싱), 실시간 데이터 처리
   - 세션 관리, 랭킹, 분산 락 등 다양한 용도

2. **Redis와 Memcached의 차이는?**
   - Redis: 다양한 자료구조, 영속성 지원, Pub/Sub
   - Memcached: 단순 Key-Value, 캐싱 전용

3. **Redis가 빠른 이유는?**
   - In-Memory 저장 (RAM)
   - 단일 스레드로 컨텍스트 스위칭 없음
   - 간단한 Key-Value 구조

4. **Redis의 단점은?**
   - 메모리 용량 제한
   - 단일 스레드로 인한 처리량 한계
   - 데이터 손실 가능성 (메모리 기반)

5. **캐시 일관성 문제를 어떻게 해결하나요?**
   - DB 업데이트 시 캐시 삭제/갱신
   - TTL 설정으로 주기적 갱신
   - Cache-Aside, Write-Through 패턴 적용

6. **프로젝트에서 Redis를 어떻게 사용했나요? (BizSync 예시)**
   - 실시간 협업 시스템에서 세션 관리
   - WebSocket 연결 정보 저장
   - Pub/Sub으로 실시간 알림 전송

## 참고 자료
- [Redis 공식 문서](https://redis.io/docs/)
- [Spring Data Redis 공식 문서](https://docs.spring.io/spring-data/redis/docs/current/reference/html/)
- [Redis 한국 커뮤니티](https://redis.io/community/)
