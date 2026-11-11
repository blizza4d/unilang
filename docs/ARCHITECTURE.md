# Architecture Specification: DataNova Extract v1.0.0-rc.1 (ARCHITECTURE.md)

DataNova Extract is built on an asynchronous, multi-agent pipeline pairing frontier generative vision models with a deterministic mathematical supervisory layer.

---

## 1. System Topology Overview

```mermaid
flowchart TD
    subgraph Client ["Client Browser Runtime (Next.js 15 / React 19)"]
        UI[Split-Workspace UI]
        Viewer[2D Document Canvas & Bounding Boxes]
        Editor[Interactive Review & Form Editor]
        Droid[Kinematic Nova Droid Controller]
        Store[Zustand Document & History Store]
    end

    subgraph Edge ["Vercel Edge & Static CDN"]
        CDN[Static Assets / SSR / Fonts]
        EnvRouter[Environment-Aware API URL Router]
    end

    subgraph Backend ["FastAPI Control Tower (Python 3.13)"]
        Router[API Router: /api/v1/extract/stream]
        SecScan[Pre-Execution Security & Prompt-Injection Filter]
        BudgetMid[Token Spend Ceiling Middleware: $2/hr, $10/day]
        CORS[CORS Hardened Regex Middleware]
        
        subgraph Agents ["LangGraph Multi-Agent Orchestration"]
            Classifier[Document Classifier Agent]
            Vision[Vision Ingestion Agent: Gemini 2.5 Flash]
            Extractor[Structured Extractor Agent: GPT-4o]
            Judge[Evaluation & Schema Compliance Agent]
        end

        subgraph Invariants ["Deterministic Code Invariant Engine"]
            MathVal[Python Decimal Arithmetic Validator: $0.01 tolerance]
            GroundClamper[Coordinate Normalizer & Clamper: 0..1000]
        end

        subgraph Persistence ["Persistence & Storage Layer"]
            DB[(SQLite / PostgreSQL Async Engine)]
            Storage[Ephemeral Local / S3 Document Storage]
            Exporter[Formula Excel, CSV & Watermarked PDF Generator]
        end
    end

    UI --> Store
    Store --> Viewer
    Store --> Editor
    Store --> Droid
    CDN --> UI
    
    UI -- "POST /api/v1/extract/stream (SSE)" --> CORS
    CORS --> BudgetMid
    BudgetMid --> Router
    Router --> SecScan
    SecScan --> Classifier
    Classifier --> Vision
    Vision --> Extractor
    Extractor --> MathVal
    MathVal -- "Discrepancy Detected (Override Status)" --> Judge
    MathVal -- "Math Verified" --> Judge
    Judge --> GroundClamper
    GroundClamper -- "SSE Events" --> Router
    Router -- "data: {stage, result}" --> Store
    Store -- "Export Document" --> Exporter
    Exporter --> DB
```

---

## 2. Multi-Agent Pipeline Specifications

### Agent 1: Fast Heuristic Classifier Agent
- **Role:** Analyzes raw bytes, MIME type, and preliminary OCR text tokens.
- **Routing:** Identifies document language, script family (Latin, Devanagari, Arabic, Tamil, CJK), and structural typology (single-column, multi-column, receipt, landscape).
- **Latency:** < 15 ms.

### Agent 2: Vision Ingestion Agent
- **Model:** Google Gemini 2.5 Flash (or local Poppler rasterizer at 200 DPI).
- **Role:** Detects bounding boxes, multi-line table grids, currency symbols, and orientation.
- **Cost:** ~$0.001 per page.

### Agent 3: Structured Extractor Agent
- **Model:** OpenAI GPT-4o.
- **Role:** Extracts structured fields into strongly typed Pydantic models with `extra="forbid"`.
- **Validation:** Enforces decimal numbers, ISO 8601 dates, and currency code parity.

### Agent 4: Deterministic Math Engine (Invariant Supervisory Layer)
- **Engine:** Python `decimal.Decimal` with fixed 2-place precision.
- **Rules:**
  1. $\sum (\text{Quantity} \times \text{Unit Price}) = \text{Line Item Total} \pm \$0.01$
  2. $\sum (\text{Line Item Totals}) + \text{Tax} = \text{Grand Total} \pm \$0.01$
  3. Subtotal + CGST + SGST = Grand Total (Dual GST rule).
- **Override Action:** If any check fails, the document confidence is capped at `0.70`, the overall status is forced to `REQUIRES_HUMAN_REVIEW`, and the failing field is tagged for glowing amber review. Code always trumps model output.

### Agent 5: 2D Spatial Grounding Normalizer
- **Coordinate Space:** Normalized `[ymin, xmin, ymax, xmax]` within $[0, 1000]$.
- **Contract:** All coordinates are clamped against image bounds $[0, 1000]$. Inverted coordinates are automatically repaired. Frontend translates coordinates into CSS percentages:
  $$\text{left} = \frac{\text{xmin}}{10} \%, \quad \text{top} = \frac{\text{ymin}}{10} \%, \quad \text{width} = \frac{\text{xmax} - \text{xmin}}{10} \%, \quad \text{height} = \frac{\text{ymax} - \text{ymin}}{10} \%$$

---

## 3. Real-Time Streaming & Lifecycle Events
Communication between the backend and browser uses Server-Sent Events (`text/event-stream`):
1. `stage_start` (`stage: "ingestion"`, `elapsed_ms: 50`)
2. `stage_start` (`stage: "vision"`, `elapsed_ms: 320`)
3. `stage_start` (`stage: "extraction"`, `elapsed_ms: 1200`)
4. `stage_start` (`stage: "math_verification"`, `elapsed_ms: 1210`)
5. `result` (`data: ExtendedDocumentResponse`, `elapsed_ms: 1250`)
6. `done` (`summary: {status: "APPROVED" | "REQUIRES_HUMAN_REVIEW"}`)

Each event updates the Nova Droid state and stage progress bar without blocking UI interaction.
