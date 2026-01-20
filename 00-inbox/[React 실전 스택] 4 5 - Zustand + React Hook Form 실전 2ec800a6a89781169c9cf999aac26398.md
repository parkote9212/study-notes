# [React 실전 스택] 4/5 - Zustand + React Hook Form 실전

🏷️기술 카테고리: Frontend
💡핵심키워드: #성능최적화
💼 면접 빈출도: 최상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 18일 오후 5:42
📅 다음 복습일: 2026년 1월 25일

# 1. Abstract: 핵심 요약

> **Zustand**는 Redux를 대체하는 초경량 상태관리 라이브러리로, 보일러플레이트 없이 **간결하게** 상태를 관리합니다. **React Hook Form**은 폼 처리의 표준으로, **비제어 컴포넌트** 방식으로 최소한의 리렌더링으로 고성능을 달성합니다.
> 

**핵심 원칙**:

- Zustand: 간단한 API, 미들웨어 지원
- React Hook Form: 비제어 방식으로 성능 최적화
- Zod: 타입 안전한 스키마 검증

---

# 2. Zustand - 상태 관리

## 2.1 설치 및 기본 사용

```bash
npm install zustand
```

```tsx
// src/store/userStore.ts
import { create } from 'zustand';

interface User {
  id: number;
  name: string;
  email: string;
}

interface UserState {
  user: User | null;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}));
```

**사용**:

```tsx
function Header() {
  const user = useUserStore((state) => state.user);
  const logout = useUserStore((state) => state.logout);
  
  return (
    <div>
      {user ? (
        <>
          <span>{[user.name](http://user.name)}</span>
          <button onClick={logout}>로그아웃</button>
        </>
      ) : (
        <button>로그인</button>
      )}
    </div>
  );
}
```

---

## 2.2 미들웨어 (persist)

```tsx
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  setToken: (token: string) => void;
  clearToken: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      setToken: (token) => set({ token }),
      clearToken: () => set({ token: null }),
    }),
    {
      name: 'auth-storage',  // localStorage key
    }
  )
);
```

---

## 2.3 비동기 액션

```tsx
interface TodoState {
  todos: Todo[];
  fetchTodos: () => Promise<void>;
  addTodo: (text: string) => Promise<void>;
}

export const useTodoStore = create<TodoState>((set, get) => ({
  todos: [],
  
  fetchTodos: async () => {
    const response = await fetch('/api/todos');
    const data = await response.json();
    set({ todos: data });
  },
  
  addTodo: async (text) => {
    const response = await fetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
    const newTodo = await response.json();
    set({ todos: [...get().todos, newTodo] });
  },
}));
```

---

# 3. React Hook Form

## 3.1 기본 사용

```bash
npm install react-hook-form
```

```tsx
import { useForm } from 'react-hook-form';

interface LoginFormData {
  email: string;
  password: string;
}

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>();
  
  const onSubmit = (data: LoginFormData) => {
    console.log(data);
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input 
        {...register('email', { 
          required: '이메일을 입력하세요',
          pattern: {
            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
            message: '올바른 이메일 형식이 아닙니다',
          },
        })}
        placeholder="이메일"
      />
      {[errors.email](http://errors.email) && <span>{[errors.email](http://errors.email).message}</span>}
      
      <input 
        type="password"
        {...register('password', { 
          required: '비밀번호를 입력하세요',
          minLength: {
            value: 6,
            message: '최소 6자 이상',
          },
        })}
        placeholder="비밀번호"
      />
      {errors.password && <span>{errors.password.message}</span>}
      
      <button type="submit">로그인</button>
    </form>
  );
}
```

---

## 3.2 Zod로 스키마 검증

```bash
npm install zod @hookform/resolvers
```

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email('올바른 이메일 형식이 아닙니다'),
  password: z.string().min(6, '최소 6자 이상'),
});

type LoginFormData = z.infer<typeof loginSchema>;

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });
  
  const onSubmit = (data: LoginFormData) => {
    console.log(data);  // 타입 안전!
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {[errors.email](http://errors.email) && <span>{[errors.email](http://errors.email).message}</span>}
      
      <input type="password" {...register('password')} />
      {errors.password && <span>{errors.password.message}</span>}
      
      <button type="submit">로그인</button>
    </form>
  );
}
```

---

# 4. Zustand + React Hook Form 통합

## 4.1 로그인 실전 예제

```tsx
// store/authStore.ts
interface AuthState {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  
  login: async (email, password) => {
    const response = await fetch('/api/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    const user = await response.json();
    set({ user });
  },
  
  logout: () => set({ user: null }),
}));
```

```tsx
// LoginForm.tsx
const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});

type LoginFormData = z.infer<typeof loginSchema>;

function LoginForm() {
  const login = useAuthStore((state) => state.login);
  const [isLoading, setIsLoading] = useState(false);
  
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });
  
  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      await login([data.email](http://data.email), data.password);
      // 성공 시 리다이렉트
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {[errors.email](http://errors.email) && <span>{[errors.email](http://errors.email).message}</span>}
      
      <input type="password" {...register('password')} />
      {errors.password && <span>{errors.password.message}</span>}
      
      <button disabled={isLoading}>
        {isLoading ? '로그인 중...' : '로그인'}
      </button>
    </form>
  );
}
```

---

# 5. 고급 패턴

## 5.1 동적 필드 (useFieldArray)

```tsx
import { useForm, useFieldArray } from 'react-hook-form';

interface FormData {
  items: { name: string; quantity: number }[];
}

function DynamicForm() {
  const { register, control, handleSubmit } = useForm<FormData>({
    defaultValues: {
      items: [{ name: '', quantity: 0 }],
    },
  });
  
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });
  
  return (
    <form onSubmit={handleSubmit(data => console.log(data))}>
      {[fields.map](http://fields.map)((field, index) => (
        <div key={[field.id](http://field.id)}>
          <input {...register(`items.${index}.name`)} />
          <input type="number" {...register(`items.${index}.quantity`)} />
          <button type="button" onClick={() => remove(index)}>삭제</button>
        </div>
      ))}
      <button type="button" onClick={() => append({ name: '', quantity: 0 })}>
        추가
      </button>
      <button type="submit">제출</button>
    </form>
  );
}
```

---

## 5.2 Zustand DevTools

```tsx
import { devtools } from 'zustand/middleware';

export const useStore = create<State>()(  
  devtools(
    (set) => ({
      // state...
    }),
    { name: 'MyStore' }  // DevTools에서 볼 이름
  )
);
```

---

# 6. Interview Readiness

## ▶ Q1: Zustand vs Redux 차이는?

**A**:

| 구분 | Zustand | Redux |
| --- | --- | --- |
| **보일러플레이트** | 거의 없음 | 많음 |
| **번들 크기** | 1KB | 15KB+ |
| **설정** | 간단 | 복잡 |
| **TypeScript** | 우수 | 보통 |

---

## ▶ Q2: React Hook Form이 빠른 이유는?

**A**: **비제어 컴포넌트** 방식을 사용하기 때문입니다. 일반적인 useState 방식은 매 키입마다 리렌더링이 발생하지만, React Hook Form은 ref를 사용하여 **리렌더링을 최소화**합니다.

---

## ▶ Q3: Zod를 사용하는 이유는?

**A**: 

1. **타입 안전성**: TypeScript 타입 자동 추론
2. **선언적**: 스키마로 검증 규칙 명확하게 표현
3. **재사용성**: 프론트와 백엔드에서 동일한 스키마 사용 가능

---

## 🔑 핵심 체크리스트

- [ ]  Zustand로 간단한 상태 관리
- [ ]  persist 미들웨어로 localStorage 저장
- [ ]  React Hook Form으로 폼 처리
- [ ]  Zod로 타입 안전한 유효성 검증
- [ ]  useFieldArray로 동적 필드
- [ ]  비제어 컴포넌트로 성능 최적화

---

**작성일**: 2026-01-18  

**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)