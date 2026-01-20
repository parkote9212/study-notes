# Java 동시성: 멀티스레드와 동기화 완벽 가이드

🏷️기술 카테고리: Concurrency, Java
💡핵심키워드: #멀티스레드, #동기화
💼 면접 빈출도: 최상

# 1. Abstract: 핵심 요약

멀티스레드 환경에서 여러 스레드가 공유 자원에 동시에 접근할 때 발생하는 Race Condition, Deadlock 등의 문제를 해결하기 위한 동기화 기법을 다룹니다.

**핵심 원칙**:
- 임계 영역(Critical Section)의 동기화
- Lock과 Condition Variable
- 불변 객체 활용
- 스레드 안전 컬렉션

---

# 2. 스레드 기본

## 2.1 스레드 생성

```java
// 방법 1: Thread 상속
class MyThread extends Thread {
    @Override
    public void run() {
        // 실행 코드
    }
}
new MyThread().start();

// 방법 2: Runnable 구현
class MyRunnable implements Runnable {
    @Override
    public void run() {
        // 실행 코드
    }
}
new Thread(new MyRunnable()).start();

// 방법 3: 람다식
new Thread(() -> {
    // 실행 코드
}).start();
```

## 2.2 스레드 생명주기

- **NEW**: 스레드 생성 (start() 호출 전)
- **RUNNABLE**: 실행 가능 상태
- **BLOCKED**: Lock 대기 중
- **WAITING**: 다른 스레드 대기
- **TERMINATED**: 종료

---

# 3. 동기화

## 3.1 synchronized 키워드

```java
// 메서드 동기화
public synchronized void incrementCounter() {
    count++;
}

// 블록 동기화
public void safeMethod() {
    synchronized (this) {
        count++;
    }
}
```

## 3.2 Volatile

```java
// 변수 변경이 즉시 모든 스레드에 반영
private volatile boolean running = true;

public void stop() {
    running = false;  // 모든 스레드에 즉시 반영
}
```

## 3.3 Atomic 클래스

```java
private AtomicInteger counter = new AtomicInteger(0);

public void increment() {
    counter.incrementAndGet();  // 원자적 연산
}
```

---

# 4. 고급 동기화

## 4.1 Lock과 Condition

```java
private Lock lock = new ReentrantLock();
private Condition notEmpty = lock.newCondition();

public void produce(String value) {
    lock.lock();
    try {
        queue.add(value);
        notEmpty.signal();
    } finally {
        lock.unlock();
    }
}

public String consume() throws InterruptedException {
    lock.lock();
    try {
        while (queue.isEmpty()) {
            notEmpty.await();
        }
        return queue.poll();
    } finally {
        lock.unlock();
    }
}
```

## 4.2 ReadWriteLock

```java
private ReadWriteLock rwLock = new ReentrantReadWriteLock();

public String read() {
    rwLock.readLock().lock();
    try {
        return data;
    } finally {
        rwLock.readLock().unlock();
    }
}

public void write(String value) {
    rwLock.writeLock().lock();
    try {
        data = value;
    } finally {
        rwLock.writeLock().unlock();
    }
}
```

---

# 5. 스레드 안전 컬렉션

```java
// 동기화 래퍼
List<String> syncList = Collections.synchronizedList(new ArrayList<>());

// ConcurrentHashMap
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// BlockingQueue
BlockingQueue<String> queue = new LinkedBlockingQueue<>();
queue.put("item");
String item = queue.take();  // 비어있으면 대기
```

---

# 6. 면접 포인트

Race Condition 이해, synchronized 대안, Deadlock 회피 등이 중요합니다.

**작성일**: 2026년
**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)
