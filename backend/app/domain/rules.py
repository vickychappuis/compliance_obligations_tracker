"""Domain invariants that are not part of the state machine itself.

- The document gate: an obligation that `requires_document` cannot move to
  `submitted` without an attached document.
- Overdue derivation: overdue is *computed*, never stored as a status.
"""

from __future__ import annotations

from datetime import date

from app.domain.errors import DocumentRequired, InvalidDocument
from app.domain.obligation import Obligation, Status

_TERMINAL_FOR_OVERDUE: frozenset[Status] = frozenset({Status.SUBMITTED, Status.DONE})


def is_overdue(obligation: Obligation, today: date) -> bool:
    """An obligation is overdue when its due date has passed and it is neither
    submitted nor done. Derived on read; never persisted."""
    return (
        obligation.due_date < today and obligation.status not in _TERMINAL_FOR_OVERDUE
    )


def assert_document_gate(obligation: Obligation, target: Status) -> None:
    """Block a move to `submitted` when a required document is missing.

    The gate only applies to the `submitted` target; other transitions are
    unaffected by document state.
    """
    if (
        target is Status.SUBMITTED
        and obligation.requires_document
        and not obligation.has_document
    ):
        raise DocumentRequired()


def assert_document_allowed(
    *,
    size: int,
    content_type: str,
    max_bytes: int,
    allowed_content_types: frozenset[str],
) -> None:
    """Validate an uploaded document against the size and type policy.

    Limits are injected (like `today` in `is_overdue`) so the rule stays pure
    and testable without config. A `content_type` matches when it is listed
    exactly or when its family wildcard (e.g. `image/*`) is allowed.
    """
    if size <= 0:
        raise InvalidDocument("The uploaded file is empty")
    if size > max_bytes:
        max_mb = max_bytes / (1024 * 1024)
        raise InvalidDocument(f"File exceeds the maximum size of {max_mb:g} MB")
    if not _content_type_allowed(content_type, allowed_content_types):
        raise InvalidDocument(f"Unsupported file type: {content_type}")


def _content_type_allowed(content_type: str, allowed: frozenset[str]) -> bool:
    if content_type in allowed:
        return True
    family = content_type.split("/", 1)[0]
    return f"{family}/*" in allowed
