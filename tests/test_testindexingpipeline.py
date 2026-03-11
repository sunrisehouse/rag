import os
import sys
import json
import shutil
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.pipeline import TestIndexingPipeline

def test():
    # use_mock=True 옵션으로 실행
    pipeline = TestIndexingPipeline(data_dir="data/test_json")
    pipeline.run()
    
    # 검색 테스트
    results = pipeline.vector_store.search("hello")
    print(f"검색 결과 수: {len(results)}")
    if results:
        print(f"첫 번째 결과: {results[0].page_content}")

if __name__ == "__main__":
    test()