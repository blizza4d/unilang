"use client";

import React, { useEffect, useState } from "react";
import {
  History,
  Layers,
  Trophy,
  Sparkles,
  Command,
} from "lucide-react";
import { DocumentViewer } from "@/components/layout/DocumentViewer";
import { DataExtractorPanel } from "@/components/layout/DataExtractorPanel";
import { SplitWorkspace } from "@/components/layout/SplitWorkspace";
import { HistorySidebar } from "@/components/layout/HistorySidebar";
import { BatchQueue } from "@/components/layout/BatchQueue";
import { ScoreboardModal } from "@/components/layout/ScoreboardModal";
import { CommandPalette } from "@/components/ui/CommandPalette";
import { GuidedTour } from "@/components/ui/GuidedTour";
import { ToastHost } from "@/components/ui/ToastHost";
import { BackendStatusBanner } from "@/components/ui/BackendStatusBanner";
import { Footer } from "@/components/layout/Footer";
import { useDocumentStore } from "@/store/useDocumentStore";
import { useHistoryStore } from "@/store/useHistoryStore";
import { useBatchStore } from "@/store/useBatchStore";

export default function HomePage() {
  const toggleReviewMode = useDocumentStore((state) => state.toggleReviewMode);
  const processFile = useDocumentStore((state) => state.processFile);
  const error = useDocumentStore((state) => state.error);
  const resetStore = useDocumentStore((state) => state.resetStore);

  const toggleHistory = useHistoryStore((state) => state.toggleOpen);
  const openBatch = useBatchStore((state) => state.setIsOpen);

  const [isPaletteOpen, setIsPaletteOpen] = useState(false);
  const [isScoreboardOpen, setIsScoreboardOpen] = useState(false);
  const [isTourOpen, setIsTourOpen] = useState(false);

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      if (
        target &&
        (target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.isContentEditable)
      ) {
        return;
      }

      // Cmd/Ctrl + K opens command palette
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsPaletteOpen((prev) => !prev);
      }

      // R toggles review mode
      if (e.key === "r" || e.key === "R") {
        if (!e.ctrlKey && !e.metaKey && !e.altKey) {
          e.preventDefault();
          toggleReviewMode();
        }
      }

      // Escape clears errors
      if (e.key === "Escape") {
        if (error) {
          e.preventDefault();
          useDocumentStore.setState({ error: null });
        }
      }

      // Cmd/Ctrl + Enter runs extraction
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        processFile();
      }
    };

    window.addEventListener("keydown", handleGlobalKeyDown);
    return () => window.removeEventListener("keydown", handleGlobalKeyDown);
  }, [toggleReviewMode, processFile, error, resetStore]);

  return (
    <main className="h-screen w-screen overflow-hidden flex flex-col bg-app">
      {/* Brand Navigation Bar */}
      <header className="h-12 px-5 border-b border-subtle flex items-center justify-between shrink-0 glass-header select-none z-30">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500" />
            </span>
            <span className="text-xs font-semibold tracking-wider uppercase text-bright font-mono">
              DataNova Extract
            </span>
          </div>

          <span className="hidden sm:inline-block text-[10px] font-mono px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-muted">
            v1.0.0-rc.1 &bull; LangGraph Control Tower
          </span>
        </div>

        {/* Feature Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => toggleHistory()}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium text-zinc-300 hover:text-white hover:bg-white/5 border border-white/10 transition-colors"
            title="Open Document History"
          >
            <History className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden md:inline">History</span>
          </button>

          <button
            type="button"
            onClick={() => openBatch(true)}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium text-zinc-300 hover:text-white hover:bg-white/5 border border-white/10 transition-colors"
            title="Batch Multi-File Queue"
          >
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden md:inline">Batch</span>
          </button>

          <button
            type="button"
            onClick={() => setIsScoreboardOpen(true)}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium text-zinc-300 hover:text-white hover:bg-white/5 border border-white/10 transition-colors"
            title="View Evaluation Benchmarks"
          >
            <Trophy className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden md:inline">Scoreboard</span>
          </button>

          <button
            type="button"
            onClick={() => setIsTourOpen(true)}
            className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium text-zinc-400 hover:text-white hover:bg-white/5 border border-white/10 transition-colors"
            title="Interactive Tour"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
          </button>

          <button
            type="button"
            onClick={() => setIsPaletteOpen(true)}
            className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-mono text-zinc-400 bg-zinc-900 border border-zinc-700/60 hover:border-cyan-500/50 hover:text-cyan-300 transition-colors"
            title="Command Palette (Cmd+K)"
          >
            <Command className="w-3 h-3" />
            <span className="text-[10px]">K</span>
          </button>
        </div>
      </header>

      {/* Backend Connectivity / Mixed-Content Alert Banner */}
      <BackendStatusBanner />

      {/* 50/50 Split Workspace Area */}
      <div className="flex-1 overflow-hidden relative">
        <SplitWorkspace
          left={<DocumentViewer />}
          right={<DataExtractorPanel />}
        />
      </div>

      {/* Release Candidate & Operational Telemetry Footer */}
      <Footer />

      {/* Overlays, Modals, and Drawers */}
      <HistorySidebar />
      <BatchQueue />
      <ScoreboardModal
        isOpen={isScoreboardOpen}
        onClose={() => setIsScoreboardOpen(false)}
      />
      <CommandPalette
        isOpen={isPaletteOpen}
        onClose={() => setIsPaletteOpen(false)}
        onOpenScoreboard={() => setIsScoreboardOpen(true)}
        onStartTour={() => setIsTourOpen(true)}
      />
      <GuidedTour
        isOpen={isTourOpen}
        onClose={() => setIsTourOpen(false)}
      />
      <ToastHost />
    </main>
  );
}
