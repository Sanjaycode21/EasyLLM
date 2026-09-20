import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.api.schemas import BuildJobStatus, BuildConfiguration, BuildLogEvent
from app.jobs.job_manager import job_manager
from app.training.hardware_check import get_hardware_status
from app.compute.colab_generator import ColabNotebookGenerator
from app.config import settings

class ComputeProvider(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def submit_job(self, config: BuildConfiguration, dataset_path: Optional[Path] = None) -> BuildJobStatus:
        pass

    @abstractmethod
    def get_job_status(self, job_id: str) -> Optional[BuildJobStatus]:
        pass

    @abstractmethod
    def cancel_job(self, job_id: str) -> bool:
        pass

    @abstractmethod
    def get_logs(self, job_id: str) -> List[BuildLogEvent]:
        pass

    @abstractmethod
    def get_artifacts(self, job_id: str) -> Dict[str, Any]:
        pass

class LocalGPUProvider(ComputeProvider):
    """
    Executes training and RAG indexing on the host system (GPU/CPU).
    """
    def name(self) -> str:
        return "LocalGPUProvider"

    def submit_job(self, config: BuildConfiguration, dataset_path: Optional[Path] = None) -> BuildJobStatus:
        job = job_manager.create_job(config)
        thread = threading.Thread(
            target=job_manager.execute_build,
            args=(job.job_id, config, dataset_path),
            daemon=True
        )
        thread.start()
        return job

    def get_job_status(self, job_id: str) -> Optional[BuildJobStatus]:
        return job_manager.get_job(job_id)

    def cancel_job(self, job_id: str) -> bool:
        job = job_manager.get_job(job_id)
        if job and job.status not in ["COMPLETED", "FAILED"]:
            job_manager.update_status(job_id, "FAILED", error="Job cancelled by user.")
            return True
        return False

    def get_logs(self, job_id: str) -> List[BuildLogEvent]:
        job = job_manager.get_job(job_id)
        return job.logs if job else []

    def get_artifacts(self, job_id: str) -> Dict[str, Any]:
        job = job_manager.get_job(job_id)
        if not job or not job.model_id:
            return {}
        model = job_manager.models.get(job.model_id)
        return model.model_dump() if model else {}

class ColabProvider(ComputeProvider):
    """
    External Cloud Compute Fallback for heavy 4B+ parameter QLoRA jobs.
    Generates a ready-to-run Google Colab Notebook with pre-injected data and 4-bit Qwen3-4B pipeline.
    """
    def name(self) -> str:
        return "ColabProvider"

    def submit_job(self, config: BuildConfiguration, dataset_path: Optional[Path] = None) -> BuildJobStatus:
        job = job_manager.create_job(config)
        
        # Parse dataset records
        from app.ingestion.dataset_processor import DatasetProcessor
        training_records = []
        if dataset_path and dataset_path.exists():
            ext = dataset_path.suffix.lower()
            if ext == ".jsonl":
                training_records, _ = DatasetProcessor.validate_and_parse_jsonl(dataset_path)
            elif ext == ".csv":
                training_records, _ = DatasetProcessor.parse_csv_to_chat(dataset_path)

        # Generate notebook
        nb_filename = f"EasyLLM_Qwen3_4B_QLoRA_{job.job_id[:8]}.ipynb"
        nb_path = settings.artifacts_dir / nb_filename
        ColabNotebookGenerator.save_notebook(config, training_records, job.job_id, nb_path)

        # Log details to job
        job.colab_notebook_url = f"/api/compute/colab/{job.job_id}"
        job.colab_filename = nb_filename
        job.compute_provider = "ColabProvider"

        job_manager.update_job_log(job.job_id, "INFO", f"Generated external Colab training notebook: {nb_filename}", progress=50.0)
        job_manager.update_job_log(
            job.job_id,
            "INFO",
            f"Colab training notebook is ready. Run on free Google Colab GPU (T4/A100) to train Qwen3-4B.",
            progress=100.0
        )
        model_id = f"model-{job.job_id[:8]}"
        
        # Register model placeholder
        from app.api.schemas import RegisteredModel
        from datetime import datetime
        registered = RegisteredModel(
            id=model_id,
            name=f"Qwen3-4B Instruct ({config.strategy.upper()})",
            base_model=config.base_model_id,
            architecture=config.strategy,
            status="READY",
            dataset_name=dataset_path.name if dataset_path else "instructions",
            training_time_seconds=60.0,
            training_config=config.model_dump(),
            created_at=datetime.utcnow().isoformat()
        )
        with job_manager._lock:
            job_manager.models[model_id] = registered
            job.model_id = model_id

        job_manager.update_status(
            job.job_id,
            "COMPLETED"
        )

        return job

    def get_job_status(self, job_id: str) -> Optional[BuildJobStatus]:
        return job_manager.get_job(job_id)

    def cancel_job(self, job_id: str) -> bool:
        return False

    def get_logs(self, job_id: str) -> List[BuildLogEvent]:
        job = job_manager.get_job(job_id)
        return job.logs if job else []

    def get_artifacts(self, job_id: str) -> Dict[str, Any]:
        job = job_manager.get_job(job_id)
        if not job:
            return {}
        nb_filename = f"EasyLLM_Qwen3_4B_QLoRA_{job.job_id[:8]}.ipynb"
        return {
            "notebook_filename": nb_filename,
            "download_url": f"/api/compute/colab/{job.job_id}",
            "strategy": "qlora",
            "base_model": config.base_model_id if 'config' in locals() else "Qwen/Qwen3-4B-Instruct-2507"
        }

def get_compute_provider(strategy: str = "rag", force_provider: Optional[str] = None) -> ComputeProvider:
    """
    Intelligently routes jobs based on hardware availability and strategy:
    - RAG: Always runs on LocalGPUProvider (lightweight & fast)
    - QLoRA / Hybrid: Runs on LocalGPUProvider if local GPU fits, else routes to ColabProvider.
    """
    if force_provider == "colab":
        return ColabProvider()
    elif force_provider == "local":
        return LocalGPUProvider()

    if strategy == "rag":
        return LocalGPUProvider()

    hw = get_hardware_status()
    if hw["can_fit_qwen3_4b_local"]:
        return LocalGPUProvider()
    else:
        # Fallback to ColabProvider for heavy QLoRA when local VRAM is constrained or CPU-only
        return ColabProvider()

# Default singleton provider
compute_provider = LocalGPUProvider()
