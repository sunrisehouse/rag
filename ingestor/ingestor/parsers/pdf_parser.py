from .base import BaseParser

class PDFParser(BaseParser):
    """PDF 파일에서 텍스트를 추출하는 파서입니다. (향후 구현)"""

    def parse(self, content: str) -> str:
        """
        PDF 파일 경로를 받아 텍스트를 추출합니다.
        
        TODO: PyMuPDF(fitz) 또는 pypdf 라이브러리를 사용하여 구현해야 합니다.
        
        :param content: PDF 파일의 바이너리 내용 또는 파일 경로
        :return: 추출된 텍스트
        """
        # 이 부분은 향후 PDF 처리 라이브러리를 사용하여 구현됩니다.
        raise NotImplementedError("PDF parsing is not yet implemented.")
