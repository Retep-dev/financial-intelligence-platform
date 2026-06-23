import pandas as pd


def extract_csv_text(file_path: str) -> str:
    df = pd.read_csv(file_path, dtype=str)

    # Drop completely empty rows
    df = df.dropna(how="all")

    rows = []
    for _, row in df.iterrows():
        row_values = [str(v) if pd.notna(v) else "" for v in row]
        row_text = " | ".join(v.strip() for v in row_values if v.strip())
        if row_text:
            rows.append(row_text)

    return "\n".join(rows)
