"""Country Explorer - individual economy profiles and peer comparisons."""

import pandas as pd
import plotly.express as px
import streamlit as st

from components.charts import (
    inject_style,
    load_data,
    scale_max_map,
    chart_card,
    section_header,
)
from src.visualizations import create_multi_trend_chart

st.set_page_config(page_title="Country Explorer - Freedom in the World", layout="wide")
inject_style()

st.title("Country Explorer")
st.caption("How has a selected economy evolved — and how does it compare with peers?")

raw, long = load_data()
sm_map = scale_max_map()

economies = sorted(long["Economy"].unique())

with st.sidebar:
    st.markdown("### Selection")
    economy = st.selectbox("Economy", economies, index=economies.index("Uganda"))
    indicator = st.selectbox(
        "Indicator",
        ["Overall score", "Political rights", "Civil liberties"],
    )
    ind_code = {
        "Overall score": "FH_FIW_TOTAL",
        "Political rights": "FH_FIW_PR",
        "Civil liberties": "FH_FIW_CL",
    }[indicator]
    peers = st.multiselect(
        "Compare with (optional)",
        economies,
        default=[],
        help="Add a few economies to plot alongside the selected one.",
    )

selected_group = [economy] + [p for p in peers if p != economy]

sub = long[
    (long["INDICATOR"] == ind_code) & long["Economy"].isin(selected_group)
].copy()

section_header("Historical trend")

chart_card(
    create_multi_trend_chart(
        sub,
        title=f"{indicator} over time",
        y_label="Score",
        group_col="Economy",
    ),
    caption=(
        "Solid line: the selected economy. The comparison line(s) help judge "
        "whether its path is typical for the neighbourhood."
    ),
    key="ce_trend",
)

section_header("Indicator profile (latest year)")

latest = long["Year"].max()
profile = (
    long[
        (long["Economy"] == economy)
        & (long["Year"] == latest)
        & long["UNIT_MEASURE"].isin(sm_map)
    ]
    .copy()
)
profile["pct"] = (profile["Score"] / profile["UNIT_MEASURE"].map(sm_map) * 100).round(0)
profile = profile.sort_values("pct")

left, right = st.columns(2)
with left:
    chart_card(
        px.bar(
            profile,
            x="pct",
            y="INDICATOR",
            orientation="h",
            color="Category",
            title=f"{economy}: indicator scores as share of each scale, {latest}",
            labels={"pct": "% of indicator scale", "INDICATOR": "Indicator"},
        ),
        caption="Each indicator as a share of its own scale, weakest to strongest.",
        key="ce_profile",
    )
with right:
    first = 2013
    mov = long[
        (long["INDICATOR"] == ind_code)
        & long["Economy"].isin(selected_group)
        & long["Year"].isin([first, latest])
    ].pivot_table(index="Economy", columns="Year", values="Score", aggfunc="first")
    mov["change"] = (mov[latest] - mov[first]).round(1)
    mov = mov.sort_values("change")
    chart_card(
        px.bar(
            mov.reset_index(),
            x="change",
            y="Economy",
            orientation="h",
            title=f"Change in score, {first} to {latest}",
            labels={"change": "Change in score", "Economy": "Economy"},
            text_auto=True,
        ),
        key="ce_movers",
    )

st.caption("Source: Freedom House, Freedom in the World (World Bank Data360).")
