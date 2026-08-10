"""Map Explorer - interactive choropleth maps of any indicator and year.

Design rules (per the project brief):
- Maps are rendered full-width WITHOUT a container card and blend into the
  page background, so they stay easy to read.
- Zooming/panning is disabled entirely: no zoom buttons, no scroll zoom,
  dragmode off. The only modebar action is PNG download.
- The East Africa 5-economy maps from notebook 08 are intentionally NOT
  included; this page covers the world and Africa views.
- Indicator names are shown in plain language - never the FH_FIW_* codes.
- The status map uses the Freedom House colours (green/gold/purple) on a
  navy background, with a legend of exactly Free / Partly Free / Not Free.
"""

import pandas as pd
import streamlit as st

from components.charts import (
    inject_style,
    load_data,
    category_choices,
    scale_max_map,
    render_map,
    render_publication_map,
    build_status_map,
    semantic_colorbar,
    section_header,
)
from src.visualizations import create_choropleth

st.set_page_config(page_title="Map Explorer - Freedom in the World", layout="wide")
inject_style()

st.title("Map Explorer")
st.caption("Where in the world — for any indicator and any year.")

raw, long = load_data()
sm_map = scale_max_map()

# Summaries + the seven categories + Status. The two 1-7 ratings are
# excluded here (inverted scale, explored on their own terms).
choices_all = category_choices()
choices = choices_all[
    ~choices_all["INDICATOR"].isin(["FH_FIW_PR_RATING", "FH_FIW_CL_RATING"])
].reset_index(drop=True)

with st.sidebar:
    st.markdown("### Map settings")
    # The status map is the default view - it is the headline map.
    status_index = int(choices.index[choices["INDICATOR"] == "FH_FIW_STATUS"][0])
    selected = st.selectbox("Indicator", choices["label"].tolist(), index=status_index)
    row = choices[choices["label"] == selected].iloc[0]
    indicator = row["INDICATOR"]
    indicator_name = row["label"]
    year = st.select_slider("Year", options=list(range(2013, 2027)), value=2026)
    scope = st.radio("Scope", ["World", "Africa"])
    is_status = indicator == "FH_FIW_STATUS"
    show_change = st.checkbox(
        "Show change since 2013 instead of the level",
        value=False,
        disabled=is_status,
    )

if is_status:
    # ------------------------------------------------------------------
    # Status map: categorical, Freedom House colours, navy background.
    # ------------------------------------------------------------------
    # Note: STATUS must come from `raw` - the numeric-coerced `long` frame
    # turns its scores into NaN.
    status_data = (
        raw[(raw["INDICATOR"] == "FH_FIW_STATUS") & (raw["Year"] == year)]
        .dropna(subset=["Score"])
        .copy()
    )
    status_data["classification"] = status_data["Score"].map(
        {"F": "Free", "PF": "Partly Free", "NF": "Not Free"}
    )
    fig = build_status_map(
        status_data,
        year,
        scope="africa" if scope == "Africa" else "world",
    )
    fig.update_layout(height=780 if scope == "Africa" else 640)
    render_publication_map(fig, f"freedom_in_the_world_{year}", key="me_map")
    st.caption(
        "Free (green): political rights and civil liberties broadly respected · "
        "Partly Free (gold): mixed or limited · Not Free (purple): heavily "
        "restricted. Of the 197 economies in this dataset, 195 are countries and "
        "2 are territories (Hong Kong SAR, China and Puerto Rico), per the FiW "
        "metadata's country/territory distinction. Map zoom is disabled."
    )
else:
    # ------------------------------------------------------------------
    # Numeric maps: level or change, always as % of scale.
    # ------------------------------------------------------------------
    scale_max = sm_map.get(row["UNIT_MEASURE"], 100)
    sub = long[long["INDICATOR"] == indicator].copy()
    sub["Score"] = pd.to_numeric(sub["Score"], errors="coerce")

    if show_change:
        base = sub[sub["Year"] == 2013][["REF_AREA", "Economy", "Score"]].rename(
            columns={"Score": "s2013"}
        )
        current = sub[sub["Year"] == year][["REF_AREA", "Score"]].rename(
            columns={"Score": "s_now"}
        )
        map_data = base.merge(current, on="REF_AREA").dropna()
        # Change as % of the indicator's scale: every indicator shares the
        # same -100..100 colour scale and maps are directly comparable.
        map_data["change_pct"] = (
            (map_data["s_now"] - map_data["s2013"]) / scale_max * 100
        ).round(1)
        color_col, colorbar_label = "change_pct", "Change (% of scale)"
        range_color = (-100, 100)
        title = f"{indicator_name}: change from 2013 to {year}"
    else:
        map_data = sub[sub["Year"] == year].dropna(subset=["Score"]).copy()
        # Level as % of the indicator's scale: every map is 0-100, labelled
        # 'Not free' to 'Free' instead of raw 0-4 / 0-12 / 0-100 numbers.
        map_data["pct"] = (map_data["Score"] / scale_max * 100).round(1)
        color_col, colorbar_label = "pct", "Score (% of scale)"
        range_color = (0, 100)
        title = f"{indicator_name} by economy, {year}"

    fig = create_choropleth(
        map_data,
        location_col="REF_AREA",
        color_col=color_col,
        title=title,
        colorbar_label=colorbar_label,
        range_color=range_color,
        scope="africa" if scope == "Africa" else "world",
    )
    semantic_colorbar(fig, "change" if show_change else "level")
    render_map(
        fig,
        caption=(
            "Map zoom is disabled by design; the only chart action is PNG "
            "download (camera button). Colours run from Not free to Free; "
            "the exact value appears on hover."
        ),
        key="me_map",
        # The Africa view renders taller so the continent is easier to read.
        height=760 if scope == "Africa" else 560,
    )

section_header("Reading the map")
st.markdown(
    """
- **Status view** — three categories: **Free** (green), **Partly Free**
  (gold), **Not Free** (purple), with the Freedom House colours on a navy
  background. The dataset holds 195 countries and 2 territories.
- **Level view** — colour shows the score as a share of the indicator's
  scale (0–100%), from **Not free** to **Free**.
- **Change view** — colour shows the change since 2013 as a share of the
  scale (red = declined, blue = improved), from **Declined** to **Improved**.
- All 197 economies render reliably (ISO-3 matching verified in notebook 08);
  nothing is silently dropped.
- **Land without data** — e.g. **Western Sahara**, which is not among the
  dataset's 197 economies — appears in a neutral dark tone so no territory
  is missing from the map's outline.
"""
)

st.caption("Source: Freedom House, Freedom in the World (World Bank Data360).")
