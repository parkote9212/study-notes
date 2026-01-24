---
tags:
  - interview
  - mybatis
  - sql
  - window-function
created: 2025-01-23
difficulty: 중
---

# MyBatis Window Function 면접

## 질문
> Window Function의 개념과 RANK, LAG, 이동평균을 실무에서 어떻게 활용하는지 설명해주세요.

## 핵심 답변 (3줄)
1. Window Function은 OVER 절을 사용하여 행 그룹에 대한 계산을 수행하되, GROUP BY와 달리 개별 행을 유지하여 순위, 이전/다음 값 참조, 이동평균 등을 계산합니다.
2. RANK()는 지역별 가격 순위를, LAG()는 전월 대비 변동률을, 이동평균은 3개월 평균 가격 추세를 파악하는 데 사용됩니다.
3. PARTITION BY로 그룹을 나누고, ORDER BY로 정렬 기준을 정하며, ROWS BETWEEN으로 계산 범위를 지정하여 다양한 분석이 가능합니다.

## 상세 설명

### Window Function의 핵심 구조
```sql
함수명() OVER (
    PARTITION BY 그룹컬럼    -- 선택: 데이터를 그룹으로 분할
    ORDER BY 정렬컬럼        -- 필수/선택: 순서 지정
    ROWS BETWEEN ... AND ... -- 선택: 계산 범위 지정
)
```

### 실무 활용 사례 1: 지역별 가격 순위

**비즈니스 요구사항:**
- 전국 아파트 가격 순위
- 시/도별 가격 순위
- 상위 몇 %인지 백분위 표시

**구현:**
```xml
<select id="getRegionRankingStats">
    SELECT
        region_code,
        sido,
        sigungu,
        avg_price,
        -- 전체 순위
        RANK() OVER (ORDER BY avg_price DESC) as overall_rank,
        -- 시도별 순위
        RANK() OVER (PARTITION BY sido ORDER BY avg_price DESC) as sido_rank,
        -- 백분위수
        PERCENT_RANK() OVER (ORDER BY avg_price DESC) as price_percentile,
        -- 가격 등급
        CASE
            WHEN PERCENT_RANK() OVER (ORDER BY avg_price DESC) <= 0.33 THEN 'HIGH'
            WHEN PERCENT_RANK() OVER (ORDER BY avg_price DESC) <= 0.66 THEN 'MEDIUM'
            ELSE 'LOW'
        END as price_grade
    FROM region_stats
</select>
```

**결과 예시:**
```
region  | sido | avg_price | overall_rank | sido_rank | percentile | grade
강남구   | 서울 | 150000   | 1            | 1         | 0.00       | HIGH
서초구   | 서울 | 140000   | 2            | 2         | 0.01       | HIGH
송파구   | 서울 | 130000   | 3            | 3         | 0.02       | HIGH
```

### 실무 활용 사례 2: 가격 추세 분석 (LAG, 이동평균)

**비즈니스 요구사항:**
- 아파트별 월간 가격 변화 추적
- 전월 대비 변동률 계산
- 3개월 이동평균으로 단기 추세 파악

**구현:**
```xml
<select id="getPriceTrend">
    WITH monthly_stats AS (
        SELECT
            apartment_id,
            DATE_FORMAT(deal_date, '%Y-%m-01') as month,
            AVG(price_per_m2) as avg_price
        FROM real_estate_deal
        GROUP BY apartment_id, DATE_FORMAT(deal_date, '%Y-%m-01')
    )
    SELECT
        apartment_id,
        month,
        avg_price,
        -- 3개월 이동평균
        AVG(avg_price) OVER (
            PARTITION BY apartment_id
            ORDER BY month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) as ma_3month,
        -- 이전 달 가격
        LAG(avg_price, 1) OVER (
            PARTITION BY apartment_id
            ORDER BY month
        ) as prev_month_price,
        -- 전월 대비 변동률
        ROUND(
            (avg_price - LAG(avg_price, 1) OVER (
                PARTITION BY apartment_id ORDER BY month
            )) / LAG(avg_price, 1) OVER (
                PARTITION BY apartment_id ORDER BY month
            ) * 100,
            2
        ) as mom_change_rate,
        -- 추세 판단
        CASE
            WHEN avg_price - LAG(avg_price, 1) OVER (...) >= 500 THEN 'RISING'
            WHEN avg_price - LAG(avg_price, 1) OVER (...) <= -500 THEN 'FALLING'
            ELSE 'STABLE'
        END as trend_status
    FROM monthly_stats
</select>
```

### RANK vs DENSE_RANK vs ROW_NUMBER

```sql
-- 예시 데이터: 점수 (95, 90, 90, 85)
SELECT
    name,
    score,
    RANK() OVER (ORDER BY score DESC) as rank_result,
    DENSE_RANK() OVER (ORDER BY score DESC) as dense_rank_result,
    ROW_NUMBER() OVER (ORDER BY score DESC) as row_number_result
FROM students;

-- 결과:
-- name  | score | RANK | DENSE_RANK | ROW_NUMBER
-- Alice | 95    | 1    | 1          | 1
-- Bob   | 90    | 2    | 2          | 2
-- Carol | 90    | 2    | 2          | 3  (동점이어도 고유 번호)
-- David | 85    | 4    | 3          | 4  (RANK는 3 건너뜀)
```

**차이점:**
- `RANK()`: 동점 시 다음 순위 건너뜀 (1, 2, 2, 4)
- `DENSE_RANK()`: 동점 시 다음 순위 연속 (1, 2, 2, 3)
- `ROW_NUMBER()`: 동점 무관 고유 번호 (1, 2, 3, 4)

### Window Frame 지정 (ROWS BETWEEN)

```sql
-- 현재 행 포함 최근 3개월
ROWS BETWEEN 2 PRECEDING AND CURRENT ROW

-- 현재 행 기준 전후 1개월
ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING

-- 처음부터 현재까지 (누적)
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW

-- 현재부터 끝까지
ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
```

## 코드 예시 (필요시)
```sql
-- LAG/LEAD를 활용한 전후 비교
SELECT
    deal_date,
    deal_amount,
    LAG(deal_amount, 1) OVER (ORDER BY deal_date) as prev_amount,
    LEAD(deal_amount, 1) OVER (ORDER BY deal_date) as next_amount,
    deal_amount - LAG(deal_amount, 1) OVER (ORDER BY deal_date) as diff
FROM deals;

-- PARTITION BY로 그룹별 독립 계산
SELECT
    region_code,
    deal_date,
    deal_amount,
    RANK() OVER (
        PARTITION BY region_code  -- 지역별로 독립적 순위
        ORDER BY deal_amount DESC
    ) as region_rank
FROM deals;

-- 이동평균 3개월
AVG(price) OVER (
    PARTITION BY apartment_id
    ORDER BY month
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
) as ma_3month
```

## 꼬리 질문 예상
- PARTITION BY와 GROUP BY의 차이점은?
- LAG 함수에서 offset을 2 이상으로 설정하면 어떻게 되나요?
- Window Function의 성능 최적화 방법은?
- ROWS와 RANGE의 차이점은?
- NULL 값이 포함된 경우 LAG/LEAD는 어떻게 동작하나요?

## 참고
- [[MyBatis-Window-Function]]
- [[MyBatis-CTE-WITH절]]
- [[SQL-집계함수]]