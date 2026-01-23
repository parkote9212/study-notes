# JPA-쿼리-QueryDSL

🏷️기술 카테고리: JPA, Spring
💡핵심키워드: #JPA, #쿼리최적화, #타입안전
💼 면접 빈출도: 최상

# 1. Abstract

**QueryDSL**은 JPQL을 타입 안전하게 작성할 수 있도록 도와주는 빌더 API로, **컴파일 시점 오류 감지**, **동적 쿼리**, **코드 재사용성**을 제공하여 실무에서 필수적인 도구입니다.

**핵심 원칙**:
- Q클래스: 컴파일 시 자동 생성
- 메서드 체이닝: 직관적인 쿼리 작성
- BooleanBuilder: 동적 쿼리

# 2. QueryDSL 설정

## 2.1 의존성 추가

```gradle
// build.gradle
dependencies {
    implementation 'com.querydsl:querydsl-jpa:5.0.0:jakarta'
    annotationProcessor 'com.querydsl:querydsl-apt:5.0.0:jakarta'
    annotationProcessor 'jakarta.persistence:jakarta.persistence-api'
}
```

## 2.2 기본 사용

```java
@Repository
@RequiredArgsConstructor
public class MemberRepositoryImpl {
    private final JPAQueryFactory queryFactory;
    
    public List<Member> findByName(String name) {
        return queryFactory
            .selectFrom(QMember.member)
            .where(QMember.member.name.eq(name))
            .fetch();
    }
}
```

# 3. 동적 쿼리

```java
public List<Member> searchMembers(MemberSearchCondition condition) {
    BooleanBuilder builder = new BooleanBuilder();
    
    if (condition.getName() != null) {
        builder.and(member.name.eq(condition.getName()));
    }
    if (condition.getAge() != null) {
        builder.and(member.age.goe(condition.getAge()));
    }
    
    return queryFactory
        .selectFrom(member)
        .where(builder)
        .fetch();
}
```

# 4. 페이징 & 정렬

```java
public Page<Member> findMembers(Pageable pageable) {
    List<Member> content = queryFactory
        .selectFrom(member)
        .offset(pageable.getOffset())
        .limit(pageable.getPageSize())
        .fetch();
    
    long total = queryFactory
        .selectFrom(member)
        .fetchCount();
    
    return new PageImpl<>(content, pageable, total);
}
```

# 5. Projection

```java
// DTO 직접 조회
public List<MemberDTO> findMemberDTOs() {
    return queryFactory
        .select(Projections.constructor(MemberDTO.class,
            member.id,
            member.name,
            member.age))
        .from(member)
        .fetch();
}
```

# 6. Interview Readiness

## Q1: QueryDSL vs JPQL?

**A**:
- QueryDSL: 타입 안전, 컴파일 오류 감지, 코드 자동완성
- JPQL: 문자열 기반, 런타임 오류

## Q2: QueryDSL vs Criteria?

**A**:
- QueryDSL: 가독성 우수, 학습 곡선 낮음
- Criteria: 가독성 떨어짐, 복잡함

## Q3: BooleanBuilder의 용도는?

**A**: 동적 쿼리 작성 시 조건을 동적으로 추가/조합하기 위해 사용합니다.

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
