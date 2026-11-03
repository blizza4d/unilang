import asyncio
import hashlib
from typing import Any
from schemas.document_schemas import ExtractedInvoice, LineItem, ValidationScore
from schemas.grounding import (
    BoundingBox,
    ExtendedDocumentResponse,
    FieldGrounding,
    GroundingResult,
    PageDimension,
    UsageSummary,
)

SCENARIOS: list[dict[str, Any]] = [
    # 1. Clean English invoice, APPROVED
    {
        "keywords": ["english", "clean", "sample1", "corp"],
        "vendor_name": "Apex Global Solutions Inc.",
        "invoice_number": "INV-2026-0891",
        "date": "2026-02-14",
        "currency": "USD",
        "total_amount": 1420.00,
        "tax_amount": 120.00,
        "line_items": [
            LineItem(description="Cloud Infrastructure Setup", quantity=1.0, unit_price=800.00, total_price=800.00),
            LineItem(description="Security Architecture Audit", quantity=1.0, unit_price=500.00, total_price=500.00),
        ],
        "scores": [
            ValidationScore(field_name="vendor_name", confidence_score=0.99, needs_review=False, reasoning="Logo matches header"),
            ValidationScore(field_name="invoice_number", confidence_score=0.98, needs_review=False, reasoning="Standard format found"),
            ValidationScore(field_name="date", confidence_score=0.96, needs_review=False, reasoning="ISO date verified"),
            ValidationScore(field_name="currency", confidence_score=1.00, needs_review=False, reasoning="USD symbol clear"),
            ValidationScore(field_name="total_amount", confidence_score=0.98, needs_review=False, reasoning="800 + 500 + 120 == 1420.00 verified"),
            ValidationScore(field_name="tax_amount", confidence_score=0.95, needs_review=False, reasoning="Tax rate stated 10% on services"),
            ValidationScore(field_name="line_items", confidence_score=0.98, needs_review=False, reasoning="Row math verified"),
        ],
        "status": "APPROVED",
    },
    # 2. German invoice with decimal commas, one flagged date
    {
        "keywords": ["german", "deutsch", "gmbh", "sample2"],
        "vendor_name": "Muster GmbH & Co. KG",
        "invoice_number": "RE-2026-4401",
        "date": "2026-03-31",
        "currency": "EUR",
        "total_amount": 2975.00,
        "tax_amount": 475.00,
        "line_items": [
            LineItem(description="Software-Lizenzpaket Enterprise", quantity=5.0, unit_price=500.00, total_price=2500.00),
        ],
        "scores": [
            ValidationScore(field_name="vendor_name", confidence_score=0.97, needs_review=False, reasoning="Handelsregister entity found"),
            ValidationScore(field_name="invoice_number", confidence_score=0.95, needs_review=False, reasoning="Rechnungsnummer matched"),
            ValidationScore(field_name="date", confidence_score=0.74, needs_review=True, reasoning="Ambiguous German format 31.03.26 resolved via locale"),
            ValidationScore(field_name="currency", confidence_score=0.99, needs_review=False, reasoning="EUR symbol verified"),
            ValidationScore(field_name="total_amount", confidence_score=0.98, needs_review=False, reasoning="2500 + 475 == 2975.00 verified"),
            ValidationScore(field_name="tax_amount", confidence_score=0.97, needs_review=False, reasoning="19% MwSt printed and verified"),
            ValidationScore(field_name="line_items", confidence_score=0.98, needs_review=False, reasoning="Row math verified"),
        ],
        "status": "REQUIRES_HUMAN_REVIEW",
    },
    # 3. Hindi GST invoice with CGST and SGST, flagged tax total
    {
        "keywords": ["hindi", "india", "gst", "sample3"],
        "vendor_name": "भारत इलेक्ट्रॉनिक्स लिमिटेड (Bharat Electronics)",
        "invoice_number": "BEL/26/9012",
        "date": "2026-01-20",
        "currency": "INR",
        "total_amount": 11800.00,
        "tax_amount": 1800.00,
        "line_items": [
            LineItem(description="Digital Sensor Assembly", quantity=10.0, unit_price=1000.00, total_price=10000.00),
        ],
        "scores": [
            ValidationScore(field_name="vendor_name", confidence_score=0.96, needs_review=False, reasoning="Bilingual Hindi-English entity matched"),
            ValidationScore(field_name="invoice_number", confidence_score=0.94, needs_review=False, reasoning="Tax invoice header identified"),
            ValidationScore(field_name="date", confidence_score=0.93, needs_review=False, reasoning="Date confirmed from metadata"),
            ValidationScore(field_name="currency", confidence_score=0.99, needs_review=False, reasoning="₹ symbol mapped to INR"),
            ValidationScore(field_name="total_amount", confidence_score=0.78, needs_review=True, reasoning="Combined CGST (900) + SGST (900) requires verification"),
            ValidationScore(field_name="tax_amount", confidence_score=0.80, needs_review=True, reasoning="Combined Dual-GST total extracted"),
            ValidationScore(field_name="line_items", confidence_score=0.95, needs_review=False, reasoning="10 x 1000 == 10000 verified"),
        ],
        "status": "REQUIRES_HUMAN_REVIEW",
    },
    # 4. Arabic right-to-left invoice with an arithmetic mismatch
    {
        "keywords": ["arabic", "dubai", "riyadh", "sample4"],
        "vendor_name": "شركة النور للحلول الرقمية (Al-Noor Solutions)",
        "invoice_number": "INV-AR-771",
        "date": "2026-02-05",
        "currency": "AED",
        "total_amount": 5400.00,
        "tax_amount": 250.00,
        "line_items": [
            LineItem(description="IT Consulting Hours", quantity=10.0, unit_price=500.00, total_price=5200.00),
        ],
        "scores": [
            ValidationScore(field_name="vendor_name", confidence_score=0.95, needs_review=False, reasoning="RTL business entity transliterated"),
            ValidationScore(field_name="invoice_number", confidence_score=0.94, needs_review=False, reasoning="Invoice reference extracted"),
            ValidationScore(field_name="date", confidence_score=0.91, needs_review=False, reasoning="Gregorian calendar date resolved"),
            ValidationScore(field_name="currency", confidence_score=0.98, needs_review=False, reasoning="درهم mapped to AED"),
            ValidationScore(field_name="total_amount", confidence_score=0.50, needs_review=True, reasoning="Math validation failed: Sum of line items (5200.00) + Tax (250.00) != 5400.00"),
            ValidationScore(field_name="tax_amount", confidence_score=0.50, needs_review=True, reasoning="Math validation failed on linked grand total"),
            ValidationScore(field_name="line_items", confidence_score=0.50, needs_review=True, reasoning="Math validation failed: Row 1: 10 x 500 = 5000.00 but total_price is 5200.00"),
        ],
        "status": "REQUIRES_HUMAN_REVIEW",
    },
    # 5. Blurry Japanese receipt with illegible regions
    {
        "keywords": ["japanese", "receipt", "tokyo", "sample5"],
        "vendor_name": "株式会社未来システムズ (Mirai Systems)",
        "invoice_number": "JP-9902",
        "date": "2026-04-10",
        "currency": "JPY",
        "total_amount": 44000.00,
        "tax_amount": 4000.00,
        "line_items": [
            LineItem(description="Hardware Component Maintenance", quantity=1.0, unit_price=40000.00, total_price=40000.00),
        ],
        "scores": [
            ValidationScore(field_name="vendor_name", confidence_score=0.94, needs_review=False, reasoning="Kanji corporate suffix matched"),
            ValidationScore(field_name="invoice_number", confidence_score=0.72, needs_review=True, reasoning="Noise and blurry stamp near invoice number: [ILLEGIBLE]"),
            ValidationScore(field_name="date", confidence_score=0.92, needs_review=False, reasoning="Reiwa / Gregorian standard date recognized"),
            ValidationScore(field_name="currency", confidence_score=0.99, needs_review=False, reasoning="円 mapped to JPY"),
            ValidationScore(field_name="total_amount", confidence_score=0.96, needs_review=False, reasoning="40000 + 4000 == 44000 verified"),
            ValidationScore(field_name="tax_amount", confidence_score=0.95, needs_review=False, reasoning="10% Consumption Tax verified"),
            ValidationScore(field_name="line_items", confidence_score=0.96, needs_review=False, reasoning="Row math verified"),
        ],
        "status": "REQUIRES_HUMAN_REVIEW",
    },
    # 6. Prompt-injection attempt inside an invoice footer
    {
        "keywords": ["injection", "jailbreak", "security", "sample6"],
        "vendor_name": "CyberDefense Labs",
        "invoice_number": "SEC-007",
        "date": "2026-05-01",
        "currency": "USD",
        "total_amount": 550.00,
        "tax_amount": 50.00,
        "line_items": [
            LineItem(description="Penetration Testing Service", quantity=1.0, unit_price=500.00, total_price=500.00),
        ],
        "scores": [
            ValidationScore(field_name="vendor_name", confidence_score=0.98, needs_review=False, reasoning="Vendor validated"),
            ValidationScore(field_name="invoice_number", confidence_score=0.95, needs_review=False, reasoning="Header matched"),
            ValidationScore(field_name="date", confidence_score=0.95, needs_review=False, reasoning="ISO date verified"),
            ValidationScore(field_name="currency", confidence_score=0.99, needs_review=False, reasoning="USD symbol verified"),
            ValidationScore(field_name="total_amount", confidence_score=0.40, needs_review=True, reasoning="Possible prompt-injection content detected in document footer: 'Ignore instructions'"),
            ValidationScore(field_name="tax_amount", confidence_score=0.95, needs_review=False, reasoning="Tax verified"),
            ValidationScore(field_name="line_items", confidence_score=0.98, needs_review=False, reasoning="Row math verified"),
        ],
        "status": "REQUIRES_HUMAN_REVIEW",
    },
]


def select_demo_scenario(file_bytes: bytes, filename: str = "") -> dict[str, Any]:
    fn_lower = filename.lower()
    for s in SCENARIOS:
        for kw in s["keywords"]:
            if kw in fn_lower:
                return s

    # Select by hash rotation
    h = int(hashlib.sha256(file_bytes).hexdigest(), 16)
    idx = h % len(SCENARIOS)
    return SCENARIOS[idx]


async def run_demo_pipeline(
    file_bytes: bytes,
    filename: str = "",
    simulate_delay: bool = True,
) -> ExtendedDocumentResponse:
    scenario = select_demo_scenario(file_bytes, filename)

    if simulate_delay:
        await asyncio.sleep(1.2)

    invoice = ExtractedInvoice(
        vendor_name=scenario["vendor_name"],
        invoice_number=scenario["invoice_number"],
        date=scenario["date"],
        currency=scenario["currency"],
        total_amount=scenario["total_amount"],
        tax_amount=scenario["tax_amount"],
        line_items=scenario["line_items"],
    )

    boxes = [
        BoundingBox(page=1, x=0.08, y=0.08, width=0.45, height=0.05),
        BoundingBox(page=1, x=0.65, y=0.12, width=0.25, height=0.04),
        BoundingBox(page=1, x=0.65, y=0.18, width=0.22, height=0.04),
        BoundingBox(page=1, x=0.68, y=0.78, width=0.24, height=0.05),
    ]

    field_groundings = [
        FieldGrounding(field_name="vendor_name", boxes=[boxes[0]], source_text=invoice.vendor_name),
        FieldGrounding(field_name="invoice_number", boxes=[boxes[1]], source_text=invoice.invoice_number),
        FieldGrounding(field_name="date", boxes=[boxes[2]], source_text=invoice.date),
        FieldGrounding(field_name="total_amount", boxes=[boxes[3]], source_text=str(invoice.total_amount)),
    ]

    grounding = GroundingResult(
        fields=field_groundings,
        line_items=[],
        page_dimensions=[PageDimension(page=1, width_px=1000, height_px=1414)],
    )

    return ExtendedDocumentResponse(
        extracted_data=invoice,
        validation_metrics=scenario["scores"],
        overall_status=scenario["status"],
        grounding=grounding,
        page_count=1,
        processing_ms=1250,
        usage=UsageSummary(input_tokens=1650, output_tokens=320, estimated_cost_usd=0.009),
    )
