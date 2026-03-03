from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import YES_NO_FIELDS
from src.master_reference import load_master_reference


SEVERITY_MAP = {"F": "Fatal", "M": "Minor", "G": "Grievous"}


def _normalize_yes_no(value):
    if pd.isna(value):
        return np.nan
    v = str(value).strip().lower()
    if v in {"ys", "y", "yes"}:
        return "yes"
    if v in {"n", "no"}:
        return "no"
    return v


def _clean_footer_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    fir_missing = df["FIR NO"].isna()
    latlon_missing = df["Latitude"].isna() & df["Longitude"].isna()
    toc_text = df["TYPE OF COLLISION"].astype(str).str.lower().str.strip()
    legend_rows = toc_text.str.contains("type of vehicle", na=False) | toc_text.str.startswith("1-motorised", na=False)
    mask_drop = (fir_missing & latlon_missing) | legend_rows
    return df.loc[~mask_drop].copy(), int(mask_drop.sum())


def _decode_code(series: pd.Series, mapping: dict[int, str]) -> tuple[pd.Series, pd.Series]:
    code = pd.to_numeric(series, errors="coerce").astype("Int64")
    label = code.map(mapping).fillna("Unknown/Out-of-master")
    flag = label.eq("Unknown/Out-of-master")
    return code, label.where(~code.isna(), np.nan), flag


def clean_data(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df, removed = _clean_footer_rows(raw_df)

    for col in YES_NO_FIELDS:
        if col in df:
            df[col] = df[col].map(_normalize_yes_no)

    df["D/N"] = df["D/N"].astype(str).str.strip().str.upper().str[0]
    df.loc[~df["D/N"].isin(["D", "N"]), "D/N"] = np.nan

    df["GEOMETRY"] = df["GEOMETRY"].astype(str).str.strip().str.lower().replace({"straight\\t": "straight"})
    df["GEOMETRY"] = df["GEOMETRY"].replace({"curve ": "curve", "straight ": "straight"})
    df["JN/NOT"] = df["JN/NOT"].map(_normalize_yes_no)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    df["year"] = df["Date"].dt.year
    df["month_num"] = df["Date"].dt.month
    df["day"] = df["Date"].dt.day
    df["day_of_week"] = df["Date"].dt.day_name()
    df["week_of_year"] = df["Date"].dt.isocalendar().week.astype("Int64")

    t = pd.to_datetime(df["Time"].astype(str).str.strip(), errors="coerce")
    df["hour"] = t.dt.hour
    df["minute"] = t.dt.minute
    df["time_bucket"] = pd.cut(
        df["hour"], bins=[-0.1, 6, 12, 18, 24], labels=["0-6", "6-12", "12-18", "18-24"], right=False
    )

    refs = load_master_reference()
    for src, dst, mapping in [
        ("PATTERN OF COLLISION", "PATTERN_OF_COLLISION", refs["Pattern of Collision"]),
        ("TYPE OF COLLISION", "TYPE_OF_COLLISION", refs["Type of Collision"]),
        ("TYPE OF VEHICLE-1", "TYPE_OF_VEHICLE_1", refs["Type of Vehicle"]),
        ("TYPE OF VEHICLE-2", "TYPE_OF_VEHICLE_2", refs["Type of Vehicle"]),
    ]:
        df[f"{dst}_CODE"], df[f"{dst}_LABEL"], df[f"{dst}_UNKNOWN"] = _decode_code(df[src], mapping)

    df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)
    df["is_night"] = np.where(df["D/N"].eq("N") | df["hour"].isin([0, 1, 2, 3, 4, 5, 20, 21, 22, 23]), 1, 0)

    df["severity_target"] = df["SEVERITY"].astype(str).str.strip().str.upper().map(SEVERITY_MAP)
    df.loc[df["severity_target"].isna(), "severity_target"] = df["SEVERITY"].astype(str).str.strip()

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    categorical_cols = [c for c in df.columns if c not in numeric_cols]
    for col in categorical_cols:
        if df[col].isna().any():
            mode = df[col].mode(dropna=True)
            fill = mode.iloc[0] if not mode.empty else "Unknown"
            df[col] = df[col].fillna(fill)

    info = {"removed_footer_rows": removed, "rows_after_cleaning": len(df)}
    return df, info
