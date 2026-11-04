import pytest
from config import Settings, get_settings


def test_settings_default_cors():
    settings = Settings()
    assert "https://uni-lang.vercel.app" in settings.ALLOWED_ORIGINS
    assert "http://localhost:3000" in settings.ALLOWED_ORIGINS
    assert settings.ALLOWED_ORIGIN_REGEX == r"^https:\/\/.*\.vercel\.app$"


def test_settings_unconfigured_keys_auto_demo_fallback(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    monkeypatch.setenv("FEATURE_DEMO_MODE", "false")
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    # In development/staging, lacking keys automatically enables demo mode rather than crashing
    s = Settings(
        OPENAI_API_KEY="",
        GOOGLE_API_KEY="",
        FEATURE_DEMO_MODE=False,
        ENVIRONMENT="development",
    )
    assert s.FEATURE_DEMO_MODE is True
    get_settings.cache_clear()


def test_settings_production_requires_postgres(monkeypatch):
    with pytest.raises(ValueError, match="Production environment cannot use SQLite"):
        Settings(
            ENVIRONMENT="production",
            DATABASE_URL="sqlite+aiosqlite:///./datanova.db",
            API_KEY="prod-secret-key-12345",
            STORAGE_BACKEND="s3",
            S3_ENDPOINT_URL="https://s3.amazonaws.com",
            S3_ACCESS_KEY="mock",
            S3_SECRET_KEY="mock",
        )
