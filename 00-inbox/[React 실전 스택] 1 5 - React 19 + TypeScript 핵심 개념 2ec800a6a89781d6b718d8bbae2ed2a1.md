# [React 실전 스택] 1/5 - React 19 + TypeScript 핵심 개념

🏷️기술 카테고리: Frontend
💡핵심키워드: #성능최적화, #함수형프로그래밍
💼 면접 빈출도: 최상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 18일 오후 4:10
📅 다음 복습일: 2026년 1월 25일

# 1. Abstract: 핵심 요약

> **React 19**는 2024년 12월 공식 출시된 최신 메이저 버전으로, **React Compiler**, **Server Components**, **Actions** 등 혁신적인 기능을 도입했습니다. TypeScript와 함께 사용하면 **타입 안전성**을 확보하면서 **선언적 UI 개발**의 강력함을 경험할 수 있습니다.
> 

**핵심 원칙**:

- 컴포넌트 기반: UI를 재사용 가능한 조각으로 분리
- 선언적 프로그래밍: "어떻게"가 아닌 "무엇을" 표현
- 단방향 데이터 흐름: 부모 → 자식으로 props 전달

---

# 2. React 19 주요 변경사항

## 2.1 React Compiler (자동 최적화)

**React 18 이전:**

```tsx
// ❌ 수동으로 useMemo, useCallback 사용
const ExpensiveComponent = ({ data }: Props) => {
  const filtered = useMemo(() => {
    return data.filter(item => item.active);
  }, [data]);
  
  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []);
  
  return <div onClick={handleClick}>{filtered.length}</div>;
};
```

**React 19:**

```tsx
// ✅ React Compiler가 자동으로 최적화
const ExpensiveComponent = ({ data }: Props) => {
  const filtered = data.filter(item => item.active);
  
  const handleClick = () => {
    console.log('clicked');
  };
  
  return <div onClick={handleClick}>{filtered.length}</div>;
};
```

**장점**: 불필요한 리렌더링을 컴파일러가 자동으로 방지

---

## 2.2 use() Hook (데이터 패칭)

```tsx
import { use } from 'react';

interface User {
  id: number;
  name: string;
}

const UserProfile = ({ userPromise }: { userPromise: Promise<User> }) => {
  // ✅ Promise를 직접 unwrap
  const user = use(userPromise);
  
  return <div>{[user.name](http://user.name)}</div>;
};
```

**특징**:

- Suspense와 자동 연동
- 조건문 안에서도 사용 가능 (기존 Hooks 규칙 완화)

---

## 2.3 Server Components (RSC)

```tsx
// ✅ Server Component (기본)
const ServerComponent = async () => {
  const data = await fetch('[https://api.example.com/data](https://api.example.com/data)');
  const json = await data.json();
  
  return <div>{json.title}</div>;
};

// Client Component (명시적 선언)
'use client';
const ClientComponent = () => {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
};
```

**차이점**:

| 구분 | Server Component | Client Component |
| --- | --- | --- |
| **실행 위치** | 서버 | 브라우저 |
| **번들 크기** | 포함 안됨 | 포함됨 |
| **Hooks 사용** | ❌ 불가 | ✅ 가능 |
| **async/await** | ✅ 가능 | ❌ 불가 |

---

# 3. TypeScript와 React

## 3.1 Props 타입 정의

```tsx
// ✅ Props 인터페이스
interface ButtonProps {
  text: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

const Button = ({ text, onClick, variant = 'primary', disabled }: ButtonProps) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn-${variant}`}
    >
      {text}
    </button>
  );
};
```

---

## 3.2 children 타입

```tsx
import { ReactNode } from 'react';

interface CardProps {
  title: string;
  children: ReactNode;  // ✅ 모든 React 노드 허용
}

const Card = ({ title, children }: CardProps) => {
  return (
    <div className="card">
      <h2>{title}</h2>
      {children}
    </div>
  );
};
```

---

## 3.3 이벤트 핸들러 타입

```tsx
import { ChangeEvent, FormEvent } from 'react';

const LoginForm = () => {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    console.log([e.target](http://e.target).value);
  };
  
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // 로그인 로직
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleChange} />
      <button type="submit">로그인</button>
    </form>
  );
};
```

---

# 4. 핵심 Hooks

## 4.1 useState

```tsx
import { useState } from 'react';

const Counter = () => {
  // ✅ 타입 추론 (number)
  const [count, setCount] = useState(0);
  
  // ✅ 명시적 타입
  const [user, setUser] = useState<User | null>(null);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>+1</button>
      <button onClick={() => setCount(prev => prev + 1)}>+1 (함수형)</button>
    </div>
  );
};
```

---

## 4.2 useEffect

```tsx
import { useEffect, useState } from 'react';

const DataFetcher = () => {
  const [data, setData] = useState<User[]>([]);
  
  useEffect(() => {
    // ✅ 비동기 함수는 내부에서 정의
    const fetchData = async () => {
      const response = await fetch('/api/users');
      const json = await response.json();
      setData(json);
    };
    
    fetchData();
    
    // ✅ cleanup 함수
    return () => {
      console.log('cleanup');
    };
  }, []); // 빈 배열 = 마운트시 1회만
  
  return <div>{data.length}명</div>;
};
```

**의존성 배열**:

- `[]`: 마운트시 1회 실행
- `[count]`: count 변경시마다 실행
- 생략: 매 렌더링마다 실행 (비권장)

---

## 4.3 useRef

```tsx
import { useRef, useEffect } from 'react';

const AutoFocusInput = () => {
  const inputRef = useRef<HTMLInputElement>(null);
  
  useEffect(() => {
    // ✅ DOM 직접 조작
    inputRef.current?.focus();
  }, []);
  
  return <input ref={inputRef} />;
};
```

---

# 5. 컴포넌트 패턴

## 5.1 Presentational vs Container

```tsx
// ✅ Presentational (UI만 담당)
interface UserCardProps {
  name: string;
  email: string;
}

const UserCard = ({ name, email }: UserCardProps) => (
  <div className="card">
    <h3>{name}</h3>
    <p>{email}</p>
  </div>
);

// ✅ Container (로직 담당)
const UserCardContainer = ({ userId }: { userId: number }) => {
  const [user, setUser] = useState<User | null>(null);
  
  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(setUser);
  }, [userId]);
  
  if (!user) return <div>Loading...</div>;
  
  return <UserCard name={[user.name](http://user.name)} email={[user.email](http://user.email)} />;
};
```

---

## 5.2 Compound Components

```tsx
interface TabsProps {
  children: ReactNode;
}

const Tabs = ({ children }: TabsProps) => {
  const [activeTab, setActiveTab] = useState(0);
  
  return (
    <div className="tabs">
      {[React.Children.map](http://React.Children.map)(children, (child, index) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, {
            isActive: index === activeTab,
            onClick: () => setActiveTab(index),
          });
        }
        return child;
      })}
    </div>
  );
};

const Tab = ({ label, isActive, onClick }: any) => (
  <button
    className={isActive ? 'active' : ''}
    onClick={onClick}
  >
    {label}
  </button>
);

// 사용
<Tabs>
  <Tab label="Tab 1" />
  <Tab label="Tab 2" />
</Tabs>
```

---

# 6. Interview Readiness

## ▶ Q1: React의 Virtual DOM이란?

**A**: 실제 DOM의 가벼운 복사본으로, 상태 변경시 Virtual DOM에서 먼저 변경사항을 계산(Diffing)한 후 실제 DOM에 최소한의 변경만 적용(Reconciliation)하여 **성능을 최적화**합니다.

---

## ▶ Q2: React 19의 주요 변경사항은?

**A**:

1. **React Compiler**: 자동 메모이제이션
2. **use() Hook**: Promise 직접 처리
3. **Server Components**: 서버에서 렌더링
4. **Actions**: 폼 처리 간소화

---

## ▶ Q3: useState vs useRef 차이는?

**A**:

| 구분 | useState | useRef |
| --- | --- | --- |
| **리렌더링** | 값 변경시 리렌더링 | 리렌더링 없음 |
| **용도** | UI 상태 | DOM 참조, 값 보관 |
| **업데이트** | 비동기 | 즉시 |

---

## ▶ Q4: useEffect의 의존성 배열이 중요한 이유는?

**A**: 의존성 배열에 포함된 값이 변경될 때만 effect가 실행되므로, **불필요한 실행을 방지**하고 **무한 루프를 예방**합니다. 빈 배열(`[]`)은 마운트시 1회만 실행됩니다.

---

## 🔑 핵심 체크리스트

- [ ]  React는 선언적 UI 라이브러리
- [ ]  컴포넌트는 함수로 작성 (Functional Component)
- [ ]  Props는 부모 → 자식 단방향
- [ ]  useState로 상태 관리, useEffect로 부수효과 처리
- [ ]  TypeScript로 Props 타입 정의 필수
- [ ]  React 19: Compiler, use(), Server Components
- [ ]  useRef는 리렌더링을 발생시키지 않음

---

**작성일**: 2026-01-18  

**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)