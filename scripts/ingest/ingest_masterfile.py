"""Ingest Heat Stress Masterfile Excel and extract the relevant sheet.

This module ingests the masterfile (.xlsx), reads the target sheet
(default: 'RF Ewe.ram data'), and persists the ingested data to CSV and
Parquet. Object columns are cast to strings to ensure Parquet compatibility.

Import and call `ingest_masterfile_sheet()` from other modules, or run this
file directly to perform the ingestion with defaults.
"""
from definitions import RAW_DATA_DIR, INCOMING_DATA_DIR

from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

# inputs
HEAT_STRESS_MASTERFILE_MAY_2024_XLSX = INCOMING_DATA_DIR / "Heat Stress Masterfile May 2024.xlsx"
SHEET_NAME = "RF Ewe.ram data"

# default outputs for script execution
DEFAULT_OUTPUT_CSV = RAW_DATA_DIR / f"{HEAT_STRESS_MASTERFILE_MAY_2024_XLSX.stem} - {SHEET_NAME}.csv"
DEFAULT_OUTPUT_PARQUET = RAW_DATA_DIR / f"{HEAT_STRESS_MASTERFILE_MAY_2024_XLSX.stem} - {SHEET_NAME}.parquet"


def clean_temp_logger_ids(df):
    
    columns = [
        "Temp logger # 2022",
        "Temp logger # 2023",
        "Temp logger # 2024",
    ]

    # Values that should be ignored when checking for unexpected fractional values
    allowed_fractional_values = [
        0.7,  # Known data entry artifact; row will be dropped
    ]

    def _to_nullable_int(col_name: str, series: pd.Series) -> pd.Series:
        numeric = pd.to_numeric(series, errors="coerce")

        # Alert on fractional values before conversion (excluding allowed values)
        fractional_mask = numeric.notna() & (numeric % 1 != 0)
        fractional_mask = fractional_mask & ~numeric.isin(allowed_fractional_values)
        
        if fractional_mask.any():
            sample_indices = numeric.loc[fractional_mask].head(5).index.tolist()
            sample_values = numeric.loc[fractional_mask].head(5).tolist()
            raise ValueError(
                f"Column '{col_name}' has {fractional_mask.sum()} fractional values; "
                f"first examples (index -> value): {list(zip(sample_indices, sample_values))}"
            )

        return numeric.astype("Int64")

    # Identify rows with allowed fractional values (to be dropped)
    rows_to_drop = pd.Series([False] * len(df), index=df.index)
    for col in columns:
        if col in df.columns:
            numeric = pd.to_numeric(df[col], errors="coerce")
            rows_to_drop |= numeric.isin(allowed_fractional_values)
    
    dropped_rows = df[rows_to_drop].copy()
    df = df[~rows_to_drop].reset_index(drop=True)
    
    # convert columns to nullable int
    for col in columns:
        if col in df.columns:
            df[col] = _to_nullable_int(col, df[col])
    
    return df, dropped_rows


def clean(df) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df, dropped_rows = clean_temp_logger_ids(df)

    return df, dropped_rows


def document_anomalies(df: pd.DataFrame, anomalies_path: Path) -> None:
    """Analyze dataframe for known anomalies and write details to a text file.

    Current checks:
    - Rows with a 2023 pregnancy scan result but missing 2023 scan date.
    - Specific EID "940 110009540002" flagged if present with the above condition.
    """
    lines: list[str] = []
    lines.append("Data Ingestion Anomalies\n")
    lines.append("=========================\n\n")

    # Check: 2023 preg scan has result but no date
    preg_result_col = "Preg scan 2023"
    preg_date_col = "date of preg scanning 2023"
    eid_col = "EID"

    if preg_result_col in df.columns and preg_date_col in df.columns:
        mask = df[preg_result_col].astype(str).str.strip().ne("") & df[preg_date_col].isna()
        count = int(mask.sum())
        lines.append(
            f"Rows with '{preg_result_col}' present but missing '{preg_date_col}': {count}\n"
        )
        if count:
            # Include a small sample for quick inspection
            cols_to_show = [c for c in [eid_col, preg_result_col, preg_date_col] if c in df.columns]
            sample = df.loc[mask, cols_to_show].head(10)
            lines.append("Sample (up to 10 rows):\n")
            lines.append(sample.to_string(index=True) + "\n\n")

            # Specific EID of interest
            if eid_col in df.columns:
                specific_eid = "940 110009540002"
                specific_mask = mask & (df[eid_col] == specific_eid)
                if specific_mask.any():
                    lines.append(
                        f"Specific EID '{specific_eid}' exhibits anomaly. Details:\n"
                    )
                    lines.append(
                        df.loc[specific_mask, cols_to_show].to_string(index=True) + "\n\n"
                    )
    else:
        lines.append(
            f"Columns not found to check preg-scan anomaly: present={preg_result_col in df.columns}, date_col_present={preg_date_col in df.columns}\n\n"
        )

    # Write anomalies report if there is any content
    if lines:
        with open(anomalies_path, "w", encoding="utf-8") as f:
            f.writelines(lines)


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

    df, dropped_rows = clean(df)

    # Document dropped rows
    if not dropped_rows.empty:
        comments_path = RAW_DATA_DIR / f"{HEAT_STRESS_MASTERFILE_MAY_2024_XLSX.stem} - {SHEET_NAME} - DROPPED_ROWS.txt"
        with open(comments_path, "w", encoding="utf-8") as f:
            f.write("Rows Dropped During Data Ingestion\n")
            f.write("===================================\n\n")
            f.write(f"Total rows dropped: {len(dropped_rows)}\n\n")
            f.write("Reason: Rows with invalid fractional values in temp logger columns\n")
            f.write("- 0.7: Known data entry artifact; row(s) removed as data quality issue\n\n")
            f.write("Dropped row details:\n")
            f.write(dropped_rows.to_string())

    # Document anomalies (non-dropping issues)
    anomalies_path = RAW_DATA_DIR / f"{HEAT_STRESS_MASTERFILE_MAY_2024_XLSX.stem} - {SHEET_NAME} - ANOMALIES.txt"
    document_anomalies(df, anomalies_path)

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
    ingest_masterfile_sheet(
        input_filepath=HEAT_STRESS_MASTERFILE_MAY_2024_XLSX,
        sheet_name=SHEET_NAME,
        output_csv_path=DEFAULT_OUTPUT_CSV,
        output_parquet_path=DEFAULT_OUTPUT_PARQUET,
    )