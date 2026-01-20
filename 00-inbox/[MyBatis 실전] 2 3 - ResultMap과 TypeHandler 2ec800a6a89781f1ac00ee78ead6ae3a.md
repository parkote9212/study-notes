# [MyBatis 실전] 2/3 - ResultMap과 TypeHandler

🏷️기술 카테고리: DataBase, Spring
💡핵심키워드: #쿼리최적화
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 18일 오후 10:28
📅 다음 복습일: 2026년 1월 25일

# 1. Abstract

> **ResultMap**은 MyBatis의 강력한 기능으로, **복잡한 조인**, **중첩 객체**, **커스텀 타입 변환**을 지원합니다.
> 

---

# 2. ResultMap

## 2.1 association (N:1)

```xml
<resultMap id="memberWithTeamMap" type="Member">
    <id property="id" column="member_id"/>
    <association property="team" javaType="Team">
        <id property="id" column="team_id"/>
        <result property="name" column="team_name"/>
    </association>
</resultMap>
```

---

## 2.2 collection (1:N)

```xml
<resultMap id="teamWithMembersMap" type="Team">
    <collection property="members" ofType="Member">
        <id property="id" column="member_id"/>
    </collection>
</resultMap>
```

---

## 🔑 핵심 체크리스트

- [ ]  ResultMap 복잡 매핑
- [ ]  association N:1
- [ ]  collection 1:N

---

**작성일**: 2026-01-18  

**면접 빈출도**: ⭐⭐⭐⭐ (상)