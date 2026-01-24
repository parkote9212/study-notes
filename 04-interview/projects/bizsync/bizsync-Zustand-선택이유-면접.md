---
tags:
  - interview
  - react
  - zustand
  - bizsync
  - project
created: 2025-01-23
difficulty: 중
---

# BizSync - Zustand 선택 이유

## 질문
> Zustand를 Redux나 Recoil 대신 선택한 이유는 무엇인가요?

## 핵심 답변 (3줄)
1. **보일러플레이트 최소화** - Redux 대비 액션/리듀서 없이 간결한 코드로 상태 관리 가능
2. **번들 사이즈** - 약 1KB로 매우 가벼움 (Redux Toolkit: ~40KB)
3. **React 외부에서도 사용 가능** - WebSocket 콜백 등에서 직접 상태 접근 가능

## 상세 설명
```typescript
// Zustand - 간결한 스토어 정의
export const useKanbanStore = create<KanbanStore>((set) => ({
  currentBoard: null,
  setBoard: (board) => set({ currentBoard: board }),
  updateTask: (taskId, updates) => set((state) => ({
    currentBoard: {
      ...state.currentBoard,
      columns: state.currentBoard.columns.map(col => ({
        ...col,
        tasks: col.tasks.map(task => 
          task.taskId === taskId ? { ...task, ...updates } : task
        )
      }))
    }
  }))
}));

// Redux였다면 - 액션 타입, 액션 생성자, 리듀서 모두 필요
```

## 꼬리 질문 예상
- Zustand의 `set` 함수에서 불변성은 어떻게 유지하나요?
- `persist` 미들웨어를 사용하지 않은 이유는?

## 참고
- [[React-상태관리-비교]]
- [[Zustand-공식문서]]
