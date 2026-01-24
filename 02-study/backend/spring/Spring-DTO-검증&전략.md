---
tags: study, Spring, Validation, DTO
created: 2026-01-24
---

# DTO vs Entity 검증 전략

## 한 줄 요약
> DTO에서 Bean Validation으로 1차 검증, Controller에서 커스텀 검증 메서드 호출하여 DB 조회 전에 빠르게 실패(Fail-Fast) 처리

## 상세 설명

검증 위치에 따라 성능과 효율성이 달라집니다. DTO에서 검증하면 DB 부하 없이 빠른 실패가 가능하고, Entity에서 검증하면 데이터 무결성을 보장하지만 DB까지 갔다가 실패하여 비효율적입니다.

### 검증 레이어별 비교

| 검증 위치 | 시점 | 장점 | 단점 |
|----------|------|------|------|
| **DTO** | Service 호출 전 | DB 부하 없이 빠른 실패 | - |
| **Entity** | DB 저장 직전 | 데이터 무결성 보장 | DB까지 갔다가 실패 (비효율) |
| **Controller** | HTTP 요청 직후 | 명확한 검증 위치 | Controller 코드 복잡 |

### Bean Validation vs 커스텀 검증

**Bean Validation**: 단순 필수/길이/형식 검증에 적합
- `@NotNull`, `@Size`, `@Email` 등

**커스텀 검증 메서드**: 조건부 로직에 적합
- 특정 조건에 따라 필수 여부가 달라지는 경우
- 명시적 호출 필요

### BizSync 적용 사례

비용 결재(EXPENSE)일 때만 projectId, amount가 필수이고, 일반 결재(휴가, 업무)는 불필요합니다.

## 코드 예시

```java
// DTO 검증 (추천 ✅)
public record ApprovalCreateRequestDTO(
    @NotNull(message = "결재 유형은 필수입니다.")
    ApprovalType type,
    
    @DecimalMin(value = "0.01", message = "금액은 0보다 커야 합니다.")
    BigDecimal amount,
    
    Long projectId,
    
    @NotBlank(message = "결재 제목은 필수입니다.")
    @Size(max = 100, message = "제목은 100자 이하여야 합니다.")
    String title,
    
    @NotBlank(message = "결재 내용은 필수입니다.")
    String content,
    
    @NotEmpty(message = "결재자는 최소 1명 이상이어야 합니다.")
    List<Long> approverIds
) {
    // 커스텀 검증 메서드
    public void validateExpenseApproval() {
        if (type == ApprovalType.EXPENSE) {
            if (projectId == null) {
                throw new IllegalArgumentException(
                    "비용 결재는 프로젝트 ID가 필수입니다."
                );
            }
            if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
                throw new IllegalArgumentException(
                    "비용 결재는 유효한 금액이 필수입니다."
                );
            }
        }
    }
}

// Controller에서 호출
@RestController
@RequestMapping("/api/approvals")
public class ApprovalController {
    
    @PostMapping
    public ResponseEntity<?> createApproval(
        @Valid @RequestBody ApprovalCreateRequestDTO dto  // Bean Validation
    ) {
        dto.validateExpenseApproval();  // 커스텀 검증
        
        Long documentId = approvalService.createApproval(userId, dto);
        return ResponseEntity.ok(documentId);
    }
}
```

## 주의사항 / 함정

1. **중복 검증 방지**: DTO와 Entity에서 동일한 검증 로직 중복 작성 금지
2. **Bean Validation 자동 실행**: `@Valid`는 Spring이 자동 실행
3. **커스텀 메서드 명시적 호출**: 잊지 말고 호출해야 함
4. **검증 순서**: Bean Validation → 커스텀 검증 → Service 로직

## 관련 개념
- [[Bean-Validation]]
- [[레이어드-아키텍처]]
- [[Fail-Fast-원칙]]

## 면접 질문
1. DTO에서 검증하는 것과 Entity에서 검증하는 것의 차이는?
2. @Valid 어노테이션의 동작 원리는?
3. 검증 로직을 어느 계층에 두는 것이 좋은가?

## 참고 자료
- Jakarta Bean Validation 공식 문서
- 실무 프로젝트: BizSync
