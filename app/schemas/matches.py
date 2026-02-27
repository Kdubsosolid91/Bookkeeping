from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.core import MatchType


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MatchCreate(APIModel):
    business_id: UUID
    bank_transaction_id: UUID
    register_transaction_id: UUID
    match_type: MatchType


class MatchOut(MatchCreate):
    id: UUID
    created_at: datetime
