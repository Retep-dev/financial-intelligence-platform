import re
from datetime import datetime
from typing import List, Tuple


# Common date patterns found in financial documents
DATE_PATTERNS: List[Tuple[str, str]] = [
    (r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", r"\1/\2/\3"),       # MM/DD/YYYY
    (r"\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b", r"\1-\2-\3"),         # YYYY-MM-DD
    (r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{2,4})\b", r"\1 \2 \3"),
    (r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{2,4})\b", r"\1 \2, \3"),
]

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}


def normalize_dates(text: str) -> str:
    """Convert recognized date strings to ISO format (YYYY-MM-DD) where unambiguous."""

    def replace_date(match: re.Match) -> str:
        original = match.group(0)
        parts = re.split(r"[\s,/-]+", original.lower())

        # Text month format
        if any(part in MONTHS for part in parts):
            day = None
            month = None
            year = None
            for part in parts:
                if part in MONTHS:
                    month = MONTHS[part]
                elif part.isdigit() and day is None:
                    day = int(part)
                elif part.isdigit() and year is None:
                    year = int(part)
            if month and day and year:
                if year < 100:
                    year += 2000 if year < 50 else 1900
                try:
                    return datetime(year, month, day).strftime("%Y-%m-%d")
                except ValueError:
                    return original
            return original

        # Numeric format
        numeric = [p for p in parts if p.isdigit()]
        if len(numeric) == 3:
            a, b, c = map(int, numeric)

            # YYYY-MM-DD
            if a > 1900:
                year, month, day = a, b, c
            # MM/DD/YYYY
            elif c > 1900 or (c < 100 and len(str(c)) in (2, 4)):
                month, day, year = a, b, c
                if year < 100:
                    year += 2000 if year < 50 else 1900
            else:
                return original

            try:
                return datetime(year, month, day).strftime("%Y-%m-%d")
            except ValueError:
                return original

        return original

    # Normalize month names first so regex matching is simpler
    for pattern, _ in DATE_PATTERNS:
        text = re.sub(pattern, replace_date, text, flags=re.IGNORECASE)

    return text
