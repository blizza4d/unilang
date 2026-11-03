"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";

export interface ConfidenceRingProps {
  score: number;
  size?: number;
  needsReview: boolean;
}

export const ConfidenceRing: React.FC<ConfidenceRingProps> = React.memo(
  ({ score, size = 28, needsReview }) => {
    const shouldReduceMotion = useReducedMotion();
    const clampedScore = Math.max(0, Math.min(1, score));
    const percentage = Math.round(clampedScore * 100);

    const strokeWidth = 2.5;
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - clampedScore * circumference;

    const strokeColor = needsReview ? "#F59E0B" : "#8EA48C";

    return (
      <div
        className="relative inline-flex items-center justify-center shrink-0"
        style={{ width: size, height: size }}
        role="img"
        aria-label={`Confidence ${percentage} percent`}
      >
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth={strokeWidth}
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: shouldReduceMotion ? strokeDashoffset : circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: shouldReduceMotion ? 0 : 0.6, ease: "easeOut" }}
            strokeLinecap="round"
          />
        </svg>
        <span
          className="absolute font-mono text-[9px] font-medium leading-none tracking-tighter"
          style={{ color: strokeColor }}
        >
          {percentage}
        </span>
      </div>
    );
  }
);

ConfidenceRing.displayName = "ConfidenceRing";

export default ConfidenceRing;
