---
tags: interview, react, zustand, bizsync, project
created: 2025-01-23
difficulty: 중
---

# BizSync - React + Zustand 상태관리 면접

## 질문 1: Zustand를 선택한 이유
> Zustand를 Redux나 Recoil 대신 선택한 이유는 무엇인가요?

### 핵심 답변 (3줄)
1. **보일러플레이트 최소화** - Redux 대비 액션/리듀서 없이 간결한 코드로 상태 관리 가능
2. **번들 사이즈** - 약 1KB로 매우 가벼움 (Redux Toolkit: ~40KB)
3. **React 외부에서도 사용 가능** - WebSocket 콜백 등에서 직접 상태 접근 가능

### 상세 설명
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

### 꼬리 질문 예상
- Zustand의 `set` 함수에서 불변성은 어떻게 유지하나요?
- `persist` 미들웨어를 사용하지 않은 이유는?

---

## 질문 2: 칸반 보드 상태 설계
> 칸반 보드의 복잡한 중첩 상태(Board → Column → Task)를 어떻게 관리했나요?

### 핵심 답변 (3줄)
1. **정규화 대신 중첩 구조 유지** - API 응답 구조와 일치시켜 변환 로직 제거
2. **Immer 없이 불변성 유지** - spread 연산자로 깊은 복사 수행
3. **낙관적 업데이트** - UI 먼저 변경 후 API 요청으로 사용자 경험 향상

### 상세 설명
```typescript
// 작업 이동 시 상태 업데이트 (컬럼 간 이동)
moveTask: (taskId, fromColumnId, toColumnId, newIndex) => 
  set((state) => {
    const board = state.currentBoard;
    if (!board) return state;

    // 1. 원본 컬럼에서 태스크 제거
    const task = board.columns
      .find(c => c.columnId === fromColumnId)
      ?.tasks.find(t => t.taskId === taskId);

    // 2. 대상 컬럼에 태스크 추가
    const updatedColumns = board.columns.map(col => {
      if (col.columnId === fromColumnId) {
        return { ...col, tasks: col.tasks.filter(t => t.taskId !== taskId) };
      }
      if (col.columnId === toColumnId) {
        const newTasks = [...col.tasks];
        newTasks.splice(newIndex, 0, task!);
        return { ...col, tasks: newTasks };
      }
      return col;
    });

    return { currentBoard: { ...board, columns: updatedColumns } };
  })
```

### 꼬리 질문 예상
- 정규화(normalization)했다면 어떤 구조가 되었을까요?
- Immer를 사용했다면 코드가 어떻게 달라졌을까요?

---

## 질문 3: WebSocket과 Zustand 통합
> 실시간 업데이트를 위한 WebSocket 이벤트와 Zustand 상태를 어떻게 연결했나요?

### 핵심 답변 (3줄)
1. **커스텀 훅으로 분리** - `useBoardSocket` 훅에서 연결/구독 로직 캡슐화
2. **콜백 패턴 사용** - 소켓 이벤트 발생 시 부모의 refetch 함수 호출
3. **useRef로 클라이언트 관리** - 리렌더링과 무관하게 WebSocket 인스턴스 유지

### 상세 설명
```typescript
// useBoardSocket.ts
export const useBoardSocket = (projectId: string | undefined, onUpdate: () => void) => {
  const client = useRef<Client | null>(null);

  useEffect(() => {
    if (!projectId) return;

    client.current = new Client({
      brokerURL: import.meta.env.VITE_WS_URL,
      reconnectDelay: 5000,
      onConnect: () => {
        // 구독: 해당 프로젝트의 보드 변경 알림
        client.current?.subscribe(`/topic/projects/${projectId}`, (message) => {
          if (message.body === "BOARD_UPDATE") {
            onUpdate(); // API 재호출로 최신 데이터 동기화
          }
        });
      }
    });

    client.current.activate();
    return () => client.current?.deactivate();
  }, [projectId, onUpdate]);
};

// 사용처 (KanbanBoardPage)
const fetchBoard = useCallback(async () => {
  const data = await api.get(`/projects/${projectId}/board`);
  setBoard(data);
}, [projectId]);

useBoardSocket(projectId, fetchBoard);
```

### 꼬리 질문 예상
- `onUpdate`를 `useCallback`으로 감싸야 하는 이유는?
- 서버에서 변경된 데이터만 보내는 방식(delta sync)은 왜 선택하지 않았나요?

---

## 질문 4: 여러 Store 분리 전략
> 프로젝트에서 여러 개의 Store(user, project, kanban, notification)를 어떻게 분리했나요?

### 핵심 답변 (3줄)
1. **도메인별 분리** - 각 기능 영역별로 독립적인 store 생성
2. **store 간 의존성 최소화** - 필요시 컴포넌트 레벨에서 조합
3. **persist 선택적 적용** - userStore만 localStorage 연동 (인증 토큰)

### 상세 설명
```
stores/
├── userStore.ts      # 인증 상태, 사용자 정보 (persist)
├── projectStore.ts   # 프로젝트 목록, 선택된 프로젝트
├── kanbanStore.ts    # 칸반 보드 데이터 (API 의존)
├── approvalStore.ts  # 결재 문서 상태
├── notificationStore.ts  # 알림 목록
└── uiStore.ts        # 다이얼로그, 사이드바 상태
```

```typescript
// 컴포넌트에서 필요한 store만 선택적으로 import
const KanbanBoardPage = () => {
  const user = useUserStore(state => state.user);
  const { currentBoard, setBoard } = useKanbanStore();
  // ...
};
```

### 꼬리 질문 예상
- Store 간 데이터 공유가 필요하면 어떻게 처리하나요?
- 전역 상태가 너무 많아지면 어떤 문제가 생길 수 있나요?

---

## 질문 5: React 19 + TypeScript 타입 안정성
> TypeScript를 활용해 상태 관리의 타입 안정성을 어떻게 확보했나요?

### 핵심 답변 (3줄)
1. **Store 인터페이스 정의** - 상태와 액션을 포함한 전체 타입 명시
2. **API 응답 타입 분리** - `types/` 폴더에 도메인별 타입 정의
3. **Generic 활용** - `create<KanbanStore>()` 형태로 타입 추론 강화

### 상세 설명
```typescript
// types/kanban.ts
export interface Task {
  taskId: number;
  title: string;
  content?: string;
  assigneeName?: string;
  deadline?: string;
  sequence: number;
}

export interface Column {
  columnId: number;
  name: string;
  columnType: 'TODO' | 'IN_PROGRESS' | 'DONE' | 'CUSTOM';
  sequence: number;
  tasks: Task[];
}

export interface BoardData {
  projectId: number;
  projectName: string;
  myRole: string;
  columns: Column[];
}

// Store 인터페이스
interface KanbanStore {
  currentBoard: BoardData | null;
  setBoard: (board: BoardData | null) => void;
  updateTask: (taskId: number, updates: Partial<Task>) => void;
  // ...
}
```

### 꼬리 질문 예상
- `Partial<Task>`를 사용한 이유는?
- API 응답 타입과 Store 타입이 다를 때 어떻게 처리하나요?

---

## 참고
- [[React-상태관리-비교]]
- [[Zustand-공식문서]]
- [[bizsync-면접-WebSocket-STOMP]]
