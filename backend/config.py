import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Keys for Model Providers
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # LLM Providers & Models
    LLM_PROVIDER_VISION: Literal["openai", "google"] = "google"
    LLM_PROVIDER_EXTRACTOR: Literal["openai", "google"] = "openai"
    LLM_PROVIDER_JUDGE: Literal["openai", "google"] = "openai"

    VISION_MODEL: str = "gemini-2.5-flash"
    EXTRACTOR_MODEL: str = "gpt-4o"
    JUDGE_MODEL: str = "gpt-4o"

    # Ingestion Constraints
    MAX_UPLOAD_MB: int = 15
    MAX_PDF_PAGES: int = 8
    PDF_RENDER_DPI: int = 200

    # LLM Execution Controls
    LLM_TIMEOUT_SECONDS: int = 90
    LLM_MAX_RETRIES: int = 2

    # Validation Thresholds
    REVIEW_THRESHOLD: float = 0.85
    MATH_TOLERANCE: float = 0.01

    # Network & Logging
    ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True

    # Feature Flags & Extensions
    FEATURE_STREAMING: bool = True
    FEATURE_GROUNDING: bool = True
    FEATURE_PERSISTENCE: bool = True
    FEATURE_HISTORY: bool = True
    FEATURE_BATCH: bool = True
    FEATURE_EXPORTS: bool = True
    FEATURE_EVAL: bool = True
    FEATURE_RATE_LIMIT: bool = True
    FEATURE_DEMO_MODE: bool = False

    DATABASE_URL: str = "sqlite+aiosqlite:///./datanova.db"
    BATCH_MAX_FILES: int = 20
    MAX_BATCH_FILES: int = 20
    BATCH_CONCURRENCY: int = 3
    RATE_LIMIT_PER_MINUTE: int = 30
    RATE_LIMIT_BURST: int = 10
    MAX_HISTORY_ITEMS: int = 200
    COST_TRACKING: bool = True
    PRICE_TABLE_JSON: str = '{"gpt-4o": {"input": 2.50, "output": 10.00}, "gemini-2.5-flash": {"input": 0.15, "output": 0.60}}'
    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    SECURITY_HEADERS: bool = True
    TRUSTED_HOSTS: list[str] = Field(default_factory=lambda: ["*"])
    API_KEY: str = ""


    @field_validator("ALLOWED_ORIGINS", "CORS_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        return ["http://localhost:3000"]

    @field_validator("TRUSTED_HOSTS", mode="before")
    @classmethod
    def parse_trusted_hosts(cls, value: object) -> list[str]:
        if isinstance(value, str):
            return [h.strip() for h in value.split(",") if h.strip()]
        if isinstance(value, list):
            return [str(h).strip() for h in value if str(h).strip()]
        return ["*"]

    @model_validator(mode="after")
    def validate_provider_keys(self) -> "Settings":
        if (
            self.FEATURE_DEMO_MODE
            or "pytest" in sys.modules
            or os.getenv("PYTEST_CURRENT_TEST")
            or os.getenv("DATANOVA_SKIP_KEY_VALIDATION", "false").lower() == "true"
        ):
            return self

        provider_map = {
            "vision": self.LLM_PROVIDER_VISION,
            "extractor": self.LLM_PROVIDER_EXTRACTOR,
            "judge": self.LLM_PROVIDER_JUDGE,
        }

        for role, provider in provider_map.items():
            if provider == "openai" and not self.OPENAI_API_KEY:
                raise ValueError(
                    f"Provider '{provider}' configured for role '{role}', but OPENAI_API_KEY is not set."
                )
            if provider == "google" and not self.GOOGLE_API_KEY:
                raise ValueError(
                    f"Provider '{provider}' configured for role '{role}', but GOOGLE_API_KEY is not set."
                )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
