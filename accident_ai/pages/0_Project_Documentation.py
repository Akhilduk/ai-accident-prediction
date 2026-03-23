import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import CLEANED_DATASET, LEADERBOARD_PATH, TRAINING_REPORT_JSON
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

DATA_PATH = CLEANED_DATASET
TRAINING_JSON_PATH = TRAINING_REPORT_JSON


def _safe_read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _safe_read_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def _format_factor_value(value: str) -> str:
    value = str(value)
    mapping = {
        "yes": "junction areas",
        "no": "non-junction areas",
        "day": "daylight hours",
        "night": "night hours",
        "straight": "straight roads",
        "curve": "curved roads",
    }
    return mapping.get(value.lower(), value.replace("_", " "))


def _factor_sentence(factor: str, value: str, chance: float) -> str:
    value_text = _format_factor_value(value)
    if factor == "JN/NOT":
        return f"In **{value_text}**, the probability of **serious injury** is **{chance:.1f}%**."
    if factor == "day_night_label":
        return f"During **{value_text}**, the probability of **serious injury** is **{chance:.1f}%**."
    if factor == "GEOMETRY":
        return f"On **{value_text}**, the probability of **serious injury** is **{chance:.1f}%**."
    return f"For **{factor} = {value_text}**, the probability of **serious injury** is **{chance:.1f}%**."

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
  - Note: it is included automatically when the package is installed.

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

st.markdown("## 10A) Detailed result interpretation for reports")
st.markdown(
    """
This section is written in a **report-ready** style so you can directly use the logic in project reports, presentations, or review notes.

### A) How to write correlation findings in simple language
When you see a factor with a high positive value, write it like this:
- **Simple style**: "Straight roads show a high association with serious injury cases."
- **Better report style**: "The correlation analysis indicates that straight-road locations are more frequently linked with severe outcomes than many other road conditions in the selected data."

If the dashboard also shows a rate/result such as **76.5%**, write:
- "On straight roads, the probability of serious injury is about **76.5%** in the selected dataset."
- "In non-junction areas, the probability of serious injury is about **75.6%**."
- "During daylight hours, the probability of serious injury is about **77.5%**."

### B) How to interpret correlation values
- **0.00 to 0.19**: very weak relationship; usually not strong enough to treat as a major driver by itself.
- **0.20 to 0.34**: low to moderate relationship; worth monitoring.
- **0.35 to 0.49**: meaningful relationship; can be treated as an important warning sign.
- **0.50 and above**: strong relationship; often one of the main factors connected with the target outcome.

### C) What to write in findings
Use the following simple structure:
1. **Finding**: which factor stands out?
2. **Result interpretation**: what does the number mean in practical terms?
3. **Why it matters**: why should officials care?
4. **Suggested action**: what should be done next?

### D) Example report-ready findings
#### 1. Straight road geometry
- **Finding**: Straight-road sections show a strong association with serious injury outcomes.
- **Result interpretation**: In the selected records, straight roads have a high serious-injury probability. This means severe crashes are not limited to curves or complex road shapes; they are also common on roads where drivers may travel faster or become less cautious.
- **Why it matters**: People often expect curves and junctions to be riskier, but the analysis suggests straight roads may also need strong safety attention.
- **Suggested action**: improve speed control, install warning boards, strengthen lane discipline monitoring, and review overtaking behaviour on straight sections.

#### 2. Non-junction areas
- **Finding**: Non-junction areas show a high share of serious-injury cases.
- **Result interpretation**: This means many severe crashes are happening away from intersections, possibly where vehicles move at higher speed and face fewer control points.
- **Why it matters**: Safety interventions should not focus only on junctions; open road stretches also require attention.
- **Suggested action**: review median opening control, shoulder condition, roadside hazards, speeding behaviour, and visibility on long non-junction corridors.

#### 3. Daylight hours
- **Finding**: Daytime crashes also show a high severe-outcome rate.
- **Result interpretation**: This means severe crashes are not only a night-time problem. High traffic volume, mixed road users, and risky daytime driving behaviour may also be increasing severity.
- **Why it matters**: Daylight does not automatically mean safe conditions.
- **Suggested action**: strengthen daytime enforcement, manage crossing activity, improve lane discipline, and reduce unsafe overtaking during busy hours.

### E) How to interpret the "Why Is Severity High?" output
This section uses:
- **target_rate = target_cases / total_records**
- **risk_score = target_rate × sqrt(total_records)**

#### What target_rate means
- It tells the **chance** of the selected outcome for a specific group.
- Example: if straight roads have a `target_rate` of `0.765`, it means **76.5%** of the selected records in that group belong to the chosen severe category.

#### What risk_score means
- It balances **high rate** and **sample reliability**.
- A small group can show a high percentage by chance.
- A larger group with a slightly lower percentage may be more important in practice.
- So the dashboard gives a higher priority to factors that are both:
  - linked with severe outcomes, and
  - supported by enough records.

### F) How to explain F1 score in your report
- **F1 score** is the balance between **precision** and **recall**.
- In simple terms, it answers: "Is the model both accurate when it predicts a class, and good at finding most real cases of that class?"
- A **higher F1 score** means the model gives more reliable classification performance.

#### Simple interpretation guide
- **0.90 and above**: excellent model performance
- **0.80 to 0.89**: very strong performance
- **0.70 to 0.79**: good and usable performance
- **0.60 to 0.69**: moderate performance; usable with caution
- **Below 0.60**: weak performance; model improvement is needed

### G) How to explain prediction output
When the prediction page shows probabilities, explain them like this:
- "The model does not give only one label; it gives the chance of each severity class."
- "The class with the highest probability is treated as the most likely outcome."
- "If Fatal = 0.10, Serious Injury = 0.65, Minor = 0.25, the model expects Serious Injury to be the most likely result."

### H) Final conclusion style for reports
You can use wording like this:
- "The analysis shows that road geometry, junction condition, and day/night condition are among the main factors associated with accident severity."
- "Straight roads, non-junction areas, and daylight periods show a comparatively high probability of serious injury in the selected dataset."
- "These results suggest that safety planning should not focus only on traditionally risky locations such as junctions or night hours; broader corridor-level control is also important."
- "The findings should be used as decision-support evidence and combined with field inspection before implementing final interventions."

### I) Solution section for reports
Based on the dashboard results, common recommendations are:
- speed management on straight corridors
- better enforcement in non-junction stretches
- daytime traffic control and crossing management
- road-sign review and visibility improvement
- focused inspection of locations repeatedly appearing in high-severity groups
- awareness campaigns for overspeeding, unsafe overtaking, and lane indiscipline
"""
)

st.markdown("## 10B) Current dataset: ready-to-copy result interpretation")
current_df = _safe_read_csv(DATA_PATH)
leaderboard_df = _safe_read_csv(LEADERBOARD_PATH)
training_json = _safe_read_json(TRAINING_JSON_PATH)

if current_df.empty:
    st.info("Current cleaned dataset could not be loaded right now, so live result interpretation cannot be generated. Please re-open the Data Manager page once and then return here.")
else:
    current_df["serious_injury_flag"] = current_df["severity_target"].eq("Grievous").astype(int)
    total_records = len(current_df)
    severity_counts = current_df["severity_target"].value_counts()
    grievous_count = int(severity_counts.get("Grievous", 0))
    fatal_count = int(severity_counts.get("Fatal", 0))
    minor_count = int(severity_counts.get("Minor", 0))

    st.markdown(
        f"""
### A) Overall severity result
- Total accident records analysed: **{total_records}**
- Serious injury cases: **{grievous_count}**
- Fatal cases: **{fatal_count}**
- Minor injury cases: **{minor_count}**

**Simple interpretation**
- Serious injury is the dominant class in the current cleaned dataset.
- This means most of the recorded accidents in this dataset fall into the serious-injury category, so the model and the dashboard naturally focus strongly on this severity level.
"""
    )

    st.markdown("### B) Most important severity findings from current data")
    for factor in ["JN/NOT", "day_night_label", "GEOMETRY"]:
        grouped = (
            current_df.groupby(factor, dropna=False, observed=False)
            .agg(total_records=("serious_injury_flag", "size"), serious_cases=("serious_injury_flag", "sum"))
            .reset_index()
        )
        grouped["target_rate"] = grouped["serious_cases"] / grouped["total_records"]
        best_row = grouped.sort_values(["target_rate", "total_records"], ascending=[False, False]).iloc[0]
        st.write(f"- {_factor_sentence(factor, best_row[factor], float(best_row['target_rate']) * 100)}")

    st.markdown(
        """
**Result interpretation**
- These percentages show where serious-injury outcomes are most common in the present dataset.
- They should be read as a probability within that factor group, not as proof that the factor alone causes the injury severity.
- For reporting, these are the best direct statements to use because they come from actual grouped accident records.
"""
    )

    corr_cols = ["Distance", "hour", "month_num", "is_night", "day_night_label", "GEOMETRY", "JN/NOT", "time_bucket", "TYPE_OF_COLLISION_LABEL"]
    corr_view = current_df[corr_cols].copy()
    for col in corr_cols:
        if not pd.api.types.is_numeric_dtype(corr_view[col]):
            corr_view[col] = corr_view[col].astype("category").cat.codes
    corr_view["serious_injury_flag"] = current_df["serious_injury_flag"]
    corr_series = (
        corr_view.corr(numeric_only=True)["serious_injury_flag"]
        .drop("serious_injury_flag")
        .sort_values(key=lambda s: s.abs(), ascending=False)
        .head(5)
    )
    st.markdown("### C) Correlation matrix: current output interpretation")
    for name, value in corr_series.items():
        strength = "high" if abs(value) >= 0.35 else ("medium" if abs(value) >= 0.20 else "low")
        direction = "positive" if value > 0 else "negative"
        st.write(
            f"- **{name}** shows a **{strength} {direction} relationship** with the serious-injury flag in the current matrix output (**correlation = {value:.3f}**)."
        )
    st.markdown(
        """
**How to explain this in a report**
- A positive value means the coded factor tends to move in the same direction as serious injury.
- A negative value means it tends to move in the opposite direction.
- For categorical columns, the dashboard first converts labels into internal codes, so the correlation matrix should be used mainly to identify **which factors are more connected**, while the grouped percentages should be used to explain **which exact category is riskier**.
"""
    )

    if not leaderboard_df.empty:
        best_model = leaderboard_df.sort_values(["test_f1_macro", "cv_f1_macro_mean"], ascending=False).iloc[0]
        best_name = str(best_model["model"])
        details = training_json.get(best_name, {})
        report = details.get("classification_report", {})
        grievous_f1 = report.get("Grievous", {}).get("f1-score")
        fatal_f1 = report.get("Fatal", {}).get("f1-score")
        minor_f1 = report.get("Minor", {}).get("f1-score")

        st.markdown("### D) F1 score and model output interpretation")
        st.markdown(
            f"""
- Best model from current training report: **{best_name}**
- Test Accuracy: **{float(best_model['test_accuracy']):.3f}**
- Test Macro-F1: **{float(best_model['test_f1_macro']):.3f}**
- Cross-validation Macro-F1: **{float(best_model['cv_f1_macro_mean']):.3f}**

**Simple interpretation**
- The overall Macro-F1 score is modest, which means the model is **usable for guidance** but is **not yet highly reliable across all severity classes**.
- The model performs best on the **Grievous** class because that class has the strongest class-level F1 score in the report.
- The model is much weaker on **Fatal** and **Minor** cases, so those predictions should be read carefully and ideally supported with field judgement.
"""
        )
        if grievous_f1 is not None:
            st.write(f"- Grievous class F1-score: **{float(grievous_f1):.3f}**")
        if fatal_f1 is not None:
            st.write(f"- Fatal class F1-score: **{float(fatal_f1):.3f}**")
        if minor_f1 is not None:
            st.write(f"- Minor class F1-score: **{float(minor_f1):.3f}**")

        st.markdown(
            """
**Report-ready conclusion**
- The machine-learning model captures the serious-injury pattern better than the other severity classes.
- Therefore, the present model is more useful for identifying broad high-severity risk than for giving highly precise class prediction for every single accident.
- Additional data balancing, feature improvement, and model tuning are recommended if the project needs stronger fatal/minor discrimination.
"""
        )

    st.markdown(
        """
### E) Final solution-oriented interpretation
- The current data suggests that **road geometry, junction condition, time pattern, and collision type** are among the factors most connected with severity.
- The grouped probability analysis shows that some categories within these factors have a much higher serious-injury share than others.
- This means road-safety action should focus first on the conditions that repeatedly appear with high `target_rate` and strong record support.

**Practical solutions**
- strengthen speed control and lane-discipline enforcement on straight and open road sections
- inspect non-junction corridors for speeding, roadside hazards, and poor recovery space
- manage busy daytime periods through enforcement, crossing control, and overtaking checks
- prioritise locations and conditions that appear repeatedly in the top severity groups for engineering review
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
