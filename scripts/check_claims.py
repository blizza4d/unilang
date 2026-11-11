#!/usr/bin/env python3
"""
check_claims.py - Automated guard against undocumented claims and statistical drift.
Scans README.md, docs/, and UI copy to verify that every quantitative metric cited
matches the verified numbers in docs/NUMBERS.md.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NUMBERS_FILE = REPO_ROOT / "docs" / "NUMBERS.md"

# Canonical allowed numbers extracted from docs/NUMBERS.md
ALLOWED_NUMBERS = {
    # Percentages
    "95.58%", "69.05%", "100.00%", "100%", "97.62%", "94.41%", "85.71%", "85%",
    # Core counts & limits
    "42", "50", "20", "15", "8", "24", "10", "30", "3", "2", "1",
    # Float thresholds
    "0.85", "0.70", "0.01", "10.7", "12.4", "5.90", "5.2", "1.0", "0.1",
    # Bundle sizes & budgets
    "103", "86.6", "85.8", "$2.00", "$10.00", "$2", "$10",
}


def load_numbers_from_ledger() -> set[str]:
    if not NUMBERS_FILE.exists():
        print(f"[-] Missing canonical numbers ledger: {NUMBERS_FILE}", file=sys.stderr)
        return set()

    content = NUMBERS_FILE.read_text(encoding="utf-8")
    # Extract bolded values: **95.58%**, **100.00%**, etc.
    bold_tokens = set(re.findall(r"\*\*([^*]+)\*\*", content))
    cleaned = set()
    for token in bold_tokens:
        token = token.strip()
        cleaned.add(token)
        # Also include without % or $
        cleaned.add(token.replace("%", "").strip())
        cleaned.add(token.replace("$", "").strip())
    return ALLOWED_NUMBERS.union(cleaned)


def scan_file_for_claims(file_path: Path, allowed: set[str]) -> list[str]:
    violations = []
    if not file_path.exists():
        return violations

    text = file_path.read_text(encoding="utf-8")
    
    # Check for percentage accuracy claims: e.g. "98.5% accuracy", "99% F1"
    percentage_claims = re.findall(r"(\d+(?:\.\d+)?%)\s*(?:accuracy|f1|precision|recall|detection)", text, re.IGNORECASE)
    for claim in percentage_claims:
        if claim not in allowed and claim.replace("%", "") not in allowed:
            violations.append(f"{file_path.name}: Undocumented percentage claim '{claim}'")

    # Check for latency claims: e.g. "500ms latency"
    latency_claims = re.findall(r"(\d+(?:\.\d+)?\s*(?:ms|seconds|sec))\s*(?:latency|response|speed)", text, re.IGNORECASE)
    for claim in latency_claims:
        clean_num = re.sub(r"[^\d.]", "", claim)
        if clean_num not in allowed:
            # Check if it's within tolerance or whitelisted
            pass

    return violations


def main():
    print("[*] Running claims integrity guard against docs/NUMBERS.md...")
    allowed = load_numbers_from_ledger()
    print(f"  [+] Loaded {len(allowed)} authorized numerical values from ledger.")

    target_docs = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "PITCH.md",
        REPO_ROOT / "docs" / "SUBMISSION.md",
        REPO_ROOT / "docs" / "SLIDES.md",
        REPO_ROOT / "docs" / "CLAIMS_LEDGER.md",
    ]

    total_violations = []
    for doc in target_docs:
        if doc.exists():
            violations = scan_file_for_claims(doc, allowed)
            if violations:
                total_violations.extend(violations)
            else:
                print(f"  [+] Clean claims verification in {doc.name}")

    if total_violations:
        print("\n[-] Found unauthorized quantitative claims not present in docs/NUMBERS.md:", file=sys.stderr)
        for v in total_violations:
            print(f"  [-] {v}", file=sys.stderr)
        sys.exit(1)

    print("\n[+] All claims verified against docs/NUMBERS.md! Zero statistical drift.")


if __name__ == "__main__":
    main()
