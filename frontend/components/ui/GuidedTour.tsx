"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ArrowRight, ArrowLeft, X, CheckCircle2 } from "lucide-react";

interface TourStep {
  title: string;
  description: string;
  highlight: string;
}

const TOUR_STEPS: TourStep[] = [
  {
    title: "1. Multilingual Document Ingestion",
    description:
      "Drop single or batch multi-page PDF, PNG, JPG, or WEBP invoices. Supports English, German MwSt, Hindi GST, Arabic RTL, and Japanese Qualified Invoices.",
    highlight: "Left Workspace / File Dropzone",
  },
  {
    title: "2. Autonomous Multi-Agent Pipeline",
    description:
      "Watch the Vision Agent transcribe spatial layouts, the Extractor Agent structure schema fields, and the Adversarial Judge Agent verify arithmetic via live HTTP Server-Sent Events.",
    highlight: "Streaming Progress Timeline",
  },
  {
    title: "3. 2D Coordinate Spatial Grounding",
    description:
      "Hover over any extracted field in the sidebar to illuminate its exact source coordinates on the document canvas in glowing cyan.",
    highlight: "Interactive Document Canvas Overlay",
  },
  {
    title: "4. Deterministic Arithmetic Verification",
    description:
      "Row totals (Qty × Unit Price) and grand totals (Subtotal + Tax) are verified by pure deterministic code. Any discrepancy triggers human review.",
    highlight: "Extraction Sidebar & Review Workspace",
  },
  {
    title: "5. Enterprise Export & Audit Ledger",
    description:
      "Export certified ReportLab PDFs, formula-driven Excel workbooks (=C2*D2), or CSV bundles. Every human correction is recorded in an immutable audit ledger.",
    highlight: "Export Menu & Persistent History",
  },
];

interface GuidedTourProps {
  isOpen: boolean;
  onClose: () => void;
}

export function GuidedTour({ isOpen, onClose }: GuidedTourProps): React.JSX.Element {
  const [stepIndex, setStepIndex] = useState<number>(0);

  if (!isOpen) return <></>;

  const currentStep = TOUR_STEPS[stepIndex] ?? TOUR_STEPS[0]!;
  const isLast = stepIndex === TOUR_STEPS.length - 1;

  const handleNext = () => {
    if (isLast) {
      onClose();
      setStepIndex(0);
    } else {
      setStepIndex((i) => i + 1);
    }
  };

  const handlePrev = () => {
    setStepIndex((i) => Math.max(0, i - 1));
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 select-none pointer-events-auto">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm"
        />

        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="relative w-full max-w-md bg-[#11131a] border border-[#232734] rounded-2xl shadow-2xl overflow-hidden p-5 z-10"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-[#232734]">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400">
                <Sparkles className="w-4 h-4" />
              </div>
              <span className="text-xs font-mono font-medium text-cyan-400 uppercase tracking-wide">
                Product Walkthrough ({stepIndex + 1}/{TOUR_STEPS.length})
              </span>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="p-1 rounded text-zinc-500 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Body */}
          <div className="py-4">
            <h4 className="text-sm font-bold text-white mb-2">
              {currentStep.title}
            </h4>
            <p className="text-xs text-zinc-400 leading-relaxed">
              {currentStep.description}
            </p>
            <div className="mt-3 text-[10px] font-mono text-zinc-500 bg-[#161922] px-2.5 py-1.5 rounded-lg border border-[#232734]">
              Target: <span className="text-cyan-300">{currentStep.highlight}</span>
            </div>
          </div>

          {/* Footer Controls */}
          <div className="flex items-center justify-between pt-3 border-t border-[#232734]">
            <button
              type="button"
              onClick={handlePrev}
              disabled={stepIndex === 0}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-zinc-400 hover:text-white disabled:opacity-30 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Back
            </button>

            <button
              type="button"
              onClick={handleNext}
              className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-semibold bg-cyan-500 text-black hover:bg-cyan-400 shadow transition-colors"
            >
              <span>{isLast ? "Get Started" : "Next"}</span>
              {isLast ? (
                <CheckCircle2 className="w-3.5 h-3.5" />
              ) : (
                <ArrowRight className="w-3.5 h-3.5" />
              )}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
