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
from src.master_reference import DEFAULT_MASTER_REF_TABLES, load_master_reference, save_master_reference
from src.ui import apply_theme

apply_theme(
    "Data Upload & Manager",
    icon="🗂️",
    subtitle="Upload versions, set active dataset, and maintain master reference codes.",
)

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

st.subheader("Master Reference Tables (Editable)")
st.caption("You can add/edit/delete codes and labels below. Changes are saved locally and used in decoding.")

refs = load_master_reference()
edited_refs = {}
for title in ["Pattern of Collision", "Type of Collision", "Type of Vehicle"]:
    with st.expander(title, expanded=False):
        base_df = pd.DataFrame({"Code": list(refs[title].keys()), "Label": list(refs[title].values())})
        if base_df.empty:
            base_df = pd.DataFrame({"Code": [None], "Label": [""]})
        edited = st.data_editor(
            base_df,
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{title}",
            column_config={
                "Code": st.column_config.NumberColumn("Code", step=1, format="%d"),
                "Label": st.column_config.TextColumn("Label"),
            },
        )
        cleaned_editor = edited.dropna(subset=["Code", "Label"]).copy()
        cleaned_editor["Code"] = cleaned_editor["Code"].astype(int)
        cleaned_editor["Label"] = cleaned_editor["Label"].astype(str).str.strip()
        cleaned_editor = cleaned_editor[cleaned_editor["Label"] != ""]
        edited_refs[title] = dict(zip(cleaned_editor["Code"], cleaned_editor["Label"]))

c1, c2 = st.columns(2)
with c1:
    if st.button("Save Master Reference Changes", type="primary"):
        save_master_reference(edited_refs)
        st.success("Master reference updated successfully.")
with c2:
    if st.button("Reset Master Reference to Default"):
        save_master_reference(DEFAULT_MASTER_REF_TABLES)
        st.success("Master reference reset to default values.")
