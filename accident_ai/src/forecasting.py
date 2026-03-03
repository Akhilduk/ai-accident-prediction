from __future__ import annotations

import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

from src.features import build_hotspot_features


def forecast_hotspots(df: pd.DataFrame) -> pd.DataFrame:
    place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
    feat = build_hotspot_features(df)
    features = ["month_num", "lag_1", "lag_2", "rolling_3"]
    if len(feat) < 6:
        out = feat[[place_col, "year", "month_num", "accident_count"]].copy()
        out["predicted_next_month_count"] = out["accident_count"]
        return out

    model = GradientBoostingRegressor(random_state=42)
    model.fit(feat[features], feat["accident_count"])

    latest = feat.sort_values([place_col, "year", "month_num"]).groupby(place_col).tail(1).copy()
    latest["month_num"] = ((latest["month_num"] % 12) + 1).astype(int)
    latest["predicted_next_month_count"] = model.predict(latest[features]).clip(min=0)
    return latest[[place_col, "year", "month_num", "predicted_next_month_count"]].sort_values(
        "predicted_next_month_count", ascending=False
    )
