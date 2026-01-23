---
tags: study, mybatis, sql, cte
created: 2025-01-23
---

# MyBatis CTE (Common Table Expression) WITH절

## 한 줄 요약
> CTE(WITH절)는 복잡한 쿼리를 단계별로 분리하여 가독성과 유지보수성을 높이는 SQL 기법으로, MyBatis에서 통계 계산과 변동률 분석에 효과적으로 활용된다.

## 상세 설명

### CTE란?
- **Common Table Expression**: 임시 결과 집합을 정의하는 SQL 구문
- `WITH` 키워드로 시작하여 하나 이상의 임시 테이블을 정의
- 메인 쿼리에서 정의된 CTE를 참조하여 사용
- 복잡한 쿼리를 논리적 단계로 분리하여 가독성 향상

### CTE의 장점
1. **가독성**: 복잡한 서브쿼리를 명확한 이름의 단계로 분리
2. **재사용성**: 동일한 CTE를 쿼리 내에서 여러 번 참조 가능
3. **유지보수성**: 각 단계별 로직을 독립적으로 수정 가능
4. **디버깅**: 각 CTE 단계별로 결과를 확인하기 쉬움

### MyBatis에서의 활용 패턴

#### 1. 월별 통계 계산 - 3단계 CTE 구조
```xml
<insert id="calculateAndInsertMonthlyStats">
    INSERT INTO monthly_statistics (...)
    WITH monthly_aggregation AS (
        -- Step 1: 월별 기본 집계
        SELECT
            region_code,
            YEAR(deal_date) as stats_year,
            MONTH(deal_date) as stats_month,
            AVG(deal_amount) as avg_deal_amount,
            MAX(deal_amount) as max_deal_amount,
            MIN(deal_amount) as min_deal_amount,
            COUNT(*) as deal_count,
            AVG(price_per_m2) as avg_price_per_m2
        FROM real_estate_deal
        WHERE cancel_yn = 'N'
          AND YEAR(deal_date) = #{year}
          AND MONTH(deal_date) = #{month}
        GROUP BY region_code, YEAR(deal_date), MONTH(deal_date)
    ),
    previous_month_data AS (
        -- Step 2: 전월 데이터 조회
        SELECT
            region_code,
            avg_deal_amount as prev_month_avg
        FROM monthly_statistics
        WHERE stats_year = CASE WHEN #{month} = 1 THEN #{year} - 1 ELSE #{year} END
          AND stats_month = CASE WHEN #{month} = 1 THEN 12 ELSE #{month} - 1 END
    ),
    previous_year_data AS (
        -- Step 3: 전년 동월 데이터 조회
        SELECT
            region_code,
            avg_deal_amount as prev_year_avg
        FROM monthly_statistics
        WHERE stats_year = #{year} - 1
          AND stats_month = #{month}
    )
    -- Step 4: 변동률 계산 및 결과 반환
    SELECT
        ma.region_code,
        ma.stats_year,
        ma.stats_month,
        ma.avg_deal_amount,
        -- 전월 대비 변동률 (MoM: Month over Month)
        ROUND(
            CASE
                WHEN pm.prev_month_avg IS NOT NULL AND pm.prev_month_avg > 0
                THEN ((ma.avg_deal_amount - pm.prev_month_avg) / pm.prev_month_avg * 100)
                ELSE NULL
            END,
            2
        ) as mom_change_rate,
        -- 전년 동월 대비 변동률 (YoY: Year over Year)
        ROUND(
            CASE
                WHEN py.prev_year_avg IS NOT NULL AND py.prev_year_avg > 0
                THEN ((ma.avg_deal_amount - py.prev_year_avg) / py.prev_year_avg * 100)
                ELSE NULL
            END,
            2
        ) as yoy_change_rate
    FROM monthly_aggregation ma
    LEFT JOIN previous_month_data pm ON ma.region_code = pm.region_code
    LEFT JOIN previous_year_data py ON ma.region_code = py.region_code
</insert>
```

**쿼리 구조 해설:**
1. `monthly_aggregation`: 현재 월의 기본 통계 집계
2. `previous_month_data`: 비교 기준이 되는 전월 데이터
3. `previous_year_data`: 비교 기준이 되는 전년 동월 데이터
4. 메인 SELECT: 3개의 CTE를 JOIN하여 변동률 계산

#### 2. 지역별 순위 통계 - 2단계 CTE
```xml
<select id="getRegionRankingStats" resultType="RegionRankingResponse">
    WITH region_stats AS (
        -- Step 1: 지역별 기본 통계
        SELECT
            d.region_code,
            r.sido,
            r.sigungu,
            AVG(d.deal_amount) as avg_price,
            COUNT(*) as deal_count,
            AVG(d.price_per_m2) as avg_price_per_m2,
            STDDEV(d.deal_amount) as price_stddev
        FROM real_estate_deal d
        INNER JOIN region r ON d.region_code = r.region_code
        WHERE d.cancel_yn = 'N'
          AND d.deal_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
        GROUP BY d.region_code, r.sido, r.sigungu
    ),
    ranking AS (
        -- Step 2: Window Function으로 순위 계산
        SELECT
            *,
            RANK() OVER (ORDER BY avg_price DESC) as overall_rank,
            RANK() OVER (PARTITION BY sido ORDER BY avg_price DESC) as sido_rank,
            PERCENT_RANK() OVER (ORDER BY avg_price DESC) as price_percentile
        FROM region_stats
    )
    SELECT
        region_code,
        sido,
        sigungu,
        avg_price,
        overall_rank,
        sido_rank,
        ROUND(price_percentile * 100, 1) as pricePercentile
    FROM ranking
    ORDER BY overall_rank
</select>
```

## 코드 예시

### 변동률 계산 패턴
```sql
-- MoM(Month over Month) 변동률
ROUND(
    CASE
        WHEN prev_month_avg IS NOT NULL AND prev_month_avg > 0
        THEN ((current_avg - prev_month_avg) / prev_month_avg * 100)
        ELSE NULL
    END,
    2
) as mom_change_rate

-- YoY(Year over Year) 변동률
ROUND(
    CASE
        WHEN prev_year_avg IS NOT NULL AND prev_year_avg > 0
        THEN ((current_avg - prev_year_avg) / prev_year_avg * 100)
        ELSE NULL
    END,
    2
) as yoy_change_rate
```

### 전월/전년 계산 로직
```sql
-- 전월 계산 (1월인 경우 전년 12월)
WHERE stats_year = CASE WHEN #{month} = 1 THEN #{year} - 1 ELSE #{year} END
  AND stats_month = CASE WHEN #{month} = 1 THEN 12 ELSE #{month} - 1 END

-- 전년 동월
WHERE stats_year = #{year} - 1
  AND stats_month = #{month}
```

## 주의사항 / 함정

### 1. NULL 처리 필수
- 변동률 계산 시 분모가 0이거나 NULL인 경우 처리
- `CASE WHEN` 으로 NULL 체크 후 계산

### 2. LEFT JOIN vs INNER JOIN
- 전월/전년 데이터가 없을 수 있으므로 `LEFT JOIN` 사용
- INNER JOIN 사용 시 데이터가 누락될 수 있음

### 3. CTE 순서
- CTE는 정의 순서대로 참조 가능
- 나중에 정의된 CTE가 먼저 정의된 CTE를 참조 가능

### 4. ON DUPLICATE KEY UPDATE
- MySQL에서 INSERT와 UPDATE를 한번에 처리
- 통계 데이터 재계산 시 유용

## 관련 개념
- [[MyBatis-Window-Function]]
- [[MyBatis-동적SQL]]
- [[SQL-집계함수]]

## 면접 질문
1. CTE(WITH절)와 서브쿼리의 차이점은?
2. 월별 통계에서 전월 대비 변동률을 계산하는 방법은?
3. CTE를 사용하는 이유와 장점은?

## 참고 자료
- MySQL 8.0 CTE Documentation
- MyBatis Dynamic SQL