import sqlite3
import json
import os
from typing import List, Dict, Any
import csv
from src.logger import get_logger

logger = get_logger(__name__)

class Repository:
    def __init__(self, db_path: str = "data/main.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """데이터베이스 및 테이블 초기화 (Run 기반 구조)"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. 실행(Run) 마스터 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transformation_run (
                    run_id TEXT PRIMARY KEY,
                    transformer_name TEXT,
                    total_chunks INTEGER,
                    source_count INTEGER,
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    finished_at TIMESTAMP
                )
            """)

            # 2. 위키 청크 상세 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wiki_chunk (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT,
                    source TEXT,
                    hierarchy TEXT,
                    content TEXT,
                    char_count INTEGER,
                    metadata_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (run_id) REFERENCES transformation_run (run_id)
                )
            """)
            conn.commit()
        logger.info(f"Repository 초기화 완료 (Run-based): {self.db_path}")

    def save_transformation_run(self, run_info: Dict[str, Any]):
        """변환 실행(Run) 마스터 정보를 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO transformation_run (run_id, transformer_name, total_chunks, source_count, remarks)
                    VALUES (:run_id, :transformer_name, :total_chunks, :source_count, :remarks)
                """, {
                    "run_id": run_info['run_id'],
                    "transformer_name": run_info.get('transformer_name', 'default'),
                    "total_chunks": run_info.get('total_chunks', 0),
                    "source_count": run_info.get('source_count', 0),
                    "remarks": run_info.get('remarks', '')
                })
                conn.commit()
        except Exception as e:
            logger.error(f"Run 정보 저장 오류: {e}")
            raise

    def save_wiki_chunks(self, chunks_data: List[Dict[str, Any]]):
        """청크 리스트를 일괄 저장 (Run ID 포함)"""
        if not chunks_data:
            return

        prepared = [
            (
                d['run_id'],
                d['source'], 
                d['hierarchy'], 
                d['content'], 
                d.get('char_count', len(d['content'])),
                json.dumps(d.get('metadata', {}), ensure_ascii=False)
            )
            for d in chunks_data
        ]

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executemany("""
                    INSERT INTO wiki_chunk (run_id, source, hierarchy, content, char_count, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, prepared)
                conn.commit()
            logger.info(f"Repository: {len(chunks_data)}개 wiki_chunk 저장 완료 (Run: {chunks_data[0]['run_id']})")
        except Exception as e:
            logger.error(f"청크 저장 오류: {e}")
            raise

    def update_run_finished_at(self, run_id: str):
        """작업이 완료된 시점에 finished_at을 현재 시간으로 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE transformation_run 
                    SET finished_at = CURRENT_TIMESTAMP 
                    WHERE run_id = ?
                """, (run_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Run 종료 시간 업데이트 오류: {e}")

    def get_run_statistics(self):
        """분석을 위해 실행별 통계 정보를 조회"""
        query = """
            SELECT r.run_id, r.transformer_name, r.total_chunks, AVG(c.char_count) as avg_len, r.created_at
            FROM transformation_run r
            JOIN wiki_chunk c ON r.run_id = c.run_id
            GROUP BY r.run_id
            ORDER BY r.created_at DESC
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(query).fetchall()]
    