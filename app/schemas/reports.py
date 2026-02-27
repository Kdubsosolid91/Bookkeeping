from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ReportLine(APIModel):
    account_id: UUID
    account_name: str
    account_type: str
    total: float


class PnLReportOut(APIModel):
    from_date: date
    to_date: date
    lines: List[ReportLine]


class BalanceSheetReportOut(APIModel):
    as_of: date
    lines: List[ReportLine]


class DrilldownLine(APIModel):
    register_transaction_id: UUID
    txn_date: date
    payee: Optional[str] = None
    memo: Optional[str] = None
    amount: float


class DrilldownReportOut(APIModel):
    account_id: UUID
    from_date: date
    to_date: date
    lines: List[DrilldownLine]
