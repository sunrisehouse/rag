import os
from typing import List
from sentence_transformers import SentenceTransformer
from .base import BaseEmbeddingModel
from ..logger import log
from .. import config

class SentenceTransformerModel(BaseEmbeddingModel):
    """
    Hugging Face의 SentenceTransformer 라이브러리를 사용하는 임베딩 모델입니다.
    모델을 로컬 경로에 다운로드하고 관리합니다.
    """
    def __init__(self, model_name: str):
        """
        :param model_name: Hugging Face 모델 이름 (e.g., "jhgan/ko-sbert-nli")
        """
        model_save_path = os.path.join(config.EMBEDDING_MODEL_SAVE_PATH, model_name.replace("/", "_"))

        try:
            # 모델이 로컬에 저장되어 있는지 확인하고, 없으면 다운로드합니다.
            if not os.path.exists(model_save_path):
                log.info(f"Model '{model_name}' not found locally. Downloading and saving to '{model_save_path}'.")
                # Hugging Face Hub에서 모델 다운로드
                model_to_save = SentenceTransformer(model_name)
                model_to_save.save(model_save_path)
                log.info(f"Model successfully saved to '{model_save_path}'.")

            # 로컬 경로에서 모델 로드
            log.info(f"Loading SentenceTransformer model from local path: {model_save_path}")
            self.model = SentenceTransformer(model_save_path)
            log.info("Model loaded successfully from local path.")
            
        except Exception as e:
            log.error(f"Failed to load or download SentenceTransformer model '{model_name}'. Error: {e}")
            log.error("Please check your internet connection, model name, and permissions to write to the save directory.")
            raise e

    def embed(self, text: str) -> List[float]:
        """단일 텍스트를 임베딩합니다."""
        if not text:
            return []
        vector = self.model.encode(text)
        return vector.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """텍스트 배치를 임베딩합니다."""
        if not texts:
            return []
        vectors = self.model.encode(texts)
        return [v.tolist() for v in vectors]
