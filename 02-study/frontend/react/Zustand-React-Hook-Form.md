---
tags: study, Zustand, React-Hook-Form, React, Frontend
created: 2026-01-24
---

# Zustand React Hook Form

## 한 줄 요약
> Zustand는 Redux를 대체하는 초경량 상태관리 라이브러리, React Hook Form은 비제어 컴포넌트 방식으로 최소 리렌더링 폼 처리

## 상세 설명

Zustand는 보일러플레이트 없이 간결하게 상태를 관리하며, React Hook Form은 ref를 사용하여 매 키입력마다 리렌더링을 방지합니다.

### Zustand 핵심

**간단한 API**
- create()로 스토어 생성
- set()으로 상태 업데이트
- 미들웨어 지원 (persist, devtools)

**비동기 액션**
- 스토어 내부에서 async 함수 정의
- API 호출 후 상태 업데이트

### React Hook Form 핵심

**비제어 컴포넌트**
- ref로 입력값 관리
- 리렌더링 최소화
- 성능 우수

**Zod 스키마 검증**
- 타입 안전한 유효성 검증
- 자동 타입 추론
- 프론트/백엔드 공유 가능

## 코드 예시

```typescript
// Zustand 스토어
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
    { name: 'auth-storage' }
  )
);

// 사용
const token = useAuthStore((state) => state.token);
const setToken = useAuthStore((state) => state.setToken);

// React Hook Form + Zod
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
    console.log(data);
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
      
      <input type="password" {...register('password')} />
      {errors.password && <span>{errors.password.message}</span>}
      
      <button type="submit">로그인</button>
    </form>
  );
}

// 통합 예제: Zustand + React Hook Form
const login = useAuthStore((state) => state.login);

const onSubmit = async (data: LoginFormData) => {
  try {
    await login(data.email, data.password);
  } catch (error) {
    console.error(error);
  }
};
```

## 주의사항 / 함정

1. **Zustand vs Redux**: Zustand는 간단하지만 Redux는 성숙한 생태계
2. **비제어 컴포넌트**: 실시간 검증이 필요하면 watch() 사용
3. **Zod 스키마**: 프론트/백엔드 일치 확인 필요
4. **useFieldArray**: 동적 필드는 별도 Hook 사용

## 관련 개념
- [[상태관리]]
- [[비제어-컴포넌트]]
- [[스키마-검증]]
- [[Zod]]

## 면접 질문
1. Zustand vs Redux 차이는?
2. React Hook Form이 빠른 이유는?
3. Zod를 사용하는 이유는?

## 참고 자료
- Zustand 공식 문서
- React Hook Form 공식 문서
