import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from app.services.ocr import ocr_pdf

try:
    import pdfplumber
except Exception:  # pragma: no cover - optional runtime dependency
    pdfplumber = None


def _parse_date(value: str) -> Optional[date]:
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%m-%d-%y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_amount(token: str) -> Optional[float]:
    raw = token.strip().replace("$", "").replace(",", "")
    if not raw:
        return None
    negative = False
    if raw.startswith("(") and raw.endswith(")"):
        negative = True
        raw = raw[1:-1]
    try:
        value = float(raw)
    except ValueError:
        return None
    return -value if negative else value


def normalize_description(desc: str) -> str:
    prefixes = ["SQ *", "POS ", "ACH ", "ONLINE ", "CHECKCARD ", "PAYPAL *"]
    cleaned = desc.strip()
    for prefix in prefixes:
        if cleaned.upper().startswith(prefix):
            cleaned = cleaned[len(prefix) :].strip()
            break
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


@dataclass
class ParsedTransaction:
    txn_date: date
    description_raw: str
    description_clean: str
    amount: float
    running_balance: Optional[float]
    source_page: Optional[int] = None
    source_row: Optional[int] = None


@dataclass
class ParsedStatementMeta:
    statement_start: Optional[date] = None
    statement_end: Optional[date] = None
    beginning_balance: Optional[float] = None
    ending_balance: Optional[float] = None


DATE_PATTERN = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")
AMOUNT_PATTERN = re.compile(r"\(?\$?-?\d{1,3}(?:,\d{3})*(?:\.\d{2})\)?")
PERIOD_PATTERN = re.compile(
    r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*-\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
)


def extract_text(pdf_path: Path) -> str:
    if pdfplumber is None:
        raise RuntimeError("pdfplumber is required to parse PDFs")

    text_chunks: List[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_chunks.append(page_text)

    return "\n".join(text_chunks)


def extract_text_with_ocr(pdf_path: Path) -> str:
    text = extract_text(pdf_path)
    if text.strip():
        return text
    return ocr_pdf(pdf_path)


def parse_statement_meta(text: str) -> ParsedStatementMeta:
    meta = ParsedStatementMeta()

    match = PERIOD_PATTERN.search(text)
    if match:
        meta.statement_start = _parse_date(match.group(1))
        meta.statement_end = _parse_date(match.group(2))

    for line in text.splitlines():
        if meta.beginning_balance is None and "beginning balance" in line.lower():
            amounts = AMOUNT_PATTERN.findall(line)
            if amounts:
                meta.beginning_balance = _parse_amount(amounts[-1])
        if meta.ending_balance is None and "ending balance" in line.lower():
            amounts = AMOUNT_PATTERN.findall(line)
            if amounts:
                meta.ending_balance = _parse_amount(amounts[-1])

    return meta


def parse_transactions(text: str) -> List[ParsedTransaction]:
    transactions: List[ParsedTransaction] = []

    for line in text.splitlines():
        date_match = DATE_PATTERN.search(line)
        if not date_match:
            continue

        txn_date = _parse_date(date_match.group(1))
        if not txn_date:
            continue

        amounts = [a for a in (AMOUNT_PATTERN.findall(line)) if a.strip()]
        if not amounts:
            continue

        parsed_amounts = [_parse_amount(a) for a in amounts]
        parsed_amounts = [a for a in parsed_amounts if a is not None]
        if not parsed_amounts:
            continue

        amount = parsed_amounts[-1]
        running_balance = None
        if len(parsed_amounts) >= 2:
            amount = parsed_amounts[-2]
            running_balance = parsed_amounts[-1]

        description = line
        if date_match:
            description = line[date_match.end() :]
        if amounts:
            idx = description.find(amounts[0])
            if idx != -1:
                description = description[:idx]

        description_raw = description.strip()
        description_clean = normalize_description(description_raw)

        transactions.append(
            ParsedTransaction(
                txn_date=txn_date,
                description_raw=description_raw,
                description_clean=description_clean,
                amount=amount,
                running_balance=running_balance,
            )
        )

    return transactions


def _extract_tables_from_page(page) -> List[List[str]]:
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "intersection_tolerance": 5,
        "snap_tolerance": 3,
        "join_tolerance": 3,
    }
    table = page.extract_table(table_settings)
    if not table:
        table = page.extract_table()
    if not table:
        return []
    return [[cell.strip() if cell else "" for cell in row] for row in table]


def parse_transactions_from_pdf(pdf_path: Path) -> List[ParsedTransaction]:
    if pdfplumber is None:
        return []

    parsed: List[ParsedTransaction] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            rows = _extract_tables_from_page(page)
            if not rows:
                continue

            for row_index, row in enumerate(rows, start=1):
                row_text = " ".join(cell for cell in row if cell).strip()
                if not row_text:
                    continue

                date_cell = None
                for cell in row:
                    if DATE_PATTERN.search(cell or ""):
                        date_cell = cell
                        break
                if not date_cell:
                    continue

                date_match = DATE_PATTERN.search(date_cell)
                if not date_match:
                    continue

                txn_date = _parse_date(date_match.group(1))
                if not txn_date:
                    continue

                amounts = []
                for cell in row:
                    amounts.extend(AMOUNT_PATTERN.findall(cell or ""))
                amounts = [a for a in amounts if a.strip()]
                parsed_amounts = [_parse_amount(a) for a in amounts]
                parsed_amounts = [a for a in parsed_amounts if a is not None]
                if not parsed_amounts:
                    continue

                amount = parsed_amounts[-1]
                running_balance = None
                if len(parsed_amounts) >= 2:
                    amount = parsed_amounts[-2]
                    running_balance = parsed_amounts[-1]

                desc_parts: List[str] = []
                for cell in row:
                    if not cell:
                        continue
                    if DATE_PATTERN.search(cell):
                        continue
                    if AMOUNT_PATTERN.search(cell):
                        continue
                    desc_parts.append(cell)

                description_raw = " ".join(desc_parts).strip() or row_text
                description_clean = normalize_description(description_raw)

                parsed.append(
                    ParsedTransaction(
                        txn_date=txn_date,
                        description_raw=description_raw,
                        description_clean=description_clean,
                        amount=amount,
                        running_balance=running_balance,
                        source_page=page_index,
                        source_row=row_index,
                    )
                )

    return parsed


def imported_hash(txn_date: date, amount: float, description_clean: str, running_balance: Optional[float]) -> str:
    base = f"{txn_date.isoformat()}|{amount:.2f}|{description_clean}|{running_balance if running_balance is not None else ''}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
