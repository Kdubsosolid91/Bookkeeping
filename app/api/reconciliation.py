from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.core import ReconciliationItem, ReconciliationSession, ReconciliationStatus
from app.repositories.reconciliation import ReconciliationRepository
from app.schemas.reconciliation import (
    ReconciliationCreate,
    ReconciliationItemCreate,
    ReconciliationItemOut,
    ReconciliationSessionOut,
)

router = APIRouter(tags=["reconciliation"])


@router.post(
    "/api/businesses/{business_id}/reconciliations",
    response_model=ReconciliationSessionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_reconciliation_session(
    business_id: UUID, payload: ReconciliationCreate, db: Session = Depends(get_db)
) -> ReconciliationSessionOut:
    repo = ReconciliationRepository(db)

    session = ReconciliationSession(
        business_id=business_id,
        bank_account_id=payload.bank_account_id,
        statement_start=payload.statement_start,
        statement_end=payload.statement_end,
        beginning_balance=payload.beginning_balance,
        ending_balance=payload.ending_balance,
        status=ReconciliationStatus.OPEN,
    )

    session = repo.create_session(session)
    return ReconciliationSessionOut(
        id=session.id,
        business_id=session.business_id,
        bank_account_id=session.bank_account_id,
        statement_start=session.statement_start,
        statement_end=session.statement_end,
        beginning_balance=session.beginning_balance,
        ending_balance=session.ending_balance,
        status=session.status,
        created_at=session.created_at,
        closed_at=session.closed_at,
        items=[],
    )


@router.get("/api/reconciliations/{session_id}", response_model=ReconciliationSessionOut)
def get_reconciliation_session(session_id: UUID, db: Session = Depends(get_db)) -> ReconciliationSessionOut:
    repo = ReconciliationRepository(db)
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Reconciliation session not found")

    items = repo.list_items(session_id)
    return ReconciliationSessionOut(
        id=session.id,
        business_id=session.business_id,
        bank_account_id=session.bank_account_id,
        statement_start=session.statement_start,
        statement_end=session.statement_end,
        beginning_balance=session.beginning_balance,
        ending_balance=session.ending_balance,
        status=session.status,
        created_at=session.created_at,
        closed_at=session.closed_at,
        items=[
            ReconciliationItemOut(
                id=item.id,
                business_id=item.business_id,
                register_transaction_id=item.register_transaction_id,
                cleared_amount=float(item.cleared_amount),
                cleared_date=item.cleared_date,
            )
            for item in items
        ],
    )


@router.post("/api/reconciliations/{session_id}/add-item", response_model=ReconciliationItemOut)
def add_reconciliation_item(
    session_id: UUID, payload: ReconciliationItemCreate, db: Session = Depends(get_db)
) -> ReconciliationItemOut:
    repo = ReconciliationRepository(db)
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Reconciliation session not found")
    if session.status == ReconciliationStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Reconciliation session is closed")

    item = ReconciliationItem(
        business_id=session.business_id,
        reconciliation_session_id=session_id,
        register_transaction_id=payload.register_transaction_id,
        cleared_amount=payload.cleared_amount,
        cleared_date=payload.cleared_date,
    )

    item = repo.add_item(item)
    return ReconciliationItemOut(
        id=item.id,
        business_id=item.business_id,
        register_transaction_id=item.register_transaction_id,
        cleared_amount=float(item.cleared_amount),
        cleared_date=item.cleared_date,
    )


@router.post("/api/reconciliations/{session_id}/close", response_model=ReconciliationSessionOut)
def close_reconciliation_session(
    session_id: UUID, db: Session = Depends(get_db)
) -> ReconciliationSessionOut:
    repo = ReconciliationRepository(db)
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Reconciliation session not found")

    session.status = ReconciliationStatus.CLOSED
    session.closed_at = datetime.utcnow()
    session = repo.close_session(session)

    items = repo.list_items(session_id)
    return ReconciliationSessionOut(
        id=session.id,
        business_id=session.business_id,
        bank_account_id=session.bank_account_id,
        statement_start=session.statement_start,
        statement_end=session.statement_end,
        beginning_balance=session.beginning_balance,
        ending_balance=session.ending_balance,
        status=session.status,
        created_at=session.created_at,
        closed_at=session.closed_at,
        items=[
            ReconciliationItemOut(
                id=item.id,
                business_id=item.business_id,
                register_transaction_id=item.register_transaction_id,
                cleared_amount=float(item.cleared_amount),
                cleared_date=item.cleared_date,
            )
            for item in items
        ],
    )
