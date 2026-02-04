---
tags:
  - interview
  - java
  - record
  - dto
  - fitneeds
  - project
created: 2025-01-23
difficulty: 중
---

# Fitneeds - Record DTO 활용

## 질문
> Java Record를 DTO로 사용한 이유와 장점은?

## 핵심 답변 (3줄)
1. **불변성 보장** - 생성 후 값 변경 불가, 스레드 안전
2. **보일러플레이트 제거** - getter, equals, hashCode, toString 자동 생성
3. **명확한 의도** - "이 객체는 데이터 전달용"임을 코드로 표현

## 상세 설명
```java
// Request DTO - 검증 어노테이션과 함께 사용
public record ReservationCreateRequest(
    @NotNull(message = "회원 ID는 필수입니다") 
    String userId,
    
    @NotNull(message = "스케줄 ID는 필수입니다") 
    Long schdId,
    
    @NotNull(message = "이용권 ID는 필수입니다") 
    Long passId
) {}

// Search DTO - 페이징 포함
public record ReservationSearchRequest(
    String userId,
    String status,
    LocalDate startDate,
    LocalDate endDate,
    @Valid BasePagingRequest paging
) {
    public ReservationSearchRequest {
        // Compact Constructor - 기본값 설정
        if (paging == null) {
            paging = BasePagingRequest.defaultPaging();
        }
    }
}

// Response DTO - 팩토리 메서드 패턴
public record ReservationResponse(
    Long rsvId,
    String userName,
    String programName,
    LocalDate rsvDt,
    String status
) {
    public static ReservationResponse from(Reservation r) {
        return new ReservationResponse(
            r.getRsvId(),
            r.getUser().getUserName(),
            r.getSchedule().getProgram().getProgramName(),
            r.getRsvDt(),
            r.getSttsCd()
        );
    }
}
```

## 꼬리 질문 예상
- Record에서 유효성 검증은 어떻게 하나요?
- Record의 한계점은?

## 참고
- [[fitneeds-RESTful-API설계-면접]]
