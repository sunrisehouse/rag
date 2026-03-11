import os
from sentence_transformers import SentenceTransformer

def download():
    model_name = "BAAI/bge-m3"
    save_path = "./models/BAAI_bge-m3"
    
    print(f"🚀 모델 다운로드 시작: {model_name}")
    model = SentenceTransformer(model_name)
    model.save(save_path)
    print(f"✅ 다운로드 완료! 경로: {os.path.abspath(save_path)}")

if __name__ == "__main__":
    download()