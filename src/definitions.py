from pathlib import Path

DEMO_MODE = False



# NOTE: Some files overwritten if DEMO_MODE is True
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
INCOMING_DATA_DIR = DATA_DIR / "00_incoming"
RAW_DATA_DIR = DATA_DIR / "01_raw"

INTERIM_DATA_DIR = DATA_DIR / "02_interim"

if DEMO_MODE:
    RAW_DATA_DIR = DATA_DIR / "01_raw_sample"