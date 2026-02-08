---
tags:
  - interview
  - react
  - drag-and-drop
  - hello-pangea-dnd
  - bizsync
  - project
created: 2025-02-05
difficulty: 중상
---

# BizSync - React 드래그 앤 드롭 구현 (@hello-pangea/dnd)

## 질문
> React에서 드래그 앤 드롭을 구현한 경험을 설명해주세요.

## 핵심 답변 (3줄)
1. **문제**: 칸반 보드에서 업무 카드를 직관적으로 이동시키는 UX 필요
2. **해결**: `@hello-pangea/dnd` 라이브러리로 드래그 앤 드롭 구현 (react-beautiful-dnd 후속)
3. **결과**: 컬럼 간 이동, 같은 컬럼 내 순서 변경, 애니메이션 효과로 직관적인 UX 제공

## 상세 설명

### 배경
칸반 보드의 핵심은 업무 카드를 드래그해서 상태를 변경하는 것입니다. HTML5 Drag & Drop API는 복잡하고, 브라우저 호환성 문제가 있어 검증된 라이브러리가 필요했습니다.

### 왜 @hello-pangea/dnd인가?
- **react-beautiful-dnd의 커뮤니티 포크** (Atlassian이 공식 지원 중단)
- **성능**: 가상 DOM 최적화로 리렌더링 최소화
- **접근성**: 키보드 네비게이션 지원 (스크린 리더 친화적)
- **부드러운 애니메이션**: 드래그 시 자연스러운 움직임

### 핵심 개념

**3가지 컴포넌트**
1. `<DragDropContext>`: 최상위 래퍼 (드래그 이벤트 리스너)
2. `<Droppable>`: 드롭 가능한 영역 (칸반 컬럼)
3. `<Draggable>`: 드래그 가능한 아이템 (업무 카드)

### 구현 과정

**1단계: DragDropContext로 전체 감싸기**
```tsx
<DragDropContext onDragEnd={handleDragEnd}>
  {/* 칸반 보드 컨텐츠 */}
</DragDropContext>
```

**2단계: Droppable로 컬럼 정의**
```tsx
<Droppable droppableId={`column-${column.columnId}`}>
  {(provided, snapshot) => (
    <Box
      ref={provided.innerRef}
      {...provided.droppableProps}
      sx={{
        backgroundColor: snapshot.isDraggingOver ? 'grey.100' : 'transparent',
        minHeight: '100px',
      }}
    >
      {/* 업무 카드들 */}
      {provided.placeholder}  {/* 드래그 시 공간 확보 */}
    </Box>
  )}
</Droppable>
```

**3단계: Draggable로 카드 정의**
```tsx
<Draggable draggableId={`task-${task.taskId}`} index={index}>
  {(provided, snapshot) => (
    <Card
      ref={provided.innerRef}
      {...provided.draggableProps}
      {...provided.dragHandleProps}
      sx={{
        opacity: snapshot.isDragging ? 0.8 : 1,
        transform: snapshot.isDragging ? 'rotate(5deg)' : 'none',
      }}
    >
      {/* 업무 카드 내용 */}
    </Card>
  )}
</Draggable>
```

**4단계: onDragEnd 핸들러 구현**
```tsx
const handleDragEnd = async (result: DropResult) => {
  const { source, destination, draggableId } = result;
  
  // 드롭 위치가 없으면 취소
  if (!destination) return;
  
  // 같은 위치면 취소
  if (
    source.droppableId === destination.droppableId &&
    source.index === destination.index
  ) {
    return;
  }
  
  const taskId = parseInt(draggableId.replace('task-', ''));
  const sourceColumnId = parseInt(source.droppableId.replace('column-', ''));
  const destColumnId = parseInt(destination.droppableId.replace('column-', ''));
  
  // 낙관적 업데이트 (UI 먼저 반영)
  const newColumns = updateColumnsOptimistically(
    boardData.columns,
    taskId,
    sourceColumnId,
    destColumnId,
    source.index,
    destination.index
  );
  
  setBoard({ ...boardData, columns: newColumns });
  
  // 서버에 동기화
  try {
    await taskApi.moveTask(taskId, {
      columnId: destColumnId,
      sequence: destination.index + 1,
    });
  } catch (error) {
    // 실패 시 롤백
    refreshBoard();
  }
};
```

### 성능 최적화
- **React.memo**: 변경되지 않은 카드는 리렌더링 안 함
- **useCallback**: handleDragEnd 함수 메모이제이션
- **낙관적 업데이트**: UI 먼저 반영 후 서버 동기화

### 주의사항
- `droppableId`와 `draggableId`는 **문자열**이어야 함
- `index`는 0부터 시작하는 **순서**
- `provided.placeholder`는 드래그 시 빈 공간 확보용 (필수)

## 코드 예시
```tsx
import { DragDropContext, Draggable, Droppable, DropResult } from "@hello-pangea/dnd";

const KanbanBoardPage = () => {
  const handleDragEnd = async (result: DropResult) => {
    if (!result.destination) return;
    
    const taskId = parseInt(result.draggableId.replace('task-', ''));
    const destColumnId = parseInt(result.destination.droppableId.replace('column-', ''));
    
    // 낙관적 업데이트
    updateLocalState();
    
    // 서버 동기화
    await taskApi.moveTask(taskId, {
      columnId: destColumnId,
      sequence: result.destination.index + 1,
    });
  };
  
  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      {columns.map(column => (
        <Droppable key={column.columnId} droppableId={`column-${column.columnId}`}>
          {(provided, snapshot) => (
            <Box
              ref={provided.innerRef}
              {...provided.droppableProps}
              sx={{ backgroundColor: snapshot.isDraggingOver ? 'lightblue' : 'white' }}
            >
              {column.tasks.map((task, index) => (
                <Draggable
                  key={task.taskId}
                  draggableId={`task-${task.taskId}`}
                  index={index}
                >
                  {(provided, snapshot) => (
                    <Card
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      sx={{ opacity: snapshot.isDragging ? 0.5 : 1 }}
                    >
                      <CardContent>{task.title}</CardContent>
                    </Card>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </Box>
          )}
        </Droppable>
      ))}
    </DragDropContext>
  );
};
```

## 꼬리 질문 예상
- 낙관적 업데이트(Optimistic Update)란?
  → UI를 먼저 업데이트하고 서버 응답을 기다리지 않는 방식 (실패 시 롤백)
- react-beautiful-dnd와의 차이는?
  → @hello-pangea/dnd는 커뮤니티 포크로, React 19 지원 및 버그 수정
- 드래그 중 스크롤은 어떻게 처리하나?
  → 라이브러리가 자동으로 처리 (드래그 시 경계에 닿으면 자동 스크롤)

## 참고
- [[bizsync-Zustand-선택이유-면접]]
- @hello-pangea/dnd GitHub
