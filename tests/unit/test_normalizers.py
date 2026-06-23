from financial_intelligence_platform.services.ingestion.preprocessing.date_normalizer import normalize_dates
from financial_intelligence_platform.services.ingestion.preprocessing.currency_normalizer import normalize_currencies
from financial_intelligence_platform.services.ingestion.preprocessing.numeric_normalizer import normalize_numbers


def test_normalize_dates_us_format():
    text = "The report was filed on 01/15/2024."
    result = normalize_dates(text)
    assert "2024-01-15" in result


def test_normalize_dates_iso_format():
    text = "Meeting scheduled for 2024-03-22."
    result = normalize_dates(text)
    assert "2024-03-22" in result


def test_normalize_currencies():
    text = "Revenue was $1,000,000 and costs were €500,000."
    result = normalize_currencies(text)
    assert "USD 1,000,000" in result
    assert "EUR 500,000" in result


def test_normalize_numbers_parentheses():
    text = "The loss was (123.45) this quarter."
    result = normalize_numbers(text)
    assert "-123.45" in result


def test_normalize_numbers_magnitude_suffix():
    text = "Market cap reached 1.5B."
    result = normalize_numbers(text)
    assert "1500000000" in result


def test_normalize_numbers_thousands_separator():
    text = "Total assets: 12,345,678.90"
    result = normalize_numbers(text)
    assert "12345678.90" in result
