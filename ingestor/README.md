# RAG Ingestor

이 프로젝트는 `crawler` 프로젝트를 통해 수집된 데이터를 파싱하고 임베딩하여 벡터 데이터베이스(Elasticsearch)에 저장하는 역할을 합니다.

## 주요 기능

- **데이터 소스:** `crawler`가 수집한 SQLite DB의 HTML 데이터. (향후 PDF 파일 확장 예정)
- **파싱:** 문서 타입(HTML, PDF)에 따라 확장 가능한 파서 구조.
- **임베딩:** `sentence-transformers`를 사용하여 텍스트를 벡터로 변환. 설정 파일을 통해 쉽게 다른 모델로 교체 가능.
- **벡터 저장소:** Elasticsearch를 사용하여 임베딩된 벡터와 원문 텍스트 저장.
- **상태 관리:** SQLite DB를 사용하여 각 문서의 처리 상태(성공, 실패) 및 작업 로그 기록.
- **설정 관리:** `.env` 파일을 통해 데이터베이스 경로, Elasticsearch 주소, 임베딩 모델 등 주요 설정을 관리.

## 프로젝트 구조

```
ingestor/
├── .env.example        # 환경설정 예시 파일
├── requirements.txt      # 프로젝트 의존성 라이브러리
├── README.md             # 프로젝트 설명 파일
├── config.py             # 설정 로드
├── logger.py             # 로깅 설정
├── database.py           # DB 스키마 및 상태 관리 함수
├── main.py               # Ingestion 프로세스 실행 메인 파일
├── vector_store.py       # Elasticsearch 연동 클래스
├── parsers/              # 문서 파싱 모듈
│   ├── __init__.py
│   ├── base.py
│   ├── html_parser.py
│   └── pdf_parser.py
└── embedders/            # 임베딩 모델 관리 모듈
    ├── __init__.py
    ├── base.py
    └── sentence_transformer.py
```

## 사용법

1.  **가상환경 생성 및 활성화**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **의존성 설치**
    ```bash
    pip install -r requirements.txt
    ```

3.  **환경 변수 설정**
    `.env.example` 파일을 복사하여 `.env` 파일을 생성하고, 자신의 환경에 맞게 값을 수정합니다.
    ```bash
    cp .env.example .env
    ```
    - `CRAWLER_DB_PATH`: `crawler` 프로젝트의 `crawler.db` 파일 경로를 정확하게 지정해야 합니다.
    - `ES_HOST`, `ES_PORT`: Elasticsearch 서버 주소를 지정합니다.
    - `EMBEDDING_MODEL`: 사용할 `sentence-transformer` 모델 이름을 지정합니다. (폐쇄망 환경이므로, 미리 다운로드된 모델의 경로를 지정해야 할 수도 있습니다.)

4.  **데이터베이스 테이블 초기화**
    `ingestor`를 처음 실행하면 필요한 테이블이 자동으로 생성되지만, 수동으로 생성하고 싶다면 다음을 실행합니다.
    ```bash
    python -c "from database import init_db; init_db()"
    ```
    
5.  **Ingestion 프로세스 실행**
    ```bash
    python -m main
    ```
    또는
    ```bash
    python main.py
    ```
