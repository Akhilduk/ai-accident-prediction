from pathlib import Path

import streamlit as st

from src.cleaning import clean_data
from src.data_io import get_active_dataset, load_excel_cached
from src.viz import plot_top_hotspots

st.title("NATRAC Accident Analytics & AI Prediction")

active = get_active_dataset()
if active is None:
    st.warning("No dataset found. Please upload in Data Manager.")
    st.stop()

raw = load_excel_cached(str(active))
df, info = clean_data(raw)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Accidents", f"{len(df):,}")
k2.metric("Fatal Count", f"{int(df['FATAL'].sum()):,}")
k3.metric("Grievous Count", f"{int(df['GRIEVOUS'].sum()):,}")
k4.metric("Minor Count", f"{int(df['MINOR'].sum()):,}")
fatal_rate = (df["FATAL"].sum() / len(df) * 100) if len(df) else 0
k5.metric("Fatal Rate", f"{fatal_rate:.2f}%")
hotspot = plot_top_hotspots(df)
top_place = hotspot.iloc[0, 0] if not hotspot.empty else "N/A"
k6.metric("Top Hotspot", str(top_place))

st.caption(f"Active dataset: {Path(active).name} | Footer rows removed: {info['removed_footer_rows']}")

c1, c2, c3, c4 = st.columns(4)
c1.page_link("pages/2_Data_Manager.py", label="Upload Data")
c2.page_link("pages/3_Dashboard.py", label="View Dashboard")
c3.page_link("pages/4_Model_Training.py", label="Train Models")
c4.page_link("pages/5_Prediction.py", label="Prediction")
