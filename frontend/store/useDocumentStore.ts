import { create } from "zustand";
import { devtools } from "zustand/middleware";
import { extractDocument, ApiError } from "@/lib/api";
import { streamExtract } from "@/lib/stream";
import {
  ActivePipelineStage,
  BoundingBox,
  EditableValue,
  ExtendedDocumentResponse,
  LineItem,
  OverallStatus,
  PipelineStage,
  ScalarFieldName,
  StageState,
} from "@/lib/types";

export interface ApiErrorState {
  message: string;
  code: string;
  status: number;
}

const INITIAL_STAGES: Record<ActivePipelineStage, StageState> = {

  prepare: { status: "idle", durationMs: null, message: "Preparing document" },
  vision: { status: "idle", durationMs: null, message: "Spatial transcription" },
  extractor: { status: "idle", durationMs: null, message: "Multilingual structuring" },
  grounding: { status: "idle", durationMs: null, message: "Bounding box localization" },
  judge: { status: "idle", durationMs: null, message: "Deterministic math & judge QA" },
  finalize: { status: "idle", durationMs: null, message: "Finalizing response" },
};

export interface DocumentStateValues {
  file: File | null;
  filePreviewUrl: string | null;
  isProcessing: boolean;
  extractedData: ExtendedDocumentResponse | null;
  isReviewMode: boolean;
  error: ApiErrorState | null;
  resolvedFields: Record<string, boolean>;
  abortController: AbortController | null;
  runId: number;
  pipelineStages: Record<ActivePipelineStage, StageState>;
  currentStage: PipelineStage | null;
  activeFieldKey: string | null;
  activeField: string | null;
  activePage: number;
  boundingBoxes: BoundingBox[];
}

export interface DocumentStoreActions {
  setFile: (file: File | null) => void;
  resetStore: () => void;
  toggleReviewMode: () => void;
  setReviewMode: (value: boolean) => void;
  processFile: () => Promise<void>;
  updateFieldValue: (field: ScalarFieldName, value: EditableValue) => void;
  updateLineItemValue: (
    index: number,
    prop: keyof LineItem,
    value: EditableValue
  ) => void;
  approveAll: () => void;
  setActiveField: (key: string | null) => void;
  setActivePage: (page: number) => void;
  setExtractedData: (data: ExtendedDocumentResponse) => void;
  setBoundingBoxes: (boxes: BoundingBox[]) => void;
}


export type DocumentStore = DocumentStateValues & DocumentStoreActions;

const initialState: DocumentStateValues = {
  file: null,
  filePreviewUrl: null,
  isProcessing: false,
  extractedData: null,
  isReviewMode: false,
  error: null,
  resolvedFields: {},
  abortController: null,
  runId: 0,
  pipelineStages: INITIAL_STAGES,
  currentStage: null,
  activeFieldKey: null,
  activeField: null,
  activePage: 1,
  boundingBoxes: [],
};


function checkAndDeriveStatus(
  currentData: ExtendedDocumentResponse,
  resolvedMap: Record<string, boolean>
): OverallStatus {
  if (currentData.overall_status === "FAILED") {
    return "FAILED";
  }

  const flagged = currentData.validation_metrics.filter((m) => m.needs_review);
  if (flagged.length === 0) {
    return "APPROVED";
  }

  const allResolved = flagged.every((metric) => {
    if (metric.field_name === "line_items") {
      const lineItemKeys = Object.keys(resolvedMap).filter((k) =>
        k.startsWith("line_items.")
      );
      if (lineItemKeys.length > 0) return true;
      return currentData.extracted_data.line_items.every(
        (it) => Math.abs(it.quantity * it.unit_price - it.total_price) <= 0.01
      );
    }
    return resolvedMap[metric.field_name] === true;
  });

  return allResolved ? "APPROVED" : "REQUIRES_HUMAN_REVIEW";
}

export const useDocumentStore = create<DocumentStore>()(
  devtools(
    (set, get) => ({
      ...initialState,

      setFile: (newFile: File | null) => {
        const { filePreviewUrl, abortController, runId } = get();
        if (abortController) {
          abortController.abort();
        }
        if (filePreviewUrl) {
          URL.revokeObjectURL(filePreviewUrl);
        }

        let newUrl: string | null = null;
        if (newFile) {
          try {
            newUrl = URL.createObjectURL(newFile);
          } catch {
            newUrl = null;
          }
        }

        set({
          file: newFile,
          filePreviewUrl: newUrl,
          extractedData: null,
          isReviewMode: false,
          error: null,
          resolvedFields: {},
          abortController: null,
          runId: runId + 1,
          pipelineStages: INITIAL_STAGES,
          currentStage: null,
          activeFieldKey: null,
          activePage: 1,
        });
      },

      resetStore: () => {
        const { filePreviewUrl, abortController } = get();
        if (abortController) {
          abortController.abort();
        }
        if (filePreviewUrl) {
          URL.revokeObjectURL(filePreviewUrl);
        }
        set(initialState);
      },

      toggleReviewMode: () => {
        set((state) => ({ isReviewMode: !state.isReviewMode }));
      },

      setReviewMode: (value: boolean) => {
        set({ isReviewMode: value });
      },

      setActiveField: (key: string | null) => {
        set({ activeFieldKey: key, activeField: key });
      },

      setActivePage: (page: number) => {
        set({ activePage: page });
      },

      setBoundingBoxes: (boxes: BoundingBox[]) => {
        set({ boundingBoxes: boxes });
      },

      setExtractedData: (data: ExtendedDocumentResponse) => {
        let boxes: BoundingBox[] = [];
        if (data.grounding?.fields) {
          boxes = data.grounding.fields.flatMap((f) =>
            f.boxes.map((b) => ({
              ...b,
              field_name: f.field_name,
              confidence: f.grounding_confidence,
              text: f.source_text,
            }))
          );
        }
        set({
          extractedData: data,
          boundingBoxes: boxes,
          isReviewMode: data.overall_status === "REQUIRES_HUMAN_REVIEW",
        });
      },


      processFile: async () => {
        const { file, isProcessing, runId } = get();
        if (!file || isProcessing) return;

        const currentRunId = runId + 1;
        const controller = new AbortController();

        set({
          isProcessing: true,
          error: null,
          abortController: controller,
          runId: currentRunId,
          pipelineStages: INITIAL_STAGES,
          currentStage: "prepare",
        });

        const useStreaming = true; // Streaming enabled by default in Phase 2

        if (useStreaming) {
          try {
            await streamExtract(
              file,
              {
                onStage: (event) => {
                  if (get().runId !== currentRunId) return;
                  set((state) => ({
                    currentStage: event.stage,
                    pipelineStages: {
                      ...state.pipelineStages,
                      [event.stage]: {
                        status: event.status,
                        durationMs: event.duration_ms,
                        message: event.message,
                      },
                    },
                  }));
                },
                onResult: (event) => {
                  if (get().runId !== currentRunId) return;
                  set({
                    extractedData: event.result,
                    isReviewMode: event.result.overall_status === "REQUIRES_HUMAN_REVIEW",
                    resolvedFields: {},
                    currentStage: "finalize",
                  });
                },
                onError: (event) => {
                  if (get().runId !== currentRunId) return;
                  set({
                    error: {
                      message: event.message,
                      code: event.error_code,
                      status: 500,
                    },
                  });
                },
              },
              controller.signal
            );
          } catch (err: unknown) {
            if (get().runId !== currentRunId) return;
            if (err instanceof DOMException && err.name === "AbortError") return;

            // Fallback to Phase 1 non-streaming endpoint on streaming error
            try {
              const res = await extractDocument(file, controller.signal);
              if (get().runId === currentRunId) {
                set({
                  extractedData: res as ExtendedDocumentResponse,
                  isReviewMode: res.overall_status === "REQUIRES_HUMAN_REVIEW",
                  resolvedFields: {},
                });
              }
            } catch (fallbackErr: unknown) {
              if (fallbackErr instanceof ApiError) {
                set({
                  error: {
                    message: fallbackErr.message,
                    code: fallbackErr.code,
                    status: fallbackErr.status,
                  },
                });
              } else {
                set({
                  error: {
                    message: "Extraction failed.",
                    code: "EXTRACTION_ERROR",
                    status: 500,
                  },
                });
              }
            }
          } finally {
            if (get().runId === currentRunId) {
              set({ isProcessing: false, abortController: null });
            }
          }
        } else {
          // Standard Phase 1 endpoint
          try {
            const response = await extractDocument(file, controller.signal);
            if (get().runId === currentRunId) {
              set({
                extractedData: response as ExtendedDocumentResponse,
                isReviewMode: response.overall_status === "REQUIRES_HUMAN_REVIEW",
                resolvedFields: {},
              });
            }
          } catch (err: unknown) {
            if (get().runId !== currentRunId) return;
            if (err instanceof DOMException && err.name === "AbortError") return;

            if (err instanceof ApiError) {
              set({
                error: {
                  message: err.message,
                  code: err.code,
                  status: err.status,
                },
              });
            } else {
              set({
                error: {
                  message: "Extraction failed.",
                  code: "UNKNOWN_ERROR",
                  status: 500,
                },
              });
            }
          } finally {
            if (get().runId === currentRunId) {
              set({ isProcessing: false, abortController: null });
            }
          }
        }
      },

      updateFieldValue: (field: ScalarFieldName, value: EditableValue) => {
        const { extractedData, resolvedFields } = get();
        if (!extractedData) return;

        let parsedValue: EditableValue = value;
        if (field === "total_amount" || field === "tax_amount") {
          const num = typeof value === "number" ? value : parseFloat(String(value));
          if (Number.isNaN(num)) return;
          parsedValue = num;
        }

        const updatedInvoice = {
          ...extractedData.extracted_data,
          [field]: parsedValue,
        };

        const updatedResolved = {
          ...resolvedFields,
          [field]: true,
        };

        const newStatus = checkAndDeriveStatus(
          { ...extractedData, extracted_data: updatedInvoice },
          updatedResolved
        );

        set({
          extractedData: {
            ...extractedData,
            extracted_data: updatedInvoice,
            overall_status: newStatus,
          },
          resolvedFields: updatedResolved,
        });
      },

      updateLineItemValue: (
        index: number,
        prop: keyof LineItem,
        value: EditableValue
      ) => {
        const { extractedData, resolvedFields } = get();
        if (!extractedData) return;

        const currentItems = [...extractedData.extracted_data.line_items];
        const targetItem = currentItems[index];
        if (!targetItem) return;

        let parsedValue: EditableValue = value;
        if (prop !== "description") {
          const num = typeof value === "number" ? value : parseFloat(String(value));
          if (Number.isNaN(num)) return;
          parsedValue = num;
        }

        const updatedItem: LineItem = {
          ...targetItem,
          [prop]: parsedValue,
        };

        if (prop === "quantity" || prop === "unit_price") {
          const q = prop === "quantity" ? (parsedValue as number) : targetItem.quantity;
          const u = prop === "unit_price" ? (parsedValue as number) : targetItem.unit_price;
          updatedItem.total_price = parseFloat((q * u).toFixed(2));
        }

        currentItems[index] = updatedItem;

        const updatedInvoice = {
          ...extractedData.extracted_data,
          line_items: currentItems,
        };

        const updatedResolved = {
          ...resolvedFields,
          [`line_items.${index}.${prop}`]: true,
          line_items: true,
        };

        const newStatus = checkAndDeriveStatus(
          { ...extractedData, extracted_data: updatedInvoice },
          updatedResolved
        );

        set({
          extractedData: {
            ...extractedData,
            extracted_data: updatedInvoice,
            overall_status: newStatus,
          },
          resolvedFields: updatedResolved,
        });
      },

      approveAll: () => {
        const { extractedData } = get();
        if (!extractedData) return;
        set({
          extractedData: {
            ...extractedData,
            overall_status: "APPROVED",
          },
        });
      },
    }),

    { name: "DocumentStore", enabled: process.env.NODE_ENV === "development" }
  )
);

export function selectFlaggedCount(state: DocumentStateValues): number {
  if (!state.extractedData) return 0;
  return state.extractedData.validation_metrics.filter((m) => m.needs_review).length;
}

export function selectUnresolvedCount(state: DocumentStateValues): number {
  if (!state.extractedData) return 0;
  const flagged = state.extractedData.validation_metrics.filter((m) => m.needs_review);
  let unresolved = 0;

  for (const item of flagged) {
    if (item.field_name === "line_items") {
      const lineResolved = Object.keys(state.resolvedFields).some((k) =>
        k.startsWith("line_items")
      );
      if (!lineResolved) unresolved += 1;
    } else {
      if (!state.resolvedFields[item.field_name]) {
        unresolved += 1;
      }
    }
  }

  return unresolved;
}
