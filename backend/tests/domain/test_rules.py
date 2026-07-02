from __future__ import annotations

from datetime import date

import pytest

from app.domain.errors import DocumentRequired, InvalidDocument
from app.domain.obligation import Status
from app.domain.rules import (
    assert_document_allowed,
    assert_document_gate,
    is_document_gate_satisfied,
    is_overdue,
)
from tests.domain.conftest import make_obligation

ALLOWED = frozenset({"application/pdf", "image/*"})
MAX_BYTES = 1024

TODAY = date(2026, 6, 27)
PAST = date(2026, 6, 1)
FUTURE = date(2026, 7, 1)


class TestIsOverdue:
    def test_past_due_and_pending_is_overdue(self) -> None:
        ob = make_obligation(status=Status.PENDING, due_date=PAST)
        assert is_overdue(ob, TODAY) is True

    def test_past_due_and_in_progress_is_overdue(self) -> None:
        ob = make_obligation(status=Status.IN_PROGRESS, due_date=PAST)
        assert is_overdue(ob, TODAY) is True

    def test_past_due_but_submitted_is_not_overdue(self) -> None:
        ob = make_obligation(status=Status.SUBMITTED, due_date=PAST)
        assert is_overdue(ob, TODAY) is False

    def test_past_due_but_done_is_not_overdue(self) -> None:
        ob = make_obligation(status=Status.DONE, due_date=PAST)
        assert is_overdue(ob, TODAY) is False

    def test_future_due_is_not_overdue(self) -> None:
        ob = make_obligation(status=Status.PENDING, due_date=FUTURE)
        assert is_overdue(ob, TODAY) is False

    def test_due_today_is_not_overdue(self) -> None:
        ob = make_obligation(status=Status.PENDING, due_date=TODAY)
        assert is_overdue(ob, TODAY) is False


class TestDocumentGate:
    def test_blocks_submit_when_required_and_missing(self) -> None:
        ob = make_obligation(requires_document=True, has_document=False)
        with pytest.raises(DocumentRequired):
            assert_document_gate(ob, Status.SUBMITTED)

    def test_allows_submit_when_required_and_present(self) -> None:
        ob = make_obligation(requires_document=True, has_document=True)
        assert_document_gate(ob, Status.SUBMITTED)

    def test_allows_submit_when_not_required(self) -> None:
        ob = make_obligation(requires_document=False, has_document=False)
        assert_document_gate(ob, Status.SUBMITTED)

    def test_gate_only_applies_to_submitted_target(self) -> None:
        ob = make_obligation(requires_document=True, has_document=False)
        for target in (Status.IN_PROGRESS, Status.PENDING, Status.DONE):
            assert_document_gate(ob, target)


class TestDocumentAllowed:
    def test_accepts_allowed_type_within_limit(self) -> None:
        assert_document_allowed(
            size=512,
            content_type="application/pdf",
            max_bytes=MAX_BYTES,
            allowed_content_types=ALLOWED,
        )

    def test_accepts_type_via_family_wildcard(self) -> None:
        assert_document_allowed(
            size=512,
            content_type="image/png",
            max_bytes=MAX_BYTES,
            allowed_content_types=ALLOWED,
        )

    def test_rejects_empty_file(self) -> None:
        with pytest.raises(InvalidDocument):
            assert_document_allowed(
                size=0,
                content_type="application/pdf",
                max_bytes=MAX_BYTES,
                allowed_content_types=ALLOWED,
            )

    def test_rejects_oversized_file(self) -> None:
        with pytest.raises(InvalidDocument):
            assert_document_allowed(
                size=MAX_BYTES + 1,
                content_type="application/pdf",
                max_bytes=MAX_BYTES,
                allowed_content_types=ALLOWED,
            )

    def test_rejects_unsupported_type(self) -> None:
        with pytest.raises(InvalidDocument):
            assert_document_allowed(
                size=512,
                content_type="application/x-msdownload",
                max_bytes=MAX_BYTES,
                allowed_content_types=ALLOWED,
            )


class TestIsDocumentGateSatisfied:
    def test_satisfied_when_not_required(self) -> None:
        ob = make_obligation(requires_document=False, has_document=False)
        assert is_document_gate_satisfied(ob) is True

    def test_not_satisfied_when_required_and_missing(self) -> None:
        ob = make_obligation(requires_document=True, has_document=False)
        assert is_document_gate_satisfied(ob) is False

    def test_satisfied_when_required_and_present(self) -> None:
        ob = make_obligation(requires_document=True, has_document=True)
        assert is_document_gate_satisfied(ob) is True
