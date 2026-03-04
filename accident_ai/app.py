import streamlit as st

from src.ui import apply_theme

st.set_page_config(page_title="Road Accident Analytics and Prediction", layout="wide", page_icon="AI")

apply_theme(
    "Road Accident Analytics and Prediction",
    icon="ANALYTICS",
    subtitle="A complete workflow for data cleaning, analytics dashboard, model training, and AI-based forecasting.",
)

st.markdown(
    """
    <div class="glass-card">
      <b>Quick Start:</b> Open <b>Data Manager</b> to select dataset, then visit <b>Dashboard</b> and <b>Prediction</b>.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Simple Guide (For First-Time Users)", expanded=False):
    st.markdown(
        """
1. **Data Manager**: Upload your Excel file and make it active.
2. **Dashboard**: Explore accident trends with simple filters.
3. **Model Training**: Train AI models and save the best one.
4. **Prediction**: Get severity prediction and future hotspot ranking.

**Simple meaning of key terms**
- **Severity**: How serious an accident outcome is.
- **Hotspot**: A place with higher accident risk.
- **Forecast**: Future estimate based on past data.
"""
    )

with st.expander("Complete Non-Technical Glossary (Read Once)", expanded=False):
    st.markdown(
        """
### Who is this app for?
- **Traffic police / transport teams**: to identify risky places and patterns.
- **Planning teams**: to decide where to add signals, lighting, medians, footpaths, or enforcement.
- **General users**: to understand how accident patterns change by place, time, and road condition.

### What is shown in each page?
- **Data Manager**: Upload file, clean data, and define code meanings.
- **Dashboard**: Visual analysis (map, trends, hotspots, factor relationships).
- **Model Training**: Compare AI models and save the best one.
- **Prediction**: Get severity probability and 5-year hotspot forecast.

### Important words in simple language
- **Feature / Factor**: Any input detail like month, road type, day/night, or vehicle type.
- **Target**: The final output we want to predict (here: accident severity).
- **Severity**:
  - **Fatal** = death involved.
  - **Serious Injury (Grievous)** = major injury.
  - **Minor Injury** = less serious injury.
- **Correlation**: How two things move together.
  - Positive value: both tend to increase together.
  - Negative value: one increases while other decreases.
  - Near zero: weak/no clear relationship.
- **Hotspot**: A place with relatively high accident count/risk.

### What this system does *not* claim
- It shows **pattern-based guidance**, not courtroom proof of cause.
- Use results together with local checks (road inspection, traffic volume, weather, enforcement).
"""
    )
