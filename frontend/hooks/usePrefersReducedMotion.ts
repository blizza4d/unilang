"use client";

import { useSyncExternalStore } from "react";

function subscribe(callback: () => void): () => void {
  if (typeof window === "undefined") {
    return () => {};
  }

  const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const handleMediaChange = () => callback();

  mediaQuery.addEventListener("change", handleMediaChange);
  window.addEventListener("storage", callback);

  return () => {
    mediaQuery.removeEventListener("change", handleMediaChange);
    window.removeEventListener("storage", callback);
  };
}

function getSnapshot(): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  // Check in-app override first
  try {
    const override = localStorage.getItem("datanova_reduced_motion");
    if (override !== null) {
      return override === "true";
    }
  } catch {
    // LocalStorage unavailable in sandbox
  }
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function getServerSnapshot(): boolean {
  return false;
}

export function usePrefersReducedMotion(): boolean {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

export function setInAppReducedMotion(value: boolean | null): void {
  if (typeof window === "undefined") return;
  try {
    if (value === null) {
      localStorage.removeItem("datanova_reduced_motion");
    } else {
      localStorage.setItem("datanova_reduced_motion", value ? "true" : "false");
    }
    window.dispatchEvent(new Event("storage"));
  } catch {
    // LocalStorage unavailable
  }
}
