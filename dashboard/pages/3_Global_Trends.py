"""Global Trends - how scores changed across the world over time."""

import pandas as pd
import plotly.express as px
import streamlit as st

from components.charts import (
    inject_style,
    load_data,
    category_choices,
    chart_card,
    section_header,
)
from src.visualizations import create_trend_chart

st.set_page_config(page_title="Global Trends - Freedom in the World", layout="wide")
inject_style()

st.title("Global Trends")
st.caption("How have freedom scores changed between 2013 and 2026?")

raw, long = load_data()
choices = category_choices(numeric_only=True)

# ---------------------------------------------------------------------------
# Controls live in the sidebar - content stays full width
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Filters")
    selected = st.selectbox("Indicator", choices["label"].tolist())
    indicator = choices[choices["label"] == selected].iloc[0]["INDICATOR"]
    start, end = st.select_slider(
        "Year range",
        options=list(range(2013, 2027)),
        value=(2013, 2026),
    )

sub = long[(long["INDICATOR"] == indicator) & long["Year"].between(start, end)].copy()
sub["Score"] = pd.to_numeric(sub["Score"], errors="coerce")

section_header("Trends")

left, right = st.columns(2)
with left:
    chart_card(
        create_trend_chart(
            sub.groupby("Year")["Score"].mean().round(2).reset_index(),
            title=f"Global mean score, {start}-{end}",
            y_label="Mean score",
        ),
        caption=(
            "Mean across the economies present in each year; missing scores "
            "are skipped, never imputed."
        ),
        key="gt_trend",
    )
with right:
    chart_card(
        px.box(
            sub,
            x="Year",
            y="Score",
            title="Distribution of scores by year",
            labels={"Score": "Score", "Year": "Year"},
        ),
        caption="The whole distribution, not just the mean.",
        key="gt_box",
    )

section_header("Who moved, and how far")

improved_count = {}
for year in range(start + 1, end + 1):
    prev = sub[sub["Year"] == year - 1].set_index("REF_AREA")["Score"]
    curr = sub[sub["Year"] == year].set_index("REF_AREA")["Score"]
    both = pd.concat([prev, curr], axis=1, keys=[year - 1, year]).dropna()
    improved_count[year] = int((both[year] > both[year - 1]).sum())

if improved_count:
    chart_card(
        px.bar(
            pd.DataFrame(
                {"Year": list(improved_count.keys()), "improved": list(improved_count.values())}
            ),
            x="Year",
            y="improved",
            title="Number of economies scoring higher than the previous year",
            labels={"improved": "Economies improved", "Year": "Year"},
        ),
        key="gt_improved",
    )
else:
    st.info("Select a wider year range to compare consecutive years.")

st.caption("Source: Freedom House, Freedom in the World (World Bank Data360).")
