# [Spring] DAO vs Repository 차이

🏷️기술 카테고리: Design Pattern, Spring
💡핵심키워드: #디자인패턴, #레이어드아키텍처, #클린코드
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): Yes
날짜: 2026년 1월 8일 오후 11:59
📅 다음 복습일: 2026년 1월 25일

## 🧐 DAO(Data Access Object)란?

DAO는 데이터베이스나 기타 영구 저장소(파일 시스템, 클라우드 DB 등)에 접근하는 로직을 **캡슐화**하는 객체입니다. 

핵심 목표는 **비즈니스 로직(Service Layer)과 데이터 접근 기술(DB API, JDBC, JPA 등)을 분리**하는 것입니다.

---

## 🛠️ DAO의 핵심 역할

### 1. CRUD 작업 수행

Create, Read, Update, Delete와 같은 기본적인 데이터 조작 작업을 수행합니다.

### 2. 데이터 기술 캡슐화

JDBC 코드를 직접 사용하든, MyBatis 매퍼를 사용하든, JPA/Hibernate API를 사용하든, 이러한 **구현 기술의 세부 사항**을 외부에 숨깁니다.

### 3. 관심사의 분리 (Separation of Concerns)

| 계층 (Layer) | 역할 (Concern) | 예시 |
| --- | --- | --- |
| **Controller** | 클라이언트 요청 처리 및 응답 포맷 | HTTP 요청/응답, JSON 변환 |
| **Service** | 핵심 비즈니스 로직 수행 | 주문 결제, 재고 확인, 이메일 발송 |
| **DAO/Repository** | **순수 데이터 접근** | `SELECT * FROM user WHERE id = ?`, JPA의 `save()`, `findBy()` |

**만약 Service 계층에서 직접 JDBC 코드를 작성한다면:**

- DB를 MySQL에서 PostgreSQL로 바꾸거나
- JDBC에서 JPA로 기술을 변경할 때
- **Service 계층 전체를 수정**해야 하는 재앙이 발생

**DAO를 사용하면:**

- Service는 DAO 인터페이스만 바라보므로
- **DAO의 구현체만 교체**하면 됨

---

## 🚀 Modern Spring Boot 환경에서의 변화

### 1. Spring Data JPA의 Repository

Modern Java 및 Spring Boot 환경에서는 JPA와 Spring Data JPA 덕분에 DAO라는 용어 대신 **Repository**라는 용어가 더 일반적이고 선호됩니다.

| 전통적인 용어 | Modern Spring 용어 | 설명 |
| --- | --- | --- |
| **DAO** | **Repository** | 데이터 접근을 담당하는 객체. Spring Data JPA는 이를 인터페이스로 추상화하여 제공 |
| **DAO 구현체** | **자동 생성됨** | 개발자가 직접 JDBC나 EntityManager 코드를 작성하지 않아도, Spring이 런타임에 **프록시** 객체로 구현 |

### 2. 예시 (Modern Spring Boot)

```java
// DAO의 역할을 하는 Repository (인터페이스만 정의)
public interface UserRepository extends JpaRepository<User, Long> {
    // findByUsername()과 같은 메서드 구현은 Spring이 자동으로 처리
}
```

Spring Data JPA는 이 인터페이스를 보고 런타임에 프록시 객체를 자동으로 생성해 CRUD 메서드를 제공합니다.

---

## 🏗️ DAO vs Repository 비교

| 구분 | DAO | Repository |
| --- | --- | --- |
| **기원** | Java EE 패턴 | Domain Driven Design (DDD) |
| **관점** | 기술적 관점 (데이터 접근) | 도메인 친화적 관점 (객체 컬렉션) |
| **추상화 수준** | 낮음 (DB 테이블 중심) | 높음 (도메인 모델 중심) |
| **현대 프레임워크** | 제한적 지원 | Spring Data JPA 전체 지원 |

---

## 💡 언제 DAO가 여전히 필요한가?

Spring Data JPA가 해결해 주지 못하는 경우:

### 1. QueryDSL 사용

복잡한 동적 쿼리나 조인 로직을 처리할 때, `UserRepository` 인터페이스와 별개로 **QueryDSL 전용 구현체**를 만들어 사용합니다. 이때 이 구현체가 전통적인 DAO의 역할을 수행합니다.

### 2. 대규모 Batch 작업

대용량 데이터를 처리하기 위해 JDBC의 `Batch Update` 기능을 직접 사용해야 할 때, 별도의 DAO 클래스를 구현합니다.

---

## 💡 면접 대비 핵심 포인트

**질문:** "DAO와 Repository의 차이점을 설명하고, Spring 환경에서는 어떤 용어를 주로 사용해야 하나요?"

**모범 답변:**

"DAO는 데이터 접근 로직을 캡슐화하는 **패턴 이름**입니다. 구현 기술에 상관없이 데이터 조작을 담당합니다.

Repository는 Domain Driven Design(DDD)에서 유래한 용어로, **도메인 객체 컬렉션**의 접근을 추상화하는 개념입니다. DAO보다 좀 더 도메인 친화적입니다.

**Spring Data JPA**에서는 DAO의 역할을 **Repository** 인터페이스로 구현합니다. 이는 데이터 접근을 기술적인 관점(DAO)보다는 **비즈니스 도메인 관점(Repository)**에서 바라보도록 유도하는 Modern 프레임워크의 흐름을 반영한 것입니다. 따라서 Spring Boot 프로젝트에서는 **`Repository`**라는 용어를 주로 사용해야 합니다."

---

## 📚 결론

- **DAO**: 기술적 관점의 데이터 접근 객체 (전통적 용어)
- **Repository**: 도메인 친화적 관점의 객체 컬렉션 추상화 (Modern Spring 표준)
- **Modern Spring Boot**에서는 `Repository` 용어를 사용하는 것이 표준