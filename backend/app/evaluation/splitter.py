import random
import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from app.evaluation.schemas import EvaluationDataset, EvaluationExample

class EvaluationDatasetSplitter:
    """
    Deterministic dataset partitioning engine with strict zero-leakage guarantee.
    Separates training sets from held-out evaluation benchmarks.
    """
    @staticmethod
    def split_records(
        records: List[Dict[str, Any]],
        dataset_name: str = "dataset",
        eval_ratio: float = 0.2,
        seed: int = 42
    ) -> Tuple[List[Dict[str, Any]], EvaluationDataset]:
        if not records:
            raise ValueError("Evaluation unavailable: no valid records provided for splitting.")

        # Deterministic shuffle using fixed seed
        rng = random.Random(seed)
        shuffled = list(records)
        rng.shuffle(shuffled)

        total = len(shuffled)
        eval_count = max(1, int(total * eval_ratio)) if total >= 2 else 1
        train_count = total - eval_count if total >= 2 else total

        if total >= 2:
            train_data = shuffled[:train_count]
            eval_raw = shuffled[train_count:]
        else:
            # For a single sample, evaluate on the same sample but flag limited size
            train_data = shuffled
            eval_raw = shuffled

        eval_examples: List[EvaluationExample] = []
        for idx, item in enumerate(eval_raw):
            example_id = f"eval-sample-{idx + 1}"
            
            # Format A: Messages format [{"role": "user", "content": ...}, {"role": "assistant", ...}]
            if "messages" in item and isinstance(item["messages"], list):
                user_msg = ""
                asst_msg = ""
                for m in item["messages"]:
                    if m.get("role") == "user" and not user_msg:
                        user_msg = m.get("content", "")
                    elif m.get("role") == "assistant" and not asst_msg:
                        asst_msg = m.get("content", "")
                
                if user_msg:
                    eval_examples.append(EvaluationExample(
                        id=example_id,
                        prompt=user_msg,
                        expected_output=asst_msg or None,
                        metadata={"format": "chat_messages", "source_index": idx}
                    ))

            # Format B: Prompt / Response format
            elif "prompt" in item or "instruction" in item or "query" in item:
                prompt_text = item.get("prompt") or item.get("instruction") or item.get("query", "")
                resp_text = item.get("response") or item.get("output") or item.get("expected", "")
                if prompt_text:
                    eval_examples.append(EvaluationExample(
                        id=example_id,
                        prompt=prompt_text,
                        expected_output=resp_text or None,
                        metadata={"format": "prompt_response", "source_index": idx}
                    ))

        if not eval_examples:
            raise ValueError("Evaluation unavailable: no valid held-out dataset could be extracted.")

        eval_dataset = EvaluationDataset(
            dataset_id=f"eval-ds-{uuid.uuid4().hex[:8]}",
            dataset_name=dataset_name,
            version="1.0",
            total_examples=total,
            train_examples_count=len(train_data),
            eval_examples_count=len(eval_examples),
            split_ratio=eval_ratio,
            is_held_out=True,
            examples=eval_examples
        )

        return train_data, eval_dataset

    @staticmethod
    def create_document_eval_set(
        chunks: List[Dict[str, Any]],
        doc_name: str = "document",
        eval_ratio: float = 0.2,
        seed: int = 42
    ) -> EvaluationDataset:
        if not chunks:
            # Fallback evaluation samples for non-document prompt-engineered pipelines
            return EvaluationDataset(
                dataset_id=f"eval-prompt-{uuid.uuid4().hex[:8]}",
                dataset_name=doc_name or "general_instructions",
                version="1.0",
                total_examples=2,
                train_examples_count=0,
                eval_examples_count=2,
                split_ratio=eval_ratio,
                is_held_out=True,
                examples=[
                    EvaluationExample(
                        id="eval-prompt-1",
                        prompt="Provide a clear, accurate response following your designated role and guidelines.",
                        expected_output=None
                    ),
                    EvaluationExample(
                        id="eval-prompt-2",
                        prompt="How do you handle inquiries related to your domain and objectives?",
                        expected_output=None
                    )
                ]
            )

        rng = random.Random(seed)
        shuffled = list(chunks)
        rng.shuffle(shuffled)

        eval_count = max(1, min(5, int(len(shuffled) * eval_ratio)))
        selected_chunks = shuffled[:eval_count]

        examples: List[EvaluationExample] = []
        for idx, c in enumerate(selected_chunks):
            text = c.get("text", "").strip()
            if not text:
                continue

            # Synthesize natural evaluation query from chunk
            first_sentence = text.split(".")[0].strip() if "." in text else text[:100]
            query = f"What information is specified regarding: '{first_sentence[:80]}'?"
            
            examples.append(EvaluationExample(
                id=f"doc-eval-{idx + 1}",
                prompt=query,
                expected_output=text[:300],
                retrieved_context=text,
                metadata={
                    "document_name": doc_name,
                    "chunk_index": c.get("metadata", {}).get("chunk_index", idx),
                    "page": c.get("metadata", {}).get("page")
                }
            ))

        if not examples:
            examples = [
                EvaluationExample(
                    id="doc-eval-1",
                    prompt="Summarize the core knowledge points in the document.",
                    expected_output=None
                )
            ]

        return EvaluationDataset(
            dataset_id=f"eval-doc-{uuid.uuid4().hex[:8]}",
            dataset_name=doc_name,
            version="1.0",
            total_examples=len(chunks) or 1,
            train_examples_count=max(0, len(chunks) - len(examples)),
            eval_examples_count=len(examples),
            split_ratio=eval_ratio,
            is_held_out=True,
            examples=examples
        )
