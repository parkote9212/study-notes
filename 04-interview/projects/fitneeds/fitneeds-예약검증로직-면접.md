---
tags:
  - interview
  - validation
  - business-logic
  - fitneeds
  - project
created: 2025-01-23
difficulty: 중
---

# Fitneeds - 예약 검증 로직

## 질문
> 예약 생성 시 다양한 검증(종목 일치, 중복 예약, 잔여 횟수)을 어떻게 처리했나요?

## 핵심 답변 (3줄)
1. **검증 메서드 분리** - `validateSportMatch()`, `validateDuplicateReservation()` 등 책임 분리
2. **엔티티 내부 검증** - 잔여 횟수, 상태 검증은 엔티티 메서드에서 처리
3. **트랜잭션 내 일관성** - 검증 → 차감 → 저장 순서로 원자적 처리

## 상세 설명
```java
@Transactional
public void createReservation(ReservationCreateRequest request, String adminId) {
    // 1. 엔티티 조회
    User user = userRepository.findById(request.userId()).orElseThrow();
    Schedule schedule = scheduleRepository.findById(request.schdId()).orElseThrow();
    UserPass userPass = userPassRepository.findById(request.passId()).orElseThrow();
    
    // 2. 비즈니스 검증 (서비스 레벨)
    validateSportMatch(userPass, schedule);
    validateDuplicateReservation(user.getUserId(), schedule);
    
    // 3. 이용권 차감 (엔티티 레벨 - 잔여 횟수, 상태 검증 포함)
    userPass.deductCount(1);
    
    // 4. 스케줄 예약 수 증가
    schedule.increaseReservationCount();
    
    // 5. 예약 생성
    Reservation reservation = Reservation.create(user, schedule, userPass, adminId);
    reservationRepository.save(reservation);
    
    // 6. 이력 저장
    savePassLog(userPass, "USE", -1, "관리자 예약 등록", adminId);
}

private void validateSportMatch(UserPass pass, Schedule schedule) {
    Long passSportId = pass.getSport().getSportId();
    Long programSportId = schedule.getProgram().getSportType().getSportId();
    
    if (!passSportId.equals(programSportId)) {
        throw new IllegalArgumentException("이용권 종목과 수업 종목 불일치");
    }
}

private void validateDuplicateReservation(String userId, Schedule schedule) {
    int count = reservationMapper.countDuplicateReservation(
        userId, schedule.getStrtDt(), schedule.getStrtTm(), "RESERVED");
    
    if (count > 0) {
        throw new IllegalStateException("해당 시간에 이미 예약 존재");
    }
}
```

## 꼬리 질문 예상
- 동시성 이슈(같은 이용권으로 동시 예약)는 어떻게 방지하나요?
- 검증 로직을 별도 Validator 클래스로 분리하면 어떤 장점이 있나요?

## 참고
- [[비즈니스-검증-패턴]]
- [[fitneeds-결제트랜잭션-면접]]
