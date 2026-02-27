from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.core import BankMatch


class MatchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, match_id: UUID) -> Optional[BankMatch]:
        return self.db.get(BankMatch, match_id)

    def create(self, match: BankMatch) -> BankMatch:
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match

    def delete(self, match: BankMatch) -> None:
        self.db.delete(match)
        self.db.commit()
