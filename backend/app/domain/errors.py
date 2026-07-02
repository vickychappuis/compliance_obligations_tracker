"""Domain-level exceptions.

These carry domain meaning only. Mapping them to HTTP status codes happens in
the route/exception-handler layer, never here.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain errors."""


class InvalidTransition(DomainError):
    """Raised when a state transition is not allowed by the state machine."""

    def __init__(self, from_status: str, to_status: str) -> None:
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(f"Invalid transition: {from_status} -> {to_status}")


class DocumentRequired(DomainError):
    """Raised when moving to `submitted` without a required attached document."""

    def __init__(self) -> None:
        super().__init__(
            "A document is required before this obligation can be submitted"
        )


class InvalidDocument(DomainError):
    """Raised when an uploaded document violates the size or type policy."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)


class NotFound(DomainError):
    """Raised when a requested obligation does not exist."""

    def __init__(self, obligation_id: str) -> None:
        self.obligation_id = obligation_id
        super().__init__(f"Obligation not found: {obligation_id}")


class VersionConflict(DomainError):
    """Raised when an optimistic-lock version check fails (concurrent update)."""

    def __init__(self) -> None:
        super().__init__(
            "The obligation was modified by another request; reload and retry"
        )
