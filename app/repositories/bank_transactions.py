from datetime import date
from typing import Dict, Iterable, List, Optional
from uuid import UUID

from sqlalchemy import and_, or_, select, update
from sqlalchemy.orm import Session

from app.models.core import BankTransaction, BankTxnStatus


class BankTransactionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_business(
        self,
        business_id: UUID,
        status: Optional[BankTxnStatus] = None,
        bank_account_id: Optional[UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        sort: str = "txn_date_desc",
    ) -> Iterable[BankTransaction]:
        filters = [BankTransaction.business_id == business_id]

        if status is not None:
            filters.append(BankTransaction.status == status)
        if bank_account_id is not None:
            filters.append(BankTransaction.bank_account_id == bank_account_id)
        if date_from is not None:
            filters.append(BankTransaction.txn_date >= date_from)
        if date_to is not None:
            filters.append(BankTransaction.txn_date <= date_to)
        if search:
            like = f"%{search}%"
            filters.append(
                or_(
                    BankTransaction.description_raw.ilike(like),
                    BankTransaction.description_clean.ilike(like),
                )
            )

        stmt = select(BankTransaction).where(and_(*filters))

        if sort == "txn_date_asc":
            stmt = stmt.order_by(BankTransaction.txn_date.asc(), BankTransaction.created_at.asc())
        elif sort == "created_at_desc":
            stmt = stmt.order_by(BankTransaction.created_at.desc())
        else:
            stmt = stmt.order_by(BankTransaction.txn_date.desc(), BankTransaction.created_at.desc())

        stmt = stmt.limit(limit).offset(offset)
        return self.db.scalars(stmt).all()

    def get(self, bank_transaction_id: UUID) -> Optional[BankTransaction]:
        return self.db.get(BankTransaction, bank_transaction_id)

    def update(self, bank_transaction: BankTransaction) -> BankTransaction:
        self.db.add(bank_transaction)
        self.db.commit()
        self.db.refresh(bank_transaction)
        return bank_transaction

    def batch_update(self, ids: List[UUID], fields: Dict) -> List[UUID]:
        if not ids:
            return []

        stmt = (
            update(BankTransaction)
            .where(BankTransaction.id.in_(ids))
            .values(**fields)
            .returning(BankTransaction.id)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return list(result.scalars().all())
