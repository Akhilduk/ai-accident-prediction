from __future__ import annotations

import re
import warnings
import numpy as np
import pandas as pd

from src.config import REQUIRED_COLUMNS, YES_NO_FIELDS
from src.master_reference import load_master_reference


SEVERITY_MAP = {"F": "Fatal", "M": "Minor", "G": "Grievous"}
MIN_YEAR = 2000
MAX_YEAR = pd.Timestamp.now().year + 1



def _header_key(name: str) -> str:
    s = str(name).strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*/\s*", "/", s)
    return s.upper()


def _canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    expected = REQUIRED_COLUMNS
    expected_key_to_name = {_header_key(c): c for c in expected}
    rename_map = {}
    for col in df.columns:
        key = _header_key(col)
        if key in expected_key_to_name:
            rename_map[col] = expected_key_to_name[key]
    return df.rename(columns=rename_map)


def _parse_mixed_dates(series: pd.Series) -> pd.Series:
    s = series.copy()
    parsed = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")

    # Handle Excel serial dates (e.g., 45123) before generic parsing.
    numeric = pd.to_numeric(s, errors="coerce")
    excel_mask = numeric.between(20000, 80000, inclusive="both")
    if excel_mask.any():
        parsed.loc[excel_mask] = pd.to_datetime(numeric.loc[excel_mask], unit="D", origin="1899-12-30", errors="coerce")

    # First pass: day-first covers formats like 16-03-2021 and 2/8/2023 meaning 2-Aug-2023.
    unresolved = parsed.isna()
    if unresolved.any():
        parsed1 = pd.to_datetime(s.loc[unresolved], errors="coerce", dayfirst=True)
        parsed.loc[unresolved] = parsed1
    # Second pass for unresolved values in case some are month-first (e.g., 08/02/2023).
    unresolved = parsed.isna()
    if unresolved.any():
        parsed2 = pd.to_datetime(s[unresolved], errors="coerce", dayfirst=False)
        parsed.loc[unresolved] = parsed2
    return parsed


def _parse_month_value(series: pd.Series) -> pd.Series:
    month_map = {
        "jan": 1,
        "january": 1,
        "feb": 2,
        "february": 2,
        "mar": 3,
        "march": 3,
        "apr": 4,
        "april": 4,
        "may": 5,
        "jun": 6,
        "june": 6,
        "jul": 7,
        "july": 7,
        "aug": 8,
        "august": 8,
        "sep": 9,
        "sept": 9,
        "september": 9,
        "oct": 10,
        "october": 10,
        "nov": 11,
        "november": 11,
        "dec": 12,
        "december": 12,
    }
    numeric = pd.to_numeric(series, errors="coerce")
    text = series.astype(str).str.strip().str.lower().map(month_map)
    out = numeric.fillna(text)
    return out.clip(lower=1, upper=12)


def _normalize_day_name(series: pd.Series) -> pd.Series:
    day_map = {
        "mon": "Monday",
        "monday": "Monday",
        "tue": "Tuesday",
        "tues": "Tuesday",
        "tuesday": "Tuesday",
        "wed": "Wednesday",
        "wednesday": "Wednesday",
        "thu": "Thursday",
        "thur": "Thursday",
        "thurs": "Thursday",
        "thursday": "Thursday",
        "fri": "Friday",
        "friday": "Friday",
        "sat": "Saturday",
        "saturday": "Saturday",
        "sun": "Sunday",
        "sunday": "Sunday",
    }
    return series.astype(str).str.strip().str.lower().map(day_map)


def _extract_hour_minute(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    hour = pd.Series(np.nan, index=series.index, dtype="float64")
    minute = pd.Series(np.nan, index=series.index, dtype="float64")
    text = series.astype(str).str.strip()

    # Handles values like 8.5, 11.15, 20.3 where decimal part encodes minutes (5 -> 50, 3 -> 30).
    decimal_like = text.str.match(r"^\d{1,2}(\.\d{1,2})?$", na=False)
    if decimal_like.any():
        parts = text[decimal_like].str.split(".", n=1, expand=True)
        h = pd.to_numeric(parts[0], errors="coerce")
        m_raw = parts[1].fillna("0")
        m = pd.to_numeric(m_raw, errors="coerce")
        one_digit = m_raw.str.len() == 1
        m.loc[one_digit] = m.loc[one_digit] * 10
        h = h.clip(lower=0, upper=23)
        m = m.clip(lower=0, upper=59)
        hour.loc[decimal_like] = h
        minute.loc[decimal_like] = m

    unresolved = hour.isna() | minute.isna()
    if unresolved.any():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            parsed = pd.to_datetime(text[unresolved], errors="coerce")
        hour.loc[unresolved] = parsed.dt.hour
        minute.loc[unresolved] = parsed.dt.minute

    return hour, minute


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
    fir_missing = df["FIR NO"].isna() if "FIR NO" in df.columns else pd.Series(False, index=df.index)
    if {"Latitude", "Longitude"}.issubset(df.columns):
        latlon_missing = df["Latitude"].isna() & df["Longitude"].isna()
    else:
        latlon_missing = pd.Series(False, index=df.index)
    toc_text = (
        df["TYPE OF COLLISION"].astype(str).str.lower().str.strip()
        if "TYPE OF COLLISION" in df.columns
        else pd.Series("", index=df.index)
    )
    legend_rows = toc_text.str.contains("type of vehicle", na=False) | toc_text.str.startswith("1-motorised", na=False)
    mask_drop = (fir_missing & latlon_missing) | legend_rows
    return df.loc[~mask_drop].copy(), int(mask_drop.sum())


def _decode_code(series: pd.Series, mapping: dict[int, str]) -> tuple[pd.Series, pd.Series]:
    code = pd.to_numeric(series, errors="coerce").astype("Int64")
    label = code.map(mapping).fillna("Unknown/Out-of-master")
    flag = label.eq("Unknown/Out-of-master")
    return code, label.where(~code.isna(), np.nan), flag


def clean_data(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = _canonicalize_columns(raw_df.copy())
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan
    df, removed = _clean_footer_rows(df)

    for col in YES_NO_FIELDS:
        if col in df:
            df[col] = df[col].map(_normalize_yes_no)

    df["D/N"] = (
        df["D/N"]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace("DAY", "D", regex=False)
        .str.replace("NIGHT", "N", regex=False)
        .str[0]
    )
    df.loc[~df["D/N"].isin(["D", "N"]), "D/N"] = np.nan
    df["day_night_label"] = df["D/N"].map({"D": "Day", "N": "Night"}).fillna("Unknown")

    df["GEOMETRY"] = df["GEOMETRY"].astype(str).str.strip().str.lower().replace({"straight\\t": "straight"})
    df["GEOMETRY"] = df["GEOMETRY"].replace({"curve ": "curve", "straight ": "straight"})
    df["JN/NOT"] = df["JN/NOT"].map(_normalize_yes_no)

    parsed_date = _parse_mixed_dates(df["Date"])
    df["year"] = parsed_date.dt.year
    df["month_num"] = parsed_date.dt.month
    df["day"] = parsed_date.dt.day
    df["day_of_week"] = parsed_date.dt.day_name()

    # Fallbacks from explicit columns to preserve as many rows as possible.
    year_fallback = pd.to_numeric(df["Year of Accident"], errors="coerce")
    month_fallback = _parse_month_value(df["Month of the year"])
    dow_fallback = _normalize_day_name(df["DAY OF THE WEEK"])
    df["year"] = df["year"].fillna(year_fallback)
    df["month_num"] = df["month_num"].fillna(month_fallback)
    df["day_of_week"] = df["day_of_week"].fillna(dow_fallback)
    df["day"] = df["day"].fillna(1)
    df.loc[(df["year"] < MIN_YEAR) | (df["year"] > MAX_YEAR), "year"] = np.nan

    date_from_parts = pd.to_datetime(
        dict(
            year=pd.to_numeric(df["year"], errors="coerce"),
            month=pd.to_numeric(df["month_num"], errors="coerce"),
            day=pd.to_numeric(df["day"], errors="coerce"),
        ),
        errors="coerce",
    )
    df["Date"] = parsed_date.fillna(date_from_parts)
    df["week_of_year"] = df["Date"].dt.isocalendar().week.astype("Int64")

    df["hour"], df["minute"] = _extract_hour_minute(df["Time"])
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
    df["is_night"] = np.where(
        df["day_night_label"].eq("Night") | df["hour"].isin([0, 1, 2, 3, 4, 5, 20, 21, 22, 23]), 1, 0
    )

    df["severity_target"] = df["SEVERITY"].astype(str).str.strip().str.upper().map(SEVERITY_MAP)
    df.loc[df["severity_target"].isna(), "severity_target"] = df["SEVERITY"].astype(str).str.strip()

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        non_null = df[col].dropna()
        if not non_null.empty:
            df[col] = df[col].fillna(non_null.median())

    categorical_cols = [c for c in df.columns if c not in numeric_cols]
    for col in categorical_cols:
        if df[col].isna().any():
            mode = df[col].mode(dropna=True)
            fill = mode.iloc[0] if not mode.empty else "Unknown"
            if pd.api.types.is_categorical_dtype(df[col]) and fill not in df[col].cat.categories:
                df[col] = df[col].cat.add_categories([fill])
            df[col] = df[col].fillna(fill)

    info = {"removed_footer_rows": removed, "rows_after_cleaning": len(df)}
    return df, info
