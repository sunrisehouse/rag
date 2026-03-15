import os
import sys
import sqlite3

# 1. 프로젝트 루트를 경로에 추가 (ModuleNotFoundError 방지)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.documents import Document
from src.transformer.wiki_structure_transformer import WikiStructureTransformer
from src.database.repository import Repository
from src.logger import get_logger

logger = get_logger(__name__)

def test_transformer():
    logger.info("=== WikiStructureTransformer 테스트 시작 ===")
    
    # 2. 테스트용 DB 및 Repository 설정
    db_path = "data/main.db"
    if os.path.exists(db_path):
        os.remove(db_path)  # 깨끗한 테스트를 위해 기존 DB 삭제
    
    repo = Repository(db_path=db_path)
    transformer = WikiStructureTransformer(repository=repo)

    # 3. 테스트용 복잡한 HTML 샘플 (중첩 구조 포함)
    html_content = """
    <div class="wiki-content">
        <h1>서비스 가이드</h1>
        <p>서비스의 전체 개요입니다.</p>
        <h2>설치 방법</h2>
        <div class="nested-container">
            <h1>환경 설정</h1>
            <p>파이썬 3.9 이상이 필요합니다.</p>
            <pre>pip install -r requirements.txt</pre>
        </div>
        <h2>실행 방법</h2>
        <p>python main.py를 입력하세요.</p>
    </div>
    """
    
    raw_docs = [
        Document(
            page_content=html_content, 
            metadata={"source": "test_wiki.html", "author": "admin"}
        )
    ]

    # 4. 트랜스포머 실행
    logger.info("변환 및 DB 저장 수행 중...")
    chunked_docs = transformer.transform_documents(raw_docs)

    # 5. 결과 검증 (LangChain Document 형태)
    print("\n--- [1] 변환된 Document 객체 확인 ---")
    for i, doc in enumerate(chunked_docs):
        print(f"Chunk #{i+1}")
        print(f"  - 계층(Hierarchy): {doc.metadata.get('hierarchy')}")
        print(f"  - 내용(Content): {doc.page_content[:60]}...")
        print("-" * 30)

    # 6. DB 저장 결과 확인 (SQLite 직접 조회)
    print("\n--- [2] SQLite (main.db) 저장 데이터 확인 ---")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, hierarchy, content FROM wiki_chunks")
        rows = cursor.fetchall()
        
        for row in rows:
            print(f"DB ID: {row[0]}")
            print(f"  - 저장된 계층: {row[1]}")
            print(f"  - 저장된 본문: {row[2][:50]}...")
            print("-" * 30)

    if len(rows) > 0:
        print(f"\n✅ 테스트 성공! 총 {len(rows)}개의 청크가 처리되었습니다.")

if __name__ == "__main__":
    try:
        test_transformer()
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()