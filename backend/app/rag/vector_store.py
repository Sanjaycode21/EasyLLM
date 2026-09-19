import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from app.rag.embeddings import EmbeddingEngine
from app.config import settings

class VectorStore:
    """
    Vector storage and retrieval index for RAG.
    Maintains normalized embeddings, document metadata, and fast cosine similarity search.
    """
    def __init__(self, index_id: str):
        self.index_id = index_id
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray = np.zeros((0, 384), dtype=np.float32)
        self.save_dir = settings.vector_db_dir / index_id
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def add_documents(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return
        
        texts = [c["text"] for c in chunks]
        new_embeddings = EmbeddingEngine.embed_texts(texts)
        
        if len(self.chunks) == 0:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
            
        self.chunks.extend(chunks)
        self.save()

    def search(self, query: str, top_k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        if len(self.chunks) == 0 or len(self.embeddings) == 0:
            return []
        
        query_vec = EmbeddingEngine.embed_query(query)
        # Cosine similarity for normalized embeddings is dot product
        scores = np.dot(self.embeddings, query_vec)
        
        # Rank indices by score descending
        ranked_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in ranked_indices:
            score = float(scores[idx])
            results.append((self.chunks[idx], score))
            
        return results

    def save(self):
        index_file = self.save_dir / "index.pkl"
        meta_file = self.save_dir / "metadata.json"
        
        with open(index_file, "wb") as f:
            pickle.dump({"embeddings": self.embeddings, "chunks": self.chunks}, f)
            
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump({
                "index_id": self.index_id,
                "num_chunks": len(self.chunks),
                "embedding_dim": int(self.embeddings.shape[1]) if len(self.embeddings) > 0 else 0
            }, f, indent=2)

    @classmethod
    def load(cls, index_id: str) -> "VectorStore":
        store = cls(index_id)
        index_file = store.save_dir / "index.pkl"
        if index_file.exists():
            with open(index_file, "rb") as f:
                data = pickle.load(f)
                store.embeddings = data.get("embeddings", np.zeros((0, 384), dtype=np.float32))
                store.chunks = data.get("chunks", [])
        return store
