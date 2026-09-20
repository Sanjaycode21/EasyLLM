"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useAppStore } from "@/lib/store";
import { useEffect } from "react";
import { getProvider } from "@/lib/providers";

export function Navbar() {
  const pathname = usePathname();
  const { hardware, setHardware, useLocalProvider, setUseLocalProvider } = useAppStore();

  useEffect(() => {
    async function loadHw() {
      try {
        const provider = getProvider(useLocalProvider);
        const hw = await provider.getHardware();
        setHardware(hw);
      } catch (err) {
        console.warn("Backend not reached for hardware diagnostics:", err);
      }
    }
    loadHw();
  }, [useLocalProvider, setHardware]);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/60 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        {/* Brand & Left Navigation with EasyLLM Logo */}
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5">
            <Image
              src="/logo.png"
              alt="EasyLLM"
              width={36}
              height={36}
              className="h-9 w-auto object-contain"
              priority
            />
            <div className="flex flex-col">
              <span className="text-base font-bold tracking-tight text-slate-900 leading-none">
                EasyLLM
              </span>
              <span className="text-[10px] tracking-wider uppercase font-semibold text-slate-400 mt-0.5">
                Describe · Train · Your AI
              </span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-5 text-sm font-medium text-slate-600">
            <Link
              href="/"
              className={`transition hover:text-slate-900 ${
                pathname === "/" ? "text-slate-900 font-semibold" : ""
              }`}
            >
              Architect
            </Link>
            <Link
              href="/models"
              className={`transition hover:text-slate-900 ${
                pathname === "/models" ? "text-slate-900 font-semibold" : ""
              }`}
            >
              Model Registry
            </Link>
            <Link
              href="/models"
              className={`flex items-center gap-1.5 transition hover:text-slate-900 ${
                pathname.startsWith("/evaluation") ? "text-blue-700 font-bold" : ""
              }`}
            >
              <span>Evaluation Engine</span>
              <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700 border border-emerald-200">
                Live
              </span>
            </Link>
            <Link
              href="/diagnostics"
              className={`transition hover:text-slate-900 ${
                pathname === "/diagnostics" ? "text-slate-900 font-semibold" : ""
              }`}
            >
              Diagnostics
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="transition hover:text-slate-900 text-slate-500"
            >
              API Docs
            </a>
          </nav>

        </div>

        {/* Unified Sleek Status & Action Group */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setUseLocalProvider(!useLocalProvider)}
            title="Click to toggle between Live Backend and Local Mock Mode"
            className={`rounded-full px-3 py-1 text-xs font-semibold transition border ${
              useLocalProvider
                ? "bg-amber-50 text-amber-800 border-amber-200 shadow-2xs"
                : "bg-slate-50 text-slate-700 border-slate-200/80 hover:bg-slate-100 shadow-2xs"
            }`}
          >
            {useLocalProvider ? "Local Mode" : "Live API"}
          </button>

          {/* Primary Action Button */}
          <Link
            href="/"
            className="rounded-full bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 transition"
          >
            New Build
          </Link>
        </div>
      </div>
    </header>
  );
}
