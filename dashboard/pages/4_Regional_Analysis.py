"""Regional Analysis - UN M49 main regions and Africa sub-regions."""

import pandas as pd
import plotly.express as px
import streamlit as st

from components.charts import (
    inject_style,
    load_data,
    scale_max_map,
    chart_card,
    semantic_colorbar,
    add_designer_footer,
    section_header,
)
from src.regions import (
    get_region_lookup,
    get_africa_subregion_lookup,
    AFRICA_UN_M49,
)
from src.visualizations import create_multi_trend_chart, create_heatmap

st.set_page_config(page_title="Regional Analysis - Freedom in the World", layout="wide")
inject_style()

st.title("Regional Analysis")
st.caption(
    "UN M49 geographic classification (documented, user-approved) applied to "
    "the dataset's own economy labels — never classified by assumption."
)

raw, long = load_data()
sm_map = scale_max_map()

with st.sidebar:
    st.markdown("### Region scheme")
    scheme = st.radio(
        "Grouping",
        ["UN M49 main regions", "Africa sub-regions"],
    )

total = long[long["INDICATOR"] == "FH_FIW_TOTAL"]

if scheme == "UN M49 main regions":
    lookup = get_region_lookup()
    total = total.assign(region=total["Economy"].map(lookup))
    group_col = "region"
else:
    lookup = get_africa_subregion_lookup()
    total = total[total["Economy"].isin(AFRICA_UN_M49)].assign(
        region=total["Economy"].map(lookup)
    )
    group_col = "region"

section_header("Trends")

trend = total.groupby([group_col, "Year"])["Score"].mean().reset_index()
chart_card(
    create_multi_trend_chart(
        trend,
        title="Mean overall score by region, 2013-2026",
        y_label="Mean overall score (0-100)",
        group_col=group_col,
    ),
    caption="Each line is the mean overall score of the region's economies in that year.",
    key="ra_trend",
)

col1, col2 = st.columns(2)
with col1:
    r2026 = total[total["Year"] == 2026].groupby(group_col)["Score"].mean().round(2).sort_values()
    chart_card(
        px.bar(
            r2026,
            orientation="h",
            title="Mean overall score by region, 2026",
            labels={"value": "Mean overall score (0-100)", group_col: "Region"},
            text_auto=True,
        ),
        key="ra_ranking",
    )
with col2:
    r2013 = total[total["Year"] == 2013].groupby(group_col)["Score"].mean()
    change = (r2026 - r2013).round(2).sort_values()
    chart_card(
        px.bar(
            change,
            orientation="h",
            title="Change in mean score, 2013 to 2026",
            labels={"value": "Change in score", group_col: "Region"},
            text_auto=True,
        ),
        key="ra_movers",
    )

section_header("Where each region's scores come from (2026)")

cats = [
    "FH_FIW_A", "FH_FIW_B", "FH_FIW_C", "FH_FIW_D",
    "FH_FIW_E", "FH_FIW_F", "FH_FIW_G",
    "FH_FIW_PR", "FH_FIW_CL", "FH_FIW_TOTAL",
]
cat_labels = {
    "FH_FIW_A": "A Electoral", "FH_FIW_B": "B Pluralism", "FH_FIW_C": "C Gov. function",
    "FH_FIW_D": "D Expression", "FH_FIW_E": "E Association", "FH_FIW_F": "F Rule of law",
    "FH_FIW_G": "G Personal autonomy", "FH_FIW_PR": "Political rights",
    "FH_FIW_CL": "Civil liberties", "FH_FIW_TOTAL": "Overall",
}
cat_data = long[
    long["INDICATOR"].isin(cats) & (long["Year"] == 2026)
].copy()
cat_data["region"] = cat_data["Economy"].map(lookup)
cat_data["pct"] = cat_data["Score"] / cat_data["UNIT_MEASURE"].map(sm_map) * 100
pivot = (
    cat_data.pivot_table(index="region", columns="INDICATOR", values="pct", aggfunc="mean")
    .rename(columns=cat_labels)
    .round(1)
)

heatmap_fig = create_heatmap(
    pivot,
    title="Region × category: mean score as % of scale, 2026",
    colorbar_label="% of scale",
    zmin=0,
    zmax=100,
    # The Freedom House colour language, matching the maps:
    # purple (less free) -> gold -> green (more free).
    colorscale=[
        [0.0, "#9260A8"],
        [0.5, "#D5A616"],
        [1.0, "#00A767"],
    ],
)
semantic_colorbar(heatmap_fig, "level")
add_designer_footer(heatmap_fig)
chart_card(
    heatmap_fig,
    caption=(
        "Rule of law is the weakest category in every region; expression the "
        "strongest in most. The gap between the top and bottom regions runs "
        "through every category. Colours run from Not free to Free."
    ),
    key="ra_heatmap",
)

st.caption(
    "Classifications: UN M49 (unstats.un.org/unsd/methodology/m49), approved for "
    "this project. Source: Freedom House, Freedom in the World (World Bank Data360)."
)
