from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generates a response from the LLM based on the prompt."""
        pass
