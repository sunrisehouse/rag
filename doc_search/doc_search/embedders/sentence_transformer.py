from sentence_transformers import SentenceTransformer
from typing import List
from .base import BaseEmbedder
from .. import config

class SentenceTransformerEmbedder(BaseEmbedder):
    def __init__(self):
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)

    def encode(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
