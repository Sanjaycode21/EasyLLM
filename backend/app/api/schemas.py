from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from app.multimodal.schemas import PipelineTraceStep, MultimodalProcessingResult, MultimodalBatchResult

# Dataset Metadata Schemas
class DatasetMetadata(BaseModel):
    filename: str
    file_type: str = "txt"
    modality: Optional[Literal["text", "document", "image", "audio", "unknown"]] = "text"
    file_size_bytes: int = 0
    num_records: int = 0
    num_valid_examples: int = 0
    num_invalid_examples: int = 0
    format: str = "raw_text" # "chat_messages", "prompt_response", "document_text", "tabular", "multimodal_image", "multimodal_audio"
    sample_preview: Optional[List[Any]] = None
    training_compatible: bool = False
    knowledge_density: float = 0.0 # 0 to 1 score indicating if document is informational
    validation_errors: List[str] = []
    normalized_content: Optional[str] = None
    pipeline_trace: List[PipelineTraceStep] = []

# Requirement Analysis Schema
class ArchitectureAnalysis(BaseModel):
    task: str
    knowledge_required: bool
    behavior_customization: bool
    recommended_strategy: Literal["rag", "qlora", "hybrid"]
    reason: str
    confidence: float = 0.95
    suggested_base_model: str = "Qwen/Qwen3-4B-Instruct-2507"
    data_compatible: bool = True
    validation_notes: List[str] = []
    modalities_detected: List[str] = []
    pipeline_trace: List[PipelineTraceStep] = []

# Hardware Status Schema
class HardwareStatus(BaseModel):
    gpu_name: str
    physical_gpu_name: str = "N/A"
    total_vram_gb: float = 0.0
    free_vram_gb: float = 0.0
    cuda_available: bool = False
    pytorch_cuda: bool = False
    pytorch_version: str = "N/A"
    driver_version: Optional[str] = None
    cpu_cores: int = 1
    system_ram_gb: float = 0.0
    free_ram_gb: float = 0.0
    libraries: Dict[str, str] = {}
    target_model: str = "Qwen/Qwen3-4B-Instruct-2507"
    can_fit_qwen3_4b_local: bool = False
    recommended_mode: str = "colab_recommended"
    recommended_mode_text: str = ""

# Build Configuration
class BuildConfiguration(BaseModel):
    requirement: str
    dataset_id: Optional[str] = None
    strategy: Literal["rag", "qlora", "hybrid"]
    base_model_id: str = "Qwen/Qwen3-4B-Instruct-2507"
    lora_rank: int = 8
    lora_alpha: int = 16
    learning_rate: float = 2e-4
    epochs: int = 2
    batch_size: int = 1
    gradient_accumulation_steps: int = 4
    max_seq_length: int = 512
    chunk_size: int = 500
    chunk_overlap: int = 50
    force_compute_provider: Optional[Literal["auto", "local", "colab"]] = "auto"

# Build Status & Log Event
class BuildLogEvent(BaseModel):
    timestamp: str
    level: str # INFO, WARNING, ERROR, PROGRESS
    message: str
    progress_pct: Optional[float] = None
    loss: Optional[float] = None
    step: Optional[int] = None
    total_steps: Optional[int] = None

class BuildJobStatus(BaseModel):
    job_id: str
    status: Literal[
        "QUEUED",
        "INITIALIZING",
        "DOWNLOADING_MODEL",
        "PREPARING_DATA",
        "TRAINING",
        "EVALUATING",
        "SAVING",
        "COMPLETED",
        "FAILED"
    ]
    strategy: Literal["rag", "qlora", "hybrid"]
    base_model_id: str
    dataset_id: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress_percentage: float = 0.0
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    current_loss: Optional[float] = None
    loss_history: List[Dict[str, Any]] = []
    logs: List[BuildLogEvent] = []
    error_message: Optional[str] = None
    model_id: Optional[str] = None
    colab_notebook_url: Optional[str] = None
    colab_filename: Optional[str] = None
    compute_provider: Optional[str] = None

from app.evaluation.schemas import EvaluationReport

# Evaluation Schema
class EvaluationMetric(BaseModel):
    name: str
    base_score: float
    custom_score: float
    improvement: float
    description: str

class EvaluationSample(BaseModel):
    prompt: str
    expected_output: Optional[str] = None
    base_model_output: str
    custom_model_output: str
    evaluation_notes: str

class ModelEvaluation(BaseModel):
    model_id: str
    evaluated_at: str
    num_samples_evaluated: int
    overall_base_score: float
    overall_custom_score: float
    metrics: List[EvaluationMetric]
    sample_comparisons: List[EvaluationSample]

# Evaluation Run Request
class EvaluationRunRequest(BaseModel):
    pipeline_id: str
    dataset_id: Optional[str] = None
    split_ratio: float = 0.2
    seed: int = 42

# Registered Model Schema
class RegisteredModel(BaseModel):
    id: str
    name: str
    base_model: str
    architecture: Literal["rag", "qlora", "hybrid"]
    status: str = "READY"
    adapter_path: Optional[str] = None
    vector_db_path: Optional[str] = None
    dataset_name: Optional[str] = None
    training_time_seconds: Optional[float] = None
    evaluation: Optional[ModelEvaluation] = None
    evaluation_report: Optional[EvaluationReport] = None
    training_config: Optional[Dict[str, Any]] = None
    created_at: str


# Chat Request & Response
class ChatRequest(BaseModel):
    model_id: str
    message: str
    history: List[Dict[str, str]] = [] # [{"role": "user", "content": "..."}, ...]

class RetrievedSource(BaseModel):
    document_name: str
    page: Optional[int] = None
    chunk_index: int
    snippet: str
    relevance_score: float

class ChatResponse(BaseModel):
    message: str
    model_id: str
    architecture: Literal["rag", "qlora", "hybrid"]
    sources: Optional[List[RetrievedSource]] = None
    metadata: Dict[str, Any] = {}
