export type ModalityType = "text" | "document" | "image" | "audio" | "unknown";

export interface PipelineTraceStep {
  step_id: string;
  title: string;
  modality?: string;
  component: string;
  status: "completed" | "active" | "failed" | "pending";
  description: string;
  input_type: string;
  output_type: string;
  details?: Record<string, any>;
}

export interface MultimodalProcessingResult {
  id: string;
  filename: string;
  modality: ModalityType;
  mime_type: string;
  file_size_bytes: number;
  status: "PROCESSED" | "FAILED" | "PENDING";
  normalized_content?: string;
  metadata?: Record<string, any>;
  pipeline_trace?: PipelineTraceStep[];
  error_message?: string;
}

export interface MultimodalBatchResult {
  batch_id: string;
  items: MultimodalProcessingResult[];
  modalities_detected: string[];
  total_files: number;
  successful_files: number;
  failed_files: number;
  combined_knowledge_text: string;
  pipeline_trace: PipelineTraceStep[];
}

export interface DatasetMetadata {
  filename: string;
  file_type: string;
  modality?: ModalityType;
  file_size_bytes: number;
  num_records: number;
  num_valid_examples: number;
  num_invalid_examples: number;
  format: string;
  sample_preview?: any[];
  training_compatible: boolean;
  knowledge_density: number;
  validation_errors: string[];
  normalized_content?: string;
  pipeline_trace?: PipelineTraceStep[];
}

export interface ArchitectureAnalysis {
  task: string;
  knowledge_required: boolean;
  behavior_customization: boolean;
  recommended_strategy: "rag" | "qlora" | "hybrid";
  reason: string;
  confidence: number;
  suggested_base_model: string;
  data_compatible: boolean;
  validation_notes: string[];
  modalities_detected?: string[];
  pipeline_trace?: PipelineTraceStep[];
}

export interface HardwareStatus {
  gpu_name: string;
  physical_gpu_name?: string;
  total_vram_gb: number;
  free_vram_gb: number;
  cuda_available: boolean;
  pytorch_cuda: boolean;
  pytorch_version: string;
  driver_version?: string;
  cpu_cores: number;
  system_ram_gb: number;
  free_ram_gb?: number;
  libraries?: Record<string, string>;
  target_model?: string;
  can_fit_qwen3_4b_local?: boolean;
  recommended_mode?: string;
  recommended_mode_text?: string;
  device_name?: string;
  recommended_quantization?: string;
}

export interface BuildConfiguration {
  requirement: string;
  dataset_id?: string;
  strategy: "rag" | "qlora" | "hybrid";
  base_model_id: string;
  lora_rank?: number;
  lora_alpha?: number;
  learning_rate?: number;
  epochs?: number;
  batch_size?: number;
  gradient_accumulation_steps?: number;
  max_seq_length?: number;
  chunk_size?: number;
  chunk_overlap?: number;
}

export interface BuildLogEvent {
  timestamp: string;
  level: "INFO" | "WARNING" | "ERROR" | "PROGRESS";
  message: string;
  progress_pct?: number;
  loss?: number;
  step?: number;
  total_steps?: number;
}

export interface BuildJobStatus {
  job_id: string;
  status:
    | "QUEUED"
    | "INITIALIZING"
    | "DOWNLOADING_MODEL"
    | "PREPARING_DATA"
    | "TRAINING"
    | "EVALUATING"
    | "SAVING"
    | "COMPLETED"
    | "FAILED";
  strategy: "rag" | "qlora" | "hybrid";
  base_model_id: string;
  dataset_id?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress_percentage: number;
  current_step?: number;
  total_steps?: number;
  current_loss?: number;
  loss_history: { step: number; loss: number }[];
  logs: BuildLogEvent[];
  error_message?: string;
  model_id?: string;
  colab_notebook_url?: string;
  colab_filename?: string;
  compute_provider?: string;
}

export type ImprovementStatus =
  | "IMPROVED"
  | "REGRESSED"
  | "NO_SIGNIFICANT_CHANGE"
  | "EVALUATION_INCONCLUSIVE"
  | "EVALUATION_FAILED";

export interface EvaluationMetricResult {
  name: string;
  baseline_score: number;
  customized_score: number;
  absolute_change_pp: number; // e.g. +17.0 pp
  relative_change_pct: number; // e.g. +23.6 %
  status: "improved" | "regressed" | "no_change";
  description: string;
  evaluator_method?: "deterministic" | "llm_judge" | "hybrid";
  details?: Record<string, any>;
}

export interface EvaluationSampleResult {
  sample_id: string;
  prompt: string;
  expected_output?: string;
  baseline_output: string;
  customized_output: string;
  baseline_score: number;
  customized_score: number;
  score_delta: number;
  retrieved_sources?: RetrievedSource[];
  evaluator_notes: string;
  metrics_breakdown?: Record<string, any>;
}

export interface SystemPerformanceMetrics {
  baseline_latency_ms: number;
  customized_latency_ms: number;
  latency_delta_ms: number;
  retrieval_latency_ms?: number;
  generation_latency_ms?: number;
  baseline_tokens_generated?: number;
  customized_tokens_generated?: number;
}

export interface EvaluationReport {
  evaluation_id: string;
  pipeline_id: string;
  pipeline_type: "rag" | "qlora" | "hybrid" | "generic";
  base_model: string;
  dataset_name: string;
  dataset_version: string;
  num_examples: number;
  eval_sample_size_limited?: boolean;
  baseline: {
    pipeline_id: string;
    pipeline_type: string;
    base_model: string;
    pipeline_version: string;
    configuration?: Record<string, any>;
  };
  customized: {
    pipeline_id: string;
    pipeline_type: string;
    base_model: string;
    pipeline_version: string;
    configuration?: Record<string, any>;
  };
  overall_baseline_score: number;
  overall_customized_score: number;
  overall_absolute_change_pp: number;
  overall_relative_change_pct: number;
  overall_status: ImprovementStatus;
  metrics: EvaluationMetricResult[];
  sample_comparisons: EvaluationSampleResult[];
  system_performance: SystemPerformanceMetrics;
  conclusion: string;
  evaluator_model: string;
  evaluated_at: string;
}

export interface EvaluationJobStatus {
  evaluation_id: string;
  pipeline_id: string;
  status:
    | "QUEUED"
    | "INITIALIZING"
    | "LOADING_DATASET"
    | "LOADING_BASELINE"
    | "EVALUATING_BASELINE"
    | "LOADING_CUSTOMIZED"
    | "EVALUATING_CUSTOMIZED"
    | "CALCULATING_METRICS"
    | "COMPARING"
    | "COMPLETED"
    | "FAILED";
  progress_pct: number;
  current_step?: string;
  report?: EvaluationReport;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface EvaluationMetric {
  name: string;
  base_score: number;
  custom_score: number;
  improvement: number;
  description: string;
}

export interface EvaluationSample {
  prompt: string;
  expected_output?: string;
  base_model_output: string;
  custom_model_output: string;
  evaluation_notes: string;
}

export interface ModelEvaluation {
  model_id: string;
  evaluated_at: string;
  num_samples_evaluated: number;
  overall_base_score: number;
  overall_custom_score: number;
  metrics: EvaluationMetric[];
  sample_comparisons: EvaluationSample[];
}

export interface RegisteredModel {
  id: string;
  name: string;
  base_model: string;
  architecture: "rag" | "qlora" | "hybrid";
  status: string;
  adapter_path?: string;
  vector_db_path?: string;
  dataset_name?: string;
  training_time_seconds?: number;
  evaluation?: ModelEvaluation;
  evaluation_report?: EvaluationReport;
  training_config?: Record<string, any>;
  created_at: string;
}

export interface RetrievedSource {
  document_name: string;
  page?: number;
  chunk_index: number;
  snippet: string;
  relevance_score: number;
}

export interface ChatResponse {
  message: string;
  model_id: string;
  architecture: "rag" | "qlora" | "hybrid";
  sources?: RetrievedSource[];
  metadata: {
    latency_ms?: number;
    base_model?: string;
    used_trained_adapter?: boolean;
    num_sources_retrieved?: number;
    tokens?: number;
  };
}

export interface AIPlatformProvider {
  getHardware(): Promise<HardwareStatus>;
  uploadDataset(file: File): Promise<DatasetMetadata>;
  analyzeRequirement(
    requirement: string,
    datasetId?: string
  ): Promise<ArchitectureAnalysis>;
  startBuild(config: BuildConfiguration): Promise<BuildJobStatus>;
  getBuildStatus(jobId: string): Promise<BuildJobStatus>;
  getModels(): Promise<RegisteredModel[]>;
  getModel(modelId: string): Promise<RegisteredModel>;
  getEvaluation(modelId: string): Promise<ModelEvaluation>;
  getEvaluationReport(modelIdOrEvalId: string): Promise<EvaluationReport>;
  sendMessage(
    modelId: string,
    message: string,
    history?: { role: string; content: string }[]
  ): Promise<ChatResponse>;
}

