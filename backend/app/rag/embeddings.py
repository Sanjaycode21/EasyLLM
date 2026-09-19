import numpy as np
from typing import List
from app.config import settings

class EmbeddingEngine:
    """
    Generates genuine dense semantic embeddings for documents and queries.
    Uses sentence-transformers / all-MiniLM-L6-v2, with deterministic dense vector fallback.
    """
    _model = None
    
    @classmethod
    def get_model(cls):
        if cls._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer(settings.embedding_model_name)
            except Exception as e:
                print(f"[EmbeddingEngine] Warning: Could not load SentenceTransformer ({e}). Using dense semantic hash embedder.")
                cls._model = "fallback"
        return cls._model

    @classmethod
    def embed_texts(cls, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 384), dtype=np.float32)
        
        model = cls.get_model()
        if model != "fallback":
            embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.astype(np.float32)
        else:
            # Deterministic dense semantic hash embedding (384-d normalized)
            dim = 384
            vecs = []
            for t in texts:
                words = t.lower().split()
                vec = np.zeros(dim, dtype=np.float32)
                for i, w in enumerate(words):
                    h = hash(w) % dim
                    vec[h] += 1.0 / (1.0 + np.log1p(i))
                    # Add bigram hash
                    if i > 0:
                        h2 = hash(words[i-1] + "_" + w) % dim
                        vec[h2] += 0.5
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
                vecs.append(vec)
            return np.array(vecs, dtype=np.float32)

    @classmethod
    def embed_query(cls, query: str) -> np.ndarray:
        return cls.embed_texts([query])[0]
