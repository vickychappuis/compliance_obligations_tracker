from __future__ import annotations

from datetime import date

from app.domain.obligation import Obligation, ObligationType, Status


def make_obligation(
    *,
    status: Status = Status.PENDING,
    due_date: date = date(2026, 1, 1),
    requires_document: bool = False,
    has_document: bool = False,
) -> Obligation:
    """Build an Obligation for tests with sensible defaults."""
    return Obligation(
        id="test-id",
        type=ObligationType.ANNUAL_REPORT,
        title="Annual report",
        description="File the annual report.",
        status=status,
        due_date=due_date,
        owner="Jane Founder",
        requires_document=requires_document,
        has_document=has_document,
        company_tax_id="123456789",
    )
