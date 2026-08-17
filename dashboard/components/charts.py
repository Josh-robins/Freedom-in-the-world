"""Shared dashboard components: data loading, chart rendering, styling.

Every chart in the dashboard follows the same conventions as the notebooks:
standardized Plotly styling (via src/visualizations.py), a source note, and
a modebar restricted to PNG download. Maps are rendered full-width **without**
a container card, blend into the page background (transparent canvas), and
zoom/pan is disabled entirely.

Display language: the dashboard shows **real words**, never the FH_FIW_*
codes. Indicator pickers use the survey question text or plain names.
"""

import pandas as pd
import streamlit as st
from pathlib import Path

from src.data_loader import load_processed_data

# ---------------------------------------------------------------------------
# Visual language - DARK THEME: black background, white text, amber accent.
# (Defined in .streamlit/config.toml; the constants below keep charts and
# cards consistent with it.)
# ---------------------------------------------------------------------------
ACCENT = "#c97b1e"      # amber - highlights, deltas, primary widget color
TEXT = "#f9fafb"        # near-white - body text, headings
MUTED = "#9ca3af"       # gray - captions, notes
SURFACE = "#111111"     # card / sidebar surface (secondary background)
BORDER = "#262626"      # card borders

# Publication-style status map (Freedom House look).
NAVY = "#0E2A45"                        # map background / ocean
LAND_DARK = "#1a2330"                   # land without data
FH_STATUS_COLORS = {
    "Free": "#00A767",
    "Partly Free": "#D5A616",
    "Not Free": "#9260A8",
}

# Modebar: the ONLY action available is downloading the chart as PNG.
# No zoom, pan, or other buttons - maps therefore cannot be zoomed in.
CHART_CONFIG = {
    "displaylogo": False,
    "scrollZoom": False,
    "modeBarButtons": [["toImage"]],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "freedom_in_the_world_chart",
        "scale": 2,
    },
}

SOURCE_NOTE = "Source: Freedom House, Freedom in the World (World Bank Data360)"

# Plain-language names for the summary indicators (the other 34 use their
# survey question text verbatim - no codes anywhere in the dashboard).
SUMMARY_NAMES = {
    "FH_FIW_TOTAL": "Overall score",
    "FH_FIW_PR": "Political rights",
    "FH_FIW_CL": "Civil liberties",
    "FH_FIW_PR_RATING": "Political rights rating (1-7, 1 = most free)",
    "FH_FIW_CL_RATING": "Civil liberties rating (1-7, 1 = most free)",
    "FH_FIW_STATUS": "Status (Free / Partly Free / Not Free)",
}


# ---------------------------------------------------------------------------
# Data loading (cached - the processed long dataset loads once per session)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading the Freedom in the World dataset...")
def load_data():
    """Return (raw_long, numeric_long).

    ``raw_long`` keeps the mixed-type Score column (STATUS strings intact);
    ``numeric_long`` has Score coerced to numeric (STATUS rows become NaN and
    are only ever analysed through ``raw_long``).
    """
    raw = load_processed_data()
    numeric = raw.copy()
    numeric["Score"] = pd.to_numeric(numeric["Score"], errors="coerce")
    return raw, numeric


@st.cache_data(show_spinner=False)
def indicator_lookup():
    """The 40-indicator dictionary (code, label, category, scale)."""
    from src.indicators import get_indicator_dictionary

    return get_indicator_dictionary()


@st.cache_data(show_spinner=False)
def indicator_choices(numeric_only=False):
    """Readable indicator picker options - real words, no FH_FIW_ codes.

    Returns a DataFrame with columns INDICATOR, label, Category, UNIT_MEASURE.
    The label is the survey question text (or a plain name for the six
    summary indicators). ``numeric_only=True`` excludes the categorical
    status (and the inverted ratings, for maps on a shared scale).
    """
    lookup = indicator_lookup()
    if numeric_only:
        lookup = lookup[lookup["UNIT_MEASURE"].isin(scale_max_map())]
    rows = []
    for r in lookup.sort_values("INDICATOR").itertuples():
        rows.append(
            {
                "INDICATOR": r.INDICATOR,
                "label": SUMMARY_NAMES.get(r.INDICATOR, r.INDICATOR_LABEL),
                "INDICATOR_LABEL": r.INDICATOR_LABEL,
                "Category": r.Category,
                "UNIT_MEASURE": r.UNIT_MEASURE,
                "UNIT_MEASURE_LABEL": r.UNIT_MEASURE_LABEL,
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def category_choices(numeric_only=False):
    """Picker options at the meaningful level: the summary indicators plus
    the seven categories (Rule of Law, Electoral Process, ...). Individual
    survey questions are intentionally excluded - they are too granular for
    the pickers. Category labels are the bare category name, without the
    'Political rights: ' / 'Civil liberties: ' prefix.
    """
    choices = indicator_choices(numeric_only=numeric_only)
    is_summary = choices["INDICATOR"].isin(SUMMARY_NAMES.keys())
    is_category = choices["INDICATOR"].str.fullmatch(r"FH_FIW_[A-G]")
    cats = choices[is_summary | is_category].copy()
    cats["label"] = cats["label"].str.replace(
        r"^(Political rights|Civil liberties): ", "", regex=True
    )
    # Display order: summaries first, then categories A-G.
    order = [
        "FH_FIW_TOTAL", "FH_FIW_PR", "FH_FIW_CL",
        "FH_FIW_PR_RATING", "FH_FIW_CL_RATING", "FH_FIW_STATUS",
        "FH_FIW_A", "FH_FIW_B", "FH_FIW_C", "FH_FIW_D",
        "FH_FIW_E", "FH_FIW_F", "FH_FIW_G",
    ]
    cats["_order"] = pd.Categorical(cats["INDICATOR"], categories=order, ordered=True)
    cats = cats.sort_values("_order").drop(columns="_order").reset_index(drop=True)
    return cats


@st.cache_data(show_spinner=False)
def scale_max_map():
    """UNIT_MEASURE code -> scale width (for % of scale normalization)."""
    return {
        "0_TO_4": 4,
        "0_TO_12": 12,
        "0_TO_16": 16,
        "0_TO_40": 40,
        "0_TO_60": 60,
        "0_TO_100": 100,
    }


def readable_name(code, choices):
    """Map an indicator code to its plain-language label."""
    row = choices[choices["INDICATOR"] == code]
    if len(row):
        return row.iloc[0]["label"]
    return code


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def add_designer_footer(fig):
    """A small 'Designed by Josh' footer on every map-type figure."""
    fig.add_annotation(
        text="Designed by Josh",
        x=0.985,
        y=-0.08,
        xref="paper",
        yref="paper",
        showarrow=False,
        xanchor="right",
        font=dict(size=11, color=MUTED),
    )
    return fig


def finalize_figure(fig, blend=False, height=560):
    """Dark-theme styling for every dashboard chart:
    - titles are always centered;
    - the source note is a subtitle under the title (top of the chart), so
      it can never collide with the x-axis label;
    - no drag interactions;
    - maps (``blend=True``) get the publication look: navy background
      #0E2A45, thin country borders, Natural Earth projection, and a
      'Designed by Josh' footer."""
    # Drop any bottom-anchored source annotation added by the src helpers
    # (its paper-relative position collides with the x-axis title in wide
    # dashboard figures) - the note moves to the title subtitle instead.
    if fig.layout.annotations:
        fig.layout.annotations = tuple(
            a for a in fig.layout.annotations if a.text != SOURCE_NOTE
        )

    fig.update_layout(
        dragmode=False,
        template="plotly_dark",
        font=dict(color=TEXT),
        # Fixed height + enough top margin for the title block (title +
        # source subtitle) so downloaded PNGs never truncate it, while the
        # gap between the title and the plot stays small.
        height=height,
        margin=dict(t=110, b=80, l=80, r=40),
        title=dict(
            text=(fig.layout.title.text or ""),
            x=0.5,
            xanchor="center",
            y=0.98,
            yanchor="top",
            font=dict(size=15),
            subtitle=dict(text=SOURCE_NOTE, font=dict(size=11, color=MUTED)),
        ),
    )
    fig.update_annotations(font=dict(color=MUTED))
    if blend:
        # Publication-style map: navy background with thin country borders
        # and the Natural Earth projection - matching the status map. Land
        # without data (e.g. Western Sahara, absent from the dataset) shows
        # in a neutral dark tone so no territory is missing.
        fig.update_layout(
            paper_bgcolor=NAVY,
            plot_bgcolor=NAVY,
            # Tight margins: the map fills the panel, not confined in padding.
            margin=dict(l=20, r=20, t=120, b=80),
        )
        fig.update_geos(
            bgcolor=NAVY,
            oceancolor=NAVY,
            landcolor=LAND_DARK,
            projection_type="natural earth",
            showcountries=True,
            countrycolor="rgba(255,255,255,0.25)",
            countrywidth=0.4,
        )
        # The Freedom House colour language for numeric maps too:
        # purple (less free) -> gold (middle) -> green (more free), matching
        # the status map's palette instead of the default blue/red gradient.
        if fig.layout.coloraxis is not None:
            fig.layout.coloraxis.colorscale = [
                [0.0, FH_STATUS_COLORS["Not Free"]],
                [0.5, FH_STATUS_COLORS["Partly Free"]],
                [1.0, FH_STATUS_COLORS["Free"]],
            ]
        add_designer_footer(fig)
    return fig


def render_chart(fig, key=None):
    """Render a chart in a card (called inside a container)."""
    st.plotly_chart(
        finalize_figure(fig),
        width="stretch",
        config=CHART_CONFIG,
        key=key,
    )


def chart_card(fig, caption=None, key=None):
    """A bordered card holding one chart - used for all non-map charts.
    The chart's own centered title (with its source subtitle) is the single
    heading; there is no separate card heading."""
    with st.container(border=True):
        render_chart(fig, key=key)
        if caption:
            st.caption(caption)
    return None


def render_map(fig, caption=None, key=None, height=560):
    """Render a map full-width, NO container card, publication navy look,
    zoom disabled. ``height`` lets a page enlarge specific scopes (e.g. the
    Africa map)."""
    st.plotly_chart(
        finalize_figure(fig, blend=True, height=height),
        width="stretch",
        config=CHART_CONFIG,
        key=key,
    )
    if caption:
        st.caption(caption)
    return None


def build_status_map(data, year, scope="world"):
    """Publication-style Freedom-in-the-World status map.

    Navy background (#0E2A45), the three Freedom House colours, a Natural
    Earth projection with thin country borders, a simple categorical legend
    (Free / Partly Free / Not Free) and a Country | Status | Year hover.
    ``data`` must have REF_AREA, Economy, Year and a 'classification'
    column (Free / Partly Free / Not Free). The classifications come from
    the dataset's own STATUS indicator - nothing is hard-coded.
    """
    import plotly.express as px

    fig = px.choropleth(
        data,
        locations="REF_AREA",
        color="classification",
        locationmode="ISO-3",
        color_discrete_map=FH_STATUS_COLORS,
        category_orders={"classification": ["Free", "Partly Free", "Not Free"]},
        hover_name="Economy",
        custom_data=["classification", "Year"],
        scope=scope,
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Status: %{customdata[0]}<br>"
            "Year: %{customdata[1]}<extra></extra>"
        )
    )
    fig.update_layout(
        title=dict(
            # Dynamic heading: the Africa scope is titled for Africa, not
            # "Freedom in the World" again.
            text=(
                f"FREEDOM IN AFRICA {year}"
                if scope == "africa"
                else f"FREEDOM IN THE WORLD {year}"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=24, color="#ffffff"),
            subtitle=dict(
                text="Freedom status by economy",
                font=dict(size=13, color=MUTED),
            ),
        ),
        paper_bgcolor=NAVY,
        font=dict(color="#ffffff"),
        margin=dict(l=20, r=20, t=120, b=70),
        legend=dict(
            title="",
            orientation="v",
            x=1.0,
            y=1.0,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color="#ffffff"),
        ),
        geo=dict(
            scope=scope,
            projection_type="natural earth",
            bgcolor=NAVY,
            oceancolor=NAVY,
            landcolor=LAND_DARK,
            showcountries=True,
            countrycolor="rgba(255,255,255,0.25)",
            countrywidth=0.4,
            showframe=False,
            showcoastlines=False,
        ),
    )
    fig.add_annotation(
        text="Source: Freedom House, Freedom in the World — World Bank Data360",
        x=0.02,
        y=-0.08,
        xref="paper",
        yref="paper",
        showarrow=False,
        xanchor="left",
        font=dict(size=11, color=MUTED),
    )
    add_designer_footer(fig)
    return fig


def render_publication_map(fig, file_name, key=None):
    """Render the publication-style status map full-width (no zoom, PNG-only
    modebar) and provide a Download Map button that exports a clean,
    high-resolution PNG of exactly the map figure - title, legend and source
    included - with none of the surrounding Streamlit UI.

    The kaleido export fetches plotly's CDN topojson, which can hiccup on
    a flaky network - the map itself must never be taken down by a failed
    download, so the export is retried once and then degrades gracefully."""
    fig.update_layout(dragmode=False)
    st.plotly_chart(
        fig,
        width="stretch",
        config=CHART_CONFIG,
        key=key,
    )
    for attempt in (1, 2):
        try:
            png = fig.to_image(format="png", width=1400, height=900, scale=2)
            break
        except Exception:
            if attempt == 2:
                st.caption(
                    "PNG export is unavailable right now — use the camera "
                    "button in the chart's top-right corner instead."
                )
                return None
    st.download_button(
        "Download Map (PNG)",
        data=png,
        file_name=f"{file_name}.png",
        mime="image/png",
        key=f"{key}_download" if key else None,
    )
    return None


def semantic_colorbar(fig, kind="level"):
    """Replace raw numeric colorbar ticks with plain-language labels.

    ``kind='level'`` -> "Not free" / "Free" at the ends.
    ``kind='change'`` -> "Declined" / "No change" / "Improved".

    The exact values stay available in the hover tooltip. Handles both
    figure styles used in the dashboard: choropleths (px stores the range
    on the shared ``layout.coloraxis``) and heatmaps (go.Heatmap keeps
    ``zmin``/``zmax`` on the trace).
    """
    trace = fig.data[0]
    if getattr(trace, "coloraxis", None):
        coloraxis = fig.layout.coloraxis
        low, high = coloraxis.cmin, coloraxis.cmax
        colorbar = coloraxis.colorbar
    else:
        # Note: 0 is a valid range bound - test for None explicitly, never
        # with `or` (0 or None evaluates to None).
        low = getattr(trace, "zmin", None)
        if low is None:
            low = getattr(trace, "cmin", None)
        high = getattr(trace, "zmax", None)
        if high is None:
            high = getattr(trace, "cmax", None)
        colorbar = trace.colorbar
    if low is None or high is None:
        return fig
    colorbar.title = ""
    if kind == "change":
        colorbar.tickvals = [low, 0, high]
        colorbar.ticktext = ["Declined", "No change", "Improved"]
    else:
        colorbar.tickvals = [low, (low + high) / 2, high]
        colorbar.ticktext = ["Not free", "", "Free"]
    return fig


def section_header(text):
    """A consistent section heading."""
    st.markdown(f"### {text}")


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def inject_branding():
    """Streamlit logo on every page: full mark + wordmark when the sidebar
    is expanded, mark-only when collapsed. Paths are script-relative because
    st.logo resolves relative paths against the working directory."""
    st.logo(
        str(ASSETS_DIR / "streamlit-logo.png"),
        icon_image=str(ASSETS_DIR / "streamlit-mark.png"),
        size="large",
    )


def inject_style():
    """Consistent dark-theme CSS: black page, white text, amber accents.
    Also applies the sidebar branding (called by every page)."""
    inject_branding()
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: #000000; }}
        [data-testid="stMetricValue"] {{ color: {TEXT}; }}
        [data-testid="stMetricDelta"] {{ color: {ACCENT}; }}
        h1, h2, h3 {{ color: {TEXT}; }}
        .stCaption, [data-testid="stCaptionContainer"] {{ color: {MUTED}; }}
        [data-testid="stMetric"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 14px 18px;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: {BORDER};
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.5);
        }}
        [data-testid="stSidebar"] {{
            background: #0a0a0a;
            border-right: 1px solid {BORDER};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
