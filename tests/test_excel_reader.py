from pathlib import Path

import pandas as pd
import pytest

from app.core.exceptions import FileMissingError
from app.utils.excel_reader import clean_columns, read_excel_sheet


def test_clean_columns():
    df = pd.DataFrame(columns=[" Rule ID ", " Domain "])

    cleaned = clean_columns(df)

    assert "Rule ID" in cleaned.columns
    assert "Domain" in cleaned.columns


def test_missing_file():
    with pytest.raises(FileMissingError):
        read_excel_sheet(
            Path("does_not_exist.xlsx"),
            sheet_name="Sheet1",
        )