import { EvaluationDashboard } from "@/components/evaluation/EvaluationDashboard";

export default function EvaluationPage({ params }: { params: { modelId: string } }) {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-white">System Evaluation Benchmark</h1>
        <p className="text-xs text-zinc-400 mt-1">
          Detailed metrics and held-out validation report for model: <span className="font-mono text-zinc-300">{params.modelId}</span>
        </p>
      </div>
      <EvaluationDashboard modelId={params.modelId} />
    </div>
  );
}
