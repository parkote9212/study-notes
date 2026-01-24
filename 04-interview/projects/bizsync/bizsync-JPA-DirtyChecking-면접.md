---
tags:
  - interview
  - jpa
  - dirty-checking
  - bizsync
  - project
created: 2025-01-23
difficulty: 상
---

# BizSync - JPA Dirty Checking

## 질문
> JPA의 Dirty Checking 메커니즘과 BizSync의 Project 엔티티에서 이를 활용한 update() 메서드를 설명해주세요.

## 핵심 답변 (3줄)
1. **Dirty Checking**은 영속 상태의 엔티티가 변경되면 트랜잭션 커밋 시점에 자동으로 UPDATE 쿼리를 실행하는 JPA의 기능입니다
2. 1차 캐시의 스냅샷과 현재 엔티티를 비교하여 변경된 필드만 감지하므로, 명시적인 update() 호출 없이도 DB에 반영됩니다
3. BizSync는 편의 메서드(project.update())로 엔티티를 변경하면 자동으로 UPDATE가 실행되어 코드가 간결해집니다

## 상세 설명
JPA의 영속성 컨텍스트는 엔티티를 관리할 때 최초 조회 시점의 상태를 스냅샷으로 저장합니다. 트랜잭션이 커밋될 때 JPA는 현재 엔티티와 스냅샷을 비교(Dirty Check)하여 변경사항이 있으면 UPDATE 쿼리를 자동 생성합니다.

**Dirty Checking의 동작 과정:**
1. 엔티티를 영속성 컨텍스트에 로딩 (SELECT)
2. 최초 상태를 스냅샷으로 저장
3. 비즈니스 로직에서 엔티티의 필드 변경
4. 트랜잭션 커밋 전 flush() 호출 시 변경 감지
5. 변경된 필드만 포함된 UPDATE 쿼리 자동 생성 및 실행

## 코드 예시
```java
// Project.java - 편의 메서드
@Entity
public class Project {
    public void update(String name, String description, 
                      LocalDate startDate, LocalDate endDate, 
                      BigDecimal totalBudget) {
        if (name != null && !name.isBlank()) {
            this.name = name;
        }
        if (description != null) {
            this.description = description;
        }
        // ... 나머지 필드 업데이트
    }
}

// ProjectService.java - Dirty Checking 활용
@Transactional
public void updateProject(Long projectId, ProjectUpdateRequestDTO dto) {
    Project project = projectRepository.findById(projectId)
        .orElseThrow();
    
    project.update(dto.name(), dto.description(), 
                  dto.startDate(), dto.endDate(), dto.totalBudget());
    
    // save() 호출 불필요! 트랜잭션 커밋 시 자동 UPDATE
}
```

## 꼬리 질문 예상
- @DynamicUpdate를 사용하면 어떤 차이가 있나요?
- Dirty Checking과 merge()의 차이는?

## 참고
- [[JPA-영속성컨텍스트]]
- [[bizsync-JPA-MyBatis하이브리드-면접]]
