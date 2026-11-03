"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Layers,
  X,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  StopCircle,
  ExternalLink,
  PieChart,
} from "lucide-react";
import { useBatchStore } from "@/store/useBatchStore";
import { useHistoryStore } from "@/store/useHistoryStore";

export function BatchQueue(): React.JSX.Element {
  const isOpen = useBatchStore((state) => state.isOpen);
  const setIsOpen = useBatchStore((state) => state.setIsOpen);
  const status = useBatchStore((state) => state.status);
  const items = useBatchStore((state) => state.items);
  const summary = useBatchStore((state) => state.summary);
  const cancelBatch = useBatchStore((state) => state.cancelBatch);
  const resetBatch = useBatchStore((state) => state.resetBatch);
  const selectDocument = useHistoryStore((state) => state.selectDocument);

  if (!isOpen) return <></>;

  const completedCount = items.filter((i) => i.status === "completed").length;
  const failedCount = items.filter((i) => i.status === "failed").length;
  const totalCount = items.length || 1;
  const progressPct = Math.round(((completedCount + failedCount) / totalCount) * 100);

  const handleOpenDoc = (resultId?: string) => {
    if (resultId) {
      selectDocument(resultId);
      setIsOpen(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setIsOpen(false)}
          className="fixed inset-0 bg-black/75 backdrop-blur-sm"
        />

        {/* Modal Window */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="relative w-full max-w-2xl bg-[#0f1118] border border-[#232734] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh] z-10"
        >
          {/* Header */}
          <div className="p-4 border-b border-[#232734] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-zinc-100">
                  Batch Multi-Agent Extraction
                </h3>
                <p className="text-xs text-zinc-400 font-mono">
                  {status === "uploading"
                    ? "Uploading files to queue..."
                    : status === "processing"
                    ? `Processing: ${completedCount} / ${items.length} completed`
                    : status === "completed"
                    ? "Batch run finished"
                    : "Batch status: " + status}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {status === "processing" && (
                <button
                  type="button"
                  onClick={cancelBatch}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-rose-400 bg-rose-500/10 border border-rose-500/30 hover:bg-rose-500/20 transition-colors"
                >
                  <StopCircle className="w-3.5 h-3.5" />
                  Cancel
                </button>
              )}
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-[#181b24] h-1.5">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progressPct}%` }}
              className={`h-full transition-all duration-300 ${
                status === "completed"
                  ? "bg-emerald-400"
                  : status === "failed" || status === "cancelled"
                  ? "bg-rose-500"
                  : "bg-cyan-400"
              }`}
            />
          </div>

          {/* Summary Banner if completed */}
          {summary && (
            <div className="p-4 bg-cyan-950/20 border-b border-cyan-900/40 grid grid-cols-3 gap-3 text-center">
              <div className="p-2 rounded-lg bg-[#141722]/80 border border-zinc-800">
                <div className="text-[10px] font-mono text-zinc-400 uppercase">Success Rate</div>
                <div className="text-base font-semibold text-emerald-400 mt-0.5">
                  {Math.round(summary.success_rate * 100)}%
                </div>
              </div>
              <div className="p-2 rounded-lg bg-[#141722]/80 border border-zinc-800">
                <div className="text-[10px] font-mono text-zinc-400 uppercase">Avg Confidence</div>
                <div className="text-base font-semibold text-cyan-400 mt-0.5">
                  {Math.round(summary.average_confidence * 100)}%
                </div>
              </div>
              <div className="p-2 rounded-lg bg-[#141722]/80 border border-zinc-800">
                <div className="text-[10px] font-mono text-zinc-400 uppercase">Total Extracted</div>
                <div className="text-base font-semibold text-white mt-0.5 font-mono">
                  ${summary.total_invoice_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </div>
              </div>
            </div>
          )}

          {/* Items List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2.5 scrollbar-thin">
            {items.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-3 rounded-xl border border-[#232734] bg-[#141722]/60 hover:bg-[#181c2a] transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0">
                  {item.status === "processing" ? (
                    <Loader2 className="w-4 h-4 animate-spin text-cyan-400 shrink-0" />
                  ) : item.status === "completed" ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : item.status === "failed" ? (
                    <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border-2 border-zinc-700 shrink-0" />
                  )}
                  <div className="min-w-0">
                    <div className="text-xs font-medium text-zinc-200 truncate max-w-sm">
                      {item.filename}
                    </div>
                    {item.error && (
                      <div className="text-[11px] text-rose-400 truncate max-w-sm">
                        {item.error}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {typeof item.confidence === "number" && (
                    <span className="text-[11px] font-mono text-cyan-300">
                      {Math.round(item.confidence * 100)}%
                    </span>
                  )}
                  {item.result_id && (
                    <button
                      type="button"
                      onClick={() => handleOpenDoc(item.result_id)}
                      className="p-1 rounded text-zinc-400 hover:text-cyan-400 transition-colors"
                      title="Inspect in workspace"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-[#232734] flex items-center justify-end gap-2 bg-[#0c0e14]">
            <button
              type="button"
              onClick={resetBatch}
              className="px-3 py-1.5 text-xs font-medium text-zinc-400 hover:text-zinc-200 rounded-lg hover:bg-zinc-800 transition-colors"
            >
              Clear
            </button>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="px-4 py-1.5 text-xs font-medium bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors"
            >
              Dismiss
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
