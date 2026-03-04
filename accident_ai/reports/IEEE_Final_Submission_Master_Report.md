# B.TECH CIVIL ENGINEERING PROJECT REPORT

## AI-Based Accident Analytics and Hotspot Forecasting for Jurisdiction-Level Road Safety Planning

---

## COVER PAGE (Template)

**PROJECT TITLE**  
AI-Based Accident Analytics and Hotspot Forecasting for Jurisdiction-Level Road Safety Planning

**Submitted by**  
**Student Name:** `[YOUR NAME]`  
**Register Number:** `[YOUR REGISTER NUMBER]`

**Under the Guidance of**  
**Guide Name/Designation:** `[GUIDE NAME], [DESIGNATION], Department of Civil Engineering`

**Department of Civil Engineering**  
`[COLLEGE NAME]`  
`[UNIVERSITY NAME]`  
`[CITY, STATE]`

**Academic Year:** `[20XX-20XX]`

---

## CERTIFICATE (Use College Prescribed Format)

This is to certify that the project report entitled **“AI-Based Accident Analytics and Hotspot Forecasting for Jurisdiction-Level Road Safety Planning”** submitted by **[YOUR NAME]** (Reg. No. **[YOUR REGISTER NUMBER]**) to the Department of Civil Engineering, **[COLLEGE NAME]**, is a bonafide record of work carried out under my supervision.

**Guide Signature**  
**HOD Signature**  
**External/Internal Examiner**

---

## DECLARATION

I, **[YOUR NAME]**, hereby declare that this report is my original work completed under the guidance of **[GUIDE NAME]** and has not been submitted for any other degree/diploma in any institution.

**Place:**  
**Date:**  
**Student Signature**

---

## ACKNOWLEDGEMENT

I express my sincere gratitude to my project guide **[GUIDE NAME]** for continuous support, technical insights, and valuable suggestions throughout this work. I thank the Head of the Department and faculty members of Civil Engineering Department, **[COLLEGE NAME]**, for their guidance and support. I also acknowledge my friends and family for their encouragement.

---

## ABSTRACT

Road traffic safety planning in civil engineering requires both historical analysis and predictive capability for proactive interventions. This project presents an AI-based decision support platform for accident data cleaning, analytics, severity prediction, and hotspot forecasting at jurisdiction level.  

The system resolves mixed-format data issues such as inconsistent date/time representations, encoded categorical values, and day/night label variations. It integrates an interactive dashboard, model benchmarking module, and prediction studio for non-technical users. Severity prediction models (Random Forest, XGBoost, CatBoost) are evaluated using cross-validation and test metrics. A five-year recursive monthly hotspot forecasting model is implemented with calendar continuity and lag-based temporal features.  

The final platform supports practical civil engineering use cases such as risk-prioritized intervention planning, junction treatment targeting, and temporal enforcement strategy. In addition, a Historical-vs-Predicted ranking toggle improves transparency and trust in forecasting outputs.

**Keywords:** Road Safety, Accident Analytics, Hotspot Forecasting, Severity Prediction, Civil Engineering, Machine Learning.

---

## TABLE OF CONTENTS (Fill Page Numbers After Final Formatting)

1. Introduction ............................................. `__`  
2. Problem Statement ........................................ `__`  
3. Objectives ............................................... `__`  
4. Scope of Work ............................................ `__`  
5. Study Area and Dataset Description ....................... `__`  
6. Data Preprocessing and Standardization ................... `__`  
7. System Architecture ...................................... `__`  
8. Methodology .............................................. `__`  
9. Implementation Details ................................... `__`  
10. Results and Discussion .................................. `__`  
11. Civil Engineering Interpretation ........................ `__`  
12. Validation, Reliability, and Error Analysis ............. `__`  
13. Limitations ............................................. `__`  
14. Conclusion .............................................. `__`  
15. Future Scope ............................................ `__`  
16. References .............................................. `__`  
17. Appendices .............................................. `__`

---

## LIST OF FIGURES (Fill Page Numbers)

Fig. 1. Overall system architecture ...................................... `__`  
Fig. 2. Data Manager interface ........................................... `__`  
Fig. 3. Dashboard with sidebar filters ................................... `__`  
Fig. 4. Accident map (filtered) .......................................... `__`  
Fig. 5. Month-wise severity trend ........................................ `__`  
Fig. 6. Severity distribution ............................................ `__`  
Fig. 7. Model training leaderboard ....................................... `__`  
Fig. 8. Confusion matrix of best model ................................... `__`  
Fig. 9. Single incident severity prediction .............................. `__`  
Fig. 10. Hotspot forecast (Predicted mode) ............................... `__`  
Fig. 11. Hotspot ranking (Historical mode) ............................... `__`  
Fig. 12. Jurisdiction trend comparison ................................... `__`

---

## LIST OF TABLES (Fill Page Numbers)

Table 1. Dataset fields and engineering meaning .......................... `__`  
Table 2. Data cleaning rules ............................................. `__`  
Table 3. Severity model comparison ....................................... `__`  
Table 4. Historical vs predicted hotspot comparison ...................... `__`  
Table 5. Software and hardware requirements .............................. `__`

---

# 1. INTRODUCTION

Road accidents continue to be a major challenge in transportation engineering and public safety. Traditional road safety analysis approaches are mostly descriptive and retrospective, which limits their utility for preventive planning. Civil engineers increasingly require digital tools that can integrate data quality correction, analytics, and prediction in one workflow.

This project develops an end-to-end AI-assisted platform focused on:
1. robust preprocessing of accident records,
2. jurisdiction-level risk exploration,
3. machine learning based severity prediction,
4. long-range hotspot forecasting for planning support.

The system is implemented as an interactive web application so that domain users without programming experience can directly use filtered dashboards and predictive outputs.

---

# 2. PROBLEM STATEMENT

Accident data is often operationally collected and manually maintained, leading to:
1. inconsistent date formats (`dd/mm/yyyy`, `dd-mm-yyyy`, mixed text),
2. inconsistent time formats (`8.5`, `11.15`, `20.0`, `20:30`),
3. coded fields for collisions/vehicles requiring decoding,
4. variations in day-night tags (`D/N`, `D/ N`, `Day`, `Night`),
5. footer/legend rows embedded with data rows.

Because of this, direct model training can produce unreliable trends and misleading outputs. Planning agencies need a system that first standardizes data and then produces interpretable predictions (especially jurisdiction-wise future hotspot ranking).

---

# 3. OBJECTIVES

1. Build a complete accident analytics and prediction platform for jurisdiction-level planning.
2. Standardize mixed-format records with maximum retention of valid data.
3. Train and compare multiple severity prediction models.
4. Forecast hotspot risk for a 5-year horizon.
5. Provide side-by-side historical and predicted hotspot ranking.
6. Deliver a user-friendly interface for civil engineering practitioners.

---

# 4. SCOPE OF WORK

## 4.1 In Scope
1. Excel-based accident data ingestion.
2. Cleaning and transformation of structured tabular records.
3. Severity classification and hotspot forecasting.
4. Interactive analytics dashboard and planning interface.

## 4.2 Out of Scope
1. Real-time IoT/live traffic feeds.
2. Automatic CCTV/video analytics.
3. Full GIS network simulation.

---

# 5. STUDY AREA AND DATASET DESCRIPTION

Dataset contains jurisdiction-level accident records with key fields:
1. Place/Jurisdiction
2. FIR number
3. Date, time, day/night
4. Collision pattern/type
5. Vehicle type fields
6. Fatal/Grievous/Minor indicators
7. Geometry and infrastructure fields (median/shoulder/footpath/junction)
8. Latitude and longitude

The records are suitable for both temporal and spatial analytics once standardized.

---

# 6. DATA PREPROCESSING AND STANDARDIZATION

## 6.1 Header Normalization
Column variants are canonicalized to expected schema (`D/ N` -> `D/N`, spacing and slash normalization).

## 6.2 Date Standardization
Multi-pass parsing supports slash/hyphen formats and fallback from alternate date components (`Year of Accident`, `Month of the year`, `DAY OF THE WEEK`).

## 6.3 Time Standardization
Time values like `8.5`, `9.3`, `11.15` are converted to hour-minute semantics with fallback parser.

## 6.4 Category Normalization
Day/Night values normalized to `D`/`N`; additional readable label generated as `day_night_label`.

## 6.5 Master Reference Decoding
Code columns for collision and vehicle classes are decoded through editable reference tables.

## 6.6 Missing Value Handling
1. Numeric columns: median fill.
2. Categorical columns: mode fill with category-safe handling.

## 6.7 Data Quality Outcome (Current Tested Run)
1. Rows after cleaning: **1151**
2. Footer rows removed: **34**
3. Key derived columns (`Date`, `year`, `month_num`, `day_of_week`, `hour`, `minute`, `D/N`) available without nulls in tested run.

---

# 7. SYSTEM ARCHITECTURE

The application consists of four major user modules and one shared backend layer.

## 7.1 User Modules
1. **Home:** summary, KPIs, quick navigation.
2. **Data Manager:** upload/version selection, validation, cleaned view.
3. **Dashboard:** filter-driven maps/charts/hotspots.
4. **Model Training & Prediction:** model benchmarking, severity risk prediction, hotspot forecasting.

## 7.2 Backend Components
1. `cleaning.py` – data transformation and feature derivation.
2. `modeling.py` – model training, evaluation, best-model persistence.
3. `forecasting.py` – monthly recursive hotspot forecasting.
4. `viz.py`/`ui.py` – visualization and theme system.

---

# 8. METHODOLOGY

## 8.1 Severity Prediction Workflow
1. Select features from cleaned dataset.
2. Split train/test with stratification.
3. Build preprocessing + model pipelines.
4. Evaluate using CV and hold-out metrics.
5. Save best model for inference in Prediction Studio.

## 8.2 Models Evaluated
1. RandomForestClassifier
2. XGBoostClassifier
3. CatBoostClassifier

## 8.3 Evaluation Metrics
1. Accuracy
2. Macro-F1
3. Macro-Recall
4. Confusion Matrix

## 8.4 Hotspot Forecasting Method
1. Aggregate monthly accident counts per jurisdiction.
2. Create continuous month timelines (missing months filled with 0).
3. Generate lag and seasonality features:
   - lag_1, lag_2, lag_3
   - rolling_3
   - month sin/cos
   - trend index
4. Train GradientBoostingRegressor.
5. Forecast recursively for 60 months.

## 8.5 Historical vs Predicted Comparison
Hotspot page supports:
1. **Historical (Actual Data):** rank by observed count for selected month-year.
2. **Predicted (AI Forecast):** rank by model-estimated count/risk for selected period.

---

# 9. IMPLEMENTATION DETAILS

## 9.1 Software Stack
1. Python 3.12
2. Streamlit
3. pandas, numpy
4. scikit-learn
5. xgboost, catboost
6. plotly

## 9.2 Deployment Pattern
Local-first app, with potential free hosting on Streamlit Community Cloud/Hugging Face Spaces.

## 9.3 User Experience Features
1. Sidebar filters with clear/reset behavior.
2. Theme adaptability and appearance controls.
3. Readable labels for non-technical users.

---

# 10. RESULTS AND DISCUSSION

## 10.1 Severity Model Metrics (Latest Run)

| Model | CV Macro-F1 | Test Accuracy | Test Macro-F1 | Test Macro-Recall |
|---|---:|---:|---:|---:|
| XGBoost | 0.3412 | 0.7273 | 0.3821 | 0.3779 |
| CatBoost | 0.2942 | 0.7619 | 0.3282 | 0.3518 |
| RandomForest | 0.2928 | 0.7532 | 0.3070 | 0.3388 |

**Inference:** XGBoost selected as best model based on macro-F1.

## 10.2 Historical Validation Example
For March 2022 historical ranking (actual data), top jurisdictions include:
1. Chadayamangalam
2. Kottarakkara
3. Venjarammood

## 10.3 Forecast Interpretation
Predicted rankings may not match a single historical snapshot because forecast reflects multi-year patterns and learned trend behavior. High-volume jurisdictions can remain top across multiple forecast months.

---

# 11. CIVIL ENGINEERING INTERPRETATION

The platform supports practical planning decisions:
1. **Persistent hotspot detection** for corridor prioritization.
2. **Temporal pattern analysis** (month/day/night) for enforcement scheduling.
3. **Severity-risk interpretation** under different geometry and junction contexts.
4. **Infrastructure intervention planning**:
   - shoulder and median treatment
   - junction redesign
   - night-visibility improvement
   - signage and speed management

---

# 12. VALIDATION, RELIABILITY, AND ERROR ANALYSIS

## 12.1 Data Reliability
Input inconsistencies are reduced by deterministic preprocessing rules and fallback reconstruction logic.

## 12.2 Model Reliability
Cross-validation and hold-out evaluation used for severity model comparison.

## 12.3 Forecast Reliability Notes
1. Forecast is univariate-plus-seasonality and trend-based.
2. External factors are not yet included; interpret as planning guidance, not deterministic truth.

---

# 13. LIMITATIONS

1. No explicit traffic exposure variables (AADT/volume).
2. No weather/rainfall/external event covariates.
3. No uncertainty bands shown for forecast output.
4. Jurisdiction-level aggregation may hide micro blackspots.

---

# 14. CONCLUSION

An end-to-end AI platform was developed for road safety analytics and prediction in civil engineering context. The workflow resolves practical data-quality challenges and provides actionable outputs through dashboard, severity prediction, and 5-year hotspot forecasting. Historical-vs-predicted comparison enhances interpretability and decision confidence for planning agencies.

---

# 15. FUTURE SCOPE

1. Add external covariates (weather, traffic flow, speed).
2. Add explainability modules (SHAP/LIME).
3. Add forecast confidence intervals.
4. Integrate GIS road class and geometric descriptors.
5. Extend to intervention recommendation optimization.

---

# 16. REFERENCES (IEEE STYLE)

[1] World Health Organization, *Global Status Report on Road Safety*, Geneva, Switzerland, latest ed.  
[2] Ministry of Road Transport and Highways, Government of India, *Road Accidents in India*, latest annual report.  
[3] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," in *Proc. KDD*, 2016.  
[4] L. Breiman, "Random Forests," *Machine Learning*, vol. 45, no. 1, pp. 5-32, 2001.  
[5] A. Dorogush, V. Ershov, and A. Gulin, "CatBoost: gradient boosting with categorical features support," 2018.  
[6] Scikit-learn Documentation, https://scikit-learn.org  
[7] Streamlit Documentation, https://docs.streamlit.io

---

# 17. FIGURE PLACEHOLDERS

**Fig. 1.** Overall system architecture flowchart  
**Fig. 2.** Data Manager page (upload/version/validation)  
**Fig. 3.** Dashboard with sidebar filters  
**Fig. 4.** Accident map (filtered view)  
**Fig. 5.** Month-wise severity trend  
**Fig. 6.** Severity distribution chart  
**Fig. 7.** Model training leaderboard  
**Fig. 8.** Best model confusion matrix  
**Fig. 9.** Single scenario severity prediction  
**Fig. 10.** Hotspot forecast (Predicted mode)  
**Fig. 11.** Hotspot ranking (Historical mode)  
**Fig. 12.** Jurisdiction trend comparison chart

---

# 18. TABLE PLACEHOLDERS

## Table 1. Dataset Fields and Description
| Sl. No. | Field | Description |
|---|---|---|
| 1 | Jurisdiction/Place | Administrative corridor jurisdiction |
| 2 | Date/Time | Accident timestamp |
| 3 | D/N | Day-night classification |
| 4 | Collision fields | Pattern and type details |
| 5 | Vehicle fields | Involved vehicle class codes |
| 6 | Severity fields | Fatal, grievous, minor indicators |
| 7 | Infra fields | Geometry, median, shoulder, footpath, junction |
| 8 | Coordinates | Latitude and Longitude |

## Table 2. Data Cleaning Rules
| Rule ID | Raw Issue | Action |
|---|---|---|
| R1 | Header mismatch | Canonicalization |
| R2 | Mixed dates | Multi-pass parsing + fallback |
| R3 | Mixed times | Decimal/time parsing |
| R4 | D/N variants | Normalization to D/N |
| R5 | Footer rows | Pattern-based removal |
| R6 | Missing values | Median/Mode filling |

## Table 3. Model Comparison (Filled)
| Model | CV Macro-F1 | Test Accuracy | Test Macro-F1 | Test Macro-Recall |
|---|---:|---:|---:|---:|
| XGBoost | 0.3412 | 0.7273 | 0.3821 | 0.3779 |
| CatBoost | 0.2942 | 0.7619 | 0.3282 | 0.3518 |
| RandomForest | 0.2928 | 0.7532 | 0.3070 | 0.3388 |

## Table 4. Historical vs Predicted Hotspot Snapshot
| Year-Month | Source | Top Jurisdiction | Value |
|---|---|---|---:|
| 2022-03 | Historical | Chadayamangalam | `<actual_count>` |
| 2025-10 | Predicted | `<jurisdiction>` | `<predicted_count>` |

## Table 5. Hardware and Software Requirements
| Item | Specification |
|---|---|
| CPU | Intel i5 / Ryzen 5 or above |
| RAM | 8 GB minimum (16 GB recommended) |
| OS | Windows 10/11 |
| Python | 3.12 |
| Libraries | Streamlit, pandas, numpy, scikit-learn, xgboost, catboost, plotly |

---

# 19. APPENDIX A: USER MANUAL

1. Open Data Manager and upload/select active dataset.
2. Review validation and cleaned preview.
3. Open Dashboard and apply filters (place/year/month/day/night/etc.).
4. Train models in Model Training page.
5. Use Prediction Studio:
   - Severity AI Prediction
   - Hotspot Forecast (Historical/Predicted)

---

# 20. APPENDIX B: REPRODUCIBILITY COMMANDS

```powershell
cd accident_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

---

# 21. FINAL SUBMISSION CHECKLIST

1. Replace placeholders:
   - `[YOUR NAME]`
   - `[YOUR REGISTER NUMBER]`
   - `[COLLEGE NAME]`, `[UNIVERSITY NAME]`
   - `[GUIDE NAME]`, `[DESIGNATION]`
   - `[20XX-20XX]`
2. Insert all figure screenshots with captions.
3. Verify table numbering and pagination.
4. Ensure reference style is IEEE.
5. Export to PDF after final proofreading.
