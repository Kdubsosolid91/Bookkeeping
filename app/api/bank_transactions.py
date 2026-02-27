from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.core import BankTxnStatus
from app.repositories.bank_transactions import BankTransactionRepository
from app.schemas.bank_transactions import (
    BankTransactionBatchResult,
    BankTransactionBatchUpdate,
    BankTransactionOut,
    BankTransactionUpdate,
)

router = APIRouter(tags=["bank-transactions"])


@router.get("/api/businesses/{business_id}/bank-transactions", response_model=List[BankTransactionOut])
def list_bank_transactions(
    business_id: UUID,
    status: Optional[BankTxnStatus] = None,
    bank_account_id: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: Optional[str] = Query("txn_date_desc"),
    db: Session = Depends(get_db),
) -> List[BankTransactionOut]:
    repo = BankTransactionRepository(db)
    return list(
        repo.list_by_business(
            business_id=business_id,
            status=status,
            bank_account_id=bank_account_id,
            date_from=date_from,
            date_to=date_to,
            search=search,
            limit=limit,
            offset=offset,
            sort=sort or "txn_date_desc",
        )
    )


def apply_suggested_defaults(payload: BankTransactionUpdate) -> BankTransactionUpdate:
    if payload.status is None and (
        payload.suggested_vendor is not None
        or payload.suggested_account_id is not None
        or payload.suggested_confidence is not None
    ):
        payload.status = BankTxnStatus.SUGGESTED
    return payload


@router.patch("/api/bank-transactions/{bank_transaction_id}", response_model=BankTransactionOut)
def update_bank_transaction(
    bank_transaction_id: UUID, payload: BankTransactionUpdate, db: Session = Depends(get_db)
) -> BankTransactionOut:
    repo = BankTransactionRepository(db)
    bank_txn = repo.get(bank_transaction_id)
    if not bank_txn:
        raise HTTPException(status_code=404, detail="Bank transaction not found")

    payload = apply_suggested_defaults(payload)

    if payload.status is not None:
        bank_txn.status = payload.status
    if payload.suggested_vendor is not None:
        bank_txn.suggested_vendor = payload.suggested_vendor
    if payload.suggested_account_id is not None:
        bank_txn.suggested_account_id = payload.suggested_account_id
    if payload.suggested_confidence is not None:
        bank_txn.suggested_confidence = payload.suggested_confidence

    return repo.update(bank_txn)


@router.post("/api/bank-transactions/batch", response_model=BankTransactionBatchResult)
def batch_update_bank_transactions(
    payload: BankTransactionBatchUpdate, db: Session = Depends(get_db)
) -> BankTransactionBatchResult:
    if not payload.ids:
        raise HTTPException(status_code=400, detail="ids is required")

    if payload.status is None and (
        payload.suggested_vendor is not None
        or payload.suggested_account_id is not None
        or payload.suggested_confidence is not None
    ):
        payload.status = BankTxnStatus.SUGGESTED

    fields = {}
    if payload.status is not None:
        fields["status"] = payload.status
    if payload.suggested_vendor is not None:
        fields["suggested_vendor"] = payload.suggested_vendor
    if payload.suggested_account_id is not None:
        fields["suggested_account_id"] = payload.suggested_account_id
    if payload.suggested_confidence is not None:
        fields["suggested_confidence"] = payload.suggested_confidence

    updated_ids = BankTransactionRepository(db).batch_update(payload.ids, fields)

    return BankTransactionBatchResult(updated_count=len(updated_ids), updated_ids=updated_ids)
