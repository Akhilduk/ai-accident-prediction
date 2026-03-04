from __future__ import annotations

import pandas as pd
import plotly.express as px

from src.ui import style_plotly


def plot_severity(df: pd.DataFrame):
    fig = px.pie(df, names="severity_target", hole=0.56, title="Severity Distribution")
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return style_plotly(fig)


def plot_monthly(df: pd.DataFrame):
    g = df.groupby(["year", "month_num", "severity_target"]).size().reset_index(name="count")
    g = g.sort_values(["year", "month_num"])
    g["period"] = pd.to_datetime(dict(year=g["year"].astype(int), month=g["month_num"].astype(int), day=1))
    fig = px.line(g, x="period", y="count", color="severity_target", markers=True, title="Month-wise Severity Trend")
    fig.update_xaxes(tickformat="%Y-%m", tickangle=-35, nticks=12)
    return style_plotly(fig)


def plot_top_hotspots(df: pd.DataFrame):
    place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
    g = df.groupby(place_col).agg(total=("FIR NO", "count"), fatal=("FATAL", "sum")).reset_index()
    g["fatal_rate"] = (g["fatal"] / g["total"]).fillna(0)
    return g.sort_values("total", ascending=False).head(10)
