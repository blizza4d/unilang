"use client";

import React from "react";
import { DocType } from "@/lib/types";

interface DocTypePickerProps {
  selectedType: DocType;
  onSelectType: (type: DocType) => void;
  className?: string;
}

const SUPPORTED_OPTIONS: { type: DocType; label: string }[] = [
  { type: "invoice", label: "Commercial Invoice" },
  { type: "receipt", label: "POS / Retail Receipt" },
  { type: "purchase_order", label: "Purchase Order (PO)" },
  { type: "credit_note", label: "Credit Note / Memo" },
  { type: "bank_statement", label: "Bank Account Statement" },
  { type: "utility_bill", label: "Utility / Telecom Bill" },
  { type: "delivery_note", label: "Delivery Note / Packing Slip" },
  { type: "expense_report", label: "Employee Expense Report" },
  { type: "id_document", label: "Government ID / Passport" },
  { type: "contract_summary", label: "Contract Agreement Summary" },
];

export default function DocTypePicker({
  selectedType,
  onSelectType,
  className = "",
}: DocTypePickerProps) {
  return (
    <div className={`relative inline-block ${className}`}>
      <label htmlFor="doc-type-select" className="sr-only">
        Select Document Type
      </label>
      <select
        id="doc-type-select"
        value={selectedType}
        onChange={(e) => onSelectType(e.target.value as DocType)}
        className="bg-zinc-900 border border-zinc-700 hover:border-zinc-500 rounded-lg px-3 py-1.5 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-accent transition-colors cursor-pointer"
      >
        {SUPPORTED_OPTIONS.map((opt) => (
          <option key={opt.type} value={opt.type} className="bg-zinc-900 text-zinc-100">
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
