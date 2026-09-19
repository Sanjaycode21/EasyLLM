import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.api.schemas import BuildJobStatus, BuildConfiguration, BuildLogEvent
from app.jobs.job_manager import job_manager

class ComputeProvider(ABC):
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

class LocalComputeProvider(ComputeProvider):
    """
    Local GPU/CPU Compute Provider executing jobs in worker threads.
    """
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

compute_provider = LocalComputeProvider()
