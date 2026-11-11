# Claims Ledger (CLAIMS_LEDGER.md)

This ledger tracks every marketing, architectural, and quantitative claim made across DataNova Extract v1.0.0-rc.1 documentation, user interface, pitch materials, and submission narratives.

Each claim is cross-referenced with empirical evidence, test results, and verified measurement dates.

---

## Claims Audit Table

| ID | Public Claim | Where It Appears | Concrete Evidence & Verification | Measured Value & Date | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-001** | **Overall Field Macro F1 of 95.58%** | README, Submission, Pitch, Scoreboard | `backend/eval/run_realistic.py` executed across 42 multilingual cases | 95.58% Macro F1 (2026-11-10) | **Proven** |
| **CLM-002** | **100% Arithmetic Discrepancy Detection** | README, UI, Pitch, Submission | `backend/tests/test_math_validator.py` asserting line-item & grand-total discrepancy catches | 100.00% TPR (2026-11-10) | **Proven** |
| **CLM-003** | **Deterministic Math Validation Override** | Architecture, README, Submission | `backend/services/math_validator.py:apply_math_overrides` capping score at 0.70 and setting `REQUIRES_HUMAN_REVIEW` | Enforced in code & tests (2026-11-10) | **Proven** |
| **CLM-004** | **Multilingual Support Across 6 Script Families** | README, Header, Submission | Evaluated on Latin (94.41%), Devanagari (100%), Tamil (100%), Arabic (100%), CJK (Chinese 100%, Japanese 85.71%) | `docs/REALISTIC_BENCHMARK_RESULTS.md` (2026-11-10) | **Proven** |
| **CLM-005** | **Pre-Execution Prompt Injection Defense** | Architecture, Security Policy, Submission | `backend/tests/unit/test_security.py::test_scan_for_prompt_injection_attacks` | 100% neutralized across test battery (2026-11-10) | **Proven** |
| **CLM-006** | **Real-Time Visual Grounding Coordinates** | DocumentViewer, PageCanvas, Pitch | `backend/schemas/grounding.py` coordinate clamping `[0..1000]` normalized to container dimensions | Verified in `test_grounding.py` (2026-11-10) | **Proven** |
| **CLM-007** | **Batch Processing Up to 20 Invoices** | BatchQueue, README, UI | `backend/config.py:MAX_BATCH_FILES = 20`, frontend client queue enforced | 20 documents max (2026-11-10) | **Proven** |
| **CLM-008** | **Spend Cap & Abuse Guard ($2/hr, $10/day)** | BackendStatusBanner, Architecture | `backend/middleware/budget_limit.py` tracking live token costs with auto-fallback to demo mode | Enforced in middleware (2026-11-10) | **Proven** |
| **CLM-009** | **Continuous Kinematic Walking Droid Rig** | UI, DroidCompanion, WalkCycle | Parametric sine-wave foot planting and bobbing in `useWalkCycle.ts` without frame-skate | Reduced-motion tested (2026-11-10) | **Proven** |
| **CLM-010** | **Sub-Second Math Override Execution** | Architecture, Pitch | Python Decimal arithmetic execution takes < 1 ms | Measured at 0.1 ms p50 (2026-11-10) | **Proven** |
| **CLM-011** | **Zero-Disruption Demo Mode with Watermarked Exports** | Exporters, UI, Submission | `exporters.py` writes explicit `DEMO MODE DATA` watermark across PDF, CSV, and XLSX | Verified in `test_pipeline_v2.py` (2026-11-10) | **Proven** |
| **CLM-012** | **"Production-Ready / Enterprise Grade"** | README, Initial Drafts | *Softened to specific statements:* Single-node SQLite in development/demo, PostgreSQL required in production, stateless horizontal scalability with S3 storage | Refined in documentation (2026-11-10) | **Softened** |
| **CLM-013** | **"Universal 100+ Language Support"** | Early Drafts | *Removed:* Only claim scripts with verified tests (Latin, Devanagari, Tamil, Arabic, Chinese, Japanese) | Removed unverified languages (2026-11-10) | **Removed** |
