import json

import pandas as pd
import plotly.express as px
import streamlit as st

from src.cleaning import clean_data
from src.config import TRAINING_REPORT_JSON
from src.data_io import get_active_dataset, load_excel_cached
from src.modeling import train_and_compare
from src.ui import apply_theme

apply_theme(
    "Model Training & Comparison",
    icon="🧠",
    subtitle="Benchmark models and save the best pipeline for prediction.",
)
active = get_active_dataset()
if active is None:
    st.warning("No dataset available. Upload data first.")
    st.stop()

df, _ = clean_data(load_excel_cached(str(active)))
feature_cols = [
    "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION",
    "Distance",
    "NO. OF VEHICLE",
    "month_num",
    "day_of_week",
    "time_bucket",
    "D/N",
    "PATTERN_OF_COLLISION_LABEL",
    "TYPE_OF_COLLISION_LABEL",
    "TYPE_OF_VEHICLE_1_LABEL",
    "TYPE_OF_VEHICLE_2_LABEL",
    "GEOMETRY",
    "PRESENCE OF MEDIAN",
    "PRESENCE OF SHOULDER",
    "PRESENCE OF FOOTPATH",
    "JN/NOT",
    "is_weekend",
    "is_night",
]

if st.button("🚀 Train all 3 models", type="primary"):
    with st.spinner("Training in progress..."):
        leaderboard, report, best = train_and_compare(df, feature_cols)
    st.success(f"Best model selected: {best}")
    st.dataframe(leaderboard, use_container_width=True)
    st.plotly_chart(px.bar(leaderboard, x="model", y="test_f1_macro", title="Model Macro-F1 Comparison"), use_container_width=True)

    for model_name, details in report.items():
        st.subheader(f"{model_name} Confusion Matrix")
        cm = pd.DataFrame(details["confusion_matrix"], index=details["labels"], columns=details["labels"])
        st.plotly_chart(px.imshow(cm, text_auto=True, title=f"Confusion Matrix - {model_name}"), use_container_width=True)

if TRAINING_REPORT_JSON.exists():
    with st.expander("Latest training report JSON"):
        st.code(json.dumps(json.loads(TRAINING_REPORT_JSON.read_text()), indent=2), language="json")
