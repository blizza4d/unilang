"use client";

import React from "react";
import { Info } from "lucide-react";

interface DemoPillProps {
  source?: string | null;
  className?: string;
}

export function DemoPill({ source, className = "" }: DemoPillProps): React.JSX.Element | null {
  if (source !== "demo_fixture" && source !== "demo") {
    return null;
  }

  return (
    <div
      data-testid="demo-pill"
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30 select-none ${className}`}
      title="This extraction was served by the deterministic demo fixture pipeline"
    >
      <Info className="w-3 h-3 text-amber-400 shrink-0" />
      <span>Demo mode: sample data</span>
    </div>
  );
}
