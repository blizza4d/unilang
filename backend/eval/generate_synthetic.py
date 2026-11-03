import json
from pathlib import Path
from typing import Any, Dict, List

SYNTHETIC_BENCHMARK_CASES: List[Dict[str, Any]] = [
    {
        "id": "syn-en-001",
        "filename": "english_clean_sample1.pdf",
        "language": "en",
        "description": "Standard US Enterprise Tech Invoice with 2 line items",
        "document_type": "invoice",
        "ground_truth": {
            "invoice_number": "INV-2026-0891",
            "date": "2026-02-14",
            "vendor_name": "Apex Global Solutions Inc.",
            "total_amount": 1420.00,
            "tax_amount": 120.00,
            "currency": "USD",
            "line_items": [
                {
                    "description": "Cloud Infrastructure Setup",
                    "quantity": 1.0,
                    "unit_price": 800.00,
                    "total_price": 800.00,
                },
                {
                    "description": "Security Architecture Audit",
                    "quantity": 1.0,
                    "unit_price": 500.00,
                    "total_price": 500.00,
                },
            ],
        },
    },
    {
        "id": "syn-de-002",
        "filename": "german_deutsch_gmbh_sample2.pdf",
        "language": "de",
        "description": "German B2B Rechnung with 19% MwSt and European comma decimals",
        "document_type": "invoice",
        "ground_truth": {
            "invoice_number": "RE-2026-4401",
            "date": "2026-03-31",
            "vendor_name": "Muster GmbH & Co. KG",
            "total_amount": 2975.00,
            "tax_amount": 475.00,
            "currency": "EUR",
            "line_items": [
                {
                    "description": "Software-Lizenzpaket Enterprise",
                    "quantity": 5.0,
                    "unit_price": 500.00,
                    "total_price": 2500.00,
                }
            ],
        },
    },
    {
        "id": "syn-hi-003",
        "filename": "hindi_india_gst_sample3.pdf",
        "language": "hi",
        "description": "Indian GST Tax Invoice in Hindi / English bilingual",
        "document_type": "invoice",
        "ground_truth": {
            "invoice_number": "BEL/26/9012",
            "date": "2026-01-20",
            "vendor_name": "भारत इलेक्ट्रॉनिक्स लिमिटेड (Bharat Electronics)",
            "total_amount": 11800.00,
            "tax_amount": 1800.00,
            "currency": "INR",
            "line_items": [
                {
                    "description": "Digital Sensor Assembly",
                    "quantity": 10.0,
                    "unit_price": 1000.00,
                    "total_price": 10000.00,
                }
            ],
        },
    },
    {
        "id": "syn-ar-004",
        "filename": "arabic_dubai_sample4.pdf",
        "language": "ar",
        "description": "Arabic Middle East VAT Tax Invoice",
        "document_type": "invoice",
        "ground_truth": {
            "invoice_number": "INV-AR-771",
            "date": "2026-02-05",
            "vendor_name": "شركة النور للحلول الرقمية (Al-Noor Solutions)",
            "total_amount": 5400.00,
            "tax_amount": 250.00,
            "currency": "AED",
            "line_items": [
                {
                    "description": "IT Consulting Hours",
                    "quantity": 10.0,
                    "unit_price": 500.00,
                    "total_price": 5200.00,
                }
            ],
        },
    },
    {
        "id": "syn-ja-005",
        "filename": "japanese_tokyo_sample5.pdf",
        "language": "ja",
        "description": "Japanese Qualified Invoice with 10% consumption tax",
        "document_type": "invoice",
        "ground_truth": {
            "invoice_number": "JP-9902",
            "date": "2026-04-10",
            "vendor_name": "株式会社未来システムズ (Mirai Systems)",
            "total_amount": 44000.00,
            "tax_amount": 4000.00,
            "currency": "JPY",
            "line_items": [
                {
                    "description": "Hardware Component Maintenance",
                    "quantity": 1.0,
                    "unit_price": 40000.00,
                    "total_price": 40000.00,
                }
            ],
        },
    },
    {
        "id": "syn-inj-006",
        "filename": "injection_attack_sample6.pdf",
        "language": "en",
        "description": "Adversarial Prompt Injection Invoice with hidden system prompt instructions",
        "document_type": "invoice",
        "ground_truth": {
            "invoice_number": "SEC-007",
            "date": "2026-05-01",
            "vendor_name": "CyberDefense Labs",
            "total_amount": 550.00,
            "tax_amount": 50.00,
            "currency": "USD",
            "line_items": [
                {
                    "description": "Penetration Testing Service",
                    "quantity": 1.0,
                    "unit_price": 500.00,
                    "total_price": 500.00,
                }
            ],
        },
    },
]


def write_synthetic_dataset(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(SYNTHETIC_BENCHMARK_CASES, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    p = Path(__file__).parent / "synthetic_dataset.json"
    write_synthetic_dataset(p)
    print(f"Generated {len(SYNTHETIC_BENCHMARK_CASES)} benchmark cases in {p}")
