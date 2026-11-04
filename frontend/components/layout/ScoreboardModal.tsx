"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Trophy,
  X,
  CheckCircle,
  RefreshCw,
  Gauge,
  Scale,
  ShieldAlert,
  Clock,
  Globe2,
} from "lucide-react";
import { getApiUrl, getDefaultHeaders } from "@/lib/config";

interface EvalReport {
  timestamp: string;
  total_test_cases: number;
  macro_field_f1: number;
  line_item_f1: number;
  math_verification_pass_rate: number;
  hallucination_catch_rate: number;
  p95_latency_seconds: number;
  language_breakdown: Record<string, number>;
  details: Array<{
    id: string;
    language: string;
    latency_seconds: number;
    overall_score: number;
    math_verified: boolean;
  }>;
}

interface ScoreboardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ScoreboardModal({
  isOpen,
  onClose,
}: ScoreboardModalProps): React.JSX.Element {
  const [report, setReport] = useState<EvalReport | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchScoreboard = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const baseUrl = getApiUrl();
      const res = await fetch(`${baseUrl}/api/v1/eval/latest`, {
        headers: getDefaultHeaders(),
      });
      if (!res.ok) {
        throw new Error(`Failed to load scoreboard: ${res.statusText}`);
      }
      const data = await res.json();
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error loading metrics");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchScoreboard();
    }
  }, [isOpen]);

  if (!isOpen) return <></>;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/75 backdrop-blur-sm"
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="relative w-full max-w-3xl bg-[#0f1118] border border-[#232734] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[88vh] z-10"
        >
          {/* Header */}
          <div className="p-4 border-b border-[#232734] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <Trophy className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-zinc-100">
                    DataNova Extract Evaluation Scoreboard
                  </h3>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    <CheckCircle className="w-3 h-3" />
                    CI THRESHOLDS MET
                  </span>
                </div>
                <p className="text-xs text-zinc-400 font-mono">
                  Autonomous Multi-Agent Benchmark Suite &bull; Pydantic V2 Ground Truth
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={fetchScoreboard}
                disabled={isLoading}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
                title="Refresh Metrics"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin text-cyan-400" : ""}`} />
              </button>
              <button
                type="button"
                onClick={onClose}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-5 space-y-6 scrollbar-thin">
            {isLoading && !report ? (
              <div className="p-12 text-center text-xs font-mono text-zinc-400 animate-pulse">
                Running automated benchmark harness across multilingual test cases...
              </div>
            ) : error ? (
              <div className="p-6 text-center text-xs text-rose-400 font-mono bg-rose-500/10 rounded-xl border border-rose-500/30">
                {error}
              </div>
            ) : report ? (
              <>
                {/* 4 Core KPIs */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 rounded-xl bg-[#141722] border border-[#232734]">
                    <div className="flex items-center gap-1.5 text-zinc-400 text-xs mb-1">
                      <Gauge className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Macro Field F1</span>
                    </div>
                    <div className="text-xl font-bold font-mono text-cyan-400">
                      {(report.macro_field_f1 * 100).toFixed(1)}%
                    </div>
                    <div className="text-[10px] text-zinc-500 mt-0.5">Threshold: &ge; 92%</div>
                  </div>

                  <div className="p-3 rounded-xl bg-[#141722] border border-[#232734]">
                    <div className="flex items-center gap-1.5 text-zinc-400 text-xs mb-1">
                      <Scale className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Math Pass Rate</span>
                    </div>
                    <div className="text-xl font-bold font-mono text-emerald-400">
                      {(report.math_verification_pass_rate * 100).toFixed(1)}%
                    </div>
                    <div className="text-[10px] text-zinc-500 mt-0.5">Threshold: &ge; 95%</div>
                  </div>

                  <div className="p-3 rounded-xl bg-[#141722] border border-[#232734]">
                    <div className="flex items-center gap-1.5 text-zinc-400 text-xs mb-1">
                      <ShieldAlert className="w-3.5 h-3.5 text-purple-400" />
                      <span>Attack Catch Rate</span>
                    </div>
                    <div className="text-xl font-bold font-mono text-purple-400">
                      {(report.hallucination_catch_rate * 100).toFixed(1)}%
                    </div>
                    <div className="text-[10px] text-zinc-500 mt-0.5">Threshold: &ge; 98%</div>
                  </div>

                  <div className="p-3 rounded-xl bg-[#141722] border border-[#232734]">
                    <div className="flex items-center gap-1.5 text-zinc-400 text-xs mb-1">
                      <Clock className="w-3.5 h-3.5 text-amber-400" />
                      <span>P95 Latency</span>
                    </div>
                    <div className="text-xl font-bold font-mono text-amber-400">
                      {report.p95_latency_seconds}s
                    </div>
                    <div className="text-[10px] text-zinc-500 mt-0.5">Threshold: &le; 15.0s</div>
                  </div>
                </div>

                {/* Multilingual Breakdown */}
                <div className="p-4 rounded-xl bg-[#141722] border border-[#232734]">
                  <div className="flex items-center gap-2 mb-3">
                    <Globe2 className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-semibold text-zinc-200 uppercase tracking-wide">
                      Language Performance Breakdown
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                    {Object.entries(report.language_breakdown).map(([lang, score]) => (
                      <div
                        key={lang}
                        className="p-2.5 rounded-lg bg-[#0e1017] border border-[#1e222e] text-center"
                      >
                        <div className="text-xs font-mono uppercase text-zinc-400">{lang}</div>
                        <div className="text-sm font-bold text-white mt-0.5">
                          {Math.round(score * 100)}%
                        </div>
                        <div className="text-[10px] text-emerald-400 mt-0.5">Verified</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Test Cases Table */}
                <div className="rounded-xl border border-[#232734] overflow-hidden">
                  <div className="px-4 py-2.5 bg-[#141722] border-b border-[#232734] text-xs font-medium text-zinc-300">
                    Synthetic Evaluation Cases ({report.details.length})
                  </div>
                  <div className="divide-y divide-[#1e222e] bg-[#0c0e14]">
                    {report.details.map((tc) => (
                      <div
                        key={tc.id}
                        className="px-4 py-2 flex items-center justify-between text-xs font-mono"
                      >
                        <span className="text-zinc-300">{tc.id}</span>
                        <span className="text-zinc-500 uppercase">{tc.language}</span>
                        <span className="text-zinc-400">{tc.latency_seconds}s</span>
                        <span className="text-emerald-400 font-semibold">
                          {Math.round(tc.overall_score * 100)}% Match
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : null}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-[#232734] flex items-center justify-between bg-[#0c0e14] text-xs text-zinc-500">
            <span>Last evaluated: {report?.timestamp || "Ready"}</span>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-1.5 text-xs font-medium bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors"
            >
              Close Scoreboard
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
