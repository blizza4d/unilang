"use client";

import React from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import { OverallStatus } from "@/lib/types";

export interface StatusBadgeProps {
  status: OverallStatus;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = "" }) => {
  const shouldReduceMotion = useReducedMotion();

  const config = {
    APPROVED: {
      bg: "bg-accent-green/15 border-accent-green/30 text-accent-green",
      icon: CheckCircle2,
      label: "Approved",
    },
    AUTOMATED_PASS: {
      bg: "bg-accent-green/15 border-accent-green/30 text-accent-green",
      icon: CheckCircle2,
      label: "Automated Pass",
    },
    REQUIRES_HUMAN_REVIEW: {
      bg: "bg-accent-amber/15 border-accent-amber/30 text-accent-amber",
      icon: AlertTriangle,
      label: "Needs Review",
    },
    FAILED: {
      bg: "bg-accent-red/15 border-accent-red/30 text-accent-red",
      icon: XCircle,
      label: "Failed",
    },
  }[status];

  const Icon = config.icon;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={status}
        initial={{ opacity: 0, scale: shouldReduceMotion ? 1 : 0.94 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: shouldReduceMotion ? 1 : 0.94 }}
        transition={{ duration: shouldReduceMotion ? 0 : 0.2, ease: "easeOut" }}
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium tracking-wide ${config.bg} ${className}`}
        aria-live="polite"
      >
        <Icon className="w-3.5 h-3.5" />
        <span>{config.label}</span>
      </motion.div>
    </AnimatePresence>
  );
};

export default StatusBadge;
