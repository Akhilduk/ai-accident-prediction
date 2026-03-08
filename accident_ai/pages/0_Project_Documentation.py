import streamlit as st

from src.ui import apply_theme

apply_theme(
    "Project Documentation",
    icon="DOCS",
    subtitle="Complete end-to-end guide for non-technical users: purpose, flow, calculations, models, and setup.",
)

st.markdown(
    """
<div class="glass-card">
  <h3 style="margin:0 0 0.35rem 0;">What this project does</h3>
  <div style="opacity:0.9;">
    This system converts raw road-accident records into clear insights, visual charts, AI predictions, and future hotspot ranking.
    It is designed so departments and non-technical users can make safer road decisions with evidence.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("## 1) Purpose in simple words")
st.markdown(
    """
- **Main goal**: Understand *where*, *when*, and *how* accidents happen, then estimate future risk.
- **Who can use**: Police, transport teams, planners, safety officers, and management reviewers.
- **What you get**:
  - Clean and validated data.
  - Graphs and maps for easy pattern reading.
  - AI model comparison and best model saving.
  - Severity probability prediction.
  - Hotspot ranking for future months or exact dates.
"""
)

st.markdown("## 2) Technology stack and versions")
st.markdown(
    """
### Programming language
- **Python 3.12**

### Core app framework
- **Streamlit 1.39.0** (web UI with sidebar pages)

### Data and math
- **Pandas 2.2.2** (tables, cleaning, grouping)
- **NumPy 1.26.4** (numeric calculations)

### Machine Learning
- **scikit-learn 1.5.1** (pipelines, metrics, RandomForest, GradientBoostingRegressor)
- **XGBoost 2.1.1** (advanced classifier for severity prediction)
- **CatBoost** (optional, enabled only if environment variable is set)

### Visualizations
- **Plotly 5.24.1** (interactive charts)
- **PyDeck 0.9.1** (map layers)
- **Folium 0.17.0** (map support)

### Files and model persistence
- **openpyxl 3.1.5** (read Excel uploads)
- **joblib 1.4.2** (save/load best trained model)
"""
)

st.markdown("## 3) Project structure (how folders are organized)")
st.code(
    """
accident_ai/
  app.py                  # Main landing app
  pages/
    0_Project_Documentation.py
    1_Home.py
    2_Data_Manager.py
    3_Dashboard.py
    4_Model_Training.py
    5_Prediction.py
  src/
    config.py             # Paths, required columns, constants
    data_io.py            # Upload, versioning, active dataset management
    cleaning.py           # Data cleaning and normalization rules
    master_reference.py   # Code -> label mapping management
    modeling.py           # Train/compare models and save best model
    forecasting.py        # Future hotspot forecasting and ranking
    features.py           # Feature creation helpers
    viz.py                # Reusable charts/aggregations
    ui.py                 # Common visual style/theme
  data/
    uploads/              # All uploaded versions
    processed/            # Active cleaned csv output
    master_reference.json # Editable mapping storage
    active_dataset.txt    # Pointer to currently active dataset
  models/
    best_model.joblib     # Saved best model pipeline
  reports/
    model_leaderboard.csv
    training_report.csv
    training_report.json
    hotspot_forecast.csv
"""
)

st.markdown("## 4) End-to-end workflow (from raw file to prediction)")
st.markdown(
    """
1. **Upload Excel** in Data Manager.
2. App checks mandatory columns.
3. App cleans messy formats (dates, time, day/night, yes/no, code mappings).
4. Cleaned data is used by Home, Dashboard, Training, and Prediction pages.
5. Model Training compares multiple ML algorithms.
6. Best model is saved and later used in Prediction page.
7. Forecasting engine predicts future hotspot risk by month/date.
"""
)

st.markdown("## 5) Data cleaning logic (why and how)")
st.markdown(
    """
### Why cleaning is needed
Real accident files often have inconsistent entries. Example: mixed date formats, typed labels, numeric codes, footer notes.
If not cleaned, charts and AI outputs become misleading.

### What is cleaned
- Column names standardized to expected headers.
- Footer/legend rows removed.
- Date parsing supports Excel serial dates + multiple text formats.
- Month names/numbers normalized to `1..12`.
- Day names standardized to Monday..Sunday.
- Time converted into hour/minute and time buckets.
- Day/Night values standardized.
- Yes/No style fields normalized.
- Collision/vehicle numeric codes decoded via master reference tables.
- Severity normalized to three classes: **Fatal, Grievous, Minor**.
"""
)

st.markdown("## 6) Graphs and tables: what they mean")
with st.expander("Dashboard visuals explained in simple language", expanded=True):
    st.markdown(
        """
- **Pie chart (Severity Distribution)**: Share of Fatal / Serious Injury / Minor Injury.
- **Line chart (Month-wise Severity Trend)**: How accident severity count changes month by month.
- **Top hotspot table**: Locations with highest accident totals and fatal rate.
- **Maps**: Geographic clustering and high-incident points.
- **Filter panels**: Narrow results by place, month, day, day/night, collision type, road geometry, etc.

**How to read correctly**
- First apply filters, then read charts.
- Compare trends by season/month.
- Treat patterns as decision support, not legal proof of cause.
"""
    )

st.markdown("## 7) AI model training: how predictions are built")
st.markdown(
    """
### Models compared
- RandomForestClassifier
- XGBoostClassifier (if available)
- CatBoostClassifier (optional switch)

### Training process
1. Select feature columns and target (`severity_target`).
2. Split data into train/test.
3. Build preprocessing pipeline:
   - numeric: median imputation
   - categorical: frequent-value imputation + one-hot encoding
4. Run cross-validation (macro F1 scoring).
5. Fit final model and evaluate test metrics.
6. Save leaderboard + confusion matrix + classification report.
7. Save best model to `models/best_model.joblib`.
"""
)

st.markdown("## 8) Key calculations explained")
st.markdown(
    """
### KPI examples
- **Fatal Rate (%)** = `(Fatal Count / Total Accidents) * 100`
- **Average severity probability** = average of model probabilities over selected rows.
- **High severity risk score** = `P(Fatal) + P(Grievous)`.

### Forecasting calculations
The forecasting model learns month-by-month count patterns per location using:
- `lag_1`, `lag_2`, `lag_3` (previous months)
- `rolling_3` (recent 3-month average)
- trend index (time progression)
- seasonal signals (`sin` and `cos` of month number)

Then it predicts future monthly accident count for each jurisdiction.

### Date-level hotspot risk
- Monthly forecast is converted to daily baseline using days in month.
- Adjusted by weekday behavior ratio (example: if Fridays are historically higher risk in a place).
- Final daily risk is ranked into Top N hotspots.
"""
)

st.markdown("## 9) Matrices, reports, and outputs")
st.markdown(
    """
- **Confusion Matrix**: Shows how often each actual severity class is predicted as each class.
- **Classification Report**: Precision, recall, F1 per class.
- **Leaderboard Table**: Compares models with CV and test metrics.
- **Hotspot Ranking Table**: Sorted risk list by predicted count or daily risk score.
- **Exported reports** are saved in `reports/` for audit and review.
"""
)

st.markdown("## 10) How to run in VS Code (step-by-step)")
st.markdown(
    """
1. Open project folder in **VS Code**.
2. Open terminal in folder `accident_ai`.
3. (Recommended) Create virtual environment.
4. Install dependencies:
   - `pip install -r requirements.txt`
5. Start app:
   - `streamlit run app.py`
6. Open browser link shown in terminal.
7. Start from **Project Documentation** page, then Data Manager.

### Optional environment controls
- `ENABLE_CATBOOST=1` to include CatBoost during training.
"""
)

st.markdown("## 11) How non-technical users should use this system")
st.markdown(
    """
- Step 1: Upload latest data file.
- Step 2: Check Home KPIs for quick condition summary.
- Step 3: Use Dashboard filters to identify problem segments.
- Step 4: Train model and confirm performance quality.
- Step 5: Use Prediction page for severity and hotspot planning.
- Step 6: Use rankings to prioritize field inspections and interventions.

**Important:** AI output is a support tool. Final action should include local field judgement.
"""
)

st.success("This page is your complete non-technical guide for understanding the full project, structure, flow, calculations, and usage.")
