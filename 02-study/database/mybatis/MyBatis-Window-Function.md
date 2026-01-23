---
tags: study, mybatis, sql, window-function
created: 2025-01-23
---

# MyBatis Window Function (윈도우 함수)

## 한 줄 요약
> Window Function은 행 간 관계를 계산하는 SQL 함수로, RANK, LAG, LEAD, 이동평균 등을 통해 순위와 추세 분석을 효과적으로 수행한다.

## 상세 설명

### Window Function이란?
- 집계 함수처럼 여러 행을 대상으로 계산하지만, 결과 행 수를 줄이지 않음
- `OVER()` 절을 사용하여 계산 범위(Window)를 지정
- `PARTITION BY`: 그룹 분할
- `ORDER BY`: 정렬 기준
- `ROWS/RANGE`: 범위 지정

### 주요 Window Function 종류

#### 1. 순위 함수
- `RANK()`: 동점 시 다음 순위 건너뜀 (1, 2, 2, 4)
- `DENSE_RANK()`: 동점 시 다음 순위 연속 (1, 2, 2, 3)
- `ROW_NUMBER()`: 고유한 순번 부여 (1, 2, 3, 4)
- `PERCENT_RANK()`: 백분위 순위 (0~1)

#### 2. 값 참조 함수
- `LAG()`: 이전 행 값 참조
- `LEAD()`: 다음 행 값 참조
- `FIRST_VALUE()`: 윈도우의 첫 번째 값
- `LAST_VALUE()`: 윈도우의 마지막 값

#### 3. 집계 함수
- `SUM() OVER()`: 누적 합계
- `AVG() OVER()`: 이동 평균
- `COUNT() OVER()`: 누적 개수

## 코드 예시

### 1. 지역별 순위 계산
```xml
<select id="getRegionRankingStats" resultType="RegionRankingResponse">
    WITH region_stats AS (
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
        SELECT
            *,
            -- 전체 순위
            RANK() OVER (ORDER BY avg_price DESC) as overall_rank,
            -- 시도별 순위 (PARTITION BY 사용)
            RANK() OVER (PARTITION BY sido ORDER BY avg_price DESC) as sido_rank,
            -- 거래량 순위
            RANK() OVER (ORDER BY deal_count DESC) as volume_rank,
            -- 백분위수 (상위 몇 %인지)
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
        volume_rank,
        ROUND(price_percentile * 100, 1) as pricePercentile,
        -- 가격 등급 분류
        CASE
            WHEN price_percentile <= 0.33 THEN 'HIGH'
            WHEN price_percentile <= 0.66 THEN 'MEDIUM'
            ELSE 'LOW'
        END as priceGrade
    FROM ranking
    ORDER BY overall_rank
</select>
```

**해설:**
- `RANK() OVER (ORDER BY avg_price DESC)`: 전체 지역 중 가격 순위
- `RANK() OVER (PARTITION BY sido ORDER BY avg_price DESC)`: 시도 내 순위
- `PERCENT_RANK()`: 0~1 사이 값으로 상위 몇 %인지 계산

### 2. 이동평균 및 추세 분석 (LAG/LEAD)
```xml
<insert id="calculateAndInsertPriceTrend">
    INSERT INTO price_trend (
        apartment_id,
        trend_month,
        avg_price_per_m2,
        deal_count,
        change_rate,
        trend_status
    )
    WITH monthly_apt_stats AS (
        -- Step 1: 아파트별 월별 평균
        SELECT
            apartment_id,
            DATE_FORMAT(deal_date, '%Y-%m-01') as trend_month,
            AVG(price_per_m2) as avg_price_per_m2,
            COUNT(*) as deal_count
        FROM real_estate_deal
        WHERE cancel_yn = 'N'
          AND deal_date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
        GROUP BY apartment_id, DATE_FORMAT(deal_date, '%Y-%m-01')
        HAVING COUNT(*) >= 3  -- 월 3건 이상 거래된 경우만
    ),
    with_moving_average AS (
        -- Step 2: 이동평균 계산 (3개월)
        SELECT
            apartment_id,
            trend_month,
            avg_price_per_m2,
            deal_count,
            -- 3개월 이동평균 (ROWS BETWEEN 사용)
            AVG(avg_price_per_m2) OVER (
                PARTITION BY apartment_id
                ORDER BY trend_month
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ) as ma_3month,
            -- 이전 달 가격 (LAG 함수)
            LAG(avg_price_per_m2, 1) OVER (
                PARTITION BY apartment_id
                ORDER BY trend_month
            ) as prev_month_price,
            -- 3개월 전 가격
            LAG(avg_price_per_m2, 3) OVER (
                PARTITION BY apartment_id
                ORDER BY trend_month
            ) as price_3months_ago
        FROM monthly_apt_stats
    ),
    with_change_rate AS (
        -- Step 3: 변동률 계산
        SELECT
            apartment_id,
            trend_month,
            avg_price_per_m2,
            deal_count,
            ma_3month,
            -- 전월 대비 변동률
            ROUND(
                CASE
                    WHEN prev_month_price IS NOT NULL AND prev_month_price > 0
                    THEN ((avg_price_per_m2 - prev_month_price) / prev_month_price * 100)
                    ELSE NULL
                END,
                2
            ) as mom_change_rate,
            -- 3개월 전 대비 변동률
            ROUND(
                CASE
                    WHEN price_3months_ago IS NOT NULL AND price_3months_ago > 0
                    THEN ((avg_price_per_m2 - price_3months_ago) / price_3months_ago * 100)
                    ELSE NULL
                END,
                2
            ) as change_rate_3m
        FROM with_moving_average
    )
    SELECT
        apartment_id,
        trend_month,
        avg_price_per_m2,
        deal_count,
        mom_change_rate as change_rate,
        -- 추세 판단
        CASE
            WHEN mom_change_rate >= 5 THEN 'RISING'
            WHEN mom_change_rate <= -5 THEN 'FALLING'
            ELSE 'STABLE'
        END as trend_status
    FROM with_change_rate
    WHERE trend_month >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
</insert>
```

**핵심 포인트:**
1. `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`: 현재 행 포함 최근 3개 행
2. `LAG(column, offset)`: offset만큼 이전 행의 값
3. `PARTITION BY apartment_id`: 아파트별로 독립적 계산

### 3. Window Frame 지정 방법
```sql
-- 1. ROWS: 물리적 행 수 기준
AVG(price) OVER (
    ORDER BY date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW  -- 최근 3개 행
)

-- 2. RANGE: 논리적 값 범위 기준
SUM(amount) OVER (
    ORDER BY date
    RANGE BETWEEN INTERVAL 1 MONTH PRECEDING AND CURRENT ROW
)

-- 3. 전체 PARTITION
AVG(price) OVER (PARTITION BY region)  -- region별 전체 평균

-- 4. 누적 계산
SUM(amount) OVER (
    PARTITION BY region
    ORDER BY date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW  -- 누적 합계
)
```

### 4. RANK vs DENSE_RANK vs ROW_NUMBER 비교
```sql
SELECT
    name,
    score,
    RANK() OVER (ORDER BY score DESC) as rank_result,
    DENSE_RANK() OVER (ORDER BY score DESC) as dense_rank_result,
    ROW_NUMBER() OVER (ORDER BY score DESC) as row_number_result
FROM students;

-- 결과:
-- name  | score | rank | dense_rank | row_number
-- Alice | 95    | 1    | 1          | 1
-- Bob   | 90    | 2    | 2          | 2
-- Carol | 90    | 2    | 2          | 3
-- David | 85    | 4    | 3          | 4
```

## 주의사항 / 함정

### 1. PARTITION BY 누락
```sql
-- 잘못된 예: 전체 데이터에 대한 순위
RANK() OVER (ORDER BY price DESC)

-- 올바른 예: 지역별 순위
RANK() OVER (PARTITION BY region ORDER BY price DESC)
```

### 2. ORDER BY 필수 함수
- `LAG`, `LEAD`, `RANK` 등은 ORDER BY 필수
- 누락 시 에러 또는 예상치 못한 결과

### 3. NULL 처리
- LAG/LEAD 결과가 NULL일 수 있음 (첫/마지막 행)
- 변동률 계산 전 NULL 체크 필수

### 4. 성능 고려사항
- Window Function은 메모리 사용량이 큼
- PARTITION이 클 경우 성능 저하 가능
- 인덱스가 ORDER BY 절과 일치하면 성능 향상

### 5. Frame 범위 주의
```sql
-- 위험: UNBOUNDED FOLLOWING은 미래 데이터까지 포함
AVG(price) OVER (
    ORDER BY date
    ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
)
```

## 관련 개념
- [[MyBatis-CTE-WITH절]]
- [[SQL-집계함수]]
- [[SQL-성능최적화]]

## 면접 질문
1. RANK와 DENSE_RANK의 차이점은?
2. LAG 함수를 사용하여 전월 대비 변동률을 계산하는 방법은?
3. 이동평균(Moving Average)을 Window Function으로 구현하는 방법은?
4. PARTITION BY와 GROUP BY의 차이점은?

## 참고 자료
- MySQL 8.0 Window Functions
- PostgreSQL Window Functions Documentation