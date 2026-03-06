from .sentence_transformer import SentenceTransformerModel
from .. import config

def get_embedding_model():
    """설정에 지정된 임베딩 모델 인스턴스를 반환합니다."""
    # 현재는 SentenceTransformer만 지원하지만, 향후 모델이 추가되면
    # config.EMBEDDING_MODEL_TYPE 같은 변수를 두어 분기할 수 있습니다.
    
    model_name = config.EMBEDDING_MODEL
    if not model_name:
        raise ValueError("EMBEDDING_MODEL is not set in the configuration.")
        
    return SentenceTransformerModel(model_name=model_name)
