---
tags: study, React, TypeScript, Frontend
created: 2026-01-24
---

# React 19 TypeScript 핵심

## 한 줄 요약
> React 19는 React Compiler, Server Components, use() Hook 등 혁신적 기능을 도입하여 자동 최적화와 선언적 UI 개발을 강화

## 상세 설명

React는 컴포넌트 기반 선언적 프로그래밍으로 UI를 재사용 가능한 조각으로 분리하며, 단방향 데이터 흐름으로 부모에서 자식으로 props를 전달합니다.

### React 19 주요 변경사항

**React Compiler (자동 최적화)**
- useMemo, useCallback 수동 작성 불필요
- 컴파일러가 자동으로 불필요한 리렌더링 방지

**use() Hook (데이터 패칭)**
- Promise를 직접 unwrap
- Suspense와 자동 연동
- 조건문 안에서도 사용 가능

**Server Components (RSC)**
- 서버에서 비동기 데이터 페칭
- 클라이언트 번들 크기 감소
- `'use client'`로 Client Component 명시

### TypeScript와 React

**Props 타입 정의**
```typescript
interface ButtonProps {
  text: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}
```

**children 타입**
```typescript
import { ReactNode } from 'react';

interface CardProps {
  title: string;
  children: ReactNode;
}
```

**이벤트 핸들러 타입**
```typescript
import { ChangeEvent, FormEvent } from 'react';

const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
  console.log(e.target.value);
};

const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
  e.preventDefault();
};
```

### 핵심 Hooks

**useState**
```typescript
const [count, setCount] = useState(0);
const [user, setUser] = useState<User | null>(null);

// 함수형 업데이트
setCount(prev => prev + 1);
```

**useEffect**
- 빈 배열 `[]`: 마운트시 1회 실행
- `[count]`: count 변경시마다 실행
- cleanup 함수로 정리 작업

**useRef**
- DOM 직접 조작
- 리렌더링 없이 값 보관

### 컴포넌트 패턴

**Presentational vs Container**
- Presentational: UI만 담당
- Container: 로직 담당

**Compound Components**
- 여러 컴포넌트를 조합하여 복잡한 UI 구성

## 코드 예시
```typescript
// React 19 자동 최적화
const ExpensiveComponent = ({ data }: Props) => {
  const filtered = data.filter(item => item.active);
  const handleClick = () => console.log('clicked');
  return <div onClick={handleClick}>{filtered.length}</div>;
};

// use() Hook
const UserProfile = ({ userPromise }: { userPromise: Promise<User> }) => {
  const user = use(userPromise);
  return <div>{user.name}</div>;
};

// Server Component
const ServerComponent = async () => {
  const data = await fetch('https://api.example.com/data');
  const json = await data.json();
  return <div>{json.title}</div>;
};

// Client Component
'use client';
const ClientComponent = () => {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
};
```

## 주의사항 / 함정

1. **Server vs Client Component**: Server Component는 Hooks 사용 불가, Client Component는 async 불가
2. **useEffect 의존성 배열**: 누락 시 무한 루프 발생 가능
3. **useState 비동기**: setState는 비동기로 동작, 즉시 반영 안 됨
4. **key prop**: 리스트 렌더링 시 고유한 key 필수

## 관련 개념
- [[Virtual-DOM]]
- [[React-Hooks]]
- [[JSX]]
- [[React-성능최적화]]

## 면접 질문
1. React의 Virtual DOM이란?
2. React 19의 주요 변경사항은?
3. useState vs useRef 차이는?
4. useEffect의 의존성 배열이 중요한 이유는?

## 참고 자료
- React 19 공식 문서
- TypeScript Handbook
