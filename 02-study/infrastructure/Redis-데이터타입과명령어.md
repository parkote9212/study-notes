---
tags:
  - study
  - redis
  - data-structure
  - commands
created: 2026-02-15
---

# Redis 데이터타입과 명령어

## 한 줄 요약
> Redis는 String, Hash, List, Set, Sorted Set 등 5가지 핵심 자료구조를 제공하며, 각 용도에 맞는 명령어로 효율적인 데이터 처리가 가능하다.

## 상세 설명

### Redis의 자료구조가 중요한 이유
- 단순 Key-Value를 넘어 **복잡한 데이터 구조** 지원
- 적절한 자료구조 선택 → **성능 최적화**
- 실무 문제를 **간단한 명령어로 해결**

### 자료구조 선택 가이드

| 자료구조 | 사용 사례 | 시간 복잡도 |
|---------|----------|-----------|
| String | 캐싱, 카운터, 세션 | O(1) |
| Hash | 객체 저장, 사용자 정보 | O(1) |
| List | 최근 활동, 큐, 스택 | O(1) ~ O(N) |
| Set | 태그, 좋아요, 중복 제거 | O(1) |
| Sorted Set | 랭킹, 리더보드, 우선순위 큐 | O(log N) |

## 1. String (가장 기본)

### 특징
- 가장 단순하고 많이 사용되는 타입
- 최대 512MB까지 저장 가능
- 숫자로 변환하여 증감 연산 가능

### 주요 명령어
```bash
# 저장 / 조회
SET key value
GET key

# TTL 설정 (초 단위)
SETEX key 60 value    # 60초 후 삭제
SET key value EX 60   # 동일

# 존재 시에만 저장 / 없을 때만 저장
SET key value XX      # 기존 값 있으면 업데이트
SET key value NX      # 기존 값 없으면 저장 (분산 락에 활용)

# 숫자 증감
SET counter 100
INCR counter          # 101
INCRBY counter 5      # 106
DECR counter          # 105

# 여러 개 한번에
MSET key1 val1 key2 val2
MGET key1 key2
```

### 실무 코드 예시: 조회수 카운터
```java
@Service
public class ViewCountService {
    
    private final RedisTemplate<String, String> redisTemplate;
    
    // 조회수 증가
    public Long incrementViewCount(Long postId) {
        String key = "post:view:" + postId;
        return redisTemplate.opsForValue().increment(key);
    }
    
    // 조회수 조회
    public Long getViewCount(Long postId) {
        String key = "post:view:" + postId;
        String count = redisTemplate.opsForValue().get(key);
        return count != null ? Long.parseLong(count) : 0L;
    }
}
```

## 2. Hash (객체 저장)

### 특징
- **필드-값 쌍**으로 구성 (자바의 HashMap과 유사)
- 객체를 효율적으로 저장 가능
- 일부 필드만 수정 가능

### 주요 명령어
```bash
# 필드 저장 / 조회
HSET user:1 name "홍길동"
HSET user:1 age 25
HGET user:1 name          # "홍길동"

# 여러 필드 한번에
HMSET user:1 name "홍길동" age 25 email "hong@example.com"
HGETALL user:1            # 모든 필드-값 반환

# 필드 존재 확인
HEXISTS user:1 name       # 1 (존재)

# 필드 삭제
HDEL user:1 email

# 모든 필드 / 값만 조회
HKEYS user:1              # [name, age]
HVALS user:1              # ["홍길동", "25"]

# 숫자 필드 증감
HINCRBY user:1 age 1      # 26
```

### 실무 코드 예시: 사용자 세션 관리
```java
@Service
public class SessionService {
    
    private final RedisTemplate<String, Object> redisTemplate;
    
    // 세션 저장
    public void createSession(String sessionId, UserSession session) {
        String key = "session:" + sessionId;
        
        Map<String, String> sessionData = Map.of(
            "userId", session.getUserId().toString(),
            "username", session.getUsername(),
            "loginTime", session.getLoginTime().toString(),
            "role", session.getRole()
        );
        
        redisTemplate.opsForHash().putAll(key, sessionData);
        redisTemplate.expire(key, 30, TimeUnit.MINUTES); // 30분 TTL
    }
    
    // 세션 조회
    public UserSession getSession(String sessionId) {
        String key = "session:" + sessionId;
        Map<Object, Object> data = redisTemplate.opsForHash().entries(key);
        
        if (data.isEmpty()) return null;
        
        return UserSession.builder()
            .userId(Long.parseLong((String) data.get("userId")))
            .username((String) data.get("username"))
            .role((String) data.get("role"))
            .build();
    }
    
    // 특정 필드만 업데이트
    public void updateLastAccess(String sessionId) {
        String key = "session:" + sessionId;
        redisTemplate.opsForHash().put(key, "lastAccess", 
            LocalDateTime.now().toString());
    }
}
```

## 3. List (순서가 있는 데이터)

### 특징
- **양방향 연결 리스트** 구조
- 앞/뒤에서 삽입/삭제가 O(1)
- 최근 활동, 타임라인, 큐 구현에 적합

### 주요 명령어
```bash
# 앞/뒤 추가
LPUSH mylist "첫번째"     # 왼쪽(앞)에 추가
RPUSH mylist "마지막"     # 오른쪽(뒤)에 추가

# 앞/뒤 제거 및 반환
LPOP mylist               # 첫번째 제거 후 반환
RPOP mylist               # 마지막 제거 후 반환

# 범위 조회 (0부터 시작, -1은 끝)
LRANGE mylist 0 -1        # 전체 조회
LRANGE mylist 0 9         # 최근 10개

# 길이 조회
LLEN mylist

# 특정 인덱스 조회
LINDEX mylist 0           # 첫번째 요소

# 블로킹 팝 (큐 구현)
BLPOP mylist 10           # 10초 대기 후 팝
```

### 실무 코드 예시: 최근 활동 로그
```java
@Service
public class ActivityLogService {
    
    private final RedisTemplate<String, String> redisTemplate;
    private static final int MAX_LOG_SIZE = 100;
    
    // 활동 추가 (최신 항목이 앞에)
    public void addActivity(Long userId, String activity) {
        String key = "activity:" + userId;
        
        // 왼쪽에 추가 (최신 항목)
        redisTemplate.opsForList().leftPush(key, activity);
        
        // 100개 넘으면 오래된 항목 제거
        redisTemplate.opsForList().trim(key, 0, MAX_LOG_SIZE - 1);
        
        // TTL 7일
        redisTemplate.expire(key, 7, TimeUnit.DAYS);
    }
    
    // 최근 활동 조회
    public List<String> getRecentActivities(Long userId, int count) {
        String key = "activity:" + userId;
        return redisTemplate.opsForList().range(key, 0, count - 1);
    }
}
```

### 큐 구현 예시
```java
@Service
public class MessageQueueService {
    
    private final RedisTemplate<String, String> redisTemplate;
    
    // 메시지 추가 (Producer)
    public void enqueue(String queueName, String message) {
        redisTemplate.opsForList().rightPush(queueName, message);
    }
    
    // 메시지 처리 (Consumer)
    public String dequeue(String queueName, long timeout) {
        // 블로킹 팝: 메시지 올 때까지 대기
        return redisTemplate.opsForList()
            .leftPop(queueName, timeout, TimeUnit.SECONDS);
    }
}
```

## 4. Set (중복 없는 집합)

### 특징
- **중복 불가**, 순서 없음
- 집합 연산 지원 (합집합, 교집합, 차집합)
- 태그, 좋아요, 팔로우 관계 등에 활용

### 주요 명령어
```bash
# 추가 / 제거
SADD myset "value1" "value2"
SREM myset "value1"

# 존재 확인
SISMEMBER myset "value2"  # 1 (존재)

# 모든 멤버 조회
SMEMBERS myset

# 개수
SCARD myset

# 집합 연산
SUNION set1 set2          # 합집합
SINTER set1 set2          # 교집합
SDIFF set1 set2           # 차집합 (set1 - set2)

# 랜덤 추출
SRANDMEMBER myset 3       # 랜덤 3개
SPOP myset                # 랜덤 제거 후 반환
```

### 실무 코드 예시: 좋아요 기능
```java
@Service
public class LikeService {
    
    private final RedisTemplate<String, String> redisTemplate;
    
    // 좋아요 추가
    public boolean addLike(Long postId, Long userId) {
        String key = "post:likes:" + postId;
        Long result = redisTemplate.opsForSet().add(key, userId.toString());
        return result != null && result > 0; // 새로 추가되면 true
    }
    
    // 좋아요 취소
    public boolean removeLike(Long postId, Long userId) {
        String key = "post:likes:" + postId;
        Long result = redisTemplate.opsForSet().remove(key, userId.toString());
        return result != null && result > 0;
    }
    
    // 좋아요 개수
    public Long getLikeCount(Long postId) {
        String key = "post:likes:" + postId;
        return redisTemplate.opsForSet().size(key);
    }
    
    // 좋아요 여부 확인
    public boolean hasLiked(Long postId, Long userId) {
        String key = "post:likes:" + postId;
        return Boolean.TRUE.equals(
            redisTemplate.opsForSet().isMember(key, userId.toString())
        );
    }
    
    // 공통 좋아요 (두 게시글 모두 좋아요한 사용자)
    public Set<String> getCommonLikes(Long postId1, Long postId2) {
        String key1 = "post:likes:" + postId1;
        String key2 = "post:likes:" + postId2;
        return redisTemplate.opsForSet().intersect(key1, key2);
    }
}
```

## 5. Sorted Set (정렬된 집합)

### 특징
- **점수(score)**를 기준으로 자동 정렬
- 랭킹, 리더보드, 우선순위 큐에 최적
- 점수 범위 조회, 순위 조회 가능

### 주요 명령어
```bash
# 추가 (점수와 함께)
ZADD leaderboard 100 "user1"
ZADD leaderboard 200 "user2" 150 "user3"

# 점수 증가
ZINCRBY leaderboard 10 "user1"  # 110

# 순위 조회 (0부터 시작, 낮은 점수부터)
ZRANGE leaderboard 0 -1         # 모든 멤버 (점수 오름차순)
ZREVRANGE leaderboard 0 9       # 상위 10명 (점수 내림차순)
ZREVRANGE leaderboard 0 9 WITHSCORES  # 점수 포함

# 특정 멤버의 점수
ZSCORE leaderboard "user1"

# 특정 멤버의 순위 (0부터 시작)
ZRANK leaderboard "user1"       # 낮은 점수부터 순위
ZREVRANK leaderboard "user1"    # 높은 점수부터 순위

# 점수 범위 조회
ZRANGEBYSCORE leaderboard 100 200

# 개수
ZCARD leaderboard

# 제거
ZREM leaderboard "user1"
```

### 실무 코드 예시: 실시간 랭킹 시스템
```java
@Service
public class RankingService {
    
    private final RedisTemplate<String, String> redisTemplate;
    
    // 점수 추가/업데이트
    public void updateScore(String userId, double score) {
        String key = "ranking:global";
        redisTemplate.opsForZSet().add(key, userId, score);
    }
    
    // 점수 증가 (게임 점수 획득)
    public Double incrementScore(String userId, double delta) {
        String key = "ranking:global";
        return redisTemplate.opsForZSet().incrementScore(key, userId, delta);
    }
    
    // 상위 N명 조회
    public List<RankingDto> getTopRanking(int count) {
        String key = "ranking:global";
        
        // 점수 높은 순으로 조회
        Set<ZSetOperations.TypedTuple<String>> topUsers = 
            redisTemplate.opsForZSet().reverseRangeWithScores(key, 0, count - 1);
        
        List<RankingDto> ranking = new ArrayList<>();
        int rank = 1;
        for (ZSetOperations.TypedTuple<String> tuple : topUsers) {
            ranking.add(RankingDto.builder()
                .rank(rank++)
                .userId(tuple.getValue())
                .score(tuple.getScore())
                .build());
        }
        return ranking;
    }
    
    // 내 순위 조회
    public Long getMyRank(String userId) {
        String key = "ranking:global";
        Long rank = redisTemplate.opsForZSet().reverseRank(key, userId);
        return rank != null ? rank + 1 : null; // 0부터 시작이므로 +1
    }
    
    // 내 점수 조회
    public Double getMyScore(String userId) {
        String key = "ranking:global";
        return redisTemplate.opsForZSet().score(key, userId);
    }
    
    // 점수 범위로 조회 (1000점 이상)
    public Set<String> getUsersAboveScore(double minScore) {
        String key = "ranking:global";
        return redisTemplate.opsForZSet()
            .rangeByScore(key, minScore, Double.MAX_VALUE);
    }
}
```

## 주의사항 / 함정

### 1. 대용량 데이터 처리 시 주의
❌ **KEYS, SMEMBERS, HGETALL 등은 O(N)**
```bash
KEYS *              # 절대 프로덕션에서 사용 금지!
SMEMBERS large_set  # Set이 크면 블로킹
```

✅ **대안**:
```bash
SCAN 0              # 커서 기반 순회
SSCAN myset 0       # Set 순회
HSCAN user:1 0      # Hash 순회
```

### 2. List의 중간 삽입/삭제는 비효율
- `LINSERT`, `LSET`은 O(N) 복잡도
- 중간 수정이 많으면 다른 자료구조 고려

### 3. Sorted Set의 메모리 사용량
- 각 멤버마다 점수 저장 → 메모리 많이 사용
- 대용량 랭킹은 주기적으로 정리 필요

### 4. 자료구조 선택 실수
```java
// ❌ 나쁜 예: 랭킹을 List로 구현
// 순위 조회할 때마다 전체 정렬 필요

// ✅ 좋은 예: Sorted Set 사용
// 자동 정렬, O(log N) 삽입
```

## 관련 개념
- [[Redis-기본개념]] - Redis 개요와 사용 이유
- [[Redis-캐싱전략]] - 데이터 저장 전략
- [[Redis-Spring통합]] - Spring에서 자료구조 활용
- [[알고리즘-자료구조]] - 기본 자료구조 개념

## 면접 질문

1. **Redis의 5가지 자료구조를 설명하고, 각각의 사용 사례를 말해보세요.**
   - String: 캐싱, 카운터, 세션
   - Hash: 객체 저장, 사용자 정보
   - List: 최근 활동, 큐, 타임라인
   - Set: 태그, 좋아요, 중복 제거
   - Sorted Set: 랭킹, 리더보드

2. **좋아요 기능을 Redis로 구현한다면 어떤 자료구조를 사용하겠습니까?**
   - Set 사용
   - 중복 방지, O(1) 추가/삭제
   - `SADD post:likes:123 userId`

3. **실시간 랭킹 시스템을 Redis로 구현한다면?**
   - Sorted Set 사용
   - 점수 자동 정렬, O(log N) 삽입
   - `ZADD ranking userId score`
   - `ZREVRANGE ranking 0 9` (상위 10명)

4. **Hash와 String 중 객체 저장에 Hash를 선택하는 이유는?**
   - 일부 필드만 수정 가능 (효율적)
   - 메모리 효율적
   - 필드별 TTL은 안 되지만, 전체 Hash에 TTL 가능

5. **KEYS * 명령어가 위험한 이유와 대안은?**
   - O(N) 복잡도로 Redis 블로킹
   - 프로덕션에서 절대 사용 금지
   - 대안: SCAN 명령어 (커서 기반)

6. **List를 Queue로 사용할 때 어떤 명령어 조합을 사용하나요?**
   - Producer: `RPUSH` (뒤에 추가)
   - Consumer: `BLPOP` (앞에서 제거, 블로킹)
   - 또는 `LPUSH` + `BRPOP`

## 참고 자료
- [Redis Data Types 공식 문서](https://redis.io/docs/data-types/)
- [Redis Commands 레퍼런스](https://redis.io/commands/)
- [Spring Data Redis - Operations](https://docs.spring.io/spring-data/redis/docs/current/reference/html/#redis:template)
