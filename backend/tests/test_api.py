import os
import pytest
from fastapi.testclient import TestClient

os.environ["DATANOVA_SKIP_KEY_VALIDATION"] = "true"
os.environ["OPENAI_API_KEY"] = "mock-key-for-test"
os.environ["GOOGLE_API_KEY"] = "mock-key-for-test"

from main import app
from schemas.document_schemas import ExtractedInvoice, FinalDocumentResponse, LineItem, ValidationScore


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] in ("1.0.0", "2.0.0")


def test_empty_file_upload(client):
    response = client.post(
        "/api/v1/extract",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "EMPTY_FILE"


def test_unsupported_file_type(client):
    response = client.post(
        "/api/v1/extract",
        files={"file": ("test.txt", b"Hello, world! Not an invoice.", "text/plain")},
    )
    assert response.status_code == 415
    data = response.json()
    assert data["error_code"] == "UNSUPPORTED_TYPE"


def test_oversized_file_upload(client):
    oversized_bytes = b"%PDF-" + b"0" * (16 * 1024 * 1024)
    response = client.post(
        "/api/v1/extract",
        files={"file": ("large.pdf", oversized_bytes, "application/pdf")},
    )
    assert response.status_code == 413
    data = response.json()
    assert data["error_code"] == "FILE_TOO_LARGE"


def test_extract_happy_path_mocked(client, monkeypatch):
    from config import get_settings
    settings = get_settings()
    monkeypatch.setattr(settings, "FEATURE_DEMO_MODE", False)

    mock_response = FinalDocumentResponse(
        extracted_data=ExtractedInvoice(
            vendor_name="Test Enterprise",
            invoice_number="INV-9999",
            date="2026-01-01",
            currency="EUR",
            total_amount=100.0,
            tax_amount=0.0,
            line_items=[
                LineItem(description="Service", quantity=1.0, unit_price=100.0, total_price=100.0)
            ],
        ),
        validation_metrics=[
            ValidationScore(field_name="vendor_name", confidence_score=0.98, needs_review=False, reasoning="Clear logo"),
            ValidationScore(field_name="invoice_number", confidence_score=0.95, needs_review=False, reasoning="Found header"),
            ValidationScore(field_name="date", confidence_score=0.92, needs_review=False, reasoning="ISO date matched"),
            ValidationScore(field_name="currency", confidence_score=0.99, needs_review=False, reasoning="EUR symbol recognized"),
            ValidationScore(field_name="total_amount", confidence_score=0.94, needs_review=False, reasoning="Math verified"),
            ValidationScore(field_name="tax_amount", confidence_score=0.90, needs_review=False, reasoning="Zero tax printed"),
            ValidationScore(field_name="line_items", confidence_score=0.95, needs_review=False, reasoning="Row math verified"),
        ],
        overall_status="APPROVED",
    )

    async def mock_aprocess_document(file_bytes: bytes) -> FinalDocumentResponse:
        return mock_response

    monkeypatch.setattr("main.aprocess_document", mock_aprocess_document)

    response = client.post(
        "/api/v1/extract",
        files={"file": ("invoice.pdf", b"%PDF-mock-bytes", "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["extracted_data"]["vendor_name"] == "Test Enterprise"
    assert data["overall_status"] == "APPROVED"
