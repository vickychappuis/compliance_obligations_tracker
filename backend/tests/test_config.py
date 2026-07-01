from __future__ import annotations

from app.config import Settings


def test_max_upload_bytes_derives_from_mb() -> None:
    assert Settings(max_upload_mb=5).max_upload_bytes == 5 * 1024 * 1024


def test_allowed_document_types_set_splits_and_trims() -> None:
    settings = Settings(allowed_document_types="application/pdf, image/* , ")
    assert settings.allowed_document_types_set == frozenset(
        {"application/pdf", "image/*"}
    )


def test_defaults_allow_pdf_and_images() -> None:
    allowed = Settings().allowed_document_types_set
    assert "application/pdf" in allowed
    assert "image/*" in allowed
