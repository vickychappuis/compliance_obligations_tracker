from __future__ import annotations


class FakeStorage:
    def __init__(self) -> None:
        self.uploaded: dict[str, tuple[bytes, str]] = {}

    def upload(self, path: str, data: bytes, content_type: str) -> None:
        self.uploaded[path] = (data, content_type)

    def signed_url(self, path: str) -> str:
        return f"https://signed.example/{path}"

    def remove(self, path: str) -> None:
        self.uploaded.pop(path, None)
