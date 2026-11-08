import { ApiErrorBody, FinalDocumentResponse, OverallStatus } from "@/lib/types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const ERROR_MESSAGE_MAP: Record<string, string> = {
  EMPTY_FILE: "That file is empty.",
  CORRUPT_FILE: "We couldn't read that file. Try another copy.",
  FILE_TOO_LARGE: "File exceeds the 15 MB limit.",
  UNSUPPORTED_TYPE: "Unsupported file type.",
  VALIDATION_ERROR: "Invalid request.",
  AGENT_VISION_FAILED: "Document reading failed. Please retry.",
  AGENT_EXTRACTOR_FAILED: "Data structuring failed. Please retry.",
  AGENT_JUDGE_FAILED: "Validation failed. Please retry.",
  INTERNAL_ERROR: "Something went wrong on our side.",
  UPSTREAM_TIMEOUT: "The AI took too long. Please retry.",
  NETWORK_ERROR: "Cannot reach the extraction server.",
};

export class ApiError extends Error {
  public readonly status: number;
  public readonly code: string;
  public readonly requestId: string | null;

  constructor(status: number, code: string, message: string, requestId: string | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.requestId = requestId;
  }
}

export function isFinalDocumentResponse(data: unknown): data is FinalDocumentResponse {
  if (typeof data !== "object" || data === null) {
    return false;
  }
  const record = data as Record<string, unknown>;

  if (typeof record["extracted_data"] !== "object" || record["extracted_data"] === null) {
    return false;
  }
  const ext = record["extracted_data"] as Record<string, unknown>;
  if (
    typeof ext["vendor_name"] !== "string" ||
    typeof ext["invoice_number"] !== "string" ||
    typeof ext["date"] !== "string" ||
    typeof ext["currency"] !== "string" ||
    typeof ext["total_amount"] !== "number" ||
    typeof ext["tax_amount"] !== "number" ||
    !Array.isArray(ext["line_items"])
  ) {
    return false;
  }

  if (!Array.isArray(record["validation_metrics"])) {
    return false;
  }

  const validStatuses: OverallStatus[] = [
    "APPROVED",
    "REQUIRES_HUMAN_REVIEW",
    "FAILED",
    "AUTOMATED_PASS",
  ];
  if (
    typeof record["overall_status"] !== "string" ||
    !validStatuses.includes(record["overall_status"] as OverallStatus)
  ) {
    return false;
  }

  return true;
}

export async function extractDocument(
  file: File,
  signal?: AbortSignal
): Promise<FinalDocumentResponse> {
  const baseUrl = API_BASE_URL.replace(/\/+$/, "");
  const endpoint = `${baseUrl}/api/v1/extract`;
  const formData = new FormData();
  formData.append("file", file);

  const headers: Record<string, string> = {};
  if (typeof window !== "undefined") {
    const liveCode = window.sessionStorage.getItem("live_access_code");
    if (liveCode) {
      headers["X-Live-Access-Code"] = liveCode;
    }
  }

  console.log(`[API] Dispatching extraction request for "${file.name}" (${file.size} bytes) to ${endpoint}`);

  let response: Response;
  try {
    response = await fetch(endpoint, {
      method: "POST",
      headers,
      body: formData,
      signal,
    });
  } catch (err: unknown) {
    console.error(`[API Network Error] Failed to reach extraction server at ${endpoint}:`, err);
    if (err instanceof DOMException && err.name === "AbortError") {
      throw err;
    }
    throw new ApiError(
      0,
      "NETWORK_ERROR",
      `Cannot reach the extraction server at ${baseUrl}. Ensure backend is running and accessible.`
    );
  }

  if (!response.ok) {
    let errorCode = "INTERNAL_ERROR";
    let serverMessage = "Request failed.";
    let requestId: string | null = response.headers.get("X-Request-ID");

    try {
      const errorJson = (await response.json()) as ApiErrorBody;
      if (errorJson && typeof errorJson === "object") {
        errorCode = errorJson.error_code ?? errorCode;
        serverMessage = errorJson.message ?? serverMessage;
        requestId = errorJson.request_id ?? requestId;
      }
    } catch {
      // Body not JSON
    }

    const clientMessage = ERROR_MESSAGE_MAP[errorCode] ?? serverMessage;
    console.error(`[API Error Response] Status ${response.status} (${errorCode}): ${serverMessage}`);
    throw new ApiError(response.status, errorCode, clientMessage, requestId);
  }

  try {
    const json = await response.json();
    if (!isFinalDocumentResponse(json)) {
      console.error("[API Error] Server returned invalid document structure:", json);
      throw new ApiError(
        500,
        "VALIDATION_ERROR",
        "Server returned an unexpected document structure."
      );
    }
    return json;
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      throw err;
    }
    console.error("[API Error] JSON parse failure:", err);
    throw new ApiError(500, "CORRUPT_FILE", "Could not parse server response.");
  }
}
