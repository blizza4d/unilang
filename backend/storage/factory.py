from typing import Optional
from config import get_settings
from storage.base import ObjectStore
from storage.local import LocalObjectStore
from storage.s3 import S3ObjectStore

_storage_instance: Optional[ObjectStore] = None


def get_storage() -> ObjectStore:
    """Return the configured ObjectStore singleton."""
    global _storage_instance
    if _storage_instance is not None:
        return _storage_instance

    settings = get_settings()
    backend = getattr(settings, "STORAGE_BACKEND", "local").lower()

    if backend == "s3":
        _storage_instance = S3ObjectStore(
            bucket=getattr(settings, "S3_BUCKET", "datanova-extract"),
            endpoint_url=getattr(settings, "S3_ENDPOINT_URL", None),
            region_name=getattr(settings, "S3_REGION", "us-east-1"),
            access_key_id=getattr(settings, "S3_ACCESS_KEY", None),
            secret_access_key=getattr(settings, "S3_SECRET_KEY", None),
            server_side_encryption=getattr(settings, "S3_SSE", False),
        )
    else:
        storage_dir = getattr(settings, "LOCAL_STORAGE_DIR", "./storage_data")
        _storage_instance = LocalObjectStore(base_dir=storage_dir)

    return _storage_instance


def reset_storage_for_tests() -> None:
    """Reset storage singleton for isolation in unit tests."""
    global _storage_instance
    _storage_instance = None
