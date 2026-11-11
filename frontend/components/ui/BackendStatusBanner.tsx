"use client";

import React, { useEffect, useState, useRef } from "react";
import { AlertTriangle, CheckCircle2, RefreshCw, X, ExternalLink, Loader2 } from "lucide-react";
import { getBackendStatus } from "@/lib/config";

export function BackendStatusBanner(): React.JSX.Element | null {
  const [status, setStatus] = useState<"checking" | "online" | "unreachable" | "mixed-content" | "waking-up">("checking");
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [isDismissed, setIsDismissed] = useState(false);
  const [apiUrl, setApiUrl] = useState("");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const checkTimerRef = useRef<NodeJS.Timeout | null>(null);
  const elapsedTimerRef = useRef<NodeJS.Timeout | null>(null);

  const checkConnectivity = async () => {
    const backendStatus = getBackendStatus();
    setApiUrl(backendStatus.apiUrl);

    if (backendStatus.isMixedContent) {
      setStatus("mixed-content");
      return;
    }

    // Start 2.5s waking-up detection timer
    if (checkTimerRef.current) clearTimeout(checkTimerRef.current);
    checkTimerRef.current = setTimeout(() => {
      setStatus((curr) => (curr === "checking" ? "waking-up" : curr));
    }, 2500);

    const startTime = performance.now();
    try {
      const res = await fetch(`${backendStatus.apiUrl}/health`, {
        method: "GET",
        headers: { Accept: "application/json" },
        cache: "no-store",
      });

      if (checkTimerRef.current) clearTimeout(checkTimerRef.current);

      if (res.ok) {
        setLatencyMs(Math.round(performance.now() - startTime));
        setStatus("online");
      } else {
        setStatus("unreachable");
      }
    } catch {
      if (checkTimerRef.current) clearTimeout(checkTimerRef.current);
      setStatus("unreachable");
    }
  };

  useEffect(() => {
    checkConnectivity();
    const interval = setInterval(checkConnectivity, 30000);
    return () => {
      clearInterval(interval);
      if (checkTimerRef.current) clearTimeout(checkTimerRef.current);
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    };
  }, []);

  useEffect(() => {
    if (status === "waking-up") {
      elapsedTimerRef.current = setInterval(() => {
        setElapsedSeconds((s) => s + 1);
      }, 1000);
    } else {
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
      setElapsedSeconds(0);
    }
    return () => {
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    };
  }, [status]);

  if (isDismissed) {
    return (
      <div data-testid="backend-status-banner" className="hidden" aria-hidden="true" data-status={status} />
    );
  }

  // Waking-up Cold Start Banner (Phase Q5)
  if (status === "waking-up") {
    return (
      <aside
        data-testid="backend-status-banner"
        data-status="waking-up"
        aria-label="Server waking up notification"
        className="w-full bg-cyan-950/40 border-b border-cyan-500/30 px-4 py-2.5 flex flex-col sm:flex-row items-center justify-between text-xs text-cyan-200 z-50 animate-in fade-in duration-300"
      >
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <Loader2 className="w-4 h-4 text-cyan-400 shrink-0 animate-spin" />
          <div>
            <span className="font-semibold text-cyan-300">Extraction server is waking up:</span>{" "}
            <span>
              Free tier container cold start (~40s). Server has been waking for {elapsedSeconds}s. Your document is queued.
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 mt-2 sm:mt-0 w-full sm:w-auto justify-end">
          <div className="w-24 bg-cyan-950/60 rounded-full h-1.5 overflow-hidden border border-cyan-500/30">
            <div
              className="bg-cyan-400 h-full rounded-full transition-all duration-1000"
              style={{ width: `${Math.min((elapsedSeconds / 45) * 100, 95)}%` }}
            />
          </div>
          <button
            type="button"
            onClick={() => setIsDismissed(true)}
            className="px-2 py-0.5 rounded bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-200 border border-cyan-500/30 transition-colors"
          >
            Cancel
          </button>
        </div>
      </aside>
    );
  }

  // Unreachable or Mixed-Content Alert Banner
  if (status === "unreachable" || status === "mixed-content") {
    return (
      <aside
        data-testid="backend-status-banner"
        data-status={status}
        aria-label="Backend status warning"
        className="w-full bg-amber-500/10 border-b border-amber-500/30 px-4 py-2 flex flex-wrap items-center justify-between text-xs text-amber-200 z-50"
      >
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
                : `Cannot connect to extraction server at ${apiUrl}. Verify backend service is online.`}
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
            aria-label="Dismiss banner"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </aside>
    );
  }

  // Online state: Render persistent accessible test hook
  return (
    <div
      data-testid="backend-status-banner"
      data-status="online"
      className="hidden"
      aria-hidden="true"
      title={`Backend Online (${latencyMs ?? 0}ms)`}
    />
  );
}
