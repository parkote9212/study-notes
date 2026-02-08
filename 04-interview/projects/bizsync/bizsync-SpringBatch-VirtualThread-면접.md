---
tags:
  - interview
  - spring-batch
  - virtual-thread
  - java21
  - bizsync
  - project
created: 2025-02-05
difficulty: 상
---

# BizSync - Spring Batch와 Virtual Thread를 활용한 프로젝트 아카이빙

## 질문
> Spring Batch에서 Virtual Thread를 활용한 경험을 설명해주세요.

## 핵심 답변 (3줄)
1. **문제**: 종료된 프로젝트를 30일 후 아카이빙하는 배치 작업에서 대량 처리 성능 개선 필요
2. **해결**: Java 21 Virtual Thread 기반 TaskExecutor로 병렬 처리 구현 (동시성 10)
3. **결과**: 플랫폼 스레드 대비 메모리 효율적이며 Chunk 단위로 안전한 병렬 처리 가능

## 상세 설명

### 배경
BizSync에서는 완료된 프로젝트를 30일 후 자동으로 ARCHIVED 상태로 변경하는 배치 작업이 필요했습니다. 프로젝트가 많아질수록 처리 시간이 길어지는 문제가 있었습니다.

### 기술적 선택
**왜 Virtual Thread인가?**
- 플랫폼 스레드는 OS 스레드와 1:1 매핑 → 메모리 오버헤드 큼
- Virtual Thread는 JVM이 관리 → 수천 개 동시 실행 가능
- Spring Batch Chunk 처리와 결합 시 효율적

**구현 방식**
```java
// Virtual Thread 기반 TaskExecutor 생성
@Bean
public TaskExecutor virtualThreadTaskExecutor() {
    return new TaskExecutorAdapter(
        Executors.newVirtualThreadPerTaskExecutor()
    );
}

// Step에 적용
@Bean
public Step projectArchiveStep() {
    return new StepBuilder("projectArchiveStep", jobRepository)
        .<Project, Project>chunk(CHUNK_SIZE, transactionManager)
        .reader(projectArchiveReader())
        .processor(projectArchiveProcessor())
        .writer(projectArchiveWriter())
        .taskExecutor(virtualThreadTaskExecutor())  // Virtual Thread 적용
        .throttleLimit(10)  // 동시 처리 수 제한
        .build();
}
```

### 동작 원리
1. **Reader**: 30일 이전 완료 프로젝트를 Chunk 단위(100개)로 조회
2. **Processor**: 각 프로젝트를 Virtual Thread에서 병렬 검증
3. **Writer**: 상태를 ARCHIVED로 변경하고 저장

### 성능 개선
- Chunk 단위로 병렬 처리되어 처리 속도 향상
- Virtual Thread는 블로킹 작업에서도 효율적 (DB I/O 대기 시 다른 작업 실행)
- 메모리 사용량 최소화 (플랫폼 스레드 대비 ~100배 적음)

### 주의사항
- `throttleLimit`으로 동시성 제어 (DB 커넥션 풀 고려)
- ThreadLocal 사용 주의 (Virtual Thread는 재사용 안 됨)
- 트랜잭션 범위는 각 Chunk마다 독립적으로 유지

## 코드 예시
```java
/**
 * 프로젝트 아카이빙 Job 설정
 * 매일 오전 2시 실행 (@Scheduled)
 */
@Configuration
@RequiredArgsConstructor
public class ProjectArchiveJobConfig {
    
    private static final int CHUNK_SIZE = 100;
    private static final int VIRTUAL_THREAD_CONCURRENCY = 10;
    
    @Bean
    public Job projectArchiveJob() {
        return new JobBuilder("projectArchiveJob", jobRepository)
            .start(projectArchiveStep())
            .build();
    }
    
    @Bean
    public Step projectArchiveStep() {
        return new StepBuilder("projectArchiveStep", jobRepository)
            .<Project, Project>chunk(CHUNK_SIZE, transactionManager)
            .reader(projectArchiveReader())
            .processor(projectArchiveProcessor())
            .writer(projectArchiveWriter())
            .taskExecutor(virtualThreadTaskExecutor())
            .throttleLimit(VIRTUAL_THREAD_CONCURRENCY)
            .build();
    }
    
    @Bean
    public RepositoryItemReader<Project> projectArchiveReader() {
        LocalDate cutoffDate = LocalDate.now().minusDays(30);
        
        return new RepositoryItemReaderBuilder<Project>()
            .name("projectArchiveReader")
            .repository(projectRepository)
            .methodName("findByStatusAndEndDateBefore")
            .arguments(ProjectStatus.COMPLETED, cutoffDate)
            .sorts(Map.of("projectId", Sort.Direction.ASC))
            .pageSize(CHUNK_SIZE)
            .build();
    }
    
    @Bean
    public ItemWriter<Project> projectArchiveWriter() {
        return chunk -> {
            for (Project project : chunk) {
                project.archive();  // ARCHIVED로 상태 변경
                projectRepository.save(project);
            }
        };
    }
}
```

## 꼬리 질문 예상
- Virtual Thread와 Platform Thread의 차이는?
  → Virtual Thread는 JVM이 스케줄링하는 경량 스레드, Platform Thread는 OS 스레드와 1:1 매핑
- Spring Batch에서 병렬 처리 방식은 또 무엇이 있나?
  → Multi-threaded Step, Partitioning, Remote Chunking
- throttleLimit을 어떻게 결정했나?
  → DB 커넥션 풀 크기와 시스템 리소스를 고려하여 10으로 설정

## 참고
- [[bizsync-SpringBatch-Scheduler-면접]]
- Java 21 Virtual Thread 공식 문서
