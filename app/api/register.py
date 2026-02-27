from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.core import RegisterLine, RegisterTransaction
from app.repositories.register import RegisterRepository
from app.schemas.register import (
    RegisterLineIn,
    RegisterTransactionCreate,
    RegisterTransactionOut,
    RegisterTransactionUpdate,
)

router = APIRouter(tags=["register"])


def _validate_lines(lines: List[RegisterLineIn]) -> None:
    if not lines:
        raise HTTPException(status_code=400, detail="At least one line is required")
    total = sum(line.amount for line in lines)
    if round(total, 2) != 0:
        raise HTTPException(status_code=400, detail="Register lines must balance to 0")


@router.get("/api/businesses/{business_id}/register", response_model=List[RegisterTransactionOut])
def list_register_transactions(
    business_id: UUID,
    account_id: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> List[RegisterTransactionOut]:
    repo = RegisterRepository(db)
    return list(
        repo.list_by_business(
            business_id=business_id,
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            search=search,
            limit=limit,
            offset=offset,
        )
    )


@router.post("/api/businesses/{business_id}/register", response_model=RegisterTransactionOut, status_code=201)
def create_register_transaction(
    business_id: UUID, payload: RegisterTransactionCreate, db: Session = Depends(get_db)
) -> RegisterTransactionOut:
    _validate_lines(payload.lines)
    repo = RegisterRepository(db)

    register_txn = RegisterTransaction(
        business_id=business_id,
        txn_date=payload.txn_date,
        payee=payload.payee,
        memo=payload.memo,
        source=payload.source,
        bank_account_id=payload.bank_account_id,
    )

    lines = [
        RegisterLine(
            business_id=business_id,
            account_id=line.account_id,
            amount=line.amount,
            class_=line.class_,
            location=line.location,
            line_memo=line.line_memo,
        )
        for line in payload.lines
    ]

    return repo.create(register_txn, lines)


@router.patch("/api/register/{register_transaction_id}", response_model=RegisterTransactionOut)
def update_register_transaction(
    register_transaction_id: UUID, payload: RegisterTransactionUpdate, db: Session = Depends(get_db)
) -> RegisterTransactionOut:
    repo = RegisterRepository(db)
    register_txn = repo.get(register_transaction_id)
    if not register_txn:
        raise HTTPException(status_code=404, detail="Register transaction not found")

    if payload.txn_date is not None:
        register_txn.txn_date = payload.txn_date
    if payload.payee is not None:
        register_txn.payee = payload.payee
    if payload.memo is not None:
        register_txn.memo = payload.memo
    if payload.source is not None:
        register_txn.source = payload.source
    if payload.bank_account_id is not None:
        register_txn.bank_account_id = payload.bank_account_id

    lines = None
    if payload.lines is not None:
        _validate_lines(payload.lines)
        lines = [
            RegisterLine(
                business_id=register_txn.business_id,
                account_id=line.account_id,
                amount=line.amount,
                class_=line.class_,
                location=line.location,
                line_memo=line.line_memo,
            )
            for line in payload.lines
        ]

    return repo.update(register_txn, lines)
