import pytest
from schemas.document_schemas import ExtractedInvoice, LineItem, ValidationScore
from utils.math_validator import (
    apply_math_overrides,
    check_grand_total,
    check_line_item,
    run_math_report,
)


def test_passing_invoice():
    invoice = ExtractedInvoice(
        vendor_name="Acme Corp",
        invoice_number="INV-001",
        date="2026-03-15",
        currency="USD",
        total_amount=115.00,
        tax_amount=15.00,
        line_items=[
            LineItem(description="Widget A", quantity=2.0, unit_price=25.00, total_price=50.00),
            LineItem(description="Widget B", quantity=5.0, unit_price=10.00, total_price=50.00),
        ],
    )
    report = run_math_report(invoice, tolerance=0.01)
    assert report.all_passed is True
    assert len(report.failing_fields) == 0
    assert report.total_check.passed is True


def test_failing_line_item():
    item = LineItem(description="Defective Math Item", quantity=3.0, unit_price=10.00, total_price=35.00)
    check = check_line_item(item, tolerance=0.01, index=0)
    assert check.passed is False
    assert "35.00" in check.reasoning

    invoice = ExtractedInvoice(
        vendor_name="Acme Corp",
        invoice_number="INV-002",
        date="2026-03-15",
        currency="USD",
        total_amount=40.00,
        tax_amount=5.00,
        line_items=[item],
    )
    report = run_math_report(invoice, tolerance=0.01)
    assert report.all_passed is False
    assert "line_items" in report.failing_fields


def test_failing_grand_total():
    invoice = ExtractedInvoice(
        vendor_name="Acme Corp",
        invoice_number="INV-003",
        date="2026-03-15",
        currency="USD",
        total_amount=200.00,
        tax_amount=10.00,
        line_items=[
            LineItem(description="Item 1", quantity=1.0, unit_price=100.00, total_price=100.00)
        ],
    )
    report = run_math_report(invoice, tolerance=0.01)
    assert report.all_passed is False
    assert "total_amount" in report.failing_fields
    assert "tax_amount" in report.failing_fields
    assert "line_items" in report.failing_fields


def test_empty_line_items_skipped():
    invoice = ExtractedInvoice(
        vendor_name="Acme Corp",
        invoice_number="INV-004",
        date="2026-03-15",
        currency="USD",
        total_amount=50.00,
        tax_amount=0.00,
        line_items=[],
    )
    report = run_math_report(invoice, tolerance=0.01)
    assert report.total_check.skipped is True
    assert report.all_passed is True


def test_float_drift_handling():
    invoice = ExtractedInvoice(
        vendor_name="Float Lab",
        invoice_number="INV-DRIFT",
        date="2026-03-15",
        currency="USD",
        total_amount=0.30,
        tax_amount=0.20,
        line_items=[
            LineItem(description="Item X", quantity=1.0, unit_price=0.10, total_price=0.10)
        ],
    )
    report = run_math_report(invoice, tolerance=0.01)
    assert report.all_passed is True


def test_apply_math_overrides_forces_review_and_caps_confidence():
    invoice = ExtractedInvoice(
        vendor_name="Bad Math Inc",
        invoice_number="INV-BAD",
        date="2026-03-15",
        currency="USD",
        total_amount=999.00,
        tax_amount=10.00,
        line_items=[
            LineItem(description="Bad Calc", quantity=2.0, unit_price=10.00, total_price=25.00)
        ],
    )
    report = run_math_report(invoice, tolerance=0.01)
    assert not report.all_passed

    initial_scores = [
        ValidationScore(field_name="vendor_name", confidence_score=0.95, needs_review=False, reasoning="Verified"),
        ValidationScore(field_name="line_items", confidence_score=0.98, needs_review=False, reasoning="Looks great"),
        ValidationScore(field_name="total_amount", confidence_score=0.92, needs_review=False, reasoning="Total printed"),
    ]

    overridden = apply_math_overrides(initial_scores, report, threshold=0.85)
    score_map = {s.field_name: s for s in overridden}

    assert score_map["vendor_name"].needs_review is False
    assert score_map["vendor_name"].confidence_score == 0.95

    assert score_map["line_items"].needs_review is True
    assert score_map["line_items"].confidence_score <= 0.5
    assert "Math validation failed" in score_map["line_items"].reasoning

    assert score_map["total_amount"].needs_review is True
    assert score_map["total_amount"].confidence_score <= 0.5


def test_threshold_exact_boundary_comparison():
    """Catches Mutation 3: Verifies strict `<` threshold comparison (score == threshold does NOT trigger review)."""
    invoice = ExtractedInvoice(
        vendor_name="Boundary Inc",
        invoice_number="INV-BOUND",
        date="2026-03-15",
        currency="USD",
        total_amount=100.00,
        tax_amount=0.00,
        line_items=[
            LineItem(description="Item", quantity=1.0, unit_price=100.00, total_price=100.00)
        ],
    )
    report = run_math_report(invoice, tolerance=0.01)
    assert report.all_passed

    initial_scores = [
        ValidationScore(field_name="vendor_name", confidence_score=0.85, needs_review=False, reasoning="Exact threshold score"),
    ]
    overridden = apply_math_overrides(initial_scores, report, threshold=0.85)
    assert overridden[0].needs_review is False, "Score equal to threshold must NOT trigger review (strict `<` required)"
