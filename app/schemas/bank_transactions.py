from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.core import BankTxnDirection, BankTxnStatus


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BankTransactionOut(APIModel):
    id: UUID
    business_id: UUID
    bank_account_id: UUID
    pdf_upload_id: Optional[UUID] = None
    txn_date: date
    description_raw: str
    description_clean: str
    amount: float
    direction: BankTxnDirection
    running_balance: Optional[float] = None
    imported_hash: str
    status: BankTxnStatus
    suggested_vendor: Optional[str] = None
    suggested_account_id: Optional[UUID] = None
    suggested_confidence: Optional[float] = None
    source_page: Optional[int] = None
    source_row: Optional[int] = None


class BankTransactionUpdate(APIModel):
    status: Optional[BankTxnStatus] = None
    suggested_vendor: Optional[str] = None
    suggested_account_id: Optional[UUID] = None
    suggested_confidence: Optional[float] = Field(default=None, ge=0, le=1)


class BankTransactionBatchUpdate(APIModel):
    ids: List[UUID]
    status: Optional[BankTxnStatus] = None
    suggested_vendor: Optional[str] = None
    suggested_account_id: Optional[UUID] = None
    suggested_confidence: Optional[float] = Field(default=None, ge=0, le=1)


class BankTransactionBatchResult(APIModel):
    updated_count: int
    updated_ids: List[UUID]
