from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from schemas.document_schemas import ExtractedInvoice, LineItem, ValidationScore


@dataclass
class LineItemCheck:
    item_index: int
    description: str
    passed: bool
    expected_total: Decimal
    actual_total: Decimal
    difference: Decimal
    reasoning: str


@dataclass
class TotalCheck:
    passed: bool
    skipped: bool
    computed_total: Decimal
    reported_total: Decimal
    tax_amount: Decimal
    line_items_sum: Decimal
    difference: Decimal
    reasoning: str


@dataclass
class MathReport:
    line_checks: list[LineItemCheck]
    total_check: TotalCheck
    all_passed: bool
    failing_fields: set[str]

    def to_prompt_text(self) -> str:
        lines: list[str] = ["### DETERMINISTIC MATH REPORT (GROUND TRUTH)"]
        if self.line_checks:
            lines.append("Line Item Validations:")
            for lc in self.line_checks:
                status = "PASSED" if lc.passed else "FAILED"
                lines.append(f"  - Row {lc.item_index + 1} ({lc.description}): [{status}] {lc.reasoning}")
        else:
            lines.append("Line Item Validations: No line items present.")

        total_status = "SKIPPED" if self.total_check.skipped else ("PASSED" if self.total_check.passed else "FAILED")
        lines.append(f"Grand Total Validation: [{total_status}] {self.total_check.reasoning}")

        overall = "ALL PASSED" if self.all_passed else "FAILURES DETECTED"
        lines.append(f"Summary: {overall}. Failing fields: {sorted(list(self.failing_fields)) or 'None'}")
        return "\n".join(lines)


def _to_decimal(val: float | int | str) -> Decimal:
    try:
        return Decimal(str(val))
    except Exception:
        return Decimal("0.0")


def _format_decimal(d: Decimal) -> str:
    return f"{d:.2f}"


def check_line_item(item: LineItem, tolerance: float, index: int = 0) -> LineItemCheck:
    qty = _to_decimal(item.quantity)
    unit_price = _to_decimal(item.unit_price)
    actual_total = _to_decimal(item.total_price)
    expected_total = (qty * unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    diff = abs(expected_total - actual_total)
    tol = _to_decimal(tolerance)

    passed = diff <= tol
    desc = item.description or f"Item {index + 1}"
    qty_str = f"{qty:g}"
    if passed:
        reasoning = f"Quantity {qty_str} * Unit Price {_format_decimal(unit_price)} == Total {_format_decimal(actual_total)}"
    else:
        reasoning = (
            f"Row {index + 1} ({desc}): {qty_str} x {_format_decimal(unit_price)} = {_format_decimal(expected_total)} "
            f"but total_price is {_format_decimal(actual_total)} (diff: {_format_decimal(diff)})"
        )

    return LineItemCheck(
        item_index=index,
        description=desc,
        passed=passed,
        expected_total=expected_total,
        actual_total=actual_total,
        difference=diff,
        reasoning=reasoning,
    )


def check_grand_total(invoice: ExtractedInvoice, tolerance: float) -> TotalCheck:
    if not invoice.line_items:
        return TotalCheck(
            passed=True,
            skipped=True,
            computed_total=Decimal("0.0"),
            reported_total=_to_decimal(invoice.total_amount),
            tax_amount=_to_decimal(invoice.tax_amount),
            line_items_sum=Decimal("0.0"),
            difference=Decimal("0.0"),
            reasoning="No line items to verify.",
        )

    items_sum = sum((_to_decimal(item.total_price) for item in invoice.line_items), Decimal("0.0"))
    tax = _to_decimal(invoice.tax_amount)
    reported_total = _to_decimal(invoice.total_amount)
    computed_total = items_sum + tax
    diff = abs(computed_total - reported_total)
    tol = _to_decimal(tolerance)

    passed = diff <= tol
    if passed:
        reasoning = (
            f"Sum of line items ({_format_decimal(items_sum)}) + Tax ({_format_decimal(tax)}) == "
            f"Total Amount ({_format_decimal(reported_total)})"
        )
    else:
        reasoning = (
            f"Sum of line items ({_format_decimal(items_sum)}) + Tax ({_format_decimal(tax)}) = {_format_decimal(computed_total)}, "
            f"which does not match total_amount ({_format_decimal(reported_total)}, diff: {_format_decimal(diff)})"
        )

    return TotalCheck(
        passed=passed,
        skipped=False,
        computed_total=computed_total,
        reported_total=reported_total,
        tax_amount=tax,
        line_items_sum=items_sum,
        difference=diff,
        reasoning=reasoning,
    )


def run_math_report(invoice: ExtractedInvoice, tolerance: float) -> MathReport:
    line_checks: list[LineItemCheck] = []
    failing_fields: set[str] = set()

    for idx, item in enumerate(invoice.line_items):
        chk = check_line_item(item, tolerance, idx)
        line_checks.append(chk)
        if not chk.passed:
            failing_fields.add("line_items")

    total_chk = check_grand_total(invoice, tolerance)
    if not total_chk.skipped and not total_chk.passed:
        failing_fields.add("total_amount")
        failing_fields.add("tax_amount")
        failing_fields.add("line_items")

    all_passed = (len(failing_fields) == 0)

    return MathReport(
        line_checks=line_checks,
        total_check=total_chk,
        all_passed=all_passed,
        failing_fields=failing_fields,
    )


def apply_math_overrides(
    metrics: list[ValidationScore],
    report: MathReport,
    threshold: float = 0.85,
) -> list[ValidationScore]:
    """Guarantees deterministic mathematical truth overrides LLM scores."""
    updated: list[ValidationScore] = []
    line_item_fails = [c.reasoning for c in report.line_checks if not c.passed]

    for score in metrics:
        if score.field_name in report.failing_fields:
            if score.field_name == "line_items":
                override_text = "Math validation failed: " + "; ".join(line_item_fails)
            elif score.field_name in ("total_amount", "tax_amount"):
                override_text = f"Math validation failed: {report.total_check.reasoning}"
            else:
                override_text = "Math validation check failed on linked financial fields."

            combined_reasoning = f"{override_text} | LLM Note: {score.reasoning}".strip(" |")
            new_score = min(score.confidence_score, 0.5)

            updated.append(
                ValidationScore(
                    field_name=score.field_name,
                    confidence_score=new_score,
                    needs_review=True,
                    reasoning=combined_reasoning,
                )
            )
        else:
            updated.append(
                ValidationScore(
                    field_name=score.field_name,
                    confidence_score=score.confidence_score,
                    needs_review=(score.confidence_score < threshold),
                    reasoning=score.reasoning,
                )
            )
    return updated
