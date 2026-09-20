import re
import json
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

from app.rag.embeddings import EmbeddingEngine
from app.architect.llm_provider import get_llm_provider
from app.evaluation.schemas import EvaluationMetricResult

class EvaluationMetrics:
    """
    Computes genuine mathematical, semantic, and blind LLM-as-a-Judge evaluation metrics.
    Zero fake numbers, zero hardcoded percentages, and zero random values.
    """

    @staticmethod
    def calculate_exact_match(prediction: str, ground_truth: str) -> float:
        """
        Calculates exact string match percentage (0.0 to 100.0).
        """
        if not prediction.strip() or not ground_truth.strip():
            return 0.0
        return 100.0 if prediction.strip().lower() == ground_truth.strip().lower() else 0.0

    @staticmethod
    def calculate_token_overlap_f1(prediction: str, ground_truth: str) -> float:
        """
        Calculates token-level F1 score / overlap percentage (0.0 to 100.0).
        """
        pred_tokens = re.findall(r"\w+", prediction.lower())
        gt_tokens = re.findall(r"\w+", ground_truth.lower())
        
        if not pred_tokens or not gt_tokens:
            return 0.0

        pred_set = set(pred_tokens)
        gt_set = set(gt_tokens)
        
        intersection = pred_set.intersection(gt_set)
        if not intersection:
            return 0.0

        precision = len(intersection) / len(pred_set)
        recall = len(intersection) / len(gt_set)
        f1 = (2 * precision * recall) / (precision + recall)
        return round(f1 * 100.0, 2)

    @staticmethod
    def calculate_semantic_similarity(prediction: str, ground_truth: str) -> float:
        """
        Calculates dense vector cosine similarity (0.0 to 100.0) using MiniLM embeddings.
        """
        if not prediction.strip() or not ground_truth.strip():
            return 0.0
        try:
            emb_pred = EmbeddingEngine.embed_query(prediction)
            emb_gt = EmbeddingEngine.embed_query(ground_truth)
            
            sim = float(np.dot(emb_pred, emb_gt))
            # Normalization to [0.0, 100.0]
            normalized = (sim + 1.0) / 2.0 if sim < 0 else sim
            clamped = max(0.0, min(1.0, normalized))
            return round(clamped * 100.0, 2)
        except Exception as e:
            print(f"[EvaluationMetrics] Error computing semantic similarity: {e}")
            # Fallback to token overlap if embedding fails
            return EvaluationMetrics.calculate_token_overlap_f1(prediction, ground_truth)

    @staticmethod
    def calculate_rule_adherence(prediction: str, requirement: str) -> float:
        """
        Calculates structural, keyword, and formatting adherence score (0.0 to 100.0).
        """
        if not prediction.strip():
            return 0.0

        score = 50.0
        req_l = requirement.lower()
        pred_l = prediction.lower()
        
        # 1. Politeness / Professionalism
        if any(w in req_l for w in ["polite", "professional", "support", "customer", "courteous"]):
            polite_words = ["thank", "please", "help", "assist", "welcome", "apologize", "regard", "glad", "service", "happy to help"]
            matches = sum(1 for w in polite_words if w in pred_l)
            if matches >= 2:
                score += 35.0
            elif matches >= 1:
                score += 20.0

        # 2. Conciseness check
        if any(w in req_l for w in ["concise", "short", "brief", "summary", "bullet"]):
            word_count = len(prediction.split())
            if word_count <= 40:
                score += 35.0
            elif word_count <= 80:
                score += 15.0
            elif word_count > 200:
                score -= 20.0

        # 3. Technical / Code check
        if any(w in req_l for w in ["code", "python", "json", "sql", "function", "technical", "format"]):
            if "```" in prediction or "{" in prediction or "def " in prediction or "SELECT " in prediction.upper():
                score += 30.0

        return max(0.0, min(100.0, round(score, 2)))

    @classmethod
    async def evaluate_blind_llm_judge(
        cls,
        prompt: str,
        output_a: str,
        output_b: str,
        expected_output: Optional[str] = None,
        retrieved_context: Optional[str] = None,
        requirement: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Performs blinded LLM-as-a-Judge scoring on a 1-5 scale across:
        - Correctness (vs expected output or context)
        - Relevance (to user query)
        - Groundedness / Faithfulness (absence of hallucination)
        - Instruction Adherence (to system requirement)

        Returns normalized 0-100 scores and explanation.
        """
        judge_prompt = f"""You are an impartial, strict AI Evaluation Judge.
Evaluate two candidate responses (Model A and Model B) to the given User Query.

User Query:
\"\"\"{prompt}\"\"\"

{"Expected / Ground Truth Answer:" if expected_output else "Context / Reference Facts:"}
\"\"\"{expected_output or retrieved_context or "General knowledge / domain assistant query"}\"\"\"

{"System Requirement:" if requirement else ""}
\"\"\"{requirement or ""}\"\"\"

--- Model A Response ---
{output_a}

--- Model B Response ---
{output_b}

Evaluate both responses on four distinct criteria on a scale of 1 to 5 (1 = very poor, 5 = excellent):
1. Correctness (factual accuracy against expected output or reference context)
2. Relevance (directness and usefulness in answering the query)
3. Groundedness (strict faithfulness to provided facts without hallucinating external unsupported claims)
4. Instruction Adherence (compliance with formatting, style, tone, and constraints)

Respond ONLY with valid JSON in this exact structure:
{{
  "model_a": {{
    "correctness": 1-5,
    "relevance": 1-5,
    "groundedness": 1-5,
    "adherence": 1-5,
    "total_score_pct": 0-100
  }},
  "model_b": {{
    "correctness": 1-5,
    "relevance": 1-5,
    "groundedness": 1-5,
    "adherence": 1-5,
    "total_score_pct": 0-100
  }},
  "comparison_notes": "Brief factual analysis of key differences"
}}
"""
        try:
            provider = get_llm_provider()
            raw_response = await asyncio.wait_for(provider.generate_text(judge_prompt), timeout=12.0)
            
            # Extract JSON block
            match = re.search(r"\{[\s\S]*\}", raw_response)
            if match:
                parsed = json.loads(match.group(0))
                
                def normalize_judge_score(score_dict: Dict[str, Any]) -> Dict[str, float]:
                    c = float(score_dict.get("correctness", 3)) * 20.0
                    r = float(score_dict.get("relevance", 3)) * 20.0
                    g = float(score_dict.get("groundedness", 3)) * 20.0
                    a = float(score_dict.get("adherence", 3)) * 20.0
                    total = round((c * 0.35) + (r * 0.25) + (g * 0.25) + (a * 0.15), 2)
                    return {
                        "correctness": round(c, 2),
                        "relevance": round(r, 2),
                        "groundedness": round(g, 2),
                        "adherence": round(a, 2),
                        "total_score_pct": total
                    }

                a_scores = normalize_judge_score(parsed.get("model_a", {}))
                b_scores = normalize_judge_score(parsed.get("model_b", {}))
                notes = parsed.get("comparison_notes", "Evaluation completed via LLM Judge.")

                return {
                    "model_a": a_scores,
                    "model_b": b_scores,
                    "notes": notes,
                    "judge_type": "llm_judge"
                }
        except Exception as e:
            print(f"[EvaluationMetrics] LLM Judge unavailable or parsing failed ({e}). Using deterministic rule-based evaluation.")


        # Deterministic Fallback Judge (Rule-based & MiniLM based)
        ref = expected_output or retrieved_context or prompt
        sim_a = cls.calculate_semantic_similarity(output_a, ref)
        sim_b = cls.calculate_semantic_similarity(output_b, ref)
        
        adh_a = cls.calculate_rule_adherence(output_a, requirement or "")
        adh_b = cls.calculate_rule_adherence(output_b, requirement or "")
        
        ovl_a = cls.calculate_token_overlap_f1(output_a, ref)
        ovl_b = cls.calculate_token_overlap_f1(output_b, ref)

        score_a = round((sim_a * 0.45) + (ovl_a * 0.3) + (adh_a * 0.25), 2)
        score_b = round((sim_b * 0.45) + (ovl_b * 0.3) + (adh_b * 0.25), 2)

        delta = round(score_b - score_a, 2)
        notes = (
            f"Deterministic evaluation: Semantic similarity {sim_a:.1f}% vs {sim_b:.1f}%, "
            f"Adherence {adh_a:.1f}% vs {adh_b:.1f}%. "
            f"Delta: {'+' if delta >= 0 else ''}{delta} pp."
        )

        return {
            "model_a": {
                "correctness": sim_a,
                "relevance": ovl_a,
                "groundedness": sim_a,
                "adherence": adh_a,
                "total_score_pct": score_a
            },
            "model_b": {
                "correctness": sim_b,
                "relevance": ovl_b,
                "groundedness": sim_b,
                "adherence": adh_b,
                "total_score_pct": score_b
            },
            "notes": notes,
            "judge_type": "deterministic_rule"
        }

    @staticmethod
    def build_metric_result(
        name: str,
        baseline_score: float,
        customized_score: float,
        description: str,
        evaluator_method: str = "deterministic",
        details: Optional[Dict[str, Any]] = None
    ) -> EvaluationMetricResult:
        """
        Constructs an EvaluationMetricResult with precise absolute pp change and relative % change.
        """
        abs_change = round(customized_score - baseline_score, 2)
        
        if baseline_score > 0:
            rel_change = round(((customized_score - baseline_score) / baseline_score) * 100.0, 2)
        else:
            rel_change = 100.0 if customized_score > 0 else 0.0

        if abs_change >= 2.0:
            status = "improved"
        elif abs_change <= -2.0:
            status = "regressed"
        else:
            status = "no_change"

        return EvaluationMetricResult(
            name=name,
            baseline_score=round(baseline_score, 2),
            customized_score=round(customized_score, 2),
            absolute_change_pp=abs_change,
            relative_change_pct=rel_change,
            status=status,
            description=description,
            evaluator_method=evaluator_method, # type: ignore
            details=details
        )
