"use client";

import React from "react";

interface StageStripProps {
  children: React.ReactNode;
  caption?: string;
  className?: string;
}

export const StageStrip: React.FC<StageStripProps> = ({
  children,
  caption,
  className = "",
}) => {
  return (
    <div
      data-testid="droid-stage-strip"
      className={`relative w-full h-[88px] flex flex-col justify-end overflow-hidden select-none pointer-events-none ${className}`}
    >
      {/* Ground Horizon Hairline */}
      <div className="absolute bottom-[12px] left-0 right-0 h-px bg-[var(--border-subtle)]" />

      {/* Droid Character Placement Area */}
      <div className="relative w-full h-full flex items-end justify-center pointer-events-auto">
        {children}
      </div>

      {/* Accessible Polite Status Live Caption */}
      {caption && (
        <div
          aria-live="polite"
          className="absolute bottom-[-16px] left-0 right-0 text-center text-[11px] font-mono text-[var(--text-muted)] tracking-wide"
        >
          {caption}
        </div>
      )}
    </div>
  );
};

export default StageStrip;
