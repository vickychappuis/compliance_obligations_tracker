from __future__ import annotations

from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session

from app.config import Settings
from app.domain.errors import (
    DocumentRequired,
    InvalidDocument,
    InvalidTransition,
    NotFound,
    VersionConflict,
)
from app.domain.obligation import ObligationType, Status
from app.services.obligation_service import (
    ObligationCreate,
    ObligationPatch,
    ObligationService,
)
from tests.fakes import FakeStorage

TODAY = date(2026, 6, 27)


def _new(
    *,
    requires_document: bool = False,
    due_date: date = TODAY + timedelta(days=10),
    owner: str = "Jane Founder",
    type: ObligationType = ObligationType.ANNUAL_REPORT,
) -> ObligationCreate:
    return ObligationCreate(
        type=type,
        title="Annual report",
        description="File it.",
        due_date=due_date,
        owner=owner,
        requires_document=requires_document,
        company_tax_id="123456789",
    )


def test_create_starts_pending_with_audit(session: Session) -> None:
    svc = ObligationService(session)
    view = svc.create(_new())
    assert view.row.status == Status.PENDING.value
    assert view.row.version == 1
    assert len(view.audit) == 1
    assert view.audit[0].from_status is None
    assert view.audit[0].to_status == Status.PENDING.value
    assert view.allowed_transitions == [Status.IN_PROGRESS]


def test_change_state_bumps_version_and_records_audit(session: Session) -> None:
    svc = ObligationService(session)
    view = svc.create(_new())
    updated = svc.change_state(view.row.id, Status.IN_PROGRESS, expected_version=1)
    assert updated.row.status == Status.IN_PROGRESS.value
    assert updated.row.version == 2
    assert [e.to_status for e in updated.audit] == [
        Status.PENDING.value,
        Status.IN_PROGRESS.value,
    ]
    assert updated.audit[-1].from_status == Status.PENDING.value


def test_invalid_transition_is_rejected(session: Session) -> None:
    svc = ObligationService(session)
    view = svc.create(_new())
    with pytest.raises(InvalidTransition):
        svc.change_state(view.row.id, Status.DONE, expected_version=1)
    session.refresh(view.row)
    assert view.row.status == Status.PENDING.value
    assert view.row.version == 1


def test_document_gate_blocks_then_allows_submit(session: Session) -> None:
    storage = FakeStorage()
    svc = ObligationService(session, storage=storage)
    view = svc.create(_new(requires_document=True))
    svc.change_state(view.row.id, Status.IN_PROGRESS, expected_version=1)
    with pytest.raises(DocumentRequired):
        svc.change_state(view.row.id, Status.SUBMITTED, expected_version=2)

    attached = svc.attach_document(
        view.row.id, "filing.pdf", "application/pdf", b"%PDF-1.7 data"
    )
    submitted = svc.change_state(
        view.row.id, Status.SUBMITTED, expected_version=attached.row.version
    )
    assert submitted.row.status == Status.SUBMITTED.value
    assert submitted.has_document is True


def test_attach_document_uploads_bytes_and_signs_url(session: Session) -> None:
    storage = FakeStorage()
    svc = ObligationService(session, storage=storage)
    view = svc.create(_new(requires_document=True))

    attached = svc.attach_document(view.row.id, "filing.pdf", "application/pdf", b"abc")
    document = attached.documents[0]
    assert document.size == 3
    assert document.storage_path in storage.uploaded
    assert storage.uploaded[document.storage_path] == (b"abc", "application/pdf")

    url = svc.document_download_url(view.row.id, document.id)
    assert url == f"https://signed.example/{document.storage_path}"


def test_attach_document_rejects_oversized_file(session: Session) -> None:
    storage = FakeStorage()
    svc = ObligationService(
        session, storage=storage, settings=Settings(max_upload_mb=1)
    )
    view = svc.create(_new(requires_document=True))

    oversized = b"x" * (1024 * 1024 + 1)
    with pytest.raises(InvalidDocument):
        svc.attach_document(view.row.id, "big.pdf", "application/pdf", oversized)
    assert storage.uploaded == {}


def test_attach_document_rejects_unsupported_type(session: Session) -> None:
    storage = FakeStorage()
    svc = ObligationService(session, storage=storage)
    view = svc.create(_new(requires_document=True))

    with pytest.raises(InvalidDocument):
        svc.attach_document(view.row.id, "evil.exe", "application/x-msdownload", b"MZ")
    assert storage.uploaded == {}


def test_document_download_url_missing_raises_not_found(session: Session) -> None:
    svc = ObligationService(session, storage=FakeStorage())
    view = svc.create(_new())
    with pytest.raises(NotFound):
        svc.document_download_url(view.row.id, "does-not-exist")


def test_remove_document_deletes_row_and_storage_object(session: Session) -> None:
    storage = FakeStorage()
    svc = ObligationService(session, storage=storage)
    view = svc.create(_new(requires_document=True))
    attached = svc.attach_document(view.row.id, "filing.pdf", "application/pdf", b"abc")
    document = attached.documents[0]
    document_id = document.id
    storage_path = document.storage_path
    assert storage_path in storage.uploaded

    after = svc.remove_document(view.row.id, document_id)
    assert after.documents == []
    assert after.has_document is False
    assert storage_path not in storage.uploaded


def test_remove_document_missing_raises_not_found(session: Session) -> None:
    svc = ObligationService(session, storage=FakeStorage())
    view = svc.create(_new())
    with pytest.raises(NotFound):
        svc.remove_document(view.row.id, "does-not-exist")


def test_version_conflict_on_stale_expected_version(session: Session) -> None:
    svc = ObligationService(session)
    view = svc.create(_new())
    svc.change_state(view.row.id, Status.IN_PROGRESS, expected_version=1)
    with pytest.raises(VersionConflict):
        svc.change_state(view.row.id, Status.SUBMITTED, expected_version=1)


def test_document_mutations_bump_version(session: Session) -> None:
    storage = FakeStorage()
    svc = ObligationService(session, storage=storage)
    view = svc.create(_new(requires_document=True))

    attached = svc.attach_document(view.row.id, "filing.pdf", "application/pdf", b"abc")
    assert attached.row.version == 2

    removed = svc.remove_document(view.row.id, attached.documents[0].id)
    assert removed.row.version == 3


def test_update_fields_bumps_version(session: Session) -> None:
    svc = ObligationService(session)
    view = svc.create(_new())
    updated = svc.update_fields(view.row.id, ObligationPatch(requires_document=True))
    assert updated.row.version == 2


def test_document_removal_invalidates_stale_transition(session: Session) -> None:
    storage = FakeStorage()
    svc = ObligationService(session, storage=storage)
    view = svc.create(_new(requires_document=True))
    svc.change_state(view.row.id, Status.IN_PROGRESS, expected_version=1)
    attached = svc.attach_document(view.row.id, "filing.pdf", "application/pdf", b"abc")
    version_before_removal = attached.row.version

    svc.remove_document(view.row.id, attached.documents[0].id)

    with pytest.raises(VersionConflict):
        svc.change_state(
            view.row.id, Status.SUBMITTED, expected_version=version_before_removal
        )
    session.refresh(view.row)
    assert view.row.status == Status.IN_PROGRESS.value


def test_get_and_change_missing_raises_not_found(session: Session) -> None:
    svc = ObligationService(session)
    with pytest.raises(NotFound):
        svc.get_view("does-not-exist")
    with pytest.raises(NotFound):
        svc.change_state("does-not-exist", Status.IN_PROGRESS, expected_version=1)


def test_overdue_is_derived(session: Session) -> None:
    svc = ObligationService(session)
    past = svc.create(_new(due_date=TODAY - timedelta(days=1)))
    assert svc.get_view(past.row.id) is not None
    views = svc.list_views(today=TODAY)
    assert views[0].overdue is True


def test_list_is_sorted_by_due_date_and_filters(session: Session) -> None:
    svc = ObligationService(session)
    svc.create(_new(due_date=TODAY + timedelta(days=30), owner="A"))
    svc.create(_new(due_date=TODAY + timedelta(days=5), owner="B"))
    svc.create(_new(due_date=TODAY - timedelta(days=2), owner="A"))

    all_views = svc.list_views(today=TODAY)
    due_dates = [v.row.due_date for v in all_views]
    assert due_dates == sorted(due_dates)

    by_owner = svc.list_views(owner="A", today=TODAY)
    assert {v.row.owner for v in by_owner} == {"A"}
    assert len(by_owner) == 2

    overdue_only = svc.list_views(overdue=True, today=TODAY)
    assert len(overdue_only) == 1
    assert overdue_only[0].overdue is True


def test_update_fields_does_not_change_status(session: Session) -> None:
    svc = ObligationService(session)
    view = svc.create(_new())
    updated = svc.update_fields(
        view.row.id, ObligationPatch(title="Renamed", owner="New")
    )
    assert updated.row.title == "Renamed"
    assert updated.row.owner == "New"
    assert updated.row.status == Status.PENDING.value


def test_summary_counts(session: Session) -> None:
    svc = ObligationService(session)
    svc.create(_new(due_date=TODAY - timedelta(days=1)))
    svc.create(_new(due_date=TODAY + timedelta(days=10)))
    done = svc.create(_new(due_date=TODAY + timedelta(days=10)))
    svc.change_state(done.row.id, Status.IN_PROGRESS, expected_version=1)
    svc.change_state(done.row.id, Status.SUBMITTED, expected_version=2)
    svc.change_state(done.row.id, Status.DONE, expected_version=3)

    s = svc.summary(today=TODAY)
    assert s.total == 3
    assert s.overdue == 1
    assert s.upcoming == 1
    assert s.by_status[Status.DONE.value] == 1
    assert s.by_status[Status.PENDING.value] == 2
