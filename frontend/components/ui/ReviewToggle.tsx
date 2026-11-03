"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Sparkles } from "lucide-react";

export interface ReviewToggleProps {
  isReviewMode: boolean;
  onToggle: () => void;
  unresolvedCount?: number;
}

export const ReviewToggle: React.FC<ReviewToggleProps> = ({
  isReviewMode,
  onToggle,
  unresolvedCount = 0,
}) => {
  const shouldReduceMotion = useReducedMotion();

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onToggle();
    }
  };

  return (
    <div className="flex items-center gap-3">
      <span className="text-xs uppercase tracking-wider font-semibold text-muted flex items-center gap-1.5 select-none">
        <Sparkles className="w-3.5 h-3.5 text-accent-amber" />
        Human-in-the-Loop Review
      </span>
      <div
        role="switch"
        aria-checked={isReviewMode}
        tabIndex={0}
        onClick={onToggle}
        onKeyDown={handleKeyDown}
        className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border border-white/10 transition-colors duration-200 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-bright/40 ${
          isReviewMode ? "bg-accent-amber/30 border-accent-amber/50" : "bg-panel"
        }`}
        aria-label="Toggle human-in-the-loop review mode"
      >
        <motion.span
          layout={!shouldReduceMotion}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
          className={`pointer-events-none inline-block h-4 w-4 transform rounded-full shadow-lg ring-0 transition duration-200 mt-0.5 ${
            isReviewMode
              ? "translate-x-5 bg-accent-amber"
              : "translate-x-1 bg-muted"
          }`}
        />
      </div>

      {isReviewMode && unresolvedCount > 0 && (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-mono font-medium bg-accent-amber/20 text-accent-amber border border-accent-amber/30">
          {unresolvedCount} flagged
        </span>
      )}
    </div>
  );
};

export default ReviewToggle;
