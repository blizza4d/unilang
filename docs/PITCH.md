# DataNova Extract: Hackathon Winning Pitch

## 1. Executive Summary
Traditional OCR and Document AI systems fail in enterprise accounting workflows because they are **monolithic**, **statistically probabilistic without deterministic guarantees**, and **opaque**. When an OCR model misreads a German decimal comma or hallucinated tax calculation, the system either crashes downstream ERP pipelines (SAP/NetSuite) or passes silent arithmetic errors costing millions in audit penalties.

**DataNova Extract** re-architects intelligent document understanding as an **Autonomous Multi-Agent Control Tower** (Vision Ingestion Agent, Multilingual Extraction Agent, Adversarial Arithmetic Judge Agent, and 2D Spatial Grounding Agent) paired with a **Raycast-grade, high-contrast human-in-the-loop workspace**.

---

## 2. The Core Innovations

### A. The Adversarial Judge & Deterministic Math Enforcer
We do not rely on LLM arithmetic.
- The **Vision Agent** ingests raw multimodal pages (PDFs rendered at 200 DPI or lossless images) and identifies orientation, language, and table bounds.
- The **Extractor Agent** extracts structured schemas (vendor, invoice number, line items, taxes, totals) with full support for 8+ languages (English, German, Hindi GST, Arabic RTL, Japanese, French, Spanish).
- The **Adversarial Judge Agent** attempts to falsify the extraction by evaluating:
  1. `sum(quantity * unit_price) == total_price` per row.
  2. `sum(line_item_totals) + tax_amount == total_amount` (with dual-GST CGST/SGST support).
  3. Format sanity, date locale disambiguation, and prompt-injection detection.
- A **Deterministic Python Validator** overrides the judge: code always trumps model reasoning.

### B. Live SSE Streaming Control Tower
Enterprise users will not stare at a blank spinner for 10 seconds. DataNova Extract streams progress events via HTTP Server-Sent Events (`POST /api/v1/extract/stream`), dynamically animating agent milestones, live timings, and stage tokens in real time.

### C. 2D Bounding Box Spatial Grounding
Every extracted scalar field and table row is tied to exact coordinate bounding boxes `[ymin, xmin, ymax, xmax]`. Hovering a field in the sidebar illuminates the document region with a glowing cyan highlight; clicking a highlight jumps directly to the field editor.

### D. Multi-Format Enterprise Export & Audit Ledger
- **Native Excel (XLSX):** Formula-driven workbooks with `=C2*D2` row math and `=SUM(E2:En)` totals.
- **CSV Bundle (ZIP):** Header and line-item CSV files with UTF-8 BOM encoding for seamless Excel import.
- **Audit PDF:** Official certified audit report showing timestamp, checksum, model versions, confidence scores, and compliance sign-off block.
- **Audit Ledger:** Every human correction is tracked in an immutable SQLite audit trail recording previous value, corrected value, reviewer ID, timestamp, and justification.

---

## 3. Evaluation & Benchmark Scoreboard
- **Synthetic Multilingual Corpus:** Evaluated across 6 standardized test suites covering English, German MwSt, Hindi GST, Arabic VAT RTL, blurry Japanese receipts, and adversarial prompt injections.
- **F1 Accuracy Gate:** Macro Field F1 > 0.95, Line Item F1 > 0.90, Math Pass Rate > 0.98.
- **Automated CI Regression Gate:** `python eval/run_eval.py && python eval/check_thresholds.py` runs on every pull request.
