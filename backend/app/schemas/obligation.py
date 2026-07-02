from __future__ import annotations

import re
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.obligation import ObligationType, Status
from app.services.obligation_service import ObligationView, Summary

MASK_PREFIX = "••••"
COMPANY_TAX_ID_MESSAGE = (
    "company_tax_id must contain 4-64 letters or digits and may use spaces or "
    "hyphens as separators"
)
_COMPANY_TAX_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 -]{2,62}[A-Za-z0-9]$")


def mask_tax_id(value: str) -> str:
    digits = value.strip()
    if len(digits) <= 4:
        return MASK_PREFIX
    return f"{MASK_PREFIX}{digits[-4:]}"


def validate_company_tax_id(value: str) -> str:
    tax_id = value.strip()
    alnum_count = sum(char.isalnum() for char in tax_id)
    if not _COMPANY_TAX_ID_RE.fullmatch(tax_id) or alnum_count < 4:
        raise ValueError(COMPANY_TAX_ID_MESSAGE)
    return tax_id


class ObligationCreateRequest(BaseModel):
    type: ObligationType
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    due_date: date
    owner: str = Field(min_length=1, max_length=200)
    requires_document: bool = False
    company_tax_id: str = Field(min_length=1, max_length=64)

    @field_validator("company_tax_id")
    @classmethod
    def validate_tax_id(cls, value: str) -> str:
        return validate_company_tax_id(value)


class ObligationPatchRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    type: ObligationType | None = None
    due_date: date | None = None
    owner: str | None = Field(default=None, min_length=1, max_length=200)
    requires_document: bool | None = None
    company_tax_id: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("company_tax_id")
    @classmethod
    def validate_tax_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_company_tax_id(value)


class TransitionRequest(BaseModel):
    target_status: Status
    expected_version: int = Field(ge=1)


class AuditEntryResponse(BaseModel):
    from_status: Status | None
    to_status: Status
    timestamp: datetime


class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int
    uploaded_at: datetime


class DocumentUrlResponse(BaseModel):
    url: str


class ObligationResponse(BaseModel):
    id: str
    type: ObligationType
    title: str
    description: str
    status: Status
    due_date: date
    owner: str
    requires_document: bool
    has_document: bool
    company_tax_id: str
    version: int
    overdue: bool
    can_submit: bool
    allowed_transitions: list[Status]
    created_at: datetime


class ObligationDetailResponse(ObligationResponse):
    audit: list[AuditEntryResponse]
    documents: list[DocumentResponse]


class SummaryResponse(BaseModel):
    total: int
    by_status: dict[str, int]
    overdue: int
    upcoming: int


def to_response(view: ObligationView) -> ObligationResponse:
    return ObligationResponse(**_base_fields(view))


def to_detail_response(view: ObligationView) -> ObligationDetailResponse:
    return ObligationDetailResponse(
        **_base_fields(view),
        audit=[
            AuditEntryResponse(
                from_status=Status(e.from_status) if e.from_status else None,
                to_status=Status(e.to_status),
                timestamp=e.timestamp,
            )
            for e in view.audit
        ],
        documents=[
            DocumentResponse(
                id=d.id,
                filename=d.filename,
                content_type=d.content_type,
                size=d.size,
                uploaded_at=d.uploaded_at,
            )
            for d in view.documents
        ],
    )


def to_summary_response(summary: Summary) -> SummaryResponse:
    return SummaryResponse(
        total=summary.total,
        by_status=summary.by_status,
        overdue=summary.overdue,
        upcoming=summary.upcoming,
    )


def _base_fields(view: ObligationView) -> dict:
    row = view.row
    return {
        "id": row.id,
        "type": ObligationType(row.type),
        "title": row.title,
        "description": row.description,
        "status": Status(row.status),
        "due_date": row.due_date,
        "owner": row.owner,
        "requires_document": row.requires_document,
        "has_document": view.has_document,
        "company_tax_id": mask_tax_id(row.company_tax_id),
        "version": row.version,
        "overdue": view.overdue,
        "can_submit": view.can_submit,
        "allowed_transitions": view.allowed_transitions,
        "created_at": row.created_at,
    }
