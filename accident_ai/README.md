# Road Accident Analytics & AI Prediction

Python-only Streamlit app for end-to-end accident analytics, ML severity prediction, and hotspot forecasting.

## Features
- Excel upload + local version management (`data/uploads/`)
- Data cleaning with project-specific normalization and legend/footer row removal
- Master-reference decoding for collision and vehicle codes
- UI-based master reference manager (add/edit/delete codes) persisted locally
- Interactive analytics dashboard with filters, map, charts, and hotspot table
- 3-model severity classification benchmark:
  - RandomForestClassifier
  - XGBoostClassifier
  - CatBoostClassifier
- Model comparison (CV + test metrics), confusion matrices, and saved best model
- Prediction page:
  - Record-level severity probabilities
  - Place-month hotspot forecast and ranking

## Project structure

```
accident_ai/
  app.py
  pages/
    0_Project_Documentation.py
    1_Home.py
    2_Data_Manager.py
    3_Dashboard.py
    4_Model_Training.py
    5_Prediction.py
  src/
    config.py
    master_reference.py
    data_io.py
    cleaning.py
    features.py
    modeling.py
    forecasting.py
    viz.py
    utils.py
  data/uploads/
  data/processed/
  models/
  reports/
  requirements.txt
```

## Setup
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Default dataset
At startup, app auto-detects and uses:
`/mnt/data/previous accident data (1).xlsx`

If missing, upload via **Data Upload & Manager** page.

## Persistence
- Upload versions: `data/uploads/YYYYMMDD_HHMMSS_filename.xlsx`
- Active cleaned file: `data/processed/active_cleaned.csv`
- Best model: `models/best_model.joblib`
- Reports: `reports/`
- Editable master reference store: `data/master_reference.json`
