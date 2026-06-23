import re
from typing import List, Dict, Tuple


def extract_citation_markers(text: str) -> List[str]:
    """Extract chunk_id values from [citation: <chunk_id>] markers."""
    pattern = r"\[citation:\s*([^\]]+)\]"
    return re.findall(pattern, text)


def split_answer_and_sources(text: str) -> Tuple[str, List[str]]:
    """Split the answer text from any 'Sources:' section."""
    parts = re.split(r"\n\nSources:\s*", text, flags=re.IGNORECASE)
    answer = parts[0].strip()
    sources = []

    if len(parts) > 1:
        sources = [s.strip() for s in parts[1].split("\n") if s.strip()]

    return answer, sources


def normalize_citation_text(text: str) -> str:
    """Replace citation markers with superscript-style markers for display."""
    seen = {}
    counter = [0]

    def replace_marker(match: re.Match) -> str:
        chunk_id = match.group(1).strip()
        if chunk_id not in seen:
            counter[0] += 1
            seen[chunk_id] = counter[0]
        return f"[{seen[chunk_id]}]"

    return re.sub(r"\[citation:\s*([^\]]+)\]", replace_marker, text)
