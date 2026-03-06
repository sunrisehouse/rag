from .base import BaseLLM
from .gemini import GeminiLLM
from .mock_llm import MockLLM

def get_llm_provider(provider_name: str) -> BaseLLM:
    provider_name = provider_name.lower()
    if provider_name == "gemini":
        return GeminiLLM()
    elif provider_name == "mock":
        return MockLLM()
    # Add other providers here in the future
    # elif provider_name.lower() == "openai":
    #     return OpenAILLM()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
