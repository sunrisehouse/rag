import sqlite3
import numpy as np
import json
from typing import List, Dict

from .base import BaseVectorStore
from ..logger import log
from ..config import DB_PATH

class SQLiteVectorStore(BaseVectorStore):
    def __init__(self):
        self.db_path = DB_PATH
        self._create_table_if_not_exists()
        log.info(f"SQLiteVectorStore initialized, connected to {self.db_path}")

    def _get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # This allows access to columns by name
        return conn

    def _create_table_if_not_exists(self):
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                embedding BLOB NOT NULL,
                url TEXT NOT NULL,
                UNIQUE(doc_id, chunk_index)
            )
        """)
        conn.commit()
        conn.close()
        log.info("Vector store table 'vectors' is ready in SQLite database.")

    def get_relevant_documents(self, query_embedding: List[float], k: int = 4) -> List[Dict]:
        query_embedding_np = np.array(query_embedding).astype(np.float32)
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        # Fetch all embeddings and texts. This is not efficient for large databases.
        # For production, consider Faiss or a proper vector database.
        cursor.execute("SELECT id, text, embedding, url FROM vectors")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        documents = []
        for row in rows:
            db_embedding_bytes = row["embedding"]
            db_embedding = np.frombuffer(db_embedding_bytes, dtype=np.float32)
            
            # Calculate cosine similarity
            # Normalize embeddings to calculate cosine similarity efficiently
            norm_query = np.linalg.norm(query_embedding_np)
            norm_db = np.linalg.norm(db_embedding)

            if norm_query == 0 or norm_db == 0:
                similarity = 0.0
            else:
                similarity = np.dot(query_embedding_np, db_embedding) / (norm_query * norm_db)
            
            documents.append({
                "id": row["id"],
                "text": row["text"],
                "url": row["url"],
                "similarity": float(similarity)  # Ensure similarity is a float
            })
        
        # Sort by similarity in descending order and return top k
        documents.sort(key=lambda x: x["similarity"], reverse=True)
        return documents[:k]

    def add_documents(self, documents: List[Dict]):
        """Adds documents to the vector store. (Not used by doc_search, but for completeness)"""
        log.warning("add_documents method is not implemented for SQLiteVectorStore in doc_search CLI.")
        pass

    def clear_documents(self):
        """Clears all documents from the vector store. (Not used by doc_search, but for completeness)"""
        log.warning("clear_documents method is not implemented for SQLiteVectorStore in doc_search CLI.")
        pass
