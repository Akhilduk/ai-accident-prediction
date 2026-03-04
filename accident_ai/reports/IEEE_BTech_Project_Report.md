# AI-Based Accident Analytics and Hotspot Forecasting for Jurisdiction-Level Road Safety Planning

**<YOUR NAME>**, Department of Civil Engineering, <COLLEGE NAME>, <CITY>, India  
Email: <YOUR EMAIL>

## Abstract
Road traffic safety planning needs both historical analysis and predictive intelligence. This project presents a civil-engineering oriented AI platform for accident data cleaning, jurisdiction-level analytics, severity prediction, and hotspot forecasting. The system resolves mixed-format records (date/time/category inconsistencies), decodes coded attributes, and supports interactive filtering for planners. Three models were benchmarked for severity classification: Random Forest, XGBoost, and CatBoost. The deployed workflow integrates model training and user-facing prediction. For hotspot planning, a five-year recursive monthly forecast was implemented with calendar-aligned lag features and seasonality. A comparative toggle between Historical Month Ranking and Predicted Month Ranking improves interpretability for decision-makers. Results indicate that the platform can support practical intervention prioritization at jurisdiction scale through map-based risk visualization, severity probability outputs, and temporal hotspot trend analysis.

**Index Terms**-Road Safety, Accident Analytics, Severity Prediction, Hotspot Forecasting, Machine Learning, Civil Engineering.

## I. INTRODUCTION
Road traffic accidents cause major human and economic losses and remain a core concern for transportation and civil infrastructure systems. Conventional reporting workflows are often descriptive and delayed, limiting proactive planning. This project develops an AI-based platform to support jurisdiction-level road safety decisions through cleaned data, interactive analytics, and future-risk forecasting.

The implemented application allows:
1. structured accident data ingestion and validation,
2. standardization of mixed date/time formats with minimal data loss,
3. severity prediction using trained machine learning models,
4. five-year hotspot forecasting with month/date-based ranking.

## II. PROBLEM STATEMENT
Accident records commonly contain:
1. mixed date formats (`dd/mm/yyyy`, `dd-mm-yyyy`, Excel serial dates),
2. mixed time formats (`8.5`, `11.15`, `20:30`),
3. inconsistent categorical labels (`D/N`, `D/ N`, `Day`, `Night`),
4. code-based collision/vehicle variables requiring decoding.

These issues reduce reliability of both analytics and forecasting, and create difficulty for non-technical users.

## III. OBJECTIVES
1. Build an end-to-end accident analytics and prediction platform.
2. Standardize and clean mixed-format accident records.
3. Train and compare multiple severity classification models.
4. Forecast jurisdiction-level hotspots for 5 years.
5. Provide Historical vs Predicted ranking comparison.
6. Deliver a user-friendly interface for civil engineering planning.

## IV. DATA DESCRIPTION AND PREPROCESSING
### A. Dataset
Input dataset consists of jurisdiction-wise road accident records with attributes including FIR number, date, time, day/night, collision fields, vehicle fields, severity fields, geometry and infrastructure indicators, and location coordinates.

### B. Cleaning Pipeline
The preprocessing pipeline includes:
1. column header normalization for variant spellings/symbols,
2. footer/legend row removal,
3. mixed date parsing with fallback reconstruction from year/month/day columns,
4. mixed time parsing including decimal-like representations,
5. day/night normalization and derived labels,
6. code decoding for collision and vehicle attributes,
7. missing value handling for numeric/categorical fields.

### C. Data Quality Outcome
In tested runs, key derived fields (`Date`, `year`, `month_num`, `day_of_week`, `hour`, `minute`, `D/N`) were fully standardized for valid records and retained for model input.

## V. METHODOLOGY
### A. Severity Prediction
Models evaluated:
1. RandomForestClassifier,
2. XGBoostClassifier,
3. CatBoostClassifier.

Feature preparation uses numeric imputation and one-hot encoding for categorical features, with stratified train-test split and cross-validation.

### B. Hotspot Forecasting
Monthly jurisdiction-level accident counts are generated on a continuous calendar timeline (missing months filled as 0). Forecasting uses recursive monthly prediction over 60 months with lag and seasonality features.

### C. User-Centric Prediction Modes
1. Single Incident prediction (scenario-based),
2. Area Risk Explorer (any filter combination),
3. Hotspot page with Historical vs Predicted ranking source toggle.

## VI. SYSTEM IMPLEMENTATION
The solution is implemented in Python (Streamlit + scikit-learn ecosystem) with modules for:
1. data I/O and validation,
2. cleaning and feature engineering,
3. model training and evaluation,
4. forecasting,
5. visualization and interactive UI.

## VII. RESULTS AND DISCUSSION
### A. Severity Modeling
Model comparison shows XGBoost as best in tested runs (macro-F1 higher than RandomForest and CatBoost in current dataset run).

### B. Historical vs Predicted Behavior
Historical month ranking correctly reflects actual data snapshots (e.g., a specific month where a jurisdiction is top). Predicted ranking may differ due to overall multi-year trend patterns and volume behavior learned from data.

### C. Engineering Interpretation
The platform supports intervention planning by identifying:
1. persistent high-risk jurisdictions,
2. temporal concentration windows (month/day/night),
3. probable severity distribution for selected contexts.

## VIII. LIMITATIONS
1. Forecasting currently excludes exogenous factors (traffic volume, rainfall, enforcement intensity).
2. Jurisdiction-level aggregation may hide micro blackspots.
3. Confidence intervals are not yet displayed in UI.

## IX. CONCLUSION
This project demonstrates an operational AI-assisted road safety analytics platform for civil engineering applications. It improves data standardization, supports interpretable risk analysis, and provides future hotspot ranking for planning decisions. The system is suitable for academic and pilot deployment contexts.

## X. FUTURE WORK
1. Add SHAP-based model explainability.
2. Integrate weather and traffic exposure variables.
3. Add uncertainty bounds for forecast outputs.
4. Integrate GIS layers and blackspot micro-zoning.
5. Deploy with persistent hosted backend.

## REFERENCES
[1] World Health Organization, *Global Status Report on Road Safety*, Geneva, Switzerland, latest ed.  
[2] Ministry of Road Transport and Highways, Government of India, *Road Accidents in India*, latest annual report.  
[3] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," in *Proc. KDD*, 2016.  
[4] L. Breiman, "Random Forests," *Machine Learning*, vol. 45, no. 1, pp. 5-32, 2001.  
[5] A. Dorogush, V. Ershov, and A. Gulin, "CatBoost: gradient boosting with categorical features support," 2018.  
[6] Scikit-learn Documentation. [Online]. Available: https://scikit-learn.org  
[7] Streamlit Documentation. [Online]. Available: https://docs.streamlit.io

---

## FIGURE PLACEHOLDERS (Replace with your screenshots)
**Fig. 1.** Overall system architecture.  
**Fig. 2.** Data upload and dataset management page.  
**Fig. 3.** Dashboard with sidebar filters.  
**Fig. 4.** Month-wise severity trend (filtered).  
**Fig. 5.** Severity distribution chart.  
**Fig. 6.** Model training comparison and best model selection.  
**Fig. 7.** Single incident severity prediction output.  
**Fig. 8.** Hotspot forecast page in Predicted mode.  
**Fig. 9.** Hotspot page in Historical mode.  
**Fig. 10.** Jurisdiction trend comparison chart.

## TABLE PLACEHOLDERS
**TABLE I**  
**Input Variables Used in the Study**

| Sl. No. | Field | Description |
|---|---|---|
| 1 | Date | Accident date |
| 2 | Time | Accident time |
| 3 | Jurisdiction | Place/corridor jurisdiction |
| 4 | Severity fields | Fatal, Grievous, Minor |
| 5 | Geometry/infrastructure | Geometry, median, shoulder, footpath, junction |

**TABLE II**  
**Data Cleaning Rules**

| Rule ID | Raw issue | Standardization action |
|---|---|---|
| R1 | Mixed date separators | Unified datetime parsing with fallback |
| R2 | Decimal-like time | Converted to hour-minute |
| R3 | D/N variants | Normalized to D/N and Day/Night labels |
| R4 | Coded categories | Decoded with reference tables |

**TABLE III**  
**Severity Model Comparison**

| Model | CV Macro-F1 | Test Macro-F1 | Test Accuracy | Rank |
|---|---:|---:|---:|---:|
| Random Forest | <fill> | <fill> | <fill> | <fill> |
| XGBoost | <fill> | <fill> | <fill> | <fill> |
| CatBoost | <fill> | <fill> | <fill> | <fill> |

**TABLE IV**  
**Historical vs Predicted Hotspot Snapshot**

| Year-Month | Ranking Source | Top Jurisdiction | Count/Risk |
|---|---|---|---:|
| 2022-03 | Historical | Chadayamangalam | <fill> |
| 2025-10 | Predicted | <fill> | <fill> |
