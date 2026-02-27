from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.core import AccountType


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CoaAccountBase(APIModel):
    name: str
    type: AccountType
    code: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: bool = True


class CoaAccountCreate(CoaAccountBase):
    pass


class CoaAccountUpdate(APIModel):
    name: Optional[str] = None
    type: Optional[AccountType] = None
    code: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class CoaAccountOut(CoaAccountBase):
    id: UUID
    business_id: UUID
