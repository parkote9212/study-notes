---
tags:
  - interview
  - rest-api
  - spring
  - validation
  - fitneeds
  - project
created: 2025-01-23
difficulty: 중
---

# Fitneeds - REST API 설계 & 관리자 기능 면접

## 질문 1: RESTful API 설계 원칙
> 관리자 API를 설계할 때 어떤 원칙을 적용했나요?

### 핵심 답변 (3줄)
1. **리소스 중심 URL** - `/api/reservations`, `/api/user-pass`로 명사 기반 설계
2. **HTTP 메서드 활용** - GET(조회), POST(생성), PATCH(부분수정), DELETE(삭제)
3. **상태 변경 엔드포인트** - `/api/reservations/{id}/status`, `/api/reservations/{id}/cancel`

### 상세 설명
```java
@Tag(name = "[관리자] 예약 관리")
@RestController
@RequestMapping("/api/reservations")
public class AdminReservationController {
    
    // 목록 조회 - GET /api/reservations
    @GetMapping
    public ResponseEntity<PagedResponse<ReservationResponse>> getReservations(
            @Valid ReservationSearchRequest request) {
        return ResponseEntity.ok(service.getReservationList(request));
    }
    
    // 상세 조회 - GET /api/reservations/{id}
    @GetMapping("/{id}")
    public ResponseEntity<ReservationResponse> getDetail(@PathVariable Long id) {
        return ResponseEntity.ok(service.getReservationDetail(id));
    }
    
    // 생성 - POST /api/reservations
    @PostMapping
    public ResponseEntity<String> create(@Valid @RequestBody ReservationCreateRequest req) {
        service.createReservation(req, adminId);
        return ResponseEntity.ok("예약이 등록되었습니다.");
    }
    
    // 부분 수정 - PATCH /api/reservations/{id}
    @PatchMapping("/{id}")
    public ResponseEntity<String> update(@PathVariable Long id, 
                                         @RequestBody ReservationUpdateRequest req) {
        service.updateReservation(id, req, adminId);
        return ResponseEntity.ok("예약 정보가 수정되었습니다.");
    }
    
    // 상태 변경 (서브 리소스) - PATCH /api/reservations/{id}/status
    @PatchMapping("/{id}/status")
    public ResponseEntity<String> updateStatus(@PathVariable Long id,
                                               @Valid @RequestBody StatusChangeRequest req) {
        service.updateReservationStatus(id, req, adminId);
        return ResponseEntity.ok("예약 상태가 변경되었습니다.");
    }
    
    // 취소 (서브 리소스) - PATCH /api/reservations/{id}/cancel
    @PatchMapping("/{id}/cancel")
    public ResponseEntity<String> cancel(@PathVariable Long id,
                                         @Valid @RequestBody CancelRequest req) {
        service.cancelReservation(id, req, adminId);
        return ResponseEntity.ok("예약이 취소되었습니다.");
    }
}
```

### 꼬리 질문 예상
- PUT과 PATCH의 차이점은?
- 상태 변경을 `/status` 엔드포인트로 분리한 이유는?

---

## 질문 2: Record를 활용한 DTO 설계
> Java Record를 DTO로 사용한 이유와 장점은?

### 핵심 답변 (3줄)
1. **불변성 보장** - 생성 후 값 변경 불가, 스레드 안전
2. **보일러플레이트 제거** - getter, equals, hashCode, toString 자동 생성
3. **명확한 의도** - "이 객체는 데이터 전달용"임을 코드로 표현

### 상세 설명
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
    @Valid BasePagingRequest paging  // 공통 페이징
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
    LocalTime rsvTime,
    String status
) {
    // 엔티티 → DTO 변환 팩토리 메서드
    public static ReservationResponse from(Reservation r) {
        return new ReservationResponse(
            r.getRsvId(),
            r.getUser().getUserName(),
            r.getSchedule().getProgram().getProgramName(),
            r.getRsvDt(),
            r.getRsvTime(),
            r.getSttsCd()
        );
    }
}
```

### 꼬리 질문 예상
- Record에서 유효성 검증은 어떻게 하나요?
- Record의 한계점은?

---

## 질문 3: 공통 페이징 처리
> 여러 API에서 공통으로 사용하는 페이징을 어떻게 설계했나요?

### 핵심 답변 (3줄)
1. **BasePagingRequest** - page, size, sortBy, sortOrder 공통 정의
2. **PagedResponse 래퍼** - 데이터 + 페이징 메타 정보 통합
3. **MyBatis 파라미터 자동 계산** - offset, limit 자동 계산

### 상세 설명
```java
// 공통 페이징 요청
public record BasePagingRequest(
    @Min(1) Integer page,
    @Min(1) @Max(100) Integer size,
    String sortBy,
    String sortOrder
) {
    public static BasePagingRequest defaultPaging() {
        return new BasePagingRequest(1, 10, null, "DESC");
    }
    
    public int getOffset() {
        return (page - 1) * size;
    }
}

// 공통 페이징 응답
public record PagedResponse<T>(
    List<T> content,
    int totalCount,
    int currentPage,
    int totalPages,
    int size,
    boolean hasNext,
    boolean hasPrevious
) {
    public static <T> PagedResponse<T> of(List<T> content, int total, BasePagingRequest paging) {
        int totalPages = (int) Math.ceil((double) total / paging.size());
        return new PagedResponse<>(
            content, total, paging.page(), totalPages, paging.size(),
            paging.page() < totalPages,
            paging.page() > 1
        );
    }
}

// 서비스에서 사용
public PagedResponse<ReservationResponse> getReservationList(ReservationSearchRequest req) {
    List<ReservationResponse> rows = mapper.selectList(req);  // MyBatis
    int total = mapper.countList(req);
    return PagedResponse.of(rows, total, req.paging());
}
```

```xml
<!-- MyBatis에서 페이징 처리 -->
<select id="selectList" resultType="ReservationResponse">
    SELECT * FROM reservation
    WHERE 1=1
    <if test="status != null">AND status = #{status}</if>
    ORDER BY reg_dt ${paging.sortOrder}
    LIMIT #{paging.size} OFFSET #{paging.offset}
</select>
```

### 꼬리 질문 예상
- 대용량 데이터에서 OFFSET 방식의 문제점은?
- Cursor 기반 페이징으로 변경하려면?

---

## 질문 4: Swagger(OpenAPI) 문서화
> API 문서화를 어떻게 구성했나요?

### 핵심 답변 (3줄)
1. **springdoc-openapi** - 코드 기반 자동 문서 생성
2. **어노테이션 활용** - `@Tag`, `@Operation`, `@Parameter`로 설명 추가
3. **그룹핑** - 관리자/사용자 API를 태그로 구분

### 상세 설명
```java
@Tag(name = "[관리자] 예약 관리", description = "예약 조회, 등록, 수정, 취소 API")
@RestController
@RequestMapping("/api/reservations")
public class AdminReservationController {

    @Operation(
        summary = "예약 목록 조회", 
        description = "검색 조건에 따라 예약 목록을 조회합니다."
    )
    @GetMapping
    public ResponseEntity<PagedResponse<ReservationResponse>> getReservations(
            @Valid ReservationSearchRequest request
    ) {
        // ...
    }

    @Operation(
        summary = "예약 수동 등록", 
        description = "관리자가 예약을 수동으로 등록합니다."
    )
    @PostMapping
    public ResponseEntity<String> createReservation(
            @Valid @RequestBody ReservationCreateRequest request
    ) {
        // ...
    }
}
```

```yaml
# application.yml
springdoc:
  api-docs:
    path: /v3/api-docs
  swagger-ui:
    path: /swagger-ui.html
    tags-sorter: alpha
    operations-sorter: alpha
```

### 꼬리 질문 예상
- Swagger에서 인증(JWT)은 어떻게 테스트하나요?
- API 버저닝은 어떻게 처리하나요?

---

## 질문 5: SecurityHelper를 통한 인증 정보 접근
> 컨트롤러에서 현재 로그인한 관리자 정보를 어떻게 가져왔나요?

### 핵심 답변 (3줄)
1. **SecurityHelper 유틸 클래스** - SecurityContext에서 인증 정보 추출
2. **컨트롤러에서 주입** - 서비스 호출 시 adminId 전달
3. **서비스에서 직접 사용도 가능** - 필요시 SecurityHelper를 서비스에 주입

### 상세 설명
```java
@Component
@RequiredArgsConstructor
public class SecurityHelper {
    
    private final UserAdminRepository userAdminRepository;
    
    // 현재 로그인한 관리자 ID 반환
    public String getCurrentAdminUserId() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            throw new UnauthenticatedException("로그인이 필요합니다.");
        }
        return auth.getName();  // JWT에서 추출한 userId
    }
    
    // 현재 관리자 엔티티 반환 (nullable)
    public UserAdmin getCurrentAdminOrNull() {
        try {
            String userId = getCurrentAdminUserId();
            return userAdminRepository.findByUserId(userId).orElse(null);
        } catch (Exception e) {
            return null;
        }
    }
}

// 컨트롤러에서 사용
@RestController
@RequiredArgsConstructor
public class AdminReservationController {
    
    private final AdminReservationService service;
    private final SecurityHelper securityHelper;
    
    @PostMapping
    public ResponseEntity<String> create(@Valid @RequestBody ReservationCreateRequest req) {
        String adminId = securityHelper.getCurrentAdminUserId();
        service.createReservation(req, adminId);
        return ResponseEntity.ok("예약이 등록되었습니다.");
    }
}
```

### 꼬리 질문 예상
- `@AuthenticationPrincipal`을 사용하지 않은 이유는?
- 멀티 테넌시 환경에서 SecurityContext는 어떻게 관리하나요?

---

## 참고
- [[RESTful-API-설계-가이드]]
- [[Java-Record-활용법]]
- [[Spring-Security-인증-정보-접근]]
