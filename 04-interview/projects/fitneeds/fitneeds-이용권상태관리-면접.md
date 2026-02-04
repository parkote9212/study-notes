---
tags:
  - interview
  - jpa
  - entity
  - state
  - fitneeds
  - project
created: 2025-01-23
difficulty: 중
---

# Fitneeds - 이용권 상태 관리

## 질문
> 이용권의 여러 상태(ACTIVE, SUSPENDED, DELETED)를 어떻게 관리했나요?

## 핵심 답변 (3줄)
1. **Enum으로 상태 정의** - `PassStatusCd`에 상태별 메서드 제공 (isUsable, isModifiable 등)
2. **상태 전환 검증** - 엔티티 내부에서 불가능한 전환 차단 (DELETED → ACTIVE 등)
3. **비즈니스 메서드** - `deductCount()`, `restore()`, `topUp()` 등 의미 있는 메서드로 로직 캡슐화

## 상세 설명
```java
// 상태 Enum
public enum PassStatusCd {
    ACTIVE("활성"),
    SUSPENDED("정지"),
    DELETED("삭제");
    
    public boolean isUsable() { return this == ACTIVE; }
    public boolean isModifiable() { return this == ACTIVE || this == SUSPENDED; }
    public boolean isDeleted() { return this == DELETED; }
}

// 엔티티 - 상태 기반 비즈니스 로직
@Entity
public class UserPass {
    @Enumerated(EnumType.STRING)
    private PassStatusCd passStatusCode;
    private Integer remainingCount;
    
    public void deductCount(int amount) {
        if (!this.passStatusCode.isUsable()) {
            switch (this.passStatusCode) {
                case SUSPENDED -> throw new IllegalStateException("정지된 이용권");
                case DELETED -> throw new IllegalStateException("삭제된 이용권");
            }
        }
        if (this.remainingCount < amount) {
            throw new IllegalArgumentException("잔여 횟수 부족");
        }
        this.remainingCount -= amount;
    }
    
    public void updateStatus(String status) {
        PassStatusCd newStatus = PassStatusCd.valueOf(status);
        if (this.passStatusCode.isDeleted() && !newStatus.isDeleted()) {
            throw new IllegalStateException("삭제된 이용권은 상태 변경 불가");
        }
        this.passStatusCode = newStatus;
    }
}
```

## 꼬리 질문 예상
- 상태 전환 로직을 서비스가 아닌 엔티티에 둔 이유는?
- 삭제된 이용권 복구 기능은 어떻게 구현했나요?

## 참고
- [[fitneeds-이용권변동이력-면접]]
- [[fitneeds-JPA-MyBatis하이브리드-면접]]
