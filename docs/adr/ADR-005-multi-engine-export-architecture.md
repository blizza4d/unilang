# ADR-005: Multi-Engine Enterprise Export Architecture

## Status
Accepted

## Context
Downstream consumers of extracted invoice data range from data scientists needing raw JSON to financial controllers requiring native Excel workbooks and compliance officers requesting printable certified PDF summaries.

## Decision
We implemented a multi-engine exporter suite:
1. **JSON:** Full machine-readable export with confidence scores and grounding bounding boxes.
2. **CSV (ZIP):** Split invoice-header and line-item CSV files packaged in a ZIP archive with UTF-8 BOM encoding for seamless Microsoft Excel compatibility.
3. **Excel (XLSX):** Multi-sheet workbook (`openpyxl`) featuring native dynamic formulas (`=C2*D2` and `=SUM(E2:En)`), custom color styling, and frozen headers.
4. **Audit PDF:** Clean, professional vector PDF report generated using ReportLab, detailing document metadata, validation grades, and signature sign-off lines.

## Consequences
- Single API endpoint (`/api/v1/documents/{id}/export?format=...`) and direct payload export (`/api/v1/export/direct`).
- Eliminates manual spreadsheet formatting for finance operations teams.
