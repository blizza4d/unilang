"use client";

import React from "react";
import { AlertOctagon, RotateCw, X } from "lucide-react";

export interface ErrorBannerProps {
  message: string;
  code?: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({
  message,
  code,
  onRetry,
  onDismiss,
  className = "",
}) => {
  return (
    <div
      role="alert"
      className={`glass-panel border-accent-red/40 bg-accent-red/10 p-4 rounded-xl flex items-start justify-between gap-3 ${className}`}
    >
      <div className="flex items-start gap-3">
        <AlertOctagon className="w-5 h-5 text-accent-red shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-bright">{message}</p>
          {code && (
            <p className="text-xs font-mono text-muted mt-0.5">Code: {code}</p>
          )}
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-white/10 hover:bg-white/15 text-bright border border-white/10 transition-colors"
          >
            <RotateCw className="w-3.5 h-3.5" />
            Retry
          </button>
        )}
        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            aria-label="Dismiss error"
            className="p-1 rounded-lg text-muted hover:text-bright hover:bg-white/10 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorBanner;
