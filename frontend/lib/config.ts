/**
 * Centralized Application Configuration & Runtime Endpoint Resolution
 *
 * Provides a single validated source of truth for backend API connectivity,
 * preventing mixed-content errors in production browser environments and
 * ensuring consistent header configuration across all fetch clients.
 */

export interface BackendConnectionStatus {
  apiUrl: string;
  isConfigured: boolean;
  isMixedContent: boolean;
  isHttps: boolean;
}

/**
 * Resolves the active backend API base URL with strict normalization.
 * Strips trailing slashes to prevent malformed double-slash route requests.
 */
export function getApiUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  if (envUrl && envUrl.trim().length > 0) {
    return envUrl.trim().replace(/\/+$/, "");
  }

  // Fallback for local development
  return "http://localhost:8000";
}

/**
 * Validates whether the application is running in an environment where
 * the backend is properly configured or blocked by browser security.
 */
export function getBackendStatus(): BackendConnectionStatus {
  const apiUrl = getApiUrl();
  const isBrowser = typeof window !== "undefined";
  const isHttps = isBrowser ? window.location.protocol === "https:" : false;

  // Check if browser is on HTTPS but API URL is HTTP (Mixed Content security violation)
  const isMixedContent = isHttps && apiUrl.startsWith("http://");

  // On production domains, localhost is considered unconfigured
  const isLocalhost = apiUrl.includes("localhost") || apiUrl.includes("127.0.0.1");
  const isConfigured = !(isHttps && isLocalhost);

  return {
    apiUrl,
    isConfigured,
    isMixedContent,
    isHttps,
  };
}

/**
 * Returns true if the client is capable of reaching the backend without
 * triggering browser security blocks.
 */
export function isBackendReachable(): boolean {
  const status = getBackendStatus();
  return status.isConfigured && !status.isMixedContent;
}

/**
 * Canonical headers for API requests
 */
export function getDefaultHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    Accept: "application/json",
  };

  const apiKey = process.env.NEXT_PUBLIC_API_KEY;
  if (apiKey && apiKey.trim().length > 0) {
    headers["X-API-Key"] = apiKey.trim();
  }

  return headers;
}
