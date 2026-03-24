from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px

from src.ui import style_plotly

SEVERITY_LABEL_MAP = {
    "Fatal": "Fatal",
    "Grievous": "Serious Injury",
    "Minor": "Minor Injury",
}


def plot_severity(df: pd.DataFrame):
    view = df.copy()
    view["severity_label"] = view["severity_target"].map(lambda x: SEVERITY_LABEL_MAP.get(str(x), str(x)))
    fig = px.pie(view, names="severity_label", hole=0.56, title="Severity Distribution")
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return style_plotly(fig)


def plot_monthly(df: pd.DataFrame):
    g = df.groupby(["year", "month_num", "severity_target"]).size().reset_index(name="count")
    g = g.sort_values(["year", "month_num"])
    g["severity_label"] = g["severity_target"].map(lambda x: SEVERITY_LABEL_MAP.get(str(x), str(x)))
    g["period"] = pd.to_datetime(dict(year=g["year"].astype(int), month=g["month_num"].astype(int), day=1))
    fig = px.line(g, x="period", y="count", color="severity_label", markers=True, title="Month-wise Severity Trend")
    fig.update_xaxes(tickformat="%Y-%m", tickangle=-35, nticks=12)
    return style_plotly(fig)


def plot_top_hotspots(df: pd.DataFrame):
    place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
    view = df.copy()

    if place_col not in view.columns:
        return pd.DataFrame(columns=[place_col, "total", "fatal", "grievous", "minor", "severity_score", "average_score", "fatal_rate"])

    for col in ["FATAL", "GRIEVOUS", "MINOR"]:
        if col not in view.columns:
            view[col] = 0
        view[col] = pd.to_numeric(view[col], errors="coerce").fillna(0)

    # Always calculate row-wise severity_score using required formula:
    # severity_score = (10*FATAL) + (5*GRIEVOUS) + (2*MINOR)
    view["SEVERITY SCORE"] = (10 * view["FATAL"]) + (5 * view["GRIEVOUS"]) + (2 * view["MINOR"])
    view["severity_score"] = view["SEVERITY SCORE"]

    if "FIR NO" not in view.columns:
        view["FIR NO"] = 1

    # total accidents of corridor = number of records for each corridor in filtered data
    view["corridor_total_accidents"] = view.groupby(place_col)["FIR NO"].transform("count")
    safe_corridor_total = view["corridor_total_accidents"].where(view["corridor_total_accidents"] > 0, 1)
    # Row-wise average contribution requested by user:
    # average_score(row) = severity_score(row) / total accidents of that corridor
    calculated_avg_row = view["severity_score"] / safe_corridor_total

    # If an AVERAGE_SCORE-like column exists and matches the formula, use it.
    def _normalize_avg_col_name(name: str) -> str:
        return "".join(ch for ch in str(name).lower() if ch.isalnum())

    average_score_src = next((c for c in view.columns if _normalize_avg_col_name(c) == "averagescore"), None)
    if average_score_src is not None:
        provided_avg_row = pd.to_numeric(view[average_score_src], errors="coerce")
        valid = provided_avg_row.notna()
        matches = np.isclose(provided_avg_row, calculated_avg_row, rtol=1e-4, atol=1e-4)
        view["average_score_row"] = np.where(valid & matches, provided_avg_row, calculated_avg_row)
        mismatch_count = int((valid & ~matches).sum())
        provided_count = int(valid.sum())
    else:
        view["average_score_row"] = calculated_avg_row
        mismatch_count = 0
        provided_count = 0

    g = (
        view.groupby(place_col)
        .agg(
            total=("FIR NO", "count"),
            fatal=("FATAL", "sum"),
            grievous=("GRIEVOUS", "sum"),
            minor=("MINOR", "sum"),
            severity_score=("severity_score", "sum"),
            average_score=("average_score_row", "sum"),
        )
        .reset_index()
    )
    g["fatal_rate"] = (g["fatal"] / g["total"]).fillna(0)
    g["average_score"] = g["average_score"].fillna(0)  # equals severity_score / total
    out = g.sort_values(["average_score", "severity_score", "total"], ascending=False).head(10)
    out.attrs["avg_score_source_column"] = average_score_src or "calculated"
    out.attrs["avg_score_input_rows"] = provided_count
    out.attrs["avg_score_mismatch_rows"] = mismatch_count
    return out
