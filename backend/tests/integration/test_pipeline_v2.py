import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoints(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_capabilities_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert "streaming" in data
    assert "grounding" in data
    assert "exports" in data
    assert "batch" in data
    assert data["server_version"] == "2.0.0"


@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    resp = await client.get("/health")
    headers = resp.headers
    assert "X-Content-Type-Options" in headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "X-Frame-Options" in headers
    assert "Strict-Transport-Security" in headers


@pytest.mark.asyncio
async def test_export_direct_json(client: AsyncClient):
    invoice_payload = {
        "invoice_number": "INV-TEST-01",
        "date": "2026-03-01",
        "vendor_name": "Test Vendor LLC",
        "total_amount": 110.0,
        "tax_amount": 10.0,
        "currency": "USD",
        "line_items": [
            {
                "description": "Consulting",
                "quantity": 1.0,
                "unit_price": 100.0,
                "total_price": 100.0,
            }
        ],
        "overall_status": "APPROVED",
        "math_verified": True,
        "validation_metrics": [
            {
                "field_name": "total_amount",
                "confidence_score": 0.99,
                "needs_review": False,
                "reasoning": "Valid math",
            }
        ],
    }

    resp = await client.post(
        "/api/v1/export/direct?format=json&filename=test_doc",
        json=invoice_payload,
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")


@pytest.mark.asyncio
async def test_export_direct_xlsx(client: AsyncClient):
    invoice_payload = {
        "invoice_number": "INV-XLSX-01",
        "date": "2026-03-01",
        "vendor_name": "Excel Corp",
        "total_amount": 250.0,
        "tax_amount": 25.0,
        "currency": "EUR",
        "line_items": [
            {
                "description": "License",
                "quantity": 1.0,
                "unit_price": 225.0,
                "total_price": 225.0,
            }
        ],
        "overall_status": "APPROVED",
        "math_verified": True,
        "validation_metrics": [],
    }

    resp = await client.post(
        "/api/v1/export/direct?format=xlsx&filename=test_doc",
        json=invoice_payload,
    )
    assert resp.status_code == 200
    assert "spreadsheet" in resp.headers["content-type"]


@pytest.mark.asyncio
async def test_documents_list_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/documents")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_eval_latest_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/eval/latest")
    assert resp.status_code == 200
    data = resp.json()
    assert "macro_field_f1" in data
    assert "total_test_cases" in data
