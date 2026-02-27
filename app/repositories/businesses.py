from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.core import Business


class BusinessRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_workspace(self, workspace_id: UUID) -> Iterable[Business]:
        stmt = select(Business).where(Business.workspace_id == workspace_id).order_by(Business.name.asc())
        return self.db.scalars(stmt).all()

    def get(self, business_id: UUID) -> Optional[Business]:
        return self.db.get(Business, business_id)

    def create(self, business: Business) -> Business:
        self.db.add(business)
        self.db.commit()
        self.db.refresh(business)
        return business

    def update(self, business: Business) -> Business:
        self.db.add(business)
        self.db.commit()
        self.db.refresh(business)
        return business

    def delete(self, business: Business) -> None:
        self.db.delete(business)
        self.db.commit()
