import pandas as pd
import plotly.express as px
import streamlit as st

from src.cleaning import clean_data
from src.data_io import get_active_dataset, load_excel_cached
from src.viz import plot_monthly, plot_severity, plot_top_hotspots

st.title("Analytics Dashboard")
active = get_active_dataset()
if active is None:
    st.warning("No dataset available. Upload data first.")
    st.stop()

df, _ = clean_data(load_excel_cached(str(active)))

place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
with st.sidebar:
    st.header("Filters")
    place = st.multiselect("Place/Jurisdiction", sorted(df[place_col].astype(str).unique()))
    month = st.multiselect("Month", sorted(df["month_num"].astype(int).unique()))
    dow = st.multiselect("Day of Week", sorted(df["day_of_week"].astype(str).unique()))
    dn = st.multiselect("D/N", sorted(df["D/N"].astype(str).unique()))
    geometry = st.multiselect("Geometry", sorted(df["GEOMETRY"].astype(str).unique()))

f = df.copy()
if place:
    f = f[f[place_col].astype(str).isin(place)]
if month:
    f = f[f["month_num"].astype(int).isin(month)]
if dow:
    f = f[f["day_of_week"].astype(str).isin(dow)]
if dn:
    f = f[f["D/N"].astype(str).isin(dn)]
if geometry:
    f = f[f["GEOMETRY"].astype(str).isin(geometry)]

st.subheader("Accident Map")
map_df = f.dropna(subset=["Latitude", "Longitude"]).copy()
if not map_df.empty:
    fig_map = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        color="severity_target",
        hover_data=["FIR NO", "Date", "severity_target", "PATTERN_OF_COLLISION_LABEL", "TYPE_OF_COLLISION_LABEL"],
        zoom=9,
        height=450,
    )
    fig_map.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(plot_monthly(f), use_container_width=True)
with c2:
    st.plotly_chart(plot_severity(f), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    pattern = f.groupby("PATTERN_OF_COLLISION_LABEL").size().reset_index(name="count").sort_values("count", ascending=False)
    st.plotly_chart(px.bar(pattern, x="PATTERN_OF_COLLISION_LABEL", y="count", title="Pattern of Collision"), use_container_width=True)
with c4:
    ctype = f.groupby("TYPE_OF_COLLISION_LABEL").size().reset_index(name="count").sort_values("count", ascending=False)
    st.plotly_chart(px.bar(ctype, x="TYPE_OF_COLLISION_LABEL", y="count", title="Type of Collision"), use_container_width=True)

veh = f.groupby(["TYPE_OF_VEHICLE_1_LABEL", "TYPE_OF_VEHICLE_2_LABEL"]).size().reset_index(name="count")
st.plotly_chart(
    px.density_heatmap(veh, x="TYPE_OF_VEHICLE_1_LABEL", y="TYPE_OF_VEHICLE_2_LABEL", z="count", title="Vehicle-1 vs Vehicle-2 Matrix"),
    use_container_width=True,
)

jn = f.groupby(["JN/NOT", "severity_target"]).size().reset_index(name="count")
st.plotly_chart(px.bar(jn, x="JN/NOT", y="count", color="severity_target", barmode="group", title="Junction vs Non-Junction"), use_container_width=True)

infra_cols = ["GEOMETRY", "PRESENCE OF MEDIAN", "PRESENCE OF SHOULDER", "PRESENCE OF FOOTPATH"]
for col in infra_cols:
    g = f.groupby([col, "severity_target"]).size().reset_index(name="count")
    st.plotly_chart(px.bar(g, x=col, y="count", color="severity_target", title=f"{col} impact"), use_container_width=True)

st.subheader("Top 10 Hotspots")
st.dataframe(plot_top_hotspots(f), use_container_width=True)
