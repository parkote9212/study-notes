---
tags: study, React, Authentication, Router, TypeScript
created: 2026-01-20
---

# ProtectedRoute 패턴으로 인증 페이지 보호

## 한 줄 요약
> React Router의 고차 컴포넌트 패턴으로 인증되지 않은 사용자의 페이지 접근을 차단하고 로그인 페이지로 리다이렉트

## 상세 설명

### 문제 상황
- URL에 `/projects` 직접 입력하면 로그인 없이 페이지 접근 가능
- API 호출은 실패하지만 페이지는 렌더링됨 (보안 취약)

### 해결: ProtectedRoute 컴포넌트

**동작 흐름:**
```
사용자 요청
    ↓
ProtectedRoute 실행
    ↓
토큰 확인
    ├─ 있음 + 유효 → 페이지 렌더링 ✅
    └─ 없음 or 만료 → /login 리다이렉트 ❌
```

## 코드 예시
```tsx
// 1. ProtectedRoute 컴포넌트
import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export default ProtectedRoute;

// 2. auth 유틸리티
export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('accessToken');
  if (!token) return false;
  
  // JWT 토큰 만료 체크
  try {
    const payload = parseJwt(token);
    const currentTime = Date.now() / 1000;
    
    if (payload.exp && payload.exp > currentTime) {
      return true;
    }
    
    // 만료된 토큰 제거
    clearTokens();
    return false;
  } catch (error) {
    clearTokens();
    return false;
  }
};

// JWT 파싱
const parseJwt = (token: string): any => {
  const base64Url = token.split('.')[1];
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  const jsonPayload = decodeURIComponent(
    atob(base64)
      .split('')
      .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
      .join('')
  );
  return JSON.parse(jsonPayload);
};

// 3. App.tsx에 적용
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/* 인증 필요한 페이지들 */}
        <Route path="/projects" element={
          <ProtectedRoute>
            <ProjectListPage />
          </ProtectedRoute>
        } />
        
        <Route path="/projects/:projectId" element={
          <ProtectedRoute>
            <KanbanBoardPage />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}
```

## 주의사항 / 함정

1. **replace 속성 필수**
   ```tsx
   <Navigate to="/login" replace />
   // replace 없으면 뒤로가기로 보호된 페이지 재접근 가능
   ```

2. **JWT 만료 체크**
   ```typescript
   // ❌ 잘못된 시간 비교
   decoded.exp < Date.now()  // exp는 초, Date.now()는 밀리초
   
   // ✅ 올바른 비교
   decoded.exp < Date.now() / 1000
   ```

3. **클라이언트 검증 ≠ 보안**
   - ProtectedRoute는 UX 개선용
   - 백엔드 API도 반드시 토큰 검증 필요 (2중 방어)
   - 개발자 도구로 localStorage 조작 가능

4. **토큰 저장 위치**
   - localStorage: XSS 공격 취약
   - httpOnly Cookie: 더 안전하지만 CORS 설정 복잡
   - BizSync: localStorage 사용 (간단한 프로젝트)

5. **try-catch 필수**
   - 잘못된 토큰 형식일 수 있음
   - atob(), JSON.parse() 모두 예외 발생 가능
   ```typescript
   try {
     const payload = parseJwt(token);
   } catch (error) {
     clearTokens();  // 파싱 실패 시 토큰 제거
     return false;
   }
   ```

## 관련 개념
- [[React_Router_v6]]
- [[JWT_토큰_인증]]
- [[고차_컴포넌트_패턴]]
- [[localStorage_vs_Cookie]]
- [[Base64_인코딩]]

## 면접 질문
1. ProtectedRoute가 무엇이며 왜 사용하나?
2. Navigate 컴포넌트의 replace 속성은 무엇인가?
3. 클라이언트 사이드 인증만으로 보안이 충분한가?
4. JWT 토큰을 어디에 저장하는 것이 안전한가?

## 참고 자료
- React Router v6 공식 문서
- 실무 프로젝트: BizSync 프론트엔드 인증 처리
