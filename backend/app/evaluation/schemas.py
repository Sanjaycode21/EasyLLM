from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

ImprovementStatus = Literal[
    "IMPROVED",
    "REGRESSED",
    "NO_SIGNIFICANT_CHANGE",
    "EVALUATION_INCONCLUSIVE",
    "EVALUATION_FAILED"
]

EvaluationJobState = Literal[
    "QUEUED",
    "INITIALIZING",
    "LOADING_DATASET",
    "LOADING_BASELINE",
    "EVALUATING_BASELINE",
    "LOADING_CUSTOMIZED",
    "EVALUATING_CUSTOMIZED",
    "CALCULATING_METRICS",
    "COMPARING",
    "COMPLETED",
    "FAILED"
]

class EvaluationExample(BaseModel):
    id: str
    prompt: str
    expected_output: Optional[str] = None
    retrieved_context: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EvaluationDataset(BaseModel):
    dataset_id: str
    dataset_name: str
    version: str = "1.0"
    total_examples: int
    train_examples_count: int
    eval_examples_count: int
    split_ratio: float = 0.2
    is_held_out: bool = True
    examples: List[EvaluationExample] = Field(default_factory=list)

class EvaluationMetricResult(BaseModel):
    name: str
    baseline_score: float
    customized_score: float
    absolute_change_pp: float # e.g. +17.0 pp
    relative_change_pct: float # e.g. +23.6 %
    status: Literal["improved", "regressed", "no_change"]
    description: str
    evaluator_method: Literal["deterministic", "llm_judge", "hybrid"] = "deterministic"
    details: Optional[Dict[str, Any]] = None

class EvaluationSampleResult(BaseModel):
    sample_id: str
    prompt: str
    expected_output: Optional[str] = None
    baseline_output: str
    customized_output: str
    baseline_score: float # 0 to 100
    customized_score: float # 0 to 100
    score_delta: float
    retrieved_sources: Optional[List[Dict[str, Any]]] = None
    evaluator_notes: str
    metrics_breakdown: Dict[str, Any] = Field(default_factory=dict)

class SystemPerformanceMetrics(BaseModel):
    baseline_latency_ms: float = 0.0
    customized_latency_ms: float = 0.0
    latency_delta_ms: float = 0.0
    retrieval_latency_ms: Optional[float] = None
    generation_latency_ms: Optional[float] = None
    baseline_tokens_generated: Optional[int] = None
    customized_tokens_generated: Optional[int] = None

class PipelineMetadata(BaseModel):
    pipeline_id: str
    pipeline_type: Literal["rag", "qlora", "hybrid", "generic"]
    base_model: str
    pipeline_version: str = "1.0"
    configuration: Dict[str, Any] = Field(default_factory=dict)

class EvaluationReport(BaseModel):
    evaluation_id: str
    pipeline_id: str
    pipeline_type: Literal["rag", "qlora", "hybrid", "generic"]
    base_model: str
    dataset_name: str
    dataset_version: str = "1.0"
    num_examples: int
    eval_sample_size_limited: bool = False
    
    baseline: PipelineMetadata
    customized: PipelineMetadata
    
    overall_baseline_score: float
    overall_customized_score: float
    overall_absolute_change_pp: float
    overall_relative_change_pct: float
    overall_status: ImprovementStatus
    
    metrics: List[EvaluationMetricResult]
    sample_comparisons: List[EvaluationSampleResult]
    system_performance: SystemPerformanceMetrics
    
    conclusion: str
    evaluator_model: str = "MiniLM + Gemini-3.6-Flash / Rule Judge"
    evaluated_at: str

class EvaluationJobStatus(BaseModel):
    evaluation_id: str
    pipeline_id: str
    status: EvaluationJobState
    progress_pct: float = 0.0
    current_step: Optional[str] = None
    report: Optional[EvaluationReport] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
