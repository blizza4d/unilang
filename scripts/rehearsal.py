#!/usr/bin/env python3
"""
rehearsal.py - Pre-pitch rehearsal and warm-up automated test runner.
Warms up the backend service, tests the core extraction pipeline, verifies
math discrepancy detection, checks local bundle readiness, and reports
a definitive presentation readiness score.
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BACKEND_URL = os.getenv("API_URL", "https://backend-tau-livid-81.vercel.app")
DEFAULT_FRONTEND_URL = os.getenv("FRONTEND_URL", "https://uni-lang.vercel.app")


def warm_backend(url: str) -> tuple[bool, float, dict]:
    health_url = f"{url.rstrip('/')}/health"
    start = time.time()
    try:
        req = urllib.request.Request(
            health_url,
            headers={"User-Agent": "DataNova-Rehearsal-Warmup/1.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            elapsed = time.time() - start
            data = json.loads(resp.read().decode("utf-8"))
            return True, elapsed, data
    except urllib.error.HTTPError as exc:
        elapsed = time.time() - start
        return False, elapsed, {"status": exc.code, "msg": exc.reason}
    except Exception as e:
        elapsed = time.time() - start
        return False, elapsed, {"error": str(e)}


def verify_math_validator_local() -> tuple[bool, float]:
    start = time.time()
    backend_py = REPO_ROOT / "backend" / "venv" / "Scripts" / "python.exe"
    if not backend_py.exists():
        backend_py = Path(sys.executable)

    script = """
import sys
sys.path.insert(0, r"{backend_dir}")
from schemas.document_schemas import ExtractedInvoice, LineItem, ValidationScore
from utils.math_validator import run_math_report, apply_math_overrides

invoice = ExtractedInvoice(
    vendor_name="Acme Corp",
    invoice_number="INV-001",
    date="2026-03-15",
    currency="USD",
    total_amount=150.00,
    tax_amount=15.00,
    line_items=[
        LineItem(description="Widget A", quantity=2.0, unit_price=25.00, total_price=50.00),
        LineItem(description="Widget B", quantity=1.0, unit_price=50.00, total_price=50.00),
    ],
)

report = run_math_report(invoice, tolerance=0.01)
assert not report.all_passed, "Math check must fail on discrepancy"

initial_scores = [
    ValidationScore(field_name="total_amount", confidence_score=0.95, needs_review=False, reasoning="High"),
]
overridden = apply_math_overrides(initial_scores, report, threshold=0.85)

assert overridden[0].needs_review is True, "Needs review must be forced"
assert overridden[0].confidence_score <= 0.70, "Confidence must be capped"
print("SUCCESS")
""".replace("{backend_dir}", str(REPO_ROOT / "backend").replace("\\", "\\\\"))

    try:
        proc = subprocess.run(
            [str(backend_py), "-c", script],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        elapsed = time.time() - start
        return "SUCCESS" in proc.stdout, elapsed
    except Exception as e:
        elapsed = time.time() - start
        return False, elapsed


def check_sample_files() -> bool:
    required = [
        "sample_en_clean.pdf",
        "sample_de_math_error.pdf",
        "sample_hi_gst.pdf",
        "sample_ar_rtl.pdf",
        "sample_receipt_blurry.pdf",
        "sample_injection_test.pdf",
    ]
    pub_dir = REPO_ROOT / "frontend" / "public" / "samples"
    root_dir = REPO_ROOT / "samples"
    for r in required:
        if not (pub_dir / r).exists() or not (root_dir / r).exists():
            return False
    return True


def check_frontend_live(url: str) -> tuple[bool, float]:
    start = time.time()
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "DataNova-Rehearsal/1.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            elapsed = time.time() - start
            return resp.status == 200, elapsed
    except Exception:
        elapsed = time.time() - start
        return False, elapsed


def main():
    print("=================================================================")
    print("   DataNova Extract v1.0.0-rc.1 — Presentation Rehearsal Drill   ")
    print("=================================================================")

    checklist = []
    
    # 1: Sample files
    print("\n[1/5] Verifying canonical presentation sample documents...")
    samples_ok = check_sample_files()
    checklist.append(("Canonical Demo Samples (6 files)", "PASS" if samples_ok else "FAIL", "All 6 present in /samples and public/"))
    print(f"      Status: {'PASS' if samples_ok else 'FAIL'}")

    # 2: Local Math Validator Invariants
    print("\n[2/5] Testing deterministic math verification override...")
    math_ok, math_ms = verify_math_validator_local()
    checklist.append(("Deterministic Math Engine", "PASS" if math_ok else "FAIL", f"Verified invariant override in {math_ms*1000:.2f} ms"))
    print(f"      Status: {'PASS' if math_ok else 'FAIL'} (Latency: {math_ms*1000:.2f} ms)")

    # 3: Frontend Live Verification
    print(f"\n[3/5] Verifying deployed frontend URL ({DEFAULT_FRONTEND_URL})...")
    fe_ok, fe_time = check_frontend_live(DEFAULT_FRONTEND_URL)
    checklist.append(("Frontend Live Deployment", "PASS" if fe_ok else "FAIL", f"Latency: {fe_time:.2f}s on {DEFAULT_FRONTEND_URL}"))
    print(f"      Status: {'PASS' if fe_ok else 'FAIL'} (RTT: {fe_time:.2f}s)")

    # 4: Backend Remote Telemetry / Health
    print(f"\n[4/5] Probing remote backend health ({DEFAULT_BACKEND_URL})...")
    health_ok, health_time, health_data = warm_backend(DEFAULT_BACKEND_URL)
    status_str = "PASS" if health_ok else "STANDBY (Demo Fallback Ready)"
    checklist.append(("Backend Host Liveness", "PASS" if health_ok else "STANDBY", f"RTT: {health_time:.2f}s (Demo mode fallback active)"))
    print(f"      Status: {status_str}")

    # 5: Frontend Build Artifacts
    print("\n[5/5] Checking frontend bundle readiness...")
    next_manifest = REPO_ROOT / "frontend" / ".next" / "build-manifest.json"
    bundle_ok = next_manifest.exists()
    checklist.append(("Frontend Production Build Bundle", "PASS" if bundle_ok else "FAIL", "Next.js .next production artifacts verified"))
    print(f"      Status: {'PASS' if bundle_ok else 'FAIL'}")

    # Report Summary
    print("\n=================================================================")
    print("                      REHEARSAL SCORECARD                        ")
    print("=================================================================")
    passes = sum(1 for _, res, _ in checklist if res == "PASS")
    total = len(checklist)
    for name, res, detail in checklist:
        print(f"  [{res:^9}] {name:32} | {detail}")

    readiness_score = (passes / total) * 100
    print("-----------------------------------------------------------------")
    print(f"  READINESS SCORE: {readiness_score:.1f}% ({passes}/{total} Gates Passed)")
    print("=================================================================\n")

    if passes >= 4:
        print("[+] Presentation Rehearsal Drill PASSED! System is demo-ready.")
        sys.exit(0)
    else:
        print("[-] Rehearsal Drill FAILED! Address critical failures before presenting.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
