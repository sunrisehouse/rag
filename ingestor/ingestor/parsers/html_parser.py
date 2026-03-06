from bs4 import BeautifulSoup
from .base import BaseParser

class HTMLParser(BaseParser):
    """HTML 컨텐츠에서 텍스트를 추출하는 파서입니다."""

    def parse(self, content: str) -> str:
        """
        BeautifulSoup을 사용하여 HTML에서 텍스트를 추출합니다.
        
        :param content: HTML 문자열
        :return: 추출된 텍스트
        """
        if not content:
            return ""
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # 불필요한 태그(script, style) 제거
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        # 텍스트 추출 및 공백 정제
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        return text
