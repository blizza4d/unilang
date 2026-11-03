"use client";

import React from "react";
import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  Maximize2,
  ChevronLeft,
  ChevronRight,
  Layers,
} from "lucide-react";

interface ViewerToolbarProps {
  zoom: number;
  rotation: number;
  currentPage: number;
  totalPages: number;
  showThumbnails: boolean;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetView: () => void;
  onRotate: () => void;
  onPrevPage: () => void;
  onNextPage: () => void;
  onToggleThumbnails: () => void;
}

export function ViewerToolbar({
  zoom,
  rotation,
  currentPage,
  totalPages,
  showThumbnails,
  onZoomIn,
  onZoomOut,
  onResetView,
  onRotate,
  onPrevPage,
  onNextPage,
  onToggleThumbnails,
}: ViewerToolbarProps): React.JSX.Element {
  return (
    <div className="flex items-center justify-between px-3 py-2 bg-[#12141a]/95 backdrop-blur-md border border-[#232730] rounded-xl text-zinc-300 shadow-lg text-xs select-none">
      {/* Page Navigation */}
      <div className="flex items-center gap-1.5">
        <button
          type="button"
          onClick={onToggleThumbnails}
          title="Toggle page thumbnails"
          className={`p-1.5 rounded-lg border transition-colors ${
            showThumbnails
              ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/40"
              : "border-transparent hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <Layers className="w-4 h-4" />
        </button>

        <div className="h-4 w-px bg-zinc-800 mx-1" />

        <button
          type="button"
          onClick={onPrevPage}
          disabled={currentPage <= 1}
          className="p-1 rounded-md hover:bg-zinc-800 disabled:opacity-30 disabled:hover:bg-transparent transition-opacity"
          title="Previous Page"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <span className="font-mono text-zinc-400 px-1">
          <span className="text-zinc-200 font-medium">{currentPage}</span> /{" "}
          <span>{totalPages || 1}</span>
        </span>
        <button
          type="button"
          onClick={onNextPage}
          disabled={currentPage >= totalPages}
          className="p-1 rounded-md hover:bg-zinc-800 disabled:opacity-30 disabled:hover:bg-transparent transition-opacity"
          title="Next Page"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Zoom and Transform Controls */}
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={onZoomOut}
          disabled={zoom <= 0.45}
          className="p-1.5 rounded-md hover:bg-zinc-800 disabled:opacity-30 transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>

        <span className="font-mono text-[11px] text-zinc-400 w-12 text-center">
          {Math.round(zoom * 100)}%
        </span>

        <button
          type="button"
          onClick={onZoomIn}
          disabled={zoom >= 3.0}
          className="p-1.5 rounded-md hover:bg-zinc-800 disabled:opacity-30 transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>

        <div className="h-4 w-px bg-zinc-800 mx-1" />

        <button
          type="button"
          onClick={onRotate}
          className="p-1.5 rounded-md hover:bg-zinc-800 transition-colors"
          title={`Rotate (Current: ${rotation}°)`}
        >
          <RotateCw className="w-3.5 h-3.5" />
        </button>

        <button
          type="button"
          onClick={onResetView}
          className="p-1.5 rounded-md hover:bg-zinc-800 transition-colors"
          title="Reset Zoom & Pan"
        >
          <Maximize2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
