#!/usr/bin/env python3
"""
DataNova Extract Deployment Verification & Smoke Test Tool
Checks:
1. /health endpoint liveness
2. /health/deep endpoint readiness
3. CORS preflight simulation for https://uni-lang.vercel.app and preview domains
4. Response headers and timing
"""

import sys
import argparse
import urllib.request
import urllib.error
import json
import time

def test_endpoint(url: str, method: str = "GET", headers: dict = None) -> tuple[int, dict, dict]:
    headers = headers or {}
    req = urllib.request.Request(url, headers=headers, method=method)
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            latency = (time.time() - start_time) * 1000
            resp_body = response.read().decode("utf-8")
            resp_headers = dict(response.headers)
            try:
                data = json.loads(resp_body)
            except Exception:
                data = {"raw": resp_body}
            data["_latency_ms"] = round(latency, 1)
            return response.status, data, resp_headers
    except urllib.error.HTTPError as e:
        latency = (time.time() - start_time) * 1000
        err_body = e.read().decode("utf-8")
        try:
            data = json.loads(err_body)
        except Exception:
            data = {"error": err_body}
        data["_latency_ms"] = round(latency, 1)
        return e.code, data, dict(e.headers)
    except Exception as e:
        return 0, {"error": str(e)}, {}

def main():
    parser = argparse.ArgumentParser(description="Verify DataNova Extract Backend Deployment")
    parser.add_argument("--url", default="http://localhost:8000", help="Base backend URL")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    print(f"==================================================")
    print(f"DataNova Extract Deployment Check: {base_url}")
    print(f"==================================================")

    # 1. Liveness check
    print("\n[1/3] Testing Liveness (/health)...")
    status, data, _ = test_endpoint(f"{base_url}/health")
    if status == 200:
        print(f"  [PASS] /health returned HTTP 200 ({data.get('_latency_ms')}ms)")
        print(f"         Status: {data.get('status')}, Version: {data.get('version')}")
    else:
        print(f"  [FAIL] /health returned status {status}: {data}")

    # 2. Deep readiness check
    print("\n[2/3] Testing Deep Readiness (/health/deep)...")
    status, data, _ = test_endpoint(f"{base_url}/health/deep")
    if status == 200:
        print(f"  [PASS] /health/deep returned HTTP 200 ({data.get('_latency_ms')}ms)")
        print(f"         Checks: {data.get('checks')}")
    else:
        print(f"  [WARN] /health/deep returned status {status}: {data}")

    # 3. CORS Preflight Simulation
    print("\n[3/3] Simulating CORS Preflight for https://uni-lang.vercel.app...")
    preflight_headers = {
        "Origin": "https://uni-lang.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, X-Request-ID",
    }
    status, _, resp_headers = test_endpoint(
        f"{base_url}/api/v1/extract",
        method="OPTIONS",
        headers=preflight_headers,
    )
    allow_origin = resp_headers.get("access-control-allow-origin") or resp_headers.get("Access-Control-Allow-Origin")
    if allow_origin == "https://uni-lang.vercel.app" or allow_origin == "*":
        print(f"  [PASS] CORS Preflight succeeded! Allow-Origin: {allow_origin}")
    else:
        print(f"  [FAIL] CORS Preflight failed or returned origin: {allow_origin}")
        print(f"         Response headers: {resp_headers}")

    print("\n==================================================")
    print("Verification completed.")
    print("==================================================")

if __name__ == "__main__":
    main()
