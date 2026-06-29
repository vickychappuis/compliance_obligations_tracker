"""The obligation state machine — the single source of truth for transitions.

Allowed transitions (any transition not listed here is invalid):

    pending    -> in_progress
    in_progress -> submitted | pending
    submitted  -> done | in_progress   (rejection / rework)
    done       -> in_progress          (reopen)
"""

from __future__ import annotations

from app.domain.errors import InvalidTransition
from app.domain.obligation import Status

_TRANSITIONS: dict[Status, frozenset[Status]] = {
    Status.PENDING: frozenset({Status.IN_PROGRESS}),
    Status.IN_PROGRESS: frozenset({Status.SUBMITTED, Status.PENDING}),
    Status.SUBMITTED: frozenset({Status.DONE, Status.IN_PROGRESS}),
    Status.DONE: frozenset({Status.IN_PROGRESS}),
}


def allowed_transitions(from_status: Status) -> frozenset[Status]:
    """Return the set of statuses reachable from `from_status` in one step."""
    return _TRANSITIONS.get(from_status, frozenset())


def is_allowed(from_status: Status, to_status: Status) -> bool:
    return to_status in allowed_transitions(from_status)


def validate_transition(from_status: Status, to_status: Status) -> None:
    """Raise `InvalidTransition` if the transition is not permitted."""
    if not is_allowed(from_status, to_status):
        raise InvalidTransition(from_status.value, to_status.value)
