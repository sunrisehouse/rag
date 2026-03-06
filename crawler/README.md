# Confluence Wiki Crawler

이 프로젝트는 Python으로 작성된 Confluence 위키 페이지 크롤러입니다. 지정된 페이지에서 시작하여 링크를 따라가며 모든 페이지의 콘텐츠를 수집하고 SQLite 데이터베이스에 저장합니다.

## 주요 기능

- **동적 페이지 크롤링**: `Selenium`을 사용하여 JavaScript 렌더링을 포함한 동적 웹 페이지를 효과적으로 크롤링합니다.
- **트리 구조 탐색**: 페이지 내의 링크를 재귀적으로 따라가며 위키 전체를 탐색합니다.
- **중복 방지**: 이미 방문한 페이지는 다시 방문하지 않아 무한 루프를 방지합니다.
- **데이터 저장**: 크롤링한 데이터(URL, 제목, 본문, 부모 페이지)를 `SQLite` 데이터베이스에 저장하여 쉽게 관리하고 조회할 수 있습니다.
- **설정 분리**: 로그인 정보나 시작 URL 등 민감한 정보는 별도의 설정 파일(`config.py`)에서 관리합니다.

## 프로젝트 구조

```
.
├── crawler/
│   ├── __init__.py
│   ├── main.py           # 크롤러 실행 스크립트
│   ├── crawler.py        # Confluence 크롤링 로직 구현
│   ├── database.py       # SQLite 데이터베이스 연결 및 쿼리
│   └── config.py         # 설정 파일 (URL, 자격 증명 등)
├── requirements.txt      # 프로젝트 의존성 목록
├── .gitignore            # Git 형상관리 제외 파일 목록
└── README.md             # 프로젝트 설명 및 실행 방법 안내
```

## 사용 방법

### 1. 프로젝트 복제

```bash
git clone <repository_url>
cd 01.crawler
```

### 2. 가상 환경 생성 및 활성화

Python `venv`를 사용하여 독립적인 실행 환경을 구성합니다.

- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **Windows**:
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

### 3. 의존성 설치

`requirements.txt` 파일에 명시된 라이브러리들을 설치합니다.

```bash
pip install -r requirements.txt
```

### 4. 설정 파일 수정

`crawler/config.py` 파일을 열어 본인의 Confluence 환경에 맞게 정보를 수정합니다.

```python
# crawler/config.py

# Confluence 사이트의 기본 URL을 입력하세요. (예: "https://wiki.example.com")
BASE_URL = "https://your-confluence-domain.atlassian.net/wiki"

# 크롤링을 시작할 페이지의 전체 URL을 입력하세요.
START_URL = "https://your-confluence-domain.atlassian.net/wiki/spaces/SPACEKEY/pages/12345678/My-Start-Page"

# Confluence 로그인 계정 정보를 입력하세요.
USERNAME = "your_email@example.com"
PASSWORD = "your_password_or_api_token"
```

**주의**: 비밀번호 대신 Atlassian API 토큰을 사용하는 것을 권장합니다.

### 5. 크롤러 실행

모든 설정이 완료되었으면 아래 명령어를 실행하여 크롤링을 시작합니다.

```bash
python -m crawler.main
```

크롤링이 시작되면 Selenium이 제어하는 Chrome 브라우저 창이 나타나고, 자동으로 로그인 및 페이지 이동을 시작합니다. 크롤링된 데이터는 프로젝트 루트 디렉토리에 `confluence_crawler.db` 파일로 저장됩니다.

## 데이터베이스

- 데이터베이스 파일: `confluence_crawler.db`
- 테이블: `pages`
- 스키마:
  - `id`: INTEGER (Primary Key)
  - `url`: TEXT (Unique)
  - `title`: TEXT
  - `content`: TEXT
  - `parent_url`: TEXT
  - `crawled_at`: TIMESTAMP