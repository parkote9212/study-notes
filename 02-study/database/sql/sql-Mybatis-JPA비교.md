---
tags:
  - study
  - database
  - jpa
  - spring
  - mybatis
  - 아키텍처
created: 2026-01-23
difficulty: 상
---
# MyBatis-기술선택-JPA비교

🏷️기술 카테고리: DataBase, JPA, Spring
💡핵심키워드: #JPA, #MyBatis, #아키텍처
💼 면접 빈출도: 최상

# 1. Abstract: 핵심 요약

JPA와 MyBatis는 각각의 장단점이 명확합니다. **프로젝트 특성**에 따라 적절히 선택하거나 **혼용**하는 것이 최선입니다.

**핵심 원칙**:
- JPA: 객체 지향, 생산성
- MyBatis: SQL 제어, 성능
- 상황에 맞게 선택 또는 혼용

# 2. JPA vs MyBatis 비교

## 2.1 핵심 차이점

| 구분 | JPA | MyBatis |
| --- | --- | --- |
| **패러다임** | ORM (객체-관계 매핑) | SQL Mapper |
| **SQL 작성** | 자동 생성 | 직접 작성 |
| **SQL 제어** | 제한적 (JPQL, QueryDSL) | 완전 제어 |
| **성능 튜닝** | 어려움 | 쉬움 |
| **학습 곡선** | 높음 (영속성 컨텍스트 등) | 낮음 (SQL만 알면 됨) |
| **CRUD** | 자동 제공 | 수동 작성 |
| **복잡한 쿼리** | 어려움 | 쉬움 |
| **도메인 모델** | Rich Domain Model | Anemic Model |
| **N+1 문제** | 주의 필요 | 발생 안 함 |
| **DB 변경** | 용이 | 어려움 |

# 3. 선택 기준

## 3.1 JPA 추천 상황

✅ **CRUD 중심 애플리케이션**
- 단순한 조회, 등록, 수정, 삭제가 대부분

✅ **빠른 개발이 필요한 경우**
- 프로토타입, MVP, 스타트업

✅ **도메인 모델이 명확한 경우**
- 비즈니스 로직이 엔티티에 집중

✅ **DB 변경 가능성이 있는 경우**
- MySQL ↔ PostgreSQL 등

✅ **객체 지향 설계 우선**
- DDD(Domain Driven Design) 적용

## 3.2 MyBatis 추천 상황

✅ **복잡한 쿼리가 많은 경우**
- 통계, 리포트, 대시보드

✅ **성능이 매우 중요한 경우**
- 대용량 데이터 처리
- 쿼리 튜닝 필수

✅ **레거시 DB 연동**
- 기존 DB 스키마 변경 불가
- 복잡한 테이블 구조

✅ **SQL 직접 제어 필요**
- 프로시저, 함수 호출
- 특정 DB 기능 활용

✅ **팀의 SQL 역량이 높은 경우**
- DBA 협업이 많은 경우

# 4. 혼용 전략 (Best Practice)

```java
@Service
@RequiredArgsConstructor
public class UserService {
    // JPA Repository
    private final UserRepository userRepository;  
    
    // MyBatis Mapper
    private final UserMapper userMapper;
    
    // ✅ JPA: 단순 CRUD
    public void createUser(User user) {
        userRepository.save(user);
    }
    
    public User getUser(Long id) {
        return userRepository.findById(id)
            .orElseThrow();
    }
    
    // ✅ MyBatis: 복잡한 통계 쿼리
    public List<MonthlyReport> getMonthlyReport(int year) {
        return userMapper.getMonthlyReport(year);
    }
    
    // ✅ MyBatis: 복잡한 조인
    public List<UserDetailDTO> getUserDetails(SearchCondition condition) {
        return userMapper.getUserDetails(condition);
    }
}
```

## 4.1 혼용 시 주의사항

**트랜잭션 관리**:
```java
@Transactional
public void updateUserAndLog(Long userId, String name) {
    // JPA
    User user = userRepository.findById(userId).orElseThrow();
    user.changeName(name);  // Dirty Checking
    
    // MyBatis
    userMapper.insertLog(userId, "이름 변경: " + name);
    
    // 같은 트랜잭션 내에서 실행됨
}
```

**캐시 동기화**:
- JPA의 1차 캐시와 MyBatis는 분리되어 있음
- 같은 데이터를 두 곳에서 조회/수정 시 주의

# 5. 실무 사례

## 5.1 e-커머스

```
- 상품 관리: JPA (CRUD 중심)
- 주문 관리: JPA (도메인 로직 복잡)
- 통계/대시보드: MyBatis (복잡한 집계 쿼리)
- 정산 시스템: MyBatis (성능 중요)
```

## 5.2 금융 시스템

```
- 계좌 관리: JPA (트랜잭션 처리)
- 이체/결제: JPA (도메인 로직)
- 일일 마감: MyBatis (대량 데이터 처리)
- 리포트: MyBatis (복잡한 조회)
```

# 6. Interview Readiness

## Q1: JPA와 MyBatis 중 어떤 것을 선택하시겠습니까?

**A**: "프로젝트의 특성에 따라 다릅니다. CRUD 중심이고 빠른 개발이 필요하면 JPA를, 복잡한 쿼리와 성능 튜닝이 중요하면 MyBatis를 선택합니다. 실무에서는 두 가지를 혼용하여 각각의 장점을 활용하는 것이 효과적입니다."

## Q2: JPA의 가장 큰 단점은?

**A**: "학습 곡선이 높고, 복잡한 쿼리를 작성하기 어렵습니다. 또한 N+1 문제와 같은 성능 이슈를 주의해야 하며, 쿼리 튜닝이 MyBatis보다 어렵습니다."

## Q3: MyBatis의 가장 큰 단점은?

**A**: "모든 SQL을 직접 작성해야 하므로 생산성이 떨어집니다. 또한 DB가 변경되면 SQL을 모두 수정해야 하며, 도메인 모델 패턴 적용이 어렵습니다."

## Q4: 두 가지를 혼용할 때 주의할 점은?

**A**: "같은 트랜잭션 내에서 JPA와 MyBatis를 함께 사용할 때, JPA의 1차 캐시와 MyBatis는 분리되어 있어 데이터 동기화 문제가 발생할 수 있습니다. 필요시 em.flush()를 호출하여 JPA의 변경사항을 DB에 먼저 반영해야 합니다."

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
