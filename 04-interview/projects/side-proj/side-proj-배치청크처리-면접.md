---
tags:
  - interview
  - batch
  - chunk
  - spring
  - side-proj
  - project
created: 2025-01-23
difficulty: 중
---

# Side-proj - 배치 청크 처리

## 질문
> 대용량 데이터를 처리할 때 청크 단위로 나눠 처리한 이유는?

## 핵심 답변 (3줄)
1. **메모리 효율** - 전체 데이터를 한 번에 로드하지 않고 일부만 처리
2. **트랜잭션 분리** - 청크마다 커밋하여 장애 시 일부만 롤백
3. **성능 최적화** - 배치 INSERT로 DB 왕복 횟수 감소

## 상세 설명
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class AptDataBatchService {
    
    private static final int CHUNK_SIZE = 1000;
    private final AptTradeRepository repository;
    
    @Transactional
    public void saveAptTradeData(List<AptTradeDto> dataList) {
        int totalSize = dataList.size();
        log.info("총 {}건의 데이터를 {}건씩 청크로 처리", totalSize, CHUNK_SIZE);
        
        for (int i = 0; i < totalSize; i += CHUNK_SIZE) {
            int endIndex = Math.min(i + CHUNK_SIZE, totalSize);
            List<AptTradeDto> chunk = dataList.subList(i, endIndex);
            
            // 엔티티 변환
            List<AptTrade> entities = chunk.stream()
                .map(dto -> AptTrade.builder()
                    .dealAmount(dto.getDealAmount())
                    .buildYear(dto.getBuildYear())
                    .dealYear(dto.getDealYear())
                    .dealMonth(dto.getDealMonth())
                    .dealDay(dto.getDealDay())
                    .aptName(dto.getAptName())
                    .build())
                .toList();
            
            // 배치 INSERT
            repository.saveAll(entities);
            
            log.info("청크 {}/{} 완료 ({}-{})", 
                (i / CHUNK_SIZE) + 1, 
                (totalSize + CHUNK_SIZE - 1) / CHUNK_SIZE,
                i + 1, endIndex);
        }
    }
}
```

**배치 INSERT 최적화:**
```yaml
# application.yml
spring:
  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 1000  # CHUNK_SIZE와 동일하게
        order_inserts: true
        order_updates: true
```

## 꼬리 질문 예상
- 청크 처리 중 일부가 실패하면 어떻게 처리하나요?
- Spring Batch의 Chunk-oriented Processing과의 차이는?

## 참고
- [[JPA-배치-INSERT-최적화]]
- [[side-proj-외부API-응답파싱-면접]]
