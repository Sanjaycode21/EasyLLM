"use client";

import { useAppStore } from "@/lib/store";
import {
  Sparkles,
  ArrowRight,
  BookOpen,
  Sliders,
  Layers,
  ChevronDown,
  ChevronUp,
  Cpu,
  Database,
  ShieldCheck,
  Zap,
  CheckCircle2,
  HardDrive,
  Info
} from "lucide-react";
import { useState } from "react";
import { getProvider } from "@/lib/providers";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { MultimodalPipelineTrace } from "./MultimodalPipelineTrace";

export function DecisionCard() {
  const router = useRouter();
  const {
    requirement,
    dataset,
    analysis,
    setAnalysis,
    isAnalyzing,
    isBuilding,
    setIsBuilding,
    setActiveJob,
    useLocalProvider,
  } = useAppStore();

  const [isTriggeringBuild, setIsTriggeringBuild] = useState(false);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  const handleAnalyze = async () => {
    if (!requirement.trim()) {
      toast.error("Please enter what you want your AI to do.");
      return;
    }

    try {
      const provider = getProvider(useLocalProvider);
      const res = await provider.analyzeRequirement(requirement, dataset?.filename);
      setAnalysis(res);
      toast.success(`Autonomous Architect selected: ${res.recommended_strategy.toUpperCase()}`);
    } catch (err: any) {
      toast.error(err.message || "Failed to analyze requirement");
    }
  };

  const handleBuild = async () => {
    if (!analysis) return;
    setIsTriggeringBuild(true);
    setIsBuilding(true);

    try {
      const provider = getProvider(useLocalProvider);
      const job = await provider.startBuild({
        requirement,
        strategy: analysis.recommended_strategy,
        base_model_id: analysis.suggested_base_model || "Qwen/Qwen3-4B-Instruct-2507",
        epochs: 2,
        lora_rank: 8,
        lora_alpha: 16,
        batch_size: 1,
        gradient_accumulation_steps: 4,
        max_seq_length: 512,
      });

      setActiveJob(job);
      toast.success(`Launched AI creation: ${job.job_id}`);
      router.push(`/build/${job.job_id}`);
    } catch (err: any) {
      toast.error(err.message || "Failed to launch AI creation pipeline");
      setIsBuilding(false);
    } finally {
      setIsTriggeringBuild(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Analyze Trigger */}
      {!analysis ? (
        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing || !requirement.trim()}
          className="w-full flex items-center justify-center gap-2.5 rounded-xl bg-blue-600 px-6 py-3.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-40"
        >
          {isAnalyzing ? (
            <span className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 animate-spin" />
              AI Architect Analyzing Your Goal & Data...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Analyze Goal & Design Optimal AI Architecture
            </span>
          )}
        </button>
      ) : (
        /* Architecture Decision Display */
        <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-blue-50 px-3 py-0.5 text-[11px] font-bold text-blue-700 border border-blue-200/60">
                  Architect Decision
                </span>
                <span className="text-[11px] text-slate-500 font-medium">
                  Confidence: <span className="text-emerald-700 font-bold">{Math.round(analysis.confidence * 100)}%</span>
                </span>
              </div>
              <h3 className="mt-2 text-base sm:text-lg font-bold text-slate-900 flex items-center gap-2">
                {analysis.recommended_strategy === "rag" && (
                  <>
                    <BookOpen className="h-5 w-5 text-blue-600" />
                    Knowledge Retrieval (RAG) Architecture
                  </>
                )}
                {analysis.recommended_strategy === "qlora" && (
                  <>
                    <Sliders className="h-5 w-5 text-purple-600" />
                    Behavioral Adaptation (QLoRA) Architecture
                  </>
                )}
                {analysis.recommended_strategy === "hybrid" && (
                  <>
                    <Layers className="h-5 w-5 text-amber-600" />
                    Hybrid Architecture (QLoRA + Knowledge RAG)
                  </>
                )}
              </h3>
            </div>

            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="rounded-lg border border-slate-200 bg-slate-50 px-3.5 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition self-start sm:self-auto"
            >
              Re-Analyze
            </button>
          </div>

          {/* User-Friendly Strategy Rationale */}
          <div className="rounded-xl bg-slate-50/80 p-4 border border-slate-200/80 text-xs sm:text-sm">
            <span className="font-bold text-slate-700 block text-xs mb-1 uppercase tracking-wider">
              Why this architecture was chosen for you:
            </span>
            <p className="text-slate-800 leading-relaxed">{analysis.reason}</p>
          </div>

          {/* Multimodal Pipeline Trace Diagram */}
          <MultimodalPipelineTrace
            strategy={analysis.recommended_strategy}
            modalities={analysis.modalities_detected || [dataset?.file_type || "text"]}
            trace={analysis.pipeline_trace}
          />

          {/* Validation & Modality Notes */}
          {analysis.validation_notes && analysis.validation_notes.length > 0 && (
            <div className="space-y-1.5">
              {analysis.validation_notes.map((note, idx) => (
                <div key={idx} className="flex items-start gap-2 text-xs text-slate-600">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                  <span>{note}</span>
                </div>
              ))}
            </div>
          )}

          {/* Expandable Technical Blueprint Drawer */}
          <div className="rounded-xl border border-slate-200 bg-slate-50/50 overflow-hidden">
            <button
              type="button"
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              className="w-full flex items-center justify-between p-3.5 text-xs font-semibold text-slate-700 hover:bg-slate-100/80 transition"
            >
              <div className="flex items-center gap-2">
                <Cpu className="h-4 w-4 text-blue-600" />
                <span>View technical configuration (Autonomous Blueprint)</span>
              </div>
              <div className="flex items-center gap-1 text-[11px] text-slate-500">
                <span>{showTechnicalDetails ? "Hide technical specs" : "Show technical specs"}</span>
                {showTechnicalDetails ? (
                  <ChevronUp className="h-4 w-4 text-slate-500" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-slate-500" />
                )}
              </div>
            </button>

            {showTechnicalDetails && (
              <div className="p-4 pt-1 border-t border-slate-200/80 space-y-3 text-xs bg-white">
                <p className="text-[11px] text-slate-500 mb-2">
                  All machine learning hyperparameters, quantization profiles, and hardware safeguards have been automatically computed for you.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-200/60">
                    <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Foundation Model</span>
                    <span className="font-mono text-slate-900 font-semibold">{analysis.suggested_base_model || "Qwen/Qwen3-4B-Instruct-2507"}</span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">3.8B Parameters · 28 Layers · 2560 Hidden Dim</span>
                  </div>

                  <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-200/60">
                    <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Precision & Quantization</span>
                    <span className="font-mono text-slate-900 font-semibold">4-bit NormalFloat4 (NF4)</span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">BitsAndBytes 4-bit · Double Quant Enabled</span>
                  </div>

                  <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-200/60">
                    <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">LoRA Adapter Config</span>
                    <span className="font-mono text-slate-900 font-semibold">Rank (r): 8 · Alpha (α): 16 · Dropout: 0.05</span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">All 7 linear projection targets (q,k,v,o,gate,up,down)</span>
                  </div>

                  <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-200/60">
                    <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Batch & Sequence Budget</span>
                    <span className="font-mono text-slate-900 font-semibold">Seq Len: 512 · Batch: 1 · Grad Accum: 4</span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Gradient Checkpointing Active · VRAM: ~3.2 GB</span>
                  </div>

                  <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-200/60">
                    <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Embedding & Vector Index</span>
                    <span className="font-mono text-slate-900 font-semibold">all-MiniLM-L6-v2 (384-dim)</span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Cosine Similarity In-Memory VectorStore</span>
                  </div>

                  <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-200/60">
                    <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Hardware Guardrail</span>
                    <span className="font-mono text-emerald-700 font-semibold">6GB VRAM Safe Profile</span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Zero risk of OOM crash on NVIDIA RTX 3050</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Primary Action Button: "Create AI" */}
          <div className="pt-2 flex items-center justify-between">
            <span className="text-xs text-slate-500">
              Ready to construct your custom AI pipeline
            </span>
            <button
              onClick={handleBuild}
              disabled={isTriggeringBuild || isBuilding}
              className="flex items-center gap-2 rounded-xl bg-blue-600 px-7 py-3 text-sm font-semibold text-white shadow-md shadow-blue-600/20 transition hover:bg-blue-700 disabled:opacity-50"
            >
              {isTriggeringBuild ? (
                <span>Launching AI Construction...</span>
              ) : (
                <>
                  <span>Create AI</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
