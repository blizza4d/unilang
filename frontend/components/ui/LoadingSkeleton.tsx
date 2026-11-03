"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { PipelineTimeline } from "./PipelineTimeline";
import type { PipelineStage } from "@/lib/types";

interface LoadingSkeletonProps {
  currentStage?: PipelineStage;
  stageTimings?: Partial<Record<PipelineStage, number>>;
}

const STATUS_MESSAGES = [
  "Mapping multimodal spatial layout...",
  "Translating and structuring schema...",
  "Running adversarial mathematical verification...",
  "Computing 2D bounding box spatial grounding...",
];

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  currentStage,
  stageTimings,
}) => {
  const [statusIndex, setStatusIndex] = useState(0);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    const interval = setInterval(() => {
      setStatusIndex((prev) => (prev + 1) % STATUS_MESSAGES.length);
    }, 2200);
    return () => clearInterval(interval);
  }, []);

  const containerVariants = {
    initial: { opacity: 0 },
    animate: {
      opacity: 1,
      transition: {
        staggerChildren: shouldReduceMotion ? 0 : 0.08,
      },
    },
  };

  const itemVariants = {
    initial: { opacity: 0, y: shouldReduceMotion ? 0 : 6 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.3 } },
  };

  return (
    <div
      role="status"
      aria-busy="true"
      className="relative w-full h-full p-6 flex flex-col gap-6 overflow-hidden select-none"
    >
      {/* Real-time Streaming Timeline */}
      {currentStage && currentStage !== "idle" && (
        <PipelineTimeline
          currentStage={currentStage}
          stageTimings={stageTimings}
        />
      )}

      {/* Scanning light beam */}
      {!shouldReduceMotion && (
        <div className="pointer-events-none absolute inset-x-0 h-24 bg-gradient-to-b from-transparent via-bright/10 to-transparent animate-scan z-10" />
      )}

      <motion.div
        variants={containerVariants}
        initial="initial"
        animate="animate"
        className="flex flex-col gap-6"
      >
        {/* Header Skeleton */}
        <motion.div
          variants={itemVariants}
          className="flex items-center justify-between pb-4 border-b border-subtle"
        >
          <div className="space-y-2">
            <div className="h-6 w-48 bg-white/[0.05] rounded-md animate-pulse" />
            <div className="h-4 w-32 bg-white/[0.03] rounded-md animate-pulse" />
          </div>
          <div className="h-6 w-24 bg-white/[0.05] rounded-full animate-pulse" />
        </motion.div>

        {/* 7 Field Rows Skeletons */}
        <div className="grid grid-cols-1 gap-3">
          {Array.from({ length: 7 }).map((_, idx) => (
            <motion.div
              key={`field-skel-${idx}`}
              variants={itemVariants}
              className="flex items-center justify-between p-3 rounded-lg bg-white/[0.02] border border-white/[0.04]"
            >
              <div className="h-4 w-28 bg-white/[0.05] rounded animate-pulse" />
              <div className="h-4 w-40 bg-white/[0.07] rounded animate-pulse" />
            </motion.div>
          ))}
        </div>

        {/* Table Skeleton (4 rows) */}
        <motion.div
          variants={itemVariants}
          className="mt-2 rounded-xl border border-white/[0.05] p-4 bg-white/[0.02]"
        >
          <div className="h-4 w-36 bg-white/[0.05] rounded mb-4 animate-pulse" />
          <div className="space-y-2.5">
            {Array.from({ length: 4 }).map((_, rIdx) => (
              <div
                key={`tbl-row-${rIdx}`}
                className="grid grid-cols-4 gap-4 py-2 border-b border-white/[0.03]"
              >
                <div className="h-3.5 bg-white/[0.04] rounded animate-pulse col-span-2" />
                <div className="h-3.5 bg-white/[0.04] rounded animate-pulse" />
                <div className="h-3.5 bg-white/[0.04] rounded animate-pulse" />
              </div>
            ))}
          </div>
        </motion.div>

        {/* Cycling Status Text */}
        <div className="flex items-center justify-center pt-2">
          <AnimatePresence mode="wait">
            <motion.div
              key={statusIndex}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.2 }}
              className="flex items-center gap-2 text-xs font-mono text-muted"
            >
              <span className="w-2 h-2 rounded-full bg-accent-amber animate-ping" />
              <span>{STATUS_MESSAGES[statusIndex]}</span>
            </motion.div>
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
};

export default LoadingSkeleton;
