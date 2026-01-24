---
tags: study, shadcn-ui, Tailwind-CSS, React, Frontend
created: 2026-01-24
---

# shadcn/ui Tailwind CSS

## 한 줄 요약
> shadcn/ui는 복사-붙여넣기 방식의 컴포넌트 라이브러리로 npm 설치가 아닌 소스 코드를 프로젝트에 직접 추가하여 완전한 커스터마이징 가능

## 상세 설명

shadcn/ui는 Radix UI + Tailwind CSS 기반의 컴포넌트로, 패키지 의존성 없이 코드를 직접 소유하여 수정 자유도가 높으며, Tailwind의 유틸리티 클래스로 빠르게 스타일링합니다.

### shadcn/ui 특징

**Copy-Paste 방식**:
- npm 패키지가 아님
- `npx shadcn-ui@latest add button`으로 컴포넌트 추가
- src/components/ui/에 코드가 생성됨
- 원하는 대로 수정 가능

**Radix UI 기반**:
- 접근성(a11y) 완벽 지원
- 키보드 네비게이션
- ARIA 속성 자동 적용

**Tailwind CSS**:
- 유틸리티 우선 CSS
- 빠른 스타일링
- Dark Mode 지원

### Tailwind CSS 핵심

**유틸리티 클래스**:
- `bg-blue-500`, `text-white`, `p-4`, `rounded-lg`
- HTML에서 직접 스타일링
- 빌드 시 사용된 클래스만 CSS에 포함

**반응형 디자인**:
- `sm:`, `md:`, `lg:`, `xl:` 접두어
- 모바일 우선(Mobile First)

**다크 모드**:
- `dark:` 접두어로 다크 모드 스타일 적용
- 자동 토글 지원

## 코드 예시

```bash
# shadcn/ui 초기화
npx shadcn-ui@latest init

# 컴포넌트 추가
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog

# 사용
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardContent } from "@/components/ui/card"

export default function App() {
  return (
    <Card>
      <CardHeader>
        <h2>제목</h2>
      </CardHeader>
      <CardContent>
        <p>내용</p>
        <Button variant="default">버튼</Button>
      </CardContent>
    </Card>
  )
}

// Tailwind 유틸리티 클래스
<div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md">
  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
    제목
  </h1>
  <Button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
    클릭
  </Button>
</div>

// 반응형 디자인
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <Card>카드 1</Card>
  <Card>카드 2</Card>
  <Card>카드 3</Card>
</div>

// 커스텀 컴포넌트
// src/components/ui/button.tsx (자동 생성됨)
import * as React from "react"
import { cn } from "@/lib/utils"

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", ...props }, ref) => {
    return (
      <button
        className={cn(
          "inline-flex items-center justify-center rounded-md text-sm font-medium",
          variant === "default" && "bg-primary text-primary-foreground hover:bg-primary/90",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
```

## 주의사항 / 함정

1. **npm 패키지 아님**: 코드가 프로젝트에 직접 추가됨
2. **업데이트**: 자동 업데이트 없음, 수동으로 코드 교체 필요
3. **Tailwind 필수**: Tailwind CSS 설정 필요
4. **중복 클래스**: cn() 유틸로 클래스 병합

## 관련 개념
- [[Radix-UI]]
- [[Tailwind-CSS]]
- [[유틸리티-우선-CSS]]
- [[접근성]]

## 면접 질문
1. shadcn/ui가 다른 UI 라이브러리와 다른 점은?
2. Tailwind CSS의 장점은?
3. 유틸리티 우선 CSS란?

## 참고 자료
- shadcn/ui 공식 문서
- Tailwind CSS 공식 문서
