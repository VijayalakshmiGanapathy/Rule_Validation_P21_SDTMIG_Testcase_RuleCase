from pathlib import Path
import pandas as pd

from app.core.exceptions import FileMissingError, SheetMissingError


def read_excel_sheet(file_path: Path, sheet_name: str, skiprows: int = 0) -> pd.DataFrame:
    if not file_path.exists():
        raise FileMissingError(f"File not found: {file_path}")

    excel_file = pd.ExcelFile(file_path)

    if sheet_name not in excel_file.sheet_names:
        raise SheetMissingError(f"Sheet '{sheet_name}' not found in {file_path.name}")

    return pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skiprows)


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.astype(str).str.strip()
    return df