"""Indicator dictionary, built from the raw CSV's own label columns.

The metadata JSON contains no indicator definitions; the authoritative
names and scales live in the CSV (INDICATOR, INDICATOR_LABEL,
UNIT_MEASURE, UNIT_MEASURE_LABEL).
"""

import pandas as pd

from src.data_loader import load_raw_data


def get_indicator_dictionary():
    """Build the indicator lookup table from the raw CSV.

    Returns one row per indicator code with columns:
    ``INDICATOR``, ``INDICATOR_LABEL`` (question text), ``Category``,
    ``UNIT_MEASURE`` (scale code, e.g. 0_TO_4) and ``UNIT_MEASURE_LABEL``.

    ``Category`` is derived from the label text itself: the segment before
    the first ``": "`` (e.g. ``Rule of Law: Is there protection ...`` ->
    ``Rule of Law``). The six summary indicators (TOTAL, PR, CL, ratings,
    status) carry the prefix ``Freedom in the World``. Nothing is invented -
    every category string is written in the CSV's own labels.
    """
    raw = load_raw_data()
    columns = ["INDICATOR", "INDICATOR_LABEL", "UNIT_MEASURE", "UNIT_MEASURE_LABEL"]
    table = raw[columns].drop_duplicates().reset_index(drop=True)
    table["Category"] = table["INDICATOR_LABEL"].str.split(": ", n=1).str[0]
    order = ["INDICATOR", "INDICATOR_LABEL", "Category", "UNIT_MEASURE", "UNIT_MEASURE_LABEL"]
    return table[order]
