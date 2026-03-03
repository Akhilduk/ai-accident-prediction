from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"

DEFAULT_DATASET = Path("/mnt/data/previous accident data (1).xlsx")
ACTIVE_DATASET_POINTER = DATA_DIR / "active_dataset.txt"
CLEANED_DATASET = PROCESSED_DIR / "active_cleaned.csv"
BEST_MODEL_PATH = MODELS_DIR / "best_model.joblib"
LEADERBOARD_PATH = REPORTS_DIR / "model_leaderboard.csv"
TRAINING_REPORT_JSON = REPORTS_DIR / "training_report.json"
TRAINING_REPORT_CSV = REPORTS_DIR / "training_report.csv"
HOTSPOT_FORECAST_PATH = REPORTS_DIR / "hotspot_forecast.csv"

REQUIRED_COLUMNS = [
    "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION",
    "FIR NO",
    "Latitude",
    "Longitude",
    "Distance",
    "NO. OF VEHICLE",
    "Date",
    "DAY OF THE WEEK",
    "Month of the year",
    "Year of Accident",
    "Time",
    "D/N",
    "PATTERN OF COLLISION",
    "TYPE OF COLLISION",
    "TYPE OF VEHICLE-1",
    "TYPE OF VEHICLE-2",
    "FATAL",
    "GRIEVOUS",
    "MINOR",
    "SEVERITY",
    "GEOMETRY",
    "PRESENCE OF MEDIAN",
    "PRESENCE OF SHOULDER",
    "PRESENCE OF FOOTPATH",
    "SIDE ROAD",
    "JN/NOT",
]

YES_NO_FIELDS = [
    "PRESENCE OF MEDIAN",
    "PRESENCE OF SHOULDER",
    "PRESENCE OF FOOTPATH",
    "SIDE ROAD",
    "JN/NOT",
]

CATEGORY_FIELDS = [
    "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION",
    "DAY OF THE WEEK",
    "D/N",
    "GEOMETRY",
    "PRESENCE OF MEDIAN",
    "PRESENCE OF SHOULDER",
    "PRESENCE OF FOOTPATH",
    "SIDE ROAD",
    "JN/NOT",
    "PATTERN_OF_COLLISION_LABEL",
    "TYPE_OF_COLLISION_LABEL",
    "TYPE_OF_VEHICLE_1_LABEL",
    "TYPE_OF_VEHICLE_2_LABEL",
    "time_bucket",
]
