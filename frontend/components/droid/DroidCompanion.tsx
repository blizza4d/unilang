"use client";

import React, { useEffect, useState, useMemo } from "react";
import { Droid } from "./Droid";
import { DroidFacing, DroidGlow, DroidState } from "./types";
import { StageStrip } from "./StageStrip";
import { useDocumentStore } from "@/store/useDocumentStore";
import { usePrefersReducedMotion } from "@/hooks/usePrefersReducedMotion";

interface DroidCompanionProps {
  className?: string;
  renderMode?: "full" | "strip" | "compact";
}

const NOVA_TIPS = [
  "Nova: 'All math is verified with Python Decimal precision!'",
  "Nova: 'Tip: Press R anytime to enter Review Mode.'",
  "Nova: 'Tip: Press ? to view all keyboard shortcuts.'",
  "Nova: 'Tip: Hover any field to see its bounding box!'",
  "Nova: 'Beep boop! Ready for your next invoice!'",
  "Nova: 'Tip: Press Cmd/Ctrl+K for the Command Palette.'",
];

export const DroidCompanion: React.FC<DroidCompanionProps> = ({
  className = "",
  renderMode = "strip",
}) => {
  const file = useDocumentStore((s) => s.file);
  const isProcessing = useDocumentStore((s) => s.isProcessing);
  const currentStage = useDocumentStore((s) => s.currentStage);
  const extractedData = useDocumentStore((s) => s.extractedData);
  const error = useDocumentStore((s) => s.error);

  const reducedMotion = usePrefersReducedMotion();
  const [isEnabled, setIsEnabled] = useState<boolean>(true);
  const [celebrateActive, setCelebrateActive] = useState<boolean>(false);
  const [tipIndex, setTipIndex] = useState<number>(0);
  const [activeTip, setActiveTip] = useState<string | null>(null);

  // Check user preference ("Show Nova")
  useEffect(() => {
    try {
      const pref = localStorage.getItem("datanova_show_droid");
      if (pref === "false") {
        setIsEnabled(false);
      }
    } catch {
      // Storage unavailable
    }
  }, []);

  // Trigger brief celebration on approval
  useEffect(() => {
    if (extractedData?.overall_status === "APPROVED") {
      setCelebrateActive(true);
      const timer = setTimeout(() => {
        setCelebrateActive(false);
      }, 1600);
      return () => clearTimeout(timer);
    }
  }, [extractedData?.overall_status]);

  const handleDroidClick = () => {
    const nextTip = NOVA_TIPS[tipIndex % NOVA_TIPS.length] ?? NOVA_TIPS[0]!;
    setTipIndex((prev) => prev + 1);
    setActiveTip(nextTip);
    setCelebrateActive(true);
    setTimeout(() => setCelebrateActive(false), 1200);
    setTimeout(() => setActiveTip(null), 4000);
  };

  const { state, glow, caption, facing } = useMemo<{
    state: DroidState;
    glow: DroidGlow;
    caption: string;
    facing: DroidFacing;
  }>(() => {
    if (activeTip) {
      return {
        state: "celebrate",
        glow: "green",
        caption: activeTip,
        facing: "right",
      };
    }

    if (error) {
      return {
        state: "error",
        glow: "red",
        caption: "Processing issue detected.",
        facing: "right",
      };
    }

    if (celebrateActive) {
      return {
        state: "celebrate",
        glow: "green",
        caption: "Document verified & approved!",
        facing: "right",
      };
    }

    if (isProcessing) {
      if (currentStage === "vision") {
        return {
          state: "scan",
          glow: "cyan",
          caption: "Reading document text & spatial layout...",
          facing: "right",
        };
      }
      if (currentStage === "extractor") {
        return {
          state: "think",
          glow: "cyan",
          caption: "Structuring financial entities & line items...",
          facing: "right",
        };
      }
      if (currentStage === "judge" || currentStage === "compliance") {
        return {
          state: "walk",
          glow: "cyan",
          caption: "Verifying arithmetic consistency...",
          facing: "left",
        };
      }
      return {
        state: "walk",
        glow: "cyan",
        caption: "Analyzing document...",
        facing: "right",
      };
    }

    if (extractedData) {
      if (extractedData.overall_status === "REQUIRES_HUMAN_REVIEW") {
        return {
          state: "alert",
          glow: "amber",
          caption: "Arithmetic or confidence warning — human review required.",
          facing: "right",
        };
      }
      return {
        state: "idle",
        glow: "green",
        caption: "Verified document ready for export.",
        facing: "right",
      };
    }

    if (file) {
      return {
        state: "walk",
        glow: "info",
        caption: "Document loaded — ready to process.",
        facing: "right",
      };
    }

    return {
      state: "idle",
      glow: "info",
      caption: "Nova ready to inspect invoices.",
      facing: "right",
    };
  }, [activeTip, error, celebrateActive, isProcessing, currentStage, extractedData, file]);

  if (!isEnabled) {
    return null;
  }

  const droidElement = (
    <div
      role="button"
      tabIndex={0}
      onClick={handleDroidClick}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handleDroidClick();
        }
      }}
      className="cursor-pointer active:scale-90 transition-transform select-none outline-none focus:ring-1 focus:ring-cyan-500/50 rounded-lg"
      title="Click Nova for tips & greeting!"
      aria-label="Nova Droid companion (click for tips)"
    >
      <Droid
        state={reducedMotion ? "idle" : state}
        facing={facing}
        size={renderMode === "compact" ? 44 : 64}
        glow={glow}
        paused={reducedMotion}
      />
    </div>
  );

  if (renderMode === "strip") {
    return (
      <StageStrip caption={caption} className={className}>
        {droidElement}
      </StageStrip>
    );
  }

  return (
    <div className={`flex flex-col items-center gap-1 ${className}`}>
      {droidElement}
      {caption && (
        <span aria-live="polite" className="text-[10px] font-mono text-[var(--text-muted)]">
          {caption}
        </span>
      )}
    </div>
  );
};

export default DroidCompanion;
