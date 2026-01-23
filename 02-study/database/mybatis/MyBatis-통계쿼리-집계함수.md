---
tags: study, mybatis, sql, aggregate-function
created: 2025-01-23
---

# MyBatis 통계 쿼리 및 집계 함수

## 한 줄 요약
> MyBatis에서 AVG, SUM, COUNT, STDDEV 등 집계 함수와 통계 지표를 활용하여 데이터 분석 및 비즈니스 인사이트를 도출한다.

## 상세 설명

### 집계 함수란?
- 여러 행의 데이터를 하나의 결과값으로 계산하는 함수
- `GROUP BY`와 함께 사용하여 그룹별 통계 산출
- 주요 함수: `AVG`, `SUM`, `COUNT`, `MAX`, `MIN`, `STDDEV`

### 통계 쿼리의 활용
1. **기본 통계**: 평균, 합계, 최대/최소값
2. **변동성 분석**: 표준편차, 변동계수
3. **비교 분석**: 전월 대비, 전년 대비, 평균 대비
4. **순위 분석**: 상위/하위 N개 추출

## 코드 예시

### 1. 기본 집계 함수
```xml
<select id="getBasicStats" resultType="BasicStatsResponse">
    SELECT
        region_code,
        COUNT(*) as total_count,                    -- 거래 건수
        AVG(deal_amount) as avg_amount,             -- 평균 거래가
        SUM(deal_amount) as total_amount,           -- 총 거래액
        MAX(deal_amount) as max_amount,             -- 최고가
        MIN(deal_amount) as min_amount,             -- 최저가
        STDDEV(deal_amount) as stddev_amount,       -- 표준편차
        VARIANCE(deal_amount) as variance_amount    -- 분산
    FROM real_estate_deal
    WHERE cancel_yn = 'N'
      AND deal_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
    GROUP BY region_code
</select>
```

### 2. 통계 지표 계산 (변동계수, 가격 변동성)
```xml
<select id="getComparisonStats" resultType="ComparisonStatsResponse">
    WITH region_stats AS (
        SELECT
            d.region_code,
            CONCAT(r.sido, ' ', r.sigungu) as region_name,
            COUNT(*) as total_deals,
            AVG(d.deal_amount) as avg_price,
            MIN(d.deal_amount) as min_price,
            MAX(d.deal_amount) as max_price,
            AVG(d.price_per_m2) as avg_price_per_m2,
            STDDEV(d.deal_amount) as price_stddev
        FROM real_estate_deal d
        INNER JOIN region r ON d.region_code = r.region_code
        WHERE d.cancel_yn = 'N'
          AND d.deal_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
        GROUP BY d.region_code, r.sido, r.sigungu
    ),
    comparison_metrics AS (
        SELECT
            region_code,
            region_name,
            total_deals,
            avg_price,
            min_price,
            max_price,
            avg_price_per_m2,
            price_stddev,
            -- 전체 평균 대비 비율
            ROUND((avg_price / (SELECT AVG(avg_price) FROM region_stats) * 100), 2)
                as price_vs_average,
            -- 가격 변동성 (범위/평균 * 100)
            ROUND(((max_price - min_price) / avg_price * 100), 2)
                as price_volatility,
            -- 순위
            RANK() OVER (ORDER BY avg_price DESC) as price_rank,
            RANK() OVER (ORDER BY total_deals DESC) as volume_rank,
            -- 변동계수 (CV: Coefficient of Variation)
            -- CV = (표준편차 / 평균) * 100
            ROUND((price_stddev / avg_price * 100), 2) as cv
        FROM region_stats
    )
    SELECT
        region_code as regionCode,
        region_name as regionName,
        total_deals as totalDeals,
        avg_price as avgPrice,
        min_price as minPrice,
        max_price as maxPrice,
        avg_price_per_m2 as avgPricePerM2,
        price_stddev as priceStddev,
        price_vs_average as priceVsAverage,
        price_volatility as priceVolatility,
        price_rank as priceRank,
        volume_rank as volumeRank,
        cv as coefficientOfVariation,
        -- CV 값에 따른 등급 분류
        CASE
            WHEN cv <= 10 THEN '안정적'
            WHEN cv <= 20 THEN '보통'
            ELSE '변동성큼'
        END as volatilityGrade
    FROM comparison_metrics
    ORDER BY price_rank
</select>
```

**주요 통계 지표:**
- **변동계수(CV)**: `(표준편차 / 평균) * 100` - 데이터의 상대적 변동성
- **가격 변동성**: `(최대값 - 최소값) / 평균 * 100` - 가격 범위
- **평균 대비 비율**: `(개별값 / 전체평균) * 100` - 상대적 위치

### 3. 조건부 집계 (CASE WHEN 활용)
```xml
<select id="getConditionalStats" resultType="ConditionalStatsResponse">
    SELECT
        region_code,
        -- 조건별 개수
        COUNT(*) as total_count,
        COUNT(CASE WHEN deal_amount >= 100000 THEN 1 END) as high_price_count,
        COUNT(CASE WHEN deal_amount < 50000 THEN 1 END) as low_price_count,
        
        -- 조건별 평균
        AVG(CASE WHEN area < 60 THEN deal_amount END) as avg_small_area,
        AVG(CASE WHEN area >= 60 AND area < 85 THEN deal_amount END) as avg_medium_area,
        AVG(CASE WHEN area >= 85 THEN deal_amount END) as avg_large_area,
        
        -- 조건별 합계
        SUM(CASE WHEN YEAR(deal_date) = YEAR(NOW()) THEN deal_amount ELSE 0 END) as this_year_total,
        SUM(CASE WHEN YEAR(deal_date) = YEAR(NOW()) - 1 THEN deal_amount ELSE 0 END) as last_year_total,
        
        -- 비율 계산
        ROUND(
            COUNT(CASE WHEN deal_amount >= 100000 THEN 1 END) * 100.0 / COUNT(*),
            2
        ) as high_price_ratio
    FROM real_estate_deal
    WHERE cancel_yn = 'N'
    GROUP BY region_code
</select>
```

### 4. HAVING 절을 활용한 그룹 필터링
```xml
<select id="getActiveRegions" resultType="ActiveRegionResponse">
    SELECT
        region_code,
        COUNT(*) as deal_count,
        AVG(deal_amount) as avg_price,
        STDDEV(deal_amount) as price_stddev
    FROM real_estate_deal
    WHERE cancel_yn = 'N'
      AND deal_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
    GROUP BY region_code
    HAVING COUNT(*) >= 10                    -- 최소 거래 건수
       AND STDDEV(deal_amount) IS NOT NULL   -- 표준편차 존재
       AND AVG(deal_amount) >= 50000         -- 최소 평균 가격
    ORDER BY deal_count DESC
</select>
```

**HAVING vs WHERE:**
- `WHERE`: 그룹화 전 행 필터링
- `HAVING`: 그룹화 후 그룹 필터링

### 5. 서브쿼리를 활용한 백분위 계산
```xml
<select id="getPercentileStats" resultType="PercentileStatsResponse">
    WITH ranked_data AS (
        SELECT
            deal_amount,
            PERCENT_RANK() OVER (ORDER BY deal_amount) as percentile
        FROM real_estate_deal
        WHERE cancel_yn = 'N'
          AND region_code = #{regionCode}
          AND deal_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
    )
    SELECT
        MIN(CASE WHEN percentile >= 0.25 THEN deal_amount END) as p25,  -- 1사분위수
        MIN(CASE WHEN percentile >= 0.50 THEN deal_amount END) as p50,  -- 중앙값
        MIN(CASE WHEN percentile >= 0.75 THEN deal_amount END) as p75,  -- 3사분위수
        MIN(CASE WHEN percentile >= 0.90 THEN deal_amount END) as p90,  -- 90 백분위수
        MIN(CASE WHEN percentile >= 0.95 THEN deal_amount END) as p95   -- 95 백분위수
    FROM ranked_data
</select>
```

### 6. 그룹별 최상위 N개 추출
```xml
<select id="getTopNByRegion" resultType="TopDealResponse">
    WITH ranked_deals AS (
        SELECT
            d.*,
            a.apt_name,
            ROW_NUMBER() OVER (
                PARTITION BY d.region_code 
                ORDER BY d.deal_amount DESC
            ) as rank_in_region
        FROM real_estate_deal d
        INNER JOIN apartment a ON d.apartment_id = a.apartment_id
        WHERE d.cancel_yn = 'N'
          AND d.deal_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
    )
    SELECT
        region_code,
        apt_name,
        deal_amount,
        deal_date,
        rank_in_region
    FROM ranked_deals
    WHERE rank_in_region <= 5  -- 각 지역별 상위 5개
    ORDER BY region_code, rank_in_region
</select>
```

### 7. 월별 누적 통계
```xml
<select id="getMonthlyCumulativeStats" resultType="MonthlyStatsResponse">
    SELECT
        DATE_FORMAT(deal_date, '%Y-%m') as month,
        COUNT(*) as monthly_count,
        AVG(deal_amount) as monthly_avg,
        -- 누적 개수
        SUM(COUNT(*)) OVER (
            ORDER BY DATE_FORMAT(deal_date, '%Y-%m')
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as cumulative_count,
        -- 누적 평균
        AVG(AVG(deal_amount)) OVER (
            ORDER BY DATE_FORMAT(deal_date, '%Y-%m')
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as cumulative_avg
    FROM real_estate_deal
    WHERE cancel_yn = 'N'
      AND region_code = #{regionCode}
      AND deal_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
    GROUP BY DATE_FORMAT(deal_date, '%Y-%m')
    ORDER BY month
</select>
```

## 주의사항 / 함정

### 1. NULL 값 처리
```sql
-- AVG는 NULL을 자동으로 제외
AVG(price)  -- NULL 값은 계산에서 제외됨

-- COUNT(*)와 COUNT(column)의 차이
COUNT(*)        -- 모든 행 개수 (NULL 포함)
COUNT(column)   -- NULL이 아닌 값의 개수

-- COALESCE로 NULL 대체
AVG(COALESCE(price, 0))  -- NULL을 0으로 치환 후 평균
```

### 2. 표준편차와 분산
```sql
-- 모집단 표준편차 vs 표본 표준편차
STDDEV_POP(price)   -- 모집단 표준편차 (N으로 나눔)
STDDEV_SAMP(price)  -- 표본 표준편차 (N-1로 나눔)
STDDEV(price)       -- 보통 STDDEV_SAMP와 동일

-- MySQL에서는 STDDEV = STDDEV_SAMP
```

### 3. GROUP BY와 SELECT 절
```sql
-- 올바른 예: GROUP BY에 포함되거나 집계 함수 사용
SELECT region_code, COUNT(*), AVG(price)
FROM deals
GROUP BY region_code

-- 잘못된 예: GROUP BY에 없는 컬럼을 그냥 SELECT
SELECT region_code, apt_name, COUNT(*)  -- apt_name이 문제
FROM deals
GROUP BY region_code
```

### 4. HAVING 절의 성능
```sql
-- 비효율적: 모든 데이터 그룹화 후 필터링
SELECT region_code, COUNT(*)
FROM deals
GROUP BY region_code
HAVING COUNT(*) > 100

-- 효율적: WHERE로 먼저 필터링 (가능한 경우)
SELECT region_code, COUNT(*)
FROM deals
WHERE deal_date >= '2024-01-01'  -- 먼저 필터링
GROUP BY region_code
HAVING COUNT(*) > 100
```

### 5. 0으로 나누기 방지
```sql
-- 안전한 나눗셈
CASE 
    WHEN denominator = 0 THEN NULL
    ELSE numerator / denominator 
END

-- 또는 NULLIF 사용
numerator / NULLIF(denominator, 0)
```

## 관련 개념
- [[MyBatis-Window-Function]]
- [[MyBatis-CTE-WITH절]]
- [[SQL-성능최적화]]

## 면접 질문
1. COUNT(*)와 COUNT(column)의 차이점은?
2. 표준편차(STDDEV)와 변동계수(CV)의 차이와 활용 방법은?
3. WHERE 절과 HAVING 절의 차이점과 사용 시기는?
4. GROUP BY 절 없이 집계 함수를 사용하면 어떻게 되나?

## 참고 자료
- MySQL Aggregate Functions
- SQL Statistical Functions