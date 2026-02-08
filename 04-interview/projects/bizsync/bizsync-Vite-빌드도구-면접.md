---
tags:
  - interview
  - vite
  - build-tool
  - react
  - bizsync
  - project
created: 2025-02-05
difficulty: 중
---

# BizSync - Vite를 빌드 도구로 선택한 이유

## 질문
> React 프로젝트에서 Create React App 대신 Vite를 선택한 이유는 무엇인가요?

## 핵심 답변 (3줄)
1. **개발 속도**: Vite는 개발 서버 시작이 **즉시**(Cold Start ~200ms), HMR(Hot Module Replacement)도 빠름
2. **빌드 성능**: esbuild 기반 사전 번들링 + Rollup 프로덕션 빌드로 **CRA 대비 10배 빠른 빌드**
3. **생태계**: TypeScript, React 19 기본 지원, 설정 간단, 최신 기술 스택 (ESM 기반)

## 상세 설명

### 배경
React 프로젝트를 시작할 때 전통적으로 CRA(Create React App)를 사용했지만, 2023년 React 공식 문서에서 CRA를 권장하지 않게 되었습니다. 대안으로 Vite, Next.js, Remix 등이 있지만, BizSync는 **SPA(Single Page Application)**이므로 Vite를 선택했습니다.

### Vite vs Create React App

| 항목 | Vite | Create React App |
|------|------|------------------|
| **개발 서버 시작** | ~200ms (즉시) | ~30초 (느림) |
| **HMR 속도** | 즉시 반영 | 느림 (전체 번들 재빌드) |
| **번들러** | esbuild + Rollup | Webpack |
| **TypeScript** | 기본 지원 | 추가 설정 필요 |
| **프로덕션 빌드** | 빠름 | 느림 |
| **유지보수** | 활발 | 중단 (2023년 권장 안 함) |

### Vite의 핵심 원리

**1. Native ESM 기반 개발 서버**
- 브라우저가 직접 ES Module을 로드
- 변경된 파일만 다시 로드 (전체 번들링 없음)
- 의존성은 esbuild로 사전 번들링 (Go 언어 기반, 초고속)

**2. HMR (Hot Module Replacement)**
```tsx
// 파일 수정 시 브라우저가 즉시 반영 (새로고침 없이)
import { useUserStore } from './stores/userStore';

// userStore.ts 수정 → HMR로 자동 업데이트 (상태 유지)
```

**3. esbuild 의존성 최적화**
- `node_modules`의 수백 개 파일을 단일 ESM 모듈로 번들링
- Go 언어로 작성되어 JavaScript 번들러보다 10~100배 빠름

### 실제 체감 차이

**개발 중**
- `npm run dev` 실행 → **즉시 서버 시작** (CRA는 30초 대기)
- 코드 수정 → **즉시 반영** (CRA는 3~5초 대기)
- 개발 생산성 대폭 향상

**프로덕션 빌드**
```bash
# Vite
npm run build
# → 10초 내 완료 (Rollup 기반)

# CRA
npm run build
# → 1~2분 소요 (Webpack 기반)
```

### 설정 비교

**Vite (vite.config.ts)**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8080',  // 백엔드 프록시
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
```

**CRA (craco.config.js 또는 eject 필요)**
- 설정 변경하려면 `eject` 필요 (되돌릴 수 없음)
- 또는 craco, react-app-rewired 같은 추가 도구 필요

### BizSync에서 Vite 활용

**1. 개발 환경 (.env)**
```bash
VITE_API_URL=http://localhost:8080
```

**2. 환경변수 사용**
```tsx
const API_URL = import.meta.env.VITE_API_URL;  // Vite 방식
// const API_URL = process.env.REACT_APP_API_URL;  // CRA 방식
```

**3. Docker 멀티스테이지 빌드**
```dockerfile
# 빌드 스테이지
FROM node:21-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build  # Vite 빌드 (빠름!)

# 프로덕션 스테이지
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### 주의사항
- 환경변수는 `VITE_` 접두사 필수
- `import.meta.env` 사용 (CRA의 `process.env`와 다름)
- 일부 라이브러리는 CommonJS만 지원 (호환성 확인 필요)

## 코드 예시
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  
  // 개발 서버 설정
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
  
  // 빌드 설정
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          mui: ['@mui/material', '@mui/icons-material'],
        },
      },
    },
  },
  
  // TypeScript 경로 별칭
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
```

## 꼬리 질문 예상
- Vite가 프로덕션에서는 Rollup을 쓰는 이유는?
  → esbuild는 빠르지만 코드 스플리팅/트리 쉐이킹이 Rollup보다 약함
- Next.js와 Vite의 차이는?
  → Next.js는 SSR/SSG 프레임워크, Vite는 빌드 도구 (SPA에 적합)
- Webpack과의 차이는?
  → Webpack은 전체 번들링, Vite는 ESM + 필요한 것만 로드

## 참고
- [[bizsync-Docker-멀티스테이지빌드-면접]]
- Vite 공식 문서
