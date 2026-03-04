from __future__ import annotations

import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder

from src.config import BEST_MODEL_PATH, LEADERBOARD_PATH, REPORTS_DIR, TRAINING_REPORT_CSV, TRAINING_REPORT_JSON

try:
    from xgboost import XGBClassifier
except Exception:
    XGBClassifier = None

try:
    from catboost import CatBoostClassifier
except Exception:
    CatBoostClassifier = None


def _build_preprocessor(X: pd.DataFrame):
    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = [c for c in X.columns if c not in numeric_features]
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric_features),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        # Dense output avoids sparse-index issues seen with CatBoost on some environments.
                        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical_features,
            ),
        ]
    )
    return preprocessor


def get_models():
    models = {"RandomForest": RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced")}
    if XGBClassifier is not None:
        models["XGBoost"] = XGBClassifier(
            n_estimators=250,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=42,
        )
    # CatBoost is optional and disabled by default for cloud stability.
    # Enable explicitly with environment variable: ENABLE_CATBOOST=1
    if CatBoostClassifier is not None and os.getenv("ENABLE_CATBOOST", "0") == "1":
        models["CatBoost"] = CatBoostClassifier(iterations=250, learning_rate=0.05, depth=8, verbose=False, random_seed=42)
    return models


def train_and_compare(df: pd.DataFrame, feature_cols: list[str], target_col: str = "severity_target"):
    train_df = df[df[target_col].notna()].copy()
    X = train_df[feature_cols]
    y = train_df[target_col]
    label_encoder = LabelEncoder()
    label_encoder.fit(y)
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    preprocessor = _build_preprocessor(X)
    models = get_models()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    rows = []
    trained = {}
    report = {}

    for name, model in models.items():
        try:
            pipe = Pipeline([("preprocessor", preprocessor), ("model", model)])
            use_encoded_target = name == "XGBoost"
            y_train_fit = label_encoder.transform(y_train) if use_encoded_target else y_train
            y_test_eval = label_encoder.transform(y_test) if use_encoded_target else y_test

            cv_scores = cross_val_score(pipe, x_train, y_train_fit, scoring="f1_macro", cv=cv, error_score="raise")
            pipe.fit(x_train, y_train_fit)
            pred_raw = pipe.predict(x_test)
            pred = label_encoder.inverse_transform(pred_raw.astype(int)) if use_encoded_target else pred_raw
            proba = pipe.predict_proba(x_test) if hasattr(pipe, "predict_proba") else None
            class_labels = label_encoder.classes_.tolist() if use_encoded_target else list(pipe.classes_)
            metrics = {
                "model": name,
                "cv_f1_macro_mean": float(cv_scores.mean()),
                "test_accuracy": float(accuracy_score(y_test_eval, pred_raw) if use_encoded_target else accuracy_score(y_test, pred)),
                "test_f1_macro": float(f1_score(y_test_eval, pred_raw, average="macro") if use_encoded_target else f1_score(y_test, pred, average="macro")),
                "test_recall_macro": float(
                    recall_score(y_test_eval, pred_raw, average="macro") if use_encoded_target else recall_score(y_test, pred, average="macro")
                ),
            }
            rows.append(metrics)
            trained[name] = {"pipeline": pipe, "y_test": y_test, "pred": pred, "proba": proba, "class_labels": class_labels}
            report[name] = {
                "status": "ok",
                "metrics": metrics,
                "classification_report": classification_report(y_test, pred, output_dict=True),
                "confusion_matrix": confusion_matrix(y_test, pred, labels=sorted(y.unique())).tolist(),
                "labels": sorted(y.unique()),
            }
        except Exception as exc:
            report[name] = {"status": "failed", "error": str(exc)}

    if not rows:
        raise RuntimeError("All models failed during training. Check data quality and dependencies.")

    leaderboard = pd.DataFrame(rows).sort_values(["test_f1_macro", "cv_f1_macro_mean"], ascending=False)
    best_model_name = leaderboard.iloc[0]["model"]
    best_pipeline = trained[best_model_name]["pipeline"]
    best_class_labels = trained[best_model_name]["class_labels"]

    BEST_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": best_pipeline,
            "features": feature_cols,
            "target": target_col,
            "class_labels": best_class_labels,
            "model_name": best_model_name,
        },
        BEST_MODEL_PATH,
    )
    leaderboard.to_csv(LEADERBOARD_PATH, index=False)
    leaderboard.to_csv(TRAINING_REPORT_CSV, index=False)
    Path(TRAINING_REPORT_JSON).write_text(json.dumps(report, indent=2))

    return leaderboard, report, best_model_name


def load_best_model():
    if not BEST_MODEL_PATH.exists():
        return None
    return joblib.load(BEST_MODEL_PATH)
