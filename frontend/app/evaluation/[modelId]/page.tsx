import { EvaluationDashboard } from "@/components/evaluation/EvaluationDashboard";
import Link from "next/link";
import { ArrowLeft, Database, ShieldCheck } from "lucide-react";

export default function EvaluationPage({ params }: { params: { modelId: string } }) {
  return (
    <div className="space-y-6">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center justify-between">
        <Link
          href="/models"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Back to Model Registry</span>
        </Link>
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-[11px] font-bold text-emerald-700 border border-emerald-200 flex items-center gap-1">
          <ShieldCheck className="h-3.5 w-3.5" />
          Verified Quantitative Benchmark
        </span>
      </div>

      {/* Main Dashboard Component */}
      <EvaluationDashboard modelId={params.modelId} />
    </div>
  );
}
