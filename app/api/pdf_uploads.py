from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.deps import get_db
from app.models.core import BankAccount, BankTransaction, BankTxnDirection, BankTxnStatus, PdfParseStatus, PdfUpload
from app.repositories.pdf_uploads import PdfUploadRepository
from app.schemas.pdf_uploads import PdfUploadOut, PdfUploadStatusOut
from app.settings import settings
from app.services.pdf_parser import (
    imported_hash,
    parse_statement_meta,
    parse_transactions,
    parse_transactions_from_pdf,
    extract_text_with_ocr,
)
from app.services.institution_detector import detect_institution_name

router = APIRouter(tags=["pdf-uploads"])


def get_storage_dir() -> Path:
    base = Path(settings.storage_dir)
    uploads = base / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    return uploads


def _get_or_create_bank_account(db: Session, business_id: UUID, name: str) -> BankAccount:
    stmt = select(BankAccount).where(
        BankAccount.business_id == business_id,
        BankAccount.name == name,
    )
    existing = db.scalars(stmt).first()
    if existing:
        return existing

    bank_account = BankAccount(
        business_id=business_id,
        name=name,
        institution=name,
        is_active=True,
    )
    db.add(bank_account)
    db.commit()
    db.refresh(bank_account)
    return bank_account


@router.post("/api/bank-accounts/{bank_account_id}/uploads", response_model=PdfUploadOut, status_code=201)
def upload_pdf_statement(
    bank_account_id: UUID,
    business_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> PdfUploadOut:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    storage_dir = get_storage_dir()
    target_path = storage_dir / file.filename

    with target_path.open("wb") as buffer:
        buffer.write(file.file.read())

    repo = PdfUploadRepository(db)
    upload = PdfUpload(
        business_id=business_id,
        bank_account_id=bank_account_id,
        filename=file.filename,
        storage_path=str(target_path),
        parse_status=PdfParseStatus.PENDING,
    )
    return repo.create(upload)


@router.post("/api/businesses/{business_id}/uploads", response_model=PdfUploadOut, status_code=201)
def upload_pdf_statement_detect_bank(
    business_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> PdfUploadOut:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    storage_dir = get_storage_dir()
    target_path = storage_dir / file.filename

    with target_path.open("wb") as buffer:
        buffer.write(file.file.read())

    text = extract_text_with_ocr(target_path)
    detected_name = detect_institution_name(text) or "Unknown Bank"
    bank_account = _get_or_create_bank_account(db, business_id, detected_name)

    repo = PdfUploadRepository(db)
    upload = PdfUpload(
        business_id=business_id,
        bank_account_id=bank_account.id,
        filename=file.filename,
        storage_path=str(target_path),
        parse_status=PdfParseStatus.PENDING,
    )
    return repo.create(upload)


@router.get("/api/uploads/{upload_id}/status", response_model=PdfUploadStatusOut)
def get_upload_status(upload_id: UUID, db: Session = Depends(get_db)) -> PdfUploadStatusOut:
    repo = PdfUploadRepository(db)
    upload = repo.get(upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return PdfUploadStatusOut(
        id=upload.id,
        parse_status=upload.parse_status,
        statement_start=upload.statement_start,
        statement_end=upload.statement_end,
        beginning_balance=upload.beginning_balance,
        ending_balance=upload.ending_balance,
    )


@router.post("/api/uploads/{upload_id}/parse", response_model=PdfUploadOut)
def parse_upload(upload_id: UUID, db: Session = Depends(get_db)) -> PdfUploadOut:
    repo = PdfUploadRepository(db)
    upload = repo.get(upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    pdf_path = Path(upload.storage_path)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Stored PDF not found")

    try:
        text = extract_text_with_ocr(pdf_path)
        if not text.strip():
            raise ValueError("No extractable text found in PDF")

        meta = parse_statement_meta(text)
        parsed = parse_transactions_from_pdf(pdf_path)
        if not parsed:
            parsed = parse_transactions(text)
        if not parsed:
            raise ValueError("No transactions parsed from PDF")

        upload.statement_start = meta.statement_start
        upload.statement_end = meta.statement_end
        upload.beginning_balance = meta.beginning_balance
        upload.ending_balance = meta.ending_balance

        for item in parsed:
            amount = float(item.amount)
            direction = BankTxnDirection.DEBIT if amount < 0 else BankTxnDirection.CREDIT
            txn = BankTransaction(
                business_id=upload.business_id,
                bank_account_id=upload.bank_account_id,
                pdf_upload_id=upload.id,
                txn_date=item.txn_date,
                description_raw=item.description_raw,
                description_clean=item.description_clean,
                amount=amount,
                direction=direction,
                running_balance=item.running_balance,
                imported_hash=imported_hash(
                    item.txn_date,
                    amount,
                    item.description_clean,
                    item.running_balance,
                ),
                status=BankTxnStatus.NEW,
                source_page=item.source_page,
                source_row=item.source_row,
            )
            try:
                with db.begin_nested():
                    db.add(txn)
                    db.flush()
            except IntegrityError:
                continue

        upload.parse_status = PdfParseStatus.PARSED
        db.add(upload)
        db.commit()
        db.refresh(upload)
        return upload
    except Exception as exc:
        upload.parse_status = PdfParseStatus.FAILED
        db.add(upload)
        db.commit()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
