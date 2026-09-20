import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
import asyncio
from app.evaluation.schemas import EvaluationDataset, EvaluationExample
from app.evaluation.splitter import EvaluationDatasetSplitter
from app.evaluation.metrics import EvaluationMetrics
from app.evaluation.engine import EvaluationEngine
from app.evaluation.manager import EvaluationJobManager


def test_dataset_splitter_deterministic_and_zero_leakage():
    records = [
        {"messages": [{"role": "user", "content": f"Query {i}"}, {"role": "assistant", "content": f"Answer {i}"}]}
        for i in range(10)
    ]
    
    # Split with seed 42
    train_a, eval_ds_a = EvaluationDatasetSplitter.split_records(records, dataset_name="test_ds", eval_ratio=0.2, seed=42)
    # Split again with same seed
    train_b, eval_ds_b = EvaluationDatasetSplitter.split_records(records, dataset_name="test_ds", eval_ratio=0.2, seed=42)

    assert len(train_a) == 8
    assert len(eval_ds_a.examples) == 2
    assert eval_ds_a.total_examples == 10
    assert eval_ds_a.is_held_out is True
    
    # Check deterministic reproducibility
    assert [e.prompt for e in eval_ds_a.examples] == [e.prompt for e in eval_ds_b.examples]

    # Verify zero data leakage (eval prompts do not appear in train set)
    train_prompts = set()
    for item in train_a:
        for m in item["messages"]:
            if m["role"] == "user":
                train_prompts.add(m["content"])

    eval_prompts = set(e.prompt for e in eval_ds_a.examples)
    assert train_prompts.isdisjoint(eval_prompts), "Data leakage detected between train and eval splits!"

def test_document_chunk_eval_splitter():
    chunks = [
        {"chunk_id": i, "text": f"Knowledge paragraph {i}. Facts and figures for section {i}.", "metadata": {"chunk_index": i}}
        for i in range(10)
    ]
    eval_ds = EvaluationDatasetSplitter.create_document_eval_set(chunks, doc_name="manual.pdf", eval_ratio=0.2, seed=42)
    
    assert len(eval_ds.examples) == 2
    assert eval_ds.dataset_name == "manual.pdf"
    assert "Knowledge paragraph" in eval_ds.examples[0].retrieved_context

def test_evaluation_metrics_deterministic():
    # Exact Match
    assert EvaluationMetrics.calculate_exact_match("hello world", "Hello World") == 100.0
    assert EvaluationMetrics.calculate_exact_match("hello world", "hello there") == 0.0

    # Token Overlap F1
    f1_exact = EvaluationMetrics.calculate_token_overlap_f1("the quick brown fox", "the quick brown fox")
    assert f1_exact == 100.0
    
    f1_partial = EvaluationMetrics.calculate_token_overlap_f1("the quick fox", "the quick brown fox")
    assert 50.0 < f1_partial < 100.0

    # Semantic similarity
    sim_high = EvaluationMetrics.calculate_semantic_similarity(
        "You can return any purchased item within 30 days.",
        "Items may be returned for a refund within 30 calendar days."
    )
    sim_low = EvaluationMetrics.calculate_semantic_similarity(
        "The celestial mechanics of orbital satellites.",
        "A chocolate cake recipe with buttercream frosting."
    )
    assert sim_high > 70.0
    assert sim_low < sim_high

def test_metric_result_building_and_deltas():
    # Improvement case
    improved = EvaluationMetrics.build_metric_result(
        name="Semantic Similarity",
        baseline_score=60.0,
        customized_score=85.0,
        description="Test metric"
    )
    assert improved.absolute_change_pp == 25.0
    assert improved.relative_change_pct == 41.67
    assert improved.status == "improved"

    # Regression case
    regressed = EvaluationMetrics.build_metric_result(
        name="Groundedness",
        baseline_score=80.0,
        customized_score=65.0,
        description="Test metric"
    )
    assert regressed.absolute_change_pp == -15.0
    assert regressed.relative_change_pct == -18.75
    assert regressed.status == "regressed"

async def test_evaluation_engine_e2e_and_regression_detection(tmp_path):

    eval_ds = EvaluationDataset(
        dataset_id="test-ds-1",
        dataset_name="support_eval",
        total_examples=2,
        train_examples_count=8,
        eval_examples_count=2,
        examples=[
            EvaluationExample(
                id="ex-1",
                prompt="How do I get a refund?",
                expected_output="Refunds are processed within 30 days of return receipt."
            ),
            EvaluationExample(
                id="ex-2",
                prompt="What are standard support hours?",
                expected_output="Customer support operates Monday to Friday 9 AM to 5 PM EST."
            )
        ]
    )

    pipeline_info = {
        "id": "test-pipeline-1",
        "architecture": "rag",
        "base_model": "Qwen/Qwen3-4B-Instruct-2507",
        "training_config": {"requirement": "Provide polite, concise answers."}
    }

    report = await EvaluationEngine.evaluate_pipeline(pipeline_info, eval_ds)

    assert report.num_examples == 2
    assert len(report.metrics) >= 4
    assert len(report.sample_comparisons) == 2
    assert report.system_performance.baseline_latency_ms >= 0.0
    assert report.overall_status in ["IMPROVED", "REGRESSED", "NO_SIGNIFICANT_CHANGE"]

    # Persistence verification
    manager = EvaluationJobManager(storage_dir=tmp_path)
    manager._save_report(report)
    loaded = manager.get_report(report.evaluation_id)
    assert loaded is not None
    assert loaded.evaluation_id == report.evaluation_id
    assert loaded.num_examples == 2

if __name__ == "__main__":
    test_dataset_splitter_deterministic_and_zero_leakage()
    test_document_chunk_eval_splitter()
    test_evaluation_metrics_deterministic()
    test_metric_result_building_and_deltas()
    asyncio.run(test_evaluation_engine_e2e_and_regression_detection(Path("./scratch_eval")))
    print("[SUCCESS] All Evaluation Engine test cases passed!")
