---
tags:
  - interview
  - transaction
  - payment
  - spring
  - fitneeds
  - project
created: 2025-01-23
difficulty: 중
---

# Fitneeds - 결제 예약 트랜잭션

## 질문
> 결제와 예약이 하나의 트랜잭션으로 처리되어야 하는 이유와 구현 방법은?

## 핵심 답변 (3줄)
1. **원자성 보장** - 결제 성공 시에만 예약 생성, 둘 중 하나 실패 시 전체 롤백
2. **@Transactional** - 서비스 메서드에 선언하여 하나의 트랜잭션으로 묶음
3. **검증 → 처리 → 저장** 순서로 비즈니스 로직 구성

## 상세 설명
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
        
        // 3. 이용권 결제 처리
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

## 꼬리 질문 예상
- 외부 PG 결제 API 호출 시 트랜잭션은 어떻게 처리하나요?
- `@Transactional`의 기본 전파 속성(propagation)은?

## 참고
- [[Spring-트랜잭션-전파]]
- [[fitneeds-중복예약방지-면접]]
