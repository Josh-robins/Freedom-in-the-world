"""Cleaning and reshaping functions.

The raw files in data/raw/ are never modified - every function here
returns a new DataFrame.
"""

import pandas as pd


def reshape_freedom_data(raw, indicators=None, value_name="Score"):
    """Melt the raw wide CSV into long format and attach the indicator dictionary.

    The wide frame has one row per (economy, indicator) with year columns;
    this returns one row per (economy, indicator, year):

        REF_AREA | Economy | INDICATOR | INDICATOR_LABEL | Category |
        UNIT_MEASURE | UNIT_MEASURE_LABEL | Year | Score

    Cleaning decisions (documented in notebook 03):
    - The economy name comes from the CSV's own REF_AREA_LABEL (verified
      equal to the metadata lookup in notebook 02) and is renamed to Economy.
    - Year values are converted to int.
    - Scores are coerced to numeric with ``pd.to_numeric(errors="coerce")``,
      so non-numeric cells become NaN (missing) - never imputed.
    - The STATUS indicator (``UNIT_MEASURE == "CAT"``) is categorical: its
      scores stay strings (F / PF / NF) and are excluded from coercion.
    - If the indicator lookup is passed, its ``Category`` column is attached.
    """
    id_cols = [
        "REF_AREA",
        "REF_AREA_LABEL",
        "INDICATOR",
        "INDICATOR_LABEL",
        "UNIT_MEASURE",
        "UNIT_MEASURE_LABEL",
    ]
    year_cols = [c for c in raw.columns if str(c).isdigit()]

    long = raw.melt(
        id_vars=id_cols,
        value_vars=year_cols,
        var_name="Year",
        value_name=value_name,
    )
    long["Year"] = long["Year"].astype(int)

    # Scores: numeric indicators are coerced to float; the categorical
    # STATUS indicator keeps its string values (F / PF / NF). The column is
    # first widened to object because pandas 3.0 str dtype rejects floats.
    long[value_name] = long[value_name].astype(object)
    numeric = long["UNIT_MEASURE"] != "CAT"
    long.loc[numeric, value_name] = pd.to_numeric(
        long.loc[numeric, value_name], errors="coerce"
    )

    long = long.rename(columns={"REF_AREA_LABEL": "Economy"})

    if indicators is not None:
        long = long.merge(indicators[["INDICATOR", "Category"]], on="INDICATOR", how="left")

    column_order = [
        "REF_AREA",
        "Economy",
        "INDICATOR",
        "INDICATOR_LABEL",
        "Category",
        "UNIT_MEASURE",
        "UNIT_MEASURE_LABEL",
        "Year",
        value_name,
    ]
    return long[column_order]
