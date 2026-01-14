from pathlib import Path

# Use a smaller 'sample' dataset for quicker iteration, demonstration, testing, 
# examples, etc.
DEMO_MODE = False

if DEMO_MODE:
    SAMPLE_SUFFIX = "_sample"
    # RAW_DATA_SAMPLE_SIZE = ...  # e.g. number of rows to sample
else:
    SAMPLE_SUFFIX = ""
    # RAW_DATA_SAMPLE_SIZE = None  # e.g. use full dataset

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
INCOMING_DATA_DIR = DATA_DIR / "00_incoming"
RAW_DATA_DIR = DATA_DIR / f"01_raw{SAMPLE_SUFFIX}"


INCOMING_COSINOR_ANALYSIS_DIRECTORY = INCOMING_DATA_DIR / "processed_cosinor_output"

INTERIM_DATA_DIR = DATA_DIR / "02_interim"
PROCESSED_DATA_DIR = DATA_DIR / "03_processed"