from typing import List, Optional
import aioboto3
from storage.base import ObjectStore


class S3ObjectStore(ObjectStore):
    """S3 and MinIO compatible async ObjectStore using aioboto3."""

    def __init__(
        self,
        bucket: str,
        endpoint_url: Optional[str] = None,
        region_name: str = "us-east-1",
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        server_side_encryption: bool = False,
    ):
        self.bucket = bucket
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.server_side_encryption = server_side_encryption
        self.session = aioboto3.Session()

    def _get_client_args(self) -> dict:
        args = {
            "region_name": self.region_name,
        }
        if self.endpoint_url:
            args["endpoint_url"] = self.endpoint_url
        if self.access_key_id and self.secret_access_key:
            args["aws_access_key_id"] = self.access_key_id
            args["aws_secret_access_key"] = self.secret_access_key
        return args

    async def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        clean_key = key.lstrip("/\\").replace("\\", "/")
        extra_args = {"ContentType": content_type}
        if self.server_side_encryption:
            extra_args["ServerSideEncryption"] = "AES256"

        async with self.session.client("s3", **self._get_client_args()) as s3:
            await s3.put_object(
                Bucket=self.bucket,
                Key=clean_key,
                Body=data,
                **extra_args,
            )
        return clean_key

    async def get(self, key: str) -> bytes:
        clean_key = key.lstrip("/\\").replace("\\", "/")
        async with self.session.client("s3", **self._get_client_args()) as s3:
            try:
                response = await s3.get_object(Bucket=self.bucket, Key=clean_key)
                async with response["Body"] as stream:
                    return await stream.read()
            except s3.exceptions.NoSuchKey:
                raise FileNotFoundError(f"S3 Object not found: {key}")

    async def delete(self, key: str) -> bool:
        clean_key = key.lstrip("/\\").replace("\\", "/")
        async with self.session.client("s3", **self._get_client_args()) as s3:
            await s3.delete_object(Bucket=self.bucket, Key=clean_key)
            return True

    async def exists(self, key: str) -> bool:
        clean_key = key.lstrip("/\\").replace("\\", "/")
        async with self.session.client("s3", **self._get_client_args()) as s3:
            try:
                await s3.head_object(Bucket=self.bucket, Key=clean_key)
                return True
            except Exception:
                return False

    async def presign_get(self, key: str, expires_in_seconds: int = 3600) -> str:
        clean_key = key.lstrip("/\\").replace("\\", "/")
        async with self.session.client("s3", **self._get_client_args()) as s3:
            url: str = await s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": clean_key},
                ExpiresIn=expires_in_seconds,
            )
            return url

    async def list_prefix(self, prefix: str) -> List[str]:
        clean_prefix = prefix.lstrip("/\\").replace("\\", "/")
        keys: List[str] = []
        async with self.session.client("s3", **self._get_client_args()) as s3:
            paginator = s3.get_paginator("list_objects_v2")
            async for page in paginator.paginate(Bucket=self.bucket, Prefix=clean_prefix):
                for obj in page.get("Contents", []):
                    keys.append(obj["Key"])
        return keys
