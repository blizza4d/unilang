"use client";

import React, { useId, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { AlertTriangle, CheckCircle, UserCheck, Copy, Check } from "lucide-react";
import { ValidationScore } from "@/lib/types";
import { ConfidenceRing } from "@/components/ui/ConfidenceRing";
import { useDocumentStore } from "@/store/useDocumentStore";

export interface ExtractedFieldProps {
  label: string;
  value: string | number;
  validationScore: ValidationScore | undefined;
  isReviewMode: boolean;
  onChange: (value: string) => void;
  inputType?: "text" | "number" | "date";
  isResolved: boolean;
  fieldKey?: string;
}

export const ExtractedField: React.FC<ExtractedFieldProps> = React.memo(
  ({
    label,
    value,
    validationScore,
    isReviewMode,
    onChange,
    inputType = "text",
    isResolved,
    fieldKey,
  }) => {
    const inputId = useId();
    const shouldReduceMotion = useReducedMotion();
    const setActiveField = useDocumentStore((state) => state.setActiveField);
    const [copied, setCopied] = useState(false);

    const needsReview = validationScore?.needs_review ?? false;
    const confidence = validationScore?.confidence_score ?? 1.0;
    const reasoning = validationScore?.reasoning ?? "";
    const isFlaggedUnresolved = isReviewMode && needsReview && !isResolved;
    const isFlaggedResolved = isReviewMode && needsReview && isResolved;

    const displayPlaceholder =
      needsReview && (value === "" || value === 0)
        ? "Not found in document"
        : "—";

    let containerStyle = "group border border-white/5 bg-panel/50 hover:bg-white/[0.02]";
    if (isFlaggedUnresolved) {
      containerStyle =
        "group ring-2 ring-accent-amber/50 bg-accent-amber/10 border-accent-amber/30 " +
        (shouldReduceMotion ? "" : "animate-pulse");
    } else if (isFlaggedResolved) {
      containerStyle = "group ring-1 ring-accent-green/40 bg-accent-green/5 border-accent-green/30";
    }

    const handleChange = (rawText: string) => {
      if (inputType === "number") {
        // Normalize European decimal commas e.g. "12,50" -> "12.50"
        let normalized = rawText;
        if (rawText.includes(",") && !rawText.includes(".")) {
          normalized = rawText.replace(",", ".");
        }
        onChange(normalized);
      } else {
        onChange(rawText);
      }
    };

    const handleFocus = () => {
      if (fieldKey && setActiveField) {
        setActiveField(fieldKey);
      }
    };

    const handleBlur = () => {
      if (setActiveField) {
        setActiveField(null);
      }
    };

    const handleCopy = (e: React.MouseEvent) => {
      e.stopPropagation();
      if (value === undefined || value === null || value === "") return;
      navigator.clipboard.writeText(String(value));
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    };

    return (
      <div
        className={`p-3 rounded-xl transition-all duration-300 ${containerStyle}`}
        onMouseEnter={handleFocus}
        onMouseLeave={handleBlur}
      >
        <div className="flex items-center justify-between gap-3">
          <label
            htmlFor={inputId}
            className="text-xs uppercase tracking-wider font-semibold text-muted select-none shrink-0"
          >
            {label}
          </label>

          <div className="flex items-center gap-1.5 flex-1 justify-end min-w-0">
            <input
              id={inputId}
              type={inputType === "number" ? "text" : inputType}
              inputMode={inputType === "number" ? "decimal" : undefined}
              value={value ?? ""}
              placeholder={displayPlaceholder}
              onFocus={handleFocus}
              onBlur={handleBlur}
              onChange={(e) => handleChange(e.target.value)}
              className={`w-full max-w-[240px] text-right bg-transparent border-none focus:ring-0 outline-none text-bright text-sm transition-colors ${
                inputType === "number" ? "font-mono tabular-nums" : ""
              } placeholder:text-muted/60`}
            />

            {/* Quick-copy button */}
            {value !== "" && value !== undefined && value !== null && (
              <button
                type="button"
                onClick={handleCopy}
                className="opacity-0 group-hover:opacity-100 focus:opacity-100 p-1 rounded text-zinc-500 hover:text-zinc-200 transition-opacity shrink-0"
                title="Copy value"
                aria-label={`Copy ${label}`}
              >
                {copied ? (
                  <Check className="w-3.5 h-3.5 text-accent-green" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </button>
            )}

            {isReviewMode && (
              <div className="flex items-center gap-1.5 shrink-0">
                <AnimatePresence mode="wait">
                  {isFlaggedUnresolved && (
                    <motion.div
                      key="alert-icon"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ duration: 0.2 }}
                      title={`Confidence: ${Math.round(confidence * 100)}% - Review required`}
                    >
                      <AlertTriangle className="w-4 h-4 text-accent-amber shrink-0" />
                    </motion.div>
                  )}

                  {isFlaggedResolved && (
                    <motion.div
                      key="resolved-icon"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ duration: 0.2 }}
                      title="Resolved by human reviewer"
                    >
                      <CheckCircle className="w-4 h-4 text-accent-green shrink-0" />
                    </motion.div>
                  )}

                  {!needsReview && (
                    <motion.div
                      key="verified-icon"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.2 }}
                      className="flex items-center gap-1.5"
                      title={`AI Verified: ${Math.round(confidence * 100)}%`}
                    >
                      <CheckCircle className="w-3.5 h-3.5 text-accent-green shrink-0" />
                      <ConfidenceRing
                        score={confidence}
                        size={22}
                        needsReview={false}
                      />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}
          </div>
        </div>

        {/* Explainability drawer for flagged fields */}
        {isReviewMode && needsReview && reasoning && (
          <div
            className={`mt-2 pt-2 border-t text-[11px] font-mono leading-relaxed transition-colors ${
              isResolved
                ? "border-accent-green/20 text-accent-green"
                : "border-accent-amber/20 text-accent-amber"
            }`}
          >
            <div className="flex items-center gap-1.5 font-sans font-medium text-xs mb-0.5">
              {isResolved ? (
                <>
                  <UserCheck className="w-3.5 h-3.5 shrink-0" />
                  <span>Review Complete: Verified & Overridden</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  <span>Validation Warning:</span>
                </>
              )}
            </div>
            <p className="opacity-90">{reasoning}</p>
          </div>
        )}
      </div>
    );
  }
);

ExtractedField.displayName = "ExtractedField";
