from __future__ import annotations

from pathlib import Path
import re
import pandas as pd
import streamlit as st

from src.config import ACTIVE_DATASET_POINTER, DEFAULT_DATASET, REQUIRED_COLUMNS, UPLOADS_DIR
from src.utils import ensure_dirs, timestamped_name


def _read_excel(path: Path) -> pd.DataFrame:
    return pd.read_excel(path)


@st.cache_data(show_spinner=False)
def load_excel_cached(path: str) -> pd.DataFrame:
    return _read_excel(Path(path))




def _header_key(name: str) -> str:
    s = str(name).strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*/\s*", "/", s)
    return s.upper()
def validate_columns(df: pd.DataFrame) -> tuple[bool, list[str]]:
    df_keys = {_header_key(c) for c in df.columns}
    missing = [c for c in REQUIRED_COLUMNS if _header_key(c) not in df_keys]
    return len(missing) == 0, missing


def save_uploaded_file(uploaded_file) -> Path:
    ensure_dirs(UPLOADS_DIR)
    file_name = timestamped_name(uploaded_file.name)
    target = UPLOADS_DIR / file_name
    with open(target, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return target


def set_active_dataset(path: Path) -> None:
    ACTIVE_DATASET_POINTER.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_DATASET_POINTER.write_text(str(path.resolve()))


def get_active_dataset() -> Path | None:
    if ACTIVE_DATASET_POINTER.exists():
        p = Path(ACTIVE_DATASET_POINTER.read_text().strip())
        if p.exists():
            return p
    if DEFAULT_DATASET.exists():
        return DEFAULT_DATASET
    files = sorted(UPLOADS_DIR.glob("*.xlsx"))
    return files[-1] if files else None


def list_versions() -> list[Path]:
    ensure_dirs(UPLOADS_DIR)
    return sorted(UPLOADS_DIR.glob("*.xlsx"), reverse=True)
