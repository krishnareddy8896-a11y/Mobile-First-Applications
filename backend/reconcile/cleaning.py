import re
from decimal import Decimal, InvalidOperation


def normalize_ref(raw):
    if raw is None:
        return None
    match = re.search(r"\d+", str(raw))
    return f"REC-{match.group()}" if match else None


def parse_amount(raw):
    if raw is None:
        return None
    text = str(raw).strip().replace(",", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None
