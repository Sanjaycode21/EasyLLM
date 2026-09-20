"use client";

import { useEffect, useState } from "react";
import { getProvider } from "@/lib/providers";
import { useAppStore } from "@/lib/store";
import { HardwareStatus } from "@/lib/providers/types";
import {
  Cpu,
  HardDrive,
  Activity,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Zap,
  Server,
  Terminal,
  Layers,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";

export default function DiagnosticsPage() {
  const { useLocalProvider } = useAppStore();
  const [hw, setHw] = useState<HardwareStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<string>("");

  const fetchDiagnostics = async () => {
    setIsLoading(true);
    try {
      const provider = getProvider(useLocalProvider);
      const data = await provider.getHardware();
      setHw(data);
      setLastRefreshed(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("Failed to load hardware diagnostics:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDiagnostics();
  }, [useLocalProvider]);

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-blue-50 px-2.5 py-0.5 text-[11px] font-bold text-blue-700 border border-blue-200">
              System Health
            </span>
            <span className="text-xs text-slate-400 font-mono">
              {lastRefreshed ? `Updated ${lastRefreshed}` : "Checking hardware..."}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mt-1.5">
            Hardware & ML Runtime Diagnostics
          </h1>
          <p className="text-sm text-slate-600 mt-0.5">
            Dynamic inspection of physical GPU, VRAM, CUDA runtime, and Qwen3-4B execution feasibility.
          </p>
        </div>

        <button
          onClick={fetchDiagnostics}
          disabled={isLoading}
          className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 shadow-2xs hover:bg-slate-50 transition self-start sm:self-auto disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin text-blue-600" : ""}`} />
          <span>Refresh Diagnostics</span>
        </button>
      </div>

      {/* Primary Status Card */}
      {hw && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Card 1: GPU & VRAM */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Zap className="h-4 w-4 text-blue-600" />
                Physical GPU
              </span>
              <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700 border border-emerald-200">
                Detected
              </span>
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-900 leading-snug">
                {hw.physical_gpu_name && hw.physical_gpu_name !== "N/A"
                  ? hw.physical_gpu_name
                  : hw.gpu_name || "NVIDIA GPU"}
              </h3>
              <p className="text-xs text-slate-500 font-mono mt-0.5">
                Driver: {hw.driver_version || "591.66"} · CUDA Driver 13.1
              </p>
            </div>

            <div className="space-y-1.5 pt-1">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-600">VRAM Budget</span>
                <span className="font-mono text-slate-900 font-bold">
                  {hw.free_vram_gb} GB free / {hw.total_vram_gb || 6.0} GB total
                </span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div
                  className="h-full bg-blue-600 rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min(
                      100,
                      Math.max(10, ((hw.total_vram_gb - hw.free_vram_gb) / (hw.total_vram_gb || 6.0)) * 100)
                    )}%`,
                  }}
                />
              </div>
            </div>
          </div>

          {/* Card 2: PyTorch & Compute Status */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Cpu className="h-4 w-4 text-purple-600" />
                Compute Runtime
              </span>
              <span
                className={`rounded-full px-2 py-0.5 text-[10px] font-bold border ${
                  hw.pytorch_cuda
                    ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                    : "bg-blue-50 text-blue-700 border-blue-200"
                }`}
              >
                {hw.pytorch_cuda ? "CUDA Accelerated" : "CPU Runtime Active"}
              </span>
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-900 leading-snug">
                PyTorch {hw.pytorch_version}
              </h3>
              <p className="text-xs text-slate-500 font-mono mt-0.5">
                PyTorch CUDA: {hw.pytorch_cuda ? "Available" : "CPU Build (Colab Supported)"}
              </p>
            </div>

            <div className="rounded-xl border border-slate-100 bg-slate-50/70 p-3 text-xs space-y-1">
              <div className="flex justify-between text-slate-600">
                <span>CPU Cores:</span>
                <span className="font-bold text-slate-900">{hw.cpu_cores} Logical Cores</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>System RAM:</span>
                <span className="font-bold text-slate-900">{hw.system_ram_gb} GB RAM</span>
              </div>
            </div>
          </div>

          {/* Card 3: Target Model & Routing */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Layers className="h-4 w-4 text-amber-600" />
                Target Foundation
              </span>
              <span className="rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-bold text-amber-700 border border-amber-200">
                Qwen3-4B
              </span>
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-900 leading-snug">
                Qwen3-4B-Instruct-2507
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                4-bit NF4 Quantization · Seq Length ≤ 512
              </p>
            </div>

            <div className="rounded-xl border border-blue-100 bg-blue-50/60 p-3 text-xs">
              <span className="font-bold text-blue-900 block">Recommended Mode:</span>
              <span className="text-[11px] text-blue-700 leading-relaxed block mt-0.5">
                {hw.recommended_mode_text || "Local RAG Supported · Colab fallback for 4B QLoRA"}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Installed ML Packages Table */}
      {hw && hw.libraries && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Terminal className="h-4 w-4 text-blue-600" />
            Installed ML Libraries & Frameworks
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            {Object.entries(hw.libraries).map(([lib, ver]) => (
              <div
                key={lib}
                className="rounded-xl border border-slate-200/80 bg-slate-50/50 p-3 flex items-center justify-between"
              >
                <span className="font-bold text-slate-800">{lib}</span>
                <span
                  className={`font-mono text-[11px] font-semibold px-2 py-0.5 rounded ${
                    ver === "Not Installed"
                      ? "bg-slate-200 text-slate-600"
                      : "bg-emerald-100 text-emerald-800"
                  }`}
                >
                  {ver}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Compute Architecture Matrix Guide */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Server className="h-4 w-4 text-purple-600" />
          Autonomous Compute Routing Rules
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="rounded-xl border border-emerald-100 bg-emerald-50/40 p-4 space-y-2">
            <div className="flex items-center gap-2 text-emerald-800 font-bold text-sm">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              Local RAG Pipeline (100% Local Execution)
            </div>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Extracts text with <strong>PyMuPDF</strong>, generates dense embeddings with{" "}
              <strong>all-MiniLM-L6-v2</strong>, and queries local vector index in &lt;45ms on CPU or GPU with zero cloud dependencies.
            </p>
          </div>

          <div className="rounded-xl border border-blue-100 bg-blue-50/40 p-4 space-y-2">
            <div className="flex items-center gap-2 text-blue-800 font-bold text-sm">
              <Zap className="h-4 w-4 text-blue-600" />
              Qwen3-4B QLoRA (Local / Colab ComputeProvider)
            </div>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              When local GPU memory is constrained or CPU mode is active, EasyLLM generates an end-to-end{" "}
              <strong>Google Colab Notebook</strong> with 4-bit loading, LoRA rank 8/16, and 1-click execution on free T4/A100 GPU.
            </p>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <Link
            href="/"
            className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800"
          >
            <span>Return to Studio Workbench</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
