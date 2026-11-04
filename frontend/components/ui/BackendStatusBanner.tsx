"use client";

import React, { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, RefreshCw, X, ExternalLink } from "lucide-react";
import { getBackendStatus } from "@/lib/config";

export function BackendStatusBanner(): React.JSX.Element | null {
  const [status, setStatus] = useState<"checking" | "online" | "unreachable" | "mixed-content">("checking");
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [isDismissed, setIsDismissed] = useState(false);
  const [apiUrl, setApiUrl] = useState("");

  const checkConnectivity = async () => {
    const backendStatus = getBackendStatus();
    setApiUrl(backendStatus.apiUrl);

    if (backendStatus.isMixedContent) {
      setStatus("mixed-content");
      return;
    }

    try {
      const startTime = performance.now();
      const res = await fetch(`${backendStatus.apiUrl}/health`, {
        method: "GET",
        headers: { Accept: "application/json" },
        cache: "no-store",
      });

      if (res.ok) {
        setLatencyMs(Math.round(performance.now() - startTime));
        setStatus("online");
      } else {
        setStatus("unreachable");
      }
    } catch {
      setStatus("unreachable");
    }
  };

  useEffect(() => {
    checkConnectivity();
    const interval = setInterval(checkConnectivity, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isDismissed || status === "online" || status === "checking") {
    return null;
  }

  return (
    <div className="w-full bg-amber-500/10 border-b border-amber-500/30 px-4 py-2 flex flex-wrap items-center justify-between text-xs text-amber-200 z-50">
      <div className="flex items-center gap-2">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
        <div>
          <span className="font-semibold text-amber-300">
            {status === "mixed-content"
              ? "Backend Configuration Required:"
              : "Backend Unreachable:"}
          </span>{" "}
          <span>
            {status === "mixed-content"
              ? `The app is running on HTTPS, but NEXT_PUBLIC_API_URL is defaulting to insecure HTTP (${apiUrl}). Browser blocked mixed-content requests.`
              : `Cannot connect to extraction server at ${apiUrl}. Verify the backend is running and CORS is configured.`}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3 mt-1 sm:mt-0">
        <button
          type="button"
          onClick={() => checkConnectivity()}
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 border border-amber-500/30 transition-colors"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Retry</span>
        </button>

        <a
          href="https://github.com/blizza4d/unilang/blob/main/docs/DEPLOYMENT.md"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-amber-300 underline hover:text-amber-100"
        >
          <span>Deployment Guide</span>
          <ExternalLink className="w-3 h-3" />
        </a>

        <button
          type="button"
          onClick={() => setIsDismissed(true)}
          className="p-1 rounded hover:bg-amber-500/20 text-amber-400 hover:text-amber-200 transition-colors"
          title="Dismiss banner"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
