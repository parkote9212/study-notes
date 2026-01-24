---
tags:
  - interview
  - mybatis
  - sql
  - cte
created: 2025-01-23
difficulty: 중
---

# MyBatis CTE (WITH절) 면접

## 질문
> MyBatis에서 CTE(Common Table Expression)를 사용하는 이유와 실제 활용 사례를 설명해주세요.

## 핵심 답변 (3줄)
1. CTE는 WITH 절을 사용하여 복잡한 쿼리를 논리적 단계로 분리함으로써 가독성과 유지보수성을 높입니다.
2. 월별 통계 계산 시 현재 월 집계 → 전월 데이터 조회 → 전년 동월 데이터 조회 → 변동률 계산의 4단계로 분리하여 각 단계를 명확하게 표현할 수 있습니다.
3. 동일한 CTE를 쿼리 내에서 여러 번 참조할 수 있어 서브쿼리 중복을 제거하고, 각 단계별로 독립적인 수정과 디버깅이 가능합니다.

## 상세 설명

### CTE의 정의와 구조
```xml
WITH cte_name AS (
    SELECT ...
),
another_cte AS (
    SELECT ...
)
SELECT * FROM cte_name JOIN another_cte
```

### 실무 활용 예시 - 월별 통계 변동률 계산

**비즈니스 요구사항:**
- 매월 지역별 평균 거래가 계산
- 전월 대비 변동률 (MoM: Month over Month)
- 전년 동월 대비 변동률 (YoY: Year over Year)

**CTE를 사용한 구현:**
```xml
WITH monthly_aggregation AS (
    -- 1단계: 현재 월 집계
    SELECT region_code, AVG(deal_amount) as avg_amount
    FROM real_estate_deal
    WHERE YEAR(deal_date) = #{year} AND MONTH(deal_date) = #{month}
    GROUP BY region_code
),
previous_month_data AS (
    -- 2단계: 전월 데이터
    SELECT region_code, avg_deal_amount as prev_month_avg
    FROM monthly_statistics
    WHERE stats_year = CASE WHEN #{month} = 1 THEN #{year} - 1 ELSE #{year} END
      AND stats_month = CASE WHEN #{month} = 1 THEN 12 ELSE #{month} - 1 END
),
previous_year_data AS (
    -- 3단계: 전년 동월 데이터
    SELECT region_code, avg_deal_amount as prev_year_avg
    FROM monthly_statistics
    WHERE stats_year = #{year} - 1 AND stats_month = #{month}
)
-- 4단계: 변동률 계산
SELECT
    ma.region_code,
    ma.avg_amount,
    ROUND((ma.avg_amount - pm.prev_month_avg) / pm.prev_month_avg * 100, 2) as mom_rate,
    ROUND((ma.avg_amount - py.prev_year_avg) / py.prev_year_avg * 100, 2) as yoy_rate
FROM monthly_aggregation ma
LEFT JOIN previous_month_data pm ON ma.region_code = pm.region_code
LEFT JOIN previous_year_data py ON ma.region_code = py.region_code
```

### CTE vs 서브쿼리 비교

**서브쿼리 방식 (가독성 낮음):**
```sql
SELECT
    ma.region_code,
    ma.avg_amount,
    ROUND((ma.avg_amount - (
        SELECT avg_deal_amount FROM monthly_statistics
        WHERE region_code = ma.region_code
          AND stats_year = CASE WHEN #{month} = 1 THEN #{year} - 1 ELSE #{year} END
    )) / (...) * 100, 2) as mom_rate
FROM (
    SELECT region_code, AVG(deal_amount) as avg_amount
    FROM real_estate_deal
    GROUP BY region_code
) ma
```

**CTE 방식 (가독성 높음):**
- 각 단계가 명확히 분리됨
- 단계별 이름으로 의도 명확화
- 디버깅 시 각 CTE를 독립적으로 실행 가능

### CTE의 장점
1. **가독성**: 복잡한 로직을 단계별로 명확하게 표현
2. **재사용성**: 동일한 CTE를 여러 번 참조 가능
3. **유지보수성**: 각 단계를 독립적으로 수정
4. **디버깅**: 각 CTE 결과를 개별적으로 확인 가능

## 코드 예시 (필요시)
```sql
-- 전월 계산 로직 (1월 처리)
CASE 
    WHEN #{month} = 1 THEN #{year} - 1  -- 1월이면 전년
    ELSE #{year}                         -- 아니면 올해
END

CASE 
    WHEN #{month} = 1 THEN 12           -- 1월이면 12월
    ELSE #{month} - 1                    -- 아니면 전월
END

-- NULL 안전 변동률 계산
ROUND(
    CASE
        WHEN prev_avg IS NOT NULL AND prev_avg > 0
        THEN ((curr_avg - prev_avg) / prev_avg * 100)
        ELSE NULL
    END,
    2
) as change_rate
```

## 꼬리 질문 예상
- CTE와 임시 테이블(Temporary Table)의 차이점은?
- CTE를 재귀적으로 사용할 수 있나요? (Recursive CTE)
- CTE의 성능은 서브쿼리와 비교해 어떤가요?
- MyBatis에서 CTE 결과를 재사용하려면 어떻게 해야 하나요?
- WITH 절에서 정의한 CTE의 스코프(유효 범위)는?

## 참고
- [[MyBatis-CTE-WITH절]]
- [[MyBatis-Window-Function]]
- [[SQL-성능최적화]]