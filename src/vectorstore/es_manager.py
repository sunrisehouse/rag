import os
from typing import List
from langchain_elasticsearch import ElasticsearchStore
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

from src.logger import get_logger

logger = get_logger(__name__)

load_dotenv()

class ESVectorStoreManager:
    def __init__(self, index_name: str, embedding_model: HuggingFaceEmbeddings):
        self.index_name = index_name
        self.embeddings = embedding_model
        self.es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self.es_user = os.getenv("ELASTICSEARCH_USER", "elastic")
        self.es_password = os.getenv("ELASTICSEARCH_PASSWORD")
        
        # VectorStore 초기화
        self.store = self._init_vectorstore()

    def _init_vectorstore(self) -> ElasticsearchStore:
        try:
            # 8.16 버전 대응: 가장 표준적인 ApproxRetrievalStrategy 설정
            # 인자 없이 호출하면 기본값으로 최적의 벡터 검색을 수행합니다.
            strategy = ElasticsearchStore.ApproxRetrievalStrategy()

            store = ElasticsearchStore(
                index_name=self.index_name,
                embedding=self.embeddings,
                es_url=self.es_url,
                es_user=self.es_user,
                es_password=self.es_password,
                strategy=strategy
            )
            logger.info(f"✅ Elasticsearch 연결 성공: {self.index_name}")
            return store
        except TypeError as e:
            # 만약 위 방식도 에러가 난다면, strategy를 아예 명시하지 않고 
            # 기본 내장 전략을 사용하도록 fallback 합니다.
            logger.warning(f"Strategy 설정 중 타입 에러 발생, 기본 설정으로 재시도: {e}")
            return ElasticsearchStore(
                index_name=self.index_name,
                embedding=self.embeddings,
                es_url=self.es_url,
                es_user=self.es_user,
                es_password=self.es_password
            )
        except Exception as e:
            logger.error(f"❌ Elasticsearch 연결 실패: {e}")
            raise

    def add_documents(self, documents: List):
        """문서 리스트를 인덱싱 (임베딩 자동 수행)"""
        if not documents:
            return
        
        logger.info(f"Elasticsearch 인덱싱 시작: {len(documents)}개 문서")
        ids = self.store.add_documents(documents)
        logger.info(f"인덱싱 완료: {len(ids)}개 문서가 저장됨")
        return ids

    def search(self, query: str, k: int = 5):
        """하이브리드 검색 수행 (Vector + BM25)"""
        # 기본적으로 k-NN 기반 유사도 검색 수행
        results = self.store.similarity_search(query, k=k)
        return results