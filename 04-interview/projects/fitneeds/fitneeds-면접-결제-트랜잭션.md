---
tags: interview, transaction, payment, spring, fitneeds, project
created: 2025-01-23
difficulty: 중
---

# Fitneeds - 결제 & 트랜잭션 처리 면접

## 질문 1: 결제 + 예약 트랜잭션 설계
> 결제와 예약이 하나의 트랜잭션으로 처리되어야 하는 이유와 구현 방법은?

### 핵심 답변 (3줄)
1. **원자성 보장** - 결제 성공 시에만 예약 생성, 둘 중 하나 실패 시 전체 롤백
2. **@Transactional** - 서비스 메서드에 선언하여 하나의 트랜잭션으로 묶음
3. **검증 → 처리 → 저장** 순서로 비즈니스 로직 구성

### 상세 설명
```java
@Service
@RequiredArgsConstructor
public class PaymentService {

    @Transactional  // 하나의 트랜잭션으로 묶음
    public Payment createAndProcessPayment(PaymentRequestDto requestDto) {
        // 1. 기초 데이터 조회 & 검증
        User user = userRepository.findByUserId(requestDto.getUserId())
                .orElseThrow(() -> new NoSuchElementException("사용자 없음"));
        
        Schedule schedule = scheduleRepository.findById(requestDto.getSchdId())
                .orElseThrow(() -> new NoSuchElementException("스케줄 없음"));
        
        // 2. 중복 예약 체크
        boolean isAlreadyReserved = reservationRepository
            .existsByUser_UserIdAndSchedule_SchdIdAndSttsCd(
                user.getUserId(), schedule.getSchdId(), RsvSttsCd.CONFIRMED);
        if (isAlreadyReserved) {
            throw new IllegalStateException("이미 예약된 스케줄입니다.");
        }
        
        // 3. 이용권 결제 처리 (있는 경우)
        UserPass usedUserPass = null;
        if (requestDto.getPayMethod() == PaymentPayMethod.PASS) {
            usedUserPass = userPassService.usePassForR(requestDto.getUserPassId(), "스케줄 예약");
        }
        
        // 4. Payment 저장
        Payment payment = Payment.builder()
                .user(user)
                .payTypeCd(PaymentPayTypeCd.SCHEDULE_RESERVATION)
                .payAmt(requestDto.getAmount())
                .sttsCd(PaymentSttsCd.PAID)
                .build();
        Payment savedPayment = paymentRepository.save(payment);
        
        // 5. Reservation 저장 (결제 성공 후에만 실행)
        reservationService.createReservation(user, schedule, branch, usedUserPass, ...);
        
        return savedPayment;
        // 여기서 예외 발생 시 전체 롤백
    }
}
```

### 꼬리 질문 예상
- 외부 PG 결제 API 호출 시 트랜잭션은 어떻게 처리하나요?
- `@Transactional`의 기본 전파 속성(propagation)은?

---

## 질문 2: 중복 예약 방지 로직
> 동일 시간대 중복 예약을 어떻게 방지했나요?

### 핵심 답변 (3줄)
1. **2단계 검증** - 동일 스케줄 중복 + 동일 시간대 중복 체크
2. **상태 기반 필터링** - CONFIRMED 상태인 예약만 중복 체크 대상
3. **DB 레벨 검증** - Repository 쿼리로 원자적 확인

### 상세 설명
```java
// A. 동일 스케줄 중복 예약 체크
boolean isAlreadyReserved = reservationRepository
    .existsByUser_UserIdAndSchedule_SchdIdAndSttsCd(
        user.getUserId(), 
        schedule.getSchdId(), 
        RsvSttsCd.CONFIRMED  // 확정된 예약만 체크
    );
if (isAlreadyReserved) {
    throw new IllegalStateException("이미 예약된 스케줄입니다.");
}

// B. 동일 시간대 중복 예약 체크 (다른 스케줄이라도)
boolean isTimeOverlapping = reservationRepository
    .existsByUser_UserIdAndRsvDtAndRsvTimeAndSttsCd(
        user.getUserId(), 
        rsvDate, 
        rsvTime, 
        RsvSttsCd.CONFIRMED
    );
if (isTimeOverlapping) {
    throw new IllegalStateException("해당 시간에 이미 다른 예약이 있습니다.");
}
```

**동시성 이슈 해결:**
```java
// 방법 1: 비관적 락 (SELECT FOR UPDATE)
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT r FROM Reservation r WHERE r.user.userId = :userId AND r.rsvDt = :date")
List<Reservation> findWithLock(@Param("userId") String userId, @Param("date") LocalDate date);

// 방법 2: Unique 제약조건
// user_id + schedule_id + stts_cd 복합 유니크 인덱스
```

### 꼬리 질문 예상
- 두 사용자가 동시에 같은 스케줄을 예약하면 어떻게 되나요?
- 비관적 락과 낙관적 락의 차이는?

---

## 질문 3: 결제 타입별 분기 처리
> 이용권 결제(PASS)와 카드 결제(CARD)를 어떻게 분기 처리했나요?

### 핵심 답변 (3줄)
1. **PayMethod Enum** - 결제 수단을 열거형으로 타입 안전하게 관리
2. **조건부 검증** - 결제 수단에 따라 필수값과 금액 검증 분기
3. **이용권 차감 로직** - PASS 결제 시 UserPassService로 이용권 사용 처리

### 상세 설명
```java
// 결제 수단별 분기 처리
if (requestDto.getPayMethod() == PaymentPayMethod.PASS) {
    // 이용권 결제
    if (requestDto.getUserPassId() == null) {
        throw new IllegalArgumentException("이용권 결제 시 userPassId는 필수입니다.");
    }
    
    // 이용권 차감
    usedUserPass = userPassService.usePassForR(
        requestDto.getUserPassId(), 
        "스케줄 예약(" + schedule.getSchdId() + ")"
    );
    
    // 금액 검증 (이용권 결제는 0원)
    if (requestDto.getAmount().compareTo(BigDecimal.ZERO) != 0) {
        throw new IllegalArgumentException("이용권 결제 시 금액은 0원이어야 합니다.");
    }
} else {
    // 카드/현금 결제
    if (requestDto.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
        throw new IllegalArgumentException("결제 금액은 0보다 커야 합니다.");
    }
}
```

```java
// PayMethod Enum
public enum PaymentPayMethod {
    CARD,    // 카드 결제
    CASH,    // 현금 결제
    PASS     // 이용권 결제
}

// PayTypeCd Enum - 결제 유형
public enum PaymentPayTypeCd {
    SCHEDULE_RESERVATION,  // 스케줄 예약
    PASS_TRADE,           // 이용권 거래
    PASS_PURCHASE         // 이용권 구매
}
```

### 꼬리 질문 예상
- 전략 패턴(Strategy Pattern)으로 리팩토링한다면?
- 새로운 결제 수단이 추가되면 어떻게 확장하나요?

---

## 질문 4: 이용권 거래 결제 분리
> 일반 예약 결제와 이용권 거래 결제를 분리한 이유는?

### 핵심 답변 (3줄)
1. **단일 책임 원칙** - 각 결제 유형별로 독립적인 비즈니스 로직
2. **참조 관계 차이** - 예약은 Schedule 참조, 거래는 Transaction 참조
3. **확장성** - 거래 결제에만 수수료 로직 추가 등 독립적 변경 가능

### 상세 설명
```java
/**
 * 이용권 거래 전용 결제 생성 (PASS_TRADE)
 * - 예약/이용권 구매 로직과 분리
 * - 결제 생성 책임만 가짐
 */
@Transactional
public Payment createPassTradePayment(
        String buyerId,
        BigDecimal amount,
        Long refTransactionId  // 거래 ID 참조
) {
    User buyer = userRepository.findByUserId(buyerId)
            .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));

    Payment payment = Payment.builder()
            .user(buyer)
            .payTypeCd(PaymentPayTypeCd.PASS_TRADE)  // 거래 결제 타입
            .targetId(refTransactionId)              // 거래 ID 참조
            .payAmt(amount)
            .payMethod(PaymentPayMethod.CARD)
            .sttsCd(PaymentSttsCd.PAID)
            .regDt(LocalDateTime.now())
            .build();

    return paymentRepository.save(payment);
}
```

**Payment 엔티티의 유연한 참조 구조:**
```java
@Entity
public class Payment {
    @Enumerated(EnumType.STRING)
    private PaymentPayTypeCd payTypeCd;  // 결제 유형
    
    private Long targetId;      // 참조 대상 ID (Schedule, Transaction 등)
    private String targetName;  // 참조 대상 이름 (프로그램명 등)
}
```

### 꼬리 질문 예상
- `targetId`로 다형적 참조를 하는 것의 장단점은?
- JPA 상속 전략으로 결제 유형을 분리했다면?

---

## 질문 5: 트랜잭션 롤백 시나리오
> 결제 처리 중 예외 발생 시 롤백은 어떻게 동작하나요?

### 핵심 답변 (3줄)
1. **RuntimeException** - 기본적으로 unchecked 예외 시 자동 롤백
2. **전체 원자성** - Payment, Reservation, UserPass 변경 모두 롤백
3. **예외 전파** - 컨트롤러로 예외가 전달되어 에러 응답 반환

### 상세 설명
```java
@Transactional
public Payment createAndProcessPayment(PaymentRequestDto requestDto) {
    // 1. User 조회 → 실패 시 NoSuchElementException (롤백)
    User user = userRepository.findByUserId(requestDto.getUserId())
            .orElseThrow(() -> new NoSuchElementException("사용자 없음"));
    
    // 2. 중복 예약 체크 → 실패 시 IllegalStateException (롤백)
    if (isAlreadyReserved) {
        throw new IllegalStateException("이미 예약된 스케줄");
    }
    
    // 3. 이용권 차감 (상태 변경) → 여기서 예외 시 롤백
    usedUserPass = userPassService.usePassForR(...);
    
    // 4. Payment 저장 → 여기서 예외 시 롤백
    Payment savedPayment = paymentRepository.save(payment);
    
    // 5. Reservation 저장 → 여기서 예외 시 전체 롤백!
    //    (Payment, UserPass 변경도 함께 롤백)
    reservationService.createReservation(...);
    
    return savedPayment;
}
```

**명시적 롤백 설정:**
```java
// Checked Exception도 롤백하려면
@Transactional(rollbackFor = Exception.class)
public Payment createPayment(...) throws IOException {
    // IOException 발생해도 롤백
}

// 특정 예외는 롤백 안함
@Transactional(noRollbackFor = {CustomException.class})
public void process() {
    // CustomException은 롤백 안함
}
```

### 꼬리 질문 예상
- Checked Exception은 왜 기본적으로 롤백되지 않나요?
- `@Transactional`이 private 메서드에서 동작하지 않는 이유는?

---

## 참고
- [[Spring-트랜잭션-전파]]
- [[JPA-동시성-제어]]
- [[fitneeds-면접-JPA-MyBatis-엔티티]]
