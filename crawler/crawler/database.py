import sqlite3
import datetime
from .logger import log
from . import config

def get_db_connection():
    """Returns a connection to the database."""
    return sqlite3.connect(config.DB_PATH)

def init_db():
    """Initializes the database and creates tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create crawl_jobs table to record crawl execution information
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crawl_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        status TEXT NOT NULL
    )
    """)

    # Change pages table to crawled_pages and add crawl_job_id
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crawled_pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crawl_job_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        html_content TEXT NOT NULL,
        parent_url TEXT,
        crawled_at TIMESTAMP NOT NULL,
        FOREIGN KEY (crawl_job_id) REFERENCES crawl_jobs (id)
    )
    """)
    
    conn.commit()
    conn.close()
    log.info(f"Database '{config.DB_PATH}' initialized and tables are ready.")

def create_crawl_job():
    """Creates a new crawl job and returns the job ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    start_time = datetime.datetime.now()
    status = "running"
    
    try:
        cursor.execute("""
        INSERT INTO crawl_jobs (start_time, status) VALUES (?, ?)
        """, (start_time, status))
        job_id = cursor.lastrowid
        conn.commit()
        log.info(f"Created new crawl job with ID: {job_id}")
        return job_id
    except Exception as e:
        log.error(f"Failed to create a new crawl job. Error: {e}")
        return None
    finally:
        conn.close()

def finish_crawl_job(job_id, status):
    """Marks a specified crawl job as finished."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    end_time = datetime.datetime.now()
    
    try:
        cursor.execute("""
        UPDATE crawl_jobs SET end_time = ?, status = ? WHERE id = ?
        """, (end_time, status, job_id))
        conn.commit()
        log.info(f"Finished crawl job {job_id} with status: {status}")
    except Exception as e:
        log.error(f"Failed to finish crawl job {job_id}. Error: {e}")
    finally:
        conn.close()

def save_crawled_page(crawl_job_id, url, html_content, parent_url):
    """Saves crawled page information to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    crawled_at = datetime.datetime.now()
    
    try:
        cursor.execute("""
        INSERT INTO crawled_pages (crawl_job_id, url, html_content, parent_url, crawled_at)
        VALUES (?, ?, ?, ?, ?)
        """, (crawl_job_id, url, html_content, parent_url, crawled_at))
        conn.commit()
        log.debug(f"Successfully saved page for job {crawl_job_id}: {url}")
    except sqlite3.IntegrityError:
        log.warning(f"URL {url} might already be saved for this job.")
    except Exception as e:
        log.error(f"Failed to save page {url}. Error: {e}")
    finally:
        conn.close()

def get_crawled_urls(crawl_job_id: int = None):
    """
    Fetches URLs stored in the database. If a crawl_job_id is provided, 
    it fetches URLs only for that job. Otherwise, it fetches all URLs.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if crawl_job_id:
            cursor.execute("SELECT url FROM crawled_pages WHERE crawl_job_id = ?", (crawl_job_id,))
        else:
            cursor.execute("SELECT url FROM crawled_pages")
        
        rows = cursor.fetchall()
        return {row[0] for row in rows}
    except Exception as e:
        log.error(f"Failed to fetch crawled URLs. Error: {e}")
        return set()
    finally:
        conn.close()

if __name__ == '__main__':
    # Running this file directly initializes the database.
    init_db()