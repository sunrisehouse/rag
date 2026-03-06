from elasticsearch import Elasticsearch
from typing import List, Dict
from .base import BaseVectorStore
from .. import config

class ElasticsearchVectorStore(BaseVectorStore):
    def __init__(self):
        auth_params = {}
        if config.ELASTICSEARCH_API_ID and config.ELASTICSEARCH_API_KEY:
            auth_params['api_key'] = (config.ELASTICSEARCH_API_ID, config.ELASTICSEARCH_API_KEY)
        elif config.ELASTICSEARCH_USERNAME and config.ELASTICSEARCH_PASSWORD:
            auth_params['basic_auth'] = (config.ELASTICSEARCH_USERNAME, config.ELASTICSEARCH_PASSWORD)
        
        self.client = Elasticsearch(
            config.ELASTICSEARCH_HOST,
            **auth_params
        )
        
        if not self.client.ping():
            raise RuntimeError("Could not connect to Elasticsearch")

    def search(self, query_vector: List[float], k: int, num_candidates: int) -> List[Dict]:
        knn_query = {
            "field": "embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": num_candidates
        }
        
        response = self.client.search(
            index=config.ELASTICSEARCH_INDEX_NAME,
            knn=knn_query,
            _source=["text", "url"]
        )
        
        return response['hits']['hits']
