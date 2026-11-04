from typing import List, Protocol, runtime_checkable


@runtime_checkable
class ObjectStore(Protocol):
    """Abstract object storage protocol for DataNova Extract."""

    async def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Store bytes at key. Returns the stored key."""
        ...

    async def get(self, key: str) -> bytes:
        """Retrieve bytes at key. Raises FileNotFoundError if missing."""
        ...

    async def delete(self, key: str) -> bool:
        """Delete object at key. Returns True if deleted or did not exist."""
        ...

    async def exists(self, key: str) -> bool:
        """Check if object exists at key."""
        ...

    async def presign_get(self, key: str, expires_in_seconds: int = 3600) -> str:
        """Generate a presigned GET URL or safe local read URI."""
        ...

    async def list_prefix(self, prefix: str) -> List[str]:
        """List all object keys under prefix."""
        ...
