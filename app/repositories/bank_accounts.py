from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.core import BankAccount


class BankAccountRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_business(self, business_id: UUID) -> Iterable[BankAccount]:
        stmt = (
            select(BankAccount)
            .where(BankAccount.business_id == business_id)
            .order_by(BankAccount.name.asc())
        )
        return self.db.scalars(stmt).all()

    def get(self, bank_account_id: UUID) -> Optional[BankAccount]:
        return self.db.get(BankAccount, bank_account_id)

    def create(self, bank_account: BankAccount) -> BankAccount:
        self.db.add(bank_account)
        self.db.commit()
        self.db.refresh(bank_account)
        return bank_account

    def update(self, bank_account: BankAccount) -> BankAccount:
        self.db.add(bank_account)
        self.db.commit()
        self.db.refresh(bank_account)
        return bank_account
