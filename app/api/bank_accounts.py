from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.core import BankAccount
from app.repositories.bank_accounts import BankAccountRepository
from app.schemas.bank_accounts import BankAccountCreate, BankAccountOut, BankAccountUpdate

router = APIRouter(tags=["bank-accounts"])


@router.get("/api/businesses/{business_id}/bank-accounts", response_model=List[BankAccountOut])
def list_bank_accounts(business_id: UUID, db: Session = Depends(get_db)) -> List[BankAccountOut]:
    repo = BankAccountRepository(db)
    return list(repo.list_by_business(business_id))


@router.post("/api/businesses/{business_id}/bank-accounts", response_model=BankAccountOut, status_code=201)
def create_bank_account(
    business_id: UUID, payload: BankAccountCreate, db: Session = Depends(get_db)
) -> BankAccountOut:
    repo = BankAccountRepository(db)
    bank_account = BankAccount(
        business_id=business_id,
        name=payload.name,
        institution=payload.institution,
        account_last4=payload.account_last4,
        opening_balance=payload.opening_balance,
        is_active=payload.is_active,
    )
    return repo.create(bank_account)


@router.patch("/api/bank-accounts/{bank_account_id}", response_model=BankAccountOut)
def update_bank_account(
    bank_account_id: UUID, payload: BankAccountUpdate, db: Session = Depends(get_db)
) -> BankAccountOut:
    repo = BankAccountRepository(db)
    bank_account = repo.get(bank_account_id)
    if not bank_account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    if payload.name is not None:
        bank_account.name = payload.name
    if payload.institution is not None:
        bank_account.institution = payload.institution
    if payload.account_last4 is not None:
        bank_account.account_last4 = payload.account_last4
    if payload.opening_balance is not None:
        bank_account.opening_balance = payload.opening_balance
    if payload.is_active is not None:
        bank_account.is_active = payload.is_active

    return repo.update(bank_account)
