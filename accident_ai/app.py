import streamlit as st

st.set_page_config(page_title="NATRAC Accident Analytics & AI Prediction", layout="wide", page_icon="🚦")

st.title("NATRAC Accident Analytics & AI Prediction")
st.markdown(
    "Use the left sidebar to navigate pages: **Home**, **Data Manager**, **Dashboard**, **Model Training**, and **Prediction**."
)
st.info("Tip: upload/select dataset in Data Manager first, then explore analytics and train models.")
