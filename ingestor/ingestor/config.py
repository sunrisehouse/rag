import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
# 프로젝트 루트에 .env 파일을 생성하고 설정을 추가하세요.
load_dotenv()

# 데이터베이스 설정
DB_PATH = os.getenv("DB_PATH")
if DB_PATH is None:
    raise ValueError("DB_PATH environment variable not set.")

# 벡터 저장소 설정 ("elasticsearch" 또는 "sqlite")
VECTOR_STORE = os.getenv("VECTOR_STORE")
if VECTOR_STORE is None:
    raise ValueError("VECTOR_STORE environment variable not set.")

# Elasticsearch 설정 (VECTOR_STORE가 'elasticsearch'일 때만 확인)
if VECTOR_STORE == "elasticsearch":
    ES_HOST = os.getenv("ES_HOST")
    if ES_HOST is None:
        raise ValueError("ES_HOST environment variable not set for Elasticsearch vector store.")

    ES_PORT_STR = os.getenv("ES_PORT")
    if ES_PORT_STR is None:
        raise ValueError("ES_PORT environment variable not set for Elasticsearch vector store.")
    ES_PORT = int(ES_PORT_STR)

    ES_INDEX_NAME = os.getenv("ES_INDEX_NAME")
    if ES_INDEX_NAME is None:
        raise ValueError("ES_INDEX_NAME environment variable not set for Elasticsearch vector store.")

# Text splitting
CHUNK_SIZE_STR = os.getenv("CHUNK_SIZE")
if CHUNK_SIZE_STR is None:
    raise ValueError("CHUNK_SIZE environment variable not set.")
CHUNK_SIZE = int(CHUNK_SIZE_STR)

CHUNK_OVERLAP_STR = os.getenv("CHUNK_OVERLAP")
if CHUNK_OVERLAP_STR is None:
    raise ValueError("CHUNK_OVERLAP environment variable not set.")
CHUNK_OVERLAP = int(CHUNK_OVERLAP_STR)


# 임베딩 모델 설정
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
if EMBEDDING_MODEL is None:
    raise ValueError("EMBEDDING_MODEL environment variable not set.")

EMBEDDING_MODEL_SAVE_PATH = os.getenv("EMBEDDING_MODEL_SAVE_PATH")
if EMBEDDING_MODEL_SAVE_PATH is None:
    raise ValueError("EMBEDDING_MODEL_SAVE_PATH environment variable not set.")


# 로깅 설정
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")
if LOG_FILE_PATH is None:
    raise ValueError("LOG_FILE_PATH environment variable not set.")

LOG_LEVEL = os.getenv("LOG_LEVEL")
if LOG_LEVEL is None:
    raise ValueError("LOG_LEVEL environment variable not set.")
