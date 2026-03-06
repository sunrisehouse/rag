from . import config
from .llms import get_llm_provider
from .vector_stores import get_vector_store
from .embedders import get_embedder
from .logger import log

class RAGSystem:
    def __init__(self):
        try:
            log.info(f"Initializing embedder with provider: {config.EMBEDDING_PROVIDER}")
            self.embedding_model = get_embedder(config.EMBEDDING_PROVIDER)
        except (ValueError, RuntimeError) as e:
            log.error(f"Error initializing embedder: {e}")
            raise

        try:
            log.info(f"Initializing vector store with provider: {config.VECTOR_STORE_PROVIDER}")
            self.vector_store = get_vector_store(config.VECTOR_STORE_PROVIDER)
        except (ValueError, RuntimeError) as e:
            log.error(f"Error initializing vector store: {e}")
            raise
        
        try:
            log.info(f"Initializing LLM with provider: {config.LLM_PROVIDER}")
            self.llm = get_llm_provider(config.LLM_PROVIDER)
        except ValueError as e:
            log.warning(f"{e}. LLM functionality will be disabled.")
            self.llm = None

    def query(self, question: str):
        # 1. Embed the user's query
        log.info("Encoding question...")
        query_vector = self.embedding_model.encode(question)

        # 2. Search the vector store
        log.info("Searching vector store...")
        hits = self.vector_store.search(
            query_vector=query_vector,
            k=3,
            num_candidates=10
        )
        
        if not hits:
            log.warning("No relevant documents found.")
            return "I couldn't find any relevant documents to answer your question.", []

        # 3. Build context and sources
        log.info(f"Found {len(hits)} relevant documents.")
        context = ""
        sources = []
        for hit in hits:
            source_text = hit['_source'].get('text', '')
            source_url = hit['_source'].get('url', '')
            context += f"Document URL: {source_url}\nContent: {source_text}\n\n"
            sources.append({'text': source_text, 'url': source_url})

        # 4. Generate response from LLM
        if not self.llm:
            log.warning("LLM is not configured. Returning retrieved documents without generating an answer.")
            return "LLM is not configured. Here are the retrieved documents.", sources
            
        prompt = f"""**Role:** You are an expert technical assistant specializing in providing clear and accurate answers to developer questions based on a given set of documents.

**Instructions:**
1.  Analyze the provided `CONTEXT` from technical documents to answer the user's `QUESTION`.
2.  Base your answer **exclusively** on the information found in the `CONTEXT`. Do not use any external knowledge.
3.  If the `CONTEXT` does not contain enough information to answer the `QUESTION`, state that you cannot find the answer in the provided documents.
4.  Format your answer using Markdown for clarity. Use code blocks (```) for code snippets, and lists or bolding where appropriate.
5.  For each piece of information you provide, you **must** cite the source URL it came from. Place the citation like this: `[Source: <URL>]`.

**CONTEXT:**
---
{context}
---

**QUESTION:**
{question}

**Answer:**
"""
        
        log.info("Generating response from LLM...")
        answer = self.llm.generate_response(prompt)
        log.info("LLM response received.")
        
        return answer, sources
