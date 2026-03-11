# rag

## 폴더구조

rag/
├── src/
│   ├── database/       # Repository (SQLite 등)
│   ├── transformer/    # WikiStructureTransformer
│   ├── vectorstore/    # Elasticsearch 관리
│   ├── llm/            # InternalChatModel (사내 LLM 연동)
│   │
│   ├── pipelines/      # ⚙️ [1] 데이터 전처리 및 저장 (Offline)
│   │   └── indexing_pipeline.py  # 주기적으로 위키를 긁어와서 DB/ES에 넣는 배치 작업
│   │
│   ├── chains/         # 🧠 [2] 핵심 AI 로직 (LangChain LCEL)
│   │   └── qa_chain.py           # 검색+프롬프트+LLM이 결합된 순수 체인 객체 생성
│   │
│   └── services/       # 🚀 [3] API 비즈니스 로직 (Online)
│       └── qa_service.py         # Controller에서 호출. qa_chain을 실행하고 예외 처리 등을 담당

## 실행

```
# mock indexing pipeline
python3 -m tests.test_testindexingpipeline

# mock qa chain
python3 -m tests.test_testqachain
```