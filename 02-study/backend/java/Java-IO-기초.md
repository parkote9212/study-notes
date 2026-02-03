---
tags:
  - study
  - java
  - io
  - file
  - stream
created: 2025-02-03
---

# Java I/O 기초

## 한 줄 요약
> 파일과 데이터를 읽고 쓰는 입출력 처리의 기본 개념과 활용

## 상세 설명

### I/O (Input/Output)의 기본 개념

Java I/O는 데이터를 읽고 쓰는 작업을 처리하는 API입니다.

**I/O 종류**
1. **Byte Stream** - 바이트 단위 (이진 데이터)
2. **Character Stream** - 문자 단위 (텍스트)
3. **Buffer Stream** - 버퍼링으로 성능 향상
4. **NIO (New I/O)** - Java 7+ 현대적 I/O

## 코드 예시

### 1. Byte Stream (InputStream/OutputStream)

#### 파일 복사

```java
// 바이트 스트림으로 파일 복사
public void copyFile(String source, String dest) throws IOException {
    try (FileInputStream fis = new FileInputStream(source);
         FileOutputStream fos = new FileOutputStream(dest)) {
        
        byte[] buffer = new byte[1024];
        int length;
        
        while ((length = fis.read(buffer)) > 0) {
            fos.write(buffer, 0, length);
        }
    }
}
```

#### 버퍼를 사용한 성능 향상

```java
// ✅ 버퍼 사용 - 훨씬 빠름
public void copyFileBuffered(String source, String dest) throws IOException {
    try (BufferedInputStream bis = new BufferedInputStream(
             new FileInputStream(source));
         BufferedOutputStream bos = new BufferedOutputStream(
             new FileOutputStream(dest))) {
        
        byte[] buffer = new byte[8192];  // 8KB 버퍼
        int length;
        
        while ((length = bis.read(buffer)) > 0) {
            bos.write(buffer, 0, length);
        }
    }
}
```

### 2. Character Stream (Reader/Writer)

#### 텍스트 파일 읽기

```java
// 텍스트 파일 한 줄씩 읽기
public List<String> readLines(String filePath) throws IOException {
    List<String> lines = new ArrayList<>();
    
    try (BufferedReader br = new BufferedReader(
            new FileReader(filePath))) {
        
        String line;
        while ((line = br.readLine()) != null) {
            lines.add(line);
        }
    }
    
    return lines;
}
```

#### 텍스트 파일 쓰기

```java
// 텍스트 파일에 쓰기
public void writeLines(String filePath, List<String> lines) 
        throws IOException {
    
    try (BufferedWriter bw = new BufferedWriter(
            new FileWriter(filePath))) {
        
        for (String line : lines) {
            bw.write(line);
            bw.newLine();  // 줄바꿈
        }
    }
}

// 파일에 추가 (append 모드)
public void appendLine(String filePath, String line) throws IOException {
    try (BufferedWriter bw = new BufferedWriter(
            new FileWriter(filePath, true))) {  // true = append
        
        bw.write(line);
        bw.newLine();
    }
}
```

### 3. Files 클래스 (Java 7+) - 가장 간단

#### 파일 읽기/쓰기

```java
// ✅ 한 번에 전체 파일 읽기
String content = Files.readString(Path.of("file.txt"));

// ✅ 한 줄씩 리스트로 읽기
List<String> lines = Files.readAllLines(Path.of("file.txt"));

// ✅ 파일 쓰기
Files.writeString(Path.of("output.txt"), "Hello World");

// ✅ 여러 줄 쓰기
List<String> lines = Arrays.asList("Line 1", "Line 2", "Line 3");
Files.write(Path.of("output.txt"), lines);
```

#### 파일 복사/이동/삭제

```java
// 파일 복사
Files.copy(
    Path.of("source.txt"), 
    Path.of("dest.txt"),
    StandardCopyOption.REPLACE_EXISTING
);

// 파일 이동
Files.move(
    Path.of("old.txt"), 
    Path.of("new.txt"),
    StandardCopyOption.REPLACE_EXISTING
);

// 파일 삭제
Files.delete(Path.of("file.txt"));

// 파일 존재 여부 확인 후 삭제
Files.deleteIfExists(Path.of("file.txt"));
```

#### 디렉토리 작업

```java
// 디렉토리 생성
Files.createDirectory(Path.of("newdir"));

// 중첩 디렉토리 생성
Files.createDirectories(Path.of("parent/child/grandchild"));

// 디렉토리 내 파일 목록
try (Stream<Path> files = Files.list(Path.of("."))) {
    files.forEach(System.out::println);
}

// 재귀적으로 모든 파일 탐색
try (Stream<Path> files = Files.walk(Path.of("."))) {
    files.filter(Files::isRegularFile)
         .forEach(System.out::println);
}
```

### 4. 파일 정보 확인

```java
Path path = Path.of("file.txt");

// 파일 존재 확인
boolean exists = Files.exists(path);

// 파일인지 디렉토리인지
boolean isFile = Files.isRegularFile(path);
boolean isDir = Files.isDirectory(path);

// 파일 크기
long size = Files.size(path);

// 읽기/쓰기 가능 여부
boolean readable = Files.isReadable(path);
boolean writable = Files.isWritable(path);

// 수정 시간
FileTime lastModified = Files.getLastModifiedTime(path);
```

### 5. 실전 예시: CSV 파일 읽기/쓰기

```java
// CSV 파일 읽기
public List<User> readUsersFromCsv(String filePath) throws IOException {
    List<User> users = new ArrayList<>();
    
    try (BufferedReader br = Files.newBufferedReader(Path.of(filePath))) {
        String line = br.readLine();  // 헤더 스킵
        
        while ((line = br.readLine()) != null) {
            String[] parts = line.split(",");
            users.add(new User(
                parts[0],                    // name
                Integer.parseInt(parts[1]),  // age
                parts[2]                     // email
            ));
        }
    }
    
    return users;
}

// CSV 파일 쓰기
public void writeUsersToCsv(String filePath, List<User> users) 
        throws IOException {
    
    try (BufferedWriter bw = Files.newBufferedWriter(Path.of(filePath))) {
        // 헤더 쓰기
        bw.write("Name,Age,Email");
        bw.newLine();
        
        // 데이터 쓰기
        for (User user : users) {
            bw.write(String.format("%s,%d,%s", 
                user.getName(), 
                user.getAge(), 
                user.getEmail()
            ));
            bw.newLine();
        }
    }
}
```

### 6. 실전 예시: 로그 파일 처리

```java
public class LogFileProcessor {
    
    // 로그 파일 분석
    public Map<String, Long> analyzeLogFile(String logPath) 
            throws IOException {
        
        Map<String, Long> errorCounts = new HashMap<>();
        
        try (Stream<String> lines = Files.lines(Path.of(logPath))) {
            lines.filter(line -> line.contains("ERROR"))
                 .forEach(line -> {
                     String errorType = extractErrorType(line);
                     errorCounts.merge(errorType, 1L, Long::sum);
                 });
        }
        
        return errorCounts;
    }
    
    // 큰 로그 파일을 날짜별로 분할
    public void splitLogByDate(String logPath, String outputDir) 
            throws IOException {
        
        Map<String, BufferedWriter> writers = new HashMap<>();
        
        try (BufferedReader br = Files.newBufferedReader(Path.of(logPath))) {
            String line;
            
            while ((line = br.readLine()) != null) {
                String date = extractDate(line);  // "2025-02-03"
                
                BufferedWriter writer = writers.computeIfAbsent(date, d -> {
                    try {
                        Path outPath = Path.of(outputDir, "log-" + d + ".txt");
                        return Files.newBufferedWriter(outPath);
                    } catch (IOException e) {
                        throw new UncheckedIOException(e);
                    }
                });
                
                writer.write(line);
                writer.newLine();
            }
        } finally {
            // 모든 writer 닫기
            for (BufferedWriter writer : writers.values()) {
                writer.close();
            }
        }
    }
    
    private String extractDate(String line) {
        // 로그에서 날짜 추출
        return line.substring(0, 10);
    }
    
    private String extractErrorType(String line) {
        // 에러 타입 추출
        return "ERROR";
    }
}
```

### 7. 임시 파일 생성

```java
// 임시 파일 생성
Path tempFile = Files.createTempFile("myapp-", ".tmp");
System.out.println("임시 파일: " + tempFile);

// 임시 디렉토리 생성
Path tempDir = Files.createTempDirectory("myapp-");
System.out.println("임시 디렉토리: " + tempDir);

// 사용 후 삭제
Files.delete(tempFile);
```

### 8. 파일 필터링 및 검색

```java
// 특정 확장자 파일만 찾기
try (Stream<Path> files = Files.walk(Path.of("."))) {
    List<Path> javaFiles = files
        .filter(p -> p.toString().endsWith(".java"))
        .collect(Collectors.toList());
    
    javaFiles.forEach(System.out::println);
}

// 크기가 큰 파일 찾기
try (Stream<Path> files = Files.walk(Path.of("."))) {
    files.filter(Files::isRegularFile)
         .filter(p -> {
             try {
                 return Files.size(p) > 1_000_000;  // 1MB 이상
             } catch (IOException e) {
                 return false;
             }
         })
         .forEach(System.out::println);
}
```

## 주의사항 / 함정

### 1. 리소스 누수

```java
// ❌ 스트림을 닫지 않음 - 메모리 누수
FileInputStream fis = new FileInputStream("file.txt");
// ... 사용
// fis.close() 호출 안 함!

// ✅ try-with-resources 사용
try (FileInputStream fis = new FileInputStream("file.txt")) {
    // 자동으로 닫힘
}
```

### 2. 인코딩 문제

```java
// ❌ 기본 인코딩 사용 (플랫폼 의존)
FileReader reader = new FileReader("file.txt");

// ✅ 명시적으로 UTF-8 지정
BufferedReader reader = Files.newBufferedReader(
    Path.of("file.txt"), 
    StandardCharsets.UTF_8
);
```

### 3. 대용량 파일 처리

```java
// ❌ 전체 파일을 메모리에 로드
String content = Files.readString(Path.of("huge-file.txt"));  // OOM!

// ✅ 스트림으로 처리
try (Stream<String> lines = Files.lines(Path.of("huge-file.txt"))) {
    lines.forEach(this::processLine);
}
```

### 4. 파일 존재 확인

```java
// ❌ 파일 존재 확인 후 삭제 (TOCTOU 문제)
if (Files.exists(path)) {
    Files.delete(path);  // 사이에 다른 프로세스가 삭제할 수 있음
}

// ✅ deleteIfExists 사용
Files.deleteIfExists(path);
```

### 5. 경로 구분자

```java
// ❌ 하드코딩된 경로 구분자
String path = "dir" + "/" + "file.txt";  // Windows에서 문제

// ✅ Path 사용
Path path = Path.of("dir", "file.txt");  // OS 독립적
```

## 관련 개념
- [[Java-예외처리-Exception]]
- [[Java-NIO]]
- [[Java-Serialization]]

## 면접 질문
1. Byte Stream과 Character Stream의 차이는?
2. try-with-resources를 사용해야 하는 이유는?

## 참고 자료
- Java I/O Tutorial
- Files API Documentation
- NIO.2 Guide