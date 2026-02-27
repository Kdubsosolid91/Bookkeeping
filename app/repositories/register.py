from datetime import date
from typing import Iterable, List, Optional
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.core import RegisterLine, RegisterTransaction


class RegisterRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_business(
        self,
        business_id: UUID,
        account_id: Optional[UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Iterable[RegisterTransaction]:
        filters = [RegisterTransaction.business_id == business_id]

        if account_id is not None:
            filters.append(RegisterLine.account_id == account_id)
        if date_from is not None:
            filters.append(RegisterTransaction.txn_date >= date_from)
        if date_to is not None:
            filters.append(RegisterTransaction.txn_date <= date_to)
        if search:
            like = f"%{search}%"
            filters.append(
                or_(
                    RegisterTransaction.payee.ilike(like),
                    RegisterTransaction.memo.ilike(like),
                )
            )

        stmt = (
            select(RegisterTransaction)
            .outerjoin(RegisterLine)
            .where(and_(*filters))
            .options(selectinload(RegisterTransaction.lines))
            .order_by(RegisterTransaction.txn_date.desc(), RegisterTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return self.db.scalars(stmt).unique().all()

    def get(self, register_transaction_id: UUID) -> Optional[RegisterTransaction]:
        stmt = (
            select(RegisterTransaction)
            .where(RegisterTransaction.id == register_transaction_id)
            .options(selectinload(RegisterTransaction.lines))
        )
        return self.db.scalars(stmt).first()

    def create(self, register_transaction: RegisterTransaction, lines: List[RegisterLine]) -> RegisterTransaction:
        register_transaction.lines = lines
        self.db.add(register_transaction)
        self.db.commit()
        self.db.refresh(register_transaction)
        return register_transaction

    def update(
        self,
        register_transaction: RegisterTransaction,
        lines: Optional[List[RegisterLine]] = None,
    ) -> RegisterTransaction:
        if lines is not None:
            register_transaction.lines = lines
        self.db.add(register_transaction)
        self.db.commit()
        self.db.refresh(register_transaction)
        return register_transaction
