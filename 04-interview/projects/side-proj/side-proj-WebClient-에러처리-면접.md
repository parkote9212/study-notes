---
tags:
  - interview
  - webclient
  - error-handling
  - side-proj
  - project
created: 2025-01-23
difficulty: 중
---

# Side-proj - WebClient 에러 처리

## 질문
> WebClient에서 onStatus를 사용한 에러 처리 전략을 설명해주세요.

## 핵심 답변 (3줄)
1. **상태 코드별 처리** - 4xx는 클라이언트 오류, 5xx는 서버 오류로 분리
2. **onStatus 체이닝** - 여러 조건을 체인으로 연결하여 세밀한 제어
3. **재시도 전략** - `retry()`, `retryWhen()`으로 일시적 오류 대응

## 상세 설명
```java
public Mono<AptTradeResponse> fetchAptTradeData(String lawd, String dealYmd) {
    return aptWebClient.get()
        .uri(uriBuilder -> uriBuilder
            .queryParam("serviceKey", serviceKey)
            .queryParam("LAWD_CD", lawd)
            .queryParam("DEAL_YMD", dealYmd)
            .build())
        .retrieve()
        // 4xx 에러 처리
        .onStatus(HttpStatusCode::is4xxClientError, response -> 
            response.bodyToMono(String.class).flatMap(body -> {
                log.error("API 요청 오류 - Status: {}, Body: {}", 
                    response.statusCode(), body);
                return Mono.error(new IllegalArgumentException(
                    "잘못된 요청 파라미터: " + body));
            })
        )
        // 5xx 에러 처리
        .onStatus(HttpStatusCode::is5xxServerError, response ->
            response.bodyToMono(String.class).flatMap(body -> {
                log.error("API 서버 오류 - Status: {}, Body: {}", 
                    response.statusCode(), body);
                return Mono.error(new RuntimeException(
                    "외부 API 서버 오류: " + body));
            })
        )
        .bodyToMono(AptTradeResponse.class)
        .timeout(Duration.ofSeconds(10))
        .retryWhen(Retry.backoff(3, Duration.ofSeconds(2))
            .filter(throwable -> throwable instanceof TimeoutException)
            .onRetryExhaustedThrow((retryBackoffSpec, retrySignal) -> 
                new RuntimeException("재시도 횟수 초과")));
}
```

## 꼬리 질문 예상
- retryWhen의 exponential backoff는 어떻게 동작하나요?
- Circuit Breaker 패턴을 적용한다면?

## 참고
- [[WebClient-에러처리-패턴]]
- [[Resilience4j-CircuitBreaker]]
