"""Loading functions for the raw and processed Freedom in the World data.

Paths are resolved relative to the project root (one level above this file),
so the helpers work no matter which directory the notebook/dashboard runs from.
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_CSV = PROJECT_ROOT / "data" / "raw" / "FH_FIW_WIDEF.csv"
RAW_METADATA = PROJECT_ROOT / "data" / "raw" / "FH_FIW.json"
PROCESSED_LONG = PROJECT_ROOT / "data" / "processed" / "freedom_in_world_long.csv"


def load_raw_data(path=RAW_CSV):
    """Load the raw wide-format CSV.

    Returns a DataFrame of 7880 rows (197 economies x 40 indicators) with
    ~38 metadata columns followed by the 14 year columns (2013-2026).
    """
    return pd.read_csv(path)


def load_metadata(path=RAW_METADATA):
    """Load the metadata JSON as a Python dict.

    The data dictionary lives here: ``database_description.ref_country``
    maps REF_AREA codes to economy names. Indicator definitions are NOT
    in this file - they live in the CSV itself.
    """
    import json

    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_processed_data(path=PROCESSED_LONG):
    """Load the cleaned long-format analytical dataset.

    Raises FileNotFoundError if the dataset has not been created yet
    (it is produced by notebook 03, data cleaning and preparation).
    """
    if not Path(path).exists():
        raise FileNotFoundError(
            f"{path} does not exist yet. "
            "Run notebook 03 (data cleaning and preparation) first."
        )
    return pd.read_csv(path)
