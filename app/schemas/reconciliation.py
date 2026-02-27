from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.core import ReconciliationStatus


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ReconciliationCreate(APIModel):
    bank_account_id: UUID
    statement_start: date
    statement_end: date
    beginning_balance: float
    ending_balance: float


class ReconciliationItemCreate(APIModel):
    register_transaction_id: UUID
    cleared_amount: float
    cleared_date: date


class ReconciliationItemOut(ReconciliationItemCreate):
    id: UUID
    business_id: UUID


class ReconciliationSessionOut(APIModel):
    id: UUID
    business_id: UUID
    bank_account_id: UUID
    statement_start: date
    statement_end: date
    beginning_balance: float
    ending_balance: float
    status: ReconciliationStatus
    created_at: datetime
    closed_at: Optional[datetime] = None
    items: List[ReconciliationItemOut] = []
