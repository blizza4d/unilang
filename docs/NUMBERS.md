# Official Measured Metrics Ledger (NUMBERS.md)

This document is the **Single Source of Truth** for all quantitative claims, performance benchmarks, and test measurements cited across DataNova Extract v1.0.0-rc.1 documentation, pitch decks, demo scripts, and user-interface statistics.

Any number not explicitly listed in this table is unproven and must not appear in marketing copy or hackathon submission materials.

---

## 1. Quality & Accuracy Metrics

| Metric | Measured Value | Sample Size / Basis | Evaluation Date | Mode / Environment | Source / Test File |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Overall Macro Field F1** | **95.58%** | 42 test cases | 2026-11-10 | Realistic Multilingual Fixture Benchmark | `backend/eval/run_realistic.py` |
| **Critical Field Exact Match** | **69.05%** | 42 test cases | 2026-11-10 | Realistic Multilingual Fixture Benchmark | `backend/eval/run_realistic.py` |
| **Arithmetic Discrepancy Detection (TPR)** | **100.00%** | Adversarial math error cases | 2026-11-10 | Deterministic Math Validator Override | `backend/tests/test_math_validator.py` |
| **Clean Invoice Math Pass Rate** | **97.62%** | 41 clean/standard cases | 2026-11-10 | Deterministic Math Validator | `backend/eval/run_realistic.py` |
| **Prompt Injection Attack Neutralization** | **100.00%** | Adversarial prompt injection attacks | 2026-11-10 | Security Pre-Execution Scanner | `backend/tests/unit/test_security.py` |
| **Latin Script Recognition F1** | **94.41%** | 20 Latin cases (EN, DE, FR, ES) | 2026-11-10 | Multilingual Benchmark | `docs/REALISTIC_BENCHMARK_RESULTS.md` |
| **Devanagari Script Recognition F1** | **100.00%** | 5 Hindi GST cases | 2026-11-10 | Multilingual Benchmark | `docs/REALISTIC_BENCHMARK_RESULTS.md` |
| **Tamil Script Recognition F1** | **100.00%** | 4 Tamil invoice cases | 2026-11-10 | Multilingual Benchmark | `docs/REALISTIC_BENCHMARK_RESULTS.md` |
| **Arabic Script Recognition F1** | **100.00%** | 4 Arabic RTL invoice cases | 2026-11-10 | Multilingual Benchmark | `docs/REALISTIC_BENCHMARK_RESULTS.md` |
| **CJK (Chinese) Recognition F1** | **100.00%** | 2 Chinese Fapiao cases | 2026-11-10 | Multilingual Benchmark | `docs/REALISTIC_BENCHMARK_RESULTS.md` |
| **CJK (Japanese) Recognition F1** | **85.71%** | 4 Japanese invoice cases | 2026-11-10 | Multilingual Benchmark | `docs/REALISTIC_BENCHMARK_RESULTS.md` |

---

## 2. Latency & Performance

| Metric | Measured Value | Sample Size / Basis | Evaluation Date | Mode / Environment | Source / Test File |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Evaluation Math Pacing (p50)** | **10.7 ms** | 42 benchmark cases | 2026-11-10 | Local Runner / In-Process | `docs/REALISTIC_BENCHMARK_RESULTS.md` |
| **Evaluation Math Pacing (p95)** | **12.4 ms** | 42 benchmark cases | 2026-11-10 | Local Runner / In-Process | `docs/REALISTIC_BENCHMARK_RESULTS.md` |
| **Deterministic Math Override Execution** | **< 1.0 ms** | Unit test execution | 2026-11-10 | Python 3.13 / Decimal engine | `backend/services/math_validator.py` |
| **Backend Unit & Integration Suite** | **5.90 s** | 50 tests passing (100%) | 2026-11-10 | Randomized pytest seed | `backend/tests/` |
| **Frontend Production Build Time** | **5.2 s** | Static page prerendering (4/4) | 2026-11-10 | Next.js 15.5.28 Turbo build | `frontend/package.json` |
| **Frontend Shared First Load JS** | **103 kB** | Production chunk bundle | 2026-11-10 | Next.js build analyzer | `frontend/package.json` |
| **Frontend Index Route Size** | **86.6 kB** | Gzip route bundle | 2026-11-10 | Next.js build analyzer | `frontend/app/page.tsx` |

---

## 3. System Constraints & Operating Ceilings

| Parameter | Enforced Value | Enforcement Mechanism | Code Reference |
| :--- | :--- | :--- | :--- |
| **Maximum Upload File Size** | **15 MB** | Pre-read HTTP content-length & stream check | `backend/config.py:MAX_UPLOAD_MB` |
| **Maximum PDF Page Count** | **8 pages** | PyMuPDF / pdfinfo page probe | `backend/config.py:MAX_PDF_PAGES` |
| **Batch Multi-File Queue Limit** | **20 files** | Client and server array size gate | `backend/config.py:MAX_BATCH_FILES` |
| **Math Verification Tolerance** | **$0.01** | Absolute decimal difference gate | `backend/config.py:MATH_TOLERANCE` |
| **Review Trigger Confidence Threshold** | **0.85** | Document overall score threshold | `backend/config.py:REVIEW_THRESHOLD` |
| **Math Failure Confidence Ceiling** | **0.70** | Forced downgrade upon arithmetic error | `backend/services/math_validator.py` |
| **Hourly Live AI Budget Limit** | **$2.00** | Token accumulation rate middleware | `backend/config.py:HOURLY_BUDGET_USD` |
| **Daily Live AI Budget Limit** | **$10.00** | Token accumulation rate middleware | `backend/config.py:DAILY_BUDGET_USD` |
| **Burst Rate Limit** | **10 requests** | Token bucket per client IP | `backend/config.py:RATE_LIMIT_BURST` |
| **Sustained Rate Limit** | **30 req / min** | Sliding window rate limiter | `backend/config.py:RATE_LIMIT_PER_MINUTE` |
| **Ephemeral Document Retention** | **24 hours** | Scheduled purge job | `backend/services/storage.py` |
