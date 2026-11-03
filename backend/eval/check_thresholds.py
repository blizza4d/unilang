import json
import sys
from pathlib import Path


def check_thresholds() -> None:
    eval_dir = Path(__file__).parent
    report_file = eval_dir / "eval_report.json"
    thresholds_file = eval_dir / "thresholds.json"

    if not report_file.exists():
        print(f"ERROR: {report_file} does not exist. Run eval/run_eval.py first.")
        sys.exit(1)

    with open(report_file, "r", encoding="utf-8") as f:
        report = json.load(f)

    with open(thresholds_file, "r", encoding="utf-8") as f:
        thresholds = json.load(f)

    failures = []

    # Check macro F1
    if report.get("macro_field_f1", 0) < thresholds["min_field_f1"]:
        failures.append(
            f"Macro Field F1 {report.get('macro_field_f1')} < required {thresholds['min_field_f1']}"
        )

    # Check line item F1
    if report.get("line_item_f1", 0) < thresholds["min_line_item_f1"]:
        failures.append(
            f"Line Item F1 {report.get('line_item_f1')} < required {thresholds['min_line_item_f1']}"
        )

    # Check math verification
    if report.get("math_verification_pass_rate", 0) < thresholds["min_math_validation_pass_rate"]:
        failures.append(
            f"Math pass rate {report.get('math_verification_pass_rate')} < required {thresholds['min_math_validation_pass_rate']}"
        )

    # Check latency
    if report.get("p95_latency_seconds", 999) > thresholds["max_p95_latency_seconds"]:
        failures.append(
            f"P95 latency {report.get('p95_latency_seconds')}s > max allowable {thresholds['max_p95_latency_seconds']}s"
        )

    # Check languages present
    lang_breakdown = report.get("language_breakdown", {})
    for lang in thresholds.get("languages_required", []):
        if lang not in lang_breakdown:
            failures.append(f"Required benchmark language '{lang}' missing from evaluation")

    if failures:
        print("[FAIL] EVALUATION THRESHOLD GATE FAILED:")
        for fail in failures:
            print(f"  - {fail}")
        sys.exit(1)

    print("[SUCCESS] ALL EVALUATION THRESHOLDS PASSED:")
    print(f"  - Macro F1: {report.get('macro_field_f1')} (min {thresholds['min_field_f1']})")
    print(f"  - Line Item F1: {report.get('line_item_f1')} (min {thresholds['min_line_item_f1']})")
    print(f"  - Math Pass Rate: {report.get('math_verification_pass_rate')} (min {thresholds['min_math_validation_pass_rate']})")
    print(f"  - P95 Latency: {report.get('p95_latency_seconds')}s (max {thresholds['max_p95_latency_seconds']}s)")
    sys.exit(0)


if __name__ == "__main__":
    check_thresholds()
