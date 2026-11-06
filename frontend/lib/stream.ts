import {
  ExtendedDocumentResponse,
  PipelineStage,
  StageStatus,
} from "@/lib/types";
import { ApiError } from "@/lib/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development"
    ? "http://localhost:8000"
    : "https://backend-tau-livid-81.vercel.app");

export interface PipelineEventPayload {
  event_id: string;
  request_id: string;
  stage: PipelineStage;
  status: StageStatus;
  timestamp: string;
  duration_ms: number | null;
  message: string;
  detail: Record<string, string | number | boolean> | null;
}

export interface ResultEventPayload {
  result: ExtendedDocumentResponse;
  document_id: string | null;
}

export interface ErrorEventPayload {
  error_code: string;
  message: string;
  stage: PipelineStage | null;
}

export interface HeartbeatEventPayload {
  timestamp: string;
}

export interface StreamHandlers {
  onStage?: (event: PipelineEventPayload) => void;
  onResult?: (event: ResultEventPayload) => void;
  onError?: (event: ErrorEventPayload) => void;
  onHeartbeat?: (event: HeartbeatEventPayload) => void;
}

export async function streamExtract(
  file: File,
  handlers: StreamHandlers,
  signal?: AbortSignal
): Promise<void> {
  const baseUrl = API_BASE_URL.replace(/\/+$/, "");
  const endpoint = `${baseUrl}/api/v1/extract/stream`;
  const formData = new FormData();
  formData.append("file", file);

  const headers: Record<string, string> = {
    Accept: "text/event-stream",
  };
  if (process.env.NEXT_PUBLIC_API_KEY) {
    headers["X-API-Key"] = process.env.NEXT_PUBLIC_API_KEY;
  }

  console.log(`[Stream API] Initiating stream extract for "${file.name}" to ${endpoint}`);

  let response: Response;
  try {
    response = await fetch(endpoint, {
      method: "POST",
      body: formData,
      headers,
      signal,
    });
  } catch (err: unknown) {
    console.error(`[Stream API Error] Network error during stream fetch from ${endpoint}:`, err);
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
    let message = "Streaming request failed.";
    try {
      const errJson = await response.json();
      errorCode = errJson.error_code ?? errorCode;
      message = errJson.message ?? message;
    } catch {
      // not JSON
    }
    console.error(`[Stream API Error Response] Status ${response.status} (${errorCode}): ${message}`);
    throw new ApiError(response.status, errorCode, message);
  }

  if (!response.body) {
    throw new ApiError(500, "STREAM_INTERRUPTED", "No readable stream received.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const frames = buffer.split("\n\n");
      buffer = frames.pop() ?? "";

      for (const frame of frames) {
        const trimmed = frame.trim();
        if (!trimmed) continue;

        let eventType = "message";
        let dataStr = "";

        const lines = trimmed.split("\n");
        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            dataStr = line.slice(5).trim();
          }
        }

        if (!dataStr) continue;

        try {
          const parsedData = JSON.parse(dataStr);
          if (eventType === "stage" && handlers.onStage) {
            handlers.onStage(parsedData as PipelineEventPayload);
          } else if (eventType === "result" && handlers.onResult) {
            handlers.onResult(parsedData as ResultEventPayload);
          } else if (eventType === "error" && handlers.onError) {
            handlers.onError(parsedData as ErrorEventPayload);
          } else if (eventType === "heartbeat" && handlers.onHeartbeat) {
            handlers.onHeartbeat(parsedData as HeartbeatEventPayload);
          }
        } catch {
          // ignore malformed frame
        }
      }
    }
  } catch (err: unknown) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw err;
    }
    if (err instanceof ApiError) {
      throw err;
    }
    console.error("[Stream API Error] Stream connection lost mid-processing:", err);
    throw new ApiError(
      0,
      "STREAM_INTERRUPTED",
      "Stream connection was lost mid-processing."
    );
  } finally {
    reader.releaseLock();
  }
}
