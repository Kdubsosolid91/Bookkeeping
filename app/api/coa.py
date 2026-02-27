from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.core import CoaAccount
from app.repositories.coa_accounts import CoaAccountRepository
from app.schemas.coa import CoaAccountCreate, CoaAccountOut, CoaAccountUpdate

router = APIRouter(tags=["coa"])


@router.get("/api/businesses/{business_id}/coa", response_model=List[CoaAccountOut])
def list_coa_accounts(business_id: UUID, db: Session = Depends(get_db)) -> List[CoaAccountOut]:
    repo = CoaAccountRepository(db)
    return list(repo.list_by_business(business_id))


@router.post("/api/businesses/{business_id}/coa", response_model=CoaAccountOut, status_code=201)
def create_coa_account(
    business_id: UUID, payload: CoaAccountCreate, db: Session = Depends(get_db)
) -> CoaAccountOut:
    repo = CoaAccountRepository(db)
    account = CoaAccount(
        business_id=business_id,
        name=payload.name,
        type=payload.type,
        code=payload.code,
        parent_id=payload.parent_id,
        is_active=payload.is_active,
    )
    return repo.create(account)


@router.patch("/api/coa/{account_id}", response_model=CoaAccountOut)
def update_coa_account(
    account_id: UUID, payload: CoaAccountUpdate, db: Session = Depends(get_db)
) -> CoaAccountOut:
    repo = CoaAccountRepository(db)
    account = repo.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="COA account not found")

    if payload.name is not None:
        account.name = payload.name
    if payload.type is not None:
        account.type = payload.type
    if payload.code is not None:
        account.code = payload.code
    if payload.parent_id is not None:
        account.parent_id = payload.parent_id
    if payload.is_active is not None:
        account.is_active = payload.is_active

    return repo.update(account)
