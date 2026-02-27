from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.core import (
    AccountType,
    BankAccount,
    BankTransaction,
    BankTxnDirection,
    BankTxnStatus,
    Business,
    CoaAccount,
    RegisterLine,
    RegisterSource,
    RegisterTransaction,
    Workspace,
)

router = APIRouter(tags=["seed"])

WORKSPACE_ID = UUID("00000000-0000-0000-0000-000000000000")
BUSINESS_ID = UUID("11111111-1111-1111-1111-111111111111")
BANK_ACCOUNT_ID = UUID("22222222-2222-2222-2222-222222222222")


def ensure_workspace(db: Session):
    workspace = db.get(Workspace, WORKSPACE_ID)
    if workspace:
        return workspace
    workspace = Workspace(id=WORKSPACE_ID, name="Demo Workspace")
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


def ensure_business(db: Session):
    business = db.get(Business, BUSINESS_ID)
    if business:
        return business
    business = Business(id=BUSINESS_ID, workspace_id=WORKSPACE_ID, name="Demo Business")
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


def ensure_bank_account(db: Session):
    acct = db.get(BankAccount, BANK_ACCOUNT_ID)
    if acct:
        return acct
    acct = BankAccount(
        id=BANK_ACCOUNT_ID,
        business_id=BUSINESS_ID,
        name="Demo Checking",
        institution="Demo Bank",
        account_last4="1234",
        opening_balance=2500,
        is_active=True,
    )
    db.add(acct)
    db.commit()
    db.refresh(acct)
    return acct


def ensure_coa(db: Session):
    existing = db.scalars(select(CoaAccount).where(CoaAccount.business_id == BUSINESS_ID)).all()
    if existing:
        return existing

    accounts = [
        CoaAccount(business_id=BUSINESS_ID, name="Checking", type=AccountType.ASSET),
        CoaAccount(business_id=BUSINESS_ID, name="Sales", type=AccountType.INCOME),
        CoaAccount(business_id=BUSINESS_ID, name="Meals", type=AccountType.EXPENSE),
        CoaAccount(business_id=BUSINESS_ID, name="Office Supplies", type=AccountType.EXPENSE),
    ]
    db.add_all(accounts)
    db.commit()
    return accounts


def ensure_bank_transactions(db: Session):
    existing = db.scalars(select(BankTransaction).where(BankTransaction.business_id == BUSINESS_ID)).all()
    if existing:
        return existing

    txns = [
        BankTransaction(
            business_id=BUSINESS_ID,
            bank_account_id=BANK_ACCOUNT_ID,
            txn_date=date.today(),
            description_raw="SQ *Coffee Shop",
            description_clean="Coffee Shop",
            amount=-12.5,
            direction=BankTxnDirection.DEBIT,
            running_balance=2487.5,
            imported_hash="demo-1",
            status=BankTxnStatus.NEW,
        ),
        BankTransaction(
            business_id=BUSINESS_ID,
            bank_account_id=BANK_ACCOUNT_ID,
            txn_date=date.today(),
            description_raw="ACH Client Payment",
            description_clean="Client Payment",
            amount=450.0,
            direction=BankTxnDirection.CREDIT,
            running_balance=2937.5,
            imported_hash="demo-2",
            status=BankTxnStatus.SUGGESTED,
        ),
    ]
    db.add_all(txns)
    db.commit()
    return txns


def ensure_register(db: Session, coa_accounts):
    existing = db.scalars(
        select(RegisterTransaction).where(RegisterTransaction.business_id == BUSINESS_ID)
    ).all()
    if existing:
        return existing

    checking = next(a for a in coa_accounts if a.name == "Checking")
    meals = next(a for a in coa_accounts if a.name == "Meals")

    txn = RegisterTransaction(
        business_id=BUSINESS_ID,
        txn_date=date.today(),
        payee="Coffee Shop",
        memo="Team meeting",
        source=RegisterSource.BANK_FEED,
        bank_account_id=BANK_ACCOUNT_ID,
    )
    line1 = RegisterLine(
        business_id=BUSINESS_ID,
        account_id=checking.id,
        amount=-12.5,
        line_memo="Coffee",
    )
    line2 = RegisterLine(
        business_id=BUSINESS_ID,
        account_id=meals.id,
        amount=12.5,
        line_memo="Meals",
    )
    txn.lines = [line1, line2]

    db.add(txn)
    db.commit()
    return [txn]


@router.post("/api/seed")
def seed_demo_data(db: Session = Depends(get_db)) -> dict:
    if db.bind is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    ensure_workspace(db)
    ensure_business(db)
    ensure_bank_account(db)
    coa_accounts = ensure_coa(db)
    ensure_bank_transactions(db)
    ensure_register(db, coa_accounts)

    return {
        "workspace_id": str(WORKSPACE_ID),
        "business_id": str(BUSINESS_ID),
        "bank_account_id": str(BANK_ACCOUNT_ID),
        "status": "seeded",
    }
