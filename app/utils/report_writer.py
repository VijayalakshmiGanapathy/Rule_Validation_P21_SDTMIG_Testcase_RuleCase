from pathlib import Path
import pandas as pd


def write_excel_report(df: pd.DataFrame, output_path: Path) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Validation Report")

        worksheet = writer.sheets["Validation Report"]
        worksheet.freeze_panes = "A2"

        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = max_length + 3

    return str(output_path)