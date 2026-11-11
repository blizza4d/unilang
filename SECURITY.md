# Security Policy

DataNova Extract takes system integrity, data privacy, and model security seriously. This document describes our security architecture, supported releases, and reporting protocols.

---

## Supported Versions

| Version | Supported | Notes |
| :--- | :--- | :--- |
| `1.0.0-rc.1` | :white_check_mark: | Active Release Candidate |
| `< 1.0.0` | :x: | Experimental / Deprecated |

---

## Security Architecture & Defenses

### 1. Prompt Injection Mitigation
All untrusted text from uploaded documents, OCR streams, and user prompts passes through pre-execution heuristic and semantic sanitizers (`backend/services/security.py`).
- Delimiter escape patterns (e.g. `"""SYSTEM:`, `<|im_start|>`, `IGNORE PREVIOUS INSTRUCTIONS`) are detected and neutralized.
- Document text is isolated strictly in sandboxed data slots separate from system instructions.

### 2. Ephemeral Storage & Retention Policy
- Uploaded invoices and rendered images are stored temporarily in isolated namespaces.
- Retention is bounded (default 24 hours).
- Automated cleanup purging prevents accumulation of sensitive corporate financial data.

### 3. API Key & Secret Hygiene
- Provider keys (`OPENAI_API_KEY`, `GOOGLE_API_KEY`) are accessed strictly via server-side environment variables.
- No keys or tokens are ever exposed to client bundles or browser runtime.
- Client error telemetry strips query strings, headers, and payload bodies before logging.

### 4. Deterministic Math Override
- LLM outputs are never trusted unconditionally for financial calculations.
- A deterministic arithmetic engine reconciles line item multiplications and grand totals independently.
- Any discrepancy instantly forces human-in-the-loop review and caps confidence ratings.

---

## Reporting a Vulnerability

If you discover a security vulnerability or security bug, please report it privately:
1. **Email:** Send details to `security@datanova-extract.ai` (or via private GitHub vulnerability advisory).
2. **Details:** Include reproduction steps, environment details, and affected components.
3. **Response SLA:** We acknowledge vulnerability reports within 24 hours and aim for patch deployment within 72 hours for critical issues.

Please do not open public GitHub issues for undisclosed security vulnerabilities.
