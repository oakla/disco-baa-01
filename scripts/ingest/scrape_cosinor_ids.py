from pathlib import Path
import pandas as pd

from definitions import INCOMING_COSINOR_ANALYSIS_DIRECTORY, INTERIM_DATA_DIR

#!/usr/bin/env python3

OUTPUT_NAME = "cosinor_IDs"
OUTPUT_DIR = INTERIM_DATA_DIR


def extract_prefixes(directory: Path, prefix_len: int = 5) -> tuple[list[str], list[str]]:
    files = [p.name for p in directory.iterdir() if p.is_file()]
    prefixes = [name[:prefix_len] for name in files]
    return files, prefixes

def main():
    src_dir = INCOMING_COSINOR_ANALYSIS_DIRECTORY  # change to your target directory
    files, prefixes = extract_prefixes(src_dir, prefix_len=5)
    
    out_base = OUTPUT_DIR
    out_base.mkdir(parents=True, exist_ok=True)

    csv_path = out_base / f"{OUTPUT_NAME}.csv"
    parquet_path = out_base / f"{OUTPUT_NAME}.parquet"

    df = pd.DataFrame({"cosinor_id": prefixes, "source_filename": files})
    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    print(f"Wrote {csv_path} and {parquet_path}")

if __name__ == "__main__":
    main()