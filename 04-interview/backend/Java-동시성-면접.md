---
tags:
  - interview
  - java
created: 2026-01-20
difficulty: 최상
---

# Java 동시성 (면접 Q&A)

## 질문 1
> Race Condition이 무엇이고 어떻게 해결하나요?

## 핵심 답변 (3줄)
1. **Race Condition** - 여러 스레드가 공유 자원에 동시 접근할 때 결과가 예측 불가능해지는 상황
2. **해결책** - synchronized, Lock, AtomicInteger, Immutable 객체 등
3. **베스트 프랙티스** - 가능하면 공유 자원을 최소화하고 불변 객체 사용

## 상세 설명

두 스레드가 같은 변수를 동시에 수정하면:
```java
// count = 0
Thread1: count++;  // 0 읽기 → 1로 증가
Thread2: count++;  // 0 읽기 → 1로 증가
// 결과: count = 1 (예상: 2)
```

이를 해결하는 방법들:

1. **synchronized** - JVM의 내장 락 사용
2. **Lock** - 더 세밀한 제어 가능
3. **AtomicInteger** - 원자적 연산 보장
4. **Immutable** - 상태 변경 자체를 피함

---

## 질문 2
> synchronized vs Lock의 차이는?

## 핵심 답변 (3줄)
1. **synchronized** - JVM 기본 제공, 사용 간단하지만 제한적
2. **Lock** - java.util.concurrent.locks, 더 유연하고 강력함
3. **차이** - Lock은 시간 초과, 인터럽트, 조건 변수 등 지원

---

## 질문 3
> Deadlock이란?

## 핵심 답변 (3줄)
1. **Deadlock** - 두 스레드가 각각 다른 스레드가 보유한 락을 대기하는 상황
2. **발생 조건** - 상호 배제, 점유와 대기, 비선점, 순환 대기 (모두 만족 시)
3. **회피** - 락 순서 통일, 타임아웃, Semaphore 등

---

**작성일**: 2026-01-20
