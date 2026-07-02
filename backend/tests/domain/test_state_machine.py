from __future__ import annotations

import pytest

from app.domain.errors import InvalidTransition
from app.domain.obligation import Status
from app.domain.state_machine import (
    allowed_transitions,
    is_allowed,
    validate_transition,
)

ALLOWED = [
    (Status.PENDING, Status.IN_PROGRESS),
    (Status.IN_PROGRESS, Status.SUBMITTED),
    (Status.IN_PROGRESS, Status.PENDING),
    (Status.SUBMITTED, Status.DONE),
    (Status.SUBMITTED, Status.IN_PROGRESS),
    (Status.DONE, Status.IN_PROGRESS),
]

FORBIDDEN = [
    (frm, to)
    for frm in Status
    for to in Status
    if (frm, to) not in ALLOWED
]


@pytest.mark.parametrize(("frm", "to"), ALLOWED)
def test_allowed_transitions_pass(frm: Status, to: Status) -> None:
    validate_transition(frm, to)
    assert is_allowed(frm, to) is True


@pytest.mark.parametrize(("frm", "to"), FORBIDDEN)
def test_forbidden_transitions_raise(frm: Status, to: Status) -> None:
    assert is_allowed(frm, to) is False
    with pytest.raises(InvalidTransition) as exc:
        validate_transition(frm, to)
    assert exc.value.from_status == frm.value
    assert exc.value.to_status == to.value


def test_self_transitions_are_forbidden() -> None:
    for status in Status:
        assert not is_allowed(status, status)


def test_allowed_transitions_sets() -> None:
    assert allowed_transitions(Status.PENDING) == frozenset({Status.IN_PROGRESS})
    assert allowed_transitions(Status.IN_PROGRESS) == frozenset(
        {Status.SUBMITTED, Status.PENDING}
    )
    assert allowed_transitions(Status.SUBMITTED) == frozenset(
        {Status.DONE, Status.IN_PROGRESS}
    )
    assert allowed_transitions(Status.DONE) == frozenset({Status.IN_PROGRESS})
