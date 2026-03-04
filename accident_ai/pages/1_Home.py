from pathlib import Path

import streamlit as st

from src.cleaning import clean_data
from src.data_io import get_active_dataset, load_excel_cached
from src.ui import apply_theme
from src.viz import plot_top_hotspots

apply_theme(
    "Road Safety Intelligence Portal",
    icon="HOME",
    subtitle="A simple platform to understand accident patterns, train models, and forecast high-risk areas.",
)

active = get_active_dataset()
if active is None:
    st.warning("No dataset found. Please upload in Data Manager.")
    st.stop()

raw = load_excel_cached(str(active))
df, info = clean_data(raw)

fatal_rate = (df["FATAL"].sum() / len(df) * 100) if len(df) else 0
hotspot = plot_top_hotspots(df)
top_place = hotspot.iloc[0, 0] if not hotspot.empty else "N/A"

st.markdown(
    """
    <div class="glass-card">
      <h3 style="margin:0 0 0.35rem 0;">Project Overview</h3>
      <div style="opacity:0.88;">
        This portal converts mixed-format accident data into standardized insights and AI predictions for decision support.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3 = st.columns(3)
k4, k5, k6 = st.columns(3)
k1.metric("Total Accidents", f"{len(df):,}")
k2.metric("Fatal Count", f"{int(df['FATAL'].sum()):,}")
k3.metric("Serious Injury Count", f"{int(df['GRIEVOUS'].sum()):,}")
k4.metric("Minor Count", f"{int(df['MINOR'].sum()):,}")
k5.metric("Fatal Rate", f"{fatal_rate:.2f}%")
k6.metric("Top Hotspot", str(top_place))

st.caption(f"Active dataset: {Path(active).name} | Footer rows removed during cleaning: {info['removed_footer_rows']}")

with st.expander("How to Read This Page (Simple)", expanded=False):
    st.markdown(
        """
- **Total Accidents**: Total reported cases in current dataset.
- **Fatal Count**: Cases where death was reported.
- **Serious Injury Count**: Cases with severe injury.
- **Minor Count**: Cases with minor injury.
- **Fatal Rate**: Fatal cases as percentage of total cases.
- **Top Hotspot**: Place with highest accident count in current data.

Use this page for a quick summary, then open **Dashboard** for deeper analysis.
"""
    )


with st.expander("Detailed Meaning of Home Page Numbers", expanded=False):
    st.markdown(
        """
- **Total Accidents** = number of rows in cleaned dataset.
- **Fatal Count** = sum of `FATAL` column.
- **Serious Injury Count** = sum of `GRIEVOUS` column.
- **Minor Count** = sum of `MINOR` column.
- **Fatal Rate (%)** = `(Fatal Count / Total Accidents) * 100`.
- **Top Hotspot** = place with highest accident frequency in current active data.

### Numerical example
If Total=1,200 and Fatal=96:
- Fatal Rate = `(96 / 1200) * 100 = 8.0%`

### How to read these KPI cards
- They are quick summary cards.
- Use them to compare data versions after upload.
- If Fatal Rate rises while Total stays same, immediate safety review may be needed.
"""
    )

t1, t2 = st.tabs(["What You Can Do", "Navigate"])

with t1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="glass-card">
              <h4 style="margin:0 0 0.35rem 0;">Data and Quality</h4>
              <ul style="margin:0; padding-left:1rem;">
                <li>Upload and version datasets</li>
                <li>Auto-clean mixed date/time formats</li>
                <li>Decode collision and vehicle references</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="glass-card">
              <h4 style="margin:0 0 0.35rem 0;">Analytics and AI</h4>
              <ul style="margin:0; padding-left:1rem;">
                <li>Interactive filtered dashboard</li>
                <li>Severity prediction using trained model</li>
                <li>5-year hotspot forecast by month or date</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

with t2:
    st.markdown("### Quick Actions")
    c1, c2, c3, c4 = st.columns(4)
    c1.page_link("pages/2_Data_Manager.py", label="Open Data Manager")
    c2.page_link("pages/3_Dashboard.py", label="Open Dashboard")
    c3.page_link("pages/4_Model_Training.py", label="Open Model Training")
    c4.page_link("pages/5_Prediction.py", label="Open Prediction")
