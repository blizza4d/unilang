# DataNova Extract: Comprehensive Architecture & Security Audit Report

**Date:** November 2026  
**Auditor:** Elite Staff-Level Full-Stack AI Architect & Security Engineer  
**Scope:** DataNova Extract Monorepo (Backend & Frontend)  
**Status:** Audit Complete & Critical Repairs Deployed  

---

## 1. Executive Summary

A comprehensive code, architecture, and security audit of the initial Phase 1 release was conducted across all backend services, LangGraph orchestration nodes, mathematical validators, and Next.js 15 client modules.

The architecture was confirmed sound in its fundamental multi-agent concept: deterministic mathematical checks reliably override probabilistic LLM judgments, and the Pydantic v2 data contracts are strictly enforced. However, several operational vulnerabilities, race conditions, edge-case number parsing defects, and platform-specific dependencies were identified that would compromise a high-stakes hackathon demo or production rollout.

All **Critical** and **High** findings have been repaired.

---

## 2. Summary of Findings

| ID | Severity | File | Description | Remediation |
|---|---|---|---|---|
| **AUD-001** | **Critical** | `backend/utils/file_parsers.py` | `pdf2image` raised unhandled `PDFInfoNotInstalledError` if Poppler binary was missing from system PATH, failing with an opaque 500 error. | Wrapped Poppler detection to return clear, actionable remediation instructions with `CorruptFileError` (HTTP 400). |
| **AUD-002** | **Critical** | `backend/utils/file_parsers.py` | Potential image decompression bomb vulnerability (`PIL.Image.DecompressionBombError`) from untrusted high-resolution uploads. | Enforced `Image.MAX_IMAGE_PIXELS = 100_000_000` and wrapped decompression limits with early bounds validation. |
| **AUD-003** | **High** | `frontend/store/useDocumentStore.ts` | Race condition in `processFile()`: uploading a second invoice while a previous extraction was in flight would overwrite state with stale results. | Implemented monotonic `runId` verification: asynchronous results matching a superseded `runId` are rejected silently. |
| **AUD-004** | **High** | `frontend/components/ui/ExtractedField.tsx` | European decimal format (`12,50`) entered or pasted into numeric input was truncated to `12.0` by JavaScript's standard `parseFloat`. | Added localized decimal normalizer converting comma separators to decimal periods before numerical coercion. |
| **AUD-005** | **Medium** | `backend/agents/prompts.py` | Edge cases in multinational invoices: credit notes with negative balances, split currency references, and ambiguous dates (`05/06/2026`). | Added comprehensive addenda for credit notes, locale-aware date ambiguity, and primary vs. payment conversion currencies. |
| **AUD-006** | **Medium** | `backend/main.py` | Deprecated Starlette `HTTP_413_REQUEST_ENTITY_TOO_LARGE` status code and unclosed `UploadFile` handles under high throughput. | Swapped to standard `413` status code and ensured `await file.close()` executes inside a `finally` block on all uploads. |
| **AUD-007** | **Low** | `frontend/components/layout/DocumentViewer.tsx` | PDF iframe blob preview occasionally lacked explicit MIME header in Chromium browsers, causing some native PDF viewers to stall. | Ensured all client-side object URLs maintain explicit `application/pdf` MIME type headers upon instantiation. |

---

## 3. Detailed Findings & Remediations

### AUD-001: Missing Poppler Diagnostic Handling
- **Problem:** When running on bare metal without Poppler (`pdftoppm`), `pdf2image.convert_from_bytes` raised `pdf2image.exceptions.PDFInfoNotInstalledError`. In Phase 1, this slipped past targeted exception blocks into the generic 500 handler, obscuring the missing dependency.
- **Why It Matters:** Hackathon judges evaluating the app locally on Windows or macOS might see a generic 500 server error rather than an actionable message instructing them to install Poppler.
- **Fix:** Explicitly intercepted `PDFInfoNotInstalledError` in `file_parsers.py` and converted it to an explicit diagnostic error indicating the exact package to install (`brew install poppler`, `apt-get install poppler-utils`, or Windows binary setup).

### AUD-002: Image Decompression Bomb Defense
- **Problem:** Malicious or malformed PNG/TIFF/JPEG files with massive pixel canvases (e.g., 50,000 x 50,000 pixels compressed into a small file) could crash worker memory during PIL decoding.
- **Why It Matters:** An unconstrained decompression bomb causes worker denial of service and memory exhaustion.
- **Fix:** Bound `Image.MAX_IMAGE_PIXELS = 100_000_000`, added explicit `DecompressionBombError` catch blocks, and downscale images via LANCZOS before base64 encoding.

### AUD-003: Race Condition on File Replacement
- **Problem:** If a user uploaded Invoice A (taking ~4 seconds to process), and immediately dropped Invoice B after 1 second, both requests ran concurrently. If Invoice A finished after Invoice B, Invoice A's data would overwrite Invoice B.
- **Why It Matters:** Destroys user trust in high-velocity accounting environments.
- **Fix:** Added a stateful `runId` counter to `useDocumentStore`. Every invocation of `processFile()` increments `runId` and tags the active controller. Incoming completions matching an outdated `runId` are discarded.

### AUD-004: Foreign Locale Decimal Separators
- **Problem:** Many European and Latin American invoices use commas for decimals (`€ 1.250,50`). Typing or pasting `1250,50` into a number input resulted in `1250` when passed through `parseFloat`.
- **Why It Matters:** Reviewers correcting German or French invoices were forced to manually replace commas with dots.
- **Fix:** Updated `ExtractedField.tsx` and `LineItemsTable.tsx` to inspect inputs and normalize single comma separators to dots prior to numeric validation.

---

## 4. Accepted Risks & Architectural Tradeoffs

1. **In-Memory Upload Processing:** Document payloads remain entirely in memory (RAM). While bounded by `MAX_UPLOAD_MB=15`, processing multiple 8-page high-DPI PDFs concurrently consumes ~80-120MB per request. This was accepted for zero-disk security posture and hackathon speed.
2. **SQLite Database Engine:** Chosen for zero-setup portability. While SQLite concurrency is bounded compared to PostgreSQL, WAL mode and connection pooling easily satisfy hackathon and single-tenant enterprise auditing workloads.

---

## 5. Known Limitations

- **Handwritten Script Accuracy:** Handwritten annotations are preserved with `[HANDWRITTEN: text]`, but accuracy drops when handwriting overlaps printed table borders.
- **Multi-Currency Settlements:** Invoices detailing both an original foreign currency and a local tax reporting conversion have their totals normalized to the primary payable currency.
