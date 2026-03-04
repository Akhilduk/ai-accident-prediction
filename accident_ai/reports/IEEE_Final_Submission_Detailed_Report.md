# AI-Based Accident Analytics and Hotspot Forecasting for Jurisdiction-Level Road Safety Planning

**<YOUR NAME>**, Department of Civil Engineering, <COLLEGE NAME>, <CITY>, India  
**Guide:** <GUIDE NAME>, <DESIGNATION>, Department of Civil Engineering, <COLLEGE NAME>  
**Email:** <YOUR EMAIL>

---

## Front Matter (For Final Submission Binding)

### 1. Cover Page (Use college-prescribed format)
- Title
- Student name and register number
- Department and institution
- Guide details
- Academic year

### 2. Certificate (department format)
Include standard departmental certificate page signed by Guide/HOD.

### 3. Declaration
I hereby declare that the project report entitled **“AI-Based Accident Analytics and Hotspot Forecasting for Jurisdiction-Level Road Safety Planning”** is my original work carried out under supervision of **<GUIDE NAME>**, and has not been submitted to any other institution for any degree.

### 4. Acknowledgement
Acknowledgement text to Guide, HOD, Department, institution, and family.

### 5. Abstract
Road safety planning in civil engineering requires both historical interpretation and predictive capability for proactive interventions. This project presents an AI-assisted accident analytics platform that integrates data cleaning, severity classification, hotspot forecasting, and interactive visual decision support. The system processes mixed-format accident records, normalizes jurisdiction-level features, and benchmarks Random Forest, XGBoost, and CatBoost classifiers for severity prediction. A five-year recursive hotspot forecast is implemented with continuous month alignment, lag features, and seasonality/trend encoding. A dedicated user interface supports filtered analytics, scenario-based prediction, and comparison between historical and predicted hotspot rankings. The platform addresses field-level data inconsistency while enabling engineering interpretation for median/shoulder upgrades, junction treatment, speed management, and corridor prioritization. Results indicate practical viability as a planning support tool for civil/transport safety decision-making.

**Index Terms**—Road Safety, Accident Severity, Hotspot Forecasting, Civil Engineering Analytics, Machine Learning, Decision Support.

---

## I. INTRODUCTION
Road traffic crashes are a major safety and economic challenge in developing and developed transport systems. Conventional analysis methods are often retrospective and static, whereas modern safety planning requires dynamic tools that can learn from historical records and estimate future risk.  

Civil engineering safety interventions (geometry correction, shoulder development, median treatment, and junction redesign) become more effective when supported by jurisdiction-level evidence and predictive insights. This project proposes a deployable AI workflow for:
1. robust cleaning of accident records,
2. filtered, map-based visual analytics,
3. model-driven severity prediction,
4. long-horizon hotspot forecasting.

The project was implemented as an interactive web application to ensure adoption by users with limited coding background.

---

## II. PROBLEM STATEMENT
Accident datasets from field offices typically contain:
1. inconsistent date formats (`dd/mm/yyyy`, `dd-mm-yyyy`, serial date-like values),
2. inconsistent time formats (`8.5`, `11.15`, `20.0`, `HH:MM`),
3. inconsistent day/night values (`D/N`, `D/ N`, `Day`, `Night`),
4. coded values requiring master-reference decoding,
5. missing and noisy records.

These issues reduce confidence in both analytics and predictive model outputs. Additionally, existing dashboards usually do not provide direct **historical vs predicted** hotspot comparison for jurisdiction-level decision making.

---

## III. OBJECTIVES
1. Create an end-to-end AI platform for accident analytics and prediction.
2. Preserve maximum useful records through robust preprocessing.
3. Compare multiple models for severity prediction.
4. Forecast hotspots for 5 years with calendar-consistent logic.
5. Provide interpretable UI for non-technical users.
6. Enable historical vs predicted hotspot ranking comparison.

---

## IV. SCOPE OF WORK
### In Scope
- Excel-based accident data processing
- Jurisdiction-level analytics
- Severity classification (Fatal/Grievous/Minor)
- Hotspot forecasting (month/date views)
- Web app for analysis and prediction

### Out of Scope
- Real-time streaming data integration
- External live APIs (weather/traffic flow)
- Automatic GIS road-geometry extraction from shapefiles

---

## V. LITERATURE CONTEXT (Brief)
Recent road safety research emphasizes:
1. tree-based models for tabular crash severity data,
2. temporal aggregation for hotspot prioritization,
3. map-centric decision interfaces for planners.

XGBoost and related boosted models are widely used in risk classification due to strong non-linear fitting capability. However, success in practical deployments depends heavily on preprocessing quality and user interpretation support.

---

## VI. DATASET AND PREPROCESSING
### A. Input Data Fields
Core fields include:
- jurisdiction/place
- FIR number
- latitude/longitude
- date, time, day/night
- collision pattern/type
- vehicle type fields
- fatal/grievous/minor/severity
- infrastructure fields (median, shoulder, footpath, junction)

### B. Data Quality Issues Identified
1. header variations (`D/ N` vs `D/N`)
2. mixed separators in date
3. decimal-style time
4. categorical inconsistencies
5. legend/footer rows in source sheets

### C. Cleaning Strategy
1. Header canonicalization to required schema
2. Footer/legend row detection and removal
3. Mixed date parsing with fallback reconstruction from Year/Month/Day columns
4. Mixed time parsing including decimal semantics (`9.3` -> `09:30`)
5. D/N normalization and `day_night_label` derivation
6. Master reference decoding for coded columns
7. Numerical and categorical missing-value handling
8. Year sanity filtering for unrealistic parsed values

### D. Cleaned Output
Derived fields include:
- `year`, `month_num`, `day`, `day_of_week`
- `hour`, `minute`, `time_bucket`
- `is_weekend`, `is_night`
- decoded collision and vehicle labels

---

## VII. SYSTEM ARCHITECTURE
The implemented system has five logical layers:

1. **Data Layer**
   - Excel input
   - active dataset pointer
   - versioned upload store

2. **Processing Layer**
   - validation
   - cleaning
   - feature derivation
   - code decoding

3. **Modeling Layer**
   - severity model benchmarking
   - best model serialization
   - forecasting model

4. **Visualization Layer**
   - dashboard charts and map
   - confusion matrices
   - risk ranking charts

5. **Interaction Layer**
   - Data Manager
   - Dashboard
   - Model Training
   - Prediction Studio

---

## VIII. METHODOLOGY
## A. Severity Prediction
### 1) Feature Pipeline
- Numeric: median imputation
- Categorical: frequent-imputation + one-hot encoding
- Unified sklearn pipeline for reproducibility

### 2) Models
- RandomForestClassifier
- XGBoostClassifier
- CatBoostClassifier

### 3) Evaluation
- Train/test split with stratification
- 5-fold stratified CV
- Metrics:
  - Accuracy
  - Macro F1
  - Macro Recall
  - Confusion matrix

### 4) Metric Equations
\[
Accuracy = \frac{TP + TN}{TP + TN + FP + FN}
\]

\[
F1 = 2 \cdot \frac{Precision \cdot Recall}{Precision + Recall}
\]

Macro-F1 is computed as arithmetic mean across classes.

## B. Hotspot Forecasting
### 1) Aggregation
Jurisdiction-wise monthly accident count time series.

### 2) Calendar Continuity Correction
Missing months are explicitly filled with `0` to preserve proper lag semantics.

### 3) Forecast Features
- lag_1, lag_2, lag_3
- rolling_3
- month seasonality (`sin`, `cos`)
- trend index

### 4) Forecast Mechanism
Recursive monthly prediction for 60 months (5 years) using GradientBoostingRegressor.

### 5) Ranking Modes
- **Predicted mode**: model output for selected period
- **Historical mode**: actual observed counts for selected period
- **Date risk mode**: weekday-weighted daily risk (predicted)

---

## IX. IMPLEMENTATION DETAILS
### A. Technology Stack
- Python
- Streamlit
- pandas, numpy
- scikit-learn
- xgboost, catboost
- plotly

### B. Project Structure (Representative)
```
accident_ai/
  app.py
  pages/
    1_Home.py
    2_Data_Manager.py
    3_Dashboard.py
    4_Model_Training.py
    5_Prediction.py
  src/
    cleaning.py
    data_io.py
    modeling.py
    forecasting.py
    ui.py
    viz.py
```

### C. User Workflows
1. Upload/select dataset in Data Manager
2. Validate cleaned output
3. Train models and select best performer
4. Use Severity prediction or Hotspot forecast for planning

---

## X. RESULTS
### A. Severity Benchmark (Sample Run)
| Model | Test Macro-F1 | Remarks |
|---|---:|---|
| XGBoost | ~0.398 | Best in current run |
| Random Forest | ~0.307 | Stable baseline |
| CatBoost | ~0.306 | Comparable to RF |

### B. Historical Check Example
Historical month ranking can show jurisdiction-specific peaks (example month where Chadayamangalam ranks first), validating that actual data ranking is preserved.

### C. Forecast Behavior
Predicted rankings may differ from specific historical months due to broader temporal trend and relative volume dominance across years.

### D. UI and Usability Outcomes
- Sidebar-based filters for dashboard and hotspot analysis
- historical vs predicted comparison toggle
- improved user readability with adaptive theme controls

---

## XI. ENGINEERING SIGNIFICANCE
The project supports civil engineering planning by:
1. identifying high-risk jurisdictions,
2. highlighting month/day/night concentration,
3. prioritizing geometric and operational interventions,
4. enabling evidence-based resource allocation.

Potential intervention categories:
- shoulder widening and maintenance
- median protection and channelization
- junction conflict reduction measures
- lighting/signage enhancement
- enforcement at high-risk time windows

---

## XII. LIMITATIONS
1. No direct exposure variables (traffic volume) in current feature set.
2. Exogenous variables (weather, enforcement) not integrated.
3. Forecast uncertainty intervals not yet displayed.
4. Jurisdiction aggregation can mask micro blackspots.

---

## XIII. FUTURE WORK
1. Add SHAP-based explanation panel.
2. Integrate rainfall, traffic exposure, and road class.
3. Add confidence intervals and scenario simulation.
4. GIS-linked micro-blackspot detection.
5. Deploy with persistent cloud database.

---

## XIV. CONCLUSION
This project delivers a complete AI-assisted safety analytics pipeline suitable for B.Tech Civil Engineering application and demonstration. It combines robust preprocessing, severity classification, and multi-year hotspot forecasting in a practical interface. The added historical-vs-predicted comparison improves planning transparency and trust in model outputs.

---

## XV. REFERENCES (IEEE STYLE)
[1] World Health Organization, *Global Status Report on Road Safety*, Geneva, Switzerland, latest ed.  
[2] Ministry of Road Transport and Highways, Government of India, *Road Accidents in India*, latest annual report.  
[3] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD)*, 2016, pp. 785-794.  
[4] L. Breiman, "Random Forests," *Machine Learning*, vol. 45, no. 1, pp. 5-32, 2001.  
[5] A. V. Dorogush, V. Ershov, and A. Gulin, "CatBoost: Gradient boosting with categorical features support," 2018.  
[6] Scikit-learn Developers, "Scikit-learn documentation." [Online]. Available: https://scikit-learn.org  
[7] Streamlit Inc., "Streamlit documentation." [Online]. Available: https://docs.streamlit.io  

---

## XVI. FIGURE PLACEHOLDERS (Insert screenshots before final print)
**Fig. 1.** System architecture diagram  
**Fig. 2.** Data Manager page (upload + validation)  
**Fig. 3.** Dashboard with sidebar filters  
**Fig. 4.** Accident map with severity colors  
**Fig. 5.** Month-wise severity trend (filtered)  
**Fig. 6.** Severity distribution chart  
**Fig. 7.** Model training leaderboard  
**Fig. 8.** Confusion matrix of best model  
**Fig. 9.** Single-incident AI severity prediction output  
**Fig. 10.** Hotspot forecast page (Predicted mode)  
**Fig. 11.** Hotspot forecast page (Historical mode)  
**Fig. 12.** Jurisdiction trend comparison chart  

---

## XVII. TABLE PLACEHOLDERS
### TABLE I  
**Input Variables**

| Sl. No. | Variable | Type | Description |
|---|---|---|---|
| 1 | Date | Date | Accident date |
| 2 | Time | Time | Accident time |
| 3 | Jurisdiction | Categorical | Place/corridor jurisdiction |
| 4 | D/N | Categorical | Day/Night |
| 5 | Severity | Categorical | Fatal/Grievous/Minor |
| 6 | Geometry | Categorical | Road geometry |
| 7 | Median/Shoulder/Footpath/Junction | Categorical | Infrastructure context |
| 8 | Lat/Long | Numeric | Spatial coordinates |

### TABLE II  
**Data Cleaning Rules**

| Rule | Problem | Action |
|---|---|---|
| R1 | Header variants | Canonicalized to required names |
| R2 | Mixed date formats | Multi-pass parse + fallback reconstruction |
| R3 | Mixed time formats | Decimal/time-string conversion |
| R4 | D/N inconsistencies | Standardized to D or N |
| R5 | Footer/legend rows | Pattern-based removal |
| R6 | Missing values | Numeric median, categorical mode |

### TABLE III  
**Severity Model Benchmark**

| Model | CV Macro-F1 | Test Accuracy | Test Macro-F1 | Test Macro-Recall |
|---|---:|---:|---:|---:|
| Random Forest | <fill> | <fill> | <fill> | <fill> |
| XGBoost | <fill> | <fill> | <fill> | <fill> |
| CatBoost | <fill> | <fill> | <fill> | <fill> |

### TABLE IV  
**Historical vs Predicted Hotspot Snapshot**

| Year-Month | Ranking Source | Top Jurisdiction | Value |
|---|---|---|---:|
| 2022-03 | Historical | Chadayamangalam | <actual_count> |
| 2025-10 | Predicted | <jurisdiction> | <predicted_count> |

---

## XVIII. APPENDIX A: USER MANUAL (SHORT)
1. Run app and open Data Manager.
2. Upload/select active dataset.
3. Open Dashboard and apply filters.
4. Train model from Model Training page.
5. Use Prediction page:
   - Severity mode for scenario risk
   - Hotspot mode for historical/predicted ranking

---

## XIX. APPENDIX B: REPRODUCIBILITY
### A. Run Commands
```powershell
cd accident_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

### B. Artifacts
- cleaned dataset output
- model leaderboard
- best model bundle
- forecast exports

---

## XX. CHECKLIST FOR FINAL SUBMISSION
1. Replace all placeholders (`<YOUR NAME>`, `<COLLEGE NAME>`, etc.)
2. Paste real screenshots for all figure placeholders
3. Fill model metric tables from latest run
4. Ensure page numbers and section formatting per department guide
5. Export final PDF after proofreading
