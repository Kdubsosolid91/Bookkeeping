from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.core import CoaAccount


class CoaAccountRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_business(self, business_id: UUID) -> Iterable[CoaAccount]:
        stmt = (
            select(CoaAccount)
            .where(CoaAccount.business_id == business_id)
            .order_by(CoaAccount.name.asc())
        )
        return self.db.scalars(stmt).all()

    def get(self, account_id: UUID) -> Optional[CoaAccount]:
        return self.db.get(CoaAccount, account_id)

    def create(self, account: CoaAccount) -> CoaAccount:
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update(self, account: CoaAccount) -> CoaAccount:
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
