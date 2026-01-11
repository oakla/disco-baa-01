"""Convert Heat Stress Masterfile from Excel format to CSV and Parquet.

This script reads the 'RF Ewe.ram data' sheet from the Heat Stress Masterfile
May 2024 Excel file and converts it to both CSV and Parquet formats for easier
data processing. Object columns are converted to strings for Parquet compatibility.
"""
from definitions import RAW_DATA_DIR
from pathlib import Path

import pandas as pd

# inputs
HEAT_STRESS_MASTERFILE_MAY_2024_xlsx = "Heat Stress Masterfile May 2024.xlsx"
SHEET_NAME = "RF Ewe.ram data"

# outputs
OUTPUT_CSV = RAW_DATA_DIR / f"{Path(HEAT_STRESS_MASTERFILE_MAY_2024_xlsx).stem} - {SHEET_NAME}.csv"
OUTPUT_PARQUET = RAW_DATA_DIR / f"{Path(HEAT_STRESS_MASTERFILE_MAY_2024_xlsx).stem} - {SHEET_NAME}.parquet"


df = pd.read_excel(str(RAW_DATA_DIR / HEAT_STRESS_MASTERFILE_MAY_2024_xlsx), sheet_name=SHEET_NAME)

# Save as CSV
df.to_csv(OUTPUT_CSV, index=False)

# Save as Parquet
# Convert object columns with mixed types to string to avoid parquet conversion errors
df_w_strings = df.copy()
for col in df.select_dtypes(include=['object']).columns:
    df_w_strings[col] = df_w_strings[col].astype(str)
df_w_strings.to_parquet(OUTPUT_PARQUET, index=False)