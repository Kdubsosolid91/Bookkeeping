import argparse
import json
from pathlib import Path

from app.services.pdf_parser import (
    extract_text_with_ocr,
    parse_statement_meta,
    parse_transactions,
    parse_transactions_from_pdf,
)


def parse_pdf(pdf_path: Path) -> dict:
    text = extract_text_with_ocr(pdf_path)
    meta = parse_statement_meta(text)
    parsed = parse_transactions_from_pdf(pdf_path)
    if not parsed:
        parsed = parse_transactions(text)

    return {
        "file": str(pdf_path),
        "statement_meta": {
            "statement_start": meta.statement_start.isoformat() if meta.statement_start else None,
            "statement_end": meta.statement_end.isoformat() if meta.statement_end else None,
            "beginning_balance": meta.beginning_balance,
            "ending_balance": meta.ending_balance,
        },
        "transactions": [
            {
                "txn_date": item.txn_date.isoformat(),
                "description_raw": item.description_raw,
                "description_clean": item.description_clean,
                "amount": item.amount,
                "running_balance": item.running_balance,
                "source_page": item.source_page,
                "source_row": item.source_row,
            }
            for item in parsed
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse sample PDFs and output JSON")
    parser.add_argument("--input", default="sample_pdfs", help="Directory containing PDFs")
    parser.add_argument("--output", default="outputs/parse_results.json", help="Output JSON path")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results = []
    for pdf_path in sorted(input_dir.glob("*.pdf")):
        results.append(parse_pdf(pdf_path))

    output_path.write_text(json.dumps(results, indent=2))
    print(f"Parsed {len(results)} PDF(s) -> {output_path}")


if __name__ == "__main__":
    main()
