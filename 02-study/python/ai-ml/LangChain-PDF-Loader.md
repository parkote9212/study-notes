# LangChain PDF Loader

## **주요 기능**

- 파일명 기반 **정확한 문서 분류** (4단계: act, decree, enforcement_rule, safety_standards)
- `pdfplumber`로 텍스트 추출 후 **`제N조` 기준 조항 청킹**
- LangChain `Document` 객체로 반환 (메타데이터 포함)

## **코드 위치**

- 로더: `app/core/lc_pdf_loader.py`
- 분류기: `app/core/document_classifier.py`

## **사용 예시 (Python)**

```python
from app.core.lc_pdf_loader import process_law_pdf

docs = process_law_pdf("산업안전보건기준에 관한 규칙.pdf")
print(docs[0].page_content[:200])
print(docs[0].metadata)
```

## **VectorDB 적재 예시 (Chroma)**

```python
from chromadb import PersistentClient
from app.core.lc_pdf_loader import process_law_pdf

client = PersistentClient(path="./safety_db")
collection = client.get_or_create_collection(
    name="safety_rules"
)

# 문서 로드
chunks = process_law_pdf("산업안전보건기준에 관한 규칙.pdf")

# 적재
collection.add(
    documents=[c.page_content for c in chunks],
    metadatas=[c.metadata for c in chunks],
    ids=[f"{c.metadata['source']}_{i}" for i, c in enumerate(chunks)]
)
```

## **질의 시 가중치 적용 (기술적 질문 우선)**

- `RAGService.query(..., use_weighting=True)` 기본 적용
- `WeightedRetriever`가 `doc_type='safety_standards'`를 상위로 재정렬

## **권장**

- 파일명은 **NFC 정규화**된 한글을 사용하세요 (맥/리눅스 자소 분리 방지).
- 기술 기준 질문(비계, 조도, 온습도 등)은 safety_standards 문서가 최우선으로 검색됩니다.
