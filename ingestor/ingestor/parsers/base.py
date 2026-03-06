from abc import ABC, abstractmethod

class BaseParser(ABC):
    """
    모든 파서가 상속해야 하는 기본 클래스입니다.
    다양한 문서 유형(HTML, PDF 등)으로부터 텍스트를 추출하는
    공통 인터페이스를 정의합니다.
    """
    @abstractmethod
    def parse(self, content: str) -> str:
        """
        입력된 컨텐츠에서 텍스트를 추출합니다.

        :param content: 파일의 내용 (e.g., HTML 문자열)
        :return: 추출된 순수 텍스트
        """
        pass
