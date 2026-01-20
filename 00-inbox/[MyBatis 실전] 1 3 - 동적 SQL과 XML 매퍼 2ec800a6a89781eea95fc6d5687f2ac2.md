# [MyBatis 실전] 1/3 - 동적 SQL과 XML 매퍼

🏷️기술 카테고리: DataBase, Spring
💡핵심키워드: #성능최적화, #쿼리최적화
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 18일 오후 10:28
📅 다음 복습일: 2026년 1월 25일

# 1. Abstract

> **MyBatis**는 SQL 매퍼 프레임워크로, **동적 SQL**, **복잡한 조인**, **프로시저** 등을 자유롭게 다룰 수 있습니다. JPA보다 SQL을 직접 작성하여 **성능 튜닝**이 필요한 경우에 적합합니다.
> 

**핵심 원칙**:

- XML 매퍼: SQL과 자바 분리
- 동적 SQL: if, choose, foreach
- @Mapper: 인터페이스만으로 구현

---

# 2. MyBatis 설정

## 2.1 의존성

```
dependencies {
    implementation 'org.mybatis.spring.boot:mybatis-spring-boot-starter:3.0.3'
    runtimeOnly 'com.mysql:mysql-connector-j'
}
```

---

## 2.2 application.yml

```yaml
mybatis:
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: com.example.domain
  configuration:
    map-underscore-to-camel-case: true
    default-fetch-size: 100
```

---

# 3. 동적 SQL

## 3.1 if 문

```xml
<select id="findMembers" resultType="Member">
    SELECT * FROM member
    WHERE 1=1
    <if test="name != null">
        AND name = #{name}
    </if>
    <if test="age != null">
        AND age >= #{age}
    </if>
</select>
```

---

## 3.2 foreach

```xml
<select id="findByIds" resultType="Member">
    SELECT * FROM member
    WHERE id IN
    <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</select>
```

---

# 4. Interview Readiness

## ▶ Q1: MyBatis의 장점은?

**A**:

1. SQL 제어
2. 성능 튜닝
3. 학습 용이
4. 동적 SQL

---

## 🔑 핵심 체크리스트

- [ ]  XML에 SQL 작성
- [ ]  @Mapper 매핑
- [ ]  if, foreach 동적 SQL
- [ ]  #{}로 파라미터

---

**작성일**: 2026-01-18  

**면접 빈출도**: ⭐⭐⭐⭐ (상)