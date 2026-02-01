---
tags:
  - interview
  - java
  - exception
created: 2026-01-31
difficulty: 중
---

# Java 예외처리 면접 대비

## 질문 1: Error와 Exception의 차이는?

> Error와 Exception의 차이점을 설명하고, 각각의 예시를 들어주세요.

### 핵심 답변 (3줄)

1. **Error는 시스템 레벨의 심각한 문제**로 개발자가 처리할 수 없고 프로그램이 강제 종료됩니다
2. **Exception은 프로그램 레벨의 문제**로 개발자가 try-catch로 처리할 수 있습니다
3. 둘 다 **Throwable을 상속**하지만, Error는 복구 불가능, Exception은 복구 가능합니다

### 상세 설명

| 구분 | Error | Exception |
|------|-------|-----------|
| 발생 원인 | 시스템 리소스 부족 | 프로그램 로직 오류 |
| 처리 가능 | ❌ 불가 | ✅ 가능 |
| 예시 | OutOfMemoryError | IOException |

## 질문 2: Checked vs Unchecked Exception

> Checked Exception과 Unchecked Exception의 차이를 설명해 주세요.

### 핵심 답변 (3줄)

1. **Checked Exception은 컴파일 타임에 예외 처리를 강제**합니다(try-catch 또는 throws 필수)
2. **Unchecked Exception은 예외 처리가 선택적**이며, 프로그래밍 실수로 발생합니다
3. Spring의 @Transactional은 **Unchecked만 자동 롤백**합니다

### 상세 설명

```java
// Checked Exception - 처리 강제
public void readFile() throws IOException {
    FileReader reader = new FileReader("file.txt");
}

// Unchecked Exception - 처리 선택
public void divide(int a, int b) {
    return a / b;  // throws 불필요
}
```

## 참고

- [[Java-예외처리-Exception]]