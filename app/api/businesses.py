from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.core import Business
from app.repositories.businesses import BusinessRepository
from app.schemas.common import BusinessCreate, BusinessOut, BusinessUpdate

router = APIRouter(prefix="/api/businesses", tags=["businesses"])


@router.get("", response_model=List[BusinessOut])
def list_businesses(workspace_id: UUID, db: Session = Depends(get_db)) -> List[BusinessOut]:
    repo = BusinessRepository(db)
    return list(repo.list_by_workspace(workspace_id))


@router.post("", response_model=BusinessOut, status_code=status.HTTP_201_CREATED)
def create_business(payload: BusinessCreate, db: Session = Depends(get_db)) -> BusinessOut:
    repo = BusinessRepository(db)
    business = Business(
        workspace_id=payload.workspace_id,
        name=payload.name,
        base_currency=payload.base_currency,
        close_lock_date=payload.close_lock_date,
    )
    return repo.create(business)


@router.patch("/{business_id}", response_model=BusinessOut)
def update_business(
    business_id: UUID, payload: BusinessUpdate, db: Session = Depends(get_db)
) -> BusinessOut:
    repo = BusinessRepository(db)
    business = repo.get(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    if payload.name is not None:
        business.name = payload.name
    if payload.base_currency is not None:
        business.base_currency = payload.base_currency
    if payload.close_lock_date is not None:
        business.close_lock_date = payload.close_lock_date

    return repo.update(business)


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business(business_id: UUID, db: Session = Depends(get_db)) -> None:
    repo = BusinessRepository(db)
    business = repo.get(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    repo.delete(business)
    return None
