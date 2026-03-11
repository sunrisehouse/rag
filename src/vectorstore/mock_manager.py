from typing import List, Any, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun

from src.logger import get_logger

logger = get_logger(__name__)

class MockVectorStoreManager:
    """
    Elasticsearch 없이 메모리 내에서 동작하는 테스트용 Mock VectorStore.
    실제 임베딩 계산을 하지 않고 단순 텍스트 매칭으로 결과를 반환합니다.
    """
    def __init__(self, index_name: str, embedding_model: Any = None):
        self.index_name = index_name
        self.documents: List[Document] = []
        logger.info(f"🛠 MockVectorStore 초기화됨 (Index: {index_name})")

    def add_documents(self, documents: List[Document]):
        """메모리 리스트에 문서 추가"""
        if not documents:
            return
        self.documents.extend(documents)
        logger.info(f"🛠 Mock: {len(documents)}개 문서가 메모리에 적재되었습니다.")
        # 가상의 ID 리스트 반환
        return [f"mock_id_{i}" for i in range(len(documents))]

    def search(self, query: str, k: int = 5) -> List[Document]:
        """키워드 포함 여부로 간단 검색 (유사도 점수 없음)"""
        logger.info(f"🛠 Mock 검색 수행 중: '{query}'")
        
        # 쿼리 단어가 포함된 문서를 우선적으로 필터링
        results = [
            doc for doc in self.documents 
            if query.lower() in doc.page_content.lower()
        ]
        
        # 검색 결과가 부족하면 전체에서 상위 k개 반환 (Fallback)
        if not results:
            results = self.documents[:k]
            
        return results[:k]

    def as_retriever(self, **kwargs):
        """
        LangChain 체인 연동을 위한 Mock Retriever 인스턴스를 반환합니다.
        BaseRetriever는 Pydantic 모델이므로 인자 전달 시 키워드 인자가 필수입니다.
        """
        
        # 내부 클래스로 MockRetriever 정의
        class MockRetriever(BaseRetriever):
            docs: List[Document]  # 검색 대상이 될 문서 리스트 필드
            
            def _get_relevant_documents(
                self, query: str, *, run_manager: CallbackManagerForRetrieverRun
            ) -> List[Document]:
                # 텍스트 포함 여부로 검색 수행
                return [d for d in self.docs if query.lower() in d.page_content.lower()][:5]

        # ✅ 핵심 수정: 클래스가 아닌 '인스턴스'를 생성하여 반환하며, 
        # 반드시 'docs=' 키워드 인자를 사용합니다.
        return MockRetriever(docs=self.documents)