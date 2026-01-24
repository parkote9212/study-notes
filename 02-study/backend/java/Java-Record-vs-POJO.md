---
tags:
  - study
  - jpa
  - java
  - 리플렉션
  - 불변성
created: 2026-01-16
difficulty: 상
---

# Java Record vs POJO (MyBatis, JPA 관점)

# 1. Abstract: 핵심 요약

> **Record vs POJO**는 Java 14에 도입된 Record와 전통적인 POJO(Plain Old Java Object)의 선택 문제입니다. MyBatis와 JPA에서 각각 다른 특성과 제약이 있으며, 사용 목적에 따라 적절히 선택해야 합니다.
> 

**핵심 원칙**:

- JPA Entity는 **POJO만 사용 가능** (Record 불가)
- MyBatis는 **Record 사용 가능**하지만 중첩 매핑 시 제약
- Request DTO는 **Record 적합** (불변성 보장)
- Response DTO는 **상황에 따라 선택**

---

# 2. Record vs POJO 기본 개념

## 2.1 Record란?

**정의**: Java 14에 도입된 불변 데이터 클래스 (Java 16에서 정식 기능)

```java
// Record 방식
public record LoginRequestDTO(
    @NotBlank String email,
    @NotBlank String password
) {}

// 자동 생성되는 것들:
// 1. private final 필드
// 2. 모든 필드를 받는 생성자
// 3. Getter 메서드 (email(), password())
// 4. equals(), hashCode(), toString()
```

**특징**:

- ✅ 불변성 (Immutable)
- ✅ 간결한 코드 (보일러플레이트 제거)
- ✅ 자동 생성 메서드
- ❌ Setter 불가
- ❌ 상속 불가 (final class)

---

## 2.2 POJO란?

**정의**: Plain Old Java Object - 특정 프레임워크에 종속되지 않은 순수 Java 객체

```java
// POJO 방식 (Lombok 사용)
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProjectBoardDTO {
    private Long projectId;
    private String name;
    private BigDecimal totalBudget;
    private List<KanbanColumnDTO> columns;
}
```

**특징**:

- ✅ 유연성 (Setter, 상속 가능)
- ✅ 프레임워크 호환성 높음
- ✅ 기본 생성자 제공 가능
- ❌ 보일러플레이트 코드 많음 (Lombok 없이)
- ❌ 불변성 보장 어려움

---

# 3. Critical Thinking: JPA 관점 분석

## ⚖️ JPA에서 Record vs POJO

### ❌ JPA Entity에 Record 사용 불가

**이유**:

1. **프록시 생성 불가**

```java
// ❌ 불가능
@Entity
public record User(
    @Id Long userId,
    String email,
    String name
) {}

// JPA는 지연 로딩을 위해 프록시 객체를 생성하는데,
// Record는 final class라서 상속 불가 → 프록시 생성 불가
```

1. **기본 생성자 없음**

```java
// JPA는 리플렉션을 사용하여 객체를 생성하므로
// 기본 생성자(no-args constructor)가 필수
// Record는 모든 필드를 받는 생성자만 자동 생성
```

1. **Setter 메서드 없음**

```java
// JPA는 Entity를 조회할 때 Setter를 통해 값을 주입
// Record는 불변이므로 Setter가 없음
```

---

### ✅ JPA Entity는 POJO 사용

```java
@Entity
@Table(name = "users")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)  // 필수!
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    private Long userId;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String password;

    // 비즈니스 로직 메서드 추가 가능
    public void updateInfo(String name, String department) {
        [this.name](http://this.name) = name;
        this.department = department;
    }
}
```

**필수 요구사항**:

- `@NoArgsConstructor` (기본 생성자)
- Non-final class (프록시 생성 위해)
- Setter 또는 필드 접근 가능 (리플렉션)

---

### ✅ JPA DTO Projection에 Record 사용 가능

```java
// ✅ 가능 - DTO Projection
public record UserSummaryDTO(
    Long userId,
    String email,
    String name
) {}

// Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    @Query("""
        SELECT new com.bizsync.backend.dto.UserSummaryDTO(
            u.userId, [u.email](http://u.email), [u.name](http://u.name)
        )
        FROM User u
        WHERE u.department = :department
    """)
    List<UserSummaryDTO> findUserSummaries(
        @Param("department") String department
    );
}
```

**장점**:

- 불변성 보장 (조회 전용 데이터)
- 간결한 코드
- 명확한 의도 (읽기 전용)

---

## 📊 JPA 사용 시 선택 가이드

| 용도 | 선택 | 이유 |
| --- | --- | --- |
| **Entity** | POJO | JPA 스펙 요구사항 (프록시, 기본 생성자) |
| **DTO Projection** | Record | 불변성, 간결성 (읽기 전용) |
| **Request DTO** | Record | 불변성 보장 (변경 방지) |
| **Response DTO** | Record | 불변성 (단, 빌더 패턴 불필요 시) |

---

# 4. Critical Thinking: MyBatis 관점 분석

## ⚖️ MyBatis에서 Record vs POJO

### ✅ MyBatis는 Record 사용 가능

**단순 조회 시 Record 사용 가능**:

```java
// ✅ 가능 - 단순 조회
public record UserDTO(
    Long userId,
    String email,
    String name
) {}

// Mapper
public interface UserMapper {
    @Select("SELECT user_id, email, name FROM users WHERE user_id = #{id}")
    @Results({
        @Result(property = "userId", column = "user_id"),
        @Result(property = "email", column = "email"),
        @Result(property = "name", column = "name")
    })
    UserDTO findById(Long id);
}
```

**MyBatis가 Record를 처리하는 방식**:

1. 모든 필드를 받는 생성자 호출
2. 컬럼 값을 생성자 파라미터로 전달
3. Setter 불필요 (생성자 주입)

---

### ⚠️ 중첩 매핑(Nested Mapping)에서 제약

```java
// ❌ Record로 중첩 매핑 시 문제
public record ProjectBoardDTO(
    Long projectId,
    String name,
    List<KanbanColumnDTO> columns  // 중첩 컬렉션
) {}

public record KanbanColumnDTO(
    Long columnId,
    String name,
    List<TaskDTO> tasks  // 중첩 컬렉션
) {}
```

```xml
<!-- resultMap에서 collection 사용 시 문제 -->
<resultMap id="ProjectBoardMap" type="ProjectBoardDTO">
    <id property="projectId" column="project_id"/>
    <result property="name" column="project_name"/>
    
    <!-- ❌ Record는 불변이라 collection 추가 불가 -->
    <collection property="columns" 
                ofType="KanbanColumnDTO"
                javaType="java.util.ArrayList">
        <!-- ... -->
    </collection>
</resultMap>
```

**문제점**:

- MyBatis는 먼저 객체를 생성한 후, Setter로 컬렉션에 요소 추가
- Record는 생성 시점에 모든 값이 확정되어야 함
- 중첩 컬렉션은 조회 결과에 따라 동적으로 추가됨

---

### ✅ 중첩 매핑은 POJO 사용

**실제 프로젝트 예시**:

```java
// ✅ POJO 사용 - MyBatis 중첩 매핑
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProjectBoardDTO {
    private Long projectId;
    private String name;
    private BigDecimal totalBudget;
    private BigDecimal usedBudget;
    private List<KanbanColumnDTO> columns;  // 1:N
}

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KanbanColumnDTO {
    private Long columnId;
    private String name;
    private Integer sequence;
    private List<TaskDTO> tasks;  // 1:N
}

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TaskDTO {
    private Long taskId;
    private String title;
    private Integer sequence;
    private LocalDate deadline;
    private String workerName;
}
```

```xml
<!-- ✅ POJO로 중첩 매핑 -->
<resultMap id="ProjectBoardMap" type="ProjectBoardDTO">
    <id property="projectId" column="project_id"/>
    <result property="name" column="project_name"/>
    <result property="totalBudget" column="total_budget"/>
    <result property="usedBudget" column="used_budget"/>

    <collection property="columns"
                ofType="KanbanColumnDTO"
                javaType="java.util.ArrayList">
        <id property="columnId" column="column_id"/>
        <result property="name" column="column_name"/>
        <result property="sequence" column="column_seq"/>

        <collection property="tasks"
                    ofType="TaskDTO"
                    javaType="java.util.ArrayList">
            <id property="taskId" column="task_id"/>
            <result property="title" column="task_title"/>
            <result property="sequence" column="task_seq"/>
            <result property="deadline" column="deadline"/>
            <result property="workerName" column="worker_name"/>
        </collection>
    </collection>
</resultMap>

<select id="selectProjectBoard" resultMap="ProjectBoardMap">
    SELECT
        p.project_id,
        [p.name](http://p.name) AS project_name,
        [p.total](http://p.total)_budget,
        p.used_budget,
        c.column_id,
        [c.name](http://c.name) AS column_name,
        c.sequence AS column_seq,
        t.task_id,
        t.title AS task_title,
        t.sequence AS task_seq,
        t.deadline,
        [u.name](http://u.name) AS worker_name
    FROM project p
    LEFT JOIN kanban_column c ON p.project_id = c.project_id
    LEFT JOIN task t ON c.column_id = t.column_id
    LEFT JOIN users u ON t.worker_id = u.user_id
    WHERE p.project_id = #{projectId}
    ORDER BY c.sequence ASC, t.sequence ASC
</select>
```

---

## 📊 MyBatis 사용 시 선택 가이드

| 용도 | 선택 | 이유 |
| --- | --- | --- |
| **단순 조회 DTO** | Record | 불변성, 간결성 |
| **중첩 매핑 DTO** | POJO | MyBatis collection 동작 방식 |
| **Request DTO** | Record | 불변성 보장 |
| **1:N, N:M 조회** | POJO | 동적 컬렉션 추가 필요 |

---

# 5. 실무 적용 전략

## 5.1 Request DTO - Record 적합 ✅

```java
// ✅ Request는 불변이어야 함
public record LoginRequestDTO(
    @NotBlank(message = "이메일은 필수입니다.")
    String email,

    @NotBlank(message = "비밀번호는 필수입니다.")
    String password
) {}

public record ProjectCreateRequestDTO(
    @NotBlank String name,
    @NotNull BigDecimal totalBudget
) {}
```

**이유**:

- 요청 데이터는 변경되면 안 됨
- 유효성 검증 후 변경 방지
- 간결한 코드

---

## 5.2 Response DTO - 상황에 따라

### ✅ Record 사용 (단순 응답)

```java
// ✅ 단순 응답
public record LoginResponseDTO(
    Long userId,
    String email,
    String name,
    String accessToken
) {}

public record JwtTokenResponse(
    String accessToken,
    String refreshToken
) {}
```

---

### ✅ POJO 사용 (복잡한 응답)

```java
// ✅ 복잡한 응답 (빌더 패턴 필요)
@Data
@Builder
public class ProjectDetailResponseDTO {
    private Long projectId;
    private String name;
    private BigDecimal totalBudget;
    private BigDecimal usedBudget;
    private List<MemberDTO> members;
    private ProjectStatus status;
    
    public BigDecimal getRemainingBudget() {
        return totalBudget.subtract(usedBudget);
    }
}
```

**POJO 선택 이유**:

- 빌더 패턴으로 선택적 필드 설정
- 계산 메서드 추가 가능
- 유연한 확장성

---

## 5.3 프로젝트 전략 정리

```
📁 com.bizsync.backend
├── 📁 dto
│   ├── 📁 request       → ✅ Record 사용
│   │   ├── [LoginRequestDTO.java](http://LoginRequestDTO.java)
│   │   ├── [SignupRequestDTO.java](http://SignupRequestDTO.java)
│   │   └── [ProjectCreateRequestDTO.java](http://ProjectCreateRequestDTO.java)
│   │
│   └── 📁 response      → 상황에 따라
│       ├── [LoginResponseDTO.java](http://LoginResponseDTO.java)          (Record - 단순)
│       ├── [JwtTokenResponse.java](http://JwtTokenResponse.java)          (Record - 단순)
│       └── kanban/
│           ├── [ProjectBoardDTO.java](http://ProjectBoardDTO.java)       (POJO - 중첩)
│           ├── [KanbanColumnDTO.java](http://KanbanColumnDTO.java)       (POJO - 중첩)
│           └── [TaskDTO.java](http://TaskDTO.java)               (POJO - 중첩)
│
├── 📁 domain
│   └── 📁 entity        → ✅ POJO만 사용 (JPA 요구사항)
│       ├── [User.java](http://User.java)
│       ├── [Project.java](http://Project.java)
│       └── [Task.java](http://Task.java)
│
└── 📁 mapper            → MyBatis
    └── 중첩 매핑 DTO    → ✅ POJO 사용
```

---

# 6. 유의사항 및 베스트 프랙티스

## ⚠️ 주의사항

### 1. Jackson 직렬화/역직렬화

```java
// ✅ Record는 Jackson 2.12+ 에서 지원
public record UserDTO(
    Long userId,
    String email
) {}

// JSON → Record (자동)
// { "userId": 1, "email": "[test@example.com](mailto:test@example.com)" }

// Record → JSON (자동)
// { "userId": 1, "email": "[test@example.com](mailto:test@example.com)" }
```

**Gradle 의존성 확인**:

```
implementation 'com.fasterxml.jackson.core:jackson-databind:2.15.0'
```

---

### 2. Bean Validation

```java
// ✅ Record에서 Validation 가능
public record SignupRequestDTO(
    @NotBlank @Email
    String email,
    
    @NotBlank @Size(min = 8, max = 20)
    String password,
    
    @NotBlank @Size(max = 20)
    String name
) {}
```

---

### 3. Lombok과 Record 비교

```java
// Lombok으로 불변 객체
@Value
public class UserDTO {
    Long userId;
    String email;
    String name;
}

// Record (더 간결)
public record UserDTO(
    Long userId,
    String email,
    String name
) {}
```

**Record 장점**:

- 표준 Java 기능 (Lombok 의존성 불필요)
- 컴파일 타임 보장
- 명확한 의도 표현

---

## 🎯 베스트 프랙티스

### 1. DTO는 계층별로 분리

```java
// Request Layer
public record CreateTaskRequest(
    String title,
    LocalDate deadline
) {}

// Domain Layer (Entity)
@Entity
public class Task {
    // POJO
}

// Response Layer
public record TaskResponse(
    Long taskId,
    String title,
    LocalDate deadline
) {}
```

---

### 2. Record에 정적 팩토리 메서드 추가

```java
public record UserDTO(
    Long userId,
    String email,
    String name
) {
    // ✅ Entity → DTO 변환
    public static UserDTO from(User user) {
        return new UserDTO(
            user.getUserId(),
            user.getEmail(),
            user.getName()
        );
    }
}

// 사용
UserDTO dto = UserDTO.from(user);
```

---

### 3. Record에 검증 로직 추가

```java
public record CreateProjectRequest(
    String name,
    BigDecimal totalBudget
) {
    // ✅ Compact Constructor
    public CreateProjectRequest {
        if (totalBudget.compareTo([BigDecimal.ZERO](http://BigDecimal.ZERO)) <= 0) {
            throw new IllegalArgumentException(
                "예산은 0보다 커야 합니다."
            );
        }
    }
}
```

---

# 7. Interview Readiness

## ▶ Q1: JPA Entity에 Record를 사용할 수 없는 이유는?

**A**: 세 가지 이유가 있습니다:

1. **프록시 생성 불가**: JPA는 지연 로딩을 위해 Entity의 프록시 객체를 생성하는데, Record는 final class라서 상속할 수 없어 프록시를 만들 수 없습니다.
2. **기본 생성자 없음**: JPA는 리플렉션으로 Entity를 생성할 때 기본 생성자를 사용하는데, Record는 모든 필드를 받는 생성자만 자동 생성됩니다.
3. **Setter 없음**: JPA가 DB에서 조회한 값을 Entity에 주입할 때 Setter를 사용하는데, Record는 불변이라 Setter가 없습니다.

따라서 JPA Entity는 반드시 POJO를 사용해야 하며, `@NoArgsConstructor`를 필수로 선언해야 합니다.

---

## ▶ Q2: MyBatis에서 Record 사용 시 제약사항은?

**A**: MyBatis는 단순 조회에서는 Record를 사용할 수 있지만, 중첩 매핑(Nested Mapping)에서는 제약이 있습니다.

**제약 이유**:

- MyBatis의 `<collection>` 태그는 먼저 부모 객체를 생성한 후, 자식 객체들을 동적으로 추가합니다
- Record는 생성 시점에 모든 값이 확정되어야 하므로, 나중에 컬렉션에 요소를 추가할 수 없습니다

**해결책**:

- 단순 조회(1:1): Record 사용 가능
- 중첩 매핑(1:N, N:M): POJO 사용 필수

예를 들어, 프로젝트 → 컬럼 → 태스크처럼 2단계 이상 중첩된 결과를 조회할 때는 POJO를 사용해야 합니다.

---

## ▶ Q3: Request DTO에 Record를 사용하는 이유는?

**A**: Request DTO는 불변성(Immutability)이 중요하기 때문입니다.

**이유**:

1. **데이터 무결성**: 유효성 검증 후 데이터가 변경되면 안 됩니다
2. **스레드 안전성**: 여러 스레드에서 동시에 접근해도 안전합니다
3. **명확한 의도**: Record는 "이 객체는 읽기 전용"이라는 의도를 코드로 명확히 표현합니다
4. **간결성**: Getter, equals, hashCode, toString이 자동 생성됩니다

또한 Record는 생성자 파라미터에 직접 `@NotBlank`, `@Email` 등의 검증 애노테이션을 붙일 수 있어 Bean Validation과도 잘 호환됩니다.

---

## ▶ Q4: Record와 Lombok @Value의 차이는?

**A**:

| 구분 | Record | Lombok @Value |
| --- | --- | --- |
| **표준** | Java 표준 (JDK 16+) | 외부 라이브러리 |
| **컴파일** | Java 컴파일러 | 애노테이션 프로세서 |
| **Getter** | 필드명() - email() | getEmail() |
| **의존성** | 없음 | Lombok 필요 |

**결론**: 새 프로젝트에서는 Record를 사용하는 것이 표준을 따르는 방식이며, 외부 의존성이 없어 더 권장됩니다. 단, JDK 16 미만 환경이거나 기존 Lombok 코드와 일관성을 유지해야 한다면 @Value를 사용할 수 있습니다.

---

## 🔑 핵심 체크리스트

- [ ]  JPA Entity는 **POJO만 가능** (Record 불가)
- [ ]  JPA Entity는 `@NoArgsConstructor` 필수
- [ ]  JPA DTO Projection은 **Record 사용 가능**
- [ ]  MyBatis 단순 조회는 **Record 가능**
- [ ]  MyBatis 중첩 매핑은 **POJO 필수**
- [ ]  Request DTO는 **Record 권장** (불변성)
- [ ]  Response DTO는 **상황에 따라 선택**
- [ ]  Record는 JDK 16+ 필요
- [ ]  Jackson 2.12+ 필요 (Record 직렬화)

---

**작성일**: 2026-01-16  

**면접 빈출도**: ⭐⭐⭐⭐ (상)  

**프로젝트**: bizsync-backend 실제 사례 기반