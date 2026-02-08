---
tags:
  - study
  - java
  - collection
created: 2025-02-01
---

# Java 컬렉션 프레임워크

## 한 줄 요약
> 데이터를 효율적으로 저장·관리하는 표준 자료구조

## 상세 설명

### What
데이터 그룹을 저장하고 조작하기 위한 통합 아키텍처입니다.

### Why
- 표준화된 데이터 관리
- 재사용 가능한 자료구조
- 성능 최적화
- 코드 일관성 유지

### 계층 구조
```
Collection (인터페이스)
├── List (순서O, 중복O)
│   ├── ArrayList
│   ├── LinkedList
│   └── Vector
├── Set (순서X, 중복X)
│   ├── HashSet
│   ├── LinkedHashSet
│   └── TreeSet
└── Queue (FIFO)
    ├── PriorityQueue
    └── Deque (ArrayDeque, LinkedList)

Map (별도 인터페이스)
├── HashMap
├── LinkedHashMap
├── TreeMap
└── Hashtable
```

---

## List - 순서가 있는 컬렉션

### ArrayList
```java
List<String> list = new ArrayList<>();
list.add("Apple");
list.add("Banana");
list.add("Apple"); // 중복 허용
list.get(0); // "Apple" - O(1)
list.remove(0); // O(n)
```

**특징:**
- 내부: 동적 배열 (Object[])
- 조회: O(1) ⭐
- 삽입/삭제: O(n)
- 초기 용량: 10, 확장: 1.5배
- **사용 시기:** 조회가 많고 삽입/삭제가 적을 때

### LinkedList
```java
List<Integer> list = new LinkedList<>();
list.add(1);
list.add(0, 0); // 맨 앞 삽입 - O(1)
list.get(1); // O(n)
```

**특징:**
- 내부: 이중 연결 리스트
- 조회: O(n)
- 삽입/삭제: O(1) ⭐
- **사용 시기:** 삽입/삭제가 빈번할 때

---

## Set - 중복 없는 집합

### HashSet
```java
Set<String> set = new HashSet<>();
set.add("A");
set.add("A"); // 중복 안 됨
set.contains("A"); // true - O(1)
```

**특징:**
- 내부: HashMap 사용
- 순서: 보장 안 함
- 성능: O(1)
- null 허용 (1개)
- **가장 빠른 Set**

### LinkedHashSet
```java
Set<String> set = new LinkedHashSet<>();
set.add("C");
set.add("A");
set.add("B");
System.out.println(set); // [C, A, B] - 삽입 순서 유지
```

### TreeSet
```java
Set<Integer> set = new TreeSet<>();
set.add(3);
set.add(1);
set.add(2);
System.out.println(set); // [1, 2, 3] - 자동 정렬
```

**특징:**
- 내부: Red-Black Tree
- 자동 정렬
- 성능: O(log n)
- null 불가
- Comparable/Comparator 필요

---

## Map - Key-Value 쌍

### HashMap
```java
Map<String, Integer> map = new HashMap<>();
map.put("Apple", 1000);
map.put("Apple", 1200); // 덮어쓰기
map.get("Apple"); // 1200
map.getOrDefault("Grape", 0); // 0
map.containsKey("Apple"); // true
```

**특징:**
- 해시 테이블 기반
- 순서: 보장 안 함
- 성능: O(1)
- null 키/값 허용
- **가장 많이 사용**

**순회 방법:**
```java
// 1. entrySet() - 가장 효율적
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}

// 2. forEach (Java 8+)
map.forEach((key, value) -> System.out.println(key + ": " + value));
```

### LinkedHashMap
```java
Map<String, Integer> map = new LinkedHashMap<>();
map.put("C", 3);
map.put("A", 1);
// {C=3, A=1} - 삽입 순서 유지
```

### TreeMap
```java
Map<String, Integer> map = new TreeMap<>();
map.put("C", 3);
map.put("A", 1);
// {A=1, C=3} - 키 정렬
```

---

## Queue/Deque

### Queue (FIFO)
```java
Queue<Integer> queue = new LinkedList<>();
queue.offer(1);
queue.offer(2);
queue.poll(); // 1
queue.peek(); // 2
```

### Deque (양방향)
```java
Deque<String> deque = new ArrayDeque<>();
deque.addFirst("A");
deque.addLast("B");
deque.pollFirst(); // "A"
```

### PriorityQueue
```java
Queue<Integer> pq = new PriorityQueue<>();
pq.offer(3);
pq.offer(1);
pq.poll(); // 1 (최소값)
```

---

## Collections 유틸리티

```java
List<Integer> list = Arrays.asList(3, 1, 2);

Collections.sort(list); // 정렬
Collections.reverse(list); // 역순
Collections.shuffle(list); // 섞기
Collections.max(list); // 최대값
Collections.min(list); // 최소값

// 불변 컬렉션 (Java 9+)
List.of("A", "B", "C");
Set.of(1, 2, 3);
Map.of("A", 1, "B", 2);

// 동기화
Collections.synchronizedList(new ArrayList<>());
Collections.synchronizedMap(new HashMap<>());
```

## 코드 예시
```java
// ConcurrentModificationException 회피
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));

// ❌ 잘못된 방법
for (String s : list) {
    if (s.equals("B")) {
        list.remove(s); // 예외 발생!
    }
}

// ✅ 올바른 방법 1
Iterator<String> iter = list.iterator();
while (iter.hasNext()) {
    if (iter.next().equals("B")) {
        iter.remove();
    }
}

// ✅ 올바른 방법 2 (Java 8+)
list.removeIf(s -> s.equals("B"));

// equals/hashCode 구현
class Person {
    String name;
    int age;
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Person p = (Person) o;
        return age == p.age && Objects.equals(name, p.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}
```

## 주의사항 / 함정

1. **순회 중 수정 금지**
   - Iterator 사용 또는 removeIf 사용

2. **Set/Map 키는 equals/hashCode 구현 필수**
   ```java
   // ❌ 구현 안 하면 중복 체크 안 됨
   ```

3. **키 객체는 불변 사용**
   - String, Integer 등 불변 객체 권장

4. **TreeSet/TreeMap은 null 불가**
   - NullPointerException 발생

5. **멀티스레드 환경**
   - ConcurrentHashMap 사용
   - Collections.synchronizedXxx() 사용

6. **ArrayList 초기 용량 설정**
   ```java
   List<String> list = new ArrayList<>(1000); // 대량 데이터 시
   ```

## 관련 개념
- [[Java-제네릭스-Generics]]
- [[Java-람다-Stream]]
- [[Java-Object-equals-hashCode]]

## 면접 질문
1. ArrayList와 LinkedList의 차이점과 각각 언제 사용하나요?
2. HashSet은 중복을 어떻게 판단하나요?
3. HashMap의 내부 동작 원리를 설명하세요.
4. ConcurrentModificationException은 언제 발생하며 어떻게 해결하나요?
5. HashMap과 TreeMap의 차이는 무엇인가요?

## 참고 자료
- Effective Java Item 28: Prefer lists to arrays
- Effective Java Item 11: Always override hashCode when you override equals