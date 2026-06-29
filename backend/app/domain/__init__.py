"""Pure domain layer.

This package is intentionally free of FastAPI, Pydantic-request, and database
concerns. Everything here is testable without HTTP or a database. Domain rules
(state machine, document gate, overdue derivation) live here and nowhere else.
"""
