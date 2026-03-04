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
### Who should use this portal?
- **Police / enforcement**: identify priority risky stretches.
- **Road engineers**: see what road conditions are linked with severe outcomes.
- **Policy teams**: prioritize interventions by data evidence.
- **General public users**: understand what, where, and when accident risk is high.

### What each page does in one line
- **Data Manager**: upload + validate + clean + code mapping.
- **Dashboard**: filtered visual analysis and factor relationships.
- **Model Training**: compare algorithms and save best model.
- **Prediction**: severity probabilities and future hotspot ranking.

### Simple dictionary of technical words
- **Feature/Factor**: an input field used for analysis (month, geometry, day/night, etc.).
- **Target**: output to predict (severity class).
- **Correlation**: relationship score between two fields from -1 to +1.
- **Matrix**: table where both rows and columns are factors and cells contain relationship value.
- **Forecast**: future estimate built from historical pattern.
- **Probability**: chance of each possible outcome (0 to 1 or 0% to 100%).
- **Model**: algorithm trained to learn past patterns.

### Important warning for all pages
- The app shows **data relationships** and **risk indications**.
- It does **not** prove legal cause-and-effect by itself.
- Always combine with field inspection, traffic counts, and local expert judgement.
"""
    )
