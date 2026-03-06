from .base import BaseLLM

class MockLLM(BaseLLM):
    """A mock LLM client for testing without a real LLM service."""

    def generate_response(self, prompt: str) -> str:
        """
        Simulates generating a response from an LLM and returns a predefined answer.
        """
        print(f"MockLLM: Generating response for prompt: {prompt[:50]}...")
        return "This is a mock response from the LLM, indicating that the RAG system successfully retrieved documents and prepared a prompt. (Source: http://fake-docs.com/mock-llm)"
