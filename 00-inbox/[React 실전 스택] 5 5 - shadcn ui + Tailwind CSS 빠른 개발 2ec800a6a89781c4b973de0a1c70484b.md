# [React 실전 스택] 5/5 - shadcn/ui + Tailwind CSS 빠른 개발

🏷️기술 카테고리: Design Pattern, Frontend
💡핵심키워드: #디자인패턴
💼 면접 빈출도: 상
⚖️ 의사결정(A vs B): No
날짜: 2026년 1월 18일 오후 5:44
📅 다음 복습일: 2026년 1월 25일

# 1. Abstract: 핵심 요약

> **shadcn/ui**는 2023-2024년 가장 탁월한 성장세를 보인 UI 컴포넌트 라이브러리로, **Copy-Paste** 방식으로 컴포넌트를 프로젝트에 추가하여 **완전한 커스터마이징**이 가능합니다. **Tailwind CSS**와 **Radix UI**를 기반으로 하여 접근성과 디자인 시스템을 동시에 해결합니다.
> 

**핵심 원칙**:

- shadcn/ui: 커스터마이징 가능한 컴포넌트 (npm 패키지 X)
- Tailwind CSS: 유틸리티 클래스 기반 스타일링
- Radix UI: 접근성(a11y) 준수

---

# 2. Tailwind CSS 설치

## 2.1 Vite + Tailwind 설정

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

```jsx
// tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

## 2.2 기본 사용법

```tsx
// ✅ Utility-First CSS
function Button() {
  return (
    <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
      클릭
    </button>
  );
}

// ✅ 반응형 디자인
function Card() {
  return (
    <div className="w-full md:w-1/2 lg:w-1/3 p-4">
      <div className="bg-white rounded-lg shadow-md p-6">
        카드 컨텐트
      </div>
    </div>
  );
}

// ✅ Dark Mode
function ThemeToggle() {
  return (
    <div className="bg-white dark:bg-gray-800 text-black dark:text-white">
      테마
    </div>
  );
}
```

---

# 3. shadcn/ui 설치

## 3.1 초기 설정

```bash
npx shadcn@latest init
```

**설정 선택**:

- TypeScript: Yes
- Style: Default
- Base color: Slate
- CSS variables: Yes

---

## 3.2 컴포넌트 추가

```bash
# Button 컴포넌트 추가
npx shadcn@latest add button

# 여러 컴포넌트 한번에
npx shadcn@latest add button card input form
```

**생성된 파일**:

```
src/
├── components/
│   └── ui/
│       ├── button.tsx
│       ├── card.tsx
│       └── input.tsx
```

---

# 4. 주요 컴포넌트 사용법

## 4.1 Button

```tsx
import { Button } from '@/components/ui/button';

function Example() {
  return (
    <div className="flex gap-2">
      <Button>Default</Button>
      <Button variant="destructive">삭제</Button>
      <Button variant="outline">외곽선</Button>
      <Button variant="ghost">고스트</Button>
      <Button size="sm">작게</Button>
      <Button size="lg">크게</Button>
    </div>
  );
}
```

---

## 4.2 Card

```tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

function UserCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>사용자 정보</CardTitle>
      </CardHeader>
      <CardContent>
        <p>이름: John Doe</p>
        <p>이메일: [john@example.com](mailto:john@example.com)</p>
      </CardContent>
    </Card>
  );
}
```

---

## 4.3 Form + Input

```tsx
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useForm } from 'react-hook-form';

function LoginForm() {
  const { register, handleSubmit } = useForm();
  
  return (
    <form onSubmit={handleSubmit(data => console.log(data))} className="space-y-4">
      <div>
        <Label htmlFor="email">이메일</Label>
        <Input 
          id="email" 
          type="email" 
          {...register('email')} 
          placeholder="[example@email.com](mailto:example@email.com)"
        />
      </div>
      
      <div>
        <Label htmlFor="password">비밀번호</Label>
        <Input 
          id="password" 
          type="password" 
          {...register('password')}
        />
      </div>
      
      <Button type="submit" className="w-full">로그인</Button>
    </form>
  );
}
```

---

## 4.4 Dialog (Modal)

```tsx
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

function Example() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>모달 열기</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>확인하세요</DialogTitle>
        </DialogHeader>
        <p>정말로 삭제하시겠습니까?</p>
        <div className="flex justify-end gap-2">
          <Button variant="outline">취소</Button>
          <Button variant="destructive">삭제</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

---

# 5. 커스터마이징

## 5.1 테마 커스터마이징

```css
/* src/index.css */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    /* ... */
  }
  
  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... */
  }
}
```

---

## 5.2 컴포넌트 수정

```tsx
// components/ui/button.tsx
import { cn } from '@/lib/utils';

const Button = ({ className, variant, ...props }) => {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center",
        variant === "default" && "bg-primary text-primary-foreground",
        variant === "destructive" && "bg-red-500 text-white",
        className  // ✅ 커스텀 클래스 추가 가능
      )}
      {...props}
    />
  );
};
```

---

# 6. 실전 패턴

## 6.1 레이아웃 컴포넌트

```tsx
function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">Dashboard</h1>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>카드 1</CardTitle>
            </CardHeader>
            <CardContent>
              컨텐트
            </CardContent>
          </Card>
          {/* 반복... */}
        </div>
      </main>
    </div>
  );
}
```

---

## 6.2 Dark Mode 구현

```bash
npm install next-themes
```

```tsx
// providers/theme-provider.tsx
import { ThemeProvider as NextThemesProvider } from 'next-themes';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </NextThemesProvider>
  );
}
```

```tsx
// components/theme-toggle.tsx
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  
  return (
    <Button 
      variant="ghost" 
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      {theme === 'dark' ? '태양' : '달'}
    </Button>
  );
}
```

---

# 7. Interview Readiness

## ▶ Q1: shadcn/ui와 Material-UI 차이는?

**A**:

| 구분 | shadcn/ui | Material-UI |
| --- | --- | --- |
| **설치 방식** | Copy-Paste | npm install |
| **커스터마이징** | 완전 자유 | 제한적 |
| **번들 크기** | 사용한 것만 | 전체 라이브러리 |
| **소스코드** | 프로젝트 내부 | node_modules |

---

## ▶ Q2: Tailwind CSS의 장점은?

**A**:

1. **빠른 개발**: HTML에서 직접 스타일링
2. **일관성**: 디자인 시스템 강제
3. **Purge CSS**: 사용 안 한 클래스 자동 제거
4. **반응형**: `md:`, `lg:` 등 브레이크포인트 지원

---

## ▶ Q3: Radix UI를 사용하는 이유는?

**A**: **접근성(Accessibility)**을 기본으로 제공하기 때문입니다. 키보드 네비게이션, 스크린 리더 지원, ARIA 속성 등이 모두 구현되어 있어 **웹 표준을 준수**하며 모든 사용자가 사용할 수 있는 UI를 만들 수 있습니다.

---

## 🔑 핵심 체크리스트

- [ ]  Tailwind로 유틸리티 클래스 스타일링
- [ ]  shadcn/ui로 컴포넌트 추가
- [ ]  Copy-Paste 방식으로 완전 커스터마이징
- [ ]  CSS 변수로 테마 관리
- [ ]  Dark Mode 구현
- [ ]  반응형 디자인 (md:, lg:)
- [ ]  Radix UI로 접근성 보장

---

**작성일**: 2026-01-18  

**면접 빈출도**: ⭐⭐⭐⭐ (상)

---

## 🎉 [React 실전 스택] 시리즈 완료!

축하합니다! 5부작을 모두 완료하셨습니다. 이제 당신은:

- ✅ React 19의 최신 기능 이해
- ✅ Vite로 초고속 개발 환경 구축
- ✅ TanStack Query로 서버 상태 관리
- ✅ Zustand + React Hook Form으로 폼과 상태 관리
- ✅ shadcn/ui + Tailwind로 빠른 UI 개발

**다음 단계**: 실전 프로젝트에 적용하고 포트폴리오를 만들어보세요!