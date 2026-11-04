export interface LineItem {
  description: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface ExtractedInvoice {
  vendor_name: string;
  invoice_number: string;
  date: string;
  currency: string;
  total_amount: number;
  tax_amount: number;
  line_items: LineItem[];
}

export type InvoiceFieldName = keyof ExtractedInvoice;

export type ScalarFieldName = Exclude<InvoiceFieldName, "line_items">;

export type OverallStatus = "APPROVED" | "REQUIRES_HUMAN_REVIEW" | "FAILED" | "AUTOMATED_PASS";

export interface ValidationScore {
  field_name: InvoiceFieldName;
  confidence_score: number;
  needs_review: boolean;
  reasoning: string;
}

export interface FinalDocumentResponse {
  extracted_data: ExtractedInvoice;
  validation_metrics: ValidationScore[];
  overall_status: OverallStatus;
}

export interface BoundingBox {
  page: number;
  x: number;
  y: number;
  width: number;
  height: number;
  field_name?: string;
  label?: string;
  text?: string;
  confidence?: number;
  box_2d?: [number, number, number, number];
}

export interface FieldGrounding {
  field_name: string;
  boxes: BoundingBox[];
  source_text: string;
  grounding_confidence: number;
}

export interface LineItemGrounding {
  row_index: number;
  prop: "description" | "quantity" | "unit_price" | "total_price";
  box: BoundingBox | null;
}

export interface PageDimension {
  page: number;
  width_px: number;
  height_px: number;
}

export interface GroundingResult {
  fields: FieldGrounding[];
  line_items: LineItemGrounding[];
  page_dimensions: PageDimension[];
}

export interface UsageSummary {
  input_tokens: number;
  output_tokens: number;
  estimated_cost_usd: number | null;
}

export interface ExtendedDocumentResponse extends FinalDocumentResponse {
  grounding?: GroundingResult | null;
  document_id?: string | null;
  page_count?: number;
  processing_ms?: number;
  usage?: UsageSummary | null;
}

export interface ApiErrorBody {
  error_code: string;
  message: string;
  request_id: string;
}

export type EditableValue = string | number;

export interface ScalarFieldConfig {
  key: ScalarFieldName;
  label: string;
  type: "text" | "number" | "date";
}

export const SCALAR_FIELDS: readonly ScalarFieldConfig[] = [
  { key: "vendor_name", label: "Vendor Name", type: "text" },
  { key: "invoice_number", label: "Invoice Number", type: "text" },
  { key: "date", label: "Invoice Date", type: "date" },
  { key: "currency", label: "Currency (ISO)", type: "text" },
  { key: "tax_amount", label: "Tax Amount", type: "number" },
  { key: "total_amount", label: "Total Payable", type: "number" },
] as const;

export type ActivePipelineStage =
  | "prepare"
  | "vision"
  | "classifier"
  | "extractor"
  | "grounding"
  | "compliance"
  | "judge"
  | "finalize";

export type PipelineStage =
  | "idle"
  | ActivePipelineStage
  | "complete"
  | "error";

export type StageStatus = "idle" | "started" | "completed" | "failed";

export interface StageState {
  status: StageStatus;
  durationMs: number | null;
  message: string;
}

export function isExtendedResponse(
  data: unknown
): data is ExtendedDocumentResponse {
  if (typeof data !== "object" || data === null) return false;
  const rec = data as Record<string, unknown>;
  return "extracted_data" in rec && "validation_metrics" in rec;
}

// ---------------------------------------------------------------------------
// Phase 3 Multi-Document & Platform Extensions
// ---------------------------------------------------------------------------

export type DocType =
  | "invoice"
  | "receipt"
  | "purchase_order"
  | "credit_note"
  | "bank_statement"
  | "utility_bill"
  | "delivery_note"
  | "expense_report"
  | "id_document"
  | "contract_summary"
  | "unknown";

export interface PageRange {
  doc_type: string;
  start_page: number;
  end_page: number;
}

export interface DocumentClassification {
  doc_type: DocType;
  confidence: number;
  language: string;
  script: string;
  is_multi_document: boolean;
  page_ranges: PageRange[];
  reasoning: string;
}

export interface GenericValidationScore {
  field_name: string;
  confidence_score: number;
  needs_review: boolean;
  reasoning: string;
}

export interface ComplianceViolation {
  rule_id: string;
  field_path: string;
  severity: "error" | "warning";
  message: string;
}

export interface ComplianceReport {
  status: "passed" | "failed" | "warning";
  checks: number;
  violations?: ComplianceViolation[];
}

export interface FraudReport {
  risk_score: number;
  tampering_detected: boolean;
  is_duplicate: boolean;
  signals?: string[];
}

export interface GenericDocumentResponse {
  document_id: string;
  tenant_id: string;
  filename: string;
  doc_type: DocType;
  schema_version: number;
  classification: DocumentClassification;
  data: Record<string, unknown>;
  validation_metrics: GenericValidationScore[];
  compliance?: ComplianceReport | null;
  fraud?: FraudReport | null;
  grounding: Record<string, unknown>;
  overall_status: OverallStatus;
  usage?: Record<string, unknown>;
}

export interface SchemaSectionLayout {
  title: string;
  fields?: string[];
  table?: string;
  columns?: string[];
}

export interface DocTypeLayout {
  sections: SchemaSectionLayout[];
}

export interface DocTypeMetadata {
  doc_type: DocType;
  title: string;
  version: number;
  field_names: string[];
  validators: string[];
  ui_layout: DocTypeLayout;
  sensitive: boolean;
}
