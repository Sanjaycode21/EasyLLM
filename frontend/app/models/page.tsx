"use client";

import { useEffect, useState } from "react";
import { RegisteredModel } from "@/lib/providers/types";
import { getProvider } from "@/lib/providers";
import { useAppStore } from "@/lib/store";
import {
  Database,
  MessageSquare,
  BarChart3,
  Download,
  Loader2,
  PlusCircle,
  ShieldCheck,
  TrendingUp,
  Cpu,
  FileText,
  Clock,
  ArrowRight
} from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

export default function ModelsPage() {
  const { useLocalProvider } = useAppStore();
  const [models, setModels] = useState<RegisteredModel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadModels() {
      try {
        const provider = getProvider(useLocalProvider);
        const data = await provider.getModels();
        setModels(data);
      } catch (err: any) {
        console.error("Failed to load models:", err);
      } finally {
        setLoading(false);
      }
    }
    loadModels();
  }, [useLocalProvider]);

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Top Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-[10px] font-bold uppercase text-blue-700 border border-blue-200">
              Registry & Benchmarks
            </span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2 mt-1">
            <Database className="h-6 w-6 text-blue-600" />
            AI Model Registry & Quantitative Evaluations
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Active neural pipelines with held-out evaluation benchmarks, semantic similarity scores, and inference playgrounds.
          </p>
        </div>
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-full bg-blue-600 px-5 py-2.5 text-xs font-semibold text-white shadow-md shadow-blue-500/20 hover:bg-blue-700 transition self-start sm:self-auto"
        >
          <PlusCircle className="h-4 w-4" />
          Create New AI
        </Link>
      </div>

      {loading ? (
        <div className="flex h-64 items-center justify-center gap-3 bg-white rounded-2xl border border-slate-200 p-8">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <p className="text-sm font-medium text-slate-500">Loading registered AI systems...</p>
        </div>
      ) : models.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center shadow-sm max-w-xl mx-auto space-y-3">
          <Database className="mx-auto h-12 w-12 text-slate-400" />
          <h3 className="text-base font-bold text-slate-800">No Models Registered Yet</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Use the Architect workbench to build your first RAG knowledge assistant, QLoRA fine-tuned model, or Hybrid pipeline.
          </p>
          <div className="pt-2">
            <Link
              href="/"
              className="inline-flex items-center gap-2 rounded-full bg-blue-600 px-6 py-2.5 text-xs font-semibold text-white hover:bg-blue-700 transition shadow-sm"
            >
              Start AI Build
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {models.map((model) => {
            const evalReport = model.evaluation_report;
            const evalLegacy = model.evaluation;
            const score = evalReport?.overall_customized_score || evalLegacy?.overall_custom_score || null;
            const baseScore = evalReport?.overall_baseline_score || evalLegacy?.overall_base_score || null;
            const delta = score !== null && baseScore !== null ? Math.round((score - baseScore) * 10) / 10 : null;

            return (
              <div
                key={model.id}
                className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 hover:border-slate-300 hover:shadow-md transition shadow-sm space-y-5"
              >
                <div className="space-y-4">
                  {/* Card Header & Architecture Tag */}
                  <div className="flex items-center justify-between">
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                        model.architecture === "rag"
                          ? "bg-blue-50 text-blue-700 border border-blue-200"
                          : model.architecture === "qlora"
                          ? "bg-purple-50 text-purple-700 border border-purple-200"
                          : "bg-amber-50 text-amber-700 border border-amber-200"
                      }`}
                    >
                      {model.architecture === "rag" ? "RAG Knowledge" : model.architecture === "qlora" ? "QLoRA Tuning" : "Hybrid Engine"}
                    </span>
                    <span className="text-[11px] font-mono text-slate-400">{model.id}</span>
                  </div>

                  {/* Title & Metadata */}
                  <div>
                    <h3 className="text-base font-bold text-slate-900 leading-snug">{model.name}</h3>
                    <p className="text-xs text-slate-500 mt-1 flex items-center gap-1.5">
                      <Cpu className="h-3 w-3 text-slate-400" />
                      <span>{model.base_model}</span>
                    </p>
                  </div>

                  {/* Highlighted Evaluation Benchmark Card */}
                  {score !== null ? (
                    <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-3.5 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase font-extrabold tracking-wider text-emerald-900 flex items-center gap-1">
                          <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
                          Held-Out Benchmark
                        </span>
                        {delta !== null && (
                          <span className={`text-[11px] font-mono font-bold ${delta >= 0 ? "text-emerald-700" : "text-rose-700"}`}>
                            {delta >= 0 ? "+" : ""}{delta} pp
                          </span>
                        )}
                      </div>
                      <div className="flex items-baseline justify-between pt-1">
                        <div className="text-xs text-slate-600">
                          Baseline: <span className="font-mono font-semibold text-slate-700">{baseScore}%</span>
                        </div>
                        <div className="text-xs text-emerald-950 font-bold">
                          Custom: <span className="font-mono text-base font-black text-emerald-700">{score}%</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-500 flex items-center gap-2">
                      <BarChart3 className="h-4 w-4 text-slate-400" />
                      <span>Evaluation generated during build</span>
                    </div>
                  )}

                  {/* Specs List */}
                  <div className="space-y-1.5 text-xs text-slate-600 pt-1">
                    {model.dataset_name && (
                      <div className="flex justify-between">
                        <span className="text-slate-400 flex items-center gap-1">
                          <FileText className="h-3 w-3" /> Dataset:
                        </span>
                        <span className="text-slate-800 font-medium truncate max-w-[140px]">{model.dataset_name}</span>
                      </div>
                    )}
                    {model.training_time_seconds && (
                      <div className="flex justify-between">
                        <span className="text-slate-400 flex items-center gap-1">
                          <Clock className="h-3 w-3" /> Build Time:
                        </span>
                        <span className="font-mono text-slate-800 font-semibold">{model.training_time_seconds}s</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Card Actions */}
                <div className="pt-4 border-t border-slate-100 flex items-center gap-2">
                  <Link
                    href={`/playground/${model.id}`}
                    className="flex-1 flex items-center justify-center gap-1.5 rounded-full bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 transition shadow-2xs"
                  >
                    <MessageSquare className="h-3.5 w-3.5" />
                    Chat
                  </Link>

                  <Link
                    href={`/evaluation/${model.id}`}
                    className="flex items-center justify-center gap-1 rounded-full border border-emerald-300 bg-emerald-50 px-3.5 py-2 text-xs font-bold text-emerald-800 hover:bg-emerald-100 transition shadow-2xs"
                    title="View Comprehensive Evaluation Benchmark"
                  >
                    <BarChart3 className="h-3.5 w-3.5 text-emerald-600" />
                    <span>Eval</span>
                  </Link>

                  {model.adapter_path && (
                    <button
                      onClick={() => toast.success(`Adapter located at: ${model.adapter_path}`)}
                      title="Model Adapter Artifact"
                      className="flex items-center justify-center rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition"
                    >
                      <Download className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
