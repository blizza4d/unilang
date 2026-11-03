import type { ExtendedDocumentResponse } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface StoredDocumentSummary {
  id: string;
  filename: string;
  file_hash: string;
  mime_type: string;
  file_size: number;
  created_at: string;
  updated_at: string;
  status: "extracted" | "reviewed" | "approved";
  overall_confidence: number;
  math_verified: boolean;
  total_amount?: number;
  currency?: string;
}

export interface StoredDocumentDetail extends StoredDocumentSummary {
  extracted_data: ExtendedDocumentResponse;
  page_images?: string[];
  edits: Array<{
    id: string;
    field_name: string;
    old_value: unknown;
    new_value: unknown;
    user_id: string;
    reason?: string;
    created_at: string;
  }>;
  approvals: Array<{
    id: string;
    user_id: string;
    notes?: string;
    created_at: string;
  }>;
}

export async function fetchDocumentList(
  limit: number = 50,
  offset: number = 0
): Promise<StoredDocumentSummary[]> {
  const res = await fetch(`${BASE_URL}/api/v1/documents?limit=${limit}&offset=${offset}`, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch documents: ${res.statusText}`);
  }
  const data = await res.json();
  return data.items || [];
}

export async function fetchDocumentDetail(id: string): Promise<StoredDocumentDetail> {
  const res = await fetch(`${BASE_URL}/api/v1/documents/${id}`, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch document ${id}: ${res.statusText}`);
  }
  return res.json();
}

export async function patchDocumentFields(
  id: string,
  fields: Record<string, unknown>,
  userId: string = "operator",
  reason: string = "Manual correction"
): Promise<StoredDocumentDetail> {
  const res = await fetch(`${BASE_URL}/api/v1/documents/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
      reason,
      fields,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to patch document: ${res.statusText}`);
  }
  return res.json();
}

export async function approveDocument(
  id: string,
  userId: string = "reviewer",
  notes?: string
): Promise<StoredDocumentDetail> {
  const res = await fetch(`${BASE_URL}/api/v1/documents/${id}/approve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
      notes,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to approve document: ${res.statusText}`);
  }
  return res.json();
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/v1/documents/${id}`, {
    method: "DELETE",
  });
  if (!res.ok && res.status !== 204) {
    throw new Error(`Failed to delete document: ${res.statusText}`);
  }
}
