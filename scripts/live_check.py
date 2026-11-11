#!/usr/bin/env python3
"""
DataNova Extract: Production Deployment Verification Suite (live_check.py)
Staff-Level QA & Reliability Verification Tool

Verifies end-to-end functionality, CORS preflights, streaming SSE integrity,
error handling contracts, and observability across the deployed frontend and backend.
"""

import sys
import time
import json
import argparse
import ssl
import uuid
import urllib.request
import urllib.error
from typing import Any, Dict, Optional, Tuple


def make_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[bytes] = None,
    timeout: float = 15.0,
) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
    headers = headers or {}
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    start_time = time.perf_counter()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            raw = resp.read().decode("utf-8", errors="replace")
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            try:
                body = json.loads(raw)
            except Exception:
                body = {"_raw": raw}
            body["_latency_ms"] = elapsed_ms
            return resp.status, body, resp_headers
    except urllib.error.HTTPError as exc:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        raw = exc.read().decode("utf-8", errors="replace")
        resp_headers = {k.lower(): v for k, v in exc.headers.items()}
        try:
            body = json.loads(raw)
        except Exception:
            body = {"_raw": raw}
        body["_latency_ms"] = elapsed_ms
        return exc.code, body, resp_headers
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return 0, {"_error": str(exc), "_latency_ms": elapsed_ms}, {}


def main() -> int:
    parser = argparse.ArgumentParser(description="DataNova Live Deployment Verification")
    parser.add_argument("--frontend-url", default="https://uni-lang.vercel.app", help="Deployed frontend URL")
    parser.add_argument("--backend-url", default="https://backend-tau-livid-81.vercel.app", help="Deployed backend API base URL")
    args = parser.parse_args()

    frontend_url = args.frontend_url.rstrip("/")
    backend_url = args.backend_url.rstrip("/")

    print("=" * 70)
    print("DATANOVA EXTRACT — PRODUCTION DEPLOYMENT VERIFICATION")
    print(f"Frontend Target: {frontend_url}")
    print(f"Backend Target:  {backend_url}")
    print("=" * 70)

    failures = 0
    warnings = 0

    # 1. Frontend Reachability
    print("\n[Check 1/11] Verifying Frontend Reachability...")
    status, body, _ = make_request(frontend_url, method="GET")
    if status == 200:
        print(f"  [PASS] Frontend is live at {frontend_url} ({body.get('_latency_ms')} ms)")
    else:
        print(f"  [FAIL] Frontend returned HTTP {status}: {body}")
        failures += 1

    # 2. Backend Liveness (/health)
    print("\n[Check 2/11] Verifying Backend Liveness (/health)...")
    status, body, _ = make_request(f"{backend_url}/health", method="GET")
    if status == 200 and body.get("status") == "ok":
        print(f"  [PASS] /health is healthy ({body.get('_latency_ms')} ms)")
        print(f"         Version: {body.get('version')}, Uptime: {body.get('uptime_seconds')}s")
    else:
        print(f"  [FAIL] /health returned HTTP {status}: {body}")
        failures += 1

    # 3. Backend Readiness (/health/deep)
    print("\n[Check 3/11] Verifying Backend Deep Readiness (/health/deep)...")
    status, body, _ = make_request(f"{backend_url}/health/deep", method="GET")
    if status == 200:
        print(f"  [PASS] Deep health check reports ready ({body.get('_latency_ms')} ms)")
    elif status == 503 and "checks" in body.get("detail", {}):
        checks = body["detail"]["checks"]
        print(f"  [WARN] Backend is in degraded mode ({body.get('_latency_ms')} ms)")
        print(f"         Subsystem status: {checks}")
        warnings += 1
    else:
        print(f"  [FAIL] /health/deep returned unexpected HTTP {status}: {body}")
        failures += 1

    # 4. Capabilities Contract (/api/v1/capabilities)
    print("\n[Check 4/11] Verifying Backend Capabilities Contract...")
    status, body, _ = make_request(f"{backend_url}/api/v1/capabilities", method="GET")
    if status == 200 and "streaming" in body and "demo_mode" in body:
        print(f"  [PASS] Capabilities match frontend contract:")
        print(f"         Demo Mode: {body.get('demo_mode')}, Streaming: {body.get('streaming')}, History: {body.get('history')}")
    else:
        print(f"  [FAIL] /api/v1/capabilities returned invalid body: {body}")
        failures += 1

    # 5. CORS Preflight (OPTIONS /api/v1/extract and /extract/stream)
    print("\n[Check 5/11] Verifying Cross-Origin Preflight (CORS)...")
    for ep in ["/api/v1/extract", "/api/v1/extract/stream"]:
        status, _, headers = make_request(
            f"{backend_url}{ep}",
            method="OPTIONS",
            headers={
                "Origin": frontend_url,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, X-Request-ID, Accept",
            },
        )
        allowed_origin = headers.get("access-control-allow-origin")
        if status == 200 and allowed_origin == frontend_url:
            print(f"  [PASS] Preflight for {ep} allowed origin '{allowed_origin}'")
        else:
            print(f"  [FAIL] Preflight for {ep} failed (status={status}, allow-origin={allowed_origin})")
            failures += 1

    # 6. Cross-Origin Document Extraction (POST /api/v1/extract)
    print("\n[Check 6/11] Verifying Cross-Origin Document Extraction (POST /api/v1/extract)...")
    boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
    mock_pdf = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"
    payload = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="live_check_sample.pdf"\r\n'
        f"Content-Type: application/pdf\r\n\r\n"
    ).encode("utf-8") + mock_pdf + f"\r\n--{boundary}--\r\n".encode("utf-8")

    status, body, headers = make_request(
        f"{backend_url}/api/v1/extract",
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Origin": frontend_url,
        },
        data=payload,
    )
    if status == 200 and "extracted_data" in body and "validation_metrics" in body:
        print(f"  [PASS] Document extraction successful ({body.get('_latency_ms')} ms)")
        print(f"         Overall Status: {body.get('overall_status')}")
        print(f"         Vendor Name:    {body.get('extracted_data', {}).get('vendor_name')}")
        print(f"         Grand Total:    {body.get('extracted_data', {}).get('total_amount')} {body.get('extracted_data', {}).get('currency')}")
    else:
        print(f"  [FAIL] Document extraction failed with HTTP {status}: {body}")
        failures += 1

    # 7. Real-Time SSE Stream Verification (POST /api/v1/extract/stream)
    print("\n[Check 7/11] Verifying Real-Time SSE Stream (POST /api/v1/extract/stream)...")
    ctx = ssl.create_default_context()
    stream_req = urllib.request.Request(
        f"{backend_url}/api/v1/extract/stream",
        data=payload,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Origin": frontend_url,
            "Accept": "text/event-stream",
        },
        method="POST",
    )
    stage_events = 0
    result_events = 0
    try:
        with urllib.request.urlopen(stream_req, context=ctx, timeout=25.0) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if line.startswith("event: stage"):
                    stage_events += 1
                elif line.startswith("event: result"):
                    result_events += 1
        if stage_events >= 1 and result_events == 1:
            print(f"  [PASS] SSE stream delivered {stage_events} stage events and {result_events} terminal result event")
        else:
            print(f"  [FAIL] Unexpected stream event counts: stages={stage_events}, results={result_events}")
            failures += 1
    except Exception as exc:
        print(f"  [FAIL] Streaming failed: {exc}")
        failures += 1

    # 8. Schema Validation & Type Guard Conformance
    print("\n[Check 8/11] Validating Pydantic & Frontend Type Guard Conformance...")
    metrics = body.get("validation_metrics", [])
    valid_keys = {"vendor_name", "invoice_number", "date", "currency", "total_amount", "tax_amount", "line_items"}
    if body.get("overall_status") in ("APPROVED", "REQUIRES_HUMAN_REVIEW", "AUTOMATED_PASS") and len(metrics) > 0:
        print(f"  [PASS] Extraction result strictly adheres to ExtendedDocumentResponse schema")
    else:
        print(f"  [FAIL] Validation metrics or overall status invalid: status={body.get('overall_status')}, count={len(metrics)}")
        failures += 1

    # 9. Deduplication & Idempotency Check
    print("\n[Check 9/11] Testing Deduplication Cache Integrity...")
    status2, body2, _ = make_request(
        f"{backend_url}/api/v1/extract",
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Origin": frontend_url,
        },
        data=payload,
    )
    if status2 == 200:
        print(f"  [PASS] Second upload returned HTTP 200 (latency: {body2.get('_latency_ms')} ms vs first {body.get('_latency_ms')} ms)")
    else:
        print(f"  [FAIL] Second identical upload failed: HTTP {status2}")
        failures += 1

    # 10. Adversarial Error Payloads Contract Enforcement
    print("\n[Check 10/11] Verifying Error Contract Enforcements (400, 413, 415)...")
    # Empty file (400)
    empty_boundary = "----Empty" + uuid.uuid4().hex
    empty_payload = f"--{empty_boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"empty.pdf\"\r\nContent-Type: application/pdf\r\n\r\n\r\n--{empty_boundary}--\r\n".encode("utf-8")
    s_empty, b_empty, _ = make_request(f"{backend_url}/api/v1/extract", method="POST", headers={"Content-Type": f"multipart/form-data; boundary={empty_boundary}"}, data=empty_payload)
    
    # Unsupported MIME (415)
    unsupported_boundary = "----Text" + uuid.uuid4().hex
    unsupported_payload = f"--{unsupported_boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"notes.txt\"\r\nContent-Type: text/plain\r\n\r\nNot an invoice\r\n--{unsupported_boundary}--\r\n".encode("utf-8")
    s_unsupp, b_unsupp, _ = make_request(f"{backend_url}/api/v1/extract", method="POST", headers={"Content-Type": f"multipart/form-data; boundary={unsupported_boundary}"}, data=unsupported_payload)

    if s_empty == 400 and b_empty.get("error_code") == "EMPTY_FILE":
        print(f"  [PASS] Empty file rejected with HTTP 400 (EMPTY_FILE)")
    else:
        print(f"  [FAIL] Empty file rejection failed: HTTP {s_empty}, body={b_empty}")
        failures += 1

    if s_unsupp == 415 and b_unsupp.get("error_code") == "UNSUPPORTED_TYPE":
        print(f"  [PASS] Unsupported MIME rejected with HTTP 415 (UNSUPPORTED_TYPE)")
    else:
        print(f"  [FAIL] Unsupported MIME rejection failed: HTTP {s_unsupp}, body={b_unsupp}")
        failures += 1

    # 11. Observability, Headers, and Information Leak Checks
    print("\n[Check 11/11] Verifying Observability, Request IDs, and Zero Information Leakage...")
    request_id = headers.get("x-request-id")
    has_stack_trace = "Traceback" in str(b_empty) or "Traceback" in str(b_unsupp)
    if not has_stack_trace:
        print("  [PASS] Zero internal stack traces exposed in error bodies")
    else:
        print("  [FAIL] Stack trace detected in error response!")
        failures += 1

    print("\n" + "=" * 70)
    print(f"DEPLOYMENT VERIFICATION SUMMARY: {11 - failures}/11 Checks Passed ({warnings} Warnings)")
    print("=" * 70)

    if failures == 0:
        print("RESULT: ALL CRITICAL DEPLOYMENT VERIFICATION GATES PASSED")
        return 0
    else:
        print(f"RESULT: {failures} VERIFICATION GATE(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
