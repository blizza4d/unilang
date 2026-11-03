"use client";

import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  Search,
  FileText,
  Clock,
  Trash2,
  CheckCircle,
  AlertTriangle,
  RotateCcw,
} from "lucide-react";
import { useHistoryStore } from "@/store/useHistoryStore";
import { formatBytes } from "@/lib/utils";

export function HistorySidebar(): React.JSX.Element {
  const isOpen = useHistoryStore((state) => state.isOpen);
  const setIsOpen = useHistoryStore((state) => state.setIsOpen);
  const items = useHistoryStore((state) => state.items);
  const isLoading = useHistoryStore((state) => state.isLoading);
  const searchQuery = useHistoryStore((state) => state.searchQuery);
  const setSearchQuery = useHistoryStore((state) => state.setSearchQuery);
  const loadHistory = useHistoryStore((state) => state.loadHistory);
  const selectDocument = useHistoryStore((state) => state.selectDocument);
  const removeDocument = useHistoryStore((state) => state.removeDocument);

  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [isOpen, loadHistory]);

  const filteredItems = items.filter((item) =>
    item.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Sliding Drawer */}
          <motion.aside
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 240 }}
            className="fixed top-0 left-0 bottom-0 w-80 md:w-96 bg-[#0f1117] border-r border-[#232730] shadow-2xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="p-4 border-b border-[#232730] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-semibold text-zinc-100">
                  Document History
                </h3>
                <span className="text-xs font-mono text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded">
                  {items.length}
                </span>
              </div>
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => loadHistory()}
                  className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
                  title="Refresh"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
                  title="Close"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Search Bar */}
            <div className="p-3 border-b border-[#232730]">
              <div className="relative flex items-center">
                <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3 pointer-events-none" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search past invoices..."
                  className="w-full bg-[#161922] border border-[#262a36] rounded-lg pl-8 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-thin">
              {isLoading && items.length === 0 ? (
                <div className="p-8 text-center text-xs font-mono text-zinc-500 animate-pulse">
                  Loading persistent records...
                </div>
              ) : filteredItems.length === 0 ? (
                <div className="p-8 text-center text-xs font-mono text-zinc-500">
                  {searchQuery ? "No matching documents found" : "No processed documents yet"}
                </div>
              ) : (
                filteredItems.map((doc) => {
                  const confPct = Math.round(doc.overall_confidence * 100);
                  const isHighConf = confPct >= 90;

                  return (
                    <div
                      key={doc.id}
                      onClick={() => {
                        selectDocument(doc.id);
                        setIsOpen(false);
                      }}
                      className="group relative p-3 rounded-xl border border-[#232730] hover:border-cyan-500/50 bg-[#141720]/80 hover:bg-cyan-950/20 cursor-pointer transition-all shadow-sm"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2 min-w-0">
                          <FileText className="w-4 h-4 text-cyan-400 shrink-0" />
                          <span className="text-xs font-medium text-zinc-200 truncate">
                            {doc.filename}
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            removeDocument(doc.id);
                          }}
                          className="opacity-0 group-hover:opacity-100 p-1 text-zinc-500 hover:text-rose-400 rounded transition-opacity"
                          title="Delete"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <div className="mt-2 flex items-center justify-between text-[11px] font-mono">
                        <span className="text-zinc-500">
                          {formatBytes(doc.file_size)} &bull;{" "}
                          {new Date(doc.created_at).toLocaleDateString([], {
                            month: "short",
                            day: "numeric",
                          })}
                        </span>
                        <div className="flex items-center gap-1.5">
                          {doc.math_verified ? (
                            <span className="flex items-center gap-0.5 text-emerald-400 text-[10px]">
                              <CheckCircle className="w-3 h-3" />
                              Math OK
                            </span>
                          ) : (
                            <span className="flex items-center gap-0.5 text-amber-400 text-[10px]">
                              <AlertTriangle className="w-3 h-3" />
                              Math Check
                            </span>
                          )}
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                              isHighConf
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                                : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                            }`}
                          >
                            {confPct}%
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
