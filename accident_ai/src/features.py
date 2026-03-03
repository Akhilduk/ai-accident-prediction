from __future__ import annotations

import pandas as pd


def build_hotspot_features(df: pd.DataFrame) -> pd.DataFrame:
    place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
    g = (
        df.groupby([place_col, "year", "month_num"], dropna=False)
        .size()
        .reset_index(name="accident_count")
        .sort_values([place_col, "year", "month_num"])
    )
    g["lag_1"] = g.groupby(place_col)["accident_count"].shift(1)
    g["lag_2"] = g.groupby(place_col)["accident_count"].shift(2)
    g["rolling_3"] = (
        g.groupby(place_col)["accident_count"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
    )
    g = g.fillna(0)
    return g
