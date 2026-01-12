"""Ingest Heat Stress Masterfile Excel and extract the relevant sheet.

This module ingests the masterfile (.xlsx), reads the target sheet
(default: 'RF Ewe.ram data'), and persists the ingested data to CSV and
Parquet. Object columns are cast to strings to ensure Parquet compatibility.

Import and call `ingest_masterfile_sheet()` from other modules, or run this
file directly to perform the ingestion with defaults.
"""
from definitions import RAW_DATA_DIR
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

# inputs
HEAT_STRESS_MASTERFILE_MAY_2024_xlsx = "Heat Stress Masterfile May 2024.xlsx"
SHEET_NAME = "RF Ewe.ram data"

# default outputs for script execution
DEFAULT_OUTPUT_CSV = RAW_DATA_DIR / f"{Path(HEAT_STRESS_MASTERFILE_MAY_2024_xlsx).stem} - {SHEET_NAME}.csv"
DEFAULT_OUTPUT_PARQUET = RAW_DATA_DIR / f"{Path(HEAT_STRESS_MASTERFILE_MAY_2024_xlsx).stem} - {SHEET_NAME}.parquet"


def ingest_masterfile_sheet(
    input_filepath: Path,
    sheet_name: str = SHEET_NAME,
    output_csv_path: Optional[Path] = None,
    output_parquet_path: Optional[Path] = None,
) -> Tuple[Path, Path]:
    """Ingest an Excel masterfile sheet and persist to CSV and Parquet.

    Args:
        input_filepath: Path to the masterfile Excel to ingest.
        sheet_name: Name of the sheet to extract.
        output_csv_path: Optional path for the CSV artifact. If None, a default
            path will be created in RAW_DATA_DIR as "<input-stem> - <sheet>.csv".
        output_parquet_path: Optional path for the Parquet artifact. If None, a
            default path will be created in RAW_DATA_DIR as
            "<input-stem> - <sheet>.parquet".

    Returns:
        A tuple of (csv_path, parquet_path).
    """
    # Determine output paths
    input_stem = Path(input_filepath).stem
    csv_path = output_csv_path or (RAW_DATA_DIR / f"{input_stem} - {sheet_name}.csv")
    parquet_path = output_parquet_path or (RAW_DATA_DIR / f"{input_stem} - {sheet_name}.parquet")

    # Ingest: read Excel and extract target sheet
    df = pd.read_excel(str(input_filepath), sheet_name=sheet_name)

    # Persist ingestion artifacts
    df.to_csv(csv_path, index=False)

    # Ensure Parquet compatibility by casting object columns to string
    df_w_strings = df.copy()
    for col in df.select_dtypes(include=["object"]).columns:
        df_w_strings[col] = df_w_strings[col].astype(str)
    df_w_strings.to_parquet(parquet_path, index=False)

    return csv_path, parquet_path

# Backward-compatible alias (deprecated): prefer `ingest_masterfile_sheet`
convert_formats = ingest_masterfile_sheet


if __name__ == "__main__":
    # Script entrypoint: ingest the default masterfile sheet and write artifacts
    input_xlsx = RAW_DATA_DIR / HEAT_STRESS_MASTERFILE_MAY_2024_xlsx
    ingest_masterfile_sheet(
        input_filepath=input_xlsx,
        sheet_name=SHEET_NAME,
        output_csv_path=DEFAULT_OUTPUT_CSV,
        output_parquet_path=DEFAULT_OUTPUT_PARQUET,
    )