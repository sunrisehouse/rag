from abc import ABC, abstractmethod
from typing import List, Dict

class BaseVectorStore(ABC):
    @abstractmethod
    def search(self, query_vector: List[float], k: int, num_candidates: int) -> List[Dict]:
        """
        Searches the vector store for the k nearest neighbors to the query_vector.
        """
        pass
