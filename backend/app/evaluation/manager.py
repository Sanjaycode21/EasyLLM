import json
import uuid
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.config import settings
from app.evaluation.schemas import EvaluationJobStatus, EvaluationReport, EvaluationDataset, EvaluationJobState
from app.evaluation.engine import EvaluationEngine

class EvaluationJobManager:
    """
    Manages lifecycle of asynchronous evaluation jobs, report persistence, and historical run tracking.
    """
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or (settings.models_dir.parent / "storage" / "evaluations")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.jobs: Dict[str, EvaluationJobStatus] = {}
        self.reports: Dict[str, EvaluationReport] = {}
        self._lock = threading.Lock()
        self._load_persisted_reports()

    def _load_persisted_reports(self):
        try:
            for file_path in self.storage_dir.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        report = EvaluationReport(**data)
                        self.reports[report.evaluation_id] = report
                except Exception as e:
                    print(f"[EvaluationJobManager] Could not load persisted report {file_path.name}: {e}")
        except Exception as e:
            print(f"[EvaluationJobManager] Error loading persisted reports: {e}")

    def _save_report(self, report: EvaluationReport):
        with self._lock:
            self.reports[report.evaluation_id] = report
        
        file_path = self.storage_dir / f"{report.evaluation_id}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report.model_dump_json(indent=2))
        except Exception as e:
            print(f"[EvaluationJobManager] Failed to persist evaluation report {report.evaluation_id}: {e}")

    def create_job(self, pipeline_id: str) -> EvaluationJobStatus:
        eval_id = f"eval-{uuid.uuid4().hex[:8]}"
        job = EvaluationJobStatus(
            evaluation_id=eval_id,
            pipeline_id=pipeline_id,
            status="QUEUED",
            progress_pct=0.0,
            current_step="Queued for evaluation",
            created_at=datetime.utcnow().isoformat()
        )
        with self._lock:
            self.jobs[eval_id] = job
        return job

    def update_job(
        self,
        eval_id: str,
        status: EvaluationJobState,
        progress_pct: Optional[float] = None,
        current_step: Optional[str] = None,
        report: Optional[EvaluationReport] = None,
        error: Optional[str] = None
    ):
        with self._lock:
            job = self.jobs.get(eval_id)
            if not job:
                return
            job.status = status
            if progress_pct is not None:
                job.progress_pct = progress_pct
            if current_step is not None:
                job.current_step = current_step
            if report is not None:
                job.report = report
            if error is not None:
                job.error_message = error
            if status in ["COMPLETED", "FAILED"]:
                job.completed_at = datetime.utcnow().isoformat()

    def get_job(self, eval_id: str) -> Optional[EvaluationJobStatus]:
        with self._lock:
            return self.jobs.get(eval_id)

    def get_report(self, eval_id: str) -> Optional[EvaluationReport]:
        with self._lock:
            return self.reports.get(eval_id)

    def list_evaluations_for_pipeline(self, pipeline_id: str) -> List[EvaluationReport]:
        with self._lock:
            matching = [r for r in self.reports.values() if r.pipeline_id == pipeline_id]
            matching.sort(key=lambda x: x.evaluated_at, reverse=True)
            return matching

    async def run_evaluation_async(
        self,
        eval_id: str,
        pipeline_info: Dict[str, Any],
        eval_dataset: EvaluationDataset
    ):
        try:
            self.update_job(eval_id, "INITIALIZING", 5.0, "Preparing evaluation pipeline...")
            
            def progress_cb(step_msg: str, pct: float):
                self.update_job(eval_id, "EVALUATING_CUSTOMIZED", pct, step_msg)

            self.update_job(eval_id, "EVALUATING_BASELINE", 15.0, "Executing baseline and customized inferences on held-out dataset...")
            
            report = await EvaluationEngine.evaluate_pipeline(
                pipeline_info=pipeline_info,
                eval_dataset=eval_dataset,
                progress_callback=progress_cb
            )
            # Override report ID with job's evaluation ID
            report.evaluation_id = eval_id
            
            self._save_report(report)
            self.update_job(eval_id, "COMPLETED", 100.0, "Evaluation complete.", report=report)
            return report

        except Exception as e:
            err_msg = str(e)
            print(f"[EvaluationJobManager] Evaluation job {eval_id} failed: {err_msg}")
            self.update_job(eval_id, "FAILED", 100.0, f"Evaluation failed: {err_msg}", error=err_msg)
            return None

evaluation_manager = EvaluationJobManager()
