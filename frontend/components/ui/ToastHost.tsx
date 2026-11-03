"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, AlertTriangle, AlertCircle, Info, X } from "lucide-react";
import { useToastStore, ToastItem } from "@/store/useToastStore";

export function ToastHost(): React.JSX.Element {
  const toasts = useToastStore((state) => state.toasts);
  const removeToast = useToastStore((state) => state.removeToast);

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none select-none">
      <AnimatePresence>
        {toasts.map((toast) => {
          const Icon =
            toast.type === "success"
              ? CheckCircle2
              : toast.type === "error"
              ? AlertCircle
              : toast.type === "warning"
              ? AlertTriangle
              : Info;

          const colorClasses =
            toast.type === "success"
              ? "border-emerald-500/40 bg-[#0f1914]/95 text-emerald-400"
              : toast.type === "error"
              ? "border-rose-500/40 bg-[#1c0f12]/95 text-rose-400"
              : toast.type === "warning"
              ? "border-amber-500/40 bg-[#1a140d]/95 text-amber-400"
              : "border-cyan-500/40 bg-[#0c151c]/95 text-cyan-400";

          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 15, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className={`pointer-events-auto rounded-xl border p-3 shadow-2xl flex items-start gap-2.5 backdrop-blur-md ${colorClasses}`}
            >
              <Icon className="w-4 h-4 mt-0.5 shrink-0" />
              <div className="min-w-0 flex-1">
                <div className="text-xs font-semibold text-zinc-100">
                  {toast.title}
                </div>
                {toast.description && (
                  <div className="text-[11px] text-zinc-400 mt-0.5 leading-tight">
                    {toast.description}
                  </div>
                )}
              </div>
              <button
                type="button"
                onClick={() => removeToast(toast.id)}
                className="p-1 rounded text-zinc-500 hover:text-white transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
