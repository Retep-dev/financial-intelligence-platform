from bs4 import BeautifulSoup


def extract_html_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Extract text from meaningful tags
    lines = []
    for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th"]):
        text = tag.get_text(strip=True)
        if text:
            lines.append(text)

    return "\n".join(lines)
