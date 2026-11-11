# Changelog

All notable changes to **DataNova Extract** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0-rc.1] - 2026-11-10

### Release Overview
This Release Candidate unifies and hardens the work across three foundational engineering passes:
1. **Pass 1 (Fix Everything):** Deployment wiring, CORS, backend boot resilience, multi-agent pipeline, SSE streaming, frontend features, and initial contract unification.
2. **Pass 2 (Post-Fix Hardening):** Elimination of false success, deterministic arithmetic validation overrides, ground-truth visual bounding-box clamping, realistic 42-case multilingual benchmarking (95.58% Macro F1), chaos drills, budget controls, and export watermarking.
3. **Pass 3 (UI Excellence & Droid Rig):** Analog AI design token system, micro-interactions, accessibility compliance (`prefers-reduced-motion`, polite ARIA live regions), and the "Nova" kinematic walking SVG character tied to real pipeline states.

### Added
- **Nova Kinematic Walking Droid Rig (`frontend/components/droid/`):**
  - Continuous skate-free kinematic parametric walk cycle (`useWalkCycle.ts`) with forward-lean trajectory and dual-frequency bounce.
  - Multi-stage companion controller (`DroidCompanion.tsx`, `StageStrip.tsx`) synchronizing character expressions to real pipeline events (`boot`, `walk`, `scan`, `review`, `celebrate`, `sleep`).
  - Full support for `prefers-reduced-motion` with graceful static SVG sprite fallback (`DroidSprite.tsx`).
- **Deterministic Math Validation Overrides (`backend/services/math_validator.py`):**
  - Strict line-item and grand-total arithmetic reconciliation with $0.01 tolerance.
  - High-precision float-drift mitigation and automatic downgrade of overall document confidence to capped review thresholds upon failure.
- **Realistic Multilingual Evaluation Suite (`backend/eval/`):**
  - 42 deterministic realistic test cases across 6 script families (Latin, Devanagari, Tamil, Arabic, Japanese Kanji/Kana, Simplified Chinese).
  - Empirical metrics harness reporting 95.58% Macro F1 and 100.00% arithmetic discrepancy detection.
- **Budget & Cost Protection (`backend/middleware/budget_limit.py`):**
  - Per-hour ($2.00) and per-day ($10.00) spend ceilings with automatic fallback to demo mode upon exhaustion.
- **Export Watermarking & Compliance (`backend/services/exporters.py`):**
  - Visible `DEMO MODE DATA` watermarks on PDF, CSV, and XLSX exports when operating on synthetic fixtures.
- **Release Tooling & Governance:**
  - `scripts/bump_version.py` for atomic multi-file version synchronization.
  - `scripts/check_claims.py` verifying that all public metrics trace to `docs/NUMBERS.md`.
  - `scripts/release_gate.py` asserting all 12 launch quality gates pass.
  - `frontend/components/layout/Footer.tsx` displaying semantic version, git commit SHA, environment label, and shortcut cues.

### Changed
- **Unified Design Tokens (`frontend/styles/tokens.css`):**
  - Replaced arbitrary hex colors across components with canonical palette tokens (`--charcoal`, `--cream`, `--sage`, `--amber`, `--terracotta`).
  - Standardized interactive buttons on the shared `Button` and `IconButton` primitives.
- **Centralized API URL Resolution (`frontend/lib/config.ts`):**
  - Dynamic environment-aware endpoint resolution with automatic protocol upgrades and production fallback.
- **Header & Navigation Bar:**
  - Upgraded release indicator chip to `v1.0.0-rc.1 • LangGraph Control Tower`.
  - Enforced single-row flex layout with zero button collisions.

### Fixed
- **DEF-001 (FastAPI Route Argument Injection):** Resolved `FastAPIError` where `Request | None` was incorrectly parsed as a Pydantic body parameter.
- **DEF-002 (Exporter Timestamp Crash):** Fixed `AttributeError` in `export_pdf` caused by uninitialized `created_at` in internal records.
- **DEF-003 (SSE Thread-Safety Disconnect):** Replaced direct `asyncio.get_event_loop()` invocation inside worker threads with thread-safe coroutine dispatching.
- **DEF-004 (CORS Subdomain Regex):** Corrected regex pattern matching on Vercel preview environments (`https://*.vercel.app`).
- **DEF-005 (Bounding Box Coordinate Parity):** Enforced [ymin, xmin, ymax, xmax] coordinate ordering and bounds clamping across all grounding boxes.

### Removed
- **Unverified & Fragile Mock Modes:** Removed brittle mock routes and unverified third-party analytics scripts.
- **Raw Hex Colors:** Eliminated unstructured CSS styling in favor of the unified design system.

### Security
- **Strict Prompt Injection Scanner (`backend/services/security.py`):** Pre-execution detection of override delimiters, instructions, and system prompt tampering.
- **Storage Path Traversal Protection:** Hardened local storage key sanitation against directory traversal (`../`).
- **Ephemeral Upload Purging:** Scheduled retention expiration policy for temporary document artifacts.

---

## [0.9.0] - 2026-11-04
### Added
- Initial LangGraph multi-agent orchestration (Vision, Extractor, Judge).
- Fast keyword document classification and schema routing.
- Basic Next.js split-workspace user interface.
