import os
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from src.logger import get_logger

logger = get_logger(__name__)

class LocalEmbedder:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        # 1. 모델이 실제로 저장되어 있는 절대 경로 계산
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_path = os.path.join(project_root, "models", model_name.replace("/", "_"))
        
        # 2. 디바이스 설정
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        
        logger.info(f"로컬 파일만 사용하여 모델 로드 시도: {self.model_path}")

        # 3. 모델 로드
        try:
            self.embeddings = HuggingFaceEmbeddings(
                # CRITICAL: model_name에 허깅페이스 ID 대신 '로컬 절대 경로'를 넣습니다.
                model_name=self.model_path, 
                model_kwargs={
                    'device': device,
                    # 핵심 옵션: 허깅페이스 허브 접속을 완전히 차단하고 로컬 파일만 봅니다.
                    'local_files_only': True 
                },
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info("로컬 임베딩 모델 준비 완료.")
        except Exception as e:
            logger.error(f"모델 로딩 실패: {e}")
            raise

    def get_model(self):
        return self.embeddings