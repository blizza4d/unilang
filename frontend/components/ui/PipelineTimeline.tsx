"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  Eye,
  FileSpreadsheet,
  Scale,
  Compass,
  CheckCircle2,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import type { PipelineStage } from "@/lib/types";

interface PipelineTimelineProps {
  currentStage: PipelineStage;
  error?: string | null;
  stageTimings?: Partial<Record<PipelineStage, number>>;
}

interface StageStep {
  id: PipelineStage;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

const STAGES: StageStep[] = [
  {
    id: "vision",
    label: "Vision Ingestion",
    icon: Eye,
    description: "Multimodal transcription & layout",
  },
  {
    id: "extractor",
    label: "Schema Extraction",
    icon: FileSpreadsheet,
    description: "Line-item parsing & currency",
  },
  {
    id: "judge",
    label: "Adversarial Judge",
    icon: Scale,
    description: "Arithmetic & Hallucination verify",
  },
  {
    id: "grounding",
    label: "Spatial Grounding",
    icon: Compass,
    description: "2D coordinate localization",
  },
];

const STAGE_ORDER: PipelineStage[] = [
  "idle",
  "vision",
  "extractor",
  "judge",
  "grounding",
  "complete",
];

export function PipelineTimeline({
  currentStage,
  error,
  stageTimings = {},
}: PipelineTimelineProps): React.JSX.Element {
  const currentIndex = STAGE_ORDER.indexOf(currentStage);
  const isFailed = currentStage === "error" || Boolean(error);
  const isComplete = currentStage === "complete";

  return (
    <div className="w-full bg-[#111318]/90 backdrop-blur-md border border-[#232730] rounded-xl p-4 shadow-xl">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-[#232730]">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            {!isComplete && !isFailed && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
            )}
            <span
              className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                isFailed
                  ? "bg-rose-500"
                  : isComplete
                  ? "bg-emerald-400"
                  : "bg-cyan-500"
              }`}
            />
          </span>
          <span className="text-xs font-mono font-medium tracking-wide text-zinc-300 uppercase">
            Control Tower Pipeline
          </span>
        </div>
        <span className="text-xs font-mono text-zinc-400">
          {isComplete
            ? "PIPELINE VERIFIED"
            : isFailed
            ? "PIPELINE HALTED"
            : "STREAMING INFERENCE"}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        {STAGES.map((step) => {
          const stepIndex = STAGE_ORDER.indexOf(step.id);
          const isPassed = currentIndex > stepIndex || isComplete;
          const isCurrent = currentStage === step.id;
          const Icon = step.icon;
          const timing = stageTimings[step.id];

          return (
            <motion.div
              key={step.id}
              initial={false}
              animate={{
                scale: isCurrent ? 1.02 : 1,
                borderColor: isCurrent
                  ? "#06b6d4"
                  : isPassed
                  ? "#10b981"
                  : isFailed && isCurrent
                  ? "#f43f5e"
                  : "#232730",
              }}
              transition={{ duration: 0.2 }}
              className={`relative rounded-lg p-3 border transition-colors ${
                isCurrent
                  ? "bg-cyan-950/20 shadow-md shadow-cyan-950/40"
                  : isPassed
                  ? "bg-emerald-950/10"
                  : "bg-[#0d0f14]/50"
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div
                  className={`p-1.5 rounded-md ${
                    isCurrent
                      ? "bg-cyan-500/20 text-cyan-300"
                      : isPassed
                      ? "bg-emerald-500/20 text-emerald-300"
                      : "bg-zinc-800 text-zinc-500"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                {isPassed && (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                )}
                {isCurrent && !isFailed && (
                  <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />
                )}
                {isCurrent && isFailed && (
                  <AlertTriangle className="w-4 h-4 text-rose-400" />
                )}
              </div>

              <div className="text-xs font-semibold text-zinc-200">
                {step.label}
              </div>
              <div className="text-[11px] text-zinc-400 mt-0.5 leading-tight line-clamp-1">
                {step.description}
              </div>

              {typeof timing === "number" && (
                <div className="mt-2 text-[10px] font-mono text-zinc-400">
                  {(timing / 1000).toFixed(2)}s
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
