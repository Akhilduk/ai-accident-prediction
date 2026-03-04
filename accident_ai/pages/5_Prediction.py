from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from src.cleaning import clean_data
from src.data_io import get_active_dataset, load_excel_cached
from src.forecasting import date_hotspot_ranking, forecast_hotspots, monthly_hotspot_ranking
from src.modeling import load_best_model
from src.ui import apply_theme, style_plotly

PLACE_COL = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
PLACE_LABEL = "Jurisdiction / Place"
SEVERITY_LABEL_MAP = {
    "Fatal": "Fatal",
    "Grievous": "Serious Injury",
    "Minor": "Minor Injury",
}


def _apply_filter(df: pd.DataFrame, col: str, values: list) -> pd.DataFrame:
    if not values:
        return df
    if pd.api.types.is_numeric_dtype(df[col]):
        return df[df[col].isin(values)]
    return df[df[col].astype(str).isin([str(v) for v in values])]


def _scenario_defaults(df: pd.DataFrame) -> dict:
    default_place = str(df[PLACE_COL].mode().iloc[0]) if not df[PLACE_COL].mode().empty else str(df[PLACE_COL].iloc[0])
    default_day = str(df["day_of_week"].mode().iloc[0]) if not df["day_of_week"].mode().empty else "Monday"
    default_month = int(df["month_num"].mode().iloc[0]) if not df["month_num"].mode().empty else 1
    default_time_bucket = str(df["time_bucket"].mode().iloc[0]) if not df["time_bucket"].mode().empty else "12-18"
    default_dn = str(df["D/N"].mode().iloc[0]) if not df["D/N"].mode().empty else "D"
    return {
        PLACE_COL: default_place,
        "day_of_week": default_day,
        "month_num": default_month,
        "time_bucket": default_time_bucket,
        "D/N": default_dn,
        "PATTERN_OF_COLLISION_LABEL": str(df["PATTERN_OF_COLLISION_LABEL"].mode().iloc[0]),
        "TYPE_OF_COLLISION_LABEL": str(df["TYPE_OF_COLLISION_LABEL"].mode().iloc[0]),
        "TYPE_OF_VEHICLE_1_LABEL": str(df["TYPE_OF_VEHICLE_1_LABEL"].mode().iloc[0]),
        "TYPE_OF_VEHICLE_2_LABEL": str(df["TYPE_OF_VEHICLE_2_LABEL"].mode().iloc[0]),
        "GEOMETRY": str(df["GEOMETRY"].mode().iloc[0]),
        "PRESENCE OF MEDIAN": str(df["PRESENCE OF MEDIAN"].mode().iloc[0]),
        "PRESENCE OF SHOULDER": str(df["PRESENCE OF SHOULDER"].mode().iloc[0]),
        "PRESENCE OF FOOTPATH": str(df["PRESENCE OF FOOTPATH"].mode().iloc[0]),
        "JN/NOT": str(df["JN/NOT"].mode().iloc[0]),
        "Distance": float(df["Distance"].median()),
        "NO. OF VEHICLE": float(df["NO. OF VEHICLE"].median()),
    }


def _historical_month_ranking(df_hist: pd.DataFrame, target_year: int, target_month: int) -> pd.DataFrame:
    m = (
        df_hist[(df_hist["year"].astype(int) == int(target_year)) & (df_hist["month_num"].astype(int) == int(target_month))]
        .groupby(PLACE_COL)
        .size()
        .reset_index(name="actual_count")
        .sort_values("actual_count", ascending=False)
    )
    m["year"] = int(target_year)
    m["month_num"] = int(target_month)
    m["rank"] = range(1, len(m) + 1)
    return m[[PLACE_COL, "year", "month_num", "actual_count", "rank"]]


apply_theme(
    "Prediction Studio",
    icon="PREDICT",
    subtitle="Simple AI predictions for incident severity and future hotspot ranking.",
)

active = get_active_dataset()
if active is None:
    st.warning("No dataset available. Upload data first.")
    st.stop()

df, _ = clean_data(load_excel_cached(str(active)))
section = st.radio(
    "Section",
    ["Severity AI Prediction", "Hotspot Forecast (5 Years)"],
    horizontal=True,
    label_visibility="collapsed",
)

with st.expander("How to Use Prediction Page (Simple)", expanded=False):
    st.markdown(
        """
Choose one section:
1. **Severity AI Prediction**: Predict how serious an accident may be for selected conditions.
2. **Hotspot Forecast (5 Years)**: See which places may have higher accident risk in future months.

**Simple meaning of technical terms**
- **Probability**: Chance of each outcome (higher = more likely).
- **High Severity Risk**: Combined risk of Fatal + Serious Injury.
- **Historical Ranking**: Ranking from actual past data.
- **Predicted Ranking**: Ranking from AI future forecast.
"""
    )



with st.expander("How prediction and forecast numbers are calculated", expanded=False):
    st.markdown(
        """
### Severity AI Prediction section
- Inputs (place, day/night, geometry, collision type, etc.) are converted into model-ready format.
- Model returns probability for each class (Fatal / Serious Injury / Minor).
- **Most likely outcome** = class with highest probability.
- In Area Risk Explorer:
  - App predicts many matching records together.
  - Shows average class probability.
  - **High Severity Risk** = probability(Fatal) + probability(Serious Injury).

### Hotspot Forecast section
- Historical monthly count is built per place.
- Lag features are created (`lag_1`, `lag_2`, `lag_3`, rolling average, trend index, month seasonality).
- Gradient Boosting model predicts future monthly counts up to 5 years.
- Ranking is sorted by predicted count for selected year/month.

### Exact-date risk logic
- Monthly prediction is converted to daily base: `monthly_pred / days_in_month`.
- It is adjusted using historical weekday pattern for that place.
- Final score shown as **predicted_daily_risk** (relative risk-style indicator for comparison across places).

### Axis meaning in prediction charts
- Bar charts: **X-axis = severity/place**, **Y-axis = probability/risk/count**.
- Trend charts: **X-axis = month-year period**, **Y-axis = actual or predicted count**.
"""
    )

if section == "Severity AI Prediction":
    model_bundle = load_best_model()
    if model_bundle is None:
        st.warning("Please train models first from 'Model Training & Comparison'.")
        st.stop()

    features = model_bundle["features"]
    pipe = model_bundle["pipeline"]
    class_labels = list(model_bundle.get("class_labels") or pipe.classes_)
    model_name = model_bundle.get("model_name", "Best trained model")

    st.info(
        f"Using model: {model_name}. Choose either 'Single Incident' for one scenario or 'Area Risk Explorer' for multiple places."
    )
    mode = st.radio(
        "Prediction mode",
        ["Single Incident (easy form)", "Area Risk Explorer (any filter combination)"],
        horizontal=True,
    )

    if mode == "Single Incident (easy form)":
        defaults = _scenario_defaults(df)
        st.caption("If you keep a field as 'Auto', typical value from your historical data is used.")
        with st.form("single_incident_form"):
            c1, c2 = st.columns(2)
            with c1:
                place_options = ["Auto"] + sorted(df[PLACE_COL].astype(str).unique().tolist())
                place_value = st.selectbox(PLACE_LABEL, place_options, help="Area where you want to estimate accident severity risk.")
                selected_date = st.date_input("Date", value=date.today(), help="Used to set month and day-of-week automatically.")
                dn_value = st.selectbox("Time type", ["Auto", "Day", "Night"])
                time_bucket = st.selectbox("Time range", ["Auto", "0-6", "6-12", "12-18", "18-24"])
                geometry = st.selectbox("Road geometry", ["Auto"] + sorted(df["GEOMETRY"].astype(str).unique().tolist()))
                junction = st.selectbox("Junction area", ["Auto", "yes", "no"])
            with c2:
                pattern = st.selectbox(
                    "Collision pattern", ["Auto"] + sorted(df["PATTERN_OF_COLLISION_LABEL"].astype(str).unique().tolist())
                )
                collision = st.selectbox(
                    "Collision type", ["Auto"] + sorted(df["TYPE_OF_COLLISION_LABEL"].astype(str).unique().tolist())
                )
                vehicle_1 = st.selectbox(
                    "Primary vehicle", ["Auto"] + sorted(df["TYPE_OF_VEHICLE_1_LABEL"].astype(str).unique().tolist())
                )
                vehicle_2 = st.selectbox(
                    "Secondary vehicle", ["Auto"] + sorted(df["TYPE_OF_VEHICLE_2_LABEL"].astype(str).unique().tolist())
                )
                median = st.selectbox("Road median present", ["Auto", "yes", "no"])
                shoulder = st.selectbox("Shoulder present", ["Auto", "yes", "no"])
                footpath = st.selectbox("Footpath present", ["Auto", "yes", "no"])

            submitted = st.form_submit_button("Predict Severity", type="primary")

        if submitted:
            row = defaults.copy()
            row["month_num"] = int(pd.Timestamp(selected_date).month)
            row["day_of_week"] = pd.Timestamp(selected_date).day_name()
            row["is_weekend"] = int(row["day_of_week"] in {"Saturday", "Sunday"})
            if place_value != "Auto":
                row[PLACE_COL] = place_value
            if dn_value != "Auto":
                row["D/N"] = "N" if dn_value == "Night" else "D"
            if time_bucket != "Auto":
                row["time_bucket"] = time_bucket
            if pattern != "Auto":
                row["PATTERN_OF_COLLISION_LABEL"] = pattern
            if collision != "Auto":
                row["TYPE_OF_COLLISION_LABEL"] = collision
            if vehicle_1 != "Auto":
                row["TYPE_OF_VEHICLE_1_LABEL"] = vehicle_1
            if vehicle_2 != "Auto":
                row["TYPE_OF_VEHICLE_2_LABEL"] = vehicle_2
            if geometry != "Auto":
                row["GEOMETRY"] = geometry
            if junction != "Auto":
                row["JN/NOT"] = junction
            if median != "Auto":
                row["PRESENCE OF MEDIAN"] = median
            if shoulder != "Auto":
                row["PRESENCE OF SHOULDER"] = shoulder
            if footpath != "Auto":
                row["PRESENCE OF FOOTPATH"] = footpath
            row["is_night"] = int(row["D/N"] == "N")

            pred_df = pd.DataFrame([row])[features]
            proba = pipe.predict_proba(pred_df)[0]
            out = pd.DataFrame({"Severity": class_labels, "Probability": proba}).sort_values("Probability", ascending=False)
            out["Severity"] = out["Severity"].map(lambda x: SEVERITY_LABEL_MAP.get(str(x), str(x)))
            st.subheader("AI Severity Prediction")
            st.dataframe(out, use_container_width=True, hide_index=True)
            st.plotly_chart(
                style_plotly(px.bar(out, x="Severity", y="Probability", title="Predicted Severity Probability")),
                use_container_width=True,
            )
            st.success(f"Most likely outcome: {out.iloc[0]['Severity']} ({out.iloc[0]['Probability']:.2%})")

    else:
        st.caption(
            "Pick any filters you want. The model will score matching records and show average risk plus top jurisdictions."
        )
        with st.expander("Filters (all optional)", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                place = st.multiselect(PLACE_LABEL, sorted(df[PLACE_COL].astype(str).unique().tolist()))
                month_num = st.multiselect("Month", sorted(df["month_num"].astype(int).unique().tolist()))
                day_of_week = st.multiselect("Day of week", sorted(df["day_of_week"].astype(str).unique().tolist()))
                dn = st.multiselect("Time type", ["D", "N"], format_func=lambda x: "Day" if x == "D" else "Night")
                time_bucket = st.multiselect("Time range", sorted(df["time_bucket"].astype(str).unique().tolist()))
            with c2:
                geometry = st.multiselect("Road geometry", sorted(df["GEOMETRY"].astype(str).unique().tolist()))
                pattern = st.multiselect("Collision pattern", sorted(df["PATTERN_OF_COLLISION_LABEL"].astype(str).unique().tolist()))
                collision = st.multiselect("Collision type", sorted(df["TYPE_OF_COLLISION_LABEL"].astype(str).unique().tolist()))
                junction = st.multiselect("Junction area", sorted(df["JN/NOT"].astype(str).unique().tolist()))

        candidate = df.copy()
        candidate = _apply_filter(candidate, PLACE_COL, place)
        candidate = _apply_filter(candidate, "month_num", month_num)
        candidate = _apply_filter(candidate, "day_of_week", day_of_week)
        candidate = _apply_filter(candidate, "D/N", dn)
        candidate = _apply_filter(candidate, "time_bucket", time_bucket)
        candidate = _apply_filter(candidate, "GEOMETRY", geometry)
        candidate = _apply_filter(candidate, "PATTERN_OF_COLLISION_LABEL", pattern)
        candidate = _apply_filter(candidate, "TYPE_OF_COLLISION_LABEL", collision)
        candidate = _apply_filter(candidate, "JN/NOT", junction)

        st.metric("Matching records", f"{len(candidate):,}")
        if candidate.empty:
            st.warning("No matching records. Remove one or more filters.")
        elif st.button("Run AI Risk Scan", type="primary"):
            pred_mat = pipe.predict_proba(candidate[features])
            summary = pd.DataFrame({"Severity": class_labels, "Probability": pred_mat.mean(axis=0)}).sort_values(
                "Probability", ascending=False
            )
            summary["Severity"] = summary["Severity"].map(lambda x: SEVERITY_LABEL_MAP.get(str(x), str(x)))
            st.subheader("Average Severity Probability")
            st.dataframe(summary.style.format({"Probability": "{:.2%}"}), use_container_width=True, hide_index=True)
            st.plotly_chart(
                style_plotly(px.bar(summary, x="Severity", y="Probability", title="Average Severity Probability")),
                use_container_width=True,
            )

            severe_labels = {"Fatal", "Grievous"}
            severe_idx = [i for i, lbl in enumerate(class_labels) if str(lbl) in severe_labels]
            severe_risk = pred_mat[:, severe_idx].sum(axis=1) if severe_idx else pred_mat.max(axis=1)
            place_risk = (
                pd.DataFrame({PLACE_LABEL: candidate[PLACE_COL].astype(str), "Severe risk score": severe_risk})
                .groupby(PLACE_LABEL)
                .agg(**{"Average severe risk": ("Severe risk score", "mean"), "Samples": ("Severe risk score", "size")})
                .reset_index()
                .sort_values("Average severe risk", ascending=False)
            )
            st.subheader("Top Jurisdictions by Predicted High Severity Risk")
            st.dataframe(place_risk.head(30), use_container_width=True, hide_index=True)
            st.plotly_chart(
                style_plotly(
                    px.bar(
                        place_risk.head(20),
                        x=PLACE_LABEL,
                        y="Average severe risk",
                        title="Top 20 Jurisdictions by High Severity Risk (Fatal + Serious Injury)",
                    )
                ),
                use_container_width=True,
            )

else:
    st.caption("Forecasting ranks jurisdictions by expected accident volume/risk for future months and dates.")
    forecast = forecast_hotspots(df, years_ahead=5)
    if forecast.empty:
        st.warning("Not enough data to build forecast.")
        st.stop()

    pred_year_options = sorted(forecast["year"].astype(int).unique().tolist())
    hist_year_options = sorted(df["year"].astype(int).unique().tolist())
    if "hotspot_target_year" not in st.session_state:
        st.session_state["hotspot_target_year"] = pred_year_options[0]
    if "hotspot_target_month" not in st.session_state:
        st.session_state["hotspot_target_month"] = 1
    if "hotspot_use_exact_date" not in st.session_state:
        st.session_state["hotspot_use_exact_date"] = False
    if "hotspot_top_n" not in st.session_state:
        st.session_state["hotspot_top_n"] = 20
    if "hotspot_ranking_source" not in st.session_state:
        st.session_state["hotspot_ranking_source"] = "Predicted (AI Forecast)"

    with st.sidebar:
        st.header("Hotspot Forecast Filters")
        st.selectbox("Ranking Source", ["Predicted (AI Forecast)", "Historical (Actual Data)"], key="hotspot_ranking_source")
        year_options = pred_year_options if st.session_state["hotspot_ranking_source"] == "Predicted (AI Forecast)" else hist_year_options
        if int(st.session_state["hotspot_target_year"]) not in year_options:
            st.session_state["hotspot_target_year"] = year_options[0]
        st.selectbox("Year", year_options, key="hotspot_target_year")
        if st.session_state["hotspot_ranking_source"] == "Predicted (AI Forecast)":
            month_options = sorted(
                forecast.loc[forecast["year"] == int(st.session_state["hotspot_target_year"]), "month_num"].astype(int).unique().tolist()
            )
        else:
            month_options = sorted(
                df.loc[df["year"].astype(int) == int(st.session_state["hotspot_target_year"]), "month_num"].astype(int).unique().tolist()
            )
        if not month_options:
            st.warning("No forecast months for selected year.")
            st.stop()
        if int(st.session_state["hotspot_target_month"]) not in month_options:
            st.session_state["hotspot_target_month"] = month_options[0]
        st.selectbox("Month", month_options, key="hotspot_target_month")
        st.checkbox("Use exact date view", key="hotspot_use_exact_date")
        default_date = date(int(st.session_state["hotspot_target_year"]), int(st.session_state["hotspot_target_month"]), 1)
        target_date = st.date_input("Target Date", value=default_date, disabled=not st.session_state["hotspot_use_exact_date"])
        st.slider("Show top jurisdictions", 5, 50, key="hotspot_top_n", step=5)

    target_year = int(st.session_state["hotspot_target_year"])
    target_month = int(st.session_state["hotspot_target_month"])
    use_exact_date = bool(st.session_state["hotspot_use_exact_date"])

    ranking_source = st.session_state["hotspot_ranking_source"]

    if ranking_source == "Historical (Actual Data)":
        ranking = _historical_month_ranking(df, target_year, target_month)
        score_col = "actual_count"
        score_label = "Actual accidents"
        if use_exact_date:
            st.info("Exact date view is available only for Predicted mode. Showing historical month ranking.")
            use_exact_date = False
    else:
        if use_exact_date:
            ranking = date_hotspot_ranking(df, forecast, target_date)
            score_col = "predicted_daily_risk"
            score_label = "Predicted daily risk"
        else:
            ranking = monthly_hotspot_ranking(forecast, target_year, target_month)
            score_col = "predicted_count"
            score_label = "Predicted monthly count"

    if ranking.empty:
        st.warning("No forecast output for selected period.")
    else:
        display = ranking.rename(columns={PLACE_COL: PLACE_LABEL, score_col: score_label})
        top_n = int(st.session_state["hotspot_top_n"])
        top_df = display.head(top_n)
        st.dataframe(top_df, use_container_width=True, hide_index=True, height=420)
        st.plotly_chart(
            style_plotly(px.bar(top_df, x=PLACE_LABEL, y=score_label, title=f"Hotspot ranking for {target_year}-{target_month:02d}")),
            use_container_width=True,
        )

        coords = df.groupby(PLACE_COL)[["Latitude", "Longitude"]].median().reset_index().rename(columns={PLACE_COL: PLACE_LABEL})
        map_df = coords.merge(top_df[[PLACE_LABEL, score_label]], on=PLACE_LABEL, how="inner")
        if not map_df.empty:
            fig = px.scatter_mapbox(
                map_df,
                lat="Latitude",
                lon="Longitude",
                size=score_label,
                color=score_label,
                hover_name=PLACE_LABEL,
                zoom=8,
                height=430,
            )
            fig.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(style_plotly(fig), use_container_width=True)

        trend_pick = st.multiselect(
            "Compare 5-year trend for jurisdictions",
            sorted(forecast[PLACE_COL].astype(str).unique().tolist()),
            default=top_df[PLACE_LABEL].head(5).tolist(),
        )
        if trend_pick:
            if ranking_source == "Historical (Actual Data)":
                hist_trend = (
                    df[df[PLACE_COL].astype(str).isin(trend_pick)]
                    .groupby([PLACE_COL, "year", "month_num"])
                    .size()
                    .reset_index(name="actual_count")
                    .sort_values(["year", "month_num"])
                )
                hist_trend = hist_trend.rename(columns={PLACE_COL: PLACE_LABEL})
                hist_trend["period"] = (
                    hist_trend["year"].astype(int).astype(str) + "-" + hist_trend["month_num"].astype(int).astype(str).str.zfill(2)
                )
                st.plotly_chart(
                    style_plotly(px.line(hist_trend, x="period", y="actual_count", color=PLACE_LABEL, title="Historical trend by jurisdiction")),
                    use_container_width=True,
                )
            else:
                trend = forecast[forecast[PLACE_COL].astype(str).isin(trend_pick)].copy()
                trend = trend.rename(columns={PLACE_COL: PLACE_LABEL})
                trend["period"] = pd.to_datetime(trend["forecast_date"]).dt.strftime("%Y-%m")
                st.plotly_chart(
                    style_plotly(px.line(trend, x="period", y="predicted_count", color=PLACE_LABEL, title="Forecast trend by jurisdiction")),
                    use_container_width=True,
                )

