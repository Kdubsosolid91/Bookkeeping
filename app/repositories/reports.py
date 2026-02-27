from datetime import date
from typing import List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.core import AccountType, CoaAccount, RegisterLine, RegisterTransaction
from app.schemas.reports import DrilldownLine, ReportLine


class ReportsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def pnl(self, business_id: UUID, from_date: date, to_date: date) -> List[ReportLine]:
        stmt = (
            select(
                CoaAccount.id.label("account_id"),
                CoaAccount.name.label("account_name"),
                CoaAccount.type.label("account_type"),
                func.sum(RegisterLine.amount).label("total"),
            )
            .join(RegisterLine, RegisterLine.account_id == CoaAccount.id)
            .join(RegisterTransaction, RegisterTransaction.id == RegisterLine.register_transaction_id)
            .where(
                CoaAccount.business_id == business_id,
                CoaAccount.type.in_(
                    [
                        AccountType.INCOME,
                        AccountType.EXPENSE,
                        AccountType.COGS,
                        AccountType.OTHER_INCOME,
                        AccountType.OTHER_EXPENSE,
                    ]
                ),
                RegisterTransaction.txn_date >= from_date,
                RegisterTransaction.txn_date <= to_date,
            )
            .group_by(CoaAccount.id)
            .order_by(CoaAccount.name.asc())
        )

        results = self.db.execute(stmt).all()
        return [
            ReportLine(
                account_id=row.account_id,
                account_name=row.account_name,
                account_type=row.account_type.value,
                total=float(row.total or 0),
            )
            for row in results
        ]

    def balance_sheet(self, business_id: UUID, as_of: date) -> List[ReportLine]:
        stmt = (
            select(
                CoaAccount.id.label("account_id"),
                CoaAccount.name.label("account_name"),
                CoaAccount.type.label("account_type"),
                func.sum(RegisterLine.amount).label("total"),
            )
            .join(RegisterLine, RegisterLine.account_id == CoaAccount.id)
            .join(RegisterTransaction, RegisterTransaction.id == RegisterLine.register_transaction_id)
            .where(
                CoaAccount.business_id == business_id,
                CoaAccount.type.in_(
                    [
                        AccountType.ASSET,
                        AccountType.LIABILITY,
                        AccountType.EQUITY,
                    ]
                ),
                RegisterTransaction.txn_date <= as_of,
            )
            .group_by(CoaAccount.id)
            .order_by(CoaAccount.name.asc())
        )

        results = self.db.execute(stmt).all()
        return [
            ReportLine(
                account_id=row.account_id,
                account_name=row.account_name,
                account_type=row.account_type.value,
                total=float(row.total or 0),
            )
            for row in results
        ]

    def drilldown(
        self, business_id: UUID, account_id: UUID, from_date: date, to_date: date
    ) -> List[DrilldownLine]:
        stmt = (
            select(
                RegisterTransaction.id.label("register_transaction_id"),
                RegisterTransaction.txn_date,
                RegisterTransaction.payee,
                RegisterTransaction.memo,
                RegisterLine.amount,
            )
            .join(RegisterTransaction, RegisterTransaction.id == RegisterLine.register_transaction_id)
            .where(
                RegisterTransaction.business_id == business_id,
                RegisterLine.account_id == account_id,
                RegisterTransaction.txn_date >= from_date,
                RegisterTransaction.txn_date <= to_date,
            )
            .order_by(RegisterTransaction.txn_date.desc(), RegisterTransaction.created_at.desc())
        )

        results = self.db.execute(stmt).all()
        return [
            DrilldownLine(
                register_transaction_id=row.register_transaction_id,
                txn_date=row.txn_date,
                payee=row.payee,
                memo=row.memo,
                amount=float(row.amount),
            )
            for row in results
        ]
