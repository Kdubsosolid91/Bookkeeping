from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.core import PdfParseStatus


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PdfUploadCreate(APIModel):
    filename: str
    storage_path: str
    statement_start: Optional[date] = None
    statement_end: Optional[date] = None
    beginning_balance: Optional[float] = None
    ending_balance: Optional[float] = None


class PdfUploadOut(APIModel):
    id: UUID
    business_id: UUID
    bank_account_id: UUID
    filename: str
    storage_path: str
    statement_start: Optional[date] = None
    statement_end: Optional[date] = None
    beginning_balance: Optional[float] = None
    ending_balance: Optional[float] = None
    parse_status: PdfParseStatus
    created_at: datetime


class PdfUploadStatusOut(APIModel):
    id: UUID
    parse_status: PdfParseStatus
    statement_start: Optional[date] = None
    statement_end: Optional[date] = None
    beginning_balance: Optional[float] = None
    ending_balance: Optional[float] = None
