---
tags: study, mybatis, dynamic-sql
created: 2025-01-23
---

# MyBatis 동적 SQL

## 한 줄 요약
> MyBatis 동적 SQL은 if, choose, foreach 등의 태그를 사용하여 런타임에 SQL을 동적으로 생성하며, 복잡한 검색 조건과 대량 데이터 처리에 효과적이다.

## 상세 설명

### 동적 SQL이란?
- 실행 시점에 조건에 따라 SQL 쿼리를 동적으로 생성
- XML 기반 태그(`<if>`, `<choose>`, `<foreach>` 등)를 사용
- 코드 중복 제거 및 유연한 쿼리 작성 가능
- MyBatis의 핵심 기능 중 하나

### 주요 동적 SQL 태그

#### 1. `<if>` - 조건부 포함
```xml
<if test="조건식">
    SQL 구문
</if>
```

#### 2. `<choose>`, `<when>`, `<otherwise>` - 다중 조건 분기
```xml
<choose>
    <when test="조건1">SQL1</when>
    <when test="조건2">SQL2</when>
    <otherwise>기본SQL</otherwise>
</choose>
```

#### 3. `<foreach>` - 컬렉션 반복
```xml
<foreach collection="컬렉션" item="항목" open="(" separator="," close=")">
    #{항목}
</foreach>
```

#### 4. `<where>` - WHERE 절 자동 관리
```xml
<where>
    <if test="조건1">AND column1 = #{value1}</if>
    <if test="조건2">AND column2 = #{value2}</if>
</where>
```

## 코드 예시

### 1. 복잡한 검색 쿼리 (실무 예제)
```xml
<select id="dynamicSearch" resultType="DealSearchResponse">
    SELECT
        d.deal_id,
        d.deal_date,
        d.deal_amount,
        d.area,
        d.floor,
        d.price_per_m2,
        a.apt_name,
        a.build_year,
        r.sido,
        r.sigungu,
        c.latitude,
        c.longitude
    FROM real_estate_deal d USE INDEX (idx_deal_date, idx_region_date)
    INNER JOIN apartment a ON d.apartment_id = a.apartment_id
    INNER JOIN region r ON d.region_code = r.region_code
    LEFT JOIN coordinate c ON a.apartment_id = c.apartment_id
    <where>
        d.cancel_yn = 'N'

        <!-- 키워드 검색 (if 사용) -->
        <if test="keyword != null and keyword != ''">
            AND (
                a.apt_name LIKE CONCAT('%', #{keyword}, '%')
                OR r.sigungu LIKE CONCAT('%', #{keyword}, '%')
                OR r.dong LIKE CONCAT('%', #{keyword}, '%')
                OR a.road_address LIKE CONCAT('%', #{keyword}, '%')
            )
        </if>

        <!-- 지역 필터 -->
        <if test="regionCode != null">
            AND d.region_code = #{regionCode}
        </if>

        <if test="sido != null">
            AND r.sido = #{sido}
        </if>

        <if test="sigungu != null">
            AND r.sigungu = #{sigungu}
        </if>

        <!-- 가격 범위 (CDATA 사용) -->
        <if test="minPrice != null">
            <![CDATA[ AND d.deal_amount >= #{minPrice} ]]>
        </if>

        <if test="maxPrice != null">
            <![CDATA[ AND d.deal_amount <= #{maxPrice} ]]>
        </if>

        <!-- 면적 범위 (choose 사용) -->
        <choose>
            <when test="areaType != null and areaType == 'SMALL'">
                <![CDATA[ AND d.area < 60 ]]>
            </when>
            <when test="areaType != null and areaType == 'MEDIUM'">
                <![CDATA[ AND d.area >= 60 AND d.area < 85 ]]>
            </when>
            <when test="areaType != null and areaType == 'LARGE'">
                <![CDATA[ AND d.area >= 85 ]]>
            </when>
            <otherwise>
                <if test="minArea != null">
                    <![CDATA[ AND d.area >= #{minArea} ]]>
                </if>
                <if test="maxArea != null">
                    <![CDATA[ AND d.area <= #{maxArea} ]]>
                </if>
            </otherwise>
        </choose>

        <!-- 날짜 범위 -->
        <if test="startDate != null">
            <![CDATA[ AND d.deal_date >= #{startDate} ]]>
        </if>

        <if test="endDate != null">
            <![CDATA[ AND d.deal_date <= #{endDate} ]]>
        </if>

        <!-- 거래 년월 (빠른 검색용) -->
        <if test="dealYearMonth != null">
            AND d.deal_year = SUBSTRING(#{dealYearMonth}, 1, 4)
            AND d.deal_month = SUBSTRING(#{dealYearMonth}, 5, 2)
        </if>

        <!-- 좌표 범위 (지도 영역 검색) -->
        <if test="bounds != null">
            AND c.latitude BETWEEN #{bounds.minLat} AND #{bounds.maxLat}
            AND c.longitude BETWEEN #{bounds.minLng} AND #{bounds.maxLng}
        </if>
    </where>

    <!-- 동적 정렬 -->
    <choose>
        <when test="sortBy == 'dealDate'">
            ORDER BY d.deal_date ${sortOrder}
        </when>
        <when test="sortBy == 'dealAmount'">
            ORDER BY d.deal_amount ${sortOrder}
        </when>
        <when test="sortBy == 'pricePerM2'">
            ORDER BY d.price_per_m2 ${sortOrder}
        </when>
        <when test="sortBy == 'area'">
            ORDER BY d.area ${sortOrder}
        </when>
        <otherwise>
            ORDER BY d.deal_date DESC
        </otherwise>
    </choose>

    LIMIT #{offset}, #{size}
</select>
```

### 2. foreach를 활용한 IN 절 처리
```xml
<select id="getComparisonStats" resultType="ComparisonStatsResponse">
    SELECT
        d.region_code,
        CONCAT(r.sido, ' ', r.sigungu) as region_name,
        COUNT(*) as total_deals,
        AVG(d.deal_amount) as avg_price,
        MIN(d.deal_amount) as min_price,
        MAX(d.deal_amount) as max_price
    FROM real_estate_deal d
    INNER JOIN region r ON d.region_code = r.region_code
    WHERE d.cancel_yn = 'N'
      AND d.deal_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
      AND d.region_code IN
      <foreach collection="regionCodes" item="code" open="(" separator="," close=")">
          #{code}
      </foreach>
    GROUP BY d.region_code, r.sido, r.sigungu
</select>
```

**foreach 속성:**
- `collection`: 반복할 컬렉션 (List, Array, Map)
- `item`: 현재 항목을 참조할 변수명
- `open`: 시작 구분자
- `close`: 종료 구분자
- `separator`: 항목 간 구분자

### 3. 검색 카운트 쿼리 (동일한 조건 재사용)
```xml
<select id="dynamicSearchCount" resultType="long">
    SELECT COUNT(*)
    FROM real_estate_deal d
    INNER JOIN apartment a ON d.apartment_id = a.apartment_id
    INNER JOIN region r ON d.region_code = r.region_code
    <if test="bounds != null">
        LEFT JOIN coordinate c ON a.apartment_id = c.apartment_id
    </if>
    <where>
        d.cancel_yn = 'N'
        
        <!-- 위의 검색 쿼리와 동일한 WHERE 조건들 -->
        <if test="keyword != null and keyword != ''">
            AND (
                a.apt_name LIKE CONCAT('%', #{keyword}, '%')
                OR r.sigungu LIKE CONCAT('%', #{keyword}, '%')
            )
        </if>
        
        <!-- ... 나머지 조건들 ... -->
    </where>
</select>
```

### 4. 동적 UPDATE 문
```xml
<update id="updateSelective">
    UPDATE user
    <set>
        <if test="name != null">name = #{name},</if>
        <if test="email != null">email = #{email},</if>
        <if test="age != null">age = #{age},</if>
        updated_at = NOW()
    </set>
    WHERE id = #{id}
</update>
```

**`<set>` 태그:**
- 자동으로 `SET` 키워드 추가
- 마지막 쉼표(,) 자동 제거

### 5. CDATA 섹션 사용
```xml
<!-- < > 기호를 SQL에서 사용할 때 -->
<if test="minPrice != null">
    <![CDATA[
        AND deal_amount >= #{minPrice}
    ]]>
</if>

<!-- 또는 escape 사용 -->
<if test="minPrice != null">
    AND deal_amount &gt;= #{minPrice}
</if>
```

## 주의사항 / 함정

### 1. test 속성 조건식 작성
```xml
<!-- 올바른 예 -->
<if test="name != null and name != ''">
    AND name = #{name}
</if>

<!-- 잘못된 예: 문자열 비교 시 '' 누락 -->
<if test="name != null and name != ">  <!-- 오류 발생 -->
    AND name = #{name}
</if>

<!-- Boolean 타입 -->
<if test="isActive == true">  <!-- 또는 isActive -->
    AND active = 1
</if>
```

### 2. `<where>` 태그의 AND/OR 처리
```xml
<!-- <where> 태그는 첫 번째 AND/OR를 자동 제거 -->
<where>
    <if test="name != null">
        AND name = #{name}  <!-- 첫 번째 조건이면 AND 자동 제거 -->
    </if>
    <if test="age != null">
        AND age = #{age}
    </if>
</where>

<!-- 결과: WHERE name = ? AND age = ? -->
```

### 3. foreach 사용 시 null 체크
```xml
<!-- 컬렉션이 null이거나 비어있을 때 처리 -->
<if test="regionCodes != null and regionCodes.size() > 0">
    AND region_code IN
    <foreach collection="regionCodes" item="code" open="(" separator="," close=")">
        #{code}
    </foreach>
</if>
```

### 4. 동적 ORDER BY 주의 (SQL Injection 위험)
```xml
<!-- 위험: ${} 사용 시 SQL Injection 가능 -->
ORDER BY ${sortColumn} ${sortOrder}

<!-- 안전한 방법: choose로 제한 -->
<choose>
    <when test="sortBy == 'dealDate'">
        ORDER BY d.deal_date ${sortOrder}
    </when>
    <when test="sortBy == 'dealAmount'">
        ORDER BY d.deal_amount ${sortOrder}
    </when>
    <otherwise>
        ORDER BY d.deal_date DESC
    </otherwise>
</choose>
```

### 5. 인덱스 힌트 사용
```xml
<!-- MySQL 인덱스 힌트 -->
FROM real_estate_deal d USE INDEX (idx_deal_date, idx_region_date)

<!-- 조건에 따라 다른 인덱스 -->
<choose>
    <when test="useRegionIndex">
        FROM real_estate_deal d USE INDEX (idx_region)
    </when>
    <otherwise>
        FROM real_estate_deal d USE INDEX (idx_date)
    </otherwise>
</choose>
```

## 관련 개념
- [[MyBatis-CTE-WITH절]]
- [[MyBatis-성능최적화]]
- [[SQL-Injection-방어]]

## 면접 질문
1. MyBatis의 `#{}` 와 `${}` 의 차이점은?
2. `<where>` 태그의 역할과 장점은?
3. 동적 SQL에서 SQL Injection을 방어하는 방법은?
4. `<foreach>`를 사용할 때 주의할 점은?

## 참고 자료
- MyBatis Dynamic SQL Documentation
- MyBatis Best Practices