from __future__ import annotations

import pandas as pd
import plotly.express as px


def plot_severity(df: pd.DataFrame):
    return px.pie(df, names="severity_target", hole=0.5, title="Severity Distribution")


def plot_monthly(df: pd.DataFrame):
    g = df.groupby(["year", "month_num", "severity_target"]).size().reset_index(name="count")
    g["period"] = g["year"].astype(str) + "-" + g["month_num"].astype(int).astype(str).str.zfill(2)
    return px.bar(g, x="period", y="count", color="severity_target", title="Month-wise Severity Split")


def plot_top_hotspots(df: pd.DataFrame):
    place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
    g = df.groupby(place_col).agg(total=("FIR NO", "count"), fatal=("FATAL", "sum")).reset_index()
    g["fatal_rate"] = (g["fatal"] / g["total"]).fillna(0)
    return g.sort_values("total", ascending=False).head(10)
