from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.data.models import AuditEntryRow, DocumentRow, ObligationRow
from app.domain.obligation import ObligationType, Status


class ObligationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, obligation_id: str) -> ObligationRow | None:
        return self.session.get(ObligationRow, obligation_id)

    def list(
        self,
        *,
        status: Status | None = None,
        type: ObligationType | None = None,
        owner: str | None = None,
    ) -> list[ObligationRow]:
        stmt = select(ObligationRow)
        if status is not None:
            stmt = stmt.where(ObligationRow.status == status.value)
        if type is not None:
            stmt = stmt.where(ObligationRow.type == type.value)
        if owner is not None:
            stmt = stmt.where(ObligationRow.owner == owner)
        stmt = stmt.order_by(ObligationRow.due_date.asc())
        return list(self.session.scalars(stmt).all())

    def add(self, row: ObligationRow) -> ObligationRow:
        self.session.add(row)
        self.session.flush()
        return row

    def bump_status(
        self, obligation_id: str, expected_version: int, new_status: Status
    ) -> int:
        result = self.session.execute(
            update(ObligationRow)
            .where(
                ObligationRow.id == obligation_id,
                ObligationRow.version == expected_version,
            )
            .values(status=new_status.value, version=ObligationRow.version + 1)
        )
        return result.rowcount

    def add_audit_entry(
        self, obligation_id: str, from_status: Status | None, to_status: Status
    ) -> AuditEntryRow:
        entry = AuditEntryRow(
            obligation_id=obligation_id,
            from_status=from_status.value if from_status is not None else None,
            to_status=to_status.value,
        )
        self.session.add(entry)
        self.session.flush()
        return entry

    def add_document(
        self,
        obligation_id: str,
        filename: str,
        content_type: str,
        storage_path: str,
        size: int,
    ) -> DocumentRow:
        document = DocumentRow(
            obligation_id=obligation_id,
            filename=filename,
            content_type=content_type,
            storage_path=storage_path,
            size=size,
        )
        self.session.add(document)
        self.session.flush()
        return document

    def get_document(self, obligation_id: str, document_id: str) -> DocumentRow | None:
        return self.session.scalars(
            select(DocumentRow).where(
                DocumentRow.id == document_id,
                DocumentRow.obligation_id == obligation_id,
            )
        ).first()

    def delete_document(self, document: DocumentRow) -> None:
        self.session.delete(document)
        self.session.flush()
