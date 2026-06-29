from __future__ import annotations

from datetime import date

import pytest

from app.domain.errors import DocumentRequired
from app.domain.obligation import Status
from app.domain.rules import assert_document_gate, is_overdue
from tests.domain.conftest import make_obligation

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
