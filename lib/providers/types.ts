export interface DatasetMetadata {
  filename: string;
  file_type: "pdf" | "docx" | "doc" | "txt" | "json" | "jsonl" | "csv" | "unknown";
  file_size_bytes: number;
  num_records: number;
  num_valid_examples: number;
  num_invalid_examples: number;
  format: string;
  sample_preview?: any[];
  training_compatible: boolean;
  knowledge_density: number;
  validation_errors: string[];
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
}

export interface HardwareStatus {
  cuda_available: boolean;
  device_name: string;
  device_count: number;
  total_vram_gb: number;
  free_vram_gb: number;
  cpu_cores: number;
  system_ram_gb: number;
  recommended_quantization: string;
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
  sendMessage(
    modelId: string,
    message: string,
    history?: { role: string; content: string }[]
  ): Promise<ChatResponse>;
}
