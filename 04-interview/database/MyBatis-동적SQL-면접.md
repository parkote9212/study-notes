---
tags: interview, mybatis, dynamic-sql
created: 2025-01-23
difficulty: 중
---

# MyBatis 동적 SQL 면접

## 질문
> MyBatis의 동적 SQL 태그들(if, choose, foreach)의 역할과 실무에서의 활용 사례를 설명해주세요.

## 핵심 답변 (3줄)
1. MyBatis 동적 SQL은 런타임에 조건에 따라 SQL을 동적으로 생성하며, `<if>`는 단일 조건 분기, `<choose>`는 다중 조건 분기(switch-case), `<foreach>`는 컬렉션 반복 처리에 사용됩니다.
2. 복잡한 검색 조건 처리 시 `<where>` 태그로 WHERE 절을 자동 관리하고, `<if>` 태그로 각 검색 조건을 선택적으로 추가하여 코드 중복 없이 다양한 조건 조합을 처리합니다.
3. `#{}`는 PreparedStatement로 SQL Injection을 방어하지만, `${}`는 문자열 치환으로 보안에 취약하므로 정렬(ORDER BY)이나 테이블명 등 제한된 경우에만 사용합니다.

## 상세 설명

### 동적 SQL의 필요성

**문제 상황:**
```java
// 검색 조건이 많은 경우 모든 조합의 쿼리를 작성해야 함
String sql1 = "SELECT * FROM deals WHERE region = ?";
String sql2 = "SELECT * FROM deals WHERE region = ? AND price >= ?";
String sql3 = "SELECT * FROM deals WHERE region = ? AND price >= ? AND area >= ?";
// ... 수십 개의 조합
```

**해결책: 동적 SQL**
```xml
<select id="search">
    SELECT * FROM deals
    <where>
        <if test="region != null">AND region = #{region}</if>
        <if test="minPrice != null">AND price >= #{minPrice}</if>
        <if test="minArea != null">AND area >= #{minArea}</if>
    </where>
</select>
```

### 1. `<if>` 태그 - 조건부 포함

```xml
<select id="dynamicSearch">
    SELECT * FROM real_estate_deal d
    INNER JOIN apartment a ON d.apartment_id = a.apartment_id
    <where>
        d.cancel_yn = 'N'
        
        <!-- 키워드 검색 -->
        <if test="keyword != null and keyword != ''">
            AND (
                a.apt_name LIKE CONCAT('%', #{keyword}, '%')
                OR a.road_address LIKE CONCAT('%', #{keyword}, '%')
            )
        </if>
        
        <!-- 가격 범위 -->
        <if test="minPrice != null">
            <![CDATA[ AND d.deal_amount >= #{minPrice} ]]>
        </if>
        
        <if test="maxPrice != null">
            <![CDATA[ AND d.deal_amount <= #{maxPrice} ]]>
        </if>
        
        <!-- 날짜 범위 -->
        <if test="startDate != null">
            AND d.deal_date >= #{startDate}
        </if>
    </where>
</select>
```

**`<where>` 태그의 역할:**
- 자동으로 `WHERE` 키워드 추가
- 첫 번째 `AND`/`OR` 자동 제거
- 모든 조건이 false면 WHERE 절 자체를 제거

### 2. `<choose>`, `<when>`, `<otherwise>` - 다중 분기

```xml
<select id="searchByAreaType">
    SELECT * FROM deals
    WHERE cancel_yn = 'N'
    <choose>
        <!-- 소형: 60㎡ 미만 -->
        <when test="areaType == 'SMALL'">
            <![CDATA[ AND area < 60 ]]>
        </when>
        <!-- 중형: 60~85㎡ -->
        <when test="areaType == 'MEDIUM'">
            <![CDATA[ AND area >= 60 AND area < 85 ]]>
        </when>
        <!-- 대형: 85㎡ 이상 -->
        <when test="areaType == 'LARGE'">
            <![CDATA[ AND area >= 85 ]]>
        </when>
        <!-- 기본값: 직접 범위 지정 -->
        <otherwise>
            <if test="minArea != null">
                <![CDATA[ AND area >= #{minArea} ]]>
            </if>
            <if test="maxArea != null">
                <![CDATA[ AND area <= #{maxArea} ]]>
            </if>
        </otherwise>
    </choose>
</select>
```

**Java의 switch-case와 유사:**
```java
switch(areaType) {
    case "SMALL":  // <when>
        sql += "AND area < 60";
        break;
    case "MEDIUM":  // <when>
        sql += "AND area >= 60 AND area < 85";
        break;
    default:  // <otherwise>
        if(minArea != null) sql += "AND area >= " + minArea;
}
```

### 3. `<foreach>` - 컬렉션 반복 (IN 절)

```xml
<select id="getComparisonStats">
    SELECT
        region_code,
        COUNT(*) as deal_count,
        AVG(deal_amount) as avg_price
    FROM real_estate_deal
    WHERE cancel_yn = 'N'
      AND region_code IN
      <foreach collection="regionCodes" item="code" open="(" separator="," close=")">
          #{code}
      </foreach>
    GROUP BY region_code
</select>
```

**Java 호출:**
```java
List<String> regionCodes = Arrays.asList("11110", "11140", "11170");
mapper.getComparisonStats(regionCodes);
```

**생성되는 SQL:**
```sql
SELECT ... FROM ... 
WHERE region_code IN ('11110', '11140', '11170')
```

**foreach 속성:**
- `collection`: List, Array, Map의 key
- `item`: 현재 요소를 참조할 변수명
- `index`: 현재 인덱스 (선택)
- `open`: 시작 구분자
- `close`: 종료 구분자
- `separator`: 요소 간 구분자

### 4. 동적 정렬 (보안 주의)

```xml
<!-- 안전한 방법: choose로 제한 -->
<select id="searchWithSort">
    SELECT * FROM deals
    WHERE cancel_yn = 'N'
    <choose>
        <when test="sortBy == 'dealDate'">
            ORDER BY deal_date ${sortOrder}
        </when>
        <when test="sortBy == 'dealAmount'">
            ORDER BY deal_amount ${sortOrder}
        </when>
        <when test="sortBy == 'pricePerM2'">
            ORDER BY price_per_m2 ${sortOrder}
        </when>
        <otherwise>
            ORDER BY deal_date DESC
        </otherwise>
    </choose>
</select>
```

**위험한 방법 (SQL Injection):**
```xml
<!-- 절대 사용 금지 -->
ORDER BY ${sortColumn} ${sortOrder}
```

### #{} vs ${} 비교

| 구분 | #{} | ${} |
|------|-----|-----|
| 처리 방식 | PreparedStatement | 문자열 치환 |
| SQL Injection | 안전 | 위험 |
| 사용 예시 | 값 바인딩 | 테이블명, 컬럼명 |
| 쿼리 예시 | `WHERE id = ?` | `WHERE id = 123` |

```xml
<!-- 안전: #{} 사용 -->
<if test="keyword != null">
    AND apt_name LIKE CONCAT('%', #{keyword}, '%')
</if>
<!-- 생성 SQL: AND apt_name LIKE CONCAT('%', ?, '%') -->

<!-- 위험: ${} 사용 -->
<if test="keyword != null">
    AND apt_name LIKE '%${keyword}%'
</if>
<!-- 생성 SQL: AND apt_name LIKE '%강남%' -->
<!-- 만약 keyword = "'; DROP TABLE users; --" 이면? -->
```

## 코드 예시 (필요시)
```xml
<!-- 조건 조합 예시 -->
<select id="complexSearch" parameterType="SearchDto">
    SELECT * FROM deals
    <where>
        <if test="keyword != null and keyword != ''">
            AND apt_name LIKE CONCAT('%', #{keyword}, '%')
        </if>
        
        <choose>
            <when test="priceRange == 'LOW'">
                <![CDATA[ AND deal_amount < 50000 ]]>
            </when>
            <when test="priceRange == 'HIGH'">
                <![CDATA[ AND deal_amount >= 100000 ]]>
            </when>
        </choose>
        
        <if test="regionCodes != null and regionCodes.size() > 0">
            AND region_code IN
            <foreach collection="regionCodes" item="code" open="(" close=")" separator=",">
                #{code}
            </foreach>
        </if>
    </where>
</select>
```

## 꼬리 질문 예상
- `<where>` 태그가 첫 번째 AND를 제거하는 원리는?
- foreach에서 컬렉션이 비어있으면 어떻게 되나요?
- `<trim>` 태그의 역할과 `<where>`와의 차이는?
- `<set>` 태그는 언제 사용하나요?
- test 속성에서 사용할 수 있는 연산자는?

## 참고
- [[MyBatis-동적SQL]]
- [[SQL-Injection-방어]]
- [[MyBatis-성능최적화]]