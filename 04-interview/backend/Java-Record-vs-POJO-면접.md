---
tags: interview, java
created: 2026-01-16
difficulty: 상
---

# Java Record vs POJO (면접 Q&A)

## 질문 1
> JPA Entity에 Record를 사용할 수 없는 이유는?

## 핵심 답변 (3줄)
1. **프록시 생성 불가** - Record는 final class라 상속 불가 → 지연 로딩용 프록시 객체 생성 불가
2. **기본 생성자 없음** - JPA는 리플렉션으로 Entity 생성 시 기본 생성자 필요 (Record는 모든 필드를 받는 생성자만 있음)
3. **Setter 없음** - JPA가 DB 값을 주입할 때 Setter 필요 (Record는 불변이라 Setter 없음)

## 상세 설명

Record는 Java 14에서 도입된 불변 데이터 클래스로, 다음과 같은 특징이 있습니다:

1. **불변성 (final class)**: Record는 최상위 부모를 상속받을 수 없는 final class입니다. JPA는 지연 로딩(Lazy Loading)을 구현하기 위해 Entity의 서브클래스인 프록시 객체를 동적으로 생성합니다. Record의 final 특성 때문에 이 프록시 생성이 불가능합니다.

2. **기본 생성자 부재**: Record는 선언된 모든 필드를 받는 생성자만 자동으로 생성됩니다. 하지만 JPA는 Entity를 DB에서 조회할 때 리플렉션을 사용하여 기본 생성자(no-args constructor)를 호출합니다. 필드 값이 없는 빈 객체를 먼저 생성한 후, Setter를 통해 값을 주입하는 방식입니다.

3. **Setter 부재**: JPA의 핵심 메커니즘 중 하나는 조회한 엔티티를 업데이트할 때 필드에 직접 접근하거나 Setter를 사용하는 것입니다. Record는 완전히 불변이므로 Setter가 없고, 생성 후 필드값을 변경할 수 없습니다.

따라서 JPA Entity는 반드시 POJO를 사용해야 하며, `@NoArgsConstructor(access = AccessLevel.PROTECTED)`를 필수로 선언해야 합니다.

## 코드 예시
```java
// ❌ 불가능
@Entity
public record User(
    @Id Long userId,
    String email
) {}

// ✅ 올바른 방식 (POJO)
@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class User {
    @Id
    private Long userId;
    private String email;
}
```

## 꼬리 질문 예상
- "그럼 JPA DTO Projection에는 Record를 사용할 수 있나요?" → 예, 조회 전용 DTO Projection에는 가능합니다.
- "JPA 대신 MyBatis를 쓰면 Record를 쓸 수 있나요?" → 단순 조회는 가능하지만, 중첩 매핑에서는 제약이 있습니다.

## 참고
- [[Java-Record-vs-POJO]]
- JPA Specification: Persistent fields and properties
- Java 16: Records

---

## 질문 2
> MyBatis에서 Record 사용 시 제약사항은?

## 핵심 답변 (3줄)
1. **단순 조회는 가능** - 1:1 매핑 시 Record의 생성자로 직접 값 주입 가능
2. **중첩 매핑은 불가** - MyBatis `<collection>` 태그는 생성 후 동적으로 요소 추가 (Record는 생성 시점에 모든 값 확정 필요)
3. **해결책**: 1:N, N:M 조회는 POJO 사용 필수

## 상세 설명

MyBatis는 SQL 결과를 객체로 매핑할 때 두 가지 방식을 사용합니다:

1. **단순 매핑 (1:1 관계)**: 
   - MyBatis는 생성자에 SQL 결과값을 파라미터로 전달
   - Record의 생성자와 완벽하게 일치하므로 사용 가능

2. **중첩 매핑 (1:N, N:M 관계)**:
   - MyBatis는 먼저 부모 객체를 생성 (기본 생성자 호출)
   - 그 후 자식 컬렉션을 동적으로 추가
   - Record는 생성 시점에 모든 필드가 확정되어야 하므로, 나중에 컬렉션을 추가할 수 없음

예를 들어, ProjectBoard → KanbanColumn → Task 같은 2단계 중첩 구조에서는 반드시 POJO를 사용해야 합니다.

## 코드 예시
```java
// ✅ 단순 조회는 가능
public record UserDTO(Long userId, String email) {}

// ❌ 중첩 매핑은 불가
public record ProjectDTO(
    Long projectId,
    List<ColumnDTO> columns  // 동적 추가 불가!
) {}

// ✅ 중첩 매핑은 POJO 사용
@Data
public class ProjectDTO {
    private Long projectId;
    private List<ColumnDTO> columns;  // Setter로 동적 추가 가능
}
```

## 꼬리 질문 예상
- "JPA Projection과의 차이는?" → JPA는 쿼리 단계에서 조인해서 조회하므로 Record 가능, MyBatis는 런타임에 매핑하므로 차이 발생
- "해결책이 더 있나요?" → 별도의 쿼리로 분리하여 단순 조회로 만들 수 있습니다.

## 참고
- [[Java-Record-vs-POJO]]
- MyBatis resultMap documentation

---

## 질문 3
> Request DTO에 Record를 사용하는 이유는?

## 핵심 답변 (3줄)
1. **불변성 보장** - 유효성 검증 후 데이터가 변경되지 않음
2. **스레드 안전** - 여러 스레드에서 동시에 접근해도 안전
3. **명확한 의도** - "이 객체는 읽기 전용"을 코드로 표현

## 상세 설명

Request DTO는 클라이언트로부터 받은 입력값을 나타내는 객체입니다. 이 데이터는 다음과 같은 특성이 필요합니다:

1. **데이터 무결성**: 유효성 검증(Validation)을 통과한 후에는 값이 변경되면 안 됩니다. POJO를 사용하면 Setter가 있어서 검증 후에도 값을 변경할 수 있는 보안 위험이 있습니다.

2. **스레드 안전성**: 멀티스레드 환경에서 요청이 동시에 처리될 때, 불변 객체는 동기화 없이도 안전합니다. POJO는 Setter를 통한 값 변경이 가능해서 Race Condition이 발생할 수 있습니다.

3. **의도의 명확성**: Record를 사용하는 것 자체가 "이 객체는 변경되지 않음"을 개발자에게 명시적으로 전달합니다.

4. **간결성**: Getter, equals(), hashCode(), toString()이 자동으로 생성되어 보일러플레이트 코드가 줄어듭니다.

5. **Bean Validation 호환성**: Record의 생성자 파라미터에 직접 `@NotBlank`, `@Email` 등의 검증 애노테이션을 붙일 수 있습니다.

## 코드 예시
```java
// ✅ Request는 Record 권장
public record LoginRequestDTO(
    @NotBlank(message = "이메일 필수")
    @Email
    String email,
    
    @NotBlank(message = "비밀번호 필수")
    @Size(min = 8, max = 20)
    String password
) {}

// ❌ POJO는 Setter로 검증 후 값 변경 가능 (위험)
@Data
public class LoginRequestDTO {
    private String email;
    private String password;
    
    // 검증 후에도 setEmail() 호출 가능!
}
```

## 꼬리 질문 예상
- "Response DTO는 뭘 써야 하나요?" → 단순한 응답은 Record, 계산 로직이 필요한 복잡한 응답은 POJO
- "JDK 16 미만 환경에서는?" → Lombok의 @Value를 사용할 수 있습니다.

## 참고
- [[Java-Record-vs-POJO]]
- Spring Validation documentation

---

## 질문 4
> Record와 Lombok @Value의 차이는?

## 핵심 답변 (3줄)
1. **표준 vs 라이브러리** - Record는 Java 표준 (JDK 16+), @Value는 Lombok 외부 라이브러리
2. **Getter 이름** - Record는 email(), @Value는 getEmail()
3. **권장** - 새 프로젝트는 Record, 기존 프로젝트는 @Value와 혼용 가능

## 상세 설명

| 구분 | Record | Lombok @Value |
| --- | --- | --- |
| **도입 시점** | Java 16+ | 외부 라이브러리 |
| **생성 방식** | Java 컴파일러 | 애노테이션 프로세서 |
| **Getter 메서드** | `email()` | `getEmail()` |
| **의존성** | 없음 | Lombok 필요 |
| **직렬화** | Jackson 2.12+ | 기본 지원 |
| **명시성** | 명확함 | 암묵적 |

**Record의 장점**:
1. Java 표준 기능이므로 외부 의존성 없음
2. 컴파일 타임에 생성되므로 디버깅 용이
3. 명확한 불변성 표현
4. IDE 지원이 더 나음

**@Value의 장점**:
1. JDK 16 미만 환경에서도 사용 가능
2. 기존 Lombok 프로젝트와 일관성 유지
3. 다양한 커스터마이징 옵션

**결론**: 새로운 프로젝트를 시작한다면 Record를 사용하는 것이 모던하고 표준적인 방식입니다. 단, JDK 16 이하 환경이거나 기존에 Lombok을 많이 사용 중인 조직이라면 @Value를 계속 사용해도 무방합니다.

## 코드 예시
```java
// Lombok @Value
@Value
public class UserDTO {
    Long userId;        // private final로 자동 생성
    String email;
    String name;
    
    // getEmail(), getUserId() 등이 자동 생성됨
}

// Record (더 간결)
public record UserDTO(
    Long userId,
    String email,
    String name
) {
    // email(), userId() 등이 자동 생성됨
}
```

## 꼬리 질문 예상
- "Entity는 @Value로도 되나요?" → 아니요, Entity는 기본 생성자 필요하므로 POJO 사용 필수
- "Record는 Jackson에서 항상 작동하나요?" → 2.12 이상이어야 하고, 모듈을 추가해야 할 수 있습니다.

## 참고
- [[Java-Record-vs-POJO]]
- Java Records vs Lombok @Value
