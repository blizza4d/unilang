"use client";

import React, { useId } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { AlertTriangle, CheckCircle, UserCheck } from "lucide-react";
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

    const needsReview = validationScore?.needs_review ?? false;
    const confidence = validationScore?.confidence_score ?? 1.0;
    const reasoning = validationScore?.reasoning ?? "";
    const isFlaggedUnresolved = isReviewMode && needsReview && !isResolved;
    const isFlaggedResolved = isReviewMode && needsReview && isResolved;

    const displayPlaceholder =
      needsReview && (value === "" || value === 0)
        ? "Not found in document"
        : "—";

    let containerStyle = "border border-white/5 bg-panel/50 hover:bg-white/[0.02]";
    if (isFlaggedUnresolved) {
      containerStyle =
        "ring-2 ring-accent-amber/50 bg-accent-amber/10 border-accent-amber/30 " +
        (shouldReduceMotion ? "" : "animate-pulse");
    } else if (isFlaggedResolved) {
      containerStyle = "ring-1 ring-accent-green/40 bg-accent-green/5 border-accent-green/30";
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

          <div className="flex items-center gap-2 flex-1 justify-end min-w-0">
            <input
              id={inputId}
              type={inputType === "number" ? "text" : inputType}
              inputMode={inputType === "number" ? "decimal" : undefined}
              value={value ?? ""}
              placeholder={displayPlaceholder}
              onFocus={handleFocus}
              onBlur={handleBlur}
              onChange={(e) => handleChange(e.target.value)}
              className={`w-full max-w-[260px] text-right bg-transparent border-none focus:ring-0 outline-none text-bright text-sm transition-colors ${
                inputType === "number" ? "font-mono tabular-nums" : ""
              } placeholder:text-muted/60`}
            />

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

        <AnimatePresence>
          {isFlaggedUnresolved && reasoning && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: shouldReduceMotion ? 0 : 0.25, ease: "easeOut" }}
              className="overflow-hidden"
            >
              <div
                className="mt-2 pt-2 border-t border-accent-amber/20 flex items-start gap-1.5 text-xs text-accent-amber"
                aria-live="polite"
              >
                <AlertTriangle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                <span className="font-mono leading-relaxed">{reasoning}</span>
              </div>
            </motion.div>
          )}

          {isFlaggedResolved && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: shouldReduceMotion ? 0 : 0.25, ease: "easeOut" }}
              className="overflow-hidden"
            >
              <div
                className="mt-2 pt-2 border-t border-accent-green/20 flex items-center gap-1.5 text-xs text-accent-green font-medium"
                aria-live="polite"
              >
                <UserCheck className="w-3.5 h-3.5 shrink-0" />
                <span>Corrected by reviewer</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }
);

ExtractedField.displayName = "ExtractedField";

export default ExtractedField;
