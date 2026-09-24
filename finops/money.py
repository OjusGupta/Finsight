from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


CENT = Decimal("0.01")
_AMOUNT_RE = re.compile(
    r"^(?:\d+(?:\.\d{1,2})?|\d{1,3}(?:,\d{2})*,\d{3}(?:\.\d{1,2})?)$"
)


def parse_money(value: object) -> Decimal:
    if value is None or isinstance(value, bool):
        raise ValueError("bad_amount")

    text = str(value).strip()
    if not text:
        raise ValueError("bad_amount")

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1].strip()
    elif text.endswith("-"):
        negative = True
        text = text[:-1].strip()

    if text.lower().startswith("rs."):
        text = text[3:].strip()
    elif text.lower().startswith("rs "):
        text = text[2:].strip()

    if not _AMOUNT_RE.fullmatch(text):
        raise ValueError("bad_amount")

    try:
        amount = Decimal(text.replace(",", ""))
    except InvalidOperation as exc:
        raise ValueError("bad_amount") from exc

    if negative:
        amount = -amount
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def format_money(value: Decimal) -> str:
    return f"{value.quantize(CENT, rounding=ROUND_HALF_UP):.2f}"
