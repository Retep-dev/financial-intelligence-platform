import re


def normalize_numbers(text: str) -> str:
    """Normalize numeric representations for consistency.

    Examples:
        1,234,567.89  ->  1234567.89
        (123.45)      ->  -123.45
        1.2M          ->  1200000
        1.2K          ->  1200
        1.2B          ->  1200000000
    """

    # Negative numbers in parentheses: (123.45) -> -123.45
    text = re.sub(r"\(([\d,]+(?:\.\d+)?)\)", r"-\1", text)

    # Magnitude suffixes
    def expand_magnitude(match: re.Match) -> str:
        number = match.group(1).replace(",", "")
        suffix = match.group(2).upper()
        value = float(number)

        multipliers = {
            "K": 1_000,
            "M": 1_000_000,
            "B": 1_000_000_000,
            "T": 1_000_000_000_000,
        }

        if suffix in multipliers:
            value *= multipliers[suffix]

        # Format as integer if whole number, else decimal
        if value == int(value):
            return str(int(value))
        return str(value)

    text = re.sub(
        r"([\d,]+(?:\.\d+)?)\s*(K|M|B|T)\b",
        expand_magnitude,
        text,
        flags=re.IGNORECASE
    )

    # Remove thousands separators to create machine-readable numbers
    def remove_commas(match: re.Match) -> str:
        return match.group(0).replace(",", "")

    text = re.sub(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b", remove_commas, text)

    return text
