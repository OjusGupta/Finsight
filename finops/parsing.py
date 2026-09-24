from __future__ import annotations

from datetime import date, datetime
import re


_DATE_FORMATS = ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d")
_DATE_PATTERNS = (
    re.compile(r"^\d{2}-\d{2}-\d{4}$"),
    re.compile(r"^\d{2}/\d{2}/\d{4}$"),
    re.compile(r"^\d{4}-\d{2}-\d{2}$"),
)


def parse_business_date(value: object) -> date:
    text = str(value).strip() if value is not None else ""
    for pattern, date_format in zip(_DATE_PATTERNS, _DATE_FORMATS):
        if pattern.fullmatch(text):
            try:
                return datetime.strptime(text, date_format).date()
            except ValueError as exc:
                raise ValueError("bad_date") from exc
    raise ValueError("bad_date")
