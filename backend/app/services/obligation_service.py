from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import uuid4

from sqlalchemy.orm import Session

from app.config import get_settings
from app.data.models import AuditEntryRow, DocumentRow, ObligationRow
from app.data.repository import ObligationRepository
from app.domain.errors import NotFound, VersionConflict
from app.domain.obligation import Obligation, ObligationType, Status
from app.domain.rules import assert_document_gate, is_overdue
from app.domain.state_machine import allowed_transitions, validate_transition
from app.integrations.storage import DocumentStorage, get_storage


@dataclass
class ObligationCreate:
    type: ObligationType
    title: str
    description: str
    due_date: date
    owner: str
    requires_document: bool
    company_tax_id: str


@dataclass
class ObligationPatch:
    title: str | None = None
    description: str | None = None
    type: ObligationType | None = None
    due_date: date | None = None
    owner: str | None = None
    requires_document: bool | None = None
    company_tax_id: str | None = None


@dataclass
class ObligationView:
    row: ObligationRow
    has_document: bool
    overdue: bool
    allowed_transitions: list[Status]
    audit: list[AuditEntryRow]
    documents: list[DocumentRow]


@dataclass
class Summary:
    total: int
    by_status: dict[str, int]
    overdue: int
    upcoming: int


class ObligationService:
    UPCOMING_WINDOW_DAYS = 30

    def __init__(self, session: Session, storage: DocumentStorage | None = None) -> None:
        self.session = session
        self.repo = ObligationRepository(session)
        self._storage = storage

    @property
    def storage(self) -> DocumentStorage:
        if self._storage is None:
            self._storage = get_storage(get_settings())
        return self._storage

    def create(self, data: ObligationCreate) -> ObligationView:
        row = ObligationRow(
            type=data.type.value,
            title=data.title,
            description=data.description,
            status=Status.PENDING.value,
            due_date=data.due_date,
            owner=data.owner,
            requires_document=data.requires_document,
            company_tax_id=data.company_tax_id,
            version=1,
        )
        self.repo.add(row)
        self.repo.add_audit_entry(row.id, None, Status.PENDING)
        self.session.commit()
        return self._view(row)

    def update_fields(self, obligation_id: str, patch: ObligationPatch) -> ObligationView:
        row = self._require(obligation_id)
        if patch.title is not None:
            row.title = patch.title
        if patch.description is not None:
            row.description = patch.description
        if patch.type is not None:
            row.type = patch.type.value
        if patch.due_date is not None:
            row.due_date = patch.due_date
        if patch.owner is not None:
            row.owner = patch.owner
        if patch.requires_document is not None:
            row.requires_document = patch.requires_document
        if patch.company_tax_id is not None:
            row.company_tax_id = patch.company_tax_id
        self.session.commit()
        return self._view(row)

    def change_state(
        self, obligation_id: str, target: Status, expected_version: int
    ) -> ObligationView:
        row = self._require(obligation_id)
        if row.version != expected_version:
            raise VersionConflict()

        current = Status(row.status)
        domain = self._to_domain(row, self._has_document(row))
        validate_transition(current, target)
        assert_document_gate(domain, target)

        affected = self.repo.bump_status(obligation_id, expected_version, target)
        if affected == 0:
            self.session.rollback()
            raise VersionConflict()
        self.repo.add_audit_entry(obligation_id, current, target)
        self.session.commit()
        self.session.refresh(row)
        return self._view(row)

    def attach_document(
        self, obligation_id: str, filename: str, content_type: str, data: bytes
    ) -> ObligationView:
        row = self._require(obligation_id)
        storage_path = f"{obligation_id}/{uuid4().hex}-{filename}"
        self.storage.upload(storage_path, data, content_type)
        self.repo.add_document(
            obligation_id, filename, content_type, storage_path, len(data)
        )
        self.session.commit()
        self.session.refresh(row)
        return self._view(row)

    def document_download_url(self, obligation_id: str, document_id: str) -> str:
        self._require(obligation_id)
        document = self.repo.get_document(obligation_id, document_id)
        if document is None:
            raise NotFound(document_id)
        return self.storage.signed_url(document.storage_path)

    def get_view(self, obligation_id: str) -> ObligationView:
        return self._view(self._require(obligation_id))

    def list_views(
        self,
        *,
        status: Status | None = None,
        type: ObligationType | None = None,
        owner: str | None = None,
        overdue: bool | None = None,
        today: date | None = None,
    ) -> list[ObligationView]:
        today = today or date.today()
        rows = self.repo.list(status=status, type=type, owner=owner)
        views = [self._view(row, today=today) for row in rows]
        if overdue is not None:
            views = [v for v in views if v.overdue == overdue]
        return views

    def summary(self, today: date | None = None) -> Summary:
        today = today or date.today()
        views = self.list_views(today=today)
        by_status = {s.value: 0 for s in Status}
        overdue = 0
        upcoming = 0
        for view in views:
            by_status[view.row.status] += 1
            if view.overdue:
                overdue += 1
            elif self._is_upcoming(view, today):
                upcoming += 1
        return Summary(
            total=len(views), by_status=by_status, overdue=overdue, upcoming=upcoming
        )

    def _require(self, obligation_id: str) -> ObligationRow:
        row = self.repo.get(obligation_id)
        if row is None:
            raise NotFound(obligation_id)
        return row

    def _has_document(self, row: ObligationRow) -> bool:
        return len(row.documents) > 0

    def _to_domain(self, row: ObligationRow, has_document: bool) -> Obligation:
        return Obligation(
            id=row.id,
            type=ObligationType(row.type),
            title=row.title,
            description=row.description,
            status=Status(row.status),
            due_date=row.due_date,
            owner=row.owner,
            requires_document=row.requires_document,
            has_document=has_document,
            company_tax_id=row.company_tax_id,
        )

    def _view(self, row: ObligationRow, today: date | None = None) -> ObligationView:
        today = today or date.today()
        has_document = self._has_document(row)
        domain = self._to_domain(row, has_document)
        return ObligationView(
            row=row,
            has_document=has_document,
            overdue=is_overdue(domain, today),
            allowed_transitions=sorted(
                allowed_transitions(Status(row.status)), key=lambda s: s.value
            ),
            audit=list(row.audit_entries),
            documents=list(row.documents),
        )

    def _is_upcoming(self, view: ObligationView, today: date) -> bool:
        if view.row.status in (Status.SUBMITTED.value, Status.DONE.value):
            return False
        delta = (view.row.due_date - today).days
        return 0 <= delta <= self.UPCOMING_WINDOW_DAYS
