---
tags:
  - interview
  - material-ui
  - mui
  - react
  - design-system
  - bizsync
  - project
created: 2025-02-05
difficulty: 중
---

# BizSync - Material-UI(MUI) 선택 이유와 활용

## 질문
> React UI 라이브러리로 Material-UI를 선택한 이유는 무엇인가요?

## 핵심 답변 (3줄)
1. **개발 속도**: 완성도 높은 컴포넌트로 빠른 프로토타이핑 (버튼, 다이얼로그, 카드, 테이블 등)
2. **디자인 일관성**: Google Material Design 기반으로 통일된 UX 제공
3. **기능 풍부**: 반응형, 다크모드, 접근성, 커스터마이징 쉬움

## 상세 설명

### 배경
BizSync는 B2B 협업 도구로, **빠른 개발**과 **직관적인 UI**가 중요했습니다. 처음부터 UI를 만들면 시간이 오래 걸리고, 디자인 일관성 유지가 어렵습니다. 검증된 UI 라이브러리가 필요했습니다.

### UI 라이브러리 비교

| 라이브러리 | 장점 | 단점 | BizSync 선택 이유 |
|-----------|------|------|------------------|
| **Material-UI** | 완성도 높음, 문서 풍부, 커스터마이징 쉬움 | 번들 크기 큼 | ✅ B2B 툴에 적합 |
| **Ant Design** | 엔터프라이즈 최적화, 테이블 강력 | 중국 디자인, 커스터마이징 어려움 | - |
| **Chakra UI** | 가볍고 빠름, 접근성 좋음 | 컴포넌트 수 적음 | - |
| **Tailwind CSS** | 유연함, 번들 작음 | 직접 만들어야 함 | - |

✅ **Material-UI 선택 이유**
1. **생산성**: 복잡한 컴포넌트(DataGrid, Autocomplete 등) 기본 제공
2. **익숙함**: Google Material Design으로 사용자가 직관적으로 이해
3. **TypeScript**: 타입 정의 완벽 지원
4. **커뮤니티**: 활발한 커뮤니티, 풍부한 예제

### BizSync에서 활용한 MUI 컴포넌트

**1. Layout Components**
- `Box`: Flexbox 기반 레이아웃 (`sx` prop으로 스타일링)
- `Stack`: 수직/수평 정렬
- `Grid`: 반응형 그리드

```tsx
<Box sx={{ display: 'flex', gap: 2, padding: 2 }}>
  <Card sx={{ flex: 1 }}>
    <CardContent>칸반 보드</CardContent>
  </Card>
</Box>
```

**2. Form Components**
- `TextField`: 입력 필드 (validation, error 표시)
- `Autocomplete`: 자동완성 검색
- `Button`, `IconButton`: 버튼

**3. Feedback Components**
- `Dialog`: 모달 창 (업무 생성, 프로젝트 설정)
- `Snackbar`: 토스트 알림
- `CircularProgress`: 로딩 스피너

**4. Data Display**
- `Card`: 업무 카드
- `Chip`: 태그, 상태 표시
- `Typography`: 텍스트 스타일링

### sx prop을 활용한 스타일링

MUI의 핵심은 **`sx` prop**입니다. Inline 스타일처럼 작성하지만, 테마와 반응형을 지원합니다.

```tsx
<Card
  sx={{
    minWidth: 250,
    maxWidth: 350,
    borderRadius: 2,
    boxShadow: 3,
    '&:hover': {
      boxShadow: 6,
      transform: 'translateY(-4px)',
    },
    // 반응형
    [theme.breakpoints.down('sm')]: {
      minWidth: '100%',
    },
  }}
>
  <CardContent>업무 카드</CardContent>
</Card>
```

### 테마 커스터마이징

```tsx
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',  // 브랜드 컬러
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Pretendard", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      {/* 앱 전체에 테마 적용 */}
    </ThemeProvider>
  );
}
```

### 다크모드 지원

```tsx
const theme = createTheme({
  palette: {
    mode: isDarkMode ? 'dark' : 'light',
  },
});
```

### 번들 크기 최적화

**문제**: MUI 전체를 import하면 번들이 큼
**해결**: Named Import로 필요한 것만 가져오기

```tsx
// ❌ 전체 import (번들 큼)
import * as MUI from '@mui/material';

// ✅ Named import (필요한 것만)
import { Button, Card, TextField } from '@mui/material';
```

### 접근성 (Accessibility)

MUI는 **WAI-ARIA** 표준을 준수하여 스크린 리더, 키보드 네비게이션을 지원합니다.

```tsx
<Button
  aria-label="업무 생성"
  onClick={handleCreateTask}
>
  <AddIcon />
</Button>
```

## 코드 예시
```tsx
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  Dialog, 
  TextField, 
  Typography 
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

const TaskCreateDialog = () => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={() => setOpen(true)}
        sx={{
          borderRadius: 2,
          textTransform: 'none',  // 대문자 변환 방지
        }}
      >
        업무 생성
      </Button>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <Box sx={{ padding: 3 }}>
          <Typography variant="h6" sx={{ marginBottom: 2 }}>
            새 업무 생성
          </Typography>

          <TextField
            label="업무 제목"
            fullWidth
            required
            sx={{ marginBottom: 2 }}
          />

          <TextField
            label="상세 내용"
            multiline
            rows={4}
            fullWidth
            sx={{ marginBottom: 2 }}
          />

          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
            <Button onClick={() => setOpen(false)}>취소</Button>
            <Button variant="contained">생성</Button>
          </Box>
        </Box>
      </Dialog>
    </>
  );
};
```

## 꼬리 질문 예상
- MUI의 `sx` prop과 `style` prop의 차이는?
  → `sx`는 테마, 반응형, 가상 선택자 지원, `style`은 plain CSS만
- 번들 크기가 크다는 단점은 어떻게 해결하나?
  → Named import, Tree-shaking, Code Splitting으로 최적화
- Emotion과 Styled-components의 차이는?
  → MUI는 Emotion 기반, Styled-components는 별도 라이브러리

## 참고
- [[bizsync-React-DragAndDrop-면접]]
- Material-UI 공식 문서
