# Hackathon Written Submission Package (SUBMISSION.md)

This document provides copy-ready submission text blocks formatted for Devpost, DoraHacks, or internal portal submission forms.

---

## 1. Project Title & Tagline
**DataNova Extract: Multilingual Document AI with Math Verification**  
*(Length: 68 characters — limit: 80 characters)*

---

## 2. Short Description
DataNova Extract is a production-grade, multilingual invoice understanding studio powered by LangGraph multi-agent orchestration, deterministic arithmetic override validation (100% discrepancy detection), interactive visual bounding-box grounding, and the kinematic Nova Droid companion.  
*(Length: 292 characters — limit: 300 characters)*

---

## 3. Long Description (Comprehensive Pitch)
*(Word count: 524 words)*

### Inspiration
Global financial operations lose millions of dollars every year to accounting errors and manual data entry bottlenecks. While modern generative vision-language models excel at reading messy visual layouts, they have a dangerous flaw in financial workflows: **they hallucinate arithmetic**. A model will confidently extract line items and invent an incorrect grand total, or miss that a discount was never applied. We built DataNova Extract to give enterprise finance teams the best of both worlds: the multilingual visual fluency of multi-agent LLMs paired with an uncompromising, deterministic arithmetic engine that never allows a math error to slip through undetected.

### What It Does
DataNova Extract ingests invoices, receipts, and tax filings in PDF and image formats across six distinct script families (Latin, Devanagari, Tamil, Arabic RTL, Chinese, and Japanese). It parses complex table layouts, handles non-standard punctuation (such as European comma decimals and Indian lakh separators), visually grounds every extracted value with normalized bounding boxes, and streams real-time stage updates to the browser. Most importantly, it executes an independent mathematical reconciliation: if calculated totals disagree with stated totals by even one cent, the system automatically flags the field in amber, caps the confidence score, and routes the document to an interactive human-in-the-loop review interface.

### How We Built It
- **Multi-Agent Orchestration:** Powered by LangGraph, coordinating specialized agents for Document Classification, Vision Ingestion, Structured Entity Extraction, and Evaluation.
- **Deterministic Math Override:** Implemented with Python Decimal arithmetic, enforcing strict line-item summations, tax verifications, and grand total reconciliations ($0.01 tolerance).
- **Interactive UI & Motion:** Built in Next.js 15, React 19, and Tailwind CSS. Features our custom "Nova" Droid—a kinematic SVG character with a skate-free parametric walking cycle that physically mirrors pipeline activity.
- **Visual Grounding:** Bounding boxes are normalized to [0..1000] coordinates and linked bidirectionally between the PDF canvas and extracted form fields.
- **Enterprise Controls:** Integrated spend caps ($2/hr, $10/day), ephemeral 24-hour document retention, and zero-disruption demo mode fallback.

### Challenges We Overcame
Balancing asynchronous Server-Sent Events across worker threads with client-side abort controllers required rigorous coroutine isolation. Furthermore, normalizing OCR bounding boxes across arbitrary aspect ratios without drift demanded an exact clamping parity contract between backend schemas and frontend canvas renderers.

### Accomplishments We Are Proud Of
- Measured **95.58% Macro F1** across 42 realistic multilingual test cases.
- Achieved **100.00% detection rate** on arithmetic discrepancies.
- Maintained **50/50 passing tests** in randomized order (5.90s).
- Compact production bundle: 103 kB shared First Load JS.

### What We Learned
Deterministic code must always serve as the supervisory gatekeeper for generative AI. Where models provide semantic understanding, traditional deterministic algorithms must enforce invariant truth.

### What Is Next
Post-hackathon plans include vendor template memory caching, ERP connectors (SAP, NetSuite, QuickBooks), and on-premise privacy deployments with local vLLM instances.

---

## 4. Tech Stack & "Built With" Tags
- `Next.js 15 (App Router)`
- `React 19`
- `FastAPI (Python 3.13)`
- `LangGraph & LangChain`
- `OpenAI GPT-4o & Google Gemini 2.5 Flash`
- `Tailwind CSS & Framer Motion`
- `PyMuPDF / ReportLab / Poppler`
- `Playwright & Pytest`
- `Vercel Serverless Hosting`

---

## 5. Project Links
- **Live Interactive Demo:** https://uni-lang.vercel.app/
- **GitHub Repository:** https://github.com/blizza4d/unilang
- **Backend API URL:** https://backend-tau-livid-81.vercel.app
- **Demo Video:** `[USER: Insert YouTube / Loom / Vimeo link]`
- **Presentation Deck:** `[USER: Insert Google Slides / Pitch.com link]`

---

## 6. Team Information
- `[USER: Add Team Name]`
- `[USER: Team Member 1 - Role, Contact / LinkedIn]`
- `[USER: Team Member 2 - Role, Contact / LinkedIn]`

---

## 7. Instructions for Judges (60-Second Walkthrough)
1. Navigate to **https://uni-lang.vercel.app/**.
2. In the left panel, click the quick sample button: **"German (Math Error)"**.
3. Watch the **Nova Droid** walk to the document and track live stages: Ingestion -> Vision -> Extraction.
4. Notice the document is flagged: **`REQUIRES HUMAN REVIEW`** because the stated total (€3,475.00) differs from the calculated sum (€2,975.00).
5. Press **`R`** on your keyboard to enter Review Mode. Hover over the Total Amount field to see its exact bounding box highlighted on the PDF.
6. Correct the total to `2975.00`. The error clears, status upgrades to **`APPROVED`**, and Nova celebrates.
7. Click **`Export -> Excel`** to download an audit-ready spreadsheet with native formulas.

---

## 8. Responsible AI Statement
- **Zero Silent Hallucinations:** Generative models are never permitted to approve financial calculations autonomously.
- **Ephemeral Storage:** Ingested documents and temporary artifacts are permanently purged after 24 hours.
- **Adversarial Resilience:** Pre-execution scanners neutralize prompt injection attempts in document text.
- **Transparent Attribution:** Every demo-mode export contains an explicit `DEMO MODE DATA` watermark to prevent accidental production usage.

---

## 9. Known Limitations
- Hand-drawn sketches and non-standard handwritten receipts are not yet optimized (evaluated primarily on digital and printed documents).
- Maximum document size is bounded at 15 MB and 8 pages per upload for serverless execution limits.
