import os
from typing import Optional
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from src.logger import get_logger

logger = get_logger(__name__)

# 환경 변수 로드 (.env 파일에서 서버 URL 등을 가져옴)
load_dotenv()

class InternalChatModel:
    """
    사내망에 구축된 자체 LLM 서버(OpenAI API 호환)와 통신하는 
    LangChain 기반의 ChatModel 관리 클래스입니다.
    """
    
    def __init__(self):
        # 1. 환경 변수로부터 설정값 로드
        self.api_url = os.getenv("INTERNAL_LLM_URL", "http://your-internal-llm-host:8000/v1")
        self.api_key = os.getenv("INTERNAL_LLM_KEY", "no-key-required")
        self.model_name = os.getenv("INTERNAL_MODEL_NAME", "internal-llama-3")
        
        # 2. 성능 및 동작 관련 세부 설정
        self.temperature = float(os.getenv("LLM_TEMPERATURE", 0.0))  # RAG는 0.0 권장 (객관성)
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", 2048))
        self.timeout = int(os.getenv("LLM_TIMEOUT", 60))
        
        # 3. 모델 인스턴스 초기화
        self._llm = self._init_chat_model()

    def _init_chat_model(self) -> ChatOpenAI:
        """
        내부 서버 정보를 바탕으로 LangChain ChatOpenAI 객체를 생성합니다.
        """
        try:
            # vLLM, Ollama, TGI 등 사내 구축 엔진은 대부분 OpenAI 규격 엔드포인트를 제공합니다.
            chat_model = ChatOpenAI(
                base_url=self.api_url,
                api_key=self.api_key,
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                streaming=True,  # 실시간 답변 생성을 위해 기본 활성화
                # 사내망 특이사항(Self-signed SSL 등)이 있을 경우 아래에 http_client 설정을 추가할 수 있습니다.
            )
            logger.info(f"✅ 사내 LLM 연결 성공: {self.model_name} ({self.api_url})")
            return chat_model
            
        except Exception as e:
            logger.error(f"❌ 사내 LLM 초기화 중 오류 발생: {e}")
            raise

    @property
    def model(self) -> ChatOpenAI:
        """초기화된 LangChain ChatModel 객체를 반환합니다."""
        return self._llm

    def get_info(self) -> dict:
        """현재 연결된 모델의 정보를 반환합니다."""
        return {
            "model_name": self.model_name,
            "api_url": self.api_url,
            "temperature": self.temperature
        }