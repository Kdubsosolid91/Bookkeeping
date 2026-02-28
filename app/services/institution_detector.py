import re
from typing import Optional


KNOWN_BANK_HINTS = [
    "BANK",
    "CREDIT UNION",
    "FCU",
    "N.A.",
    "NATIONAL ASSOCIATION",
    "SAVINGS",
]


def detect_institution_name(text: str) -> Optional[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sample = lines[:30]

    for line in sample:
        upper = line.upper()
        if any(hint in upper for hint in KNOWN_BANK_HINTS):
            cleaned = re.sub(r"\s+", " ", line).strip()
            if 3 <= len(cleaned) <= 64:
                return cleaned

    for line in sample:
        if line.isupper() and 3 <= len(line) <= 48:
            return line.title()

    return None
