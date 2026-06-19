import pandas as pd


def extract_xlsx_text(file_path: str) -> str:
    sheets = pd.read_excel(file_path, sheet_name=None, dtype=str)

    sections = []

    for sheet_name, df in sheets.items():
        sections.append(f"Sheet: {sheet_name}")

        # Drop completely empty rows and columns
        df = df.dropna(how="all").dropna(axis=1, how="all")

        for _, row in df.iterrows():
            row_values = [str(v) if pd.notna(v) else "" for v in row]
            row_text = " | ".join(v.strip() for v in row_values if v.strip())
            if row_text:
                sections.append(row_text)

    return "\n".join(sections)
