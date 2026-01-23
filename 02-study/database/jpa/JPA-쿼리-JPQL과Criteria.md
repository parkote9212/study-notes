# JPA-쿼리-JPQL과Criteria

🏷️기술 카테고리: JPA, Spring
💡핵심키워드: #JPA, #쿼리최적화
💼 면접 빈출도: 상

# 1. Abstract

**JPQL**(Java Persistence Query Language)은 엔티티 객체를 대상으로 쿼리하는 객체 지향 쿼리 언어입니다. SQL과 비슷하지만 테이블이 아닌 **엔티티**를 대상으로 하며, 데이터베이스에 독립적입니다.

**핵심 원칙**:
- JPQL: 엔티티 기반 쿼리
- Criteria API: 타입 안전한 동적 쿼리
- Native Query: 직접 SQL 사용

# 2. JPQL 기초

## 2.1 기본 문법

```java
// SELECT
String jpql = "SELECT m FROM Member m WHERE m.age > 18";
List<Member> members = em.createQuery(jpql, Member.class)
    .getResultList();

// 파라미터 바인딩
String jpql = "SELECT m FROM Member m WHERE m.name = :name";
Member member = em.createQuery(jpql, Member.class)
    .setParameter("name", "John")
    .getSingleResult();

// 페이징
List<Member> members = em.createQuery(jpql, Member.class)
    .setFirstResult(0)
    .setMaxResults(10)
    .getResultList();
```

## 2.2 조인 쿼리

```java
// 내부 조인
String jpql = "SELECT m FROM Member m INNER JOIN m.team t WHERE t.name = :teamName";

// 외부 조인
String jpql = "SELECT m FROM Member m LEFT JOIN m.team t";

// 페치 조인 (N+1 해결)
String jpql = "SELECT m FROM Member m JOIN FETCH m.team";
```

# 3. Criteria API

## 3.1 기본 사용

```java
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<Member> cq = cb.createQuery(Member.class);

Root<Member> m = cq.from(Member.class);
cq.select(m)
  .where(cb.equal(m.get("name"), "John"));

List<Member> members = em.createQuery(cq).getResultList();
```

## 3.2 동적 쿼리

```java
public List<Member> searchMembers(String name, Integer age) {
    CriteriaBuilder cb = em.getCriteriaBuilder();
    CriteriaQuery<Member> cq = cb.createQuery(Member.class);
    Root<Member> m = cq.from(Member.class);
    
    List<Predicate> predicates = new ArrayList<>();
    
    if (name != null) {
        predicates.add(cb.equal(m.get("name"), name));
    }
    if (age != null) {
        predicates.add(cb.greaterThan(m.get("age"), age));
    }
    
    cq.where(predicates.toArray(new Predicate[0]));
    return em.createQuery(cq).getResultList();
}
```

# 4. Native Query

```java
// 기본 Native Query
String sql = "SELECT * FROM member WHERE name = ?";
List<Member> members = em.createNativeQuery(sql, Member.class)
    .setParameter(1, "John")
    .getResultList();
```

# 5. Interview Readiness

## Q1: JPQL vs SQL 차이는?

**A**:
- JPQL: 엔티티 객체를 대상, DB 독립적
- SQL: 테이블을 대상, DB 종속적

## Q2: Criteria API의 장점은?

**A**:
1. 타입 안전성
2. 동적 쿼리 작성 용이
3. 컴파일 시점 오류 감지

하지만 복잡하고 가독성이 떨어져 실무에선 QueryDSL 선호

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐ (상)
