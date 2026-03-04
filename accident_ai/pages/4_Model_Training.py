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
    icon="AI",
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
- The app trains 3 models: **Random Forest**, **XGBoost**, and **CatBoost**.
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
- **Best Model**: The model with strongest balanced performance score (Macro-F1).
"""
    )

if st.button("Train All 3 Models", type="primary"):
    with st.spinner("Training in progress..."):
        leaderboard, report, best = train_and_compare(df, feature_cols)
    st.success(f"Best model selected: {best}")

    view_leaderboard = leaderboard.copy()
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

Use it to answer: **Which severity class is the model confusing most?**
"""
        )

    for model_name, details in report.items():
        st.subheader(f"{model_name} Confusion Matrix")
        labels = [_to_user_label(x) for x in details["labels"]]
        cm = pd.DataFrame(details["confusion_matrix"], index=labels, columns=labels)
        cm.index.name = "Actual"
        cm.columns.name = "Predicted"
        st.plotly_chart(style_plotly(px.imshow(cm, text_auto=True, title=f"Confusion Matrix - {model_name}")), use_container_width=True)

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

if TRAINING_REPORT_JSON.exists():
    with st.expander("Latest training report JSON"):
        st.code(json.dumps(json.loads(TRAINING_REPORT_JSON.read_text()), indent=2), language="json")
