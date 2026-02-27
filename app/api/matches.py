from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.core import BankMatch, BankTransaction, RegisterTransaction
from app.repositories.matches import MatchRepository
from app.schemas.matches import MatchCreate, MatchOut

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.post("", response_model=MatchOut, status_code=status.HTTP_201_CREATED)
def create_match(payload: MatchCreate, db: Session = Depends(get_db)) -> MatchOut:
    bank_txn = db.get(BankTransaction, payload.bank_transaction_id)
    if not bank_txn:
        raise HTTPException(status_code=404, detail="Bank transaction not found")

    register_txn = db.get(RegisterTransaction, payload.register_transaction_id)
    if not register_txn:
        raise HTTPException(status_code=404, detail="Register transaction not found")

    match = BankMatch(
        business_id=payload.business_id,
        bank_transaction_id=payload.bank_transaction_id,
        register_transaction_id=payload.register_transaction_id,
        match_type=payload.match_type,
    )

    return MatchRepository(db).create(match)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(match_id: str, db: Session = Depends(get_db)) -> None:
    repo = MatchRepository(db)
    match = repo.get(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    repo.delete(match)
    return None
