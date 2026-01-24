---
tags:
  - interview
  - java
created: 2026-01-20
difficulty: 최상
---

# Java 함수형 프로그래밍 (면접 Q&A)

## 질문 1
> 람다식이란?

## 핵심 답변 (3줄)
1. **람다식** - 익명 함수를 간결하게 표현하는 문법
2. **문법** - `(parameter) -> body` 형태
3. **활용** - 함수형 인터페이스 구현, 콜백 처리 등에 사용

## 상세 설명

Java 8 이전에는 콜백이나 이벤트 핸들러를 구현할 때 익명 클래스를 사용했습니다:

```java
// Java 7 이전
button.setOnClickListener(new ClickListener() {
    @Override
    public void onClick() {
        System.out.println("Clicked");
    }
});

// Java 8 이후 - 람다식
button.setOnClickListener(() -> System.out.println("Clicked"));
```

람다식의 장점:
- 코드 간결성
- 읽기 쉬운 함수형 스타일
- 스트림 API와 완벽 호환

---

## 질문 2
> Stream API는 무엇이고 왜 필요한가?

## 핵심 답변 (3줄)
1. **Stream** - 데이터를 선언적으로 처리하는 API
2. **특징** - filter, map, reduce 등 함수형 연산 제공
3. **장점** - 간결한 코드, 자동 병렬화 가능, 가독성 향상

## 상세 설명

기존 명령형 코드:
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
List<Integer> result = new ArrayList<>();

for (Integer n : numbers) {
    if (n % 2 == 0) {
        result.add(n * 2);
    }
}
```

Stream 사용:
```java
List<Integer> result = numbers.stream()
        .filter(n -> n % 2 == 0)
        .map(n -> n * 2)
        .collect(Collectors.toList());
```

Stream의 이점:
- 선언적: "어떻게"보다 "무엇을"에 집중
- 체인 가능: 메서드를 연쇄적으로 호출
- 병렬화 가능: `.parallel()` 한 줄로 병렬 처리
- 중간/최종 연산 분리

---

## 질문 3
> filter, map, reduce의 차이는?

## 핵심 답변 (3줄)
1. **filter** - 조건에 따라 요소 선택 (Predicate)
2. **map** - 각 요소를 변환 (Function)
3. **reduce** - 모든 요소를 하나의 값으로 집계 (BinaryOperator)

---

**작성일**: 2026-01-20
