---
tags:
  - interview
  - zustand
  - persist
  - state-management
  - bizsync
  - project
created: 2025-02-05
difficulty: 중
---

# BizSync - Zustand Persist로 사용자 정보 영속화

## 질문
> Zustand의 persist 미들웨어를 사용한 이유와 구현 방법을 설명해주세요.

## 핵심 답변 (3줄)
1. **문제**: 새로고침 시 로그인 정보가 사라져 매번 재로그인 필요
2. **해결**: Zustand의 `persist` 미들웨어로 localStorage에 사용자 정보 자동 저장/복원
3. **결과**: 페이지 새로고침 후에도 로그인 상태 유지, 타입 안전성 확보

## 상세 설명

### 배경
React의 상태(state)는 메모리에만 존재하므로, 새로고침하면 모든 상태가 초기화됩니다. JWT 토큰은 `axios` 인터셉터로 관리하지만, 사용자 정보(이름, 이메일, 역할 등)는 별도 저장이 필요했습니다.

### 왜 Zustand Persist인가?

**대안 비교**
| 방식 | 장점 | 단점 |
|------|------|------|
| **직접 localStorage** | 간단 | 매번 JSON.parse/stringify, 타입 안전성 없음 |
| **Redux Persist** | 강력한 기능 | 설정 복잡, 번들 크기 큼 |
| **Zustand Persist** | 간결한 API, 타입 안전 | - |

✅ **Zustand Persist의 장점**
- 한 줄 설정으로 localStorage 동기화
- TypeScript 타입 추론 완벽 지원
- Hydration (복원) 시 데이터 변환 가능
- 선택적 필드만 영속화 가능

### 구현 방법

**1단계: persist 미들웨어 적용**
```tsx
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export const useUserStore = create<UserStore>()(
  persist(
    (set) => ({
      user: initialUser,
      setUser: (userData) =>
        set((state) => ({
          user: { ...state.user, ...userData },
        })),
      clearUser: () => set({ user: initialUser }),
    }),
    {
      name: "user-storage",  // localStorage 키 이름
      storage: createJSONStorage(() => localStorage),
    }
  )
);
```

**2단계: userId 타입 변환 (Hydration Hook)**
```tsx
export const useUserStore = create<UserStore>()(
  persist(
    // ... 상태 정의
    {
      name: "user-storage",
      storage: createJSONStorage(() => localStorage),
      
      // localStorage에서 복원 시 userId를 number로 변환
      onRehydrateStorage: () => (state) => {
        if (state?.user?.userId !== undefined && state.user.userId !== null) {
          state.user.userId = Number(state.user.userId);  // 문자열 → 숫자 변환
        }
      },
    }
  )
);
```

**왜 타입 변환이 필요한가?**
- localStorage는 JSON.stringify로 저장 → 숫자도 문자열로 저장될 수 있음
- TypeScript는 `userId: number`로 정의했지만, 복원 시 문자열일 수 있음
- `onRehydrateStorage`로 복원 직후 타입 보장

**3단계: 컴포넌트에서 사용**
```tsx
const LoginPage = () => {
  const { setUser } = useUserStore();
  
  const handleLogin = async (email, password) => {
    const response = await authApi.login(email, password);
    
    // localStorage에 자동 저장됨
    setUser({
      userId: response.userId,
      name: response.name,
      email: response.email,
      role: response.role,
    });
    
    navigate('/dashboard');
  };
};
```

### Persist vs Non-Persist 구분

BizSync에서는 **스토어마다 persist 여부를 구분**했습니다.

**Persist 사용 (localStorage 저장)**
- ✅ `userStore`: 사용자 정보
- ✅ `themeStore`: 테마 설정 (다크모드 등)

**Persist 미사용 (메모리만 사용)**
- ❌ `kanbanStore`: 칸반 보드 데이터 (API에서 매번 조회)
- ❌ `notificationStore`: 알림 목록 (실시간 웹소켓)

**이유**: 
- 보드 데이터는 실시간 협업이므로 localStorage에 저장하면 **동기화 문제** 발생
- 사용자 정보는 변경 빈도가 낮아 캐싱 효과 좋음

### 주의사항
- **보안**: 민감 정보는 저장 금지 (토큰은 httpOnly 쿠키 권장)
- **용량**: localStorage는 5MB 제한 (큰 데이터는 IndexedDB)
- **SSR**: Next.js에서는 `typeof window !== 'undefined'` 체크 필요

## 코드 예시
```tsx
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

// 사용자 정보 타입
export interface UserInfo {
  userId: number | null;
  name: string | null;
  email: string | null;
  role: string | null;
}

// User Store 인터페이스
interface UserStore {
  user: UserInfo;
  setUser: (user: Partial<UserInfo>) => void;
  clearUser: () => void;
}

// 초기 상태
const initialUser: UserInfo = {
  userId: null,
  name: null,
  email: null,
  role: null,
};

// User Store 생성 (persist 미들웨어)
export const useUserStore = create<UserStore>()(
  persist(
    (set) => ({
      user: initialUser,
      
      setUser: (userData) =>
        set((state) => ({
          user: { 
            ...state.user, 
            ...userData,
            // userId를 명시적으로 number로 변환
            userId: userData.userId !== undefined 
              ? Number(userData.userId)
              : state.user.userId
          },
        })),
      
      clearUser: () => set({ user: initialUser }),
    }),
    {
      name: "user-storage",  // localStorage 키
      storage: createJSONStorage(() => localStorage),
      
      // localStorage에서 복원 시 타입 보장
      onRehydrateStorage: () => (state) => {
        if (state?.user?.userId !== undefined && state.user.userId !== null) {
          state.user.userId = Number(state.user.userId);
        }
      },
    }
  )
);

// 사용 예시
const App = () => {
  const { user, setUser, clearUser } = useUserStore();
  
  return (
    <div>
      {user.userId ? (
        <>
          <p>안녕하세요, {user.name}님!</p>
          <button onClick={clearUser}>로그아웃</button>
        </>
      ) : (
        <p>로그인해주세요</p>
      )}
    </div>
  );
};
```

## 꼬리 질문 예상
- localStorage의 용량 제한은?
  → 도메인당 약 5MB (브라우저마다 다름)
- sessionStorage와의 차이는?
  → sessionStorage는 탭 닫으면 사라짐, localStorage는 영구 보관
- persist 말고 다른 방법은?
  → Redux Persist, Recoil Persist, 직접 localStorage 관리

## 참고
- [[bizsync-Zustand-선택이유-면접]]
- Zustand 공식 문서
