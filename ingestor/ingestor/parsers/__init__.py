from .html_parser import HTMLParser
from .pdf_parser import PDFParser

def get_parser(source_type: str):
    """소스 유형에 맞는 파서 인스턴스를 반환합니다."""
    if source_type == 'sqlite' or source_type == 'html':
        return HTMLParser()
    elif source_type == 'pdf':
        return PDFParser()
    else:
        raise ValueError(f"Unsupported source type: {source_type}")
