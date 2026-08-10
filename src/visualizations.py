"""Reusable Plotly visualization functions.

Every chart follows the project's chart standard: meaningful title, clear
axis labels, useful hover info, and a source note. Notebooks call these
helpers instead of re-implementing the styling.
"""

SOURCE_NOTE = "Source: Freedom House, Freedom in the World (World Bank Data360)"


def _apply_standard_styling(fig):
    """Shared layout: white template, centered title, source footnote."""
    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        hovermode="x unified",
        margin=dict(b=90),
    )
    fig.add_annotation(
        text=SOURCE_NOTE,
        x=0,
        y=-0.18,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=10, color="#666666"),
        xanchor="left",
    )
    return fig


def create_trend_chart(data, title, y_label):
    """Create a styled line chart of Score over Year.

    ``data`` must be a DataFrame with integer ``Year`` and numeric
    ``Score`` columns (typically already aggregated, e.g. the global
    mean per year).
    """
    import plotly.express as px

    fig = px.line(
        data,
        x="Year",
        y="Score",
        markers=True,
        title=title,
        labels={"Score": y_label, "Year": "Year"},
    )
    return _apply_standard_styling(fig)


def create_multi_trend_chart(data, title, y_label, group_col="Economy", value_col="Score"):
    """Create a styled multi-line chart, one line per group member.

    ``data`` must have integer ``Year``, numeric ``value_col``, and a
    ``group_col`` column (e.g. Economy) identifying the series.
    """
    import plotly.express as px

    fig = px.line(
        data,
        x="Year",
        y=value_col,
        color=group_col,
        markers=True,
        title=title,
        labels={value_col: y_label, "Year": "Year"},
    )
    return _apply_standard_styling(fig)


def create_heatmap(pivot, title, colorbar_label, colorscale="RdBu_r", zmin=None, zmax=None):
    """Create a styled heatmap from a pivot table.

    ``pivot`` is a DataFrame whose rows are the y-axis categories, whose
    columns are the x-axis categories, and whose values are numeric.
    The y-axis is reversed so the first row appears at the top.
    ``zmin``/``zmax`` fix the colour range so separate heatmaps are
    directly comparable (the project's consistency rule).
    """
    import plotly.graph_objects as go

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale=colorscale,
            colorbar={"title": colorbar_label},
            zmin=zmin,
            zmax=zmax,
            hovertemplate="%{y} | %{x}: %{z:.1f}<extra></extra>",
        )
    )
    fig.update_layout(title=title, yaxis_autorange="reversed")
    return _apply_standard_styling(fig)


def create_choropleth(
    data,
    location_col,
    color_col,
    title="",
    colorbar_label="",
    scope="world",
    colorscale="RdBu_r",
    range_color=None,
    hover_name="Economy",
    color_discrete_map=None,
    fitbounds=False,
):
    """Create a styled Plotly choropleth map.

    ``data`` must have ISO-3 location codes (``location_col``), a color
    column, and an economy-name column for hover. The dataset's Data360
    codes are ISO-3 compatible (verified: all 197 render, including XKX
    Kosovo and TWN Taiwan). For numeric colors, ``range_color`` fixes the
    scale so separate maps are directly comparable; for categorical colors
    pass ``color_discrete_map`` (e.g. status maps).
    """
    import plotly.express as px

    if color_discrete_map is not None:
        fig = px.choropleth(
            data,
            locations=location_col,
            color=color_col,
            locationmode="ISO-3",
            scope=scope,
            hover_name=hover_name,
            title=title,
            color_discrete_map=color_discrete_map,
        )
    else:
        fig = px.choropleth(
            data,
            locations=location_col,
            color=color_col,
            locationmode="ISO-3",
            scope=scope,
            hover_name=hover_name,
            title=title,
            color_continuous_scale=colorscale,
            range_color=range_color,
            labels={color_col: colorbar_label},
        )

    if fitbounds:
        fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(template="plotly_white", title_x=0.5, margin=dict(b=60))
    fig.add_annotation(
        text=SOURCE_NOTE,
        x=0,
        y=-0.1,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=10, color="#666666"),
        xanchor="left",
    )
    return fig
