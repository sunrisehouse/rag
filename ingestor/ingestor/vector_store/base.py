from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseVectorStore(ABC):
    """
    모든 벡터 저장소 클래스가 상속해야 하는 기본 클래스입니다.
    벡터 데이터를 저장하고 관리하는 공통 인터페이스를 정의합니다.
    """

    @abstractmethod
    def create_index_if_not_exists(self, embedding_dim: int):
        """
        인덱스 또는 테이블이 존재하지 않으면, 벡터 저장을 위한 공간을 생성합니다.

        :param embedding_dim: 저장할 임베딩 벡터의 차원 수
        """
        pass

    @abstractmethod
    def index_document(self, text: str, vector: List[float], metadata: Dict[str, Any]) -> str:
        """
        단일 문서를 벡터 저장소에 저장(인덱싱)합니다.

        :param text: 원본 텍스트
        :param vector: 임베딩 벡터
        :param metadata: 추가 정보 (e.g., URL, 수집 시간)
        :return: 저장된 문서의 고유 ID (문자열 형태)
        """
        pass
