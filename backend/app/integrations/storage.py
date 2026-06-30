from __future__ import annotations

from typing import Protocol

import httpx

from app.config import Settings


class StorageError(RuntimeError):
    pass


class StorageNotConfigured(StorageError):
    pass


class DocumentStorage(Protocol):
    def upload(self, path: str, data: bytes, content_type: str) -> None: ...

    def signed_url(self, path: str) -> str: ...

    def remove(self, path: str) -> None: ...


class SupabaseStorage:
    def __init__(self, settings: Settings) -> None:
        self._base = settings.supabase_url.rstrip("/")
        self._key = settings.supabase_service_key
        self._bucket = settings.supabase_bucket
        self._expiry = settings.signed_url_expiry_seconds

    def _require_config(self) -> None:
        if not self._base or not self._key:
            raise StorageNotConfigured(
                "Supabase storage is not configured. Set SUPABASE_URL and "
                "SUPABASE_SERVICE_KEY."
            )

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._key}",
            "apikey": self._key,
        }

    def upload(self, path: str, data: bytes, content_type: str) -> None:
        self._require_config()
        url = f"{self._base}/storage/v1/object/{self._bucket}/{path}"
        response = httpx.post(
            url,
            content=data,
            headers={
                **self._headers,
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            timeout=30.0,
        )
        if response.status_code >= 400:
            raise StorageError(f"Upload failed ({response.status_code}).")

    def signed_url(self, path: str) -> str:
        self._require_config()
        url = f"{self._base}/storage/v1/object/sign/{self._bucket}/{path}"
        response = httpx.post(
            url,
            json={"expiresIn": self._expiry},
            headers=self._headers,
            timeout=30.0,
        )
        if response.status_code >= 400:
            raise StorageError(f"Signing failed ({response.status_code}).")
        signed = response.json().get("signedURL")
        if not signed:
            raise StorageError("Signing response missing signedURL.")
        return f"{self._base}/storage/v1{signed}"

    def remove(self, path: str) -> None:
        self._require_config()
        url = f"{self._base}/storage/v1/object/{self._bucket}/{path}"
        response = httpx.request("DELETE", url, headers=self._headers, timeout=30.0)
        if response.status_code >= 400:
            raise StorageError(f"Remove failed ({response.status_code}).")


def get_storage(settings: Settings) -> DocumentStorage:
    return SupabaseStorage(settings)
