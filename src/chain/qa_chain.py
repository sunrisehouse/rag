from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.llm import InternalChatModel
from src.vectorstore import ESVectorStoreManager
from src.embedder import LocalEmbedder

from src.logger import get_logger

logger = get_logger(__name__)

class QAChain:
    """
    Elasticsearch 검색과 사내 LLM을 결합하여 
    위키 기반 질의응답을 수행하는 LangChain LCEL 체인 클래스입니다.
    """
    def __init__(self, index_name: str = "wiki_rag_index"):
        # 1. 컴포넌트 로드
        self.embedder = LocalEmbedder()
        self.vector_store = ESVectorStoreManager(
            index_name=index_name,
            embedding_model=self.embedder.get_model()
        )
        self.internal_llm = InternalChatModel()
        
        # 2. 검색기(Retriever) 설정
        # k=5: 가장 관련성 높은 5개의 위키 청크를 가져옴
        self.retriever = self.vector_store.store.as_retriever(
            search_kwargs={"k": 5}
        )

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
        3. 답변은 정중하고 전문적인 어조를 유지하세요.

        [Context]
        {context}

        질문: {question}
        답변:"""
        return ChatPromptTemplate.from_template(template)

    def _format_docs(self, docs):
        """검색된 문서들을 LLM이 읽기 좋은 텍스트 형태로 변환합니다."""
        # 각 청크의 계층 정보와 본문을 합쳐서 전달
        return "\n\n".join(doc.page_content for doc in docs)

    def _build_chain(self):
        """LangChain LCEL을 사용하여 컴포넌트들을 연결합니다."""
        # 1. 질문을 받아 검색기로 전달하여 컨텍스트 추출
        # 2. 질문 원문과 컨텍스트를 프롬프트에 주입
        # 3. LLM 호출 및 결과 파싱
        chain = (
            {
                "context": self.retriever | self._format_docs, 
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.internal_llm.model
            | StrOutputParser()
        )
        return chain

    def get_chain(self):
        """생성된 체인 객체를 반환합니다."""
        return self.chain

    def ask(self, query: str):
        """동기 방식으로 질문에 답변합니다."""
        logger.info(f"질문 접수: {query}")
        return self.chain.invoke(query)

    def stream_ask(self, query: str):
        """실시간 스트리밍 방식으로 답변을 생성합니다."""
        logger.info(f"스트리밍 질문 접수: {query}")
        return self.chain.stream(query)