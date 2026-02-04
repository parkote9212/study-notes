---
tags:
  - interview
  - webclient
  - reactive
  - spring
  - side-proj
  - project
created: 2025-01-23
difficulty: 중
---

# Side-proj - WebClient 비동기 API 연동

## 질문
> RestTemplate 대신 WebClient를 선택한 이유는?

## 핵심 답변 (3줄)
1. **Non-blocking** - 응답 대기 중에도 다른 작업 처리 가능 (Thread 효율성)
2. **Reactive Streams** - Mono/Flux로 비동기 스트림 처리
3. **최신 표준** - Spring 5+ 권장 HTTP 클라이언트

## 상세 설명
```java
@Configuration
public class WebClientConfig {
    
    @Bean
    public WebClient aptWebClient() {
        return WebClient.builder()
            .baseUrl("https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev")
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .codecs(configurer -> configurer
                .defaultCodecs()
                .maxInMemorySize(10 * 1024 * 1024))  // 10MB
            .build();
    }
}

// 비동기 API 호출
@Service
@RequiredArgsConstructor
public class AptApiService {
    
    private final WebClient aptWebClient;
    
    public Mono<AptTradeResponse> fetchAptTradeData(String lawd, String dealYmd) {
        return aptWebClient.get()
            .uri(uriBuilder -> uriBuilder
                .queryParam("serviceKey", serviceKey)
                .queryParam("LAWD_CD", lawd)
                .queryParam("DEAL_YMD", dealYmd)
                .build())
            .retrieve()
            .onStatus(HttpStatusCode::is4xxClientError, 
                response -> Mono.error(new IllegalArgumentException("잘못된 요청")))
            .onStatus(HttpStatusCode::is5xxServerError,
                response -> Mono.error(new RuntimeException("서버 오류")))
            .bodyToMono(AptTradeResponse.class)
            .timeout(Duration.ofSeconds(10))
            .retry(3);  // 실패 시 3번 재시도
    }
}
```

## 꼬리 질문 예상
- RestTemplate과 성능 차이는 얼마나 나나요?
- Mono와 Flux의 차이는?

## 참고
- [[side-proj-WebClient-에러처리-면접]]
- [[side-proj-WebClient-Timeout설정-면접]]
