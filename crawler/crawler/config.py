import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# Confluence 설정
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
if CONFLUENCE_URL is None:
    raise ValueError("CONFLUENCE_URL environment variable not set.")

USERNAME = os.getenv("CONFLUENCE_USERNAME") 
if USERNAME is None:
    raise ValueError("CONFLUENCE_USERNAME environment variable not set.")

PASSWORD = os.getenv("CONFLUENCE_PASSWORD") 
if PASSWORD is None:
    raise ValueError("CONFLUENCE_PASSWORD environment variable not set.")

START_URL = os.getenv("START_URL")
if START_URL is None:
    raise ValueError("START_URL environment variable not set.")

# 크롤링 설정
MAX_DEPTH_STR = os.getenv("MAX_DEPTH")
if MAX_DEPTH_STR is None:
    raise ValueError("MAX_DEPTH environment variable not set.")
MAX_DEPTH = int(MAX_DEPTH_STR)

CRAWL_DELAY_STR = os.getenv("CRAWL_DELAY")
if CRAWL_DELAY_STR is None:
    raise ValueError("CRAWL_DELAY environment variable not set.")
CRAWL_DELAY = int(CRAWL_DELAY_STR)

ALLOWED_URL_REGEX = os.getenv("ALLOWED_URL_REGEX")
if ALLOWED_URL_REGEX is None:
    raise ValueError("ALLOWED_URL_REGEX environment variable not set.")

# 브라우저 설정
BROWSER = os.getenv("BROWSER")
if BROWSER is None:
    raise ValueError("BROWSER environment variable not set.")

# 로그인 필요 여부 설정
LOGIN_REQUIRED = os.getenv("LOGIN_REQUIRED", "false").lower() in ["true", "1"]

# 데이터베이스 설정
DB_PATH = os.getenv("DB_PATH")
if DB_PATH is None:
    raise ValueError("DB_PATH environment variable not set.")

# 로깅 설정
LOG_LEVEL = os.getenv("LOG_LEVEL")
if LOG_LEVEL is None:
    raise ValueError("LOG_LEVEL environment variable not set.")

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")
if LOG_FILE_PATH is None:
    raise ValueError("LOG_FILE_PATH environment variable not set.")
