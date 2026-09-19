import { create } from "zustand";
import {
  DatasetMetadata,
  ArchitectureAnalysis,
  BuildJobStatus,
  RegisteredModel,
  HardwareStatus,
} from "./providers/types";

interface AppState {
  // Provider toggle
  useLocalProvider: boolean;
  setUseLocalProvider: (val: boolean) => void;

  // Hardware Status
  hardware: HardwareStatus | null;
  setHardware: (hw: HardwareStatus | null) => void;

  // Step 1: Input & Upload
  requirement: string;
  setRequirement: (req: string) => void;
  datasetFile: File | null;
  setDatasetFile: (file: File | null) => void;
  datasetMetadata: DatasetMetadata | null;
  setDatasetMetadata: (meta: DatasetMetadata | null) => void;
  isAnalyzing: boolean;
  setIsAnalyzing: (val: boolean) => void;

  // Step 2: Architecture Decision
  analysis: ArchitectureAnalysis | null;
  setAnalysis: (analysis: ArchitectureAnalysis | null) => void;

  // Step 3: Build & Training
  activeJob: BuildJobStatus | null;
  setActiveJob: (job: BuildJobStatus | null) => void;
  isBuilding: boolean;
  setIsBuilding: (val: boolean) => void;

  // Step 4: Model Registry & Active Model
  models: RegisteredModel[];
  setModels: (models: RegisteredModel[]) => void;
  activeModel: RegisteredModel | null;
  setActiveModel: (model: RegisteredModel | null) => void;

  // Reset workflow
  resetWorkflow: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  useLocalProvider: false,
  setUseLocalProvider: (val) => set({ useLocalProvider: val }),

  hardware: null,
  setHardware: (hw) => set({ hardware: hw }),

  requirement: "",
  setRequirement: (req) => set({ requirement: req }),
  datasetFile: null,
  setDatasetFile: (file) => set({ datasetFile: file }),
  datasetMetadata: null,
  setDatasetMetadata: (meta) => set({ datasetMetadata: meta }),
  isAnalyzing: false,
  setIsAnalyzing: (val) => set({ isAnalyzing: val }),

  analysis: null,
  setAnalysis: (analysis) => set({ analysis }),

  activeJob: null,
  setActiveJob: (job) => set({ activeJob: job }),
  isBuilding: false,
  setIsBuilding: (val) => set({ isBuilding: val }),

  models: [],
  setModels: (models) => set({ models }),
  activeModel: null,
  setActiveModel: (model) => set({ activeModel: model }),

  resetWorkflow: () =>
    set({
      requirement: "",
      datasetFile: null,
      datasetMetadata: null,
      analysis: null,
      activeJob: null,
      isBuilding: false,
      isAnalyzing: false,
    }),
}));
