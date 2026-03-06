from elasticsearch import Elasticsearch
from typing import List, Dict, Any
from .. import config
from ..logger import log

from .base import BaseVectorStore

class ElasticsearchStore(BaseVectorStore):
    """Elasticsearch를 벡터 스토어로 사용하기 위한 클래스"""

    def __init__(self):
        try:
            self.client = Elasticsearch(
                [{'host': config.ES_HOST, 'port': config.ES_PORT, 'scheme': 'http'}]
            )
            if not self.client.ping():
                raise ConnectionError("Could not connect to Elasticsearch.")
            log.info("Successfully connected to Elasticsearch.")
        except Exception as e:
            log.error(f"Failed to connect to Elasticsearch: {e}")
            raise

    def create_index_if_not_exists(self, embedding_dim: int):
        """
        인덱스가 존재하지 않으면 벡터 검색에 최적화된 매핑으로 생성합니다.
        :param embedding_dim: 임베딩 벡터의 차원
        """
        index_name = config.ES_INDEX_NAME
        if not self.client.indices.exists(index=index_name):
            log.info(f"Index '{index_name}' not found. Creating new index.")
            mapping = {
                "properties": {
                    "embedding": {
                        "type": "dense_vector",
                        "dims": embedding_dim
                    },
                    "text": {
                        "type": "text"
                    },
                    "source_url": {
                        "type": "keyword"
                    },
                    "crawled_at": {
                        "type": "date"
                    }
                }
            }
            try:
                self.client.indices.create(index=index_name, mappings=mapping)
                log.info(f"Index '{index_name}' created successfully with {embedding_dim}-dimensional vector mapping.")
            except Exception as e:
                log.error(f"Failed to create index '{index_name}'. Error: {e}")
                raise
        else:
            log.info(f"Index '{index_name}' already exists.")

    def index_document(self, text: str, vector: List[float], metadata: Dict[str, Any]) -> str:
        """
        단일 문서를 Elasticsearch에 인덱싱합니다.
        :param text: 원본 텍스트
        :param vector: 임베딩 벡터
        :param metadata: 추가 정보 (e.g., URL, 수집 시간)
        :return: 생성된 Elasticsearch 문서 ID
        """
        doc = {
            "text": text,
            "embedding": vector,
            **metadata
        }
        try:
            response = self.client.index(index=config.ES_INDEX_NAME, document=doc)
            return response['_id']
        except Exception as e:
            log.error(f"Failed to index document. Metadata: {metadata}. Error: {e}")
            raise
