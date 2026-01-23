# JPA-연관관계-매핑가이드

🏷️기술 카테고리: JPA, Spring
💡핵심키워드: #JPA, #도메인주도설계
💼 면접 빈출도: 최상

# 1. Abstract

**연관관계 매핑**은 객체 간의 관계를 DB 테이블의 외래 키로 매핑하는 JPA의 핵심 기능입니다.

**핵심 원칙**:
- 연관관계 주인: 외래 키를 관리하는 엔티티
- mappedBy: 연관관계 주인이 아닌 쪽에 설정
- 양방향: 양쪽에서 모두 참조 가능

# 2. 단방향 vs 양방향

## 2.1 단방향 연관관계

```java
@Entity
public class Member {
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "team_id")
    private Team team;  // Member만 Team 참조
}

@Entity
public class Team {
    private String name;
    // Team은 Member 참조 X
}
```

## 2.2 양방향 연관관계

```java
@Entity
public class Member {
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "team_id")  // 연관관계 주인
    private Team team;
}

@Entity
public class Team {
    @OneToMany(mappedBy = "team")  // 주인 지정
    private List<Member> members = new ArrayList<>();
}
```

# 3. 다중성

## 3.1 N:1 (다대일) - 권장

```java
@Entity
public class Member {
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "team_id")
    private Team team;
}
```

## 3.2 1:1 (일대일)

```java
@Entity
public class Member {
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "locker_id")
    private Locker locker;
}
```

## 3.3 N:M (다대다) - 중간 테이블 필수

```java
// ❌ @ManyToMany 비권장
// ✅ 중간 엔티티 생성 (권장)
@Entity
public class Order {
    @ManyToOne
    @JoinColumn(name = "member_id")
    private Member member;
    
    @ManyToOne
    @JoinColumn(name = "product_id")
    private Product product;
}
```

# 4. 연관관계 주인

**외래 키 관리**:

```java
@Entity
public class Member {
    @ManyToOne
    @JoinColumn(name = "team_id")  // ✅ 주인
    private Team team;
    
    public void changeTeam(Team team) {
        this.team = team;
        team.getMembers().add(this);  // 양방향 동기화
    }
}

@Entity
public class Team {
    @OneToMany(mappedBy = "team")  // ❌ 주인 X
    private List<Member> members = new ArrayList<>();
}
```

# 5. Cascade & orphanRemoval

```java
@Entity
public class Parent {
    @OneToMany(mappedBy = "parent", 
               cascade = CascadeType.ALL,
               orphanRemoval = true)
    private List<Child> children = new ArrayList<>();
}

// Parent 저장 시 Child 자동 저장
// 관계 제거 시 Child 자동 삭제
```

# 6. Interview Readiness

## Q1: 연관관계 주인이란?

**A**: 외래 키를 관리하는 엔티티입니다. 양방향 연관관계에서는 한쪽을 주인으로 지정해야 하며, 외래 키가 있는 쪽을 주인으로 선택합니다.

## Q2: N:1과 1:N 차이는?

**A**:
- N:1: 다(자식)가 일(부모) 참조, 외래 키가 N쪽에
- 1:N: 일(부모)이 다(자식) 참조, 외래 키가 N쪽에
- 권장: N:1 양방향 사용

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
