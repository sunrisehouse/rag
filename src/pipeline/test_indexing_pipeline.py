import os
import json
from typing import List
from langchain_core.documents import Document
from src.database import Repository
from src.transformer import WikiStructureTransformer

from src.logger import get_logger

logger = get_logger(__name__)

class TestIndexingPipeline:
    def __init__(self, data_dir: str = "data/raw_json"):
        self.data_dir = data_dir
        self.repo = Repository()
        self.transformer = WikiStructureTransformer(repository=self.repo)
        
        from src.vectorstore.mock_manager import MockVectorStoreManager
        self.vector_store = MockVectorStoreManager(index_name="mock_index")


    def extract(self) -> List[Document]:
        """JSON Array 파일에서 HTML 추출"""
        all_docs = []
        if not os.path.exists(self.data_dir): return []

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.data_dir, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for i, item in enumerate(data):
                        html = item.get("html", "")
                        if html:
                            all_docs.append(Document(
                                page_content=html,
                                metadata={"source": filename, "idx": i}
                            ))
        return all_docs

    def run(self):
        logger.info("🚀 인덱싱 파이프라인 시작")
        raw_docs = self.extract()
        if not raw_docs: return logger.info("처리할 데이터가 없습니다.")

        chunked_docs = self.transformer.transform_documents(raw_docs)
        self.vector_store.add_documents(chunked_docs)
        logger.info(f"✅ 완료: {len(chunked_docs)}개 청크 인덱싱됨.")
