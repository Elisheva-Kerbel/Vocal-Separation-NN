"""S3/MinIO storage adapter (Phase 4).

All private storage access goes through this module. No public URLs, no permanent
URLs. Signed URLs are generated with a short TTL for listen/download.
"""

from __future__ import annotations

import uuid
from functools import lru_cache

import boto3
from botocore.config import Config as BotoConfig

from app.config import load_settings


@lru_cache(maxsize=1)
def _s3_client():
    settings = load_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url or None,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        region_name=settings.s3_region,
        config=BotoConfig(signature_version="s3v4"),
    )


@lru_cache(maxsize=1)
def _s3_public_client():
    settings = load_settings()
    public_url = settings.s3_public_endpoint_url or settings.s3_endpoint_url
    return boto3.client(
        "s3",
        endpoint_url=public_url or None,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        region_name=settings.s3_region,
        config=BotoConfig(signature_version="s3v4"),
    )


def _bucket() -> str:
    return load_settings().s3_bucket


def generate_storage_key(user_id: uuid.UUID, song_id: uuid.UUID, purpose: str, ext: str) -> str:
    return f"{user_id}/{song_id}/{purpose}{ext}"


def ensure_bucket() -> None:
    client = _s3_client()
    bucket = _bucket()
    try:
        client.head_bucket(Bucket=bucket)
    except client.exceptions.ClientError:
        client.create_bucket(Bucket=bucket)


def upload_fileobj(fileobj, storage_key: str, content_type: str) -> None:
    _s3_client().upload_fileobj(
        fileobj, _bucket(), storage_key,
        ExtraArgs={"ContentType": content_type},
    )


def upload_bytes(data: bytes, storage_key: str, content_type: str) -> None:
    from io import BytesIO
    upload_fileobj(BytesIO(data), storage_key, content_type)


def download_bytes(storage_key: str) -> bytes:
    from io import BytesIO
    buf = BytesIO()
    _s3_client().download_fileobj(_bucket(), storage_key, buf)
    buf.seek(0)
    return buf.read()


def download_to_file(storage_key: str, local_path: str) -> None:
    _s3_client().download_file(_bucket(), storage_key, local_path)


def upload_from_file(local_path: str, storage_key: str, content_type: str) -> None:
    _s3_client().upload_file(local_path, _bucket(), storage_key, ExtraArgs={"ContentType": content_type})


def delete_object(storage_key: str) -> None:
    _s3_client().delete_object(Bucket=_bucket(), Key=storage_key)


def generate_signed_url(storage_key: str, ttl_seconds: int, *, download_filename: str | None = None) -> str:
    params: dict = {"Bucket": _bucket(), "Key": storage_key}
    if download_filename:
        params["ResponseContentDisposition"] = f'attachment; filename="{download_filename}"'
    return _s3_public_client().generate_presigned_url(
        "get_object",
        Params=params,
        ExpiresIn=ttl_seconds,
    )


def object_exists(storage_key: str) -> bool:
    try:
        _s3_client().head_object(Bucket=_bucket(), Key=storage_key)
        return True
    except _s3_client().exceptions.ClientError:
        return False
