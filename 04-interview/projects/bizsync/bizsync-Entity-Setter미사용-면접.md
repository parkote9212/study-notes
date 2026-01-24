---
tags:
  - interview
  - jpa
  - entity
  - setter
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - Entity Setter 미사용 패턴

## 질문
> 엔티티에 Setter를 사용하지 않은 이유와 대안은 무엇인가요?

## 핵심 답변 (3줄)
1. **불변성 보장** - 의도치 않은 상태 변경 방지, 도메인 무결성 유지
2. **의미 있는 메서드** - `spendBudget()`, `complete()` 등 비즈니스 의도를 드러내는 메서드 제공
3. **빌더 패턴** - 생성 시점에만 값 설정, 이후 변경은 명시적 메서드로만

## 상세 설명
```java
@Entity
@Getter  // Setter 없음!
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Builder
public class Project {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long projectId;
    private String name;
    private BigDecimal totalBudget;
    private BigDecimal usedBudget;
    
    // ❌ Setter 대신 → ✅ 비즈니스 메서드
    public void spendBudget(BigDecimal amount) {
        BigDecimal expected = this.usedBudget.add(amount);
        if (this.totalBudget.compareTo(expected) < 0) {
            throw new IllegalStateException("예산 초과!");
        }
        this.usedBudget = expected;
    }
    
    public void complete() {
        this.status = ProjectStatus.COMPLETED;
    }
    
    public void update(String name, String description, ...) {
        if (name != null && !name.isBlank()) {
            this.name = name;
        }
    }
}
```

## 꼬리 질문 예상
- `@NoArgsConstructor(access = PROTECTED)`를 사용하는 이유는?
- 업데이트 메서드에서 null 체크하는 이유는?

## 참고
- [[JPA-엔티티-설계-가이드]]
- [[도메인주도설계-DDD]]
