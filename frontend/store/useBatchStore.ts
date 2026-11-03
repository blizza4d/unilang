import { create } from "zustand";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface BatchItem {
  id: string;
  filename: string;
  status: "pending" | "processing" | "completed" | "failed";
  confidence?: number;
  math_verified?: boolean;
  total_amount?: number;
  error?: string;
  result_id?: string;
}

export interface BatchSummary {
  batch_id: string;
  total_files: number;
  completed_files: number;
  failed_files: number;
  success_rate: number;
  average_confidence: number;
  math_verification_rate: number;
  currency_breakdown: Record<string, number>;
  total_invoice_value: number;
  elapsed_seconds: number;
}

interface BatchState {
  batchId: string | null;
  isOpen: boolean;
  status: "idle" | "uploading" | "processing" | "completed" | "cancelled" | "failed";
  items: BatchItem[];
  summary: BatchSummary | null;
  error: string | null;

  setIsOpen: (isOpen: boolean) => void;
  startBatch: (files: File[]) => Promise<void>;
  cancelBatch: () => Promise<void>;
  resetBatch: () => void;
}

export const useBatchStore = create<BatchState>((set, get) => ({
  batchId: null,
  isOpen: false,
  status: "idle",
  items: [],
  summary: null,
  error: null,

  setIsOpen: (isOpen: boolean) => set({ isOpen }),

  resetBatch: () => {
    set({
      batchId: null,
      status: "idle",
      items: [],
      summary: null,
      error: null,
      isOpen: false,
    });
  },

  startBatch: async (files: File[]) => {
    if (!files.length) return;

    set({
      isOpen: true,
      status: "uploading",
      error: null,
      summary: null,
      items: files.map((f, i) => ({
        id: `temp-${i}`,
        filename: f.name,
        status: "pending",
      })),
    });

    try {
      const formData = new FormData();
      files.forEach((f) => formData.append("files", f));

      const res = await fetch(`${BASE_URL}/api/v1/batch`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Batch upload failed: ${res.statusText}`);
      }

      const data = await res.json();
      const batchId = data.batch_id;
      set({ batchId, status: "processing" });

      // Connect SSE stream for batch progress
      const eventSource = new EventSource(`${BASE_URL}/api/v1/batch/${batchId}/events`);

      eventSource.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "item_complete") {
            set((state) => ({
              items: state.items.map((item) =>
                item.filename === payload.filename
                  ? {
                      ...item,
                      id: payload.item_id || item.id,
                      status: "completed",
                      confidence: payload.confidence,
                      math_verified: payload.math_verified,
                      total_amount: payload.total_amount,
                      result_id: payload.document_id,
                    }
                  : item
              ),
            }));
          } else if (payload.type === "item_failed") {
            set((state) => ({
              items: state.items.map((item) =>
                item.filename === payload.filename
                  ? {
                      ...item,
                      id: payload.item_id || item.id,
                      status: "failed",
                      error: payload.error,
                    }
                  : item
              ),
            }));
          } else if (payload.type === "batch_complete") {
            set({ status: "completed" });
            eventSource.close();
            // Fetch final summary
            fetch(`${BASE_URL}/api/v1/batch/${batchId}/summary`)
              .then((r) => r.json())
              .then((sum) => set({ summary: sum }))
              .catch(console.error);
          }
        } catch (e) {
          console.error("SSE parse error", e);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
      };
    } catch (err) {
      set({
        status: "failed",
        error: err instanceof Error ? err.message : "Failed to start batch processing",
      });
    }
  },

  cancelBatch: async () => {
    const { batchId } = get();
    if (!batchId) return;

    try {
      await fetch(`${BASE_URL}/api/v1/batch/${batchId}/cancel`, {
        method: "POST",
      });
      set({ status: "cancelled" });
    } catch (err) {
      console.error("Cancel failed:", err);
    }
  },
}));
