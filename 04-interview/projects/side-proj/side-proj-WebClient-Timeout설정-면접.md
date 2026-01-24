---
tags:
  - interview
  - webclient
  - timeout
  - side-proj
  - project
created: 2025-01-23
difficulty: 중
---

# Side-proj - WebClient Timeout 설정

## 질문
> WebClient의 타임아웃 설정과 ConnectionProvider 커스터마이징을 설명해주세요.

## 핵심 답변 (3줄)
1. **Connection Timeout** - TCP 연결 수립 대기 시간 (5초)
2. **Read Timeout** - 응답 데이터 수신 대기 시간 (10초)
3. **Connection Pool** - 재사용 가능한 연결 유지로 성능 향상

## 상세 설명
```java
@Configuration
public class WebClientConfig {
    
    @Bean
    public WebClient aptWebClient() {
        // Connection Pool 설정
        ConnectionProvider connectionProvider = ConnectionProvider.builder("apt-api-pool")
            .maxConnections(50)              // 최대 연결 수
            .pendingAcquireMaxCount(100)     // 대기 큐 크기
            .pendingAcquireTimeout(Duration.ofSeconds(45))
            .maxIdleTime(Duration.ofSeconds(30))  // 유휴 연결 유지 시간
            .build();
        
        // HTTP 클라이언트 설정
        HttpClient httpClient = HttpClient.create(connectionProvider)
            .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 5000)  // 연결 타임아웃
            .responseTimeout(Duration.ofSeconds(10))  // 응답 타임아웃
            .doOnConnected(conn -> conn
                .addHandlerLast(new ReadTimeoutHandler(10))  // 읽기 타임아웃
                .addHandlerLast(new WriteTimeoutHandler(10)) // 쓰기 타임아웃
            );
        
        return WebClient.builder()
            .baseUrl("https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev")
            .clientConnector(new ReactorClientHttpConnector(httpClient))
            .build();
    }
}
```

**타임아웃 계층 구조:**
1. Connection Timeout (5초) - TCP 핸드셰이크
2. Read Timeout (10초) - 첫 바이트 수신 대기
3. Response Timeout (10초) - 전체 응답 완료 대기

## 꼬리 질문 예상
- Connection Pool이 가득 찬 경우 어떻게 되나요?
- Keep-Alive와 Connection Pool의 관계는?

## 참고
- [[Reactor-Netty-커넥션관리]]
- [[side-proj-배치스케줄링-면접]]
