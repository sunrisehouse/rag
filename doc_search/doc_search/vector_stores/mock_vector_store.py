from typing import List, Dict
from .base import BaseVectorStore

class MockVectorStore(BaseVectorStore):
    """A mock vector store for testing without a real database."""

    def search(self, query_vector: List[float], k: int, num_candidates: int) -> List[Dict]:
        print("MockVectorStore: Searching with a query vector.")
        
        # Predefined fake results for consistent testing
        fake_hits = [
            {
                "_score": 0.95,
                "_source": {
                    "text": "This is the content of the first fake document from the mock vector store.",
                    "url": "http://fake-docs.com/doc1"
                }
            },
            {
                "_score": 0.91,
                "_source": {
                    "text": "This is the second mock document, useful for testing different scenarios.",
                    "url": "http://fake-docs.com/doc2"
                }
            }
        ]
        
        # Return up to 'k' documents
        return fake_hits[:k]
