"""The Obligation entity and its enumerations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class ObligationType(str, Enum):
    ANNUAL_REPORT = "annual_report"
    FRANCHISE_TAX = "franchise_tax"
    BOI_REPORT = "boi_report"
    REGISTERED_AGENT_RENEWAL = "registered_agent_renewal"


class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    DONE = "done"


@dataclass
class Obligation:
    """Domain representation of a compliance obligation.

    `has_document` is a fact the domain needs to enforce the document gate; it is
    populated by the service from persistence. `company_tax_id` is stored in full
    here - masking is a presentation concern handled at the schema layer, never
    in the domain.
    """

    id: str | None
    type: ObligationType
    title: str
    description: str
    status: Status
    due_date: date
    owner: str
    requires_document: bool
    has_document: bool
    company_tax_id: str
