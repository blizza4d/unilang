# Post-Launch Roadmap & Technical Debt Register (ROADMAP.md)

This document outlines the post-hackathon engineering roadmap for DataNova Extract through 2027, grouped by theme, with estimated Impact, Effort, and Risk.

---

## 1. Product & Architecture Roadmap

### Theme A: Accuracy & Extraction Depth
| Item | Description | Impact | Effort | Risk | Timeline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Multi-Page Spanning Tables** | Implement sliding-window chunking across 4+ page invoices with repeated headers. | High | Medium | Low | Q1 2027 |
| **Handwritten Receipt OCR** | Integrate specialized offline handwritten fine-tunes (TrOCR or Qwen2-VL) for low-quality thermal receipts. | Medium | High | Medium | Q1 2027 |
| **Custom Schema Builder** | Allow users to visually define arbitrary key-value schemas (bills of lading, customs declarations) in the UI. | High | High | Low | Q2 2027 |
| **Vendor Template Memory** | Cache coordinate layouts for recurring vendors to bypass vision LLM calls for 80% lower latency and cost. | High | Medium | Low | Q2 2027 |

### Theme B: Enterprise & ERP Integration
| Item | Description | Impact | Effort | Risk | Timeline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SAP S/4HANA & NetSuite Connectors** | Two-way REST and webhook syncing to push approved invoices directly to AP ledgers. | High | High | Medium | Q2 2027 |
| **Three-Way Matching** | Automatically reconcile invoice line items against purchase orders (PO) and receiving receipts. | High | High | High | Q3 2027 |
| **SSO / OIDC Authentication** | Enterprise Single Sign-On (Okta, Azure AD, Google Workspace) via standard JWT validation. | Medium | Low | Low | Q1 2027 |

### Theme C: Privacy, On-Premise & Local AI
| Item | Description | Impact | Effort | Risk | Timeline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Air-Gapped Appliance** | Package system into single Docker Compose / Helm chart with local vLLM (DeepSeek-R1 / Qwen2.5-VL). | High | High | Medium | Q3 2027 |
| **Zero Data Retention Enclaves** | Confidential computing containers (AWS Nitro Enclaves) guaranteeing zero disk persistence. | High | High | High | Q4 2027 |

---

## 2. Technical Debt Register

| ID | Component | Debt Description | Planned Remediation | Target Milestone |
| :--- | :--- | :--- | :--- | :--- |
| **DEBT-001** | Database Engine | Development relies on SQLite single-worker mode. High concurrency requires PostgreSQL. | Enforce PostgreSQL via asyncpg in all staging/production environments. | Q1 2027 |
| **DEBT-002** | PDF Rasterization | PDF page rendering is currently executed in-process with PyMuPDF/Poppler. | Offload CPU-heavy rasterization to asynchronous Redis Celery worker queue. | Q1 2027 |
| **DEBT-003** | Frontend E2E Coverage | Playwright test suite requires live browser headless environment in CI. | Add GitHub Actions headless Linux Playwright runner with xvfb. | Q1 2027 |
| **DEBT-004** | Client Bundle Optimization | Framer Motion chunk adds 46 kB to initial bundle. | Replace dynamic layout animations with pure CSS transforms where feasible. | Q2 2027 |
