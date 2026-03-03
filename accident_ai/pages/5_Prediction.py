import pandas as pd
import plotly.express as px
import streamlit as st

from src.cleaning import clean_data
from src.data_io import get_active_dataset, load_excel_cached
from src.forecasting import forecast_hotspots
from src.modeling import load_best_model

st.title("Prediction")
active = get_active_dataset()
if active is None:
    st.warning("No dataset available. Upload data first.")
    st.stop()

df, _ = clean_data(load_excel_cached(str(active)))
place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"

mode = st.radio("Mode", ["Severity Prediction", "Hotspot Forecast"], horizontal=True)

if mode == "Severity Prediction":
    model_bundle = load_best_model()
    if model_bundle is None:
        st.warning("Train model first from Model Training page.")
        st.stop()

    features = model_bundle["features"]
    pipe = model_bundle["pipeline"]

    c1, c2, c3 = st.columns(3)
    inputs = {}
    with c1:
        inputs[place_col] = st.selectbox("Place", sorted(df[place_col].astype(str).unique()))
        inputs["month_num"] = st.selectbox("Month", sorted(df["month_num"].astype(int).unique()))
        inputs["day_of_week"] = st.selectbox("Day of Week", sorted(df["day_of_week"].astype(str).unique()))
        inputs["time_bucket"] = st.selectbox("Time Bucket", ["0-6", "6-12", "12-18", "18-24"])
        inputs["D/N"] = st.selectbox("D/N", ["D", "N"])
    with c2:
        inputs["PATTERN_OF_COLLISION_LABEL"] = st.selectbox("Pattern", sorted(df["PATTERN_OF_COLLISION_LABEL"].astype(str).unique()))
        inputs["TYPE_OF_COLLISION_LABEL"] = st.selectbox("Type of Collision", sorted(df["TYPE_OF_COLLISION_LABEL"].astype(str).unique()))
        inputs["TYPE_OF_VEHICLE_1_LABEL"] = st.selectbox("Vehicle 1", sorted(df["TYPE_OF_VEHICLE_1_LABEL"].astype(str).unique()))
        inputs["TYPE_OF_VEHICLE_2_LABEL"] = st.selectbox("Vehicle 2", sorted(df["TYPE_OF_VEHICLE_2_LABEL"].astype(str).unique()))
    with c3:
        inputs["GEOMETRY"] = st.selectbox("Geometry", sorted(df["GEOMETRY"].astype(str).unique()))
        inputs["PRESENCE OF MEDIAN"] = st.selectbox("Median", ["yes", "no"])
        inputs["PRESENCE OF SHOULDER"] = st.selectbox("Shoulder", ["yes", "no"])
        inputs["PRESENCE OF FOOTPATH"] = st.selectbox("Footpath", ["yes", "no"])
        inputs["JN/NOT"] = st.selectbox("Junction", ["yes", "no"])

    inputs["Distance"] = float(df["Distance"].median())
    inputs["NO. OF VEHICLE"] = float(df["NO. OF VEHICLE"].median())
    inputs["is_weekend"] = int(inputs["day_of_week"] in ["Saturday", "Sunday"])
    inputs["is_night"] = int(inputs["D/N"] == "N")

    pred_df = pd.DataFrame([inputs])[features]

    if st.button("Predict Severity"):
        proba = pipe.predict_proba(pred_df)[0]
        labels = pipe.classes_
        out = pd.DataFrame({"severity": labels, "probability": proba}).sort_values("probability", ascending=False)
        st.dataframe(out, use_container_width=True)
        st.plotly_chart(px.bar(out, x="severity", y="probability", title="Predicted Severity Probabilities"), use_container_width=True)
        st.info("Recommendations: enforce speed control, improve night visibility, and strengthen junction management in high-risk zones.")
        st.download_button("Export prediction as CSV", out.to_csv(index=False), "severity_prediction.csv", "text/csv")

else:
    forecast = forecast_hotspots(df)
    st.subheader("Next-Month Hotspot Risk")
    st.dataframe(forecast.head(20), use_container_width=True)
    chart = px.bar(
        forecast.head(20),
        x=place_col,
        y="predicted_next_month_count",
        title="Predicted Next-Month Accident Count by Place",
    )
    st.plotly_chart(chart, use_container_width=True)

    coords = (
        df.groupby(place_col)[["Latitude", "Longitude"]]
        .median()
        .reset_index()
        .merge(forecast[[place_col, "predicted_next_month_count"]], on=place_col, how="inner")
    )
    m = px.scatter_mapbox(
        coords,
        lat="Latitude",
        lon="Longitude",
        size="predicted_next_month_count",
        color="predicted_next_month_count",
        hover_name=place_col,
        zoom=9,
        height=450,
    )
    m.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(m, use_container_width=True)
    st.download_button("Export hotspot forecast CSV", forecast.to_csv(index=False), "hotspot_forecast.csv", "text/csv")
