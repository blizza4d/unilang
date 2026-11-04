import { create } from "zustand";
import {
  fetchDocumentList,
  fetchDocumentDetail,
  deleteDocument,
  type StoredDocumentSummary,
  type StoredDocumentDetail,
} from "@/lib/historyApi";
import { ExtendedDocumentResponse, LineItem } from "@/lib/types";
import { useDocumentStore } from "./useDocumentStore";

interface HistoryState {
  items: StoredDocumentSummary[];
  selectedDocument: StoredDocumentDetail | null;
  isLoading: boolean;
  error: string | null;
  isOpen: boolean;
  searchQuery: string;

  setIsOpen: (isOpen: boolean) => void;
  toggleOpen: () => void;
  setSearchQuery: (query: string) => void;
  loadHistory: () => Promise<void>;
  selectDocument: (id: string) => Promise<void>;
  removeDocument: (id: string) => Promise<void>;
}

export const useHistoryStore = create<HistoryState>((set, get) => ({
  items: [],
  selectedDocument: null,
  isLoading: false,
  error: null,
  isOpen: false,
  searchQuery: "",

  setIsOpen: (isOpen: boolean) => set({ isOpen }),
  toggleOpen: () => set((state) => ({ isOpen: !state.isOpen })),
  setSearchQuery: (searchQuery: string) => set({ searchQuery }),

  loadHistory: async () => {
    set({ isLoading: true, error: null });
    try {
      const items = await fetchDocumentList(100, 0);
      set({ items, isLoading: false });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : "Failed to load history",
        isLoading: false,
      });
    }
  },

  selectDocument: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const doc = await fetchDocumentDetail(id);
      set({ selectedDocument: doc, isLoading: false });

      // Populate document into main workspace store with normalization
      if (doc.extracted_data) {
        const store = useDocumentStore.getState();
        const raw = doc.extracted_data as unknown;
        let responsePayload: ExtendedDocumentResponse;

        if (
          raw &&
          typeof raw === "object" &&
          "extracted_data" in raw &&
          "validation_metrics" in raw
        ) {
          responsePayload = raw as ExtendedDocumentResponse;
        } else {
          const inv = (raw as Record<string, unknown>) ?? {};
          responsePayload = {
            extracted_data: {
              vendor_name: String(inv["vendor_name"] || doc.vendor_name || ""),
              invoice_number: String(inv["invoice_number"] || doc.invoice_number || ""),
              date: String(inv["date"] || ""),
              currency: String(inv["currency"] || doc.currency || "USD"),
              total_amount: Number(inv["total_amount"] ?? doc.total_amount ?? 0),
              tax_amount: Number(inv["tax_amount"] ?? 0),
              line_items: Array.isArray(inv["line_items"]) ? (inv["line_items"] as LineItem[]) : [],
            },
            validation_metrics: [],
            overall_status:
              doc.status === "approved" || (doc.status as string) === "APPROVED"
                ? "APPROVED"
                : (doc.status as string) === "FAILED"
                ? "FAILED"
                : "REQUIRES_HUMAN_REVIEW",
          };
        }
        store.setExtractedData(responsePayload);
      }
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : `Failed to load document ${id}`,
        isLoading: false,
      });
    }
  },

  removeDocument: async (id: string) => {
    try {
      await deleteDocument(id);
      set((state) => ({
        items: state.items.filter((item) => item.id !== id),
        selectedDocument:
          state.selectedDocument?.id === id ? null : state.selectedDocument,
      }));
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : `Failed to delete document ${id}`,
      });
    }
  },
}));
