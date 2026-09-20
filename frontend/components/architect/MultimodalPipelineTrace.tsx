"use client";

import { PipelineTraceStep } from "@/lib/providers/types";
import {
  FileText,
  Image as ImageIcon,
  Mic,
  FileCode,
  Layers,
  ArrowDown,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  Cpu,
  Database,
  Binary
} from "lucide-react";

interface MultimodalPipelineTraceProps {
  trace?: PipelineTraceStep[];
  strategy?: string;
  modalities?: string[];
}

export function MultimodalPipelineTrace({ trace, strategy = "rag", modalities = ["text"] }: MultimodalPipelineTraceProps) {
  const activeModalities = modalities.length > 0 ? modalities : ["text"];

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-xs space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-blue-600" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
            Autonomous Multimodal Pipeline Trace
          </h3>
        </div>
        <span className="text-[11px] font-medium text-slate-500">
          Normalized Execution Flow
        </span>
      </div>

      {/* Visual Pipeline Flow */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3 relative">
        {/* Step 1: Input Modalities */}
        <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5 space-y-2 flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Stage 1 · Intake</span>
            <h4 className="text-xs font-bold text-slate-800 mt-1">Multi-Format Input</h4>
            <div className="flex flex-wrap gap-1 mt-2">
              {activeModalities.map((m, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 rounded-md bg-white px-2 py-0.5 text-[10px] font-bold text-slate-700 border border-slate-200/80 shadow-2xs"
                >
                  {m === "image" && <ImageIcon className="h-3 w-3 text-purple-600" />}
                  {m === "audio" && <Mic className="h-3 w-3 text-amber-600" />}
                  {m === "document" && <FileText className="h-3 w-3 text-blue-600" />}
                  {m === "text" && <FileCode className="h-3 w-3 text-emerald-600" />}
                  {m.toUpperCase()}
                </span>
              ))}
            </div>
          </div>
          <span className="text-[10px] text-slate-500 mt-2 block">Deterministic Router</span>
        </div>

        {/* Step 2: Feature & Content Extraction */}
        <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5 space-y-2 flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Stage 2 · Extraction</span>
            <h4 className="text-xs font-bold text-slate-800 mt-1">Modality Processors</h4>
            <p className="text-[10px] text-slate-600 leading-relaxed mt-1">
              PyMuPDF / Word XML / Vision OCR / Speech Transcriber
            </p>
          </div>
          <div className="flex items-center gap-1 text-[10px] text-emerald-700 font-semibold mt-2">
            <CheckCircle2 className="h-3 w-3" />
            <span>Zero-loss extraction</span>
          </div>
        </div>

        {/* Step 3: Normalized Representation */}
        <div className="rounded-xl border border-blue-200 bg-blue-50/40 p-3.5 space-y-2 flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider block">Stage 3 · Canonical</span>
            <h4 className="text-xs font-bold text-blue-950 mt-1">Normalized Record</h4>
            <p className="text-[10px] text-blue-900/80 leading-relaxed mt-1">
              Unified schema decoupling pipeline from raw file types.
            </p>
          </div>
          <div className="flex items-center gap-1 text-[10px] text-blue-700 font-mono font-bold mt-2">
            <Binary className="h-3 w-3" />
            <span>NormalizedInput</span>
          </div>
        </div>

        {/* Step 4: AI Architecture */}
        <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5 space-y-2 flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Stage 4 · Architecture</span>
            <h4 className="text-xs font-bold text-slate-800 mt-1 uppercase">
              {strategy === "rag" ? "RAG Vector Store" : strategy === "qlora" ? "QLoRA LoRA Adapter" : "Hybrid Architecture"}
            </h4>
            <p className="text-[10px] text-slate-600 leading-relaxed mt-1">
              {strategy === "rag" && "all-MiniLM-L6-v2 embeddings & cosine search."}
              {strategy === "qlora" && "4-bit NF4 behavioral alignment."}
              {strategy === "hybrid" && "Knowledge retrieval + persona tuning."}
            </p>
          </div>
          <span className="text-[10px] text-purple-700 font-bold mt-2">Autonomous Route</span>
        </div>

        {/* Step 5: Foundation Execution */}
        <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5 space-y-2 flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Stage 5 · Target AI</span>
            <h4 className="text-xs font-bold text-slate-800 mt-1">Qwen3-4B-Instruct</h4>
            <p className="text-[10px] text-slate-600 leading-relaxed mt-1">
              ChatML formatted response generation with citation grounding.
            </p>
          </div>
          <div className="flex items-center gap-1 text-[10px] text-emerald-700 font-semibold mt-2">
            <Sparkles className="h-3 w-3" />
            <span>Grounded Answer</span>
          </div>
        </div>
      </div>

      {/* Structured Trace Steps Breakdown if available */}
      {trace && trace.length > 0 && (
        <div className="mt-3 pt-3 border-t border-slate-100 space-y-2">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
            Detailed Trace Telemetry
          </span>
          <div className="space-y-1.5 text-xs">
            {trace.map((step, idx) => (
              <div
                key={idx}
                className="flex items-start justify-between gap-3 rounded-lg bg-slate-50 p-2.5 border border-slate-200/60"
              >
                <div className="flex items-start gap-2">
                  {step.status === "completed" ? (
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                  ) : step.status === "failed" ? (
                    <AlertCircle className="h-3.5 w-3.5 text-rose-600 shrink-0 mt-0.5" />
                  ) : (
                    <Clock className="h-3.5 w-3.5 text-slate-400 shrink-0 mt-0.5" />
                  )}
                  <div>
                    <span className="font-bold text-slate-800 text-[11px] block">{step.title}</span>
                    <p className="text-[11px] text-slate-600 font-normal leading-relaxed">{step.description}</p>
                  </div>
                </div>
                <span className="rounded bg-white px-2 py-0.5 text-[10px] font-mono text-slate-500 border border-slate-200 shrink-0">
                  {step.component}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
