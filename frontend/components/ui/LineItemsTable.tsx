"use client";

import React from "react";
import { AlertTriangle, Calculator } from "lucide-react";
import { LineItem, ValidationScore } from "@/lib/types";
import { formatCurrency } from "@/lib/utils";

export interface LineItemsTableProps {
  items: LineItem[];
  currency: string;
  score: ValidationScore | undefined;
  isReviewMode: boolean;
  resolvedFields: Record<string, boolean>;
  onChange: (index: number, prop: keyof LineItem, value: string) => void;
}

export const LineItemsTable: React.FC<LineItemsTableProps> = ({
  items,
  currency,
  score,
  isReviewMode,
  resolvedFields,
  onChange,
}) => {
  const isSectionFlagged = score?.needs_review ?? false;
  const isSectionResolved = Object.keys(resolvedFields).some((k) =>
    k.startsWith("line_items")
  );
  const showSectionWarning = isReviewMode && isSectionFlagged && !isSectionResolved;

  const subtotal = items.reduce(
    (acc, it) => acc + (typeof it.total_price === "number" ? it.total_price : 0),
    0
  );

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs uppercase tracking-wider font-semibold text-muted flex items-center gap-1.5">
          <Calculator className="w-3.5 h-3.5 text-muted" />
          Line Items ({items.length})
        </h3>
      </div>

      {/* Section-level Math Alert */}
      {showSectionWarning && score?.reasoning && (
        <div className="p-3 rounded-xl bg-accent-amber/10 border border-accent-amber/30 text-accent-amber text-xs flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <span className="font-mono leading-relaxed">{score.reasoning}</span>
        </div>
      )}

      {/* Table Container */}
      <div className="w-full overflow-x-auto rounded-xl border border-white/5 bg-panel/40">
        <table className="w-full text-left text-xs text-bright border-collapse">
          <thead>
            <tr className="border-b border-white/5 bg-white/[0.02] text-muted uppercase tracking-wider text-[11px] font-semibold">
              <th className="py-2.5 px-3 min-w-[180px]">Description</th>
              <th className="py-2.5 px-3 text-right w-20">Qty</th>
              <th className="py-2.5 px-3 text-right w-28">Unit Price</th>
              <th className="py-2.5 px-3 text-right w-28">Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {items.length === 0 ? (
              <tr>
                <td
                  colSpan={4}
                  className="py-8 text-center text-muted italic font-normal"
                >
                  No line items detected.
                </td>
              </tr>
            ) : (
              items.map((item, idx) => {
                const rowMathMismatch =
                  Math.abs(item.quantity * item.unit_price - item.total_price) > 0.01;
                const isRowEdited =
                  resolvedFields[`line_items.${idx}.description`] ||
                  resolvedFields[`line_items.${idx}.quantity`] ||
                  resolvedFields[`line_items.${idx}.unit_price`] ||
                  resolvedFields[`line_items.${idx}.total_price`];

                const isRowFlagged =
                  isReviewMode && rowMathMismatch && !isRowEdited;

                return (
                  <tr
                    key={`line-item-${idx}`}
                    className={`transition-colors duration-150 ${
                      isRowFlagged
                        ? "bg-accent-amber/10 ring-1 ring-inset ring-accent-amber/40 animate-pulse"
                        : "hover:bg-white/[0.02]"
                    }`}
                  >
                    {/* Description */}
                    <td className="py-2 px-3">
                      <input
                        type="text"
                        value={item.description}
                        placeholder="Item description"
                        onChange={(e) => onChange(idx, "description", e.target.value)}
                        className="w-full bg-transparent border-none outline-none focus:ring-0 text-bright text-xs placeholder:text-muted/40"
                      />
                    </td>

                    {/* Quantity */}
                    <td className="py-2 px-3 text-right">
                      <input
                        type="number"
                        inputMode="decimal"
                        step="any"
                        value={item.quantity}
                        onChange={(e) => onChange(idx, "quantity", e.target.value)}
                        className="w-full bg-transparent border-none outline-none focus:ring-0 text-bright text-right font-mono text-xs tabular-nums"
                      />
                    </td>

                    {/* Unit Price */}
                    <td className="py-2 px-3 text-right">
                      <input
                        type="number"
                        inputMode="decimal"
                        step="any"
                        value={item.unit_price}
                        onChange={(e) => onChange(idx, "unit_price", e.target.value)}
                        className="w-full bg-transparent border-none outline-none focus:ring-0 text-bright text-right font-mono text-xs tabular-nums"
                      />
                    </td>

                    {/* Total Price */}
                    <td className="py-2 px-3 text-right">
                      <input
                        type="number"
                        inputMode="decimal"
                        step="any"
                        value={item.total_price}
                        onChange={(e) => onChange(idx, "total_price", e.target.value)}
                        className={`w-full bg-transparent border-none outline-none focus:ring-0 text-right font-mono text-xs tabular-nums font-semibold ${
                          isRowFlagged ? "text-accent-amber" : "text-bright"
                        }`}
                      />
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
          {items.length > 0 && (
            <tfoot>
              <tr className="border-t border-white/10 bg-white/[0.02] font-semibold">
                <td colSpan={3} className="py-2.5 px-3 text-right text-muted uppercase text-[11px] tracking-wider">
                  Computed Subtotal
                </td>
                <td className="py-2.5 px-3 text-right font-mono text-xs text-bright tabular-nums">
                  {formatCurrency(subtotal, currency)}
                </td>
              </tr>
            </tfoot>
          )}
        </table>
      </div>
    </div>
  );
};

export default LineItemsTable;
