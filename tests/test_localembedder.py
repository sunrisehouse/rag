import os
import sys
import torch

# 프로젝트 루트 경로 추가 (src 폴더 인식용)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embedder.local_embedder import LocalEmbedder
from src.logger import get_logger

logger = get_logger(__name__)

def test_local_embedder():
    logger.info("=== 로컬 임베더 테스트 시작 ===")
    
    try:
        # 1. 임베더 초기화 (최초 실행 시 모델 다운로드 진행됨)
        embedder_wrapper = LocalEmbedder(model_name="BAAI/bge-m3")
        model = embedder_wrapper.get_model()
        
        # 2. 테스트용 문장 준비
        sample_texts = [
            "RAG 시스템 구축 프로젝트입니다.",
            "Elasticsearch 8.16 버전을 사용하여 벡터 검색을 구현합니다.",
            "사내망 환경에서는 로컬 임베딩 모델이 필수적입니다."
        ]
        
        # 3. 단일 쿼리 테스트 (Query Embedding)
        logger.info("테스트 1: 단일 쿼리 임베딩 중...")
        query_vector = model.embed_query(sample_texts[0])
        
        logger.info(f"✅ 쿼리 벡터 생성 성공 (차원: {len(query_vector)})")
        # BGE-M3의 표준 차원은 1024입니다.
        assert len(query_vector) == 1024, f"차원 불일치: {len(query_vector)} != 1024"

        # 4. 다중 문서 테스트 (Document Embedding)
        logger.info("테스트 2: 다중 문서 배치 임베딩 중...")
        doc_vectors = model.embed_documents(sample_texts)
        
        logger.info(f"✅ 문서 배치 벡터 생성 성공 (개수: {len(doc_vectors)})")
        assert len(doc_vectors) == len(sample_texts)

        # 5. 하드웨어 가속 확인
        device = "GPU (CUDA/MPS)" if torch.cuda.is_available() or torch.backends.mps.is_available() else "CPU"
        print(f"\n🚀 [테스트 결과 Summary]")
        print(f"- 사용 모델: BAAI/bge-m3")
        print(f"- 구동 장치: {device}")
        print(f"- 벡터 차원: {len(query_vector)}")
        print(f"- 샘플 벡터(앞 5개): {query_vector[:5]}")
        print("\n✨ 모든 임베딩 테스트를 통과했습니다!")

    except Exception as e:
        logger.error(f"❌ 임베더 테스트 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    test_local_embedder()