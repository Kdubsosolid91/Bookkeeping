from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BusinessBase(APIModel):
    name: str
    base_currency: str = "USD"
    close_lock_date: Optional[date] = None


class BusinessCreate(BusinessBase):
    workspace_id: UUID


class BusinessUpdate(APIModel):
    name: Optional[str] = None
    base_currency: Optional[str] = None
    close_lock_date: Optional[date] = None


class BusinessOut(BusinessBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
