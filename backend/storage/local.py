import asyncio
import os
import shutil
from pathlib import Path
from typing import List
from storage.base import ObjectStore


class LocalObjectStore(ObjectStore):
    """Secure filesystem-backed ObjectStore with atomic writes and directory containment."""

    def __init__(self, base_dir: str = "./storage_data"):
        self.base_path = Path(base_dir).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _resolve_key(self, key: str) -> Path:
        """Resolve key and ensure no directory traversal outside base_path."""
        clean_key = os.path.normpath(key.lstrip("/\\"))
        if clean_key.startswith("..") or ".." in clean_key.split(os.path.sep):
            raise ValueError(f"Path traversal detected in key: {key}")
        target = (self.base_path / clean_key).resolve()
        if not str(target).startswith(str(self.base_path)):
            raise ValueError(f"Path traversal detected in key: {key}")
        return target

    async def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        target = self._resolve_key(key)
        target.parent.mkdir(parents=True, exist_ok=True)

        tmp_path = target.with_suffix(f".tmp_{os.getpid()}_{id(data)}")

        def _sync_write() -> None:
            with open(tmp_path, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            shutil.move(str(tmp_path), str(target))

        await asyncio.to_thread(_sync_write)
        return key

    async def get(self, key: str) -> bytes:
        target = self._resolve_key(key)
        if not target.is_file():
            raise FileNotFoundError(f"Object not found: {key}")

        def _sync_read() -> bytes:
            with open(target, "rb") as f:
                return f.read()

        return await asyncio.to_thread(_sync_read)

    async def delete(self, key: str) -> bool:
        target = self._resolve_key(key)
        if target.is_file():
            await asyncio.to_thread(target.unlink, missing_ok=True)
            return True
        return False

    async def exists(self, key: str) -> bool:
        target = self._resolve_key(key)
        return await asyncio.to_thread(target.is_file)

    async def presign_get(self, key: str, expires_in_seconds: int = 3600) -> str:
        # For local dev, return a safe internal api path
        clean_key = key.lstrip("/\\").replace("\\", "/")
        return f"/api/v3/storage/file/{clean_key}"

    async def list_prefix(self, prefix: str) -> List[str]:
        target_dir = self._resolve_key(prefix)
        keys: List[str] = []

        def _sync_list() -> List[str]:
            results: List[str] = []
            if not target_dir.exists():
                parent = target_dir.parent
                if parent.exists():
                    for item in parent.rglob("*"):
                        if item.is_file():
                            rel = str(item.relative_to(self.base_path)).replace("\\", "/")
                            if rel.startswith(prefix):
                                results.append(rel)
                return results

            if target_dir.is_file():
                return [str(target_dir.relative_to(self.base_path)).replace("\\", "/")]

            for item in target_dir.rglob("*"):
                if item.is_file():
                    results.append(str(item.relative_to(self.base_path)).replace("\\", "/"))
            return results

        return await asyncio.to_thread(_sync_list)
