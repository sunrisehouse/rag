from .base import BaseEmbedder
from .sentence_transformer import SentenceTransformerEmbedder

def get_embedder(provider_name: str) -> BaseEmbedder:
    provider_name = provider_name.lower()
    if provider_name == "sentence_transformer":
        return SentenceTransformerEmbedder()
    # Add other embedder providers here in the future
    # elif provider_name == "openai_ada":
    #     return OpenAIEmbedder()
    else:
        raise ValueError(f"Unsupported embedder provider: {provider_name}")
