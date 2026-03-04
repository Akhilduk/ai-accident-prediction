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
