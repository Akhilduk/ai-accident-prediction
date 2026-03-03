from __future__ import annotations

import json
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
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
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
    if CatBoostClassifier is not None:
        models["CatBoost"] = CatBoostClassifier(iterations=250, learning_rate=0.05, depth=8, verbose=False, random_seed=42)
    return models


def train_and_compare(df: pd.DataFrame, feature_cols: list[str], target_col: str = "severity_target"):
    train_df = df[df[target_col].notna()].copy()
    X = train_df[feature_cols]
    y = train_df[target_col]
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    preprocessor = _build_preprocessor(X)
    models = get_models()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    rows = []
    trained = {}
    report = {}

    for name, model in models.items():
        pipe = Pipeline([("preprocessor", preprocessor), ("model", model)])
        cv_scores = cross_val_score(pipe, x_train, y_train, scoring="f1_macro", cv=cv)
        pipe.fit(x_train, y_train)
        pred = pipe.predict(x_test)
        proba = pipe.predict_proba(x_test) if hasattr(pipe, "predict_proba") else None
        metrics = {
            "model": name,
            "cv_f1_macro_mean": float(cv_scores.mean()),
            "test_accuracy": float(accuracy_score(y_test, pred)),
            "test_f1_macro": float(f1_score(y_test, pred, average="macro")),
            "test_recall_macro": float(recall_score(y_test, pred, average="macro")),
        }
        rows.append(metrics)
        trained[name] = {"pipeline": pipe, "y_test": y_test, "pred": pred, "proba": proba}
        report[name] = {
            "metrics": metrics,
            "classification_report": classification_report(y_test, pred, output_dict=True),
            "confusion_matrix": confusion_matrix(y_test, pred, labels=sorted(y.unique())).tolist(),
            "labels": sorted(y.unique()),
        }

    leaderboard = pd.DataFrame(rows).sort_values(["test_f1_macro", "cv_f1_macro_mean"], ascending=False)
    best_model_name = leaderboard.iloc[0]["model"]
    best_pipeline = trained[best_model_name]["pipeline"]

    BEST_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": best_pipeline, "features": feature_cols, "target": target_col}, BEST_MODEL_PATH)
    leaderboard.to_csv(LEADERBOARD_PATH, index=False)
    leaderboard.to_csv(TRAINING_REPORT_CSV, index=False)
    Path(TRAINING_REPORT_JSON).write_text(json.dumps(report, indent=2))

    return leaderboard, report, best_model_name


def load_best_model():
    if not BEST_MODEL_PATH.exists():
        return None
    return joblib.load(BEST_MODEL_PATH)
