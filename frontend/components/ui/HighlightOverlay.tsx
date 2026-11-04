"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { BoundingBox } from "@/lib/types";

interface HighlightOverlayProps {
  boxes: BoundingBox[];
  currentPage: number;
  activeField: string | null;
  onSelectField?: (fieldName: string) => void;
  onHoverField?: (fieldName: string | null) => void;
}

export function HighlightOverlay({
  boxes,
  currentPage,
  activeField,
  onSelectField,
  onHoverField,
}: HighlightOverlayProps): React.JSX.Element {
  const pageBoxes = boxes.filter((b) => b.page === currentPage);

  if (pageBoxes.length === 0) {
    return <div className="pointer-events-none absolute inset-0" />;
  }

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      {pageBoxes.map((box, index) => {
        let top = box.y > 1 ? box.y / 10 : box.y * 100;
        let left = box.x > 1 ? box.x / 10 : box.x * 100;
        let height = box.height > 1 ? box.height / 10 : box.height * 100;
        let width = box.width > 1 ? box.width / 10 : box.width * 100;

        if (box.box_2d) {
          const [ymin, xmin, ymax, xmax] = box.box_2d;
          top = ymin / 10;
          left = xmin / 10;
          height = (ymax - ymin) / 10;
          width = (xmax - xmin) / 10;
        }

        const fieldName = box.field_name || box.label || `field-${index}`;
        const isActive = activeField === fieldName;
        const isHovered = activeField === fieldName;

        // Color coding based on field type / confidence
        const isWarning = (box.confidence ?? 1.0) < 0.8;
        const borderColor = isActive
          ? "border-cyan-400"
          : isWarning
          ? "border-amber-400"
          : "border-emerald-400/80";
        const bgColor = isActive
          ? "bg-cyan-500/20"
          : isWarning
          ? "bg-amber-500/15"
          : "bg-emerald-500/10";

        return (
          <motion.div
            key={`${fieldName}-${box.page}-${index}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{
              opacity: isActive ? 1 : 0.75,
              scale: isActive ? 1.01 : 1,
            }}
            transition={{ duration: 0.15 }}
            style={{
              top: `${top}%`,
              left: `${left}%`,
              height: `${Math.max(height, 1.2)}%`,
              width: `${Math.max(width, 1.5)}%`,
            }}
            className={`absolute pointer-events-auto cursor-pointer rounded border-2 transition-all ${borderColor} ${bgColor} ${
              isActive ? "shadow-[0_0_12px_rgba(6,182,212,0.6)] z-30" : "hover:opacity-100 z-10"
            }`}
            onClick={() => onSelectField?.(fieldName)}
            onMouseEnter={() => onHoverField?.(fieldName)}
            onMouseLeave={() => onHoverField?.(null)}
          >
            {/* Label pill on hover or active */}
            <AnimatePresence>
              {(isActive || isHovered) && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  className="absolute -top-6 left-0 flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-medium text-white bg-zinc-900/90 border border-zinc-700 shadow-lg whitespace-nowrap z-40 pointer-events-none"
                >
                  <span className="text-cyan-300 font-semibold">{box.label || fieldName}</span>
                  {box.text && (
                    <span className="text-zinc-400 border-l border-zinc-700 pl-1.5 max-w-[120px] truncate">
                      {box.text}
                    </span>
                  )}
                  {typeof box.confidence === "number" && (
                    <span
                      className={`text-[9px] ${
                        box.confidence >= 0.9
                          ? "text-emerald-400"
                          : box.confidence >= 0.75
                          ? "text-amber-400"
                          : "text-rose-400"
                      }`}
                    >
                      {Math.round(box.confidence * 100)}%
                    </span>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        );
      })}
    </div>
  );
}
