---
tags: study, Vite, React, Build-Tool
created: 2026-01-24
---

# Vite 개발환경

## 한 줄 요약
> Vite는 ES Modules와 esbuild를 활용하여 기존 Webpack/CRA 대비 10-100배 빠른 개발 서버를 제공하는 차세대 프론트엔드 빌드 도구

## 상세 설명

Vite는 개발 시 ES Modules를 브라우저에서 직접 실행하고(번들링 없음), 프로덕션 빌드는 Rollup으로 최적화된 번들을 생성하며, HMR로 변경된 모듈만 즉시 교체합니다.

### Vite 프로젝트 생성

```bash
npm create vite@latest my-react-app -- --template react-ts
cd my-react-app
npm install
npm run dev
```

### vite.config.ts 설정

**경로 별칭**:
- `@`를 src로 설정하여 상대 경로 간소화
- tsconfig.json과 동기화 필요

**개발 서버**:
- 포트, 자동 오픈, 프록시 설정

**빌드 설정**:
- 출력 디렉토리, 소스맵, 코드 스플리팅

### 환경변수 관리

- `VITE_` 접두어 필수 (클라이언트 노출)
- .env.development, .env.production 분리
- `import.meta.env.VITE_API_URL`로 접근

### Vite vs Webpack/CRA

| 구분 | Vite | Webpack (CRA) |
|------|------|---------------|
| **콜드 스타트** | 0.5초 | 10초 |
| **HMR** | 즉시 | 1-3초 |
| **빌드 속도** | 10초 | 60초 |
| **번들 크기** | 작음 | 큼 |

**Vite 장점**:
- ES Modules 기반 (Native ESM)
- esbuild로 초고속 분석
- 설정이 간단함

## 코드 예시

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },
});

// .env.development
VITE_API_URL=http://localhost:8080

// .env.production
VITE_API_URL=https://api.example.com

// 사용
const apiUrl = import.meta.env.VITE_API_URL;
```

## 주의사항 / 함정

1. **환경변수 접두어**: `VITE_` 없으면 노출 안 됨
2. **프록시 CORS**: 개발 서버의 프록시로 CORS 문제 해결
3. **IE11 미지원**: 레거시 브라우저는 플러그인 필요
4. **경로 별칭**: vite.config.ts와 tsconfig.json 모두 설정

## 관련 개념
- [[React-개발환경]]
- [[ES-Modules]]
- [[esbuild]]
- [[Webpack-비교]]

## 면접 질문
1. Vite가 빠른 이유는?
2. Vite의 프록시 설정을 사용하는 이유는?
3. CRA에서 Vite로 마이그레이션하려면?

## 참고 자료
- Vite 공식 문서
