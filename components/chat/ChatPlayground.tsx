"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, BookOpen, Clock, FileText } from "lucide-react";
import { getProvider } from "@/lib/providers";
import { useAppStore } from "@/lib/store";
import { ChatResponse, RetrievedSource } from "@/lib/providers/types";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import LatticeLoader from "@/components/ui/LatticeLoader";

interface MessageItem {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: RetrievedSource[];
  architecture?: "rag" | "qlora" | "hybrid";
  latencyMs?: number;
  timestamp: string;
}

export function ChatPlayground({ modelId }: { modelId: string }) {
  const { useLocalProvider } = useAppStore();
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: "intro",
      role: "assistant",
      content: `Hello! I am your tailored AI system (${modelId}). Ask me anything related to your configured knowledge and guidelines!`,
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [selectedSource, setSelectedSource] = useState<RetrievedSource | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isSending) return;

    const userText = input.trim();
    setInput("");

    const userMsg: MessageItem = {
      id: `usr-${Date.now()}`,
      role: "user",
      content: userText,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsSending(true);

    try {
      const provider = getProvider(useLocalProvider);
      const historyPayload = messages
        .filter((m) => m.id !== "intro")
        .map((m) => ({ role: m.role, content: m.content }));

      const res: ChatResponse = await provider.sendMessage(modelId, userText, historyPayload);

      const botMsg: MessageItem = {
        id: `bot-${Date.now()}`,
        role: "assistant",
        content: res.message,
        sources: res.sources,
        architecture: res.architecture,
        latencyMs: res.metadata?.latency_ms,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      toast.error(err.message || "Failed to generate response");
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: `⚠️ Error executing inference: ${err.message || "Could not reach inference backend."}`,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8.5rem)] flex-col lg:flex-row gap-4">
      {/* Main Chat Stream */}
      <div className="flex flex-1 flex-col rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-100 overflow-hidden">
        {/* Chat Header */}
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-3.5 bg-slate-50/50">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white font-bold">
              <Bot className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                Inference Playground
                <span className="font-mono text-xs font-normal text-slate-500">({modelId})</span>
              </h3>
            </div>
          </div>
          <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
            <span className="h-2 w-2 rounded-full bg-emerald-600 animate-pulse" />
            Model Ready
          </span>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {m.role === "assistant" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-50 text-blue-600 border border-blue-200">
                  <Bot className="h-4 w-4" />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
                  m.role === "user"
                    ? "bg-blue-600 text-white shadow-md shadow-blue-500/10"
                    : "border border-slate-200 bg-slate-50/70 text-slate-800 shadow-2xs"
                }`}
              >
                <div className="prose max-w-none text-xs sm:text-sm">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>

                {/* Sources attribution if returned by RAG/Hybrid */}
                {m.sources && m.sources.length > 0 && (
                  <div className="mt-3 border-t border-slate-200/80 pt-2.5 space-y-1.5">
                    <span className="text-[11px] font-bold text-blue-700 flex items-center gap-1">
                      <BookOpen className="h-3 w-3" /> Grounded Reference Sources:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {m.sources.map((src, sIdx) => (
                        <button
                          key={sIdx}
                          onClick={() => setSelectedSource(src)}
                          className="flex items-center gap-1 rounded-full bg-white px-2.5 py-1 text-[10px] font-mono text-slate-700 border border-slate-200 hover:border-blue-400 hover:text-blue-700 transition shadow-2xs"
                        >
                          <FileText className="h-3 w-3 text-blue-600" />
                          <span>{src.document_name}</span>
                          {src.page && <span className="text-slate-400">p.{src.page}</span>}
                          <span className="text-emerald-600 font-bold">
                            {Math.round(src.relevance_score * 100)}%
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Latency & Metadata footer */}
                <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                  <span>{m.timestamp}</span>
                  {m.latencyMs && (
                    <span className="flex items-center gap-1 font-mono text-slate-500">
                      <Clock className="h-2.5 w-2.5" />
                      {m.latencyMs}ms
                    </span>
                  )}
                </div>
              </div>

              {m.role === "user" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-200 text-slate-700">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          ))}

          {isSending && (
            <div className="flex gap-3 items-center text-xs text-slate-700 bg-slate-50/80 p-3 rounded-2xl border border-slate-200/80 max-w-fit">
              <LatticeLoader
                status="working"
                label="Generating grounded neural response"
                pattern="orbit"
                grid={3}
                shape="round"
                cellSize={6}
                gap={2}
                fontSize={13}
                color="#2563eb"
                showTimer
              />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="border-t border-slate-200 p-4 bg-slate-50/50 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question or support query..."
            className="flex-1 rounded-full border border-slate-200 bg-white px-5 py-3 text-xs sm:text-sm text-slate-800 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-4 focus:ring-blue-500/10 shadow-2xs"
          />
          <button
            type="submit"
            disabled={!input.trim() || isSending}
            className="flex items-center justify-center rounded-full bg-blue-600 px-5 py-3 text-white shadow-md shadow-blue-500/20 hover:bg-blue-700 disabled:opacity-40 transition"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>

      {/* Side Source Inspector Panel */}
      {selectedSource && (
        <div className="w-full lg:w-80 rounded-2xl border border-slate-200 bg-white p-5 space-y-3 overflow-y-auto shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <BookOpen className="h-3.5 w-3.5 text-blue-600" />
              Cited Document Chunk
            </h4>
            <button
              onClick={() => setSelectedSource(null)}
              className="text-xs font-medium text-slate-400 hover:text-slate-700"
            >
              Close
            </button>
          </div>
          <div className="space-y-2 text-xs">
            <div className="rounded-xl bg-slate-50 p-2.5 text-slate-700 border border-slate-200/60">
              <span className="text-[10px] text-slate-400 block font-medium">Document:</span>
              <span className="font-bold text-slate-900">{selectedSource.document_name}</span>
              {selectedSource.page && (
                <span className="block text-slate-500 text-[11px] mt-0.5">Page {selectedSource.page}</span>
              )}
            </div>
            <div className="rounded-xl bg-emerald-50/50 p-2.5 text-slate-700 border border-emerald-200/60">
              <span className="text-[10px] text-emerald-700 block font-semibold">Similarity Score:</span>
              <span className="font-mono text-emerald-800 font-bold text-sm">
                {Math.round(selectedSource.relevance_score * 100)}%
              </span>
            </div>
            <div className="rounded-xl bg-slate-50 p-3 border border-slate-200/60 text-slate-700 text-[11px] leading-relaxed">
              <span className="text-[10px] text-slate-400 block mb-1 font-medium">Extracted Passage:</span>
              {selectedSource.snippet}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
