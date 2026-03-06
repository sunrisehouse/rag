from .. import config
from .base import BaseVectorStore
from .elasticsearch_store import ElasticsearchStore
from .sqlite_store import SQLiteStore
from ..logger import log

def VectorStore() -> BaseVectorStore:
    """
    설정 파일(config.py)의 VECTOR_STORE 값에 따라
    적절한 벡터 저장소 인턴스를 생성하여 반환합니다.
    """
    store_type = config.VECTOR_STORE.lower()
    log.info(f"Selected vector store type: {store_type}")

    if store_type == 'elasticsearch':
        return ElasticsearchStore()
    elif store_type == 'sqlite':
        return SQLiteStore()
    else:
        raise ValueError(f"Unsupported vector store type: '{store_type}'. Please use 'elasticsearch' or 'sqlite'.")
