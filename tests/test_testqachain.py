import os
import sys
from langchain_core.documents import Document

# 프로젝트 루트 경로 추가 (src 폴더 인식용)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chain import TestQAChain

def run_test():
    qa_chain = TestQAChain()

    # 테스트 데이터 주입 (MockVectorStore에 데이터 넣기)
    qa_chain.vector_store.add_documents([
        Document(page_content="[설정 > 환경] 신규 프로젝트는 Python 3.10과 가상환경 설정이 필수입니다."),
        Document(page_content="[시스템 > 주기] 검색 엔진의 인덱싱 주기는 매일 새벽 2시입니다.")
    ])

    print("\n--- [1] 동기 방식 테스트 ---")
    response = qa_chain.ask("신규 프로젝트 환경 설정 방법이 뭐야?")
    print(f"답변: {response}")

    print("\n--- [2] 스트리밍 방식 테스트 ---")
    # 이제 stream_ask 에러가 나지 않습니다.
    for chunk in qa_chain.stream_ask("검색 엔진 인덱싱 주기가 어떻게 돼?"):
        print(chunk, end="", flush=True)
    print()

if __name__ == "__main__":
    run_test()