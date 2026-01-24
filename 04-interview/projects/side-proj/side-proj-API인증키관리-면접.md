---
tags:
  - interview
  - security
  - api-key
  - spring
  - side-proj
  - project
created: 2025-01-23
difficulty: 중
---

# Side-proj - API 인증키 관리

## 질문
> 공공데이터 API 인증키를 안전하게 관리하는 방법은?

## 핵심 답변 (3줄)
1. **환경변수 분리** - `.env` 파일과 `application.yml` 분리
2. **Git 제외** - `.gitignore`에 `.env` 추가하여 소스 노출 방지
3. **운영 환경** - AWS Secrets Manager, K8s Secret 활용

## 상세 설명
```yaml
# application.yml (Git에 커밋)
api:
  apt-trade:
    base-url: https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev
    service-key: ${APT_API_SERVICE_KEY}  # 환경변수 참조

# .env (Git 제외)
APT_API_SERVICE_KEY=abcd1234efgh5678...실제인증키
```

```java
// 설정 클래스
@Configuration
@ConfigurationProperties(prefix = "api.apt-trade")
@Data
public class AptApiProperties {
    private String baseUrl;
    private String serviceKey;  // 자동 주입
}

// 사용
@Service
@RequiredArgsConstructor
public class AptApiService {
    
    private final AptApiProperties properties;
    private final WebClient webClient;
    
    public Mono<AptTradeResponse> fetchData(String lawd, String dealYmd) {
        return webClient.get()
            .uri(uriBuilder -> uriBuilder
                .queryParam("serviceKey", properties.getServiceKey())
                .queryParam("LAWD_CD", lawd)
                .queryParam("DEAL_YMD", dealYmd)
                .build())
            .retrieve()
            .bodyToMono(AptTradeResponse.class);
    }
}
```

**운영 환경 보안 강화:**
```yaml
# AWS Secrets Manager 사용
spring:
  cloud:
    aws:
      secretsmanager:
        enabled: true
        name: /prod/apt-api/service-key
```

## 꼬리 질문 예상
- 키 로테이션은 어떻게 처리하나요?
- 키가 유출되었을 때 대응 방안은?

## 참고
- [[환경변수-보안-관리]]
- [[AWS-SecretsManager-통합]]
