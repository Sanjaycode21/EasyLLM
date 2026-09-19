"use client";

import { RequirementInput } from "@/components/architect/RequirementInput";
import { FileDropzone } from "@/components/architect/FileDropzone";
import { DecisionCard } from "@/components/architect/DecisionCard";
import { PointerHighlight } from "@/components/ui/pointer-highlight";
import {
  ArrowRight,
  Zap,
  Sliders,
  Layers,
  FileText,
  MessageSquare,
  BookOpen,
  Cpu,
  Activity,
  CheckCircle2,
  Sparkles,
  ShieldCheck,
  Binary,
  Workflow
} from "lucide-react";
import { useAppStore } from "@/lib/store";
import Link from "next/link";

export default function HomePage() {
  const { setRequirement, setDatasetMetadata } = useAppStore();

  const loadSamplePreset = (type: "policy" | "support" | "technical") => {
    if (type === "policy") {
      setRequirement(
        "Build a company policy assistant that strictly answers employee questions using our HR and IT handbook."
      );
    } else if (type === "support") {
      setRequirement(
        "Create a customer support AI that mimics the concise, empathetic tone of our senior support team."
      );
    } else {
      setRequirement(
        "Construct an AI that grounds answers in product documentation while adopting our professional brand persona."
      );
    }
    window.scrollTo({ top: 350, behavior: "smooth" });
  };

  return (
    <div className="space-y-12 pb-20">
      {/* Hero Section */}
      <div className="text-center max-w-3xl mx-auto space-y-4 pt-2 sm:pt-4">
        <p className="text-[11px] uppercase tracking-widest font-bold text-slate-500">
          AUTONOMOUS NEURAL ARCHITECT & TRAINING PLATFORM
        </p>
        
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 leading-[1.12]">
          Publish{" "}
          <PointerHighlight rectangleClassName="border-blue-600/70 bg-blue-500/10 rounded-lg">
            <span>customized AI</span>
          </PointerHighlight>{" "}
          in 20 seconds
        </h1>
        
        <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
          Intelligent pipeline decision for enterprise tasks. Describe your goal, upload your dataset or document, and EasyLLM autonomously constructs the optimal RAG or fine-tuned model.
        </p>

        {/* CTA group */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            onClick={() => window.scrollTo({ top: 350, behavior: "smooth" })}
            className="w-full sm:w-auto rounded-full bg-blue-600 px-6 py-2.5 text-xs font-semibold text-white shadow-md shadow-blue-500/20 hover:bg-blue-700 transition"
          >
            Start free build
          </button>
          
          <button
            onClick={() => loadSamplePreset("policy")}
            className="flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800 transition px-3 py-2"
          >
            <span>Load sample workflow</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Microcopy under CTA */}
        <p className="text-xs text-slate-400 font-medium">
          Supports DOCX, PDF, JSONL, CSV & TXT · Real GPU/CPU pipeline execution
        </p>
      </div>

      {/* Modern High-Density Studio Workspace (Two-Column Layout) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-6xl mx-auto items-start">
        {/* Left Column: Primary Build Studio (7 cols) */}
        <div className="lg:col-span-7 rounded-2xl border border-slate-200/90 bg-white shadow-xl shadow-slate-100 overflow-hidden">
          {/* Workbench Header */}
          <div className="flex items-center justify-between border-b border-slate-200/80 bg-slate-50/60 px-5 py-3 text-xs text-slate-600">
            <div className="flex items-center gap-2 font-medium">
              <span className="font-bold text-slate-900">Studio Workbench</span>
              <span className="text-slate-300">·</span>
              <span>Autonomous Decision Engine</span>
            </div>
            <span className="rounded-md bg-white px-2 py-0.5 font-mono text-[10px] font-semibold text-slate-700 border border-slate-200 shadow-2xs">
              4-Bit / FP32
            </span>
          </div>

          {/* Workbench Body */}
          <div className="p-5 sm:p-6 space-y-5">
            <RequirementInput />
            <div className="border-t border-slate-100 pt-4">
              <FileDropzone />
            </div>
            <div className="border-t border-slate-100 pt-4">
              <DecisionCard />
            </div>
          </div>
        </div>

        {/* Right Column: Live Telemetry & Pipeline Intelligence (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Architecture Routing Intelligence Card */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-3.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
                <Activity className="h-3.5 w-3.5 text-blue-600" />
                Autonomous Routing Engine
              </span>
              <span className="rounded-full bg-blue-50 px-2 py-0.5 text-[10px] font-bold text-blue-700 border border-blue-200">
                Active
              </span>
            </div>

            <p className="text-xs text-slate-500 leading-relaxed">
              EasyLLM inspects task requirements, document structures, and token formats to automatically route to the highest performing pipeline:
            </p>

            <div className="space-y-2 text-xs">
              <div className="flex items-start gap-2.5 rounded-xl border border-blue-100 bg-blue-50/40 p-2.5">
                <Zap className="h-4 w-4 text-blue-600 mt-0.5 shrink-0" />
                <div>
                  <span className="font-bold text-slate-900 block">Path A · RAG Knowledge</span>
                  <span className="text-[11px] text-slate-500">Selected for policies, manuals, handbooks & documentation.</span>
                </div>
              </div>

              <div className="flex items-start gap-2.5 rounded-xl border border-purple-100 bg-purple-50/40 p-2.5">
                <Sliders className="h-4 w-4 text-purple-600 mt-0.5 shrink-0" />
                <div>
                  <span className="font-bold text-slate-900 block">Path B · QLoRA Fine-Tuning</span>
                  <span className="text-[11px] text-slate-500">Selected for conversational tone, persona & style adaptation.</span>
                </div>
              </div>

              <div className="flex items-start gap-2.5 rounded-xl border border-amber-100 bg-amber-50/40 p-2.5">
                <Layers className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
                <div>
                  <span className="font-bold text-slate-900 block">Path C · Hybrid</span>
                  <span className="text-[11px] text-slate-500">Pairs fine-tuned adapter responses with real-time vector retrieval.</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick-Start Sample Presets */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
              <Workflow className="h-3.5 w-3.5 text-blue-600" />
              Quick-Start Presets
            </span>
            <div className="grid grid-cols-1 gap-2 text-xs">
              <button
                onClick={() => loadSamplePreset("policy")}
                className="flex items-center justify-between rounded-xl border border-slate-200/80 bg-slate-50/60 p-2.5 text-left transition hover:border-blue-300 hover:bg-blue-50/40 group"
              >
                <div className="flex items-center gap-2.5">
                  <FileText className="h-4 w-4 text-blue-600" />
                  <div>
                    <span className="font-bold text-slate-800 block text-xs group-hover:text-blue-600">Enterprise Policy Assistant</span>
                    <span className="text-[10px] text-slate-400">RAG · DOCX / PDF</span>
                  </div>
                </div>
                <ArrowRight className="h-3.5 w-3.5 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition" />
              </button>

              <button
                onClick={() => loadSamplePreset("support")}
                className="flex items-center justify-between rounded-xl border border-slate-200/80 bg-slate-50/60 p-2.5 text-left transition hover:border-purple-300 hover:bg-purple-50/40 group"
              >
                <div className="flex items-center gap-2.5">
                  <MessageSquare className="h-4 w-4 text-purple-600" />
                  <div>
                    <span className="font-bold text-slate-800 block text-xs group-hover:text-purple-600">Support Tone Fine-Tuning</span>
                    <span className="text-[10px] text-slate-400">QLoRA · JSONL / CSV</span>
                  </div>
                </div>
                <ArrowRight className="h-3.5 w-3.5 text-slate-400 group-hover:text-purple-600 group-hover:translate-x-0.5 transition" />
              </button>

              <button
                onClick={() => loadSamplePreset("technical")}
                className="flex items-center justify-between rounded-xl border border-slate-200/80 bg-slate-50/60 p-2.5 text-left transition hover:border-amber-300 hover:bg-amber-50/40 group"
              >
                <div className="flex items-center gap-2.5">
                  <BookOpen className="h-4 w-4 text-amber-600" />
                  <div>
                    <span className="font-bold text-slate-800 block text-xs group-hover:text-amber-600">Grounded Persona Engine</span>
                    <span className="text-[10px] text-slate-400">Hybrid · Knowledge + Style</span>
                  </div>
                </div>
                <ArrowRight className="h-3.5 w-3.5 text-slate-400 group-hover:text-amber-600 group-hover:translate-x-0.5 transition" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* End-to-End Pipeline Visualization Flow */}
      <div className="max-w-6xl mx-auto rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Binary className="h-5 w-5 text-blue-600" />
              How EasyLLM Automates Your Model Architecture
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Zero manual hyperparameter tuning. From plain English description to a verified, deployed AI.
            </p>
          </div>
          <Link
            href="/models"
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1 self-start sm:self-auto"
          >
            View Model Registry <ArrowRight className="h-3 w-3" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="rounded-xl border border-slate-200/80 bg-slate-50/50 p-4 space-y-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-100 text-blue-700 font-bold text-xs">
              01
            </span>
            <h4 className="font-bold text-slate-900 text-sm">Objective & Ingestion</h4>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Extracts text, paragraphs, and conversation turns from Word (.docx), PDF, JSONL, or CSV documents with zero mock data.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200/80 bg-slate-50/50 p-4 space-y-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-purple-100 text-purple-700 font-bold text-xs">
              02
            </span>
            <h4 className="font-bold text-slate-900 text-sm">Autonomous Analysis</h4>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Decision engine determines knowledge density vs persona needs and selects RAG, QLoRA, or Hybrid with memory budgeting.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200/80 bg-slate-50/50 p-4 space-y-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700 font-bold text-xs">
              03
            </span>
            <h4 className="font-bold text-slate-900 text-sm">Real Execution</h4>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Executes parameter-efficient PyTorch LoRA fine-tuning and dense neural vector embedding with live streaming logs.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200/80 bg-slate-50/50 p-4 space-y-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-100 text-amber-700 font-bold text-xs">
              04
            </span>
            <h4 className="font-bold text-slate-900 text-sm">Benchmark & Chat</h4>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Generates side-by-side baseline comparisons, metric evaluations, source citations, and interactive chat playgrounds.
            </p>
          </div>
        </div>
      </div>

      {/* Architecture Comparison Specs Matrix */}
      <div className="max-w-6xl mx-auto rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm space-y-5">
        <h3 className="text-base font-bold text-slate-900">
          Architecture Capability Matrix
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="border-b border-slate-200 text-[11px] uppercase font-bold text-slate-400 bg-slate-50/50">
              <tr>
                <th className="py-3 px-4">Pipeline</th>
                <th className="py-3 px-4">Core Mechanism</th>
                <th className="py-3 px-4">Target Use Case</th>
                <th className="py-3 px-4">Build Duration</th>
                <th className="py-3 px-4">Hardware Footprint</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              <tr className="hover:bg-slate-50/60 transition">
                <td className="py-3.5 px-4 font-bold text-blue-700">Path A · RAG</td>
                <td className="py-3.5 px-4 text-slate-600 font-medium">Dense Vector Cosine Indexing</td>
                <td className="py-3.5 px-4 text-slate-900">Company Handbooks, Tech Docs, PDFs</td>
                <td className="py-3.5 px-4 font-mono text-emerald-600 font-bold">~3 to 10 seconds</td>
                <td className="py-3.5 px-4 text-slate-500 font-mono">CPU or GPU (Lightweight)</td>
              </tr>
              <tr className="hover:bg-slate-50/60 transition">
                <td className="py-3.5 px-4 font-bold text-purple-700">Path B · QLoRA</td>
                <td className="py-3.5 px-4 text-slate-600 font-medium">4-bit Low-Rank Adapter Tuning</td>
                <td className="py-3.5 px-4 text-slate-900">Support Persona, Style & Formatting</td>
                <td className="py-3.5 px-4 font-mono text-blue-600 font-bold">~15 to 45 seconds</td>
                <td className="py-3.5 px-4 text-slate-500 font-mono">Quantized VRAM / Multi-core CPU</td>
              </tr>
              <tr className="hover:bg-slate-50/60 transition">
                <td className="py-3.5 px-4 font-bold text-amber-700">Path C · Hybrid</td>
                <td className="py-3.5 px-4 text-slate-600 font-medium">QLoRA Adapter + Vector Store Retrieval</td>
                <td className="py-3.5 px-4 text-slate-900">Domain Persona with Strict Grounding</td>
                <td className="py-3.5 px-4 font-mono text-purple-600 font-bold">~20 to 60 seconds</td>
                <td className="py-3.5 px-4 text-slate-500 font-mono">Balanced Vector + Adapter</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
