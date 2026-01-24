---
tags:
  - interview
  - jpa
  - mybatis
  - fitneeds
  - project
created: 2025-01-23
difficulty: 중
---

# Fitneeds - JPA MyBatis 하이브리드 사용이유

## 질문
> 하나의 서비스에서 JPA와 MyBatis를 동시에 사용한 이유는 무엇인가요?

## 핵심 답변 (3줄)
1. **CUD는 JPA** - 엔티티 메서드로 비즈니스 로직 캡슐화, Dirty Checking으로 자동 업데이트
2. **복잡 조회는 MyBatis** - 다중 테이블 조인, 동적 검색 조건은 XML Mapper가 직관적
3. **트랜잭션 공유** - 같은 DataSource 사용 시 `@Transactional`로 일관성 보장

## 상세 설명
```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AdminReservationService {
    
    private final ReservationRepository reservationRepository; // JPA (CUD)
    private final ReservationMapper reservationMapper;         // MyBatis (조회)

    // 목록 조회 - MyBatis
    public PagedResponse<ReservationResponse> getReservationList(ReservationSearchRequest req) {
        List<ReservationResponse> rows = reservationMapper.selectReservationList(req);
        int total = reservationMapper.countReservationList(req);
        return PagedResponse.of(rows, total, req.paging());
    }

    // 생성 - JPA
    @Transactional
    public void createReservation(ReservationCreateRequest request, String adminId) {
        User user = userRepository.findById(request.userId()).orElseThrow();
        Schedule schedule = scheduleRepository.findById(request.schdId()).orElseThrow();
        
        userPass.deductCount(1);
        schedule.increaseReservationCount();
        
        Reservation reservation = Reservation.create(user, schedule, userPass, adminId);
        reservationRepository.save(reservation);
    }
}
```

## 꼬리 질문 예상
- JPA와 MyBatis가 같은 트랜잭션에서 동작하는 것을 어떻게 보장하나요?
- N+1 문제는 어떻게 해결했나요?

## 참고
- [[JPA-MyBatis-하이브리드-패턴]]
- [[fitneeds-이용권상태관리-면접]]
