"use client";

import React, { useEffect, useState } from "react";
import { Terminal, Cpu, CheckCircle2, AlertCircle } from "lucide-react";
import { useDocumentStore } from "@/store/useDocumentStore";

const APP_VERSION = "1.0.0-rc.1";

export function Footer() {
  const extractedData = useDocumentStore((state) => state.extractedData);
  const isProcessing = useDocumentStore((state) => state.isProcessing);
  const error = useDocumentStore((state) => state.error);

  const isDemo = Boolean(
    extractedData?.is_demo || extractedData?.source === "demo_fixture"
  );

  const [gitSha, setGitSha] = useState("859bfd9");
  const [envLabel, setEnvLabel] = useState("Production");

  useEffect(() => {
    const sha =
      process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA ||
      process.env.NEXT_PUBLIC_GIT_SHA ||
      "859bfd9";
    setGitSha(sha.slice(0, 7));

    const env =
      process.env.NEXT_PUBLIC_VERCEL_ENV ||
      process.env.NODE_ENV ||
      "production";
    if (env === "preview") setEnvLabel("Preview");
    else if (env === "development") setEnvLabel("Development");
    else setEnvLabel("Production");
  }, []);

  return (
    <footer
      role="contentinfo"
      aria-label="Application release and status footer"
      className="h-7 px-4 border-t border-subtle flex items-center justify-between text-[11px] font-mono text-muted bg-[#0A0A0A]/95 shrink-0 z-20 select-none backdrop-blur-sm"
    >
      {/* Left: Release Version & Git Build Stamp */}
      <div className="flex items-center gap-2.5">
        <div className="flex items-center gap-1.5 text-zinc-400">
          <Terminal className="w-3 h-3 text-cyan-400/80" />
          <span className="font-semibold text-zinc-300">
            v{APP_VERSION}
          </span>
          <span className="text-zinc-600">({gitSha})</span>
        </div>

        <span className="text-zinc-700">&bull;</span>

        <span
          className={`px-1.5 py-0.2 rounded text-[10px] font-mono uppercase tracking-wider ${
            envLabel === "Production"
              ? "bg-zinc-800/80 text-zinc-400 border border-zinc-700/50"
              : "bg-amber-950/60 text-amber-400 border border-amber-800/40"
          }`}
        >
          {envLabel}
        </span>
      </div>

      {/* Center: System Pacing & Operational State */}
      <div className="hidden sm:flex items-center gap-3 text-zinc-400">
        <div className="flex items-center gap-1.5">
          <Cpu className="w-3 h-3 text-zinc-500" />
          <span>Engine:</span>
          {isProcessing ? (
            <span className="text-cyan-400 animate-pulse font-medium">
              Pipeline Active...
            </span>
          ) : error ? (
            <span className="text-terracotta inline-flex items-center gap-1">
              <AlertCircle className="w-3 h-3" /> Degraded
            </span>
          ) : (
            <span className="text-sage inline-flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> Ready
            </span>
          )}
        </div>

        <span className="text-zinc-700">&bull;</span>

        <span
          className={`px-1.5 py-0.2 rounded text-[10px] ${
            isDemo
              ? "bg-amber-500/10 text-amber-400 border border-amber-500/30 font-medium"
              : "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30"
          }`}
        >
          {isDemo ? "DEMO MODE (FIXTURES)" : "LIVE HYBRID AI"}
        </span>
      </div>

      {/* Right: Key Shortcuts Reference */}
      <div className="flex items-center gap-2 text-[10px] text-zinc-500">
        <span className="hidden md:inline">
          <kbd className="px-1 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
            K
          </kbd>{" "}
          Palette
        </span>
        <span className="hidden md:inline text-zinc-700">&bull;</span>
        <span className="hidden lg:inline">
          <kbd className="px-1 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
            R
          </kbd>{" "}
          Review
        </span>
        <span className="hidden lg:inline text-zinc-700">&bull;</span>
        <span>
          <kbd className="px-1 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
            Ctrl+↵
          </kbd>{" "}
          Run
        </span>
      </div>
    </footer>
  );
}
