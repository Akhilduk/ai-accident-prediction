from __future__ import annotations

import calendar
from datetime import date

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor


def _build_monthly_history(df: pd.DataFrame) -> pd.DataFrame:
    place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
    base = (
        df.groupby([place_col, "year", "month_num"], dropna=False)
        .size()
        .reset_index(name="accident_count")
        .dropna(subset=["year", "month_num"])
    )
    if base.empty:
        return base

    base["year"] = base["year"].astype(int)
    base["month_num"] = base["month_num"].astype(int)
    base["month_start"] = pd.to_datetime(dict(year=base["year"], month=base["month_num"], day=1))

    global_min = base["month_start"].min()
    global_max = base["month_start"].max()
    full_months = pd.date_range(global_min, global_max, freq="MS")
    places = sorted(base[place_col].astype(str).unique().tolist())
    full_idx = pd.MultiIndex.from_product([places, full_months], names=[place_col, "month_start"])

    g = (
        base.set_index([place_col, "month_start"])["accident_count"]
        .reindex(full_idx, fill_value=0)
        .rename("accident_count")
        .reset_index()
    )
    g["year"] = g["month_start"].dt.year.astype(int)
    g["month_num"] = g["month_start"].dt.month.astype(int)
    g = g.sort_values([place_col, "month_start"])
    return g


def _build_training_rows(monthly: pd.DataFrame) -> tuple[pd.DataFrame, list[str], str]:
    place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
    m = monthly.copy()
    m["lag_1"] = m.groupby(place_col)["accident_count"].shift(1)
    m["lag_2"] = m.groupby(place_col)["accident_count"].shift(2)
    m["lag_3"] = m.groupby(place_col)["accident_count"].shift(3)
    m["rolling_3"] = (
        m.groupby(place_col)["accident_count"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
    )
    m["trend_idx"] = m.groupby(place_col).cumcount().astype(float)
    m["month_sin"] = np.sin(2 * np.pi * m["month_num"] / 12.0)
    m["month_cos"] = np.cos(2 * np.pi * m["month_num"] / 12.0)
    features = ["year", "month_num", "trend_idx", "month_sin", "month_cos", "lag_1", "lag_2", "lag_3", "rolling_3"]
    train = m.dropna(subset=["lag_1", "lag_2", "lag_3"]).copy()
    return train, features, place_col


def forecast_hotspots(df: pd.DataFrame, years_ahead: int = 5) -> pd.DataFrame:
    monthly = _build_monthly_history(df)
    train, features, place_col = _build_training_rows(monthly)
    horizon = int(max(1, years_ahead) * 12)

    if train.empty:
        latest = monthly.groupby(place_col).tail(1).copy()
        latest["forecast_date"] = latest["month_start"]
        latest["predicted_count"] = latest["accident_count"].clip(lower=0)
        latest["forecast_step"] = 0
        return latest[[place_col, "forecast_date", "year", "month_num", "predicted_count", "forecast_step"]]

    model = GradientBoostingRegressor(random_state=42)
    model.fit(train[features], train["accident_count"])

    rows: list[dict] = []
    for place, grp in monthly.groupby(place_col):
        grp = grp.sort_values("month_start")
        history = grp["accident_count"].astype(float).tolist()
        last_date = grp["month_start"].max()
        trend_idx = float(len(history))
        for step in range(1, horizon + 1):
            next_date = last_date + pd.DateOffset(months=1)
            month_num = int(next_date.month)
            year = int(next_date.year)
            lag_1 = history[-1] if len(history) >= 1 else 0.0
            lag_2 = history[-2] if len(history) >= 2 else lag_1
            lag_3 = history[-3] if len(history) >= 3 else lag_2
            rolling_3 = float(np.mean(history[-3:])) if history else 0.0
            row = pd.DataFrame(
                [
                    {
                        "year": year,
                        "month_num": month_num,
                        "trend_idx": trend_idx,
                        "month_sin": np.sin(2 * np.pi * month_num / 12.0),
                        "month_cos": np.cos(2 * np.pi * month_num / 12.0),
                        "lag_1": lag_1,
                        "lag_2": lag_2,
                        "lag_3": lag_3,
                        "rolling_3": rolling_3,
                    }
                ]
            )
            pred = float(max(0.0, model.predict(row[features])[0]))
            history.append(pred)
            trend_idx += 1.0
            rows.append(
                {
                    place_col: place,
                    "forecast_date": next_date,
                    "year": year,
                    "month_num": month_num,
                    "predicted_count": pred,
                    "forecast_step": step,
                }
            )
            last_date = next_date

    return pd.DataFrame(rows).sort_values(["forecast_date", "predicted_count"], ascending=[True, False])


def monthly_hotspot_ranking(forecast_df: pd.DataFrame, target_year: int, target_month: int) -> pd.DataFrame:
    place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
    m = forecast_df[(forecast_df["year"] == int(target_year)) & (forecast_df["month_num"] == int(target_month))].copy()
    m = m.sort_values("predicted_count", ascending=False)
    m["rank"] = range(1, len(m) + 1)
    return m[[place_col, "year", "month_num", "predicted_count", "rank"]]


def date_hotspot_ranking(df_hist: pd.DataFrame, forecast_df: pd.DataFrame, target_date: date) -> pd.DataFrame:
    place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
    month_rank = monthly_hotspot_ranking(forecast_df, target_date.year, target_date.month)
    if month_rank.empty:
        return month_rank

    weekday = pd.Timestamp(target_date).day_name()
    days_in_month = calendar.monthrange(target_date.year, target_date.month)[1]
    daily_base = month_rank["predicted_count"] / float(days_in_month)

    hist = df_hist.copy()
    place_total = hist.groupby(place_col).size().rename("total")
    place_weekday = hist[hist["day_of_week"] == weekday].groupby(place_col).size().rename("weekday_count")
    ratios = pd.concat([place_total, place_weekday], axis=1).fillna(0)
    ratios["weekday_ratio"] = np.where(ratios["total"] > 0, ratios["weekday_count"] / ratios["total"], 0.0)

    global_weekday_ratio = float((hist["day_of_week"] == weekday).mean()) if len(hist) else 0.0
    global_weekday_ratio = max(global_weekday_ratio, 1e-6)

    scored = month_rank.merge(ratios["weekday_ratio"], left_on=place_col, right_index=True, how="left").fillna(0)
    scored["weekday_weight"] = (scored["weekday_ratio"] / global_weekday_ratio).clip(lower=0.5, upper=1.8)
    scored["predicted_daily_risk"] = daily_base.values * scored["weekday_weight"]
    scored = scored.sort_values("predicted_daily_risk", ascending=False)
    scored["rank"] = range(1, len(scored) + 1)
    return scored[[place_col, "year", "month_num", "predicted_daily_risk", "rank"]]
