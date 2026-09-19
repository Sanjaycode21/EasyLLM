"use client";

import { useState, useEffect } from "react";
import { ModelEvaluation } from "@/lib/providers/types";
import { getProvider } from "@/lib/providers";
import { useAppStore } from "@/lib/store";
import { BarChart3, TrendingUp, ShieldCheck, ArrowRight, Sparkles } from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";
import Link from "next/link";
import LatticeLoader from "@/components/ui/LatticeLoader";

export function EvaluationDashboard({ modelId }: { modelId: string }) {
  const { useLocalProvider } = useAppStore();
  const [evaluation, setEvaluation] = useState<ModelEvaluation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadEval() {
      try {
        const provider = getProvider(useLocalProvider);
        const data = await provider.getEvaluation(modelId);
        setEvaluation(data);
      } catch (err: any) {
        setError(err.message || "Evaluation pending or not found.");
      } finally {
        setLoading(false);
      }
    }
    loadEval();
  }, [modelId, useLocalProvider]);

  if (loading) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-3 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6">
        <LatticeLoader
          status="working"
          label="Synthesizing benchmark evaluation metrics"
          pattern="orbit"
          grid={3}
          shape="round"
          cellSize={8}
          gap={3}
          fontSize={15}
          color="#2563eb"
          showTimer
        />
        <p className="text-xs font-medium text-slate-400">Comparing base foundation model vs fine-tuned adapter...</p>
      </div>
    );
  }

  if (error || !evaluation) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <p className="text-sm font-semibold text-amber-700">{error || "Evaluation pending"}</p>
        <p className="mt-1 text-xs text-slate-500">
          Evaluation report is generated automatically when the build finishes.
        </p>
      </div>
    );
  }

  const chartData = evaluation.metrics.map((m) => ({
    name: m.name.split(" ")[0] + " " + (m.name.split(" ")[1] || ""),
    Base: m.base_score,
    Custom: m.custom_score,
  }));

  const overallDelta = Math.round((evaluation.overall_custom_score - evaluation.overall_base_score) * 10) / 10;

  return (
    <div className="space-y-6">
      {/* Top summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <span className="text-xs text-slate-500 font-medium block">Baseline Model Score</span>
          <span className="text-3xl font-extrabold text-slate-700 mt-1 block">
            {evaluation.overall_base_score}%
          </span>
          <span className="text-[11px] text-slate-400 font-medium">Unadapted foundation baseline</span>
        </div>

        <div className="rounded-2xl border border-emerald-200 bg-emerald-50/40 p-5 shadow-sm">
          <span className="text-xs text-emerald-800 font-semibold block">Customized System Score</span>
          <span className="text-3xl font-extrabold text-emerald-700 mt-1 block">
            {evaluation.overall_custom_score}%
          </span>
          <span className="text-[11px] text-emerald-700/80 font-medium">Fine-tuned & Grounded system</span>
        </div>

        <div className="rounded-2xl border border-blue-200 bg-blue-50/40 p-5 shadow-sm">
          <span className="text-xs text-blue-800 font-semibold block">Overall Improvement</span>
          <div className="flex items-center gap-1.5 mt-1">
            <TrendingUp className="h-6 w-6 text-blue-600" />
            <span className="text-3xl font-extrabold text-blue-700">+{overallDelta}%</span>
          </div>
          <span className="text-[11px] text-blue-700/80 font-medium">Across evaluated test sets</span>
        </div>
      </div>

      {/* Metrics Chart Comparison */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">
              Comparative Benchmark (Base vs Customized)
            </h3>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
              <YAxis stroke="#94a3b8" fontSize={11} domain={[0, 100]} />
              <Tooltip
                contentStyle={{ backgroundColor: "#ffffff", borderColor: "#e2e8f0", fontSize: "12px", borderRadius: "8px", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
              />
              <Legend wrapperStyle={{ fontSize: "12px" }} />
              <Bar dataKey="Base" fill="#94a3b8" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Custom" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Metrics Table */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 mb-3">Metric Breakdown</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="border-b border-slate-200 text-[11px] uppercase font-bold text-slate-400 bg-slate-50/50">
              <tr>
                <th className="py-2.5 px-3">Metric</th>
                <th className="py-2.5 px-3">Base Score</th>
                <th className="py-2.5 px-3">Custom Score</th>
                <th className="py-2.5 px-3">Improvement</th>
                <th className="py-2.5 px-3">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {evaluation.metrics.map((m, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60 transition">
                  <td className="py-3 px-3 font-semibold text-slate-900">{m.name}</td>
                  <td className="py-3 px-3 text-slate-500 font-mono font-medium">{m.base_score}%</td>
                  <td className="py-3 px-3 text-emerald-700 font-mono font-bold">{m.custom_score}%</td>
                  <td className="py-3 px-3 text-blue-700 font-mono font-bold">+{m.improvement}%</td>
                  <td className="py-3 px-3 text-slate-500 text-[11px]">{m.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Side-by-Side Sample Generation Comparisons */}
      {evaluation.sample_comparisons.length > 0 && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900">
            Side-by-Side Held-Out Output Inspection
          </h3>
          <div className="space-y-4">
            {evaluation.sample_comparisons.map((samp, idx) => (
              <div key={idx} className="rounded-xl border border-slate-200 bg-slate-50/40 p-4 space-y-3">
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-slate-200 px-2.5 py-0.5 text-[10px] font-mono font-bold text-slate-700">
                    Evaluation Prompt {idx + 1}
                  </span>
                  <span className="text-xs font-bold text-slate-900">{samp.prompt}</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  <div className="rounded-xl bg-white p-3.5 border border-slate-200 shadow-2xs">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                      Base Model Output (Baseline)
                    </span>
                    <p className="text-slate-600 text-[11px] leading-relaxed">{samp.base_model_output}</p>
                  </div>

                  <div className="rounded-xl bg-emerald-50/50 p-3.5 border border-emerald-200 shadow-2xs">
                    <span className="text-[10px] uppercase font-bold text-emerald-800 block mb-1 flex items-center gap-1">
                      <Sparkles className="h-3 w-3" /> Customized System Output
                    </span>
                    <p className="text-emerald-950 text-[11px] leading-relaxed font-medium">
                      {samp.custom_model_output}
                    </p>
                  </div>
                </div>

                <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-200/60 flex items-center gap-1.5">
                  <ShieldCheck className="h-3.5 w-3.5 text-blue-600" />
                  {samp.evaluation_notes}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action CTA */}
      <div className="flex justify-end gap-3 pt-2">
        <Link
          href={`/playground/${modelId}`}
          className="flex items-center gap-2 rounded-full bg-blue-600 px-6 py-2.5 text-xs font-semibold text-white shadow-md shadow-blue-500/20 hover:bg-blue-700 transition"
        >
          <span>Chat with This System</span>
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
