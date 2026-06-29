from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.data.database import get_session
from app.domain.obligation import ObligationType, Status
from app.schemas.obligation import (
    DocumentRequest,
    ObligationCreateRequest,
    ObligationDetailResponse,
    ObligationPatchRequest,
    ObligationResponse,
    SummaryResponse,
    TransitionRequest,
    to_detail_response,
    to_response,
    to_summary_response,
)
from app.services.obligation_service import (
    ObligationCreate,
    ObligationPatch,
    ObligationService,
)

router = APIRouter(prefix="/obligations", tags=["obligations"])


def get_service(session: Session = Depends(get_session)) -> ObligationService:
    return ObligationService(session)


@router.get("", response_model=list[ObligationResponse])
def list_obligations(
    status: Status | None = None,
    type: ObligationType | None = None,
    owner: str | None = None,
    overdue: bool | None = None,
    service: ObligationService = Depends(get_service),
) -> list[ObligationResponse]:
    views = service.list_views(status=status, type=type, owner=owner, overdue=overdue)
    return [to_response(v) for v in views]


@router.get("/summary", response_model=SummaryResponse)
def get_summary(service: ObligationService = Depends(get_service)) -> SummaryResponse:
    return to_summary_response(service.summary())


@router.post("", response_model=ObligationDetailResponse, status_code=status.HTTP_201_CREATED)
def create_obligation(
    payload: ObligationCreateRequest,
    service: ObligationService = Depends(get_service),
) -> ObligationDetailResponse:
    view = service.create(
        ObligationCreate(
            type=payload.type,
            title=payload.title,
            description=payload.description,
            due_date=payload.due_date,
            owner=payload.owner,
            requires_document=payload.requires_document,
            company_tax_id=payload.company_tax_id,
        )
    )
    return to_detail_response(view)


@router.get("/{obligation_id}", response_model=ObligationDetailResponse)
def get_obligation(
    obligation_id: str,
    service: ObligationService = Depends(get_service),
) -> ObligationDetailResponse:
    return to_detail_response(service.get_view(obligation_id))


@router.patch("/{obligation_id}", response_model=ObligationDetailResponse)
def patch_obligation(
    obligation_id: str,
    payload: ObligationPatchRequest,
    service: ObligationService = Depends(get_service),
) -> ObligationDetailResponse:
    view = service.update_fields(
        obligation_id,
        ObligationPatch(
            title=payload.title,
            description=payload.description,
            type=payload.type,
            due_date=payload.due_date,
            owner=payload.owner,
            requires_document=payload.requires_document,
            company_tax_id=payload.company_tax_id,
        ),
    )
    return to_detail_response(view)


@router.post("/{obligation_id}/transition", response_model=ObligationDetailResponse)
def transition_obligation(
    obligation_id: str,
    payload: TransitionRequest,
    service: ObligationService = Depends(get_service),
) -> ObligationDetailResponse:
    view = service.change_state(
        obligation_id, payload.target_status, payload.expected_version
    )
    return to_detail_response(view)


@router.post("/{obligation_id}/document", response_model=ObligationDetailResponse)
def attach_document(
    obligation_id: str,
    payload: DocumentRequest,
    service: ObligationService = Depends(get_service),
) -> ObligationDetailResponse:
    view = service.attach_document(obligation_id, payload.filename, payload.content_type)
    return to_detail_response(view)
