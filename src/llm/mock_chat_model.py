from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
# AIChatMessage 대신 AIMessage를 사용합니다.
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks import CallbackManagerForLLMRun

from src.logger import get_logger

logger = get_logger(__name__)

class MockChatModel(BaseChatModel):
    """
    사내 LLM 서버 없이 체인 로직을 테스트하기 위한 Mock 채팅 모델
    """
    # model_name은 필수가 아니지만 식별을 위해 추가
    model_name: str = "mock-internal-llama"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        # 굳이 입력 메시지 전체를 보여줄 필요 없이 깔끔한 고정 답변 생성
        logger.info("generate!!")
        mock_response = "현재 시스템은 Mock 모드입니다. 검색된 [Context]를 바탕으로 생성된 가상의 답변입니다."
        
        message = AIMessage(content=mock_response)
        return ChatResult(generations=[ChatGeneration(message=message)])

    @property
    def _llm_type(self) -> str:
        return "mock-internal-chat"