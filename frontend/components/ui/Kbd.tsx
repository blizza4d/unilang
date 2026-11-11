"use client";

import React from "react";

export interface KbdProps {
  children: React.ReactNode;
  className?: string;
  size?: "sm" | "md";
}

export function Kbd({ children, className = "", size = "sm" }: KbdProps): React.JSX.Element {
  const sizeClasses =
    size === "sm"
      ? "text-[10px] px-1.5 py-0.5 min-w-[18px]"
      : "text-xs px-2 py-0.5 min-w-[22px]";

  return (
    <kbd
      className={`inline-flex items-center justify-center font-mono font-medium rounded text-[var(--text-muted)] bg-[var(--bg-elevated)] border border-[var(--border-subtle)] shadow-[inset_0_-1px_0_rgba(255,255,255,0.06)] select-none uppercase tracking-wider ${sizeClasses} ${className}`}
    >
      {children}
    </kbd>
  );
}
