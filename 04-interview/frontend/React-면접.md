---
tags:
  - interview
  - React
  - Frontend
created: 2026-01-24
difficulty: 최상
---

# React 면접

## 질문
> React 19 변경사항, Hooks, Virtual DOM, TypeScript 활용, 성능 최적화

## 핵심 답변 (3줄)
1. React 19는 Compiler로 자동 최적화, use() Hook으로 Promise 처리, Server Components로 번들 크기 감소
2. useState는 상태 관리하며 리렌더링 발생, useRef는 리렌더링 없이 값 보관 또는 DOM 참조
3. Virtual DOM으로 변경사항을 계산(Diffing)하여 실제 DOM에 최소한만 적용(Reconciliation)하여 성능 최적화

## 상세 설명

### Q1: React의 Virtual DOM이란?

**A**: 실제 DOM의 가벼운 복사본으로, 상태 변경 시 Virtual DOM에서 먼저 변경사항을 계산(Diffing)한 후 실제 DOM에 최소한의 변경만 적용(Reconciliation)하여 성능을 최적화합니다.

**동작 과정**:
1. 상태 변경 시 새로운 Virtual DOM 트리 생성
2. 이전 Virtual DOM과 비교 (Diffing)
3. 변경된 부분만 실제 DOM에 반영 (Reconciliation)

이를 통해 DOM 조작 비용을 최소화하고 효율적인 렌더링을 달성합니다.

---

### Q2: React 19의 주요 변경사항은?

**A**:

1. **React Compiler**: useMemo, useCallback 수동 작성 불필요, 컴파일러가 자동 메모이제이션
2. **use() Hook**: Promise 직접 처리, Suspense와 자동 연동, 조건문 안에서도 사용 가능
3. **Server Components**: 서버에서 비동기 데이터 페칭, 클라이언트 번들 크기 감소
4. **Actions**: 폼 처리 간소화

```typescript
// React 18 이전: 수동 최적화
const filtered = useMemo(() => data.filter(item => item.active), [data]);

// React 19: 자동 최적화
const filtered = data.filter(item => item.active);
```

---

### Q3: useState vs useRef 차이는?

**A**:

| 구분 | useState | useRef |
|------|----------|--------|
| **리렌더링** | 값 변경 시 리렌더링 | 리렌더링 없음 |
| **용도** | UI 상태 | DOM 참조, 값 보관 |
| **업데이트** | 비동기 | 즉시 |

```typescript
// useState: UI 상태 관리
const [count, setCount] = useState(0);
setCount(count + 1);  // 리렌더링 발생

// useRef: DOM 참조
const inputRef = useRef<HTMLInputElement>(null);
inputRef.current?.focus();  // 리렌더링 없음

// useRef: 값 보관
const renderCount = useRef(0);
renderCount.current += 1;  // 리렌더링 없음
```

---

### Q4: useEffect의 의존성 배열이 중요한 이유는?

**A**: 의존성 배열에 포함된 값이 변경될 때만 effect가 실행되므로, 불필요한 실행을 방지하고 무한 루프를 예방합니다.

```typescript
// 빈 배열 []: 마운트시 1회만 실행
useEffect(() => {
  fetchData();
}, []);

// [count]: count 변경시마다 실행
useEffect(() => {
  console.log(count);
}, [count]);

// 생략: 매 렌더링마다 실행 (비권장)
useEffect(() => {
  // 무한 루프 위험!
});
```

**의존성 누락 시 문제**:
```typescript
// ❌ 잘못된 예
useEffect(() => {
  console.log(count);  // count 사용하지만 의존성 배열에 없음
}, []);  // count 변경 시에도 실행 안 됨!
```

---

### Q5: Server Component와 Client Component의 차이는?

**A**:

| 구분 | Server Component | Client Component |
|------|------------------|-----------------|
| **실행 위치** | 서버 | 브라우저 |
| **번들 크기** | 포함 안됨 | 포함됨 |
| **Hooks 사용** | ❌ 불가 | ✅ 가능 |
| **async/await** | ✅ 가능 | ❌ 불가 |

```typescript
// Server Component (기본)
const ServerComponent = async () => {
  const data = await fetch('https://api.example.com/data');
  return <div>{data.title}</div>;
};

// Client Component (명시적 선언)
'use client';
const ClientComponent = () => {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
};
```

---

### Q6: React에서 key prop이 중요한 이유는?

**A**: 리스트 렌더링 시 React가 어떤 항목이 변경/추가/삭제되었는지 식별하기 위해 사용합니다.

```typescript
// ❌ 잘못된 예: index를 key로 사용
{items.map((item, index) => 
  <li key={index}>{item.name}</li>
)}

// ✅ 올바른 예: 고유한 ID를 key로 사용
{items.map(item => 
  <li key={item.id}>{item.name}</li>
)}
```

**index를 key로 사용하면 안 되는 이유**:
- 항목 순서가 바뀌면 비효율적인 리렌더링 발생
- 상태 관리가 꼬일 수 있음

---

### Q7: useMemo와 useCallback의 차이는?

**A**:

**useMemo**: 계산 결과를 메모이제이션
```typescript
const expensiveValue = useMemo(() => {
  return expensiveCalculation(a, b);
}, [a, b]);
```

**useCallback**: 함수 자체를 메모이제이션
```typescript
const handleClick = useCallback(() => {
  console.log('clicked');
}, []);
```

**React 19에서는 Compiler가 자동으로 처리하므로 수동 작성 불필요!**

---

### Q8: React의 단방향 데이터 흐름이란?

**A**: 부모 컴포넌트에서 자식 컴포넌트로만 데이터(props)가 전달되는 패턴입니다.

**장점**:
1. 데이터 흐름 추적 용이
2. 디버깅 쉬움
3. 예측 가능한 상태 관리

**자식 → 부모 통신**: 콜백 함수를 props로 전달
```typescript
// 부모
const Parent = () => {
  const [value, setValue] = useState('');
  return <Child onValueChange={setValue} />;
};

// 자식
const Child = ({ onValueChange }) => {
  return <input onChange={(e) => onValueChange(e.target.value)} />;
};
```

---

### Q9: Props Drilling 문제와 해결 방법은?

**A**: Props Drilling은 중간 컴포넌트들이 사용하지 않는 props를 단순히 전달만 하는 문제입니다.

**해결 방법**:
1. **Context API**: 전역 상태 관리
2. **Zustand/Redux**: 상태 관리 라이브러리
3. **Composition**: 컴포넌트 합성

```typescript
// ❌ Props Drilling
<App>
  <Parent user={user}>
    <Child user={user}>
      <GrandChild user={user} />
    </Child>
  </Parent>
</App>

// ✅ Context API
const UserContext = createContext(null);
<UserContext.Provider value={user}>
  <App />
</UserContext.Provider>
// GrandChild에서 useContext(UserContext)로 직접 접근
```

---

### Q10: React 성능 최적화 방법은?

**A**:

1. **React.memo**: 컴포넌트 메모이제이션
2. **useMemo**: 계산 결과 메모이제이션
3. **useCallback**: 함수 메모이제이션
4. **Code Splitting**: React.lazy + Suspense
5. **Virtual List**: 긴 리스트 최적화
6. **이미지 최적화**: lazy loading, WebP

```typescript
// React.memo
const MemoizedComponent = React.memo(MyComponent);

// Code Splitting
const LazyComponent = lazy(() => import('./LazyComponent'));
<Suspense fallback={<div>Loading...</div>}>
  <LazyComponent />
</Suspense>
```

**React 19에서는 Compiler가 자동 최적화하므로 대부분 불필요!**

## 꼬리 질문 예상
- useLayoutEffect vs useEffect 차이는?
- Controlled vs Uncontrolled Component는?
- React Fiber란?
- Concurrent Rendering은?

## 참고
- [[React-19-TypeScript-핵심]]
- [[React-Hooks]]
- [[Virtual-DOM]]
- [[React-성능최적화]]
