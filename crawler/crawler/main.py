from . import database
from .crawler import Crawler
from .logger import log

def main():
    """크롤러 실행 메인 함수."""
    
    # 1. 데이터베이스 초기화
    log.info("Initializing database...")
    database.init_db()
    
    # 2. 크롤링 작업 생성
    job_id = database.create_crawl_job()
    if not job_id:
        log.critical("Could not create a crawl job. Aborting.")
        return

    # 3. 크롤러 인스턴스 생성
    log.info(f"Creating crawler instance for job ID: {job_id}")
    crawler = Crawler(crawl_job_id=job_id)
    
    job_status = "failed" # 기본 상태를 'failed'로 설정
    try:
        # 4. 크롤링 시작
        crawler.crawl()
        job_status = "completed" # 성공적으로 완료되면 상태 변경
    
    except KeyboardInterrupt:
        job_status = "interrupted"
        log.warning("\nCrawling interrupted by user.")
    
    except Exception as e:
        log.critical(f"\nAn unexpected error occurred: {e}", exc_info=True)
        # job_status는 이미 'failed'
    
    finally:
        # 5. 크롤러 종료 (브라우저 닫기)
        crawler.close()
        
        # 6. 크롤링 작업 상태 업데이트
        database.finish_crawl_job(job_id, status=job_status)
        
        log.info(f"Crawler has been shut down. Job {job_id} finished with status '{job_status}'.")

if __name__ == '__main__':
    main()