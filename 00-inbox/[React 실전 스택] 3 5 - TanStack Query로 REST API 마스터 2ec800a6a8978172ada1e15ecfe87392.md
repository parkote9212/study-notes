# [React 실전 스택] 3/5 - TanStack Query로 REST API 마스터

🏷️기술 카테고리: Frontend
💡핵심키워드: #성능최적화, #캐싱
💼 면접 빈출도: 최상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 18일 오후 5:40
📅 다음 복습일: 2026년 1월 25일

# 1. Abstract: 핵심 요약

> **TanStack Query**(React Query v5)는 서버 상태 관리의 표준으로, **캐싱**, **자동 재요청**, **백그라운드 동기화** 등을 제공하여 REST API 통신을 혁신적으로 간소화합니다. useEffect + useState를 대체하는 필수 라이브러리입니다.
> 

**핵심 원칙**:

- useQuery: 데이터 조회 (GET)
- useMutation: 데이터 변경 (POST/PUT/DELETE)
- Automatic Refetch: 실시간 데이터 동기화

---

# 2. 설치 및 초기 설정

## 2.1 설치

```bash
npm install @tanstack/react-query
npm install -D @tanstack/react-query-devtools
```

---

## 2.2 QueryClient 설정

```tsx
// src/main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,  // 5분
      gcTime: 1000 * 60 * 10,     // 10분 (cacheTime 후속)
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

---

# 3. useQuery - 데이터 조회

## 3.1 기본 사용법

```tsx
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

interface User {
  id: number;
  name: string;
  email: string;
}

const fetchUser = async (userId: number): Promise<User> => {
  const { data } = await axios.get(`/api/users/${userId}`);
  return data;
};

function UserProfile({ userId }: { userId: number }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return <div>{[data.name](http://data.name)}</div>;
}
```

**queryKey**:

- 배열 형태
- 캐시 식별자
- 의존성으로 사용 (userId 변경 시 재요청)

---

## 3.2 페이지네이션

```tsx
function UserList() {
  const [page, setPage] = useState(1);
  
  const { data, isLoading } = useQuery({
    queryKey: ['users', page],
    queryFn: () => axios.get(`/api/users?page=${page}`),
    placeholderData: (prev) => prev,  // 이전 데이터 유지
  });
  
  return (
    <div>
      {data?.[data.map](http://data.map)(user => <div key={[user.id](http://user.id)}>{[user.name](http://user.name)}</div>)}
      <button onClick={() => setPage(p => p - 1)}>이전</button>
      <button onClick={() => setPage(p => p + 1)}>다음</button>
    </div>
  );
}
```

---

# 4. useMutation - 데이터 변경

## 4.1 POST 요청

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';

interface CreateUserDto {
  name: string;
  email: string;
}

function CreateUserForm() {
  const queryClient = useQueryClient();
  
  const mutation = useMutation({
    mutationFn: (newUser: CreateUserDto) => {
      return [axios.post](http://axios.post)('/api/users', newUser);
    },
    onSuccess: () => {
      // ✅ 성공 시 캐시 무효화
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    mutation.mutate({ name: 'John', email: '[john@example.com](mailto:john@example.com)' });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <button disabled={mutation.isPending}>
        {mutation.isPending ? '생성 중...' : '사용자 생성'}
      </button>
      {mutation.isError && <div>{mutation.error.message}</div>}
      {mutation.isSuccess && <div>성공!</div>}
    </form>
  );
}
```

---

## 4.2 Optimistic Update

```tsx
const mutation = useMutation({
  mutationFn: updateUser,
  onMutate: async (newUser) => {
    // ✅ 이전 쿼리 취소
    await queryClient.cancelQueries({ queryKey: ['user', [newUser.id](http://newUser.id)] });
    
    // ✅ 이전 데이터 백업
    const previous = queryClient.getQueryData(['user', [newUser.id](http://newUser.id)]);
    
    // ✅ Optimistic Update
    queryClient.setQueryData(['user', [newUser.id](http://newUser.id)], newUser);
    
    return { previous };
  },
  onError: (err, newUser, context) => {
    // ✅ 에러 시 롤백
    queryClient.setQueryData(['user', [newUser.id](http://newUser.id)], context?.previous);
  },
  onSettled: (newUser) => {
    queryClient.invalidateQueries({ queryKey: ['user', [newUser.id](http://newUser.id)] });
  },
});
```

---

# 5. 실전 패턴

## 5.1 API 함수 분리

```tsx
// src/api/users.ts
export const userApi = {
  getAll: () => axios.get<User[]>('/api/users'),
  getById: (id: number) => axios.get<User>(`/api/users/${id}`),
  create: (user: CreateUserDto) => [axios.post](http://axios.post)<User>('/api/users', user),
  update: (id: number, user: UpdateUserDto) => 
    axios.put<User>(`/api/users/${id}`, user),
  delete: (id: number) => axios.delete(`/api/users/${id}`),
};
```

---

## 5.2 Custom Hook

```tsx
// src/hooks/useUsers.ts
export const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const { data } = await userApi.getAll();
      return data;
    },
  });
};

export const useUser = (id: number) => {
  return useQuery({
    queryKey: ['user', id],
    queryFn: async () => {
      const { data } = await userApi.getById(id);
      return data;
    },
    enabled: !!id,  // id가 있을 때만 실행
  });
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: userApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
};
```

**사용**:

```tsx
function UserList() {
  const { data, isLoading } = useUsers();
  const createUser = useCreateUser();
  
  // ...
}
```

---

# 6. 고급 기능

## 6.1 Infinite Query (무한 스크롤)

```tsx
import { useInfiniteQuery } from '@tanstack/react-query';

function InfiniteUserList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['users', 'infinite'],
    queryFn: ({ pageParam = 1 }) => 
      axios.get(`/api/users?page=${pageParam}`),
    getNextPageParam: (lastPage, pages) => {
      return lastPage.hasMore ? pages.length + 1 : undefined;
    },
    initialPageParam: 1,
  });
  
  return (
    <div>
      {data?.[pages.map](http://pages.map)(page => 
        [page.data.map](http://page.data.map)(user => <div key={[user.id](http://user.id)}>{[user.name](http://user.name)}</div>)
      )}
      <button 
        onClick={() => fetchNextPage()}
        disabled={!hasNextPage || isFetchingNextPage}
      >
        {isFetchingNextPage ? '로딩...' : '더 보기'}
      </button>
    </div>
  );
}
```

---

## 6.2 Dependent Queries

```tsx
function UserPosts({ userId }: { userId: number }) {
  // 1. 유저 조회
  const { data: user } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => userApi.getById(userId),
  });
  
  // 2. 유저의 게시글 조회 (유저 데이터 있을 때만)
  const { data: posts } = useQuery({
    queryKey: ['posts', user?.id],
    queryFn: () => axios.get(`/api/posts?userId=${[user.id](http://user.id)}`),
    enabled: !!user,  // ✅ user가 있을 때만 실행
  });
  
  return <div>{posts?.length}개의 게시글</div>;
}
```

---

# 7. Interview Readiness

## ▶ Q1: TanStack Query를 사용하는 이유는?

**A**: 

1. **자동 캐싱**: 중복 요청 방지
2. **백그라운드 동기화**: 탭 전환 시 자동 재요청
3. **Loading/Error 상태 관리**: useEffect 없이 간편하게 관리
4. **Optimistic Update**: 빠른 UI 응답

---

## ▶ Q2: staleTime vs gcTime 차이는?

**A**:

- **staleTime**: 데이터가 신선한 상태로 유지되는 시간
- **gcTime**: 캐시된 데이터가 메모리에 유지되는 시간

```tsx
staleTime: 5분  // 5분간은 재요청 안 함
gcTime: 10분    // 10분 후 메모리에서 삭제
```

---

## ▶ Q3: invalidateQueries vs refetchQueries?

**A**:

- **invalidateQueries**: 캐시를 stale로 표시, 다음 사용시 재요청
- **refetchQueries**: 즉시 재요청

```tsx
// ✅ 대부분 invalidate 사용
queryClient.invalidateQueries({ queryKey: ['users'] });

// ✅ 즉시 동기화 필요한 경우
queryClient.refetchQueries({ queryKey: ['users'] });
```

---

## 🔑 핵심 체크리스트

- [ ]  QueryClient로 Provider 설정
- [ ]  useQuery로 GET 요청
- [ ]  useMutation으로 POST/PUT/DELETE
- [ ]  queryKey로 캐시 식별
- [ ]  invalidateQueries로 캐시 무효화
- [ ]  Custom Hook으로 재사용성 향상
- [ ]  enabled 옵션으로 조건부 실행

---

**작성일**: 2026-01-18  

**면접 빈출도**: ⭐⭐⭐⭐⭐ (최상)