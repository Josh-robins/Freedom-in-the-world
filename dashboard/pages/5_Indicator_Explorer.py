"""Indicator Explorer - the major dimensions one at a time, in plain words."""

import pandas as pd
import plotly.express as px
import streamlit as st

from components.charts import (
    inject_style,
    load_data,
    category_choices,
    scale_max_map,
    chart_card,
    render_map,
    render_publication_map,
    build_status_map,
    semantic_colorbar,
    section_header,
)
from src.visualizations import create_trend_chart, create_multi_trend_chart, create_choropleth

st.set_page_config(page_title="Indicator Explorer - Freedom in the World", layout="wide")
inject_style()

st.title("Indicator Explorer")
st.caption("What does each major dimension measure, and where does the world stand on it?")

raw, long = load_data()
sm_map = scale_max_map()
choices = category_choices()  # summaries + the seven categories (no individual questions)

with st.sidebar:
    st.markdown("### Indicator")
    selected = st.selectbox("Choose an indicator", choices["label"].tolist())
    row = choices[choices["label"] == selected].iloc[0]
    indicator = row["INDICATOR"]
    indicator_name = row["label"]

st.markdown(f"**What it measures:** {row['INDICATOR_LABEL']}")
st.markdown(f"**Category:** {row['Category']}  ·  **Scale:** {row['UNIT_MEASURE_LABEL']}")

is_status = indicator == "FH_FIW_STATUS"
if is_status:
    # STATUS is categorical - its strings live in `raw`; the numeric-coerced
    # `long` frame would turn them into NaN.
    sub = raw[(raw["INDICATOR"] == indicator)].copy()
    is_numeric = False
else:
    sub = long[(long["INDICATOR"] == indicator)].copy()
    is_numeric = sub["UNIT_MEASURE"].iloc[0] != "CAT"
    if is_numeric:
        sub["Score"] = pd.to_numeric(sub["Score"], errors="coerce")

section_header("Global level and trend")

if is_status:
    status_trend = (
        sub.pivot_table(index="Year", columns="Score", values="Economy", aggfunc="count")[["F", "PF", "NF"]]
        .reset_index()
        .melt(id_vars="Year", var_name="status", value_name="count")
    )
    chart_card(
        create_multi_trend_chart(
            status_trend,
            title=f"Economies by status, 2013-{long['Year'].max()}",
            y_label="Number of economies",
            group_col="status",
            value_col="count",
        ),
        caption=(
            "The number of Free, Partly Free and Not Free economies each year. "
            "Not Free has grown steadily since 2013."
        ),
        key="ie_trend",
    )
else:
    chart_card(
        create_trend_chart(
            sub.groupby("Year")["Score"].mean().round(2).reset_index(),
            title=f"Global mean score: {indicator_name}",
            y_label="Mean score",
        ),
        caption=(
            "Higher is more free on this scale. The two ratings (1–7) run "
            "the other way and the status is categorical — both are handled "
            "on their own terms."
        ),
        key="ie_trend",
    )

if not is_status:
    col1, col2 = st.columns(2)
    with col1:
        latest = long["Year"].max()
        top = sub[sub["Year"] == latest].nlargest(10, "Score")
        chart_card(
            px.bar(
                top.sort_values("Score"),
                x="Score",
                y="Economy",
                orientation="h",
                title=f"Top 10: {indicator_name}, {latest}",
                labels={"Score": "Score", "Economy": "Economy"},
            ),
            key="ie_top",
        )
    with col2:
        bottom = sub[sub["Year"] == latest].nsmallest(10, "Score")
        chart_card(
            px.bar(
                bottom.sort_values("Score"),
                x="Score",
                y="Economy",
                orientation="h",
                title=f"Bottom 10: {indicator_name}, {latest}",
                labels={"Score": "Score", "Economy": "Economy"},
            ),
            key="ie_bottom",
        )

section_header("Geographic view")

if is_status:
    latest = long["Year"].max()
    status_data = sub[sub["Year"] == latest].dropna(subset=["Score"]).copy()
    status_data["classification"] = status_data["Score"].map(
        {"F": "Free", "PF": "Partly Free", "NF": "Not Free"}
    )
    fig = build_status_map(status_data, latest)
    fig.update_layout(height=640)
    render_publication_map(fig, f"freedom_in_the_world_{latest}", key="ie_map")
    st.caption(
        "Free (green): broadly respected · Partly Free (gold): mixed or "
        "limited · Not Free (purple): heavily restricted. Of the 197 "
        "economies, 195 are countries and 2 are territories (Hong Kong "
        "SAR, China and Puerto Rico), per the FiW metadata."
    )
elif is_numeric:
    latest = long["Year"].max()
    scale_max = sm_map.get(sub["UNIT_MEASURE"].iloc[0], 100)
    map_data = sub[sub["Year"] == latest].dropna(subset=["Score"]).copy()
    # Level as % of the indicator's scale: 0-100 with 'Not free'/'Free'
    # labels on the colour bar instead of raw 0-4 / 0-12 / 0-100 numbers.
    map_data["pct"] = (map_data["Score"] / scale_max * 100).round(1)
    fig = create_choropleth(
        map_data,
        location_col="REF_AREA",
        color_col="pct",
        title=f"{indicator_name} by economy, {latest}",
        colorbar_label="Score (% of scale)",
        range_color=(0, 100),
    )
    semantic_colorbar(fig, "level")
    render_map(
        fig,
        caption=(
            "Map zoom is disabled; colours run from Not free to Free, "
            "with the exact value on hover. Use the camera button to "
            "download it as PNG."
        ),
        key="ie_map",
    )

st.caption("Source: Freedom House, Freedom in the World (World Bank Data360).")
