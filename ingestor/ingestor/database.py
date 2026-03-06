import sqlite3
import datetime
from .logger import log
from . import config

def get_db_connection():
    """데이터베이스 커넥션을 반환합니다."""
    return sqlite3.connect(config.DB_PATH)

def init_db():
    """Ingestion 관련 테이블을 초기화합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ingestion 실행 정보를 기록할 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingestion_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        status TEXT NOT NULL,
        source_type TEXT NOT NULL,  -- 'sqlite' or 'pdf'
        embedding_model TEXT NOT NULL
    )
    """)

    # 각 문서의 Ingestion 상태를 기록할 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingested_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingestion_job_id INTEGER NOT NULL,
        source_type TEXT NOT NULL,
        source_id INTEGER NOT NULL,  -- crawled_pages.id or pdf_files.id
        status TEXT NOT NULL, -- 'pending', 'success', 'failed'
        error_message TEXT,
        vector_id TEXT, -- Elasticsearch document ID
        processed_at TIMESTAMP,
        FOREIGN KEY (ingestion_job_id) REFERENCES ingestion_jobs (id)
    )
    """)
    conn.commit()
    conn.close()
    log.info("Ingestion database tables initialized.")

def create_ingestion_job(source_type, embedding_model):
    """새로운 Ingestion 작업을 생성하고 ID를 반환합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    start_time = datetime.datetime.now()
    status = "running"
    
    try:
        cursor.execute("""
        INSERT INTO ingestion_jobs (start_time, status, source_type, embedding_model)
        VALUES (?, ?, ?, ?)
        """, (start_time, status, source_type, embedding_model))
        job_id = cursor.lastrowid
        conn.commit()
        log.info(f"Created new ingestion job ID: {job_id} for source '{source_type}'")
        return job_id
    finally:
        conn.close()

def finish_ingestion_job(job_id, status):
    """Ingestion 작업을 완료 처리합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    end_time = datetime.datetime.now()
    
    try:
        cursor.execute("""
        UPDATE ingestion_jobs SET end_time = ?, status = ? WHERE id = ?
        """, (end_time, status, job_id))
        conn.commit()
        log.info(f"Finished ingestion job {job_id} with status: {status}")
    finally:
        conn.close()

def get_unprocessed_html_pages():
    """아직 처리되지 않은 HTML 페이지 목록을 가져옵니다."""
    conn = get_db_connection()
    # 결과를 딕셔너리 형태로 받기 위해 row_factory 설정
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # ingested_documents에 성공적으로 기록되지 않은 페이지를 찾습니다.
        cursor.execute("""
        SELECT cp.id, cp.url, cp.html_content
        FROM crawled_pages cp
        LEFT JOIN ingested_documents id ON cp.id = id.source_id AND id.source_type = 'sqlite'
        WHERE id.id IS NULL OR id.status != 'success'
        """)
        pages = cursor.fetchall()
        log.info(f"Found {len(pages)} unprocessed HTML pages.")
        return pages
    finally:
        conn.close()

def log_ingestion_status(job_id, source_type, source_id, status, vector_id=None, error_message=None):
    """개별 문서의 처리 상태를 기록합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    processed_at = datetime.datetime.now()
    
    try:
        cursor.execute("""
        INSERT INTO ingested_documents 
        (ingestion_job_id, source_type, source_id, status, vector_id, error_message, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (job_id, source_type, source_id, status, vector_id, error_message, processed_at))
        conn.commit()
    except Exception as e:
        log.error(f"Failed to log ingestion status for source {source_type}-{source_id}. Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
