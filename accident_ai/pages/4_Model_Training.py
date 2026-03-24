import json

import pandas as pd
import plotly.express as px
import streamlit as st

from src.cleaning import clean_data
from src.config import TRAINING_REPORT_JSON
from src.data_io import get_active_dataset, load_excel_cached
from src.modeling import train_and_compare
from src.ui import apply_theme, style_plotly

SEVERITY_LABEL_MAP = {
    "Fatal": "Fatal",
    "Grievous": "Serious Injury",
    "Minor": "Minor Injury",
}


def _to_user_label(label: str) -> str:
    return SEVERITY_LABEL_MAP.get(str(label), str(label))


def _metric_line(name: str, value: float) -> str:
    return f"**{name}:** {value:.3f} ({value * 100:.1f}%)"


apply_theme(
    "Model Training & Comparison",
    icon="MODEL",
    subtitle="Train 3 AI models, compare quality, and auto-save the best one for prediction.",
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

st.markdown(
    """
### What happens on this page?
- The app trains 3 models: **Random Forest**, **XGBoost**, and **CatBoost** (when the package is installed).
- It compares model quality using test data.
- The best model is saved automatically and used in the **Prediction** page.

### How to understand the scores
- **Accuracy**: Out of all cases, how many were predicted correctly.
- **Macro-F1**: Balanced score across all severity classes (best overall comparison score here).
- **Macro-Recall**: Out of actual cases in each class, how many the model found.
- **CV F1 (5-fold)**: Stability score from repeated validation splits.
"""
)

with st.expander("Technical Words in Simple Language", expanded=False):
    st.markdown(
        """
- **Model**: A math engine that learns patterns from old accident data.
- **Training**: Teaching the model using historical records.
- **Test Data**: Data not shown during training, used for quality checking.
- **Cross Validation (5-fold)**: Repeating training/testing 5 times for stable quality.
- **Confusion Matrix**: Table showing where predictions are correct and where they are mixed up.
- **Feature Importance**: A score showing which input factors the model relied on more during prediction.
- **Importance %**: Feature importance converted into percentage share across all model input features.
- **Best Model**: The model with strongest balanced performance score (Macro-F1).
"""
    )

st.markdown("### Training Speed Options")
c1, c2, c3 = st.columns(3)
with c1:
    run_mode = st.selectbox(
        "Mode",
        ["Fast (Recommended on Cloud)", "Balanced", "Full Accuracy"],
        index=0,
        help="Fast mode is best for Streamlit Cloud. Full Accuracy is slower but gives strongest benchmarking.",
    )
with c2:
    cv_splits = st.selectbox(
        "Cross-validation folds",
        [3, 4, 5],
        index=0 if run_mode == "Fast (Recommended on Cloud)" else (1 if run_mode == "Balanced" else 2),
    )
with c3:
    sample_frac = st.selectbox(
        "Data used for training",
        [0.6, 0.8, 1.0],
        index=0 if run_mode == "Fast (Recommended on Cloud)" else (1 if run_mode == "Balanced" else 2),
        format_func=lambda x: f"{int(x * 100)}%",
    )

fast_mode = run_mode != "Full Accuracy"
estimated_note = (
    "Expected runtime: about 1-3 minutes on cloud."
    if run_mode == "Fast (Recommended on Cloud)"
    else ("Expected runtime: about 3-6 minutes on cloud." if run_mode == "Balanced" else "Expected runtime: can be slow on cloud.")
)
st.caption(f"{estimated_note} Local machine is usually much faster due to stronger CPU and less shared load.")



with st.expander("How training calculations are done (simple + technical)", expanded=False):
    st.markdown(
        """
### A) Exact training pipeline
1. Records with valid severity are used.
2. Data split: **80% train** and **20% test** with class balancing (`stratify=y`).
3. Preprocessing:
   - Numeric columns -> missing values replaced by **median**.
   - Text columns -> missing values replaced by **most frequent value**, then one-hot encoded.
4. Models trained: RandomForest, XGBoost (if installed), CatBoost (if installed locally/cloud).
5. Cross-validation: selected folds (3/4/5) on training set using Macro-F1.
6. Best model is selected by sorting leaderboard by `test_f1_macro`, then `cv_f1_macro_mean`.

### B) Metric formulas with numbers
- **Accuracy** = `correct / total`
  - Example: 160 correct out of 200 => `0.80 (80%)`
- **Precision (for one class)** = `TP / (TP + FP)`
- **Recall (for one class)** = `TP / (TP + FN)`
- **F1 (for one class)** = `2 * (precision * recall) / (precision + recall)`
- **Macro-F1** = average of class-wise F1 values (all classes get equal importance).
  - Example: Fatal F1=0.50, Serious F1=0.70, Minor F1=0.90 -> Macro-F1=`(0.50+0.70+0.90)/3=0.70`.

### C) Confusion matrix: axis and cell meaning
- **Rows (Y-axis)** = Actual class.
- **Columns (X-axis)** = Predicted class.
- Diagonal cell = correct prediction count.
- Off-diagonal cell = model confusion/mistake count.

Example row:
- Actual Fatal -> Predicted [Fatal=18, Serious=7, Minor=1]
- Means 18 correct Fatal detections, 8 Fatal cases misclassified.

### D) How to read leaderboard table and bar chart
- Each row = one algorithm.
- `cv_f1_macro_mean` shows stability across folds.
- `test_f1_macro` is final balanced quality on unseen test data.
- Higher bar in "Model Comparison by Macro-F1" = better overall class-balanced model.
"""
    )

if st.button("Train All 3 Models", type="primary"):
    progress_text = st.empty()
    progress_bar = st.progress(0.0, text="Starting training...")
    log_box = st.empty()
    progress_logs: list[str] = []

    def _progress(p: float, msg: str) -> None:
        progress_bar.progress(float(p), text=msg)
        progress_text.caption(f"Progress: {int(p * 100)}%")
        progress_logs.append(msg)
        log_box.caption("Current step: " + msg)

    with st.spinner("Training in progress... Please wait."):
        leaderboard, report, best = train_and_compare(
            df,
            feature_cols,
            cv_splits=int(cv_splits),
            sample_frac=float(sample_frac),
            fast_mode=bool(fast_mode),
            progress_callback=_progress,
        )
    progress_bar.progress(1.0, text="Training completed.")
    progress_text.caption("Progress: 100%")
    st.success(f"Best model selected: {best}")

    view_leaderboard = leaderboard.copy()
    st.caption("Leaderboard table compares model quality. Higher test_f1_macro usually indicates better balanced performance across all severity classes.")
    st.dataframe(
        view_leaderboard.style.format(
            {
                "cv_f1_macro_mean": "{:.3f}",
                "test_accuracy": "{:.3f}",
                "test_f1_macro": "{:.3f}",
                "test_recall_macro": "{:.3f}",
            }
        ),
        use_container_width=True,
    )
    st.caption("Bar chart compares models using Macro-F1. Highest bar = best overall class-balanced model.")
    st.plotly_chart(
        style_plotly(px.bar(view_leaderboard, x="model", y="test_f1_macro", title="Model Comparison by Macro-F1 (Higher is better)")),
        use_container_width=True,
    )

    with st.expander("What is a Confusion Matrix? (Simple Explanation)", expanded=True):
        st.markdown(
            """
- A confusion matrix is a **truth table** of model results.
- **Rows = Actual severity** from data.
- **Columns = Predicted severity** by model.
- Big numbers on the **diagonal** (top-left to bottom-right) are good: correct predictions.
- Numbers outside diagonal are mistakes (for example, Fatal predicted as Serious Injury).
- **TP (True Positive)** for a class: model correctly says that class.
- **FP (False Positive)** for a class: model predicts that class, but actual is different.
- **FN (False Negative)** for a class: actual is that class, but model predicted something else.
- **TN (True Negative)** for a class: both actual and prediction are other classes.

Use it to answer: **Which severity class is the model confusing most?**
"""
        )

    for model_name, details in report.items():
        if details.get("status") == "failed":
            st.warning(f"{model_name} training failed and was skipped: {details.get('error', 'Unknown error')}")
            continue
        st.subheader(f"{model_name} Confusion Matrix")
        labels = [_to_user_label(x) for x in details["labels"]]
        cm = pd.DataFrame(details["confusion_matrix"], index=labels, columns=labels)
        cm_pct_values = details.get("confusion_matrix_row_pct")
        cm_pct = pd.DataFrame(cm_pct_values, index=labels, columns=labels) if cm_pct_values else pd.DataFrame()
        cm.index.name = "Actual"
        cm.columns.name = "Predicted"
        st.caption("Confusion matrix: rows are actual class, columns are predicted class. Diagonal cells are correct predictions.")
        st.plotly_chart(style_plotly(px.imshow(cm, text_auto=True, title=f"Confusion Matrix - {model_name}")), use_container_width=True)
        if not cm_pct.empty:
            st.caption("Row % matrix: each row totals ~100%. It shows, for each actual class, where predictions went.")
            st.plotly_chart(
                style_plotly(px.imshow(cm_pct.round(1), text_auto=".1f", title=f"Confusion Matrix Row % - {model_name}")),
                use_container_width=True,
            )

        m = details["metrics"]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(_metric_line("Accuracy", float(m["test_accuracy"])))
            st.markdown(_metric_line("Macro-F1", float(m["test_f1_macro"])))
        with c2:
            st.markdown(_metric_line("Macro-Recall", float(m["test_recall_macro"])))
            st.markdown(_metric_line("CV F1 (5-fold)", float(m["cv_f1_macro_mean"])))

        total = float(cm.to_numpy().sum())
        diag = float(cm.to_numpy().trace())
        correct_pct = (diag / total * 100.0) if total else 0.0
        st.caption(
            f"In this matrix, about {correct_pct:.1f}% predictions are on the correct diagonal. "
            "Higher diagonal concentration means a more reliable model."
        )

        feature_importance = details.get("feature_importance", [])
        if feature_importance:
            fi_df = pd.DataFrame(feature_importance)
            fi_df["feature"] = fi_df["feature"].map(_to_user_label).fillna(fi_df["feature"])
            st.caption(
                "Feature Importance (FI): larger score means the model relied more on that input while making predictions. "
                "Importance % is the relative share across shown features."
            )
            st.dataframe(
                fi_df.style.format({"importance": "{:.4f}", "importance_pct": "{:.2f}%"}),
                use_container_width=True,
            )
            shown_total_pct = float(fi_df["importance_pct"].sum())
            st.caption(f"Top shown features cover about {shown_total_pct:.1f}% of total model importance.")
            st.plotly_chart(
                style_plotly(
                    px.bar(
                        fi_df.sort_values("importance_pct"),
                        x="importance_pct",
                        y="feature",
                        orientation="h",
                        title=f"Top Feature Importance - {model_name}",
                    )
                ),
                use_container_width=True,
            )
            st.caption(
                "How to interpret the Top Feature graph: longer bar = stronger influence on model decisions. "
                "This does not prove a direct real-world cause; it only shows what the model used most in this dataset."
            )
            st.caption(
                "Are all factors required for training? Not always. Some features contribute very little and can be removed after validation, "
                "but keeping domain-important factors is usually safer unless performance remains stable after testing."
            )

if TRAINING_REPORT_JSON.exists():
    with st.expander("Latest training report JSON"):
        st.code(json.dumps(json.loads(TRAINING_REPORT_JSON.read_text()), indent=2), language="json")
