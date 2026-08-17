"""Freedom in the World - interactive dashboard (home / overview page).

Run with:  streamlit run dashboard/app.py
The dashboard consumes ONLY the processed long dataset
(data/processed/freedom_in_world_long.csv) and the reusable src/ helpers.
"""

import sys
from pathlib import Path

# Deployment bootstrap: make the repo root and the dashboard folder importable
# regardless of the working directory. Locally the working directory covers
# `src`; on Streamlit Cloud only the main script's directory is guaranteed on
# sys.path, so the pages' `from src...` imports need this explicit insert.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_ROOT = Path(__file__).resolve().parent
for _path in (str(PROJECT_ROOT), str(DASHBOARD_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import pandas as pd
import streamlit as st

from components.charts import (
    inject_style,
    load_data,
    chart_card,
    render_publication_map,
    build_status_map,
    section_header,
)
from src.visualizations import create_trend_chart, create_multi_trend_chart

st.set_page_config(page_title="Freedom in the World - Dashboard", layout="wide")
# Sidebar branding (logo + wordmark, collapsing to the mark) is applied by
# inject_style() on every page.
inject_style()

st.title("Freedom in the World — Interactive Dashboard")
st.caption(
    "Political rights and civil liberties in 197 economies, 2013–2026. "
    "Source: Freedom House, Freedom in the World (World Bank Data360)."
)

raw, long = load_data()

# ---------------------------------------------------------------------------
# Key metrics (the first thing a visitor sees)
# ---------------------------------------------------------------------------
total = long[long["INDICATOR"] == "FH_FIW_TOTAL"]
mean_2013 = total[total["Year"] == 2013]["Score"].mean()
mean_2026 = total[total["Year"] == 2026]["Score"].mean()

status_2026 = raw[(raw["INDICATOR"] == "FH_FIW_STATUS") & (raw["Year"] == 2026)]
status_counts = status_2026["Score"].value_counts()

s2013 = total[total["Year"] == 2013].set_index("REF_AREA")["Score"]
s2026 = total[total["Year"] == 2026].set_index("REF_AREA")["Score"]
paired = pd.concat([s2013, s2026], axis=1, keys=[2013, 2026]).dropna()
deteriorated = int((paired[2026] < paired[2013]).sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Economies covered", "197")
c2.metric("Indicators", "40")
c3.metric("Years", "2013 – 2026")
c4.metric("Global mean 2026", f"{mean_2026:.1f}", delta=f"{mean_2026 - mean_2013:+.1f} since 2013")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Free (2026)", int(status_counts.get("F", 0)))
c6.metric("Partly Free (2026)", int(status_counts.get("PF", 0)))
c7.metric("Not Free (2026)", int(status_counts.get("NF", 0)))
c8.metric("Deteriorated since 2013", deteriorated)

# ---------------------------------------------------------------------------
# The headline map: Freedom status (Free / Partly Free / Not Free)
# ---------------------------------------------------------------------------
status_data = (
    raw[(raw["INDICATOR"] == "FH_FIW_STATUS") & (raw["Year"] == 2026)]
    .dropna(subset=["Score"])
    .copy()
)
status_data["classification"] = status_data["Score"].map(
    {"F": "Free", "PF": "Partly Free", "NF": "Not Free"}
)
fig = build_status_map(status_data, 2026)
# Big headline map: render it tall so the world fills the screen.
fig.update_layout(height=760)
render_publication_map(fig, "freedom_in_the_world_2026", key="home_status_map")
st.caption(
    "Free (green): political rights and civil liberties broadly respected · "
    "Partly Free (gold): mixed or limited · Not Free (purple): heavily "
    "restricted. Of the 197 economies in this dataset, 195 are countries and "
    "2 are territories (Hong Kong SAR, China and Puerto Rico). Map zoom is "
    "disabled; use the button or camera to download it as PNG."
)

st.divider()

# ---------------------------------------------------------------------------
# The global picture - a two-column grid
# ---------------------------------------------------------------------------
section_header("The global picture at a glance")

yearly_mean = total.groupby("Year")["Score"].mean().round(2)
status_trend = (
    raw[raw["INDICATOR"] == "FH_FIW_STATUS"]
    .pivot_table(index="Year", columns="Score", values="Economy", aggfunc="count")[["F", "PF", "NF"]]
    .reset_index()
    .melt(id_vars="Year", var_name="status", value_name="count")
)

left, right = st.columns(2)
with left:
    chart_card(
        create_trend_chart(
            yearly_mean.reset_index(),
            title="Global average overall freedom score, 2013-2026",
            y_label="Mean overall score (0-100)",
        ),
        caption=(
            "The global average fell in every single year, from 61.2 (2013) "
            "to 56.9 (2026) — a −4.3 point drift with no rebound."
        ),
        key="home_global_trend",
    )
with right:
    chart_card(
        create_multi_trend_chart(
            status_trend,
            title="Economies by status: Free / Partly Free / Not Free",
            y_label="Number of economies",
            group_col="status",
            value_col="count",
        ),
        caption=(
            "Not Free grew from 47 to 59 economies (23.9% → 30.1%); the "
            "middle of the classification is being squeezed out."
        ),
        key="home_status",
    )

st.caption(
    "Guiding question: what does the Freedom in the World data reveal about "
    "the evolution, distribution and differences in political rights and "
    "civil liberties across economies between 2013 and 2026? "
    "Citation: Freedom House. (Year). Freedom in the World Year. Retrieved "
    "from https://freedomhouse.org/report/freedom-world#Data"
)
