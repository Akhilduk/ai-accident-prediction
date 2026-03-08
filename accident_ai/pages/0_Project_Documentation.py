import streamlit as st

from src.ui import apply_theme

apply_theme(
    "Project Documentation",
    icon="DOCS",
    subtitle="Complete end-to-end, non-technical guide to understand purpose, flow, models, calculations, metrics, and usage.",
)

st.markdown(
    """
<div class="glass-card">
  <h3 style="margin:0 0 0.35rem 0;">Welcome: Full Project Guide (for non-technical users)</h3>
  <div style="opacity:0.92;">
    This page explains the entire project in plain language: what it does, why it exists, which tools are used,
    what each chart/table means, how AI predictions are calculated, and how to run it in VS Code.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("## 1) What this project is and why it exists")
st.markdown(
    """
Imagine you have many accident records in Excel. This project turns that raw data into:
- **Simple dashboards** (to see trends and risky places)
- **AI predictions** (to estimate severity probability)
- **Future hotspot ranking** (to prepare safety actions ahead of time)

### Main purpose
- Help decision-makers find where/when risk is high.
- Support planning for patrol, engineering, signage, awareness, and inspections.
- Save time by automating cleaning + analysis + prediction in one place.

### Important note
This system gives **decision support**, not legal proof. Final decisions should include field verification.
"""
)

st.markdown("## 2) Who should use this")
st.markdown(
    """
- Police and traffic enforcement teams
- Transport departments
- Safety planners and policy teams
- Management and reviewers
- Any non-technical user who needs clear, data-backed road-safety insights
"""
)

st.markdown("## 3) Technology stack, versions, and why each is used")
st.markdown(
    """
### Programming language
- **Python 3.12**
  - Why: easy for data, ML, and rapid dashboard development.

### UI framework
- **Streamlit 1.39.0**
  - What it is: a Python framework to build web apps quickly.
  - Why used: creates sidebar pages, charts, tables, and filters without heavy frontend coding.

### Data processing
- **Pandas 2.2.2**
  - What it is: table/dataframe library.
  - Why used: cleaning rows, grouping by month/place, calculating counts/rates.
- **NumPy 1.26.4**
  - What it is: numeric array/math library.
  - Why used: numerical calculations (means, transformations, seasonal math).

### Machine learning
- **scikit-learn 1.5.1**
  - Why used: preprocessing pipelines, train/test split, cross-validation, metrics, and ML models.
- **XGBoost 2.1.1**
  - Why used: strong gradient-boosted trees for classification performance.
- **CatBoost (optional)**
  - Why used: robust boosting model for categorical-heavy data.
  - Note: enabled only if installed and `ENABLE_CATBOOST=1` is set.

### Visualization and maps
- **Plotly 5.24.1**
  - Why used: interactive charts (hover, zoom, legends).
- **PyDeck 0.9.1**
  - Why used: map-based visual layers.
- **Folium 0.17.0**
  - Why used: map utilities (if needed in map visual workflows).

### File and model IO
- **openpyxl 3.1.5**
  - Why used: reading Excel uploads.
- **joblib 1.4.2**
  - Why used: saving/loading trained best model quickly.
"""
)

st.markdown("## 4) Project folder structure and what each part does")
st.code(
    """
accident_ai/
  app.py                         # Main app entry and welcome screen
  pages/
    0_Project_Documentation.py   # This complete guide page
    1_Home.py                    # KPI summary page
    2_Data_Manager.py            # Upload, validation, cleaning, versioning, mapping
    3_Dashboard.py               # Filters, charts, map, matrix, hotspot analysis
    4_Model_Training.py          # Train & compare models; save best
    5_Prediction.py              # Severity prediction + hotspot forecast/ranking
  src/
    config.py                    # Paths, required columns, constants
    data_io.py                   # Read/save uploads, active dataset pointer
    cleaning.py                  # Data standardization and normalization rules
    master_reference.py          # Code-to-label lookup tables
    features.py                  # Feature helpers
    modeling.py                  # ML pipeline, metrics, model comparison
    forecasting.py               # Future monthly/date hotspot risk logic
    viz.py                       # Reusable chart/table preparation
    ui.py                        # Theme and styling utilities
  data/
    uploads/                     # Versioned uploaded files
    processed/                   # Cleaned active CSV
    active_dataset.txt           # Current active dataset pointer
    master_reference.json        # Editable code mapping store
  models/
    best_model.joblib            # Saved winning model pipeline
  reports/
    model_leaderboard.csv
    training_report.csv
    training_report.json
    hotspot_forecast.csv
"""
)

st.markdown("## 5) End-to-end flow (from raw file to final decisions)")
st.markdown(
    """
1. **Upload Excel** in Data Manager.
2. App validates required columns.
3. App cleans and standardizes records.
4. Home page shows key KPIs (quick health snapshot).
5. Dashboard shows deep analysis with filters + map + charts + correlation matrix.
6. Model Training compares multiple AI models and stores best model.
7. Prediction page uses saved best model to estimate severity probabilities.
8. Forecast engine predicts future hotspot risk and ranking.
9. Teams use these outputs to prioritize on-ground actions.
"""
)

st.markdown("## 6) Data cleaning rules (plain-language)")
st.markdown(
    """
Raw real-world data is usually messy. Cleaning makes it trustworthy.

### What is cleaned
- Header names standardized to required project headers.
- Legend/footer rows removed.
- Dates parsed from multiple formats (including Excel serial date numbers).
- Month values normalized to `1..12`.
- Day names normalized to Monday..Sunday.
- Time parsed and converted into buckets (example: late night, morning, etc.).
- Day/Night flags standardized.
- Yes/No style fields standardized.
- Numeric collision/vehicle codes translated to understandable labels.
- Severity values standardized to: **Fatal**, **Grievous**, **Minor**.

### Why this matters
Without cleaning, charts and predictions can be wrong or misleading.
"""
)

st.markdown("## 7) Page-by-page explanation for non-technical users")
with st.expander("1) Home page", expanded=False):
    st.markdown(
        """
- Shows high-level KPIs (Key Performance Indicators).
- Examples: total accidents, fatal count, minor count, fatal rate, top hotspot.
- Best for quick review and comparison between dataset versions.
"""
    )

with st.expander("2) Data Manager page", expanded=False):
    st.markdown(
        """
- Upload new Excel files.
- Keep version history.
- Select active dataset for all pages.
- Preview cleaned output and validate required columns.
- Maintain master reference code tables.
"""
    )

with st.expander("3) Dashboard page", expanded=False):
    st.markdown(
        """
- Interactive filters: place, year, month, day/night, geometry, severity, etc.
- Shows map, severity distribution, monthly trend, collision insights, hotspot table.
- Includes relationship analysis and correlation matrix.
"""
    )

with st.expander("4) Model Training page", expanded=False):
    st.markdown(
        """
- Trains multiple AI models on cleaned historical data.
- Compares models with validation metrics.
- Saves the best model for prediction use.
"""
    )

with st.expander("5) Prediction page", expanded=False):
    st.markdown(
        """
- Predicts severity probabilities for selected records/scenarios.
- Computes high-severity risk score (Fatal + Grievous probability).
- Forecasts future hotspot ranking by month/date.
"""
    )

st.markdown("## 8) How to read charts, tables, and maps")
st.markdown(
    """
### Basic chart reading
- **X-axis** = horizontal categories/time
- **Y-axis** = vertical count/value
- Higher bar/line point usually means more cases/value.

### Pie chart
- Shows percentage share of each severity class.
- Example: 20% Fatal means 20 out of every 100 cases are fatal.

### Line chart
- Shows trend over time.
- Upward slope means increasing trend; downward means decreasing trend.

### Heatmap/matrix
- Darker/stronger color means higher value or stronger relationship.

### Hotspot table
- Usually sorted descending.
- Top row is highest-risk location in selected context.
"""
)

st.markdown("## 9) Core calculations used in the project")
st.markdown(
    """
### KPI (Key Performance Indicator)
- **Meaning**: A quick business/safety summary number.
- Example KPIs in this project:
  - Total Accidents
  - Fatal Count
  - Fatal Rate
  - Night Cases

### Fatal Rate
- Formula: `(Fatal Count / Total Accidents) * 100`

### Average Probability
- The model gives class probabilities per row.
- Average across selected rows gives overall expected class share.

### High Severity Risk Score
- Formula: `P(Fatal) + P(Grievous)`
- Meaning: combined chance of serious outcomes.
"""
)

st.markdown("## 10) Correlation matrix explained (very simple)")
st.markdown(
    """
### What is a correlation matrix?
A table showing relationship strength between multiple factors at once.
Each cell compares two factors and returns a value from **-1 to +1**.

### How to read values
- `+1` = very strong positive relation
- `0` = no clear linear/rank relation
- `-1` = very strong negative relation

### Types used in this project
- **Pearson correlation**
  - Best when relationship is roughly straight-line.
- **Spearman correlation**
  - Best for rank/order relationship, not necessarily straight-line.

### Practical interpretation examples
- `+0.62`: as one factor increases, target tends to increase.
- `-0.41`: as one factor increases, target tends to decrease.
- `+0.03`: almost no useful relationship.

### Important caution
Correlation means **association**, not proven cause.
"""
)

st.markdown("## 11) Confusion matrix explained")
st.markdown(
    """
### What is confusion matrix?
A square table that compares:
- **Actual class** (real truth)
- **Predicted class** (model output)

For 3 classes (Fatal/Grievous/Minor), matrix is 3x3.

### How to read
- **Diagonal cells** = correct predictions.
- **Off-diagonal cells** = misclassifications.
- Higher diagonal values = better model.

### Why useful
It shows *where* model makes mistakes (not just overall score).
"""
)

st.markdown("## 12) Model metrics glossary (Accuracy, Precision, Recall, F1)")
st.markdown(
    """
- **Accuracy**: overall fraction of correct predictions.
- **Precision**: when model predicts a class, how often it is right.
- **Recall**: of all real cases of a class, how many model found.
- **F1 Score**: balance between precision and recall.

### Macro F1 (used in model comparison)
- Computes F1 for each class separately and averages equally.
- Useful when classes are imbalanced.

### Cross-validation (CV)
- Splits data into multiple folds, trains/tests repeatedly.
- Gives more stable performance estimate than one split.
"""
)

st.markdown("## 13) Forecasting logic (hotspot prediction)")
st.markdown(
    """
The project predicts monthly accident counts per place using historical patterns.

### Features used by forecasting model
- `lag_1`, `lag_2`, `lag_3`: previous months' counts
- `rolling_3`: recent 3-month average
- `trend_idx`: time progression index
- `month_sin`, `month_cos`: seasonal month cycle signals

### Why sin/cos for month?
Because months are cyclical (Dec -> Jan continues cycle). Sine/cosine captures seasonality smoothly.

### Date-level risk ranking
1. Start from monthly predicted count.
2. Convert to daily baseline using days in that month.
3. Adjust by weekday historical behavior (weekday ratio).
4. Rank places by predicted daily risk.
"""
)

st.markdown("## 14) AI models used and why")
st.markdown(
    """
- **RandomForestClassifier**
  - Ensemble of decision trees; reliable baseline and robust to noisy data.
- **XGBoostClassifier**
  - Boosting model; often high performance for tabular datasets.
- **CatBoostClassifier (optional)**
  - Good with categorical-heavy data; enabled when available.
- **GradientBoostingRegressor**
  - Used for monthly hotspot count forecasting (regression task).
"""
)

st.markdown("## 15) Full glossary (all common terms in this project)")
with st.expander("Open glossary", expanded=False):
    st.markdown(
        """
- **App**: the web interface users open in browser.
- **Sidebar**: left panel with page navigation and filters.
- **Dataset**: table of accident records.
- **Record/Row**: one accident entry.
- **Column/Field/Feature**: one variable (e.g., month, geometry).
- **Target**: output the model tries to predict (`severity_target`).
- **Class**: category label (Fatal/Grievous/Minor).
- **Probability**: chance from 0 to 1 (or 0% to 100%).
- **Hotspot**: location with relatively high accident risk/count.
- **Forecast**: future estimate based on historical data.
- **KPI**: key summary number used for quick monitoring.
- **Filter**: user selection to narrow data scope.
- **Model**: trained algorithm that learns patterns from past data.
- **Training**: process of teaching model from historical data.
- **Inference/Prediction**: using trained model on new/selected data.
- **Pipeline**: ordered steps (clean/encode/model) executed together.
- **One-hot encoding**: converting text categories into numeric indicator columns.
- **Imputation**: filling missing values with a strategy (median/most frequent).
- **Leaderboard**: ranked model performance table.
- **Ranking**: sorting places by risk score/count.
"""
    )

st.markdown("## 16) Installation and running in VS Code")
st.markdown(
    """
1. Open **VS Code**.
2. Open project folder and go inside `accident_ai`.
3. Open Terminal.
4. (Recommended) Create virtual environment:
   - Windows: `python -m venv .venv`
   - macOS/Linux: `python3 -m venv .venv`
5. Activate virtual environment:
   - Windows: `.venv\\Scripts\\activate`
   - macOS/Linux: `source .venv/bin/activate`
6. Install dependencies:
   - `pip install -r requirements.txt`
7. Run app:
   - `streamlit run app.py`
8. Open the local URL shown in terminal.

### Optional
- To enable CatBoost model during training:
  - Install CatBoost package if needed
  - Set env var: `ENABLE_CATBOOST=1`
"""
)

st.markdown("## 17) How non-technical teams should use results responsibly")
st.markdown(
    """
- Use this system to **prioritize** investigations and interventions.
- Use high-risk outputs to decide where to inspect first.
- Validate high-risk locations with field teams.
- Track KPI changes month-over-month after interventions.
- Treat model outputs as guidance, not absolute truth.
"""
)

st.success(
    "You are now reading the full non-technical project guide: purpose, stack, flow, charts, matrices, metrics, predictions, and setup in one place."
)
