"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Check,
  CheckCheck,
  Copy,
  Download,
  FileCode,
  Sparkles,
} from "lucide-react";

import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { ExportMenu } from "@/components/ui/ExportMenu";
import { ExtractedField } from "@/components/ui/ExtractedField";
import { LineItemsTable } from "@/components/ui/LineItemsTable";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";

import { ReviewToggle } from "@/components/ui/ReviewToggle";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { DemoPill } from "@/components/ui/DemoPill";
import { useReviewProgress } from "@/hooks/useReviewProgress";
import {
  LineItem,
  SCALAR_FIELDS,
  ScalarFieldName,
  ValidationScore,
} from "@/lib/types";
import { formatCurrency } from "@/lib/utils";
import {
  selectUnresolvedCount,
  useDocumentStore,
} from "@/store/useDocumentStore";

export const DataExtractorPanel: React.FC = () => {
  const file = useDocumentStore((state) => state.file);
  const isProcessing = useDocumentStore((state) => state.isProcessing);
  const extractedData = useDocumentStore((state) => state.extractedData);
  const isReviewMode = useDocumentStore((state) => state.isReviewMode);
  const error = useDocumentStore((state) => state.error);
  const resolvedFields = useDocumentStore((state) => state.resolvedFields);
  const currentStage = useDocumentStore((state) => state.currentStage);


  const toggleReviewMode = useDocumentStore((state) => state.toggleReviewMode);
  const processFile = useDocumentStore((state) => state.processFile);
  const updateFieldValue = useDocumentStore((state) => state.updateFieldValue);
  const updateLineItemValue = useDocumentStore((state) => state.updateLineItemValue);
  const approveAll = useDocumentStore((state) => state.approveAll);

  const unresolvedCount = useDocumentStore(selectUnresolvedCount);
  const progress = useReviewProgress();

  const [copied, setCopied] = useState(false);

  const handleCopyJson = () => {
    if (!extractedData) return;
    const jsonStr = JSON.stringify(extractedData.extracted_data, null, 2);
    navigator.clipboard.writeText(jsonStr);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJson = () => {
    if (!extractedData) return;
    const jsonStr = JSON.stringify(extractedData.extracted_data, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${extractedData.extracted_data.invoice_number || "invoice"}_extracted.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getMetric = (fieldName: string): ValidationScore | undefined => {
    return extractedData?.validation_metrics.find((m) => m.field_name === fieldName);
  };

  return (
    <div className="w-full h-full bg-panel border-l border-subtle overflow-y-auto flex flex-col">
      <AnimatePresence mode="wait">
        {/* State 1: Error Banner */}
        {error ? (
          <motion.div
            key="error-state"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="p-6 flex flex-col gap-4"
          >
            <ErrorBanner
              message={error.message}
              code={error.code}
              onRetry={processFile}
            />
          </motion.div>
        ) : isProcessing ? (
          /* State 2: Processing Skeleton */
          <motion.div
            key="loading-state"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="w-full h-full"
          >
            <LoadingSkeleton currentStage={currentStage || undefined} />
          </motion.div>
        ) : extractedData ? (
          /* State 3: Extracted Document Workspace */
          <motion.div
            key="success-state"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col min-h-full"
          >
            {/* Sticky Panel Header */}
            <header className="glass-header sticky top-0 z-20 px-6 py-4 border-b border-subtle flex flex-col gap-3">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <h1 className="text-lg font-semibold text-bright tracking-tight truncate">
                    {extractedData.extracted_data.vendor_name || "Unknown Vendor"}
                  </h1>
                  <p className="text-xs font-mono text-muted truncate">
                    Invoice: {extractedData.extracted_data.invoice_number || "—"}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <DemoPill source={extractedData.source} />
                  <StatusBadge status={extractedData.overall_status} />
                </div>
              </div>

              {/* Review Switch & Progress Bar */}
              <div className="pt-2 border-t border-white/5 flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <ReviewToggle
                    isReviewMode={isReviewMode}
                    onToggle={toggleReviewMode}
                    unresolvedCount={unresolvedCount}
                  />
                  {isReviewMode && (
                    <span className="text-[11px] font-mono text-muted">
                      {progress.resolved} of {progress.total} resolved ({progress.percent}%)
                    </span>
                  )}
                </div>

                {/* Progress Bar when Review Mode is active */}
                {isReviewMode && progress.total > 0 && (
                  <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-accent-green"
                      initial={{ width: 0 }}
                      animate={{ width: `${progress.percent}%` }}
                      transition={{ duration: 0.3, ease: "easeOut" }}
                    />
                  </div>
                )}
              </div>
            </header>

            {/* Scrollable Data Body */}
            <div className="p-6 flex flex-col gap-6 flex-1">
              {/* 7 Core Scalar Fields Grid */}
              <section aria-label="Invoice Metadata" className="flex flex-col gap-2.5">
                <h3 className="text-xs uppercase tracking-wider font-semibold text-muted">
                  Document Entities
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                  {SCALAR_FIELDS.map((field) => {
                    const score = getMetric(field.key);
                    const val = extractedData.extracted_data[field.key];
                    const isResolved = Boolean(resolvedFields[field.key]);

                    return (
                      <ExtractedField
                        key={field.key}
                        label={field.label}
                        value={val}
                        validationScore={score}
                        isReviewMode={isReviewMode}
                        inputType={field.type}
                        isResolved={isResolved}
                        onChange={(newVal) =>
                          updateFieldValue(
                            field.key as ScalarFieldName,
                            newVal
                          )
                        }
                      />
                    );
                  })}
                </div>
              </section>

              {/* Line Items Table */}
              <section aria-label="Invoice Line Items">
                <LineItemsTable
                  items={extractedData.extracted_data.line_items}
                  currency={extractedData.extracted_data.currency}
                  score={getMetric("line_items")}
                  isReviewMode={isReviewMode}
                  resolvedFields={resolvedFields}
                  onChange={(index: number, prop: keyof LineItem, val: string) =>
                    updateLineItemValue(index, prop, val)
                  }
                />
              </section>

              {/* Totals Summary Card */}
              <section
                aria-label="Financial Totals"
                className="p-4 rounded-xl border border-white/5 bg-panel/60 flex flex-col gap-2 mt-auto"
              >
                <div className="flex justify-between text-xs text-muted">
                  <span>Tax Total</span>
                  <span className="font-mono tabular-nums text-bright">
                    {formatCurrency(
                      extractedData.extracted_data.tax_amount,
                      extractedData.extracted_data.currency
                    )}
                  </span>
                </div>
                <div className="flex justify-between text-sm font-semibold text-bright pt-2 border-t border-white/5">
                  <span>Grand Total</span>
                  <span className="font-mono tabular-nums text-base text-bright">
                    {formatCurrency(
                      extractedData.extracted_data.total_amount,
                      extractedData.extracted_data.currency
                    )}
                  </span>
                </div>
              </section>
            </div>

            {/* Bottom Sticky Action Bar */}
            <footer className="sticky bottom-0 z-20 px-6 py-3.5 glass-panel border-t border-subtle flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleCopyJson}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-muted hover:text-bright hover:bg-white/5 border border-white/5 transition-colors"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-accent-green" />
                      <span className="text-accent-green">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy JSON</span>
                    </>
                  )}
                </button>

                <ExportMenu />
              </div>

              <button
                type="button"
                onClick={approveAll}
                disabled={extractedData.overall_status === "APPROVED"}
                className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  extractedData.overall_status === "APPROVED"
                    ? "bg-accent-green/20 text-accent-green cursor-default"
                    : "bg-accent-green text-app hover:bg-accent-green/90 shadow-sm"
                }`}
              >
                <CheckCheck className="w-3.5 h-3.5" />
                <span>{extractedData.overall_status === "APPROVED" ? "Approved" : "Approve All"}</span>
              </button>
            </footer>
          </motion.div>
        ) : file ? (
          /* State 5: File selected but not processed */
          <motion.div
            key="file-ready-state"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="w-full h-full flex flex-col items-center justify-center p-8 text-center"
          >
            <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 mb-4 text-muted">
              <Sparkles className="w-8 h-8 text-accent-amber" />
            </div>
            <h3 className="text-sm font-semibold text-bright mb-1">
              Document ingested and ready
            </h3>
            <p className="text-xs text-muted max-w-xs mb-6">
              Launch multi-agent OCR spatial mapping, translation, and math verification.
            </p>
            <button
              type="button"
              onClick={processFile}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-bright text-app hover:bg-bright/90 shadow-lg transition-all"
            >
              <Sparkles className="w-4 h-4 fill-current" />
              Run extraction
            </button>
          </motion.div>
        ) : (
          /* State 4: Idle state */
          <motion.div
            key="idle-state"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="w-full h-full flex flex-col items-center justify-center p-8 text-center"
          >
            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 mb-4 text-muted/60">
              <FileCode className="w-8 h-8" />
            </div>
            <h3 className="text-sm font-medium text-bright/80 mb-1">
              Extracted data will appear here
            </h3>
            <p className="text-xs text-muted max-w-xs">
              Drop any multilingual invoice in the left pane to begin automatic extraction.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DataExtractorPanel;
