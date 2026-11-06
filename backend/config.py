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
    CLASSIFIER_MODEL: str = "gemini-2.5-flash"

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
    ALLOWED_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://uni-lang.vercel.app",
            "https://backend-tau-livid-81.vercel.app",
        ]
    )
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://uni-lang.vercel.app",
            "https://backend-tau-livid-81.vercel.app",
        ]
    )
    ALLOWED_ORIGIN_REGEX: str = r"^https:\/\/.*\.vercel\.app$"
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True

    # Environment & Database
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./datanova.db"
    AUTO_MIGRATE: bool = True

    # Storage Backend
    STORAGE_BACKEND: Literal["local", "s3"] = "local"
    LOCAL_STORAGE_DIR: str = "./storage_data"
    S3_ENDPOINT_URL: str = ""
    S3_BUCKET: str = "datanova-extract"
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_SSE: bool = False

    # Queue & Worker
    QUEUE_BACKEND: Literal["inline", "redis"] = "inline"
    REDIS_URL: str = "redis://localhost:6379/0"
    WORKER_CONCURRENCY: int = 10
    JOB_TIMEOUT_SECONDS: int = 300
    JOB_MAX_TRIES: int = 3

    # Authentication & Security
    AUTH_MODE: Literal["none", "local", "oidc"] = "none"
    JWT_SECRET: str = "datanova-enterprise-jwt-signing-secret-key-32chars"
    JWT_EXPIRATION_MINUTES: int = 1440
    SECURITY_HEADERS: bool = True
    TRUSTED_HOSTS: list[str] = Field(default_factory=lambda: ["*"])
    API_KEY: str = ""

    # Feature Flags & Capabilities
    FEATURE_STREAMING: bool = True
    FEATURE_GROUNDING: bool = True
    FEATURE_PERSISTENCE: bool = True
    FEATURE_HISTORY: bool = True
    FEATURE_BATCH: bool = True
    FEATURE_EXPORTS: bool = True
    FEATURE_EVAL: bool = True
    FEATURE_RATE_LIMIT: bool = True
    FEATURE_DEMO_MODE: bool = False
    FEATURE_OCR_CROSSCHECK: bool = False
    FEATURE_COMPLIANCE_ENGINE: bool = True
    FEATURE_FRAUD_DETECTION: bool = True
    FEATURE_LEARNING: bool = True
    FEATURE_RECONCILIATION: bool = True
    FEATURE_WORKFLOWS: bool = True
    FEATURE_WEBHOOKS: bool = True
    ALLOW_SENSITIVE_TYPES: bool = True

    # Performance & Concurrency Limits
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

    @field_validator("ALLOWED_ORIGINS", "CORS_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> list[str]:
        if isinstance(value, str):
            parsed = [origin.strip() for origin in value.split(",") if origin.strip()]
            if parsed:
                return parsed
        if isinstance(value, list):
            parsed = [str(origin).strip() for origin in value if str(origin).strip()]
            if parsed:
                return parsed
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://uni-lang.vercel.app",
            "https://backend-tau-livid-81.vercel.app",
        ]

    @field_validator("TRUSTED_HOSTS", mode="before")
    @classmethod
    def parse_trusted_hosts(cls, value: object) -> list[str]:
        if isinstance(value, str):
            return [h.strip() for h in value.split(",") if h.strip()]
        if isinstance(value, list):
            return [str(h).strip() for h in value if str(h).strip()]
        return ["*"]

    @model_validator(mode="after")
    def validate_production_hardening(self) -> "Settings":
        # In production, enforce non-local storage, relational Postgres, and tight origins
        if self.ENVIRONMENT == "production":
            if "sqlite" in self.DATABASE_URL:
                raise ValueError("Production environment cannot use SQLite; set PostgreSQL DATABASE_URL")
            if self.STORAGE_BACKEND == "local":
                raise ValueError("Production environment cannot use local storage; configure S3 / MinIO")
            if "*" in self.ALLOWED_ORIGINS or "*" in self.CORS_ORIGINS:
                raise ValueError("Production environment forbids wildcard CORS origins")
            if not self.API_KEY and self.AUTH_MODE == "none":
                raise ValueError("Production environment requires API_KEY or AUTH_MODE != 'none'")
        return self

    @model_validator(mode="after")
    def validate_provider_keys(self) -> "Settings":
        if self.FEATURE_DEMO_MODE:
            return self

        has_openai = bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip())
        has_google = bool(self.GOOGLE_API_KEY and self.GOOGLE_API_KEY.strip())

        if not has_openai and not has_google:
            if self.ENVIRONMENT != "production":
                # Graceful degradation in dev/staging to prevent boot crash
                self.FEATURE_DEMO_MODE = True
                return self
            raise ValueError(
                "Neither OPENAI_API_KEY nor GOOGLE_API_KEY is configured in production. "
                "Provide API keys or explicitly set FEATURE_DEMO_MODE=true."
            )

        if (
            os.getenv("DATANOVA_SKIP_KEY_VALIDATION", "false").lower() == "true"
            or os.getenv("PYTEST_CURRENT_TEST")
            or "pytest" in sys.modules
        ):
            return self

        provider_map = {
            "vision": self.LLM_PROVIDER_VISION,
            "extractor": self.LLM_PROVIDER_EXTRACTOR,
            "judge": self.LLM_PROVIDER_JUDGE,
        }

        for role, provider in provider_map.items():
            if provider == "openai" and not has_openai:
                if self.ENVIRONMENT != "production":
                    self.FEATURE_DEMO_MODE = True
                    return self
                raise ValueError(
                    f"Provider '{provider}' configured for role '{role}', but OPENAI_API_KEY is not set."
                )
            if provider == "google" and not has_google:
                if self.ENVIRONMENT != "production":
                    self.FEATURE_DEMO_MODE = True
                    return self
                raise ValueError(
                    f"Provider '{provider}' configured for role '{role}', but GOOGLE_API_KEY is not set."
                )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
