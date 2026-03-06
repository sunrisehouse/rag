import sqlite3
import json
from typing import List, Dict, Any
from .base import BaseVectorStore
from ..database import get_db_connection # Re-use the connection from the main database module
from ..logger import log

class SQLiteStore(BaseVectorStore):
    """SQLite를 벡터 스토어로 사용하기 위한 클래스"""

    def __init__(self):
        self.conn = get_db_connection()
        log.info("Successfully connected to SQLite for Vector Store.")

    def create_index_if_not_exists(self, embedding_dim: int):
        """
        벡터 저장을 위한 'vectors' 테이블을 생성합니다.
        embedding_dim 파라미터는 여기서는 사용되지 않지만 인터페이스 호환성을 위해 유지합니다.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            embedding TEXT NOT NULL,
            source_url TEXT,
            crawled_at TIMESTAMP
        )
        """)
        self.conn.commit()
        log.info("Table 'vectors' is ready in SQLite database.")

    def index_document(self, text: str, vector: List[float], metadata: Dict[str, Any]) -> str:
        """
        단일 문서를 SQLite 테이블에 저장합니다.
        :return: 생성된 row의 ID (문자열로 변환)
        """
        cursor = self.conn.cursor()
        
        # 벡터를 JSON 문자열로 직렬화
        embedding_json = json.dumps(vector)
        
        source_url = metadata.get('source_url')
        crawled_at = metadata.get('crawled_at')

        try:
            cursor.execute("""
            INSERT INTO vectors (text, embedding, source_url, crawled_at)
            VALUES (?, ?, ?, ?)
            """, (text, embedding_json, source_url, crawled_at))
            self.conn.commit()
            doc_id = cursor.lastrowid
            log.debug(f"Successfully indexed document with ID: {doc_id} into SQLite.")
            return str(doc_id)
        except Exception as e:
            log.error(f"Failed to index document into SQLite. Metadata: {metadata}. Error: {e}")
            self.conn.rollback()
            raise
