import re


CURRENCY_SYMBOLS = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₹": "INR",
    "CHF": "CHF",
}


def normalize_currencies(text: str) -> str:
    """Normalize currency symbols and abbreviations.

    Examples:
        $1,234.56  ->  USD 1,234.56
        €100       ->  EUR 100
    """

    def replace_currency(match: re.Match) -> str:
        symbol = match.group(1)
        amount = match.group(2)
        code = CURRENCY_SYMBOLS.get(symbol, symbol)
        return f"{code} {amount}"

    # Symbol before amount
    text = re.sub(
        r"([$€£¥₹])\s*([\d,]+(?:\.\d{2})?)",
        replace_currency,
        text
    )

    # Abbreviations like USD 100, EUR100
    text = re.sub(
        r"\b(USD|EUR|GBP|JPY|INR|CHF)\s*([\d,]+(?:\.\d{2})?)",
        r"\1 \2",
        text,
        flags=re.IGNORECASE
    )

    return text
