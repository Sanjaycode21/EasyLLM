import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.api.schemas import ModelEvaluation, EvaluationMetric, EvaluationSample
from app.evaluation.schemas import EvaluationDataset, EvaluationExample, EvaluationReport
from app.evaluation.splitter import EvaluationDatasetSplitter
from app.evaluation.engine import EvaluationEngine
from app.evaluation.manager import evaluation_manager

class SystemEvaluator:
    """
    Executes genuine comparative evaluation between Base Model and Customized Model.
    Calculates semantic similarity, token overlap, and instruction adherence.
    Integrates with the unified EvaluationEngine.
    """
    @staticmethod
    async def evaluate_model(
        model_id: str,
        val_records: List[Dict[str, Any]],
        requirement: str,
        adapter_path: Optional[str] = None,
        architecture: str = "rag",
        base_model_id: str = "Qwen/Qwen3-4B-Instruct-2507"
    ) -> ModelEvaluation:
        # Build evaluation dataset from validation records
        if val_records:
            try:
                _, eval_dataset = EvaluationDatasetSplitter.split_records(val_records, dataset_name="validation_split")
            except Exception:
                # Fallback if split fails on non-standard format
                examples = []
                for idx, r in enumerate(val_records[:5]):
                    msgs = r.get("messages", [])
                    u_msg = ""
                    a_msg = ""
                    for m in msgs:
                        if m.get("role") == "user" and not u_msg:
                            u_msg = m.get("content", "")
                        elif m.get("role") == "assistant":
                            a_msg = m.get("content", "")
                    if u_msg:
                        examples.append(EvaluationExample(
                            id=f"sample-{idx+1}",
                            prompt=u_msg,
                            expected_output=a_msg or None
                        ))
                eval_dataset = EvaluationDataset(
                    dataset_id=f"eval-ds-{model_id}",
                    dataset_name="validation_records",
                    total_examples=len(val_records),
                    train_examples_count=max(0, len(val_records) - len(examples)),
                    eval_examples_count=len(examples),
                    examples=examples
                )
        else:
            eval_dataset = EvaluationDataset(
                dataset_id=f"eval-ds-{model_id}",
                dataset_name="held_out_validation",
                total_examples=1,
                train_examples_count=0,
                eval_examples_count=1,
                examples=[EvaluationExample(
                    id="sample-1",
                    prompt="Summarize the core guidelines provided in the context.",
                    expected_output=None
                )]
            )

        pipeline_info = {
            "id": model_id,
            "architecture": architecture,
            "base_model": base_model_id,
            "adapter_path": adapter_path,
            "training_config": {"requirement": requirement}
        }

        # Run through EvaluationEngine
        report = await EvaluationEngine.evaluate_pipeline(
            pipeline_info=pipeline_info,
            eval_dataset=eval_dataset
        )

        # Save to evaluation manager
        evaluation_manager._save_report(report)

        # Convert to legacy ModelEvaluation schema for backward compatibility
        legacy_metrics = [
            EvaluationMetric(
                name=m.name,
                base_score=m.baseline_score,
                custom_score=m.customized_score,
                improvement=m.absolute_change_pp,
                description=m.description
            )
            for m in report.metrics
        ]

        legacy_samples = [
            EvaluationSample(
                prompt=s.prompt,
                expected_output=s.expected_output,
                base_model_output=s.baseline_output,
                custom_model_output=s.customized_output,
                evaluation_notes=s.evaluator_notes
            )
            for s in report.sample_comparisons
        ]

        return ModelEvaluation(
            model_id=model_id,
            evaluated_at=report.evaluated_at,
            num_samples_evaluated=report.num_examples,
            overall_base_score=report.overall_baseline_score,
            overall_custom_score=report.overall_customized_score,
            metrics=legacy_metrics,
            sample_comparisons=legacy_samples
        )
