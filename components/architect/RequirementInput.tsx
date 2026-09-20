"use client";

import { useAppStore } from "@/lib/store";
import { Sparkles, HelpCircle } from "lucide-react";

const SUGGESTIONS = [
  {
    label: "Company Policy Assistant",
    text: "Build an enterprise policy assistant that strictly answers employee questions using our HR and IT handbook with exact citations.",
  },
  {
    label: "Customer Support Persona",
    text: "Create a customer support AI that mimics the concise, empathetic tone of our senior support team from our chat transcripts.",
  },
  {
    label: "Grounded Technical Expert",
    text: "Construct a technical expert AI that grounds answers in product documentation while adopting a professional engineering tone.",
  },
];

export function RequirementInput() {
  const { requirement, setRequirement } = useAppStore();

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-blue-600" />
          What do you want your AI to do?
        </label>
        <span className="text-[11px] font-mono text-slate-400">{requirement.length} chars</span>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-1 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10 transition shadow-2xs">
        <textarea
          value={requirement}
          onChange={(e) => setRequirement(e.target.value)}
          rows={3}
          placeholder="Describe your goal in plain English (e.g., 'Answer questions using company handbook with citations and maintain a polite support tone')..."
          className="w-full resize-none bg-transparent p-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none leading-relaxed"
        />
      </div>

      {/* Clean Template Pills */}
      <div className="flex flex-wrap items-center gap-2 pt-0.5">
        <span className="text-[11px] font-semibold text-slate-500">
          Examples:
        </span>
        {SUGGESTIONS.map((sug, idx) => (
          <button
            key={idx}
            type="button"
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
