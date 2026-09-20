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


const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "";

export class APIProvider implements AIPlatformProvider {
  private baseUrl: string;

  constructor(baseUrl: string = BACKEND_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async getHardware(): Promise<HardwareStatus> {
    const res = await fetch(`${this.baseUrl}/api/hardware`);
    if (!res.ok) {
      throw new Error(`Failed to fetch hardware status: ${res.statusText}`);
    }
    return res.json();
  }

  async uploadDataset(file: File): Promise<DatasetMetadata> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${this.baseUrl}/api/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  }

  async analyzeRequirement(
    requirement: string,
    datasetId?: string
  ): Promise<ArchitectureAnalysis> {
    const formData = new FormData();
    formData.append("requirement", requirement);
    if (datasetId) {
      formData.append("dataset_id", datasetId);
    }

    const res = await fetch(`${this.baseUrl}/api/analyze`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Analysis failed");
    }
    return res.json();
  }

  async startBuild(config: BuildConfiguration): Promise<BuildJobStatus> {
    const res = await fetch(`${this.baseUrl}/api/build`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Failed to start build");
    }
    return res.json();
  }

  async getBuildStatus(jobId: string): Promise<BuildJobStatus> {
    const res = await fetch(`${this.baseUrl}/api/build/${jobId}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Failed to get build status");
    }
    return res.json();
  }

  async getModels(): Promise<RegisteredModel[]> {
    const res = await fetch(`${this.baseUrl}/api/models`);
    if (!res.ok) {
      throw new Error(`Failed to list models: ${res.statusText}`);
    }
    return res.json();
  }

  async getModel(modelId: string): Promise<RegisteredModel> {
    const res = await fetch(`${this.baseUrl}/api/models/${modelId}`);
    if (!res.ok) {
      throw new Error(`Model not found: ${res.statusText}`);
    }
    return res.json();
  }

  async getEvaluation(modelId: string): Promise<ModelEvaluation> {
    const res = await fetch(`${this.baseUrl}/api/evaluation/${modelId}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Evaluation not found");
    }
    return res.json();
  }

  async getEvaluationReport(modelIdOrEvalId: string): Promise<EvaluationReport> {
    const res = await fetch(`${this.baseUrl}/api/evaluation/report/${modelIdOrEvalId}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Evaluation report not found");
    }
    return res.json();
  }


  async sendMessage(
    modelId: string,
    message: string,
    history: { role: string; content: string }[] = []
  ): Promise<ChatResponse> {
    const res = await fetch(`${this.baseUrl}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model_id: modelId,
        message,
        history,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Chat request failed");
    }
    return res.json();
  }
}
