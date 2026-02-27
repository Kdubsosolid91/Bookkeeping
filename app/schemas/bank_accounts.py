from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BankAccountBase(APIModel):
    name: str
    institution: Optional[str] = None
    account_last4: Optional[str] = None
    opening_balance: float = 0.0
    is_active: bool = True


class BankAccountCreate(BankAccountBase):
    pass


class BankAccountUpdate(APIModel):
    name: Optional[str] = None
    institution: Optional[str] = None
    account_last4: Optional[str] = None
    opening_balance: Optional[float] = None
    is_active: Optional[bool] = None


class BankAccountOut(BankAccountBase):
    id: UUID
    business_id: UUID
