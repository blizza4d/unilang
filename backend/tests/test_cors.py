import pytest
from fastapi.testclient import TestClient
from main import app
from config import get_settings


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_cors_preflight_production_domain(client):
    headers = {
        "Origin": "https://uni-lang.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, X-Request-ID",
    }
    response = client.options("/api/v1/extract", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://uni-lang.vercel.app"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_preflight_vercel_preview_regex(client):
    headers = {
        "Origin": "https://unilang-git-preview-blizza4d.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = client.options("/api/v1/extract", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://unilang-git-preview-blizza4d.vercel.app"


def test_cors_disallows_untrusted_origin(client):
    headers = {
        "Origin": "https://evil-phishing-site.com",
        "Access-Control-Request-Method": "POST",
    }
    response = client.options("/api/v1/extract", headers=headers)
    # Untrusted origin should NOT receive access-control-allow-origin
    assert response.headers.get("access-control-allow-origin") != "https://evil-phishing-site.com"


def test_vercel_origin_explicitly_in_allowed_origins():
    """Catches Mutation 1: Verifies https://uni-lang.vercel.app is explicitly in ALLOWED_ORIGINS."""
    settings = get_settings()
    assert "https://uni-lang.vercel.app" in settings.ALLOWED_ORIGINS, (
        "Production frontend domain https://uni-lang.vercel.app MUST be explicitly listed in ALLOWED_ORIGINS"
    )
