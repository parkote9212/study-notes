---
tags:
  - interview
  - jpa
  - mybatis
  - spring
  - fitneeds
  - project
created: 2025-01-23
difficulty: 중
---

# Fitneeds - JPA+MyBatis 하이브리드 & 엔티티 설계 면접

## 질문 1: JPA와 MyBatis를 함께 사용한 이유
> 하나의 서비스에서 JPA와 MyBatis를 동시에 사용한 이유는 무엇인가요?

### 핵심 답변 (3줄)
1. **CUD는 JPA** - 엔티티 메서드로 비즈니스 로직 캡슐화, Dirty Checking으로 자동 업데이트
2. **복잡 조회는 MyBatis** - 다중 테이블 조인, 동적 검색 조건은 XML Mapper가 직관적
3. **트랜잭션 공유** - 같은 DataSource 사용 시 `@Transactional`로 일관성 보장

### 상세 설명
```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AdminReservationService {
    
    private final ReservationRepository reservationRepository; // JPA (CUD)
    private final ReservationMapper reservationMapper;         // MyBatis (조회)

    // 목록 조회 - MyBatis (동적 검색, 페이징, 조인 최적화)
    public PagedResponse<ReservationResponse> getReservationList(ReservationSearchRequest req) {
        List<ReservationResponse> rows = reservationMapper.selectReservationList(req);
        int total = reservationMapper.countReservationList(req);
        return PagedResponse.of(rows, total, req.paging());
    }

    // 생성 - JPA (엔티티 메서드, 연관관계)
    @Transactional
    public void createReservation(ReservationCreateRequest request, String adminId) {
        User user = userRepository.findById(request.userId()).orElseThrow();
        Schedule schedule = scheduleRepository.findById(request.schdId()).orElseThrow();
        UserPass userPass = userPassRepository.findById(request.passId()).orElseThrow();
        
        // 엔티티 비즈니스 로직
        userPass.deductCount(1);
        schedule.increaseReservationCount();
        
        Reservation reservation = Reservation.create(user, schedule, userPass, adminId);
        reservationRepository.save(reservation);
    }
}
```

### 꼬리 질문 예상
- JPA와 MyBatis가 같은 트랜잭션에서 동작하는 것을 어떻게 보장하나요?
- N+1 문제는 어떻게 해결했나요?

---

## 질문 2: 이용권(UserPass) 엔티티의 상태 관리
> 이용권의 여러 상태(ACTIVE, SUSPENDED, DELETED)를 어떻게 관리했나요?

### 핵심 답변 (3줄)
1. **Enum으로 상태 정의** - `PassStatusCd`에 상태별 메서드 제공 (isUsable, isModifiable 등)
2. **상태 전환 검증** - 엔티티 내부에서 불가능한 전환 차단 (DELETED → ACTIVE 등)
3. **비즈니스 메서드** - `deductCount()`, `restore()`, `topUp()` 등 의미 있는 메서드로 로직 캡슐화

### 상세 설명
```java
// 상태 Enum - 상태별 행동 정의
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
        // 1. 상태 검증
        if (!this.passStatusCode.isUsable()) {
            switch (this.passStatusCode) {
                case SUSPENDED -> throw new IllegalStateException("정지된 이용권입니다.");
                case DELETED -> throw new IllegalStateException("삭제된 이용권입니다.");
            }
        }
        
        // 2. 잔여 횟수 검증
        if (this.remainingCount < amount) {
            throw new IllegalArgumentException("잔여 횟수 부족");
        }
        
        this.remainingCount -= amount;
    }
    
    public void restore(int amount) {
        if (this.passStatusCode.isDeleted()) {
            throw new IllegalStateException("삭제된 이용권은 복구 불가");
        }
        this.remainingCount += amount;
    }
    
    public void updateStatus(String status) {
        PassStatusCd newStatus = PassStatusCd.valueOf(status);
        
        // 삭제된 이용권은 다른 상태로 전환 불가
        if (this.passStatusCode.isDeleted() && !newStatus.isDeleted()) {
            throw new IllegalStateException("삭제된 이용권은 상태 변경 불가");
        }
        this.passStatusCode = newStatus;
    }
}
```

### 꼬리 질문 예상
- 상태 전환 로직을 서비스가 아닌 엔티티에 둔 이유는?
- 삭제된 이용권 복구 기능은 어떻게 구현했나요?

---

## 질문 3: 이용권 변동 이력(PassLog) 관리
> 이용권 횟수 변동 시 이력을 어떻게 기록했나요?

### 핵심 답변 (3줄)
1. **변동 유형 Enum** - `USE`, `CANCEL`, `TRADE_SELL`, `TRADE_BUY` 등 유형별 분류
2. **처리자 기록** - `processedBy` 필드로 관리자/시스템 구분
3. **서비스 레이어에서 일관 처리** - 모든 변동 시 `savePassLog()` 호출

### 상세 설명
```java
// PassLog 엔티티
@Entity
public class PassLog extends BaseTimeEntity {
    
    @ManyToOne(fetch = FetchType.LAZY)
    private UserPass userPass;
    
    @Enumerated(EnumType.STRING)
    private PassLogChgTypeCd chgTypeCd;  // USE, CANCEL, TRADE_SELL, ADJUST...
    
    private int chgCnt;         // +3 또는 -1
    private String chgRsn;      // "관리자 예약 취소: 고객 요청"
    
    @ManyToOne(fetch = FetchType.LAZY)
    private UserAdmin processedBy;  // 처리한 관리자
}

// 서비스에서 일관된 이력 저장
@Service
public class AdminPassService {
    
    @Transactional
    public void cancelReservation(Long rsvId, ReservationCancelRequest req, String adminId) {
        Reservation reservation = findById(rsvId);
        
        // 1. 예약 취소
        reservation.cancel(req.cnclRsn(), adminId);
        
        // 2. 이용권 복구
        UserPass userPass = reservation.getPass();
        userPass.restore(1);
        
        // 3. 이력 저장 (핵심!)
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

### 꼬리 질문 예상
- 이력 테이블이 커지면 어떻게 관리하나요? (파티셔닝, 아카이빙)
- 이벤트 소싱 패턴과의 차이점은?

---

## 질문 4: 예약-스케줄-이용권 간 검증 로직
> 예약 생성 시 다양한 검증(종목 일치, 중복 예약, 잔여 횟수)을 어떻게 처리했나요?

### 핵심 답변 (3줄)
1. **검증 메서드 분리** - `validateSportMatch()`, `validateDuplicateReservation()` 등 책임 분리
2. **엔티티 내부 검증** - 잔여 횟수, 상태 검증은 엔티티 메서드에서 처리
3. **트랜잭션 내 일관성** - 검증 → 차감 → 저장 순서로 원자적 처리

### 상세 설명
```java
@Transactional
public void createReservation(ReservationCreateRequest request, String adminId) {
    // 1. 엔티티 조회
    User user = userRepository.findById(request.userId()).orElseThrow();
    Schedule schedule = scheduleRepository.findById(request.schdId()).orElseThrow();
    UserPass userPass = userPassRepository.findById(request.passId()).orElseThrow();
    
    // 2. 비즈니스 검증 (서비스 레벨)
    validateSportMatch(userPass, schedule);           // 종목 일치
    validateDuplicateReservation(user.getUserId(), schedule);  // 중복 예약
    
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
        throw new IllegalArgumentException(
            "이용권 종목(" + pass.getSport().getSportNm() + ")과 " +
            "수업 종목(" + schedule.getProgram().getSportType().getSportNm() + ")이 불일치");
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

### 꼬리 질문 예상
- 동시성 이슈(같은 이용권으로 동시 예약)는 어떻게 방지하나요?
- 검증 로직을 별도 Validator 클래스로 분리하면 어떤 장점이 있나요?

---

## 질문 5: 이용권 거래(P2P) 처리 로직
> 사용자 간 이용권 거래 완료/취소 시 티켓 이동을 어떻게 구현했나요?

### 핵심 답변 (3줄)
1. **거래 완료** - 판매자 차감(`deductCount`) + 구매자 추가(`topUp` 또는 신규 생성)
2. **거래 취소** - 구매자 회수(`deductCount`) + 판매자 복구(`restore`)
3. **양방향 이력** - 판매자/구매자 각각 PassLog 기록 (TRADE_SELL, TRADE_BUY, TRADE_CANCEL)

### 상세 설명
```java
@Transactional
public void updateTradeStatus(Long id, String status, String adminId) {
    PassTradeTransaction trade = findTradeById(id);
    String oldStatus = trade.getSttsCd();
    
    trade.updateStatus(status);
    
    if ("COMPLETED".equals(status) && !"COMPLETED".equals(oldStatus)) {
        // 거래 성공: 판매자 → 구매자 이동
        processTradeCompletion(trade, adminId);
    } else if ("CANCELED".equals(status) && "COMPLETED".equals(oldStatus)) {
        // 완료된 거래 취소: 롤백
        processTradeRollback(trade, adminId);
    }
}

private void processTradeCompletion(PassTradeTransaction trade, String adminId) {
    int qty = trade.getBuyQty();
    UserPass sellerPass = trade.getPost().getUserPass();
    
    // 1) 판매자 차감
    sellerPass.deductCount(qty);
    savePassLog(sellerPass, TRADE_SELL, -qty, 
        "거래완료 판매(거래ID:" + trade.getTradeId() + ")");
    
    // 2) 구매자 추가 (기존 이용권 있으면 topUp, 없으면 신규 생성)
    String buyerId = trade.getBuyerUser().getUserId();
    Long sportId = sellerPass.getSport().getSportId();
    
    UserPass buyerPass = userPassRepository.findByUserIdAndSportId(buyerId, sportId)
        .orElseGet(() -> createNewPassForBuyer(trade, sellerPass, qty));
    
    if (buyerPass.getPassId() != null) {
        buyerPass.topUp(qty);
    }
    
    userPassRepository.save(buyerPass);
    savePassLog(buyerPass, TRADE_BUY, qty, 
        "거래완료 구매(거래ID:" + trade.getTradeId() + ")");
}
```

### 꼬리 질문 예상
- 거래 중간에 판매자가 이용권을 사용해버리면 어떻게 되나요?
- 결제 시스템과 연동 시 보상 트랜잭션(Saga 패턴)은 어떻게 구현하나요?

---

## 참고
- [[JPA-MyBatis-하이브리드-패턴]]
- [[엔티티-상태-관리-패턴]]
- [[이벤트-소싱-vs-이력-테이블]]
