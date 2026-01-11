from definitions import RAW_DATA_DIR
from pathlib import Path
import pandas as pd

# Create csv and parquet from filtered Heat Stress Masterfile.xlsx

# TODO: Should the input be the CSV or Parquet from 01_convert_formats.py?
INPUT_FILEPATH = RAW_DATA_DIR / "Heat Stress Masterfile May 2024.xlsx"
OUTPUT_STEM = RAW_DATA_DIR / "filtered" / "disco_baa_01_filtered_masterfile"


rows_to_drop_conditions = [
    # Drop males (i.e. rows were sex == 'm' or 'M')
    lambda df: df["sex"].str.lower() == "m",
]

columns_to_drop = [
    # Columns with only 1 unique value
    "State",
    "Breed",
    # "Sensor serial 3 2022",
    # "date start of joining 2023",
    # "sensor serial 3 off 2023",
    "wet_dry_marking_2023",
    "Sensor serial 1 2024",
    "GPS # 2024",
    "LWC_during_joining_2024",
    "sensor serial 3 off 2024",
    "Site",
    "sex",
    "Weaning date 2022",
    "Sensor serial 3 2023",
    "2024 treatment (males)",
    "Sensor serial 2 2024",
    "Date temp logger insterted 2024",
    "Sensor serial 1 off 2024",
    "WT_lambing_2024",
    "WT_marking _2024",
    "Farm",
    "Paddock for 2022 (rams only)",
    "Paddock for 2023 (rams only)",
    "Date end of joining 2023",
    "BLOOD TAKEN 2023",
    "date start of joining 2024",
    "Sensor serial 3 2024",
    "Sensor serial 2 off 2024",
    "BLOOD TAKEN 2024",
    "paddock_lambing_2024",
    "wet_dry_marking_2024",
]


def filter_masterfile(
    input_filepath: Path,
    output_filepath: Path,
    columns_to_drop: list[str] | None = None,
    row_filter_functions: list | None = None,
) -> None:
    """
    Filter a masterfile by dropping specified columns and rows.
    
    Args:
        input_filepath: Path to the input Excel file
        output_filepath: Path to save the output parquet file
        columns_to_drop: List of column names to drop from the dataframe
        row_filter_functions: List of functions that take a dataframe and return a boolean series
                             indicating which rows to drop (True = drop)
    """
    df = pd.read_excel(str(input_filepath), sheet_name="RF Ewe.ram data")
    
    # Drop rows based on specified conditions
    if row_filter_functions is not None:
        for condition in row_filter_functions:
            df = df[~condition(df)]
    
    # Drop specified columns
    if columns_to_drop is not None:
        df = df.drop(columns=columns_to_drop)

    # Convert object columns with mixed types to string to avoid parquet conversion errors
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str)

    # Save the filtered DataFrame to a CSV file
    df.to_csv(output_filepath.with_suffix('.csv'), index=False)
    # Save the filtered DataFrame to a parquet file
    df.to_parquet(output_filepath.with_suffix('.parquet'), index=False)

if __name__ == "__main__":
    filter_masterfile(INPUT_FILEPATH, OUTPUT_STEM, columns_to_drop, rows_to_drop_conditions)