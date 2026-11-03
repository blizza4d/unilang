"use client";

import React from "react";
import type { PageInfo } from "@/hooks/usePdfPages";

interface PageThumbnailsProps {
  pages: PageInfo[];
  currentPage: number;
  onSelectPage: (page: number) => void;
  isOpen: boolean;
}

export function PageThumbnails({
  pages,
  currentPage,
  onSelectPage,
  isOpen,
}: PageThumbnailsProps): React.JSX.Element | null {
  if (!isOpen || pages.length <= 1) {
    return null;
  }

  return (
    <div className="w-24 shrink-0 flex flex-col gap-2 p-2 bg-[#0d0f14] border-r border-[#232730] overflow-y-auto max-h-full scrollbar-thin">
      <div className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider px-1 text-center">
        Pages ({pages.length})
      </div>
      {pages.map((p) => {
        const isSelected = p.pageNumber === currentPage;
        return (
          <button
            key={p.pageNumber}
            type="button"
            onClick={() => onSelectPage(p.pageNumber)}
            className={`group relative flex flex-col items-center rounded-lg border p-1 transition-all ${
              isSelected
                ? "border-cyan-500 bg-cyan-950/30 ring-1 ring-cyan-500/50"
                : "border-[#232730] hover:border-zinc-700 bg-zinc-900/40"
            }`}
          >
            <div className="w-full aspect-[3/4] bg-zinc-950 rounded flex items-center justify-center overflow-hidden border border-zinc-800">
              {p.imageUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={p.imageUrl}
                  alt={`Thumbnail page ${p.pageNumber}`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-[11px] font-mono text-zinc-600">
                  P.{p.pageNumber}
                </span>
              )}
            </div>
            <span
              className={`text-[10px] font-mono mt-1 ${
                isSelected ? "text-cyan-400 font-semibold" : "text-zinc-400"
              }`}
            >
              Page {p.pageNumber}
            </span>
          </button>
        );
      })}
    </div>
  );
}
