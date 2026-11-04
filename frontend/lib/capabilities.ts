import { getApiUrl } from "@/lib/config";

export interface SystemCapabilities {
  streaming: boolean;
  grounding: boolean;
  history: boolean;
  exports: boolean;
  batch: boolean;
  eval_harness: boolean;
  demo_mode: boolean;
  rate_limit: boolean;
  max_upload_mb: number;
  max_pdf_pages: number;
  max_batch_files: number;
  server_version: string;
}

export const DEFAULT_CAPABILITIES: SystemCapabilities = {
  streaming: process.env.NEXT_PUBLIC_FEATURE_STREAMING !== "false",
  grounding: process.env.NEXT_PUBLIC_FEATURE_GROUNDING !== "false",
  history: process.env.NEXT_PUBLIC_FEATURE_HISTORY !== "false",
  exports: process.env.NEXT_PUBLIC_FEATURE_EXPORTS !== "false",
  batch: process.env.NEXT_PUBLIC_FEATURE_BATCH !== "false",
  eval_harness: process.env.NEXT_PUBLIC_FEATURE_EVAL !== "false",
  demo_mode: process.env.NEXT_PUBLIC_FEATURE_DEMO_MODE === "true",
  rate_limit: true,
  max_upload_mb: 15,
  max_pdf_pages: 8,
  max_batch_files: 20,
  server_version: "2.0.0",
};

let cachedCapabilities: SystemCapabilities | null = null;

export async function fetchServerCapabilities(
  baseUrl: string = getApiUrl()
): Promise<SystemCapabilities> {
  if (cachedCapabilities) {
    return cachedCapabilities;
  }
  try {
    const res = await fetch(`${baseUrl}/api/v1/capabilities`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) {
      return DEFAULT_CAPABILITIES;
    }
    const data = (await res.json()) as SystemCapabilities;
    cachedCapabilities = data;
    return data;
  } catch {
    return DEFAULT_CAPABILITIES;
  }
}
