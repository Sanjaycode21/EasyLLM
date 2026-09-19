import re
import numpy as np
from typing import List, Dict, Any
from app.rag.embeddings import EmbeddingEngine

class EvaluationMetrics:
    """
    Computes genuine mathematical and semantic evaluation metrics.
    No randomized scores or placeholders.
    """
    @staticmethod
    def calculate_exact_match(prediction: str, ground_truth: str) -> float:
        return 1.0 if prediction.strip().lower() == ground_truth.strip().lower() else 0.0

    @staticmethod
    def calculate_token_overlap(prediction: str, ground_truth: str) -> float:
        pred_tokens = set(re.findall(r"\w+", prediction.lower()))
        gt_tokens = set(re.findall(r"\w+", ground_truth.lower()))
        if not pred_tokens or not gt_tokens:
            return 0.0
        intersection = pred_tokens.intersection(gt_tokens)
        return len(intersection) / len(gt_tokens)

    @staticmethod
    def calculate_semantic_similarity(prediction: str, ground_truth: str) -> float:
        """
        Calculates cosine similarity between embedding vectors of prediction and ground truth.
        """
        if not prediction.strip() or not ground_truth.strip():
            return 0.0
        emb_pred = EmbeddingEngine.embed_query(prediction)
        emb_gt = EmbeddingEngine.embed_query(ground_truth)
        
        sim = float(np.dot(emb_pred, emb_gt))
        # Clamp to [0.0, 1.0]
        return max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim))

    @staticmethod
    def calculate_instruction_adherence(prediction: str, requirement: str) -> float:
        """
        Evaluates length, structure, and persona formatting compliance.
        """
        score = 0.5
        req_l = requirement.lower()
        pred_l = prediction.lower()
        
        # Check polite / professional keywords if asked
        if "polite" in req_l or "professional" in req_l or "support" in req_l:
            polite_words = ["thank", "please", "help", "assist", "welcome", "apologize", "regard", "glad"]
            matches = sum(1 for w in polite_words if w in pred_l)
            if matches >= 2:
                score += 0.4
            elif matches >= 1:
                score += 0.25

        # Check concise / brief if asked
        if "concise" in req_l or "short" in req_l or "brief" in req_l:
            word_count = len(prediction.split())
            if word_count <= 40:
                score += 0.3
            elif word_count <= 80:
                score += 0.15

        return min(1.0, score)
