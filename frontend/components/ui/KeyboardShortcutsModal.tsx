"use client";

import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Keyboard, Command, FileText, Search, Play, CheckCircle } from "lucide-react";
import { Kbd } from "@/components/ui/Kbd";

interface ShortcutGroup {
  category: string;
  items: {
    label: string;
    description: string;
    keys: string[];
  }[];
}

const SHORTCUT_GROUPS: ShortcutGroup[] = [
  {
    category: "Navigation & Command",
    items: [
      {
        label: "Command Palette",
        description: "Search actions, features, and sample presets",
        keys: ["⌘", "K"],
      },
      {
        label: "Document History",
        description: "Open persistent document history sidebar",
        keys: ["⌘", "H"],
      },
      {
        label: "Batch Multi-File Queue",
        description: "Upload and inspect batch extraction queue",
        keys: ["⌘", "B"],
      },
      {
        label: "Shortcuts Cheat Sheet",
        description: "Toggle this keyboard shortcuts dialog",
        keys: ["?"],
      },
    ],
  },
  {
    category: "Pipeline & Review Actions",
    items: [
      {
        label: "Run Extraction",
        description: "Launch multi-agent OCR and extraction on file",
        keys: ["⌘", "↵"],
      },
      {
        label: "Toggle Review Mode",
        description: "Inspect discrepancies and visual bounding boxes",
        keys: ["R"],
      },
      {
        label: "Approve All Verified",
        description: "Approve all verified and human-reviewed fields",
        keys: ["⌘", "A"],
      },
      {
        label: "Dismiss / Clear",
        description: "Dismiss modal, clear error, or cancel focus",
        keys: ["Esc"],
      },
    ],
  },
  {
    category: "Document Canvas Navigation",
    items: [
      {
        label: "Next / Previous Page",
        description: "Navigate multi-page PDF documents",
        keys: ["[", "]"],
      },
      {
        label: "Zoom In / Out",
        description: "Adjust document viewing scale",
        keys: ["+", "−"],
      },
      {
        label: "Reset Zoom & Center",
        description: "Fit document to canvas viewport",
        keys: ["0"],
      },
    ],
  },
];

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function KeyboardShortcutsModal({
  isOpen,
  onClose,
}: KeyboardShortcutsModalProps): React.JSX.Element | null {
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        />

        {/* Modal Window */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          transition={{ duration: 0.15, ease: "easeOut" }}
          className="relative w-full max-w-xl rounded-2xl bg-[#111318] border border-white/10 shadow-2xl overflow-hidden z-10 flex flex-col max-h-[85vh]"
          role="dialog"
          aria-modal="true"
          aria-label="Keyboard Shortcuts"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/[0.02]">
            <div className="flex items-center gap-2 text-bright">
              <Keyboard className="w-5 h-5 text-cyan-400" />
              <h2 className="text-sm font-semibold tracking-wide">
                Keyboard Shortcuts
              </h2>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="p-1 rounded-lg text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
              title="Close (Esc)"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Body */}
          <div className="p-6 overflow-y-auto space-y-6">
            {SHORTCUT_GROUPS.map((group) => (
              <div key={group.category} className="space-y-2.5">
                <h3 className="text-[11px] font-mono uppercase tracking-wider text-muted">
                  {group.category}
                </h3>
                <div className="rounded-xl border border-white/5 bg-white/[0.01] divide-y divide-white/5">
                  {group.items.map((item) => (
                    <div
                      key={item.label}
                      className="flex items-center justify-between px-3.5 py-2.5 text-xs hover:bg-white/[0.02] transition-colors"
                    >
                      <div className="min-w-0 pr-4">
                        <div className="font-medium text-zinc-200">
                          {item.label}
                        </div>
                        <div className="text-[11px] text-zinc-500 truncate">
                          {item.description}
                        </div>
                      </div>
                      <div className="flex items-center gap-1 shrink-0">
                        {item.keys.map((k) => (
                          <Kbd key={k}>{k}</Kbd>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="px-6 py-3 border-t border-white/10 bg-white/[0.01] flex items-center justify-between text-[11px] font-mono text-zinc-500">
            <span>Tip: Press <Kbd>?</Kbd> anywhere to reopen</span>
            <span>Press <Kbd>Esc</Kbd> to dismiss</span>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
