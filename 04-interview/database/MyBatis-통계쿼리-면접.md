---
tags:
  - interview
  - mybatis
  - sql
  - aggregate
created: 2025-01-23
difficulty: 중
---

# MyBatis 통계 쿼리 및 집계 함수 면접

## 질문
> 집계 함수(AVG, COUNT, STDDEV)를 활용한 통계 쿼리 작성 시 주의사항과 실무 활용 사례를 설명해주세요.

## 핵심 답변 (3줄)
1. 집계 함수는 NULL 값을 자동으로 제외하며, COUNT(*)는 모든 행을, COUNT(column)은 NULL이 아닌 값만 계산하므로 목적에 맞게 선택해야 합니다.
2. STDDEV(표준편차)로 데이터 변동성을 측정하고, 변동계수(CV = 표준편차/평균*100)로 서로 다른 단위의 데이터 변동성을 비교할 수 있습니다.
3. WHERE 절은 그룹화 전 행을 필터링하고, HAVING 절은 그룹화 후 집계 결과를 필터링하므로, 성능을 위해 가능한 WHERE 절을 먼저 사용합니다.

## 상세 설명

### 집계 함수의 기본

**주요 집계 함수:**
```sql
COUNT(*)           -- 전체 행 수 (NULL 포함)
COUNT(column)      -- NULL이 아닌 값 개수
AVG(column)        -- 평균 (NULL 제외)
SUM(column)        -- 합계 (NULL 제외)
MAX(column)        -- 최대값
MIN(column)        -- 최소값
STDDEV(column)     -- 표준편차
VARIANCE(column)   -- 분산
```

### 실무 사례 1: 지역별 기본 통계

```xml
<select id="getRegionBasicStats" resultType="RegionStatsResponse">
    SELECT
        region_code,
        COUNT(*) as total_count,                    -- 거래 건수
        AVG(deal_amount) as avg_price,              -- 평균 가격
        MAX(deal_amount) as max_price,              -- 최고가
        MIN(deal_amount) as min_price,              -- 최저가
        STDDEV(deal_amount) as price_stddev,        -- 표준편차
        
        -- 가격 범위
        MAX(deal_amount) - MIN(deal_amount) as price_range,
        
        -- NULL 안전 평균
        AVG(COALESCE(deal_amount, 0)) as avg_with_zero
    FROM real_estate_deal
    WHERE cancel_yn = 'N'
      AND deal_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
    GROUP BY region_code
</select>
```

### 실무 사례 2: 변동계수(CV)를 활용한 안정성 평가

**변동계수(Coefficient of Variation):**
- CV = (표준편차 / 평균) × 100
- 단위가 다른 데이터의 변동성 비교 가능
- CV가 낮을수록 안정적

```xml
<select id="getVolatilityAnalysis" resultType="VolatilityResponse">
    SELECT
        region_code,
        COUNT(*) as deal_count,
        AVG(deal_amount) as avg_price,
        STDDEV(deal_amount) as price_stddev,
        
        -- 변동계수 계산
        ROUND((STDDEV(deal_amount) / AVG(deal_amount) * 100), 2) as cv,
        
        -- 변동성 등급
        CASE
            WHEN STDDEV(deal_amount) / AVG(deal_amount) * 100 <= 10 THEN '안정적'
            WHEN STDDEV(deal_amount) / AVG(deal_amount) * 100 <= 20 THEN '보통'
            ELSE '변동성 큼'
        END as volatility_grade,
        
        -- 가격 변동폭
        ROUND(((MAX(deal_amount) - MIN(deal_amount)) / AVG(deal_amount) * 100), 2) 
            as price_volatility_pct
    FROM real_estate_deal
    WHERE cancel_yn = 'N'
      AND deal_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
    GROUP BY region_code
    HAVING COUNT(*) >= 10  -- 최소 거래 건수
</select>
```

**활용 예시:**
- CV = 5%: 매우 안정적 (강남구 고가 아파트)
- CV = 15%: 보통 (일반 주거지역)
- CV = 30%: 변동성 큼 (재개발 지역)

### 실무 사례 3: 조건부 집계

```xml
<select id="getConditionalStats" resultType="ConditionalStatsResponse">
    SELECT
        region_code,
        
        -- 전체 통계
        COUNT(*) as total_count,
        AVG(deal_amount) as avg_price,
        
        -- 조건별 개수
        COUNT(CASE WHEN deal_amount >= 100000 THEN 1 END) as high_price_count,
        COUNT(CASE WHEN deal_amount < 50000 THEN 1 END) as low_price_count,
        
        -- 조건별 평균
        AVG(CASE WHEN area < 60 THEN deal_amount END) as avg_small_area,
        AVG(CASE WHEN area >= 60 AND area < 85 THEN deal_amount END) as avg_medium_area,
        AVG(CASE WHEN area >= 85 THEN deal_amount END) as avg_large_area,
        
        -- 조건별 비율
        ROUND(
            COUNT(CASE WHEN deal_amount >= 100000 THEN 1 END) * 100.0 / COUNT(*),
            2
        ) as high_price_ratio,
        
        -- 올해/작년 비교
        SUM(CASE WHEN YEAR(deal_date) = YEAR(NOW()) THEN deal_amount ELSE 0 END) 
            as this_year_total,
        SUM(CASE WHEN YEAR(deal_date) = YEAR(NOW()) - 1 THEN deal_amount ELSE 0 END) 
            as last_year_total
    FROM real_estate_deal
    WHERE cancel_yn = 'N'
    GROUP BY region_code
</select>
```

### WHERE vs HAVING 비교

```xml
<select id="getActiveRegions">
    SELECT
        region_code,
        COUNT(*) as deal_count,
        AVG(deal_amount) as avg_price
    FROM real_estate_deal
    WHERE cancel_yn = 'N'                    -- ① 그룹화 전 필터링
      AND deal_date >= '2024-01-01'          -- ① 성능 향상
    GROUP BY region_code
    HAVING COUNT(*) >= 10                    -- ② 그룹화 후 필터링
       AND AVG(deal_amount) >= 50000         -- ② 집계 결과 조건
</select>
```

**실행 순서:**
1. `WHERE`: 개별 행 필터링 (인덱스 활용 가능)
2. `GROUP BY`: 그룹화
3. `집계 함수`: 계산
4. `HAVING`: 그룹 필터링

**성능 차이:**
```sql
-- 비효율: 모든 데이터 그룹화 후 필터링
SELECT region_code, COUNT(*)
FROM deals
GROUP BY region_code
HAVING MAX(deal_date) >= '2024-01-01'

-- 효율: 먼저 필터링 후 그룹화
SELECT region_code, COUNT(*)
FROM deals
WHERE deal_date >= '2024-01-01'
GROUP BY region_code
```

### COUNT(*) vs COUNT(column)

```sql
SELECT
    COUNT(*) as total_rows,           -- 10 (모든 행)
    COUNT(price) as price_count,      -- 8 (NULL이 아닌 값)
    COUNT(DISTINCT region) as regions -- 5 (중복 제거)
FROM deals;
```

**예시 데이터:**
```
id | region | price
1  | 강남   | 100000
2  | 강남   | NULL      -- COUNT(price)에서 제외
3  | 서초   | 95000
4  | 서초   | NULL      -- COUNT(price)에서 제외
```

### NULL 안전 처리

```sql
-- 문제: NULL이 있으면 결과도 NULL
SELECT AVG(price) FROM deals;  -- NULL이 하나라도 있으면?

-- 해결 1: COALESCE로 NULL을 0으로 치환
SELECT AVG(COALESCE(price, 0)) FROM deals;

-- 해결 2: WHERE로 NULL 제외
SELECT AVG(price) FROM deals WHERE price IS NOT NULL;

-- 0으로 나누기 방지
SELECT 
    numerator / NULLIF(denominator, 0)  -- denominator가 0이면 NULL 반환
FROM stats;
```

## 코드 예시 (필요시)
```sql
-- 백분위수 계산
WITH percentile_data AS (
    SELECT
        deal_amount,
        PERCENT_RANK() OVER (ORDER BY deal_amount) as pct
    FROM deals
)
SELECT
    MIN(CASE WHEN pct >= 0.25 THEN deal_amount END) as q1,  -- 25백분위
    MIN(CASE WHEN pct >= 0.50 THEN deal_amount END) as q2,  -- 중앙값
    MIN(CASE WHEN pct >= 0.75 THEN deal_amount END) as q3   -- 75백분위
FROM percentile_data;

-- 평균 대비 비율
SELECT
    region_code,
    avg_price,
    ROUND((avg_price / (SELECT AVG(avg_price) FROM region_stats)) * 100, 2)
        as vs_national_avg
FROM region_stats;
```

## 꼬리 질문 예상
- STDDEV_POP과 STDDEV_SAMP의 차이점은?
- GROUP BY 없이 집계 함수만 사용하면 어떻게 되나요?
- NULL 값이 많은 컬럼의 평균을 구할 때 주의할 점은?
- HAVING 절에서 집계 함수를 사용하지 않아도 되나요?
- 변동계수(CV)가 음수가 나올 수 있나요?

## 참고
- [[MyBatis-통계쿼리-집계함수]]
- [[MyBatis-Window-Function]]
- [[SQL-성능최적화]]