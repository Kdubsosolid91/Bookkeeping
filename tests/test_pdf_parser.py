from pathlib import Path

from app.services.pdf_parser import extract_text_with_ocr, parse_transactions, parse_transactions_from_pdf


def test_parse_sample_pdfs_has_transactions() -> None:
    sample_dir = Path(__file__).resolve().parents[1] / "sample_pdfs"
    if not sample_dir.exists():
        return

    pdfs = list(sample_dir.glob("*.pdf"))
    if not pdfs:
        return

    for pdf_path in pdfs:
        text = extract_text_with_ocr(pdf_path)
        parsed = parse_transactions_from_pdf(pdf_path)
        if not parsed:
            parsed = parse_transactions(text)
        assert parsed, f"No transactions parsed from {pdf_path}"
