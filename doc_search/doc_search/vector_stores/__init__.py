from .base import BaseVectorStore
from .elasticsearch_store import ElasticsearchVectorStore
from .mock_vector_store import MockVectorStore

def get_vector_store(provider_name: str) -> BaseVectorStore:
    provider_name = provider_name.lower()
    if provider_name == "elasticsearch":
        return ElasticsearchVectorStore()
    elif provider_name == "mock":
        return MockVectorStore()
    # Add other vector store providers here in the future
    # elif provider_name == "faiss":
    #     return FaissVectorStore()
    else:
        raise ValueError(f"Unsupported vector store provider: {provider_name}")
