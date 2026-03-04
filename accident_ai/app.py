import streamlit as st

from src.ui import apply_theme

st.set_page_config(page_title="NATRAC Accident Analytics and AI Prediction", layout="wide", page_icon="AI")

apply_theme(
    "NATRAC Accident Analytics and AI Prediction",
    icon="AI",
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
