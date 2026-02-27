from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.repositories.reports import ReportsRepository
from app.schemas.reports import BalanceSheetReportOut, DrilldownReportOut, PnLReportOut

router = APIRouter(tags=["reports"])


@router.get("/api/businesses/{business_id}/reports/pnl", response_model=PnLReportOut)
def get_pnl_report(
    business_id: UUID,
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    db: Session = Depends(get_db),
) -> PnLReportOut:
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from must be <= to")

    repo = ReportsRepository(db)
    lines = repo.pnl(business_id=business_id, from_date=from_date, to_date=to_date)
    return PnLReportOut(from_date=from_date, to_date=to_date, lines=lines)


@router.get("/api/businesses/{business_id}/reports/balance-sheet", response_model=BalanceSheetReportOut)
def get_balance_sheet_report(
    business_id: UUID,
    as_of: date = Query(..., alias="asOf"),
    db: Session = Depends(get_db),
) -> BalanceSheetReportOut:
    repo = ReportsRepository(db)
    lines = repo.balance_sheet(business_id=business_id, as_of=as_of)
    return BalanceSheetReportOut(as_of=as_of, lines=lines)


@router.get("/api/businesses/{business_id}/reports/drilldown", response_model=DrilldownReportOut)
def get_drilldown_report(
    business_id: UUID,
    account_id: UUID,
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    db: Session = Depends(get_db),
) -> DrilldownReportOut:
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from must be <= to")

    repo = ReportsRepository(db)
    lines = repo.drilldown(
        business_id=business_id,
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
    )
    return DrilldownReportOut(
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
        lines=lines,
    )
