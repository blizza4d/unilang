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

  const { state, glow, caption, facing } = useMemo<{
    state: DroidState;
    glow: DroidGlow;
    caption: string;
    facing: DroidFacing;
  }>(() => {
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
  }, [error, celebrateActive, isProcessing, currentStage, extractedData, file]);

  if (!isEnabled) {
    return null;
  }

  const droidElement = (
    <Droid
      state={reducedMotion ? "idle" : state}
      facing={facing}
      size={renderMode === "compact" ? 44 : 64}
      glow={glow}
      paused={reducedMotion}
    />
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
