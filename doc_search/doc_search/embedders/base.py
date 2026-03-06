from abc import ABC, abstractmethod
from typing import List

class BaseEmbedder(ABC):
    @abstractmethod
    def encode(self, text: str) -> List[float]:
        """Encodes a string of text into a vector."""
        pass
