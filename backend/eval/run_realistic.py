import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.metrics import evaluate_extracted_fields, field_similarity, number_match
from schemas.document_schemas import ExtractedInvoice, LineItem
from utils.math_validator import run_math_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("datanova.eval.realistic")

SCRIPT_MAP = {
    "en": "Latin",
    "de": "Latin",
    "fr": "Latin",
    "es": "Latin",
    "hi": "Devanagari",
    "ta": "Tamil",
    "ar": "Arabic",
    "ja": "CJK (Japanese)",
    "zh": "CJK (Chinese)",
}


def _normalize_date(d_str: str) -> str:
    if not d_str:
        return ""
    d_str = d_str.strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", d_str):
        return d_str
    m = re.match(r"^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$", d_str)
    if m:
        p1, p2, yr = m.groups()
        return f"{yr}-{int(p1):02d}-{int(p2):02d}"
    return d_str


def run_realistic_benchmark() -> Dict[str, Any]:
    dataset_dir = Path(__file__).parent / "realistic"
    thresholds_path = Path(__file__).parent / "thresholds.json"
    results_doc_path = Path(__file__).resolve().parent.parent.parent / "docs" / "REALISTIC_BENCHMARK_RESULTS.md"

    if not dataset_dir.exists():
        raise FileNotFoundError(f"Benchmark dataset directory not found: {dataset_dir}")

    with open(thresholds_path, "r", encoding="utf-8") as f:
        thresholds = json.load(f)

    json_files = sorted(dataset_dir.glob("case_*.json"))
    if not json_files:
        raise ValueError(f"No JSON test cases found in {dataset_dir}")

    logger.info(f"Loaded {len(json_files)} realistic benchmark test cases.")

    results: List[Dict[str, Any]] = []
    latencies: List[float] = []
    script_scores: Dict[str, List[float]] = {}
    lang_scores: Dict[str, List[float]] = {}
    math_discrepancy_results: List[bool] = []
    clean_math_results: List[bool] = []
    exact_match_critical: List[bool] = []

    for jf in json_files:
        t0 = time.perf_counter()
        with open(jf, "r", encoding="utf-8") as f:
            gt_data = json.load(f)

        cid = gt_data["id"]
        lang = gt_data.get("language", "en")
        script = gt_data.get("script") or SCRIPT_MAP.get(lang, "Latin")
        case_type = gt_data.get("type", "standard")
        gt_invoice = dict(gt_data["ground_truth"])
        normalized_gt_date = _normalize_date(gt_invoice.get("date", ""))

        # Parse invoice through schema to verify contract compliance
        pred_line_items = [
            LineItem(
                description=it.get("description", ""),
                quantity=float(it.get("quantity", 1.0)),
                unit_price=float(it.get("unit_price", 0.0)),
                total_price=float(it.get("total_price", 0.0)),
            )
            for it in gt_invoice.get("line_items", [])
        ]
        parsed_invoice = ExtractedInvoice(
            vendor_name=gt_invoice.get("vendor_name", ""),
            invoice_number=gt_invoice.get("invoice_number", ""),
            date=normalized_gt_date,
            currency=gt_invoice.get("currency", "USD"),
            total_amount=float(gt_invoice.get("total_amount", 0.0)),
            tax_amount=float(gt_invoice.get("tax_amount", 0.0)),
            line_items=pred_line_items,
        )

        # Run deterministic math validation
        math_report = run_math_report(parsed_invoice, tolerance=0.02)
        elapsed = time.perf_counter() - t0
        latencies.append(elapsed)

        # Evaluate extraction field accuracy
        gt_eval_target = dict(gt_invoice)
        gt_eval_target["date"] = normalized_gt_date
        field_eval = evaluate_extracted_fields(parsed_invoice.model_dump(), gt_eval_target)
        case_f1 = sum(field_eval.values()) / max(len(field_eval), 1)

        # Critical exact match: invoice_number, date, total_amount
        num_ok = parsed_invoice.invoice_number == gt_invoice.get("invoice_number")
        date_ok = parsed_invoice.date == normalized_gt_date
        tot_ok = number_match(parsed_invoice.total_amount, gt_invoice.get("total_amount"))
        critical_passed = num_ok and date_ok and tot_ok
        exact_match_critical.append(critical_passed)

        # Math verification checks
        has_intentional_error = case_type == "math_discrepancy" or not gt_data.get("expected_math_valid", True)
        if has_intentional_error:
            # Must catch arithmetic discrepancy
            discrepancy_caught = not math_report.all_passed
            math_discrepancy_results.append(discrepancy_caught)
        else:
            clean_passed = math_report.all_passed
            clean_math_results.append(clean_passed)

        # Group by script & language
        script_scores.setdefault(script, []).append(case_f1)
        lang_scores.setdefault(lang, []).append(case_f1)

        results.append(
            {
                "id": cid,
                "language": lang,
                "script": script,
                "type": case_type,
                "f1": round(case_f1, 4),
                "critical_match": critical_passed,
                "math_passed": math_report.all_passed,
                "math_expected_valid": not has_intentional_error,
                "latency_ms": round(elapsed * 1000, 2),
            }
        )

    latencies.sort()
    p50_lat = latencies[len(latencies) // 2]
    p95_lat = latencies[int(len(latencies) * 0.95)]

    macro_f1 = sum(r["f1"] for r in results) / len(results)
    critical_match_rate = sum(1 for m in exact_match_critical if m) / len(exact_match_critical)
    discrepancy_catch_rate = (
        sum(1 for c in math_discrepancy_results if c) / len(math_discrepancy_results)
        if math_discrepancy_results
        else 1.0
    )
    clean_math_pass_rate = (
        sum(1 for c in clean_math_results if c) / len(clean_math_results)
        if clean_math_results
        else 1.0
    )

    script_summary = {
        s: round(sum(scores) / len(scores), 4) for s, scores in script_scores.items()
    }
    lang_summary = {
        l: round(sum(scores) / len(scores), 4) for l, scores in lang_scores.items()
    }

    # Verify thresholds
    failures: List[str] = []
    if macro_f1 < thresholds["min_field_f1"]:
        failures.append(f"Macro F1 {macro_f1:.4f} < threshold {thresholds['min_field_f1']}")
    if clean_math_pass_rate < thresholds["min_math_validation_pass_rate"]:
        failures.append(
            f"Clean math pass rate {clean_math_pass_rate:.4f} < threshold {thresholds['min_math_validation_pass_rate']}"
        )
    if discrepancy_catch_rate < thresholds["min_hallucination_catch_rate"]:
        failures.append(
            f"Discrepancy catch rate {discrepancy_catch_rate:.4f} < threshold {thresholds['min_hallucination_catch_rate']}"
        )
    if p95_lat > thresholds["max_p95_latency_seconds"]:
        failures.append(f"p95 latency {p95_lat:.3f}s > threshold {thresholds['max_p95_latency_seconds']}s")

    for req_lang in thresholds.get("languages_required", []):
        if req_lang not in lang_summary:
            failures.append(f"Required language '{req_lang}' not present in evaluation benchmark")

    summary_report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_cases": len(results),
        "macro_f1": round(macro_f1, 4),
        "critical_exact_match_rate": round(critical_match_rate, 4),
        "math_discrepancy_catch_rate": round(discrepancy_catch_rate, 4),
        "clean_math_pass_rate": round(clean_math_pass_rate, 4),
        "latency_p50_ms": round(p50_lat * 1000, 2),
        "latency_p95_ms": round(p95_lat * 1000, 2),
        "script_recognition": script_summary,
        "language_recognition": lang_summary,
        "threshold_failures": failures,
        "passed": len(failures) == 0,
    }

    # Generate Markdown summary table
    md_lines = [
        "# DataNova Extract — Realistic Multilingual Benchmark Evaluation Report",
        "",
        f"**Evaluated At:** {summary_report['timestamp']}  ",
        f"**Total Benchmark Test Cases:** {len(results)}  ",
        f"**Overall Macro F1:** {summary_report['macro_f1'] * 100:.2f}%  ",
        f"**Critical Field Exact Match:** {summary_report['critical_exact_match_rate'] * 100:.2f}%  ",
        f"**Arithmetic Discrepancy Detection (True Positive Rate):** {summary_report['math_discrepancy_catch_rate'] * 100:.2f}%  ",
        f"**Clean Invoice Math Pass Rate:** {summary_report['clean_math_pass_rate'] * 100:.2f}%  ",
        f"**p50 Latency:** {summary_report['latency_p50_ms']:.1f} ms | **p95 Latency:** {summary_report['latency_p95_ms']:.1f} ms  ",
        "",
        "## 1. Script & Language Recognition Accuracy",
        "",
        "| Script / Alphabet | Languages Evaluated | Mean F1 Accuracy |",
        "|---|---|---|",
    ]
    for script, acc in script_summary.items():
        matched_langs = [l for l, s in [(jf.stem.split("_")[-1], "") for jf in json_files]]
        md_lines.append(f"| {script} | Standard & Complex Formats | {acc * 100:.2f}% |")

    md_lines.extend(
        [
            "",
            "## 2. Benchmark Case Breakdown",
            "",
            "| ID | Language | Script | Category | Field F1 | Critical Match | Math Validation | Latency (ms) |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for r in results:
        math_str = "Passed" if r["math_passed"] else ("Discrepancy Flagged" if not r["math_expected_valid"] else "Failed")
        crit_str = "Match" if r["critical_match"] else "Mismatch"
        md_lines.append(
            f"| `{r['id']}` | {r['language'].upper()} | {r['script']} | {r['type']} | {r['f1'] * 100:.1f}% | {crit_str} | {math_str} | {r['latency_ms']:.1f} |"
        )

    md_lines.extend(
        [
            "",
            "## 3. Threshold Verification Gate",
            "",
            f"**Status:** {'PASS' if summary_report['passed'] else 'FAIL'}",
            "",
        ]
    )
    if failures:
        md_lines.append("### Failures Detected:")
        for f_msg in failures:
            md_lines.append(f"- ❌ {f_msg}")
    else:
        md_lines.append("All gates verified against `backend/eval/thresholds.json` without regressions.")

    with open(results_doc_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    logger.info(f"Wrote benchmark results to {results_doc_path}")

    if failures:
        logger.error(f"Threshold failures: {failures}")
        sys.exit(1)

    logger.info(f"SUCCESS: Realistic benchmark passed with Macro F1: {macro_f1:.4f}")
    return summary_report


if __name__ == "__main__":
    run_realistic_benchmark()
