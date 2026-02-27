from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.core import RegisterSource


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RegisterLineIn(APIModel):
    account_id: UUID
    amount: float
    class_: Optional[str] = Field(default=None, alias="class")
    location: Optional[str] = None
    line_memo: Optional[str] = None


class RegisterLineOut(RegisterLineIn):
    id: UUID
    business_id: UUID


class RegisterTransactionBase(APIModel):
    txn_date: date
    payee: Optional[str] = None
    memo: Optional[str] = None
    source: RegisterSource
    bank_account_id: Optional[UUID] = None


class RegisterTransactionCreate(RegisterTransactionBase):
    lines: List[RegisterLineIn]


class RegisterTransactionUpdate(APIModel):
    txn_date: Optional[date] = None
    payee: Optional[str] = None
    memo: Optional[str] = None
    source: Optional[RegisterSource] = None
    bank_account_id: Optional[UUID] = None
    lines: Optional[List[RegisterLineIn]] = None


class RegisterTransactionOut(RegisterTransactionBase):
    id: UUID
    business_id: UUID
    lines: List[RegisterLineOut]
