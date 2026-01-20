# [MyBatis 실전] 3/3 - JPA vs MyBatis 선택 가이드

🏷️기술 카테고리: DataBase, JPA, Spring
💡핵심키워드: #JPA, #아키텍처
💼 면접 빈출도: 최상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 18일 오후 10:28
📅 다음 복습일: 2026년 1월 21일

# 1. Abstract

> JPA와 MyBatis는 각각의 장단점이 명확합니다. **프로젝트 특성**에 따라 적절히 선택하거나 **혼용**하는 것이 최선입니다.
> 

---

# 2. JPA vs MyBatis 비교

| 구분 | JPA | MyBatis |
| --- | --- | --- |
| **패러다임** | ORM | SQL Mapper |
| **SQL 제어** | 제한적 | 완전 |
| **성능 튜닝** | 어려움 | 쉽음 |
| **학습** | 높음 | 낮음 |
| **CRUD** | 자동 | 수동 |

---

# 3. 선택 기준

## 3.1 JPA 추천

✅ CRUD 중심

✅ 빠른 개발

✅ 도메인 모델 명확

---

## 3.2 MyBatis 추천

✅ 복잡한 쿼리

✅ 성능 중요

✅ 레거시 DB

---

# 4. 혼용 전략

```java
@Service
public class UserService {
    private final UserRepository userRepository;  // JPA
    private final UserMapper userMapper;          // MyBatis
    
    // JPA: CRUD
    public void createUser(User user) {
        [userRepository.save](http://userRepository.save)(user);
    }
    
    // MyBatis: 복잡 조회
    public List<Report> getReport() {
        return userMapper.getReport();
    }
}
```

---

## 🔑 핵심 체크리스트

- [ ]  JPA = 객체지향 생산성
- [ ]  MyBatis = SQL제어 성능
- [ ]  상황에 맞게 선택
- [ ]  혼용 가능

---

**작성일**: 2026-01-18  

**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)