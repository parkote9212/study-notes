---
tags:
  - study
  - TanStack-Query
  - React
  - Frontend
created: 2026-01-24
---

# TanStack Query REST API

## 한 줄 요약
> TanStack Query(React Query v5)는 서버 상태 관리의 표준으로 캐싱, 자동 재요청, 백그라운드 동기화를 제공하여 REST API 통신 간소화

## 상세 설명

TanStack Query는 useEffect + useState를 대체하여 서버 상태를 효율적으로 관리합니다. useQuery로 데이터 조회(GET), useMutation으로 데이터 변경(POST/PUT/DELETE)을 처리합니다.

### 핵심 개념

**useQuery - 데이터 조회**
- queryKey: 캐시 식별자
- queryFn: 데이터 페칭 함수
- 자동 캐싱 및 재요청

**useMutation - 데이터 변경**
- mutationFn: 변경 함수
- onSuccess: 성공 시 콜백
- invalidateQueries: 캐시 무효화

**staleTime vs gcTime**
- staleTime: 데이터가 신선한 상태로 유지되는 시간
- gcTime: 캐시된 데이터가 메모리에 유지되는 시간

**Optimistic Update**
- 서버 응답 전에 UI를 미리 업데이트
- 빠른 사용자 경험 제공

## 코드 예시

```typescript
// QueryClient 설정
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,  // 5분
      gcTime: 1000 * 60 * 10,     // 10분
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// useQuery 사용
const { data, isLoading, error } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId),
});

// useMutation 사용
const mutation = useMutation({
  mutationFn: (newUser: CreateUserDto) => axios.post('/api/users', newUser),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['users'] });
  },
});

// Custom Hook
export const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const { data } = await axios.get('/api/users');
      return data;
    },
  });
};

// Optimistic Update
const mutation = useMutation({
  mutationFn: updateUser,
  onMutate: async (newUser) => {
    await queryClient.cancelQueries({ queryKey: ['user', newUser.id] });
    const previous = queryClient.getQueryData(['user', newUser.id]);
    queryClient.setQueryData(['user', newUser.id], newUser);
    return { previous };
  },
  onError: (err, newUser, context) => {
    queryClient.setQueryData(['user', newUser.id], context?.previous);
  },
});
```

## 주의사항 / 함정

1. **queryKey 의존성**: queryKey가 바뀌면 자동 재요청
2. **staleTime 설정**: 너무 짧으면 불필요한 요청 증가
3. **invalidateQueries vs refetchQueries**: invalidate는 다음 사용시, refetch는 즉시
4. **enabled 옵션**: 조건부 실행 시 필수

## 관련 개념
- [[Server-State]]
- [[Client-State]]
- [[캐싱-전략]]
- [[Optimistic-Update]]

## 면접 질문
1. TanStack Query를 사용하는 이유는?
2. staleTime vs gcTime 차이는?
3. invalidateQueries vs refetchQueries?

## 참고 자료
- TanStack Query 공식 문서
