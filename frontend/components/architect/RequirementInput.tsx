"use client";

import { useAppStore } from "@/lib/store";
import { Terminal } from "lucide-react";

const SUGGESTIONS = [
  { label: "Customer Support (RAG)", text: "Build a customer support AI that answers using our company policies and responds professionally." },
  { label: "Technical Docs (RAG)", text: "Create an AI that answers questions accurately using our uploaded technical handbook and product manual." },
  { label: "Persona Chat (QLoRA)", text: "Create a customer support bot that writes concise, polite responses following our support conversation transcripts." },
];

export function RequirementInput() {
  const { requirement, setRequirement } = useAppStore();

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
          <Terminal className="h-3.5 w-3.5 text-blue-600" />
          Step 1 · Define Objective
        </label>
        <span className="text-[11px] font-mono text-slate-400">{requirement.length} chars</span>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-1 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10 transition shadow-xs">
        <textarea
          value={requirement}
          onChange={(e) => setRequirement(e.target.value)}
          rows={3}
          placeholder="Describe what your AI should do in plain English (e.g., 'Answer questions using company handbook and maintain a polite support tone')..."
          className="w-full resize-none bg-transparent p-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none leading-relaxed"
        />
      </div>

      {/* Clean Template Pills */}
      <div className="flex flex-wrap items-center gap-2 pt-0.5">
        <span className="text-[11px] font-semibold text-slate-500">
          Templates:
        </span>
        {SUGGESTIONS.map((sug, idx) => (
          <button
            key={idx}
            onClick={() => setRequirement(sug.text)}
            className="rounded-lg border border-slate-200/80 bg-slate-50/80 px-2.5 py-1 text-left text-[11px] font-medium text-slate-700 transition hover:border-slate-300 hover:bg-white hover:text-slate-900 shadow-2xs"
          >
            {sug.label}
          </button>
        ))}
      </div>
    </div>
  );
}
