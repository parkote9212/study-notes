---
tags:
  - interview
  - apache-poi
  - excel
  - file-upload
  - bizsync
  - project
created: 2025-02-05
difficulty: 중
---

# BizSync - Apache POI로 엑셀 대량 업무 등록/다운로드

## 질문
> Apache POI를 사용한 엑셀 파일 처리 경험을 설명해주세요.

## 핵심 답변 (3줄)
1. **문제**: 프로젝트 시작 시 수십~수백 개의 업무를 한 번에 등록하는 불편함
2. **해결**: Apache POI로 엑셀 업로드/다운로드 기능 구현 (XSSFWorkbook 사용)
3. **결과**: 업무 대량 등록 시간 단축, 기존 업무 데이터를 엑셀로 백업 가능

## 상세 설명

### 배경
칸반 보드에서 업무를 하나씩 등록하는 것은 비효율적입니다. 특히 프로젝트 초기에 수백 개의 업무를 등록해야 할 때 더욱 그렇습니다. 엑셀로 일괄 등록/다운로드 기능이 필요했습니다.

### Apache POI란?
- **Apache POI**: 자바에서 MS Office 파일을 다루는 라이브러리
- **HSSF**: `.xls` (Excel 97-2003)
- **XSSF**: `.xlsx` (Excel 2007+) ← BizSync에서 사용
- **주요 클래스**: `Workbook`, `Sheet`, `Row`, `Cell`

### 구현 기능

**1. 엑셀 업로드 (업무 대량 등록)**
- 엑셀 파일 읽기 → Row 순회 → 칼럼/담당자 조회 → Task 엔티티 생성 → 일괄 저장
- 에러 처리: 담당자 없어도 업무 생성 (null 허용), 잘못된 행은 스킵

```java
public int uploadTasksFromExcel(Long projectId, MultipartFile file) throws IOException {
    Workbook workbook = new XSSFWorkbook(file.getInputStream());
    Sheet sheet = workbook.getSheetAt(0);  // 첫 번째 시트
    
    List<Task> tasksToSave = new ArrayList<>();
    int rowIndex = 0;
    
    for (Row row : sheet) {
        if (rowIndex++ == 0) continue;  // 헤더 스킵
        
        try {
            String columnName = getCellValueAsString(row.getCell(0));
            String title = getCellValueAsString(row.getCell(1));
            String workerEmail = getCellValueAsString(row.getCell(2));
            String deadlineStr = getCellValueAsString(row.getCell(3));
            String content = getCellValueAsString(row.getCell(4));
            
            // 칸반 컬럼 조회
            KanbanColumn column = kanbanColumnRepository
                .findByProjectIdAndNameOrThrow(projectId, columnName);
            
            // 담당자 조회 (없으면 null)
            User worker = null;
            if (workerEmail != null && !workerEmail.isBlank()) {
                worker = userRepository.findByEmail(workerEmail).orElse(null);
            }
            
            // Task 생성
            Task task = Task.builder()
                .column(column)
                .worker(worker)
                .title(title)
                .content(content)
                .deadline(parseDeadline(deadlineStr))
                .sequence(maxSeq + 1)
                .build();
            
            tasksToSave.add(task);
        } catch (Exception e) {
            log.error("엑셀 {}번 행 파싱 실패: {}", rowIndex, e.getMessage());
            // 계속 진행
        }
    }
    
    taskRepository.saveAll(tasksToSave);  // 일괄 저장
    return tasksToSave.size();
}
```

**2. 엑셀 다운로드 (백업/보고서)**
- 칸반 보드의 모든 업무를 엑셀로 내보내기
- 헤더 스타일링 (굵게), 컬럼 너비 자동 조정
- ByteArrayOutputStream으로 메모리에서 생성 후 반환

```java
public byte[] downloadTasksAsExcel(Long projectId) throws IOException {
    List<Task> tasks = taskMapper.selectTasksByProjectIdOrderBy...(projectId);
    
    Workbook workbook = new XSSFWorkbook();
    Sheet sheet = workbook.createSheet("Tasks");
    
    // 헤더 생성
    Row headerRow = sheet.createRow(0);
    String[] headers = {"컬럼명", "업무제목", "담당자", "마감일", "상세내용"};
    
    CellStyle headerStyle = workbook.createCellStyle();
    Font headerFont = workbook.createFont();
    headerFont.setBold(true);
    headerStyle.setFont(headerFont);
    
    for (int i = 0; i < headers.length; i++) {
        Cell cell = headerRow.createCell(i);
        cell.setCellValue(headers[i]);
        cell.setCellStyle(headerStyle);
    }
    
    // 데이터 행 생성
    int rowIndex = 1;
    for (Task task : tasks) {
        Row row = sheet.createRow(rowIndex++);
        row.createCell(0).setCellValue(task.getColumn().getName());
        row.createCell(1).setCellValue(task.getTitle());
        row.createCell(2).setCellValue(task.getWorker()?.getEmail() ?? "미배정");
        row.createCell(3).setCellValue(task.getDeadline()?.format(...) ?? "");
        row.createCell(4).setCellValue(task.getContent() ?? "");
    }
    
    // 컬럼 너비 자동 조정
    for (int i = 0; i < headers.length; i++) {
        sheet.autoSizeColumn(i);
    }
    
    ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
    workbook.write(outputStream);
    workbook.close();
    
    return outputStream.toByteArray();
}
```

### 주의사항
- **메모리**: 대용량 엑셀은 메모리 부족 발생 가능 → SXSSFWorkbook (스트리밍) 사용
- **Cell 타입**: `getCellType()`으로 STRING, NUMERIC, BOOLEAN 등 구분
- **날짜 파싱**: DateTimeFormatter로 안전하게 파싱 (예외 처리)
- **트랜잭션**: 일괄 저장 시 트랜잭션 단위 고려

## 코드 예시
```java
@Service
@RequiredArgsConstructor
@Transactional
public class ExcelService {
    
    // 헬퍼 메서드: Cell 값을 String으로 변환
    private String getCellValueAsString(Cell cell) {
        if (cell == null) return null;
        
        return switch (cell.getCellType()) {
            case STRING -> cell.getStringCellValue().trim();
            case NUMERIC -> String.valueOf((long) cell.getNumericCellValue());
            case BOOLEAN -> String.valueOf(cell.getBooleanCellValue());
            case FORMULA -> cell.getCellFormula();
            default -> null;
        };
    }
    
    // 헬퍼 메서드: 날짜 파싱
    private LocalDate parseDeadline(String deadlineStr) {
        if (deadlineStr == null || deadlineStr.isBlank()) {
            return null;
        }
        
        try {
            return LocalDate.parse(deadlineStr, 
                DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        } catch (DateTimeParseException e) {
            log.warn("마감일 파싱 실패: {}", deadlineStr);
            return null;
        }
    }
}
```

## 꼬리 질문 예상
- 대용량 엑셀 파일은 어떻게 처리하나?
  → SXSSFWorkbook 사용 (메모리 효율적인 스트리밍 방식)
- CSV와 엑셀의 차이는?
  → CSV는 단순 텍스트, 엑셀은 스타일/수식/차트 지원
- 엑셀 파일 업로드 시 보안 고려사항은?
  → 파일 크기 제한, MIME 타입 검증, 매크로 차단

## 참고
- [[bizsync-SpringBatch-VirtualThread-면접]]
- Apache POI 공식 문서
