from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
# Mock 모델과 Mock 매니저 임포트
from src.llm import MockChatModel 
from src.vectorstore.mock_manager import MockVectorStoreManager

from src.logger import get_logger

logger = get_logger(__name__)

class TestQAChain:
    """
    Mock 구성요소들을 사용하여 
    위키 기반 질의응답 흐름을 테스트하는 전용 체인 클래스입니다.
    """
    def __init__(self):
        # 1. Mock 컴포넌트 로드
        # 로컬 임베딩 로드 없이 텍스트 매칭만 수행하도록 설정
        self.vector_store = MockVectorStoreManager(
            index_name="mock_wiki_index"
        )
        
        # BaseChatModel을 상속받은 Mock 모델 인스턴스 생성
        self.internal_llm = MockChatModel()
        
        # 2. 검색기(Retriever) 설정
        # MockVectorStoreManager의 as_retriever를 사용하여 체인에 연결
        self.retriever = self.vector_store.as_retriever()

        # 3. 사내 전용 RAG 프롬프트 정의
        self.prompt = self._get_rag_prompt()
        
        # 4. 최종 체인 구성
        self.chain = self._build_chain()

    def _get_rag_prompt(self) -> ChatPromptTemplate:
        """사내 위키 답변을 위한 시스템 프롬프트를 정의합니다."""
        template = """
        당신은 사내 위키 지식을 바탕으로 답변하는 전문 어시스턴트입니다.
        아래 제공된 [Context] 내의 정보만을 사용하여 사용자의 질문에 답변하세요.
        
        [지침]
        1. 답변은 반드시 [Context]에 근거해야 합니다. 근거가 없다면 "죄송합니다. 해당 내용은 위키에서 찾을 수 없습니다."라고 답하세요.
        2. 위키의 계층 구조(예: [A > B])를 참고하여 맥락에 맞는 정확한 정보를 제공하세요.

        [Context]
        {context}

        질문: {question}
        답변:"""
        return ChatPromptTemplate.from_template(template)

    def _format_docs(self, docs):
        """검색된 문서들을 LLM이 읽기 좋은 텍스트 형태로 변환합니다."""
        if not docs:
            return "검색된 관련 문서가 없습니다."
        return "\n\n".join(doc.page_content for doc in docs)

    def _build_chain(self):
        """LangChain LCEL을 사용하여 컴포넌트들을 연결합니다."""
        
        # self._format_docs를 RunnableLambda로 감싸서 파이프 연산이 가능하게 만듭니다.
        format_docs_runnable = RunnableLambda(self._format_docs)

        chain = (
            {
                # self.retriever가 클래스가 아닌 인스턴스인지 확인 필요
                "context": self.retriever | format_docs_runnable, 
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.internal_llm
            | StrOutputParser()
        )
        return chain

    def ask(self, query: str):
        """동기 방식으로 질문에 답변합니다."""
        logger.info(f"Mock 질문 접수: {query}")
        return self.chain.invoke(query)
    
    def stream_ask(self, query: str):
        """실시간 스트리밍 방식으로 답변을 생성합니다."""
        logger.info(f"Mock 스트리밍 질문 접수: {query}")
        # LCEL 체인은 기본적으로 .stream() 메서드를 지원합니다.
        return self.chain.stream(query)