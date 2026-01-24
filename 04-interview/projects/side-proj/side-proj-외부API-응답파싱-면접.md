---
tags:
  - interview
  - xml
  - parsing
  - side-proj
  - project
created: 2025-01-23
difficulty: 중
---

# Side-proj - 외부 API 응답 파싱

## 질문
> 공공데이터 API의 XML 응답을 어떻게 파싱했나요?

## 핵심 답변 (3줄)
1. **Jackson XML** - JSON과 동일한 방식으로 XML 매핑
2. **@JacksonXmlRootElement** - XML 루트 요소 지정
3. **@JacksonXmlProperty** - XML 속성/요소 매핑

## 상세 설명
```java
// API 응답 DTO
@Data
@JacksonXmlRootElement(localName = "response")
public class AptTradeResponse {
    
    @JacksonXmlProperty(localName = "header")
    private Header header;
    
    @JacksonXmlProperty(localName = "body")
    private Body body;
    
    @Data
    public static class Header {
        @JacksonXmlProperty(localName = "resultCode")
        private String resultCode;
        
        @JacksonXmlProperty(localName = "resultMsg")
        private String resultMsg;
    }
    
    @Data
    public static class Body {
        @JacksonXmlProperty(localName = "items")
        private Items items;
        
        @JacksonXmlProperty(localName = "numOfRows")
        private int numOfRows;
        
        @JacksonXmlProperty(localName = "totalCount")
        private int totalCount;
    }
    
    @Data
    public static class Items {
        @JacksonXmlProperty(localName = "item")
        @JacksonXmlElementWrapper(useWrapping = false)
        private List<AptTradeDto> itemList;
    }
}

// WebClient 설정
@Bean
public WebClient aptWebClient() {
    XmlMapper xmlMapper = new XmlMapper();
    xmlMapper.registerModule(new JavaTimeModule());
    
    ExchangeStrategies strategies = ExchangeStrategies.builder()
        .codecs(configurer -> {
            configurer.defaultCodecs().jackson2XmlDecoder(
                new Jackson2XmlDecoder(xmlMapper, MediaType.APPLICATION_XML));
        })
        .build();
    
    return WebClient.builder()
        .exchangeStrategies(strategies)
        .build();
}
```

## 꼬리 질문 예상
- JAXB 대신 Jackson XML을 선택한 이유는?
- 네임스페이스가 있는 XML은 어떻게 처리하나요?

## 참고
- [[Jackson-XML-매핑]]
- [[side-proj-API인증키관리-면접]]
