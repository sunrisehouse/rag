from typing import List

class RecursiveCharacterTextSplitter:
    """재귀적으로 문자를 분할하는 클래스입니다."""
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        주어진 텍스트를 설정된 chunk_size와 chunk_overlap에 따라 분할합니다.
        
        :param text: 분할할 텍스트
        :return: 분할된 텍스트 청크 리스트
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start_index = 0
        while start_index < len(text):
            end_index = start_index + self.chunk_size
            chunk = text[start_index:end_index]
            chunks.append(chunk)
            start_index += self.chunk_size - self.chunk_overlap
            
        return chunks
