"""AWS S3 connector (boto3 wrapper) with streaming download."""
from __future__ import annotations

import importlib
from typing import Generator


class S3Connector:
    def __init__(self, aws_access_key_id: str | None = None, aws_secret_access_key: str | None = None, region_name: str | None = None):
        try:
            boto3 = importlib.import_module("boto3")
        except ModuleNotFoundError as exc:
            raise RuntimeError("boto3 is required for S3 connector") from exc
        self.s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    def stream_object(self, bucket: str, key: str) -> Generator[bytes, None, None]:
        obj = self.s3.get_object(Bucket=bucket, Key=key)
        body = obj["Body"]
        for chunk in iter(lambda: body.read(8192), b""):
            yield chunk
