# Redis 캐시 전략

## 📌 핵심 요약
반복적인 DB 조회를 최소화하여 **응답 속도 92% 개선**, DB 쿼리 95% 감소

---

## 🎯 도입 배경

### 문제 상황
```
1. 프로젝트 목록 조회 시 매번 DB 쿼리 발생 (180ms)
2. 매 요청마다 권한 체크를 위해 DB 조회 (50ms)
3. 대시보드 집계 쿼리 부하 (650ms)
→ DB CPU 45%, 응답 지연
```

### 해결 목표
- 자주 조회되지만 변경이 적은 데이터 캐싱
- DB 부하 감소
- 응답 속도 개선

---

## 💡 기술적 의사결정

### 1. Redis 선택 이유

#### 로컬 캐시(Caffeine) vs Redis
```java
// ❌ 로컬 캐시의 한계
@Cacheable(cacheNames = "projects")  // Caffeine
public List<ProjectDTO> getProjects(Long userId) {
    // 문제: 각 서버마다 별도 캐시
    // → 서버 A에서 캐시 갱신해도 서버 B는 모름
}
```

| 구분 | Caffeine (로컬) | Redis (중앙) |
|------|-----------------|--------------|
| 캐시 동기화 | ❌ 서버마다 독립적 | ✅ 모든 서버 공유 |
| 확장성 | ❌ Scale-out 시 문제 | ✅ 분산 환경 적합 |
| 메모리 | 각 서버마다 사용 | 중앙 집중 |

**결론**: 향후 다중 서버 환경 고려 → Redis 선택

---

## 🏗️ 구현 상세

### 1. 프로젝트 목록 캐시

```java
@Service
@RequiredArgsConstructor
public class ProjectService {
    
    @Cacheable(value = "projects", key = "#userId")
    public List<ProjectListResponseDTO> getMyProjects(Long userId) {
        // 최초 1회만 DB 조회
        // 이후 요청은 Redis에서 반환
        return projectRepository.findByUserId(userId)
            .stream()
            .map(ProjectListResponseDTO::from)
            .toList();
    }
    
    @CacheEvict(value = "projects", key = "#userId")
    public Long createProject(Long userId, ProjectCreateRequestDTO dto) {
        // 프로젝트 생성 후 캐시 무효화
        Project project = Project.builder()
            .name(dto.name())
            .description(dto.description())
            .build();
        return projectRepository.save(project).getProjectId();
    }
}
```

**개선 결과**:
- 응답 시간: 180ms → 15ms (92% ↓)
- DB 쿼리: 100 req/sec → 5 req/sec (95% ↓)

---

### 2. 권한 캐시 (AOP 성능 개선)

```java
@Cacheable(
    value = "projectPermission", 
    key = "#projectId + ':' + #userId"
)
public ProjectMember.Role getUserRoleInProject(Long projectId, Long userId) {
    return projectMemberRepository
        .findByProjectAndUser(projectId, userId)
        .map(ProjectMember::getRole)
        .orElse(null);
}

@CacheEvict(
    value = "projectPermission", 
    key = "#projectId + ':' + #userId"
)
public void updateMemberRole(Long projectId, Long userId, Role newRole) {
    // 역할 변경 후 권한 캐시 무효화
    ProjectMember member = projectMemberRepository
        .findByProjectAndUser(projectId, userId)
        .orElseThrow();
    member.updateRole(newRole);
}
```

**개선 결과**:
- AOP 권한 체크: 50ms → 5ms (90% ↓)
- 매 API 요청마다 발생하던 권한 조회 캐싱

---

### 3. 대시보드 통계 캐시

```java
@Cacheable(value = "dashboardStats", key = "#userId")
public DashboardStatsDTO getDashboardStats(Long userId) {
    // 복잡한 집계 쿼리 (MyBatis)
    int totalProjects = dashboardMapper.countUserProjects(userId);
    int completedTasks = dashboardMapper.countCompletedTasks(userId);
    int pendingApprovals = dashboardMapper.countPendingApprovals(userId);
    
    return DashboardStatsDTO.builder()
        .totalProjects(totalProjects)
        .completedTasks(completedTasks)
        .pendingApprovals(pendingApprovals)
        .build();
}
```

**개선 결과**:
- 대시보드 로딩: 650ms → 80ms (88% ↓)
- DB CPU: 45% → 12%

---

## ⚙️ Redis 설정

### 캐시별 TTL 전략

```java
@Configuration
@EnableCaching
public class RedisConfig {
    
    @Bean
    public CacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheManager.RedisCacheManagerBuilder builder = 
            RedisCacheManager.builder(connectionFactory)
                .cacheDefaults(defaultCacheConfig());
        
        // 캐시별 개별 TTL 설정
        Map<String, RedisCacheConfiguration> cacheConfigs = new HashMap<>();
        
        cacheConfigs.put("projects", 
            cacheConfig().entryTtl(Duration.ofHours(2)));      // 변경 적음
        
        cacheConfigs.put("projectPermission", 
            cacheConfig().entryTtl(Duration.ofMinutes(30)));   // 중간
        
        cacheConfigs.put("dashboardStats", 
            cacheConfig().entryTtl(Duration.ofMinutes(10)));   // 실시간성 필요
        
        return builder
            .withInitialCacheConfigurations(cacheConfigs)
            .build();
    }
    
    private RedisCacheConfiguration cacheConfig() {
        return RedisCacheConfiguration.defaultCacheConfig()
            .serializeKeysWith(
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new StringRedisSerializer())
            )
            .serializeValuesWith(
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new GenericJackson2JsonRedisSerializer())
            );
    }
}
```

---

## 🔄 캐시 무효화 전략

### 이벤트 기반 캐시 갱신

```java
@Service
@RequiredArgsConstructor
public class CacheEvictionService {
    
    private final CacheManager cacheManager;
    
    @EventListener
    public void handleProjectUpdated(ProjectUpdatedEvent event) {
        // 프로젝트 수정 시 관련 캐시 모두 무효화
        Cache cache = cacheManager.getCache("projects");
        if (cache != null) {
            cache.evict(event.getUserId());
        }
    }
    
    @EventListener
    public void handleTaskCompleted(TaskCompletedEvent event) {
        // 태스크 완료 시 대시보드 캐시 무효화
        Cache cache = cacheManager.getCache("dashboardStats");
        if (cache != null) {
            cache.evict(event.getUserId());
        }
    }
}
```

**장점**:
- 데이터 변경 시 즉시 캐시 무효화
- 항상 최신 데이터 보장

---

## 📊 성능 측정 결과

### JMeter 부하 테스트
- 환경: 100명 동시 사용자, 5분간 요청

| API | Before | After | 개선율 |
|-----|--------|-------|--------|
| GET /api/projects | 180ms | 15ms | **92% ↓** |
| GET /api/dashboard | 650ms | 80ms | **88% ↓** |
| AOP 권한 체크 | 50ms | 5ms | **90% ↓** |

### DB 쿼리 감소
- 프로젝트 목록: 100 req/sec → 5 req/sec (95% 감소)
- 권한 조회: 500 req/sec → 25 req/sec (95% 감소)

### 리소스 사용량
- **Redis 메모리**: 약 50MB (1000명 사용자 기준)
- **DB CPU**: 45% → 12% (33%p 감소)

---

## 🔍 모니터링

### Redis 메모리 모니터링

```bash
# Redis 메모리 정보
redis-cli INFO memory

# 캐시 키 확인
redis-cli KEYS "projects::*"
redis-cli KEYS "projectPermission::*"

# 캐시 TTL 확인
redis-cli TTL "projects::123"
```

### Spring Actuator 캐시 통계

```yaml
management:
  endpoints:
    web:
      exposure:
        include: caches, metrics
  metrics:
    enable:
      cache: true
```

```bash
# 캐시 통계 확인
curl http://localhost:8080/actuator/caches
curl http://localhost:8080/actuator/metrics/cache.gets
curl http://localhost:8080/actuator/metrics/cache.hits
```

---

## 💬 면접 예상 질문

### Q1. Redis를 선택한 이유는?
**A**: 초기에는 로컬 캐시(Caffeine)도 고려했지만, **향후 다중 서버 환경(Scale-out)을 고려**하여 Redis를 선택했습니다. 로컬 캐시는 각 서버마다 독립적인 캐시를 가지기 때문에 **캐시 동기화 문제**가 발생할 수 있습니다. 반면 Redis는 중앙 집중식 캐시로 모든 서버가 동일한 캐시를 공유하여 데이터 일관성을 보장합니다.

---

### Q2. 캐시 TTL을 어떻게 설정했나요?
**A**: **데이터 변경 빈도**에 따라 차등 설정했습니다:
- `projects`: 2시간 (프로젝트는 자주 변경되지 않음)
- `projectPermission`: 30분 (권한은 가끔 변경)
- `dashboardStats`: 10분 (통계는 실시간성 필요)

추가로 **이벤트 기반 캐시 무효화**를 구현하여 데이터 변경 시 즉시 캐시를 갱신하도록 했습니다.

---

### Q3. 캐시 무효화 전략은?
**A**: **Spring Event를 활용한 이벤트 기반 무효화**를 사용했습니다:
- 프로젝트 생성/수정 → `ProjectUpdatedEvent` 발행 → 프로젝트 캐시 무효화
- 태스크 완료 → `TaskCompletedEvent` 발행 → 대시보드 캐시 무효화

이렇게 하면 **TTL 만료를 기다리지 않고 즉시 캐시 갱신**이 가능합니다.

---

### Q4. Cache Stampede 문제는 고려했나요?
**A**: 네, Cache Stampede(캐시가 만료되는 순간 대량의 DB 요청이 몰리는 문제)를 고려했습니다.

**해결 방법**:
1. **TTL을 랜덤하게 설정** (예: 10분 ± 30초)
2. **조기 갱신** 전략: TTL이 10% 남았을 때 백그라운드에서 미리 갱신
3. **Lock을 활용한 갱신**: 첫 요청만 DB 조회, 나머지는 대기

현재 프로젝트에서는 TTL이 충분히 길고(최소 10분), 사용자 수가 많지 않아 기본 TTL만 적용했지만, 트래픽이 증가하면 조기 갱신 전략을 추가할 계획입니다.

---

### Q5. 캐시 워밍업(Cache Warming)은 어떻게 처리하나요?
**A**: 현재는 **사용자가 요청할 때 캐시가 생성**되는 Lazy Loading 방식을 사용하고 있습니다.

하지만 **서버 재시작 후 초기 트래픽 처리**를 위해 다음을 고려할 수 있습니다:
```java
@EventListener(ApplicationReadyEvent.class)
public void warmUpCache() {
    // 자주 사용되는 데이터 미리 캐싱
    List<Long> activeUserIds = userRepository.findActiveUserIds();
    activeUserIds.forEach(userId -> {
        projectService.getMyProjects(userId);  // 캐시 생성
    });
}
```

---

### Q6. 성능 개선 전후를 어떻게 측정했나요?
**A**: **JMeter를 활용한 부하 테스트**를 진행했습니다:
- 100명 동시 사용자, 5분간 지속 요청
- **Before**: Redis 캐시 비활성화
- **After**: Redis 캐시 활성화
- **측정 지표**: 응답 시간, DB 쿼리 수, CPU 사용률

결과적으로 **응답 시간 92% 감소, DB 쿼리 95% 감소**를 확인했습니다.

---

## 🎓 핵심 학습 포인트

1. **캐시는 변경이 적고 조회가 많은 데이터에 효과적**
   - 프로젝트 목록, 권한 정보, 통계 데이터

2. **TTL은 데이터 특성에 맞게 설정**
   - 변경 빈도 ↓ → TTL ↑
   - 실시간성 필요 → TTL ↓

3. **이벤트 기반 캐시 무효화로 데이터 일관성 보장**
   - Spring Event를 활용한 느슨한 결합

4. **분산 환경을 고려한 기술 선택**
   - 로컬 캐시 vs Redis → Redis 선택

5. **모니터링과 측정이 중요**
   - JMeter 부하 테스트
   - Actuator 캐시 통계
   - 정량적 개선 수치 확보

---

## 📚 참고 자료
- [Spring Cache Abstraction](https://docs.spring.io/spring-framework/reference/integration/cache.html)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [Cache Stampede Problem](https://en.wikipedia.org/wiki/Cache_stampede)
