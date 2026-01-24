---
tags:
  - interview
  - JPA
  - 영속성컨텍스트
created: 2026-01-23
difficulty: 최상
---

# JPA 영속성 컨텍스트

## 질문
> 영속성 컨텍스트란 무엇이고, 왜 필요한지 설명하세요.

## 핵심 답변 (3줄)
1. 영속성 컨텍스트는 엔티티를 영구 저장하기 전에 메모리에서 관리하는 1차 캐시 공간입니다.
2. 동일 트랜잭션 내에서 같은 엔티티는 항상 동일한 객체(==)를 반환하여 동일성을 보장하고, 변경 감지로 자동 UPDATE를 제공합니다.
3. 1차 캐시, 쓰기 지연, 변경 감지, 지연 로딩 등의 기능을 통해 성능 최적화와 객체 지향적인 데이터 관리가 가능합니다.

## 상세 설명

### 영속성 컨텍스트의 역할
- **1차 캐시**: 같은 트랜잭션 내에서 동일한 엔티티 조회 시 DB 접근 없이 캐시에서 반환
- **동일성 보장**: 같은 ID의 엔티티는 항상 ==로 비교 가능
- **변경 감지(Dirty Checking)**: 엔티티 수정 시 자동으로 UPDATE SQL 생성
- **쓰기 지연**: INSERT/UPDATE를 모아서 한 번에 실행

### 엔티티 생명주기
1. **비영속(Transient)**: new로 생성만 한 상태, JPA가 모름
2. **영속(Managed)**: persist()로 영속성 컨텍스트에 저장된 상태
3. **준영속(Detached)**: 영속성 컨텍스트에서 분리된 상태
4. **삭제(Removed)**: 삭제 예정 상태

## 코드 예시

```java
@Transactional
public void example() {
    // 1. 비영속
    User user = new User("John");
    
    // 2. 영속 (1차 캐시에 저장)
    em.persist(user);
    
    // 3. 1차 캐시에서 조회 (SQL 실행 X)
    User found = em.find(User.class, user.getId());
    System.out.println(user == found);  // true (동일성 보장)
    
    // 4. 변경 감지
    user.changeName("Jane");  // UPDATE 자동 생성
    
    // 5. 트랜잭션 커밋 시 SQL 실행
}
```

## 꼬리 질문 예상
- 변경 감지(Dirty Checking)는 어떻게 작동하나요?
- 준영속 상태의 엔티티를 다시 영속 상태로 만들려면 어떻게 하나요?
- flush()와 commit()의 차이는 무엇인가요?
- 영속성 컨텍스트의 생명주기는 언제까지인가요?

## 참고
- [[JPA-영속성컨텍스트-엔티티생명주기]]
- [[JPA-영속성컨텍스트-변경감지]]
