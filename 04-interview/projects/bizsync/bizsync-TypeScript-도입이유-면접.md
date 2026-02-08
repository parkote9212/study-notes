---
tags:
  - interview
  - typescript
  - type-safety
  - react
  - bizsync
  - project
created: 2025-02-05
difficulty: 중
---

# BizSync - TypeScript 도입 이유와 효과

## 질문
> React 프로젝트에서 TypeScript를 도입한 이유와 실제 효과를 설명해주세요.

## 핵심 답변 (3줄)
1. **타입 안정성**: 컴파일 타임에 에러 발견 (런타임 에러 80% 감소)
2. **개발 생산성**: IDE 자동완성, 리팩토링 안전성, 코드 가독성 향상
3. **협업 효율**: 인터페이스로 API 스펙 명확화, 문서화 효과

## 상세 설명

### 배경
JavaScript는 동적 타입 언어라서 자유롭지만, 프로젝트가 커질수록 **타입 관련 버그**가 많아집니다. 특히 API 응답, 상태 관리, 컴포넌트 Props에서 실수가 자주 발생합니다.

### JavaScript의 문제점

```javascript
// JavaScript (❌ 런타임 에러)
function getUsername(user) {
  return user.name.toUpperCase();
}

getUsername(null);  // 💥 Cannot read property 'name' of null

// API 응답 타입 불명확
const response = await fetch('/api/user');
const data = await response.json();
console.log(data.userName);  // userName? username? 헷갈림
```

### TypeScript의 해결책

```typescript
// TypeScript (✅ 컴파일 타임 에러)
interface User {
  userId: number;
  name: string;
  email: string;
  role: 'ADMIN' | 'MANAGER' | 'MEMBER';  // Union Type
}

function getUsername(user: User | null): string {
  if (!user) return 'Unknown';  // null 체크 강제
  return user.name.toUpperCase();
}

getUsername(null);  // ✅ "Unknown" 반환
```

### BizSync에서 TypeScript 활용

**1. API 응답 타입 정의**
```typescript
// types/kanban.ts
export interface Task {
  taskId: number;
  title: string;
  content: string | null;
  deadline: string | null;
  worker: {
    userId: number;
    name: string;
    email: string;
  } | null;
  sequence: number;
}

export interface KanbanColumn {
  columnId: number;
  name: string;
  sequence: number;
  tasks: Task[];
}

export interface BoardData {
  projectId: number;
  projectName: string;
  columns: KanbanColumn[];
}

// API 호출
import { BoardData } from '../types/kanban';

async function fetchBoard(projectId: number): Promise<BoardData> {
  const response = await client.get<BoardData>(`/api/kanban/${projectId}`);
  return response.data;  // ✅ 타입 보장
}
```

**2. Zustand Store 타입 정의**
```typescript
interface KanbanStore {
  currentBoard: BoardData | null;
  filterStatus: string[];
  sortBy: "deadline" | "sequence" | "title" | null;
  sortOrder: "asc" | "desc";
  setBoard: (board: BoardData | null) => void;
  updateTask: (taskId: number, updates: Partial<Task>) => void;
}

export const useKanbanStore = create<KanbanStore>((set) => ({
  // ... 구현
}));

// 사용 시 자동완성 제공
const { currentBoard, setBoard } = useKanbanStore();
//      ^^^^^^^^^^^^ IDE가 타입 추론
```

**3. React Props 타입 정의**
```typescript
interface TaskCardProps {
  task: Task;
  onEdit: (taskId: number) => void;
  onDelete: (taskId: number) => void;
  isDragging?: boolean;  // Optional prop
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onEdit, onDelete, isDragging = false }) => {
  return (
    <Card onClick={() => onEdit(task.taskId)}>
      <Typography>{task.title}</Typography>
      {/* task.title의 타입이 string임을 보장 */}
    </Card>
  );
};

// 사용 시 타입 체크
<TaskCard 
  task={task} 
  onEdit={handleEdit} 
  onDelete={handleDelete}
  // isDragging 생략 가능 (default: false)
/>
```

**4. Union Type으로 상태 제한**
```typescript
type ProjectStatus = 'PLANNING' | 'IN_PROGRESS' | 'COMPLETED' | 'ARCHIVED';

interface Project {
  projectId: number;
  name: string;
  status: ProjectStatus;  // ✅ 4가지 값만 허용
}

// ❌ 컴파일 에러
project.status = 'ACTIVE';  // Error: Type '"ACTIVE"' is not assignable to type 'ProjectStatus'

// ✅ 정상
project.status = 'IN_PROGRESS';
```

### TypeScript의 장점

**1. 컴파일 타임 에러 감지**
```typescript
// ❌ JavaScript: 런타임에 발견
data.usreName  // 오타! 하지만 실행 전까지 모름

// ✅ TypeScript: 작성 중 발견
data.usreName  // Error: Property 'usreName' does not exist
```

**2. IDE 자동완성**
```typescript
const task: Task = { ... };
task.  // ← 여기서 IDE가 taskId, title, content 등 제안
```

**3. 리팩토링 안전성**
```typescript
// Task 인터페이스의 deadline을 string → Date로 변경
interface Task {
  deadline: Date | null;  // ← 변경
}

// ✅ 사용하는 모든 곳에서 컴파일 에러 발생
// → 누락 없이 수정 가능
```

**4. 문서화 효과**
```typescript
// 타입 정의 자체가 문서
interface TaskCreateData {
  title: string;        // 필수
  content?: string;     // 선택
  deadline?: string;    // 선택
  workerEmail?: string; // 선택
}

// 주석 없이도 API 스펙 명확
```

### 실무에서 체감한 효과

✅ **Before (JavaScript)**
- API 응답 타입 불명확 → 디버깅 어려움
- Props 잘못 전달 → 런타임 에러
- 리팩토링 시 누락 많음

✅ **After (TypeScript)**
- 작성 중 에러 발견 → 빠른 수정
- IDE 자동완성 → 생산성 향상
- 리팩토링 안전 → 유지보수 쉬움

### 주의사항
- **학습 곡선**: Generic, Union Type 등 개념 학습 필요
- **타입 정의 시간**: 초기 타입 정의에 시간 투자 필요 (하지만 나중에 시간 절약)
- **외부 라이브러리**: @types 패키지 필요 (대부분 제공됨)

## 코드 예시
```typescript
// types/kanban.ts - 타입 정의
export interface Task {
  taskId: number;
  title: string;
  content: string | null;
  deadline: string | null;
  worker: {
    userId: number;
    name: string;
    email: string;
  } | null;
  sequence: number;
}

export interface TaskCreateData {
  title: string;
  content?: string;
  deadline?: string;
  workerEmail?: string;
}

// api/task.ts - API 함수
import { Task, TaskCreateData } from '../types/kanban';

export const taskApi = {
  createTask: async (columnId: number, data: TaskCreateData): Promise<Task> => {
    const response = await client.post<Task>(`/api/tasks`, {
      columnId,
      ...data,
    });
    return response.data;  // ✅ Task 타입 보장
  },

  updateTask: async (taskId: number, data: Partial<Task>): Promise<Task> => {
    const response = await client.patch<Task>(`/api/tasks/${taskId}`, data);
    return response.data;
  },
};

// components/TaskCard.tsx - 컴포넌트
interface TaskCardProps {
  task: Task;
  onEdit: (taskId: number) => void;
  onDelete: (taskId: number) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onEdit, onDelete }) => {
  return (
    <Card onClick={() => onEdit(task.taskId)}>
      <Typography variant="h6">{task.title}</Typography>
      {task.worker && (
        <Chip label={task.worker.name} size="small" />
      )}
      <IconButton onClick={(e) => {
        e.stopPropagation();
        onDelete(task.taskId);
      }}>
        <DeleteIcon />
      </IconButton>
    </Card>
  );
};
```

## 꼬리 질문 예상
- `any` 타입을 사용하면 안 되는 이유는?
  → 타입 체크를 무력화시켜 TypeScript의 장점을 잃음
- `interface`와 `type`의 차이는?
  → interface는 확장 가능(extends), type은 Union/Intersection 가능
- Generic은 왜 사용하나?
  → 재사용 가능한 타입 정의 (예: `Array<T>`, `Promise<T>`)

## 참고
- [[bizsync-Vite-빌드도구-면접]]
- TypeScript 공식 문서
