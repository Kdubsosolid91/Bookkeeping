from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.core import ReconciliationItem, ReconciliationSession


class ReconciliationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_session(self, session_id: UUID) -> Optional[ReconciliationSession]:
        return self.db.get(ReconciliationSession, session_id)

    def list_items(self, session_id: UUID) -> List[ReconciliationItem]:
        stmt = select(ReconciliationItem).where(
            ReconciliationItem.reconciliation_session_id == session_id
        )
        return self.db.scalars(stmt).all()

    def create_session(self, session: ReconciliationSession) -> ReconciliationSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_item(self, item: ReconciliationItem) -> ReconciliationItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def close_session(self, session: ReconciliationSession) -> ReconciliationSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
