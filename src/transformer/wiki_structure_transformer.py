import re
import uuid
from datetime import datetime
from typing import Any, Sequence
from bs4 import BeautifulSoup, Tag
from langchain_core.documents import BaseDocumentTransformer, Document
from src.database import Repository
from src.logger import get_logger

logger = get_logger(__name__)

class WikiStructureTransformer(BaseDocumentTransformer):
    def __init__(self, repository: Repository = None):
        super().__init__()
        self.repo = repository or Repository()
        self.transformer_name = "WikiStructureTransformer"
        # 실행 시점에 고유 ID 부여
        self.run_id = f"RUN_{datetime.now().strftime('%m%d_%H%M')}_{str(uuid.uuid4())[:4]}"

    def transform_documents(self, documents: Sequence[Document], **kwargs: Any) -> Sequence[Document]:
        final_docs = []
        all_db_data = []
        processed_sources = set()

        for doc in documents:
            source = doc.metadata.get('source', 'Unknown')
            processed_sources.add(source)
            soup = BeautifulSoup(doc.page_content, 'html.parser')
            content_area = soup.find(class_="wiki-content") or soup.body
            
            if not content_area: continue

            def traverse_children(node, incoming_stack):
                local_stack = list(incoming_stack)
                for child in node.children:
                    if not isinstance(child, Tag): continue

                    # 1. 헤더 처리
                    if re.match(r'h[1-6]', child.name):
                        header_text = child.get_text().strip()
                        if header_text: local_stack.append(header_text)
                        continue

                    # 2. 본문 청크 생성
                    if child.name in ['p', 'li', 'pre', 'table']:
                        text = child.get_text().strip()
                        if not text: continue
                        
                        h_path = " > ".join(local_stack)
                        full_content = f"[{h_path}] {text}" if h_path else text
                        
                        all_db_data.append({
                            "run_id": self.run_id,
                            "source": source,
                            "hierarchy": h_path,
                            "content": full_content,
                            "char_count": len(full_content),
                            "metadata": str({**doc.metadata, "hierarchy": h_path})
                        })
                        continue

                    traverse_children(child, local_stack)

            traverse_children(content_area, [])

        # 3. DB 적재 (Run 마스터 정보 + Chunk 상세 정보)
        if all_db_data:
            try:
                self.repo.save_transformation_run({
                    "run_id": self.run_id,
                    "transformer_name": self.transformer_name,
                    "total_chunks": len(all_db_data),
                    "source_count": len(processed_sources)
                })
                self.repo.save_wiki_chunks(all_db_data)
                self.repo.update_run_finished_at(self.run_id)
                logger.info(f"✨ [{self.run_id}] 트랜스포머 '{self.transformer_name}' 변환 완료 및 DB 저장 성공.")
            except Exception as e:
                logger.error(f"❌ DB 저장 실패: {e}")

        return final_docs