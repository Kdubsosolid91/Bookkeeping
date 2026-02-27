from pathlib import Path
from typing import List

try:
    from pdf2image import convert_from_path
except Exception:  # pragma: no cover - optional runtime dependency
    convert_from_path = None

try:
    import pytesseract
except Exception:  # pragma: no cover - optional runtime dependency
    pytesseract = None


def ocr_pdf(pdf_path: Path, dpi: int = 300) -> str:
    if convert_from_path is None or pytesseract is None:
        raise RuntimeError("pdf2image and pytesseract are required for OCR")

    images = convert_from_path(str(pdf_path), dpi=dpi)
    text_chunks: List[str] = []
    for img in images:
        text_chunks.append(pytesseract.image_to_string(img))
    return "\n".join(text_chunks)
