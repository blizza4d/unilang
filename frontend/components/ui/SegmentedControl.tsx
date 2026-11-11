"use client";

import React from "react";
import { motion } from "framer-motion";

export interface SegmentedControlOption<T extends string> {
  value: T;
  label: string;
  icon?: React.ReactNode;
}

export interface SegmentedControlProps<T extends string> {
  options: SegmentedControlOption<T>[];
  value: T;
  onChange: (value: T) => void;
  size?: "sm" | "md";
  className?: string;
  disabled?: boolean;
}

export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
  size = "md",
  className = "",
  disabled = false,
}: SegmentedControlProps<T>): React.JSX.Element {
  const sizeClasses = size === "sm" ? "p-0.5 text-xs h-7" : "p-1 text-xs h-9";
  const itemPadding = size === "sm" ? "px-2.5 py-1" : "px-3 py-1.5";

  return (
    <div
      role="radiogroup"
      className={`inline-flex items-center rounded-md bg-[var(--bg-panel)] border border-[var(--border-subtle)] select-none ${sizeClasses} ${className}`}
    >
      {options.map((opt) => {
        const isSelected = opt.value === value;
        return (
          <button
            key={opt.value}
            type="button"
            role="radio"
            aria-checked={isSelected}
            disabled={disabled}
            onClick={() => onChange(opt.value)}
            className={`relative inline-flex items-center justify-center gap-1.5 rounded-sm font-medium transition-colors outline-none z-10 ${itemPadding} ${
              isSelected
                ? "text-[var(--text-bright)]"
                : "text-[var(--text-muted)] hover:text-[var(--text-bright)]"
            } disabled:opacity-40 disabled:pointer-events-none`}
          >
            {isSelected && (
              <motion.div
                layoutId="segmented-thumb"
                className="absolute inset-0 rounded-sm bg-[var(--bg-elevated)] border border-[var(--border-strong)] shadow-sm -z-10"
                transition={{ type: "spring", stiffness: 450, damping: 35 }}
              />
            )}
            {opt.icon && <span className="shrink-0">{opt.icon}</span>}
            <span>{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
}
