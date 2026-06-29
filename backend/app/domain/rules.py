"""Domain invariants that are not part of the state machine itself.

- The document gate: an obligation that `requires_document` cannot move to
  `submitted` without an attached document.
- Overdue derivation: overdue is *computed*, never stored as a status.
"""

from __future__ import annotations

from datetime import date

from app.domain.errors import DocumentRequired
from app.domain.obligation import Obligation, Status

_TERMINAL_FOR_OVERDUE: frozenset[Status] = frozenset({Status.SUBMITTED, Status.DONE})


def is_overdue(obligation: Obligation, today: date) -> bool:
    """An obligation is overdue when its due date has passed and it is neither
    submitted nor done. Derived on read; never persisted."""
    return obligation.due_date < today and obligation.status not in _TERMINAL_FOR_OVERDUE


def assert_document_gate(obligation: Obligation, target: Status) -> None:
    """Block a move to `submitted` when a required document is missing.

    The gate only applies to the `submitted` target; other transitions are
    unaffected by document state.
    """
    if target is Status.SUBMITTED and obligation.requires_document and not obligation.has_document:
        raise DocumentRequired()
