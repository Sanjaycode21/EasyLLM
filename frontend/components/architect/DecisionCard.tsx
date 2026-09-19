"use client";

import { useAppStore } from "@/lib/store";
import { Sparkles, ArrowRight, BookOpen, Sliders, Layers, CheckCircle2 } from "lucide-react";
import { useState } from "react";
import { getProvider } from "@/lib/providers";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export function DecisionCard() {
  const router = useRouter();
  const {
    requirement,
    analysis,
    setAnalysis,
    isAnalyzing,
    isBuilding,
    setIsBuilding,
    setActiveJob,
    useLocalProvider,
  } = useAppStore();

  const [isTriggeringBuild, setIsTriggeringBuild] = useState(false);

  const handleAnalyze = async () => {
    if (!requirement.trim()) {
      toast.error("Please enter what your AI should do.");
      return;
    }

    try {
      const provider = getProvider(useLocalProvider);
      const res = await provider.analyzeRequirement(requirement);
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
        base_model_id: analysis.suggested_base_model,
        epochs: 2,
        lora_rank: 8,
        lora_alpha: 16,
      });

      setActiveJob(job);
      toast.success(`Launched build job: ${job.job_id}`);
      router.push(`/build/${job.job_id}`);
    } catch (err: any) {
      toast.error(err.message || "Failed to launch build pipeline");
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
          className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 text-xs font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-40"
        >
          {isAnalyzing ? (
            <span className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 animate-spin" />
              Autonomous Engine Analyzing Requirement...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Analyze Requirement & Determine Architecture
            </span>
          )}
        </button>
      ) : (
        /* Architecture Decision Display */
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3.5">
            <div>
              <div className="flex items-center gap-2">
                <span className="rounded-md bg-blue-50 px-2.5 py-0.5 text-[11px] font-bold text-blue-700 border border-blue-200/60">
                  Architect Decision
                </span>
                <span className="text-[11px] text-slate-500 font-medium">
                  Confidence: <span className="text-emerald-700 font-bold">{Math.round(analysis.confidence * 100)}%</span>
                </span>
              </div>
              <h3 className="mt-1.5 text-base font-bold text-slate-900 flex items-center gap-2">
                {analysis.recommended_strategy === "rag" && (
                  <>
                    <BookOpen className="h-4 w-4 text-blue-600" />
                    Path A · Retrieval-Augmented Generation (RAG)
                  </>
                )}
                {analysis.recommended_strategy === "qlora" && (
                  <>
                    <Sliders className="h-4 w-4 text-purple-600" />
                    Path B · QLoRA Fine-Tuning
                  </>
                )}
                {analysis.recommended_strategy === "hybrid" && (
                  <>
                    <Layers className="h-4 w-4 text-amber-600" />
                    Path C · Hybrid (QLoRA + RAG)
                  </>
                )}
              </h3>
            </div>

            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-[11px] font-semibold text-slate-700 hover:bg-slate-100 transition"
            >
              Re-Analyze
            </button>
          </div>

          {/* Rationale */}
          <div className="rounded-lg bg-slate-50/70 p-3 border border-slate-200/60 text-xs">
            <span className="font-bold text-slate-600 block text-[11px] mb-0.5">Strategy Rationale:</span>
            <p className="text-slate-800 leading-relaxed font-normal">{analysis.reason}</p>
          </div>

          {/* Configuration details */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
            <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-200/60">
              <span className="text-slate-400 block">Selected Foundation Model:</span>
              <span className="font-mono text-slate-900 font-bold">{analysis.suggested_base_model}</span>
            </div>
            <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-200/60">
              <span className="text-slate-400 block">Identified Domain:</span>
              <span className="text-blue-700 font-bold capitalize">{analysis.task.replace("_", " ")}</span>
            </div>
          </div>

          {/* Real Build Trigger Button */}
          <div className="pt-2 flex items-center justify-end">
            <button
              onClick={handleBuild}
              disabled={isTriggeringBuild || isBuilding}
              className="flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-2.5 text-xs font-semibold text-white shadow-xs transition hover:bg-blue-700 disabled:opacity-50"
            >
              {isTriggeringBuild ? (
                <span>Launching Real Pipeline...</span>
              ) : (
                <>
                  <span>Execute Build ({analysis.recommended_strategy.toUpperCase()})</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
