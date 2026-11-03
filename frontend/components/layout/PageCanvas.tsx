"use client";

import React, { useRef, useState, useCallback } from "react";
import { HighlightOverlay } from "@/components/ui/HighlightOverlay";
import type { BoundingBox } from "@/lib/types";

interface PageCanvasProps {
  imageUrl?: string;
  pdfUrl?: string;
  currentPage: number;
  zoom: number;
  rotation: number;
  pan: { x: number; y: number };
  boxes: BoundingBox[];
  activeField: string | null;
  onPanChange: (pan: { x: number; y: number }) => void;
  onSelectField?: (fieldName: string) => void;
  onHoverField?: (fieldName: string | null) => void;
}

export function PageCanvas({
  imageUrl,
  pdfUrl,
  currentPage,
  zoom,
  rotation,
  pan,
  boxes,
  activeField,
  onPanChange,
  onSelectField,
  onHoverField,
}: PageCanvasProps): React.JSX.Element {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const dragStartRef = useRef<{ startX: number; startY: number; initPanX: number; initPanY: number }>({
    startX: 0,
    startY: 0,
    initPanX: 0,
    initPanY: 0,
  });

  const handleMouseDown = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      // Only drag with left mouse click and when target is canvas background or image
      if (e.button !== 0) return;
      setIsDragging(true);
      dragStartRef.current = {
        startX: e.clientX,
        startY: e.clientY,
        initPanX: pan.x,
        initPanY: pan.y,
      };
    },
    [pan]
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!isDragging) return;
      const dx = e.clientX - dragStartRef.current.startX;
      const dy = e.clientY - dragStartRef.current.startY;
      onPanChange({
        x: dragStartRef.current.initPanX + dx,
        y: dragStartRef.current.initPanY + dy,
      });
    },
    [isDragging, onPanChange]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  return (
    <div
      ref={containerRef}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      className={`relative w-full h-full flex items-center justify-center overflow-hidden bg-[#0a0c10] select-none ${
        isDragging ? "cursor-grabbing" : "cursor-grab"
      }`}
    >
      <div
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom}) rotate(${rotation}deg)`,
          transformOrigin: "center center",
          transition: isDragging ? "none" : "transform 0.15s ease-out",
        }}
        className="relative max-w-full max-h-full flex items-center justify-center shadow-2xl rounded-lg"
      >
        {imageUrl ? (
          <div className="relative inline-block border border-zinc-800 rounded-md overflow-hidden bg-white shadow-2xl">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imageUrl}
              alt={`Document Page ${currentPage}`}
              className="max-h-[78vh] w-auto object-contain block pointer-events-none"
              draggable={false}
            />
            {/* 2D Bounding Box Overlay */}
            <HighlightOverlay
              boxes={boxes}
              currentPage={currentPage}
              activeField={activeField}
              onSelectField={onSelectField}
              onHoverField={onHoverField}
            />
          </div>
        ) : pdfUrl ? (
          <div className="relative w-[700px] h-[820px] bg-zinc-900 rounded border border-zinc-800 shadow-2xl overflow-hidden">
            <iframe
              src={`${pdfUrl}#page=${currentPage}&toolbar=0&navpanes=0`}
              title="PDF Document Viewer"
              className="w-full h-full border-0 pointer-events-auto"
            />
            {/* Overlay if boxes present on top of iframe */}
            <HighlightOverlay
              boxes={boxes}
              currentPage={currentPage}
              activeField={activeField}
              onSelectField={onSelectField}
              onHoverField={onHoverField}
            />
          </div>
        ) : (
          <div className="p-12 text-center text-zinc-500 font-mono text-sm">
            No document loaded
          </div>
        )}
      </div>
    </div>
  );
}
