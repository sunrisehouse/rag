import os
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from src.logger import get_logger

logger = get_logger(__name__)

class LocalEmbedder:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        # 1. 모델을 저장할 로컬 경로 설정 (프로젝트 루트의 models 폴더)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_path = os.path.join(project_root, "models", model_name.replace("/", "_"))
        
        # 2. 폴더가 없으면 생성
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path, exist_ok=True)
            logger.info(f"모델 저장 폴der 생성: {self.model_path}")

        # 3. 디바이스 설정
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        
        logger.info(f"로컬 모델 로드 시도: {self.model_path} (Device: {device})")

        # 4. 모델 로드 (cache_folder를 지정하면 해당 경로에 저장 및 로드함)
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                cache_folder=os.path.join(project_root, "models"), # 모델 다운로드 위치 고정
                model_kwargs={'device': device},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info("로컬 임베딩 모델 준비 완료.")
        except Exception as e:
            logger.error(f"모델 로딩 실패: {e}")
            raise

    def get_model(self):
        return self.embeddings