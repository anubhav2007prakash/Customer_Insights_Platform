"""Chart components for InsightForge AI."""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from utils.helpers import plotly_config
from utils.theme import ThemeEngine


def _base_layout(**extra) -> dict:
    layout = ThemeEngine.chart_layout()
    layout.update(extra)
    return layout


def line_chart(df: pd.DataFrame, x: str, y: str, title: str = "", height: int = 320) -> None:
    """Render a themed line chart."""
    if df.empty:
        st.html('<div class="if-empty-state"><div class="if-empty-title">No trend data yet</div><div class="if-empty-copy">Add a few records to surface a line chart with clearer momentum signals.</div></div>')
        return

    colors = ThemeEngine.active_colors()
    fig = px.line(df, x=x, y=y, title=title)
    fig.update_traces(line=dict(color=colors["chart_1"], width=2.5))
    fig.update_layout(**_base_layout(height=height, showlegend=False, title=dict(text=title, font=dict(size=14))))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def area_chart(df: pd.DataFrame, x: str, y: str, title: str = "", height: int = 320) -> None:
    """Render a themed area chart."""
    if df.empty:
        st.html('<div class="if-empty-state"><div class="if-empty-title">No area data yet</div><div class="if-empty-copy">This workspace will show a richer trend view as soon as data is available.</div></div>')
        return

    colors = ThemeEngine.active_colors()
    fig = px.area(df, x=x, y=y, title=title)
    fig.update_traces(fillcolor="rgba(37,99,235,0.12)", line=dict(color=colors["chart_1"], width=2))
    fig.update_layout(**_base_layout(height=height, showlegend=False))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "", horizontal: bool = False, height: int = 320) -> None:
    """Render a themed bar chart."""
    if df.empty:
        st.html('<div class="if-empty-state"><div class="if-empty-title">No bar data yet</div><div class="if-empty-copy">This chart will appear once the underlying dataset has enough records.</div></div>')
        return

    if horizontal:
        fig = px.bar(df, x=y, y=x, orientation="h", title=title)
    else:
        fig = px.bar(df, x=x, y=y, title=title)
    fig.update_traces(marker_line_width=0, marker=dict(cornerradius=4))
    fig.update_layout(**_base_layout(height=height, showlegend=False))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def pie_chart(df: pd.DataFrame, names: str, values: str, title: str = "", height: int = 320) -> None:
    """Render a donut chart."""
    fig = px.pie(df, names=names, values=values, title=title, hole=0.55)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(**_base_layout(height=height))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def funnel_chart(df: pd.DataFrame, x: str, y: str, title: str = "", height: int = 360) -> None:
    """Render a funnel chart."""
    colors = ThemeEngine.active_colors()
    fig = go.Figure(go.Funnel(
        y=df[y], x=df[x],
        textinfo="value+percent initial",
        marker=dict(color=[colors["chart_1"], colors["chart_2"], colors["chart_3"], colors["chart_4"], colors["chart_5"]]),
    ))
    fig.update_layout(**_base_layout(height=height, title=dict(text=title, font=dict(size=14))))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def heatmap_chart(df: pd.DataFrame, x: str, y: str, z: str, title: str = "", height: int = 360) -> None:
    """Render a heatmap."""
    pivot = df.pivot(index=y, columns=x, values=z)
    colors = ThemeEngine.active_colors()
    fig = px.imshow(pivot, title=title, color_continuous_scale=[[0, colors["neutral_100"]], [1, colors["primary"]]])
    fig.update_layout(**_base_layout(height=height))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def scatter_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, size: str | None = None, height: int = 360) -> None:
    """Render a scatter/bubble chart."""
    fig = px.scatter(df, x=x, y=y, color=color, size=size, opacity=0.75)
    fig.update_traces(marker=dict(line=dict(width=0)))
    fig.update_layout(**_base_layout(height=height))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def treemap_chart(df: pd.DataFrame, path: list[str], values: str, title: str = "", height: int = 360) -> None:
    """Render a treemap."""
    fig = px.treemap(df, path=path, values=values, title=title)
    fig.update_layout(**_base_layout(height=height))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def sunburst_chart(df: pd.DataFrame, path: list[str], values: str, title: str = "", height: int = 360) -> None:
    """Render a sunburst chart."""
    fig = px.sunburst(df, path=path, values=values, title=title)
    fig.update_layout(**_base_layout(height=height))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def sankey_chart(labels: list[str], source: list[int], target: list[int], values: list[int], height: int = 400) -> None:
    """Render a Sankey diagram."""
    colors = ThemeEngine.active_colors()
    fig = go.Figure(go.Sankey(
        node=dict(label=labels, pad=20, thickness=18, color=colors["neutral_200"]),
        link=dict(source=source, target=target, value=values, color="rgba(37,99,235,0.25)"),
    ))
    fig.update_layout(**_base_layout(height=height))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def gauge_chart(value: float, title: str = "", max_val: float = 100, height: int = 280) -> None:
    """Render a gauge indicator."""
    colors = ThemeEngine.active_colors()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14}},
        gauge={
            "axis": {"range": [0, max_val]},
            "bar": {"color": colors["primary"]},
            "bgcolor": colors["neutral_100"],
            "steps": [
                {"range": [0, max_val * 0.5], "color": colors["neutral_100"]},
                {"range": [max_val * 0.5, max_val * 0.8], "color": colors["primary_subtle"]},
            ],
        },
    ))
    fig.update_layout(**_base_layout(height=height))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def radar_chart(categories: list[str], values: list[float], title: str = "", height: int = 360) -> None:
    """Render a radar chart."""
    colors = ThemeEngine.active_colors()
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(37,99,235,0.15)",
        line=dict(color=colors["primary"], width=2),
    ))
    fig.update_layout(**_base_layout(height=height, polar=dict(radialaxis=dict(visible=True))))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def box_plot(df: pd.DataFrame, x: str, y: str, title: str = "", height: int = 320) -> None:
    """Render a box plot."""
    fig = px.box(df, x=x, y=y, title=title)
    fig.update_layout(**_base_layout(height=height))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def histogram_chart(df: pd.DataFrame, x: str, title: str = "", height: int = 320) -> None:
    """Render a histogram."""
    fig = px.histogram(df, x=x, title=title, nbins=30)
    fig.update_traces(marker=dict(cornerradius=2))
    fig.update_layout(**_base_layout(height=height))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def geo_map(df: pd.DataFrame, lat: str, lon: str, size: str, title: str = "", height: int = 400) -> None:
    """Render a geographic bubble map."""
    fig = px.scatter_geo(
        df, lat=lat, lon=lon, size=size,
        hover_name="city" if "city" in df.columns else None,
        title=title,
        projection="natural earth",
    )
    fig.update_layout(**_base_layout(height=height))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def multi_line_chart(df: pd.DataFrame, x: str, y_cols: list[str], title: str = "", height: int = 340) -> None:
    """Render multiple line series."""
    fig = go.Figure()
    for col in y_cols:
        fig.add_trace(go.Scatter(x=df[x], y=df[col], mode="lines", name=col, line=dict(width=2)))
    fig.update_layout(**_base_layout(height=height, legend=dict(orientation="h", y=1.1)))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def forecast_chart(df: pd.DataFrame, x: str, y: str, lower: str, upper: str, height: int = 340) -> None:
    """Render forecast with confidence band."""
    colors = ThemeEngine.active_colors()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x], y=df[upper], mode="lines", line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=df[x], y=df[lower], mode="lines", fill="tonexty",
                             fillcolor="rgba(37,99,235,0.12)", line=dict(width=0), name="Confidence"))
    fig.add_trace(go.Scatter(x=df[x], y=df[y], mode="lines+markers", name="Forecast",
                             line=dict(color=colors["primary"], width=2.5)))
    fig.update_layout(**_base_layout(height=height))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())
