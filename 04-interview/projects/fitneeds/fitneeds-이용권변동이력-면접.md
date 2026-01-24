---
tags:
  - interview
  - entity
  - history
  - fitneeds
  - project
created: 2025-01-23
difficulty: 중
---

# Fitneeds - 이용권 변동 이력 관리

## 질문
> 이용권 횟수 변동 시 이력을 어떻게 기록했나요?

## 핵심 답변 (3줄)
1. **변동 유형 Enum** - `USE`, `CANCEL`, `TRADE_SELL`, `TRADE_BUY` 등 유형별 분류
2. **처리자 기록** - `processedBy` 필드로 관리자/시스템 구분
3. **서비스 레이어에서 일관 처리** - 모든 변동 시 `savePassLog()` 호출

## 상세 설명
```java
// PassLog 엔티티
@Entity
public class PassLog extends BaseTimeEntity {
    @ManyToOne(fetch = FetchType.LAZY)
    private UserPass userPass;
    
    @Enumerated(EnumType.STRING)
    private PassLogChgTypeCd chgTypeCd;  // USE, CANCEL, TRADE_SELL...
    
    private int chgCnt;         // +3 또는 -1
    private String chgRsn;      // "관리자 예약 취소: 고객 요청"
    
    @ManyToOne(fetch = FetchType.LAZY)
    private UserAdmin processedBy;
}

// 서비스에서 일관된 이력 저장
@Service
public class AdminPassService {
    @Transactional
    public void cancelReservation(Long rsvId, ReservationCancelRequest req, String adminId) {
        Reservation reservation = findById(rsvId);
        reservation.cancel(req.cnclRsn(), adminId);
        
        UserPass userPass = reservation.getPass();
        userPass.restore(1);
        
        // 이력 저장
        savePassLog(userPass, "CANCEL", 1, 
            "관리자 예약 취소: " + req.cnclRsn(), adminId);
    }
    
    private void savePassLog(UserPass userPass, String type, int amount, 
                            String reason, String adminId) {
        UserAdmin admin = userAdminRepository.findByUserId(adminId).orElseThrow();
        PassLog log = PassLog.builder()
            .userPass(userPass)
            .chgTypeCd(PassLogChgTypeCd.valueOf(type))
            .chgCnt(amount)
            .chgRsn(reason)
            .processedBy(admin)
            .build();
        passLogRepository.save(log);
    }
}
```

## 꼬리 질문 예상
- 이력 테이블이 커지면 어떻게 관리하나요? (파티셔닝, 아카이빙)
- 이벤트 소싱 패턴과의 차이점은?

## 참고
- [[이벤트-소싱-vs-이력-테이블]]
- [[fitneeds-예약검증로직-면접]]
