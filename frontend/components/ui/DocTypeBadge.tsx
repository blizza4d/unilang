"use client";

import React from "react";
import { DocType } from "@/lib/types";

interface DocTypeBadgeProps {
  docType: DocType;
  confidence?: number;
  className?: string;
}

const DOC_TYPE_META: Record<DocType, { label: string; icon: string; bg: string; text: string }> = {
  invoice: { label: "Commercial Invoice", icon: "📄", bg: "bg-blue-500/10", text: "text-blue-400" },
  receipt: { label: "POS Receipt", icon: "🧾", bg: "bg-emerald-500/10", text: "text-emerald-400" },
  purchase_order: { label: "Purchase Order", icon: "📋", bg: "bg-purple-500/10", text: "text-purple-400" },
  credit_note: { label: "Credit Note", icon: "💳", bg: "bg-amber-500/10", text: "text-amber-400" },
  bank_statement: { label: "Bank Statement", icon: "🏦", bg: "bg-cyan-500/10", text: "text-cyan-400" },
  utility_bill: { label: "Utility Bill", icon: "⚡", bg: "bg-yellow-500/10", text: "text-yellow-400" },
  delivery_note: { label: "Delivery Note", icon: "📦", bg: "bg-teal-500/10", text: "text-teal-400" },
  expense_report: { label: "Expense Report", icon: "💼", bg: "bg-indigo-500/10", text: "text-indigo-400" },
  id_document: { label: "Identity Document", icon: "🪪", bg: "bg-rose-500/10", text: "text-rose-400" },
  contract_summary: { label: "Legal Contract", icon: "📜", bg: "bg-violet-500/10", text: "text-violet-400" },
  unknown: { label: "Unclassified", icon: "❓", bg: "bg-zinc-500/10", text: "text-zinc-400" },
};

export default function DocTypeBadge({ docType, confidence, className = "" }: DocTypeBadgeProps) {
  const meta = DOC_TYPE_META[docType] || DOC_TYPE_META.unknown;

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border border-white/5 backdrop-blur-sm ${meta.bg} ${meta.text} ${className}`}
    >
      <span className="text-sm">{meta.icon}</span>
      <span>{meta.label}</span>
      {confidence !== undefined && (
        <span className="opacity-75 text-[10px] ml-0.5">({Math.round(confidence * 100)}%)</span>
      )}
    </div>
  );
}
