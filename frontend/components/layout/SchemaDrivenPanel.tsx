"use client";

import React from "react";
import { DocTypeMetadata, GenericDocumentResponse } from "@/lib/types";
import { useDocumentStore } from "@/store/useDocumentStore";
import DataTable, { DataTableColumn } from "@/components/ui/DataTable";
import DocTypeBadge from "@/components/ui/DocTypeBadge";

interface SchemaDrivenPanelProps {
  metadata?: DocTypeMetadata;
  genericData?: GenericDocumentResponse | null;
  className?: string;
}

export default function SchemaDrivenPanel({
  metadata,
  genericData,
  className = "",
}: SchemaDrivenPanelProps) {
  const { updateValueAtPath, resolvedFields } = useDocumentStore();

  if (!genericData) {
    return (
      <div className={`p-6 text-center text-zinc-500 italic ${className}`}>
        No document data loaded.
      </div>
    );
  }

  const layout = metadata?.ui_layout || {
    sections: [
      {
        title: "Extracted Attributes",
        fields: Object.keys(genericData.data).filter((k) => !Array.isArray(genericData.data[k])),
      },
    ],
  };

  const handleScalarChange = (fieldPath: string, newVal: string) => {
    updateValueAtPath(fieldPath, newVal);
  };

  const handleTableChange = (tableName: string, rowIndex: number, columnKey: string, newVal: string | number) => {
    updateValueAtPath(`${tableName}.${rowIndex}.${columnKey}`, newVal);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Document Overview Header */}
      <div className="flex items-center justify-between p-4 bg-zinc-900/50 border border-zinc-800 rounded-xl backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <DocTypeBadge
            docType={genericData.doc_type}
            confidence={genericData.classification?.confidence}
          />
          <span className="text-xs text-zinc-400 font-mono">
            ID: {genericData.document_id.slice(0, 8)}...
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`px-2 py-0.5 rounded text-[11px] font-medium border ${
              genericData.overall_status === "APPROVED" || genericData.overall_status === "AUTOMATED_PASS"
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                : "bg-amber-500/10 text-amber-400 border-amber-500/20"
            }`}
          >
            {genericData.overall_status}
          </span>
        </div>
      </div>

      {/* Sections dynamically driven by schema */}
      {layout.sections.map((sec, sIdx) => (
        <section key={sIdx} className="space-y-3">
          <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider px-1">
            {sec.title}
          </h3>

          {/* Scalar fields grid */}
          {sec.fields && sec.fields.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {sec.fields.map((fieldKey) => {
                const val = genericData.data[fieldKey];
                const displayVal = val !== undefined && val !== null ? String(val) : "";
                const isResolved = resolvedFields[fieldKey];

                return (
                  <div
                    key={fieldKey}
                    className="p-3 bg-zinc-900/30 border border-zinc-800/80 rounded-lg space-y-1 hover:border-zinc-700 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <label
                        htmlFor={`field-${fieldKey}`}
                        className="text-[11px] font-medium text-zinc-400 capitalize"
                      >
                        {fieldKey.replace(/_/g, " ")}
                      </label>
                      {isResolved && (
                        <span className="text-[10px] text-emerald-400 font-mono">edited ✓</span>
                      )}
                    </div>
                    <input
                      id={`field-${fieldKey}`}
                      type="text"
                      value={displayVal}
                      onChange={(e) => handleScalarChange(fieldKey, e.target.value)}
                      className="w-full bg-zinc-950/60 border border-zinc-800 rounded px-2.5 py-1 text-xs text-zinc-100 focus:outline-none focus:border-accent font-mono transition-colors"
                    />
                  </div>
                );
              })}
            </div>
          )}

          {/* Table list fields */}
          {sec.table && (
            <div className="mt-2">
              <DataTable
                columns={(sec.columns || ["description", "quantity", "unit_price", "total_price"]).map((colKey) => ({
                  key: colKey,
                  header: colKey.replace(/_/g, " ").toUpperCase(),
                  type: colKey.includes("price") || colKey.includes("amount") || colKey.includes("balance") || colKey.includes("quantity")
                    ? "number"
                    : "text",
                  align: colKey.includes("price") || colKey.includes("amount") || colKey.includes("balance") || colKey.includes("quantity")
                    ? "right"
                    : "left",
                }))}
                data={(genericData.data[sec.table] as Record<string, unknown>[]) || []}
                onCellChange={(row, col, newVal) => handleTableChange(sec.table!, row, col, newVal)}
              />
            </div>
          )}
        </section>
      ))}
    </div>
  );
}
