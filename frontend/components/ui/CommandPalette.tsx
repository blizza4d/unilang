"use client";

import React, { useEffect, useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Play,
  CheckCircle,
  FileSpreadsheet,
  Download,
  History,
  Trophy,
  ZoomIn,
  ZoomOut,
  Layers,
  HelpCircle,
} from "lucide-react";
import { useDocumentStore } from "@/store/useDocumentStore";
import { useHistoryStore } from "@/store/useHistoryStore";
import { useBatchStore } from "@/store/useBatchStore";
import { filterByFuzzy } from "@/lib/fuzzy";
import { downloadExport } from "@/lib/download";

interface CommandItem {
  id: string;
  title: string;
  category: string;
  icon: React.ComponentType<{ className?: string }>;
  shortcut?: string;
  action: () => void;
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenScoreboard: () => void;
  onStartTour: () => void;
}

export function CommandPalette({
  isOpen,
  onClose,
  onOpenScoreboard,
  onStartTour,
}: CommandPaletteProps): React.JSX.Element {
  const [query, setQuery] = useState<string>("");
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  const processFile = useDocumentStore((state) => state.processFile);
  const approveAll = useDocumentStore((state) => state.approveAll);
  const toggleReviewMode = useDocumentStore((state) => state.toggleReviewMode);
  const extractedData = useDocumentStore((state) => state.extractedData);
  const file = useDocumentStore((state) => state.file);
  const toggleHistory = useHistoryStore((state) => state.toggleOpen);
  const openBatch = useBatchStore((state) => state.setIsOpen);

  const commands: CommandItem[] = useMemo(
    () => [
      {
        id: "process",
        title: "Process Document Pipeline",
        category: "Actions",
        icon: Play,
        shortcut: "Enter",
        action: () => {
          processFile();
          onClose();
        },
      },
      {
        id: "approve",
        title: "Approve All Verified Fields",
        category: "Actions",
        icon: CheckCircle,
        shortcut: "⌘A",
        action: () => {
          approveAll();
          onClose();
        },
      },
      {
        id: "review-mode",
        title: "Toggle Human Review Workspace",
        category: "View",
        icon: FileSpreadsheet,
        action: () => {
          toggleReviewMode();
          onClose();
        },
      },
      {
        id: "history",
        title: "Open Persistent Document History",
        category: "Navigation",
        icon: History,
        shortcut: "⌘H",
        action: () => {
          toggleHistory();
          onClose();
        },
      },
      {
        id: "batch",
        title: "Open Batch Multi-Document Queue",
        category: "Navigation",
        icon: Layers,
        shortcut: "⌘B",
        action: () => {
          openBatch(true);
          onClose();
        },
      },
      {
        id: "scoreboard",
        title: "Open Evaluation Benchmark Scoreboard",
        category: "Metrics",
        icon: Trophy,
        action: () => {
          onOpenScoreboard();
          onClose();
        },
      },
      {
        id: "export-xlsx",
        title: "Export Native Excel Workbook (XLSX)",
        category: "Export",
        icon: Download,
        action: () => {
          if (extractedData) {
            downloadExport(extractedData, "xlsx", file?.name || "invoice");
          }
          onClose();
        },
      },
      {
        id: "export-json",
        title: "Export Machine-Readable JSON",
        category: "Export",
        icon: Download,
        action: () => {
          if (extractedData) {
            downloadExport(extractedData, "json", file?.name || "invoice");
          }
          onClose();
        },
      },
      {
        id: "export-pdf",
        title: "Export Certified Audit Report (PDF)",
        category: "Export",
        icon: Download,
        action: () => {
          if (extractedData) {
            downloadExport(extractedData, "pdf", file?.name || "invoice");
          }
          onClose();
        },
      },
      {
        id: "tour",
        title: "Start Interactive Product Walkthrough",
        category: "Help",
        icon: HelpCircle,
        action: () => {
          onStartTour();
          onClose();
        },
      },
    ],
    [
      processFile,
      approveAll,
      toggleReviewMode,
      toggleHistory,
      openBatch,
      onOpenScoreboard,
      onStartTour,
      onClose,
      extractedData,
      file,
    ]
  );

  const filteredCommands = useMemo(
    () => filterByFuzzy(commands, query, (c) => `${c.title} ${c.category}`),
    [commands, query]
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (isOpen) onClose();
      }
      if (!isOpen) return;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % Math.max(filteredCommands.length, 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev <= 0 ? Math.max(filteredCommands.length - 1, 0) : prev - 1
        );
      } else if (e.key === "Enter") {
        e.preventDefault();
        const cmd = filteredCommands[selectedIndex];
        if (cmd) {
          cmd.action();
        }
      } else if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose, filteredCommands, selectedIndex]);

  if (!isOpen) return <></>;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 p-4 select-none">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm"
        />

        {/* Raycast Palette Window */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -10 }}
          transition={{ duration: 0.15 }}
          className="relative w-full max-w-xl bg-[#11131a] border border-[#232734] rounded-2xl shadow-2xl overflow-hidden flex flex-col z-10"
        >
          {/* Search Header */}
          <div className="p-3.5 border-b border-[#232734] flex items-center gap-3">
            <Search className="w-4 h-4 text-zinc-400 shrink-0" />
            <input
              type="text"
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type a command or search action..."
              className="w-full bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none"
            />
            <span className="text-[10px] font-mono text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded border border-zinc-700">
              ESC
            </span>
          </div>

          {/* List of Commands */}
          <div className="max-h-[340px] overflow-y-auto p-2 space-y-1 scrollbar-thin">
            {filteredCommands.length === 0 ? (
              <div className="p-8 text-center text-xs font-mono text-zinc-500">
                No matching commands found
              </div>
            ) : (
              filteredCommands.map((cmd, idx) => {
                const Icon = cmd.icon;
                const isSelected = idx === selectedIndex;

                return (
                  <button
                    key={cmd.id}
                    type="button"
                    onClick={() => cmd.action()}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={`w-full flex items-center justify-between p-2.5 rounded-xl text-left transition-colors ${
                      isSelected
                        ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                        : "text-zinc-300 hover:bg-zinc-800/40 border border-transparent"
                    }`}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div
                        className={`p-1.5 rounded-lg ${
                          isSelected
                            ? "bg-cyan-500/30 text-cyan-300"
                            : "bg-zinc-800/60 text-zinc-400"
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="min-w-0">
                        <div className="text-xs font-medium truncate">
                          {cmd.title}
                        </div>
                        <div className="text-[10px] text-zinc-500">
                          {cmd.category}
                        </div>
                      </div>
                    </div>

                    {cmd.shortcut && (
                      <span className="text-[10px] font-mono text-zinc-400 bg-zinc-900 border border-zinc-800 px-1.5 py-0.5 rounded">
                        {cmd.shortcut}
                      </span>
                    )}
                  </button>
                );
              })
            )}
          </div>

          {/* Footer Navigation Hints */}
          <div className="p-2.5 border-t border-[#232734] bg-[#0c0e14] flex items-center justify-between text-[11px] font-mono text-zinc-500 px-4">
            <span>Navigation: &uarr;&darr; &bull; Select: Enter</span>
            <span>Raycast Command Tower</span>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
