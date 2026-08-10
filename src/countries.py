"""Country / economy lookup table, built from the metadata JSON."""

import pandas as pd

from src.data_loader import load_metadata


def get_country_dictionary():
    """Build the REF_AREA code -> economy name lookup table.

    Source: ``database_description.ref_country`` in the metadata JSON
    (data/raw/FH_FIW.json). Returns a DataFrame with columns
    ``REF_AREA`` (code) and ``Economy`` (name).
    """
    metadata = load_metadata()
    ref_country = metadata["database_description"]["ref_country"]
    table = pd.DataFrame(ref_country)
    return table.rename(columns={"code": "REF_AREA", "name": "Economy"})
