---
tags:
  - interview
  - rest-api
  - spring
  - fitneeds
  - project
created: 2025-01-23
difficulty: 중
---

# Fitneeds - RESTful API 설계

## 질문
> 관리자 API를 설계할 때 어떤 원칙을 적용했나요?

## 핵심 답변 (3줄)
1. **리소스 중심 URL** - `/api/reservations`, `/api/user-pass`로 명사 기반 설계
2. **HTTP 메서드 활용** - GET(조회), POST(생성), PATCH(부분수정), DELETE(삭제)
3. **상태 변경 엔드포인트** - `/api/reservations/{id}/status`, `/api/reservations/{id}/cancel`

## 상세 설명
```java
@Tag(name = "[관리자] 예약 관리")
@RestController
@RequestMapping("/api/reservations")
public class AdminReservationController {
    
    // 목록 조회
    @GetMapping
    public ResponseEntity<PagedResponse<ReservationResponse>> getReservations(
            @Valid ReservationSearchRequest request) {
        return ResponseEntity.ok(service.getReservationList(request));
    }
    
    // 상세 조회
    @GetMapping("/{id}")
    public ResponseEntity<ReservationResponse> getDetail(@PathVariable Long id) {
        return ResponseEntity.ok(service.getReservationDetail(id));
    }
    
    // 생성
    @PostMapping
    public ResponseEntity<String> create(@Valid @RequestBody ReservationCreateRequest req) {
        service.createReservation(req, adminId);
        return ResponseEntity.ok("예약이 등록되었습니다.");
    }
    
    // 부분 수정
    @PatchMapping("/{id}")
    public ResponseEntity<String> update(@PathVariable Long id, 
                                         @RequestBody ReservationUpdateRequest req) {
        service.updateReservation(id, req, adminId);
        return ResponseEntity.ok("예약 정보가 수정되었습니다.");
    }
    
    // 상태 변경
    @PatchMapping("/{id}/status")
    public ResponseEntity<String> updateStatus(@PathVariable Long id,
                                               @Valid @RequestBody StatusChangeRequest req) {
        service.updateReservationStatus(id, req, adminId);
        return ResponseEntity.ok("예약 상태가 변경되었습니다.");
    }
}
```

## 꼬리 질문 예상
- PUT과 PATCH의 차이점은?
- 상태 변경을 `/status` 엔드포인트로 분리한 이유는?

## 참고
- [[RESTful-API-설계-가이드]]
- [[fitneeds-Record-DTO-면접]]
