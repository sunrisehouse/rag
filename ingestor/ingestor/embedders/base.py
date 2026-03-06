from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddingModel(ABC):
    """
    모든 임베딩 모델이 상속해야 하는 기본 클래스입니다.
    텍스트를 벡터로 변환하는 공통 인터페이스를 정의합니다.
    """
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        단일 텍스트를 임베딩 벡터로 변환합니다.

        :param text: 임베딩할 텍스트
        :return: 부동소수점 값의 리스트로 표현된 벡터
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        여러 텍스트를 배치 처리하여 임베딩 벡터 리스트로 변환합니다.

        :param texts: 임베딩할 텍스트의 리스트
        :return: 벡터의 리스트
        """
        pass
