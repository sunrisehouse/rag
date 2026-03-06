import typer
from typing_extensions import Annotated
from .rag import RAGSystem
from .logger import log
import warnings

# Suppress specific warnings from sentence_transformers if they are noisy
warnings.filterwarnings("ignore", category=FutureWarning, module="sentence_transformers")

def main(question: Annotated[str, typer.Argument(help="The question to ask the RAG system.")]):
    """
    Query the RAG system to get an answer based on documents in Elasticsearch.
    """
    try:
        log.info("Initializing RAG system...")
        rag_system = RAGSystem()
        log.info("Initialization complete.")
        
        log.info(f"Querying with question: {question}")
        answer, sources = rag_system.query(question)
        
        # Use print for final user output, but logging for process steps
        print("\n--- Answer ---")
        print(answer)
        print("\n--- Sources ---")
        for i, doc in enumerate(sources, 1):
            print(f"[{i}] {doc['url']}")
            
    except Exception as e:
        log.error(f"An error occurred: {e}", exc_info=True)

def run():
    typer.run(main)

if __name__ == "__main__":
    run()
