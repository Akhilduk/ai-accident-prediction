from pathlib import Path

import pandas as pd
import streamlit as st

from src.cleaning import clean_data
from src.config import CLEANED_DATASET, PROCESSED_DIR
from src.data_io import (
    get_active_dataset,
    list_versions,
    load_excel_cached,
    save_uploaded_file,
    set_active_dataset,
    validate_columns,
)
from src.master_reference import MASTER_REF_TABLES

st.title("Data Upload & Manager")

uploaded = st.file_uploader("Upload accident Excel file", type=["xlsx", "xls"])
if uploaded is not None:
    saved = save_uploaded_file(uploaded)
    set_active_dataset(saved)
    st.success(f"Saved dataset version: {saved.name}")

versions = list_versions()
active = get_active_dataset()
if versions:
    selected = st.selectbox("Select active dataset version", versions, index=0, format_func=lambda p: p.name)
    if st.button("Set selected as active"):
        set_active_dataset(selected)
        st.success(f"Active dataset set to: {selected.name}")
        active = selected

if active:
    st.write(f"Current active dataset: `{active}`")
    raw = load_excel_cached(str(active))
    valid, missing = validate_columns(raw)
    if not valid:
        st.error(f"Missing required columns: {missing}")
    else:
        cleaned, info = clean_data(raw)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(CLEANED_DATASET, index=False)
        st.success("Dataset validated and cleaned successfully.")
        st.caption(f"Footer/legend rows removed: {info['removed_footer_rows']}")
        st.dataframe(cleaned.head(20), use_container_width=True)

st.subheader("Master Reference Tables")
for title, mapping in MASTER_REF_TABLES.items():
    with st.expander(title, expanded=False):
        ref_df = pd.DataFrame({"Code": list(mapping.keys()), "Label": list(mapping.values())})
        st.dataframe(ref_df, use_container_width=True)
