# JPA-도메인모델-Setter금지패턴

🏷️기술 카테고리: Design Pattern, JPA
💡핵심키워드: #JPA, #도메인주도설계, #캡슐화, #클린코드
💼 면접 빈출도: 상

# 1. Abstract: 핵심 요약

엔티티에서 Setter를 금지하고 **의미 있는 비즈니스 메서드**를 사용하는 것은 Modern JPA의 표준 관례입니다.

**핵심 원칙**:
- Setter는 변경의 의도를 설명하지 못함
- 비즈니스 메서드로 무결성 보장
- 도메인 모델 패턴 구현

# 2. 왜 Setter를 쓰면 안 되는가?

## 2.1 수정의 "의도(Intent)" 불명확

```java
// ❌ Setter 방식
ticket.setStatus("EXP");
// 기간이 지나서? 관리자가 강제 정지? 알 수 없음

// ✅ 메서드 방식
ticket.expire();  // 또는 ticket.suspendByAdmin();
// 코드 자체가 비즈니스 언어
```

## 2.2 객체의 무결성과 캡슐화

Setter는 외부에서 아무나 필드 값을 바꿀 수 있게 "무방비 상태"로 객체를 노출시킵니다.

```java
// ❌ Setter 사용 (위험)
int current = ticket.getRemainingCount();
ticket.setRemainingCount(current - 1);
// 실수로 -100을 넣어도 막을 방법 없음

// ✅ 비즈니스 메서드 (안전)
public void use() {
    if (this.remainingCount <= 0) {
        throw new IllegalStateException("잔여 횟수가 없습니다.");
    }
    this.remainingCount--;
    
    if (this.remainingCount == 0) {
        this.status = TicketStatus.EXHAUSTED;
    }
}
```

## 2.3 "도메인 모델 패턴" 구현

데이터와 로직이 한곳에 모여 있는 것을 **도메인 모델 패턴**이라고 합니다.

**과거 방식**:
- 엔티티에 데이터만 (Getter/Setter)
- 서비스 클래스에서 모든 계산
- 서비스 코드가 수천 줄, 중복 발생

**현대 방식 (Rich Domain Model)**:
- 엔티티가 스스로의 상태를 변경
- 서비스는 엔티티에게 일을 시키기만 (Thin Service)
- 비즈니스 로직이 엔티티 단위로 격리, 단위 테스트 용이

# 3. 실무 적용 예시

```java
// [Before] 서비스에 로직 (지양)
@Transactional
public void useTicket(Long id) {
    MemberTicket ticket = repository.findById(id).orElseThrow();
    
    if (ticket.getRemainingCount() <= 0) {
        throw new IllegalStateException("잔여 횟수 부족");
    }
    ticket.setRemainingCount(ticket.getRemainingCount() - 1);
}

// [After] 엔티티에 로직 (권장)
// Entity
public void use() {
    if (this.remainingCount <= 0) {
        throw new IllegalStateException("잔여 횟수가 없습니다.");
    }
    this.remainingCount--;
}

// Service
@Transactional
public void useTicket(Long id) {
    MemberTicket ticket = repository.findById(id).orElseThrow();
    ticket.use();  // 서비스는 명령만
}
```

# 4. 주의: 엔티티에 넣으면 안 되는 로직

모든 것을 엔티티에 넣을 수는 없습니다. 아래는 **Service**에 두어야 합니다:

1. **Repository 호출**: 엔티티는 다른 엔티티를 조회할 수 없음
2. **외부 API 호출**: 이메일 발송, 결제 API
3. **여러 엔티티의 복합 조율**: 순서 제어 로직

# 5. 가이드라인

1. Lombok `@Setter`는 엔티티에서 절대 사용 금지
2. 수정이 필요한 필드는 **비즈니스 이름(Verb)**이 담긴 메서드 생성
3. 메서드 안에서 **값의 검증(Validation)** 로직 포함

# 6. 서비스 vs 엔티티 비교

| 항목 | 트랜잭션 스크립트 | 도메인 모델 |
| --- | --- | --- |
| 엔티티 역할 | 단순 데이터 바구니 | 비즈니스 로직 포함 |
| 서비스 역할 | 모든 로직 수행 (Fat) | 명령만 전달 (Thin) |
| 단위 테스트 | 어려움 | 쉬움 |
| 코드 중복 | 발생하기 쉬움 | 거의 없음 |

**작성일**: 2026-01-23
**면접 빈출도**: ⭐⭐⭐⭐ (상)
