from . import config
from .logger import log
from .database import (
    init_db,
    create_ingestion_job,
    finish_ingestion_job,
    get_unprocessed_html_pages,
    log_ingestion_status
)
from .parsers import get_parser
from .embedders import get_embedding_model
from .vector_store import VectorStore
from .text_splitter import RecursiveCharacterTextSplitter

def run_ingestion():
    """
    SQLite DB에서 크롤링된 데이터를 설정에 따라 Elasticsearch 또는 SQLite 벡터 저장소로
    인덱싱하는 전체 프로세스를 실행합니다.
    """
    log.info("Starting ingestion process...")
    
    # 1. 초기화
    init_db()
    source_type = 'sqlite'
    embedding_model_name = config.EMBEDDING_MODEL
    
    job_id = create_ingestion_job(source_type, embedding_model_name)
    if not job_id:
        log.error("Failed to create ingestion job. Aborting.")
        return

    try:
        # 2. 모듈 로드 (Parser, Embedder, VectorStore, TextSplitter)
        parser = get_parser(source_type)
        embedding_model = get_embedding_model()
        vector_store = VectorStore()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        
        # 임베딩 차원 확인 및 인덱스 생성
        test_embedding = embedding_model.embed("test")
        embedding_dim = len(test_embedding)
        vector_store.create_index_if_not_exists(embedding_dim)

        # 3. 처리할 데이터 가져오기
        pages = get_unprocessed_html_pages()
        if not pages:
            log.info("No new pages to process.")
            finish_ingestion_job(job_id, "completed_no_data")
            return

        # 4. 데이터 처리 루프
        success_chunk_count = 0
        fail_chunk_count = 0
        for page in pages:
            page_id = page['id']
            try:
                log.debug(f"Processing page ID: {page_id}, URL: {page['url']}")
                
                # 4-1. 파싱
                text_content = parser.parse(page['html_content'])
                if not text_content:
                    log.warning(f"No content parsed from page ID: {page_id}. Skipping.")
                    continue
                
                # 4-2. 텍스트 분할
                chunks = text_splitter.split_text(text_content)
                log.info(f"Page ID {page_id} split into {len(chunks)} chunks.")

                for i, chunk in enumerate(chunks):
                    try:
                        # 4-3. 임베딩
                        vector = embedding_model.embed(chunk)
                        if not vector:
                            raise ValueError("Embedding resulted in an empty vector.")

                        # 4-4. 벡터 DB에 인덱싱
                        metadata = {"source_url": page['url']}
                        vector_id = vector_store.index_document(chunk, vector, metadata)

                        # 4-5. 성공 로그 기록
                        log_ingestion_status(job_id, source_type, page_id, "success", vector_id=f"{vector_id}_chunk_{i}")
                        success_chunk_count += 1
                        log.debug(f"Successfully indexed chunk {i+1}/{len(chunks)} for page ID: {page_id}")
                    
                    except Exception as chunk_e:
                        fail_chunk_count += 1
                        log.error(f"Failed to process chunk {i+1}/{len(chunks)} for page ID: {page_id}. Error: {chunk_e}", exc_info=True)
                        log_ingestion_status(job_id, source_type, page_id, "failed", error_message=str(chunk_e))

            except Exception as page_e:
                fail_chunk_count += 1 # 페이지 전체 실패도 실패 카운트에 포함
                log.error(f"Failed to process page ID: {page_id}. Error: {page_e}", exc_info=True)
                log_ingestion_status(job_id, source_type, page_id, "failed", error_message=str(page_e))
        
        log.info(f"Ingestion process summary: {success_chunk_count} chunks succeeded, {fail_chunk_count} chunks failed.")
        finish_ingestion_job(job_id, "completed")

    except Exception as e:
        log.critical(f"A critical error occurred during the ingestion process: {e}", exc_info=True)
        finish_ingestion_job(job_id, "failed")
    finally:
        log.info("Ingestion process finished.")

if __name__ == "__main__":
    run_ingestion()
