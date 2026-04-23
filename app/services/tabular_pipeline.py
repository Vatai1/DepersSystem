from pathlib import Path

import pandas as pd

from app.services.text_pipeline import depersonalize_text


def process_csv(file_path: str, mode: str = "replace") -> tuple[str, list[dict]]:
    df = pd.read_csv(file_path)
    all_entities = []

    for col in df.columns:
        if df[col].dtype == object:
            results = df[col].astype(str).apply(lambda x: depersonalize_text(x, mode))
            df[col] = results.apply(lambda r: r["processed_text"])
            for r in results:
                all_entities.extend(r["entities"])

    out = file_path.replace(".csv", "_depersonalized.csv")
    df.to_csv(out, index=False)
    return out, all_entities


def process_excel(file_path: str, mode: str = "replace") -> tuple[str, list[dict]]:
    df = pd.read_excel(file_path)
    all_entities = []

    for col in df.columns:
        if df[col].dtype == object:
            results = df[col].astype(str).apply(lambda x: depersonalize_text(x, mode))
            df[col] = results.apply(lambda r: r["processed_text"])
            for r in results:
                all_entities.extend(r["entities"])

    out = file_path.replace(".xlsx", "_depersonalized.xlsx").replace(".xls", "_depersonalized.xlsx")
    df.to_excel(out, index=False)
    return out, all_entities


def process_tabular(file_path: str, mode: str = "replace") -> tuple[str, list[dict]]:
    ext = Path(file_path).suffix.lower()
    if ext == ".csv":
        return process_csv(file_path, mode)
    elif ext in (".xlsx", ".xls"):
        return process_excel(file_path, mode)
    raise ValueError(f"Unsupported tabular format: {ext}")
