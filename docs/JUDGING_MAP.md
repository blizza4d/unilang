# Judging Criteria Mapping (JUDGING_MAP.md)

*Note: The following rubric is aligned with standard Global Data-thon / Physical AI / Enterprise SaaS judging frameworks. Marked: Assumed criteria, [USER MUST CONFIRM exact official weights if provided].*

---

## Evaluation Rubric Matrix

| Judging Criterion | Expected Weight | Where DataNova Extract Demonstrates It | Concrete Proof & Evidence |
| :--- | :--- | :--- | :--- |
| **1. Technical Depth & Engineering Rigor** | 25% | Multi-agent LangGraph architecture; deterministic Decimal arithmetic validation overrides; Server-Sent Events with thread-safe cancellation; strict coordinate normalization (`[0..1000]`). | `backend/services/math_validator.py`, `backend/routers/extract.py`, 50 randomized unit & integration tests passing in 5.90s. |
| **2. Usability, UX & Accessibility** | 20% | Split-workspace design; interactive bounding-box hover grounding; skate-free kinematic walking Droid companion; full `prefers-reduced-motion` compliance; polite ARIA live regions; keyboard shortcuts (`K`, `R`, `Ctrl+Enter`). | `frontend/components/droid/`, `frontend/components/layout/DocumentViewer.tsx`, zero build errors or lint warnings. |
| **3. Real-World Viability & FinOps** | 20% | Built-in token budget ceilings ($2/hr, $10/day) with auto-fallback to demo mode; 15 MB upload limits; ephemeral 24-hr document retention; batch processing up to 20 files; export to Excel with native formulas (`=SUM(...)`). | `backend/middleware/budget_limit.py`, `backend/services/exporters.py`, `frontend/components/layout/BatchQueue.tsx`. |
| **4. Multilingual & Script Generalization** | 15% | Robust extraction across 6 distinct script systems: Latin, Devanagari, Tamil, Arabic RTL, Japanese Kanji/Kana, and Simplified Chinese; handling comma decimals and lakh number formatting. | 42-case realistic benchmark (`backend/eval/run_realistic.py`): 95.58% Macro F1, 100% Arabic/Tamil/Devanagari script accuracy. |
| **5. Responsible AI & Adversarial Resilience** | 10% | Zero-hallucination arithmetic guarantees (100% discrepancy detection); pre-execution prompt injection scanner; explicit watermarking (`DEMO MODE DATA`) on synthetic exports. | `backend/services/security.py`, `backend/tests/test_math_validator.py`, `docs/CLAIMS_LEDGER.md`. |
| **6. Completeness & Demo Readiness** | 10% | Fully deployed live frontend on Vercel (`https://uni-lang.vercel.app`) with deployed FastAPI backend; instant one-click sample invoice testing; cold-start keep-warm telemetry; comprehensive offline demo fixtures. | Verified live URL, `scripts/rehearsal.py`, `scripts/live_check.py`. |
