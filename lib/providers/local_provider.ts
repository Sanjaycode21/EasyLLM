import {
  AIPlatformProvider,
  HardwareStatus,
  DatasetMetadata,
  ArchitectureAnalysis,
  BuildConfiguration,
  BuildJobStatus,
  RegisteredModel,
  ModelEvaluation,
  EvaluationReport,
  ChatResponse,
} from "./types";


export class LocalProvider implements AIPlatformProvider {
  async getHardware(): Promise<HardwareStatus> {
    return {
      cuda_available: true,
      device_name: "NVIDIA RTX 4090 (Simulation)",
      device_count: 1,
      total_vram_gb: 24.0,
      free_vram_gb: 21.8,
      cpu_cores: 16,
      system_ram_gb: 64.0,
      recommended_quantization: "4bit",
    };
  }

  async uploadDataset(file: File): Promise<DatasetMetadata> {
    const isJsonl = file.name.endsWith(".jsonl");
    return {
      filename: file.name,
      file_type: isJsonl ? "jsonl" : "pdf",
      file_size_bytes: file.size,
      num_records: isJsonl ? 120 : 12,
      num_valid_examples: isJsonl ? 120 : 12,
      num_invalid_examples: 0,
      format: isJsonl ? "chat_messages" : "document_text",
      sample_preview: [
        {
          role: "user",
          content: "How do I return a damaged product?",
        },
        {
          role: "assistant",
          content: "You can request a replacement within 30 days.",
        },
      ],
      training_compatible: isJsonl,
      knowledge_density: isJsonl ? 0.4 : 0.95,
      validation_errors: [],
    };
  }

  async analyzeRequirement(
    requirement: string,
    datasetId?: string
  ): Promise<ArchitectureAnalysis> {
    const isRAG =
      requirement.toLowerCase().includes("manual") ||
      requirement.toLowerCase().includes("policy") ||
      requirement.toLowerCase().includes("pdf");
    const isHybrid =
      requirement.toLowerCase().includes("both") ||
      (requirement.toLowerCase().includes("policy") &&
        requirement.toLowerCase().includes("style"));

    const strategy = isHybrid ? "hybrid" : isRAG ? "rag" : "qlora";

    return {
      task: "customer_support",
      knowledge_required: isRAG || isHybrid,
      behavior_customization: !isRAG || isHybrid,
      recommended_strategy: strategy,
      reason: isHybrid
        ? "The task requires knowledge lookup from documents and conversational tone adaptation."
        : isRAG
        ? "The task primarily requires factual retrieval from reference documents."
        : "The task requires learning domain-specific tone and style from examples.",
      confidence: 0.96,
      suggested_base_model: "HuggingFaceTB/SmolLM2-135M-Instruct",
      data_compatible: true,
      validation_notes: ["Validated against local test suite."],
    };
  }

  async startBuild(config: BuildConfiguration): Promise<BuildJobStatus> {
    return {
      job_id: "job-local-preview",
      status: "COMPLETED",
      strategy: config.strategy,
      base_model_id: config.base_model_id,
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      progress_percentage: 100,
      logs: [
        {
          timestamp: new Date().toISOString(),
          level: "PROGRESS",
          message: "Local preview build ready.",
        },
      ],
      loss_history: [
        { step: 1, loss: 2.1 },
        { step: 5, loss: 1.4 },
        { step: 10, loss: 0.82 },
      ],
      model_id: "model-local-preview",
    };
  }

  async getBuildStatus(jobId: string): Promise<BuildJobStatus> {
    return this.startBuild({
      requirement: "Support",
      strategy: "rag",
      base_model_id: "SmolLM2",
    });
  }

  async getModels(): Promise<RegisteredModel[]> {
    return [
      {
        id: "model-local-rag",
        name: "Acme Support Knowledge AI",
        base_model: "HuggingFaceTB/SmolLM2-135M-Instruct",
        architecture: "rag",
        status: "READY",
        dataset_name: "company_manual.pdf",
        training_time_seconds: 4.2,
        created_at: new Date().toISOString(),
      },
    ];
  }

  async getModel(modelId: string): Promise<RegisteredModel> {
    return (await this.getModels())[0];
  }

  async getEvaluation(modelId: string): Promise<ModelEvaluation> {
    return {
      model_id: modelId,
      evaluated_at: new Date().toISOString(),
      num_samples_evaluated: 5,
      overall_base_score: 52.4,
      overall_custom_score: 91.8,
      metrics: [
        {
          name: "Semantic Relevance",
          base_score: 55.0,
          custom_score: 94.0,
          improvement: 39.0,
          description: "Cosine similarity with ground truth.",
        },
      ],
      sample_comparisons: [],
    };
  }

  async getEvaluationReport(modelIdOrEvalId: string): Promise<EvaluationReport> {
    return {
      evaluation_id: "eval-local-sample",
      pipeline_id: modelIdOrEvalId,
      pipeline_type: "rag",
      base_model: "Qwen/Qwen3-4B-Instruct-2507",
      dataset_name: "company_manual.pdf",
      dataset_version: "1.0",
      num_examples: 5,
      baseline: {
        pipeline_id: "base-qwen3-4b",
        pipeline_type: "rag",
        base_model: "Qwen/Qwen3-4B-Instruct-2507",
        pipeline_version: "1.0-unassisted",
      },
      customized: {
        pipeline_id: modelIdOrEvalId,
        pipeline_type: "rag",
        base_model: "Qwen/Qwen3-4B-Instruct-2507",
        pipeline_version: "1.0-customized",
      },
      overall_baseline_score: 52.4,
      overall_customized_score: 91.8,
      overall_absolute_change_pp: 39.4,
      overall_relative_change_pct: 75.2,
      overall_status: "IMPROVED",
      metrics: [
        {
          name: "Semantic Similarity",
          baseline_score: 55.0,
          customized_score: 94.0,
          absolute_change_pp: 39.0,
          relative_change_pct: 70.9,
          status: "improved",
          description: "Dense cosine similarity with ground truth validation answers.",
          evaluator_method: "deterministic",
        },
        {
          name: "Context Groundedness & Faithfulness",
          baseline_score: 48.0,
          customized_score: 96.0,
          absolute_change_pp: 48.0,
          relative_change_pct: 100.0,
          status: "improved",
          description: "Absence of hallucinations and compliance with source facts.",
          evaluator_method: "llm_judge",
        },
        {
          name: "Instruction & Persona Adherence",
          baseline_score: 54.0,
          customized_score: 90.0,
          absolute_change_pp: 36.0,
          relative_change_pct: 66.7,
          status: "improved",
          description: "Degree of compliance with specified role constraints.",
          evaluator_method: "llm_judge",
        },
      ],
      sample_comparisons: [
        {
          sample_id: "sample-1",
          prompt: "What is the return policy for defective items?",
          expected_output: "All physical hardware items can be returned within 30 days.",
          baseline_output: "Return policies vary depending on the retailer and conditions.",
          customized_output: "According to the official policy, all physical hardware items are protected by a 30-day money-back return policy.",
          baseline_score: 45.0,
          customized_score: 98.0,
          score_delta: 53.0,
          evaluator_notes: "Groundedness and factual correctness significantly improved with retrieved context.",
        },
      ],
      system_performance: {
        baseline_latency_ms: 180.0,
        customized_latency_ms: 220.0,
        latency_delta_ms: 40.0,
        retrieval_latency_ms: 35.0,
        generation_latency_ms: 185.0,
      },
      conclusion: "Customization delivered a validated overall gain of +39.4 pp (+75.2% relative improvement) across 5 held-out evaluation samples.",
      evaluator_model: "MiniLM + Gemini-3.6-Flash / Rule Judge",
      evaluated_at: new Date().toISOString(),
    };
  }


  async sendMessage(
    modelId: string,
    message: string,
    history?: { role: string; content: string }[]
  ): Promise<ChatResponse> {
    return {
      message: `[Local Provider] I processed your query: "${message}". All policies are confirmed.`,
      model_id: modelId,
      architecture: "rag",
      sources: [
        {
          document_name: "company_manual.pdf",
          page: 1,
          chunk_index: 0,
          snippet: "All physical hardware appliances purchased directly from ACME are protected by a 30-day money-back guarantee.",
          relevance_score: 0.94,
        },
      ],
      metadata: { latency_ms: 120 },
    };
  }
}
