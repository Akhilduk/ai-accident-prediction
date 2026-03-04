import plotly.express as px
import pandas as pd
import streamlit as st

from src.cleaning import clean_data
from src.data_io import get_active_dataset, load_excel_cached
from src.ui import apply_theme, style_plotly
from src.viz import plot_monthly, plot_severity, plot_top_hotspots

apply_theme(
    "Analytics Dashboard",
    icon="📊",
    subtitle="Use the sidebar filters to instantly update all dashboard visuals.",
)

active = get_active_dataset()
if active is None:
    st.warning("No dataset available. Upload data first.")
    st.stop()

df, _ = clean_data(load_excel_cached(str(active)))
place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
place_label = "Jurisdiction / Place"

place_options = sorted(df[place_col].astype(str).unique().tolist())
month_options = sorted(df["month_num"].astype(int).unique().tolist())
year_options = sorted(df["year"].astype(int).unique().tolist())
dow_options = sorted(df["day_of_week"].astype(str).unique().tolist())
dn_options = sorted(df["day_night_label"].astype(str).unique().tolist())
geometry_options = sorted(df["GEOMETRY"].astype(str).unique().tolist())
severity_options = sorted(df["severity_target"].astype(str).unique().tolist())
correlation_key_options = [
    "Distance",
    "NO. OF VEHICLE",
    "year",
    "month_num",
    "hour",
    "is_weekend",
    "is_night",
    "day_night_label",
    "GEOMETRY",
    "JN/NOT",
    "PRESENCE OF MEDIAN",
    "PRESENCE OF SHOULDER",
    "PRESENCE OF FOOTPATH",
    "PATTERN_OF_COLLISION_LABEL",
    "TYPE_OF_COLLISION_LABEL",
    "TYPE_OF_VEHICLE_1_LABEL",
    "TYPE_OF_VEHICLE_2_LABEL",
]
friendly_factor_names = {
    "Distance": "Road Segment Distance",
    "NO. OF VEHICLE": "Number of Vehicles Involved",
    "year": "Year",
    "month_num": "Month",
    "hour": "Hour of Day",
    "is_weekend": "Weekend",
    "is_night": "Night Time",
    "day_night_label": "Day/Night",
    "GEOMETRY": "Road Geometry",
    "JN/NOT": "Junction Presence",
    "PRESENCE OF MEDIAN": "Median Present",
    "PRESENCE OF SHOULDER": "Shoulder Present",
    "PRESENCE OF FOOTPATH": "Footpath Present",
    "PATTERN_OF_COLLISION_LABEL": "Collision Pattern",
    "TYPE_OF_COLLISION_LABEL": "Collision Type",
    "TYPE_OF_VEHICLE_1_LABEL": "Primary Vehicle Type",
    "TYPE_OF_VEHICLE_2_LABEL": "Secondary Vehicle Type",
}

for key, default in {
    "dash_place": [],
    "dash_year": [],
    "dash_month": [],
    "dash_dow": [],
    "dash_dn": [],
    "dash_geometry": [],
    "dash_severity": [],
    "dash_corr_keys": ["Distance", "NO. OF VEHICLE", "month_num", "hour", "is_night", "GEOMETRY", "JN/NOT"],
    "dash_corr_method": "pearson",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.header("Dashboard Filters")
    st.caption("Laptop/Desktop: keep sidebar open. Mobile: tap the left arrow to open filters.")
    st.multiselect(place_label, place_options, key="dash_place")
    st.multiselect("Year", year_options, key="dash_year")
    st.multiselect("Month", month_options, key="dash_month")
    st.multiselect("Day of Week", dow_options, key="dash_dow")
    st.multiselect("Day / Night", dn_options, key="dash_dn")
    st.multiselect("Road Geometry", geometry_options, key="dash_geometry")
    st.multiselect("Severity", severity_options, key="dash_severity")
    st.markdown("---")
    st.markdown("**Correlation Settings**")
    st.multiselect("Correlation Keys", correlation_key_options, key="dash_corr_keys")
    st.selectbox(
        "Correlation Method",
        ["pearson", "spearman"],
        key="dash_corr_method",
        format_func=lambda x: x.title(),
    )
    if st.button("Clear all filters", use_container_width=True):
        st.session_state["dash_place"] = []
        st.session_state["dash_year"] = []
        st.session_state["dash_month"] = []
        st.session_state["dash_dow"] = []
        st.session_state["dash_dn"] = []
        st.session_state["dash_geometry"] = []
        st.session_state["dash_severity"] = []
        st.session_state["dash_corr_keys"] = ["Distance", "NO. OF VEHICLE", "month_num", "hour", "is_night", "GEOMETRY", "JN/NOT"]
        st.session_state["dash_corr_method"] = "pearson"
        st.rerun()

f = df.copy()
if st.session_state["dash_place"]:
    f = f[f[place_col].astype(str).isin(st.session_state["dash_place"])]
if st.session_state["dash_year"]:
    f = f[f["year"].astype(int).isin(st.session_state["dash_year"])]
if st.session_state["dash_month"]:
    f = f[f["month_num"].astype(int).isin(st.session_state["dash_month"])]
if st.session_state["dash_dow"]:
    f = f[f["day_of_week"].astype(str).isin(st.session_state["dash_dow"])]
if st.session_state["dash_dn"]:
    f = f[f["day_night_label"].astype(str).isin(st.session_state["dash_dn"])]
if st.session_state["dash_geometry"]:
    f = f[f["GEOMETRY"].astype(str).isin(st.session_state["dash_geometry"])]
if st.session_state["dash_severity"]:
    f = f[f["severity_target"].astype(str).isin(st.session_state["dash_severity"])]

if f.empty:
    st.warning("No rows match the selected filters. Clear one or more filters and try again.")
    st.stop()

active_filters = []
if st.session_state["dash_place"]:
    active_filters.append(f"Place={len(st.session_state['dash_place'])}")
if st.session_state["dash_year"]:
    active_filters.append(f"Year={len(st.session_state['dash_year'])}")
if st.session_state["dash_month"]:
    active_filters.append(f"Month={len(st.session_state['dash_month'])}")
if st.session_state["dash_dow"]:
    active_filters.append(f"Day={len(st.session_state['dash_dow'])}")
if st.session_state["dash_dn"]:
    active_filters.append(f"D/N={len(st.session_state['dash_dn'])}")
if st.session_state["dash_geometry"]:
    active_filters.append(f"Geometry={len(st.session_state['dash_geometry'])}")
if st.session_state["dash_severity"]:
    active_filters.append(f"Severity={len(st.session_state['dash_severity'])}")

st.subheader(f"Filtered Dashboard View ({len(f):,} records)")
st.caption("Active filters: " + (", ".join(active_filters) if active_filters else "None (showing full dataset)"))

k1, k2, k3, k4 = st.columns(4)
k1.metric("Records", f"{len(f):,}")
k2.metric("Fatal", f"{int(f['FATAL'].sum()):,}")
k3.metric("Night Cases", f"{int((f['day_night_label'] == 'Night').sum()):,}")
k4.metric("Unique Places", f"{f[place_col].nunique():,}")

t1, t2, t3, t4 = st.tabs(["Map & Severity Trend", "Collision Insights", "Hotspots", "Correlation Matrix"])

with t1:
    st.markdown("#### Accident Map (Filtered Data)")
    map_df = f.dropna(subset=["Latitude", "Longitude"]).copy()
    if map_df.empty:
        st.info("No geo points available for current filters.")
    else:
        fig_map = px.scatter_mapbox(
            map_df,
            lat="Latitude",
            lon="Longitude",
            color="severity_target",
            hover_data=["FIR NO", "Date", "severity_target", "PATTERN_OF_COLLISION_LABEL", "TYPE_OF_COLLISION_LABEL"],
            zoom=9,
            height=420,
        )
        fig_map.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(style_plotly(fig_map), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        monthly_fig = plot_monthly(f)
        monthly_fig.update_layout(title="Month-wise Severity Trend (Filtered)")
        st.plotly_chart(monthly_fig, use_container_width=True)
    with c2:
        severity_fig = plot_severity(f)
        severity_fig.update_layout(title="Severity Distribution (Filtered)")
        st.plotly_chart(severity_fig, use_container_width=True)

with t2:
    c1, c2 = st.columns(2)
    with c1:
        pattern = (
            f.groupby("PATTERN_OF_COLLISION_LABEL")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(15)
        )
        st.plotly_chart(
            style_plotly(px.bar(pattern, x="PATTERN_OF_COLLISION_LABEL", y="count", title="Top Collision Patterns (Filtered)")),
            use_container_width=True,
        )
    with c2:
        ctype = (
            f.groupby("TYPE_OF_COLLISION_LABEL")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(15)
        )
        st.plotly_chart(
            style_plotly(px.bar(ctype, x="TYPE_OF_COLLISION_LABEL", y="count", title="Top Collision Types (Filtered)")),
            use_container_width=True,
        )

    veh = (
        f.groupby(["TYPE_OF_VEHICLE_1_LABEL", "TYPE_OF_VEHICLE_2_LABEL"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(100)
    )
    st.plotly_chart(
        style_plotly(
            px.density_heatmap(
                veh,
                x="TYPE_OF_VEHICLE_1_LABEL",
                y="TYPE_OF_VEHICLE_2_LABEL",
                z="count",
                title="Vehicle-1 vs Vehicle-2 Matrix (Filtered)",
            )
        ),
        use_container_width=True,
    )

    jn = f.groupby(["JN/NOT", "severity_target"]).size().reset_index(name="count")
    st.plotly_chart(
        style_plotly(px.bar(jn, x="JN/NOT", y="count", color="severity_target", barmode="group", title="Junction vs Non-Junction (Filtered)")),
        use_container_width=True,
    )

with t3:
    st.markdown("#### Top 15 Hotspots (Filtered Data)")
    top_hotspots = plot_top_hotspots(f).head(15)
    st.dataframe(top_hotspots.rename(columns={place_col: place_label}), use_container_width=True, height=420)

with t4:
    st.markdown("#### Correlation Matrix (Filtered Data)")
    selected_keys = [k for k in st.session_state["dash_corr_keys"] if k in f.columns]
    if not selected_keys:
        st.info("Select at least one correlation key from sidebar.")
    else:
        corr_df = f[selected_keys].copy()
        for col in selected_keys:
            if not pd.api.types.is_numeric_dtype(corr_df[col]):
                corr_df[col] = corr_df[col].astype("category").cat.codes

        # Add severity indicators for direct class-wise relationship view.
        corr_df["severity_fatal"] = (f["severity_target"] == "Fatal").astype(int)
        corr_df["severity_grievous"] = (f["severity_target"] == "Grievous").astype(int)
        corr_df["severity_minor"] = (f["severity_target"] == "Minor").astype(int)
        corr_df["severity_high"] = ((f["severity_target"] == "Fatal") | (f["severity_target"] == "Grievous")).astype(int)

        corr_method = st.session_state.get("dash_corr_method", "pearson")
        corr = corr_df.corr(method=corr_method, numeric_only=True).round(3)
        fig_corr = px.imshow(corr, text_auto=True, aspect="auto", title=f"Feature Correlation Matrix ({corr_method.title()})")
        st.plotly_chart(style_plotly(fig_corr), use_container_width=True)

        sev_col = st.selectbox(
            "Find factors affecting",
            ["severity_high", "severity_fatal", "severity_grievous", "severity_minor"],
            format_func=lambda x: {
                "severity_high": "High Severity (Fatal + Grievous)",
                "severity_fatal": "Fatal",
                "severity_grievous": "Grievous",
                "severity_minor": "Minor",
            }[x],
        )
        sev_corr = (
            corr[sev_col]
            .drop(labels=[sev_col], errors="ignore")
            .sort_values(key=lambda s: s.abs(), ascending=False)
            .head(15)
            .reset_index()
            .rename(columns={"index": "key", sev_col: "correlation"})
        )
        sev_corr["impact_direction"] = sev_corr["correlation"].apply(lambda v: "Increases with target" if v > 0 else "Decreases with target")
        sev_corr["abs_correlation"] = sev_corr["correlation"].abs()
        sev_corr["factor"] = sev_corr["key"].map(lambda k: friendly_factor_names.get(k, str(k).replace("_", " ").title()))
        sev_corr["impact_level"] = sev_corr["abs_correlation"].apply(
            lambda v: "High" if v >= 0.35 else ("Medium" if v >= 0.20 else "Low")
        )

        st.plotly_chart(
            style_plotly(
                px.bar(
                    sev_corr,
                    x="key",
                    y="correlation",
                    title=f"Top {corr_method.title()} correlations with {sev_col.replace('severity_', '').title()}",
                )
            ),
            use_container_width=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Top Risk-Increasing Factors**")
            pos = sev_corr.sort_values("correlation", ascending=False).head(8)
            st.dataframe(pos[["factor", "correlation"]], use_container_width=True, hide_index=True)
        with c2:
            st.markdown("**Top Risk-Reducing Factors**")
            neg = sev_corr.sort_values("correlation", ascending=True).head(8)
            st.dataframe(neg[["factor", "correlation"]], use_container_width=True, hide_index=True)

        st.markdown("**Simple Explanation (For General Users)**")
        top3 = sev_corr.sort_values("abs_correlation", ascending=False).head(3).copy()
        if top3.empty:
            st.info("Not enough variation to explain factors for selected filters.")
        else:
            for _, row in top3.iterrows():
                direction = "higher chance" if row["correlation"] > 0 else "lower chance"
                st.write(f"- **{row['factor']}** is linked with **{direction}** of selected severity (**{row['impact_level']} impact**).")
        level_counts = sev_corr["impact_level"].value_counts()
        st.write(
            f"Impact summary: High = {int(level_counts.get('High', 0))}, "
            f"Medium = {int(level_counts.get('Medium', 0))}, "
            f"Low = {int(level_counts.get('Low', 0))}"
        )
        st.caption(
            "This shows association, not strict cause-and-effect. Use it as planning guidance with field verification."
        )
        st.dataframe(
            sev_corr[["factor", "impact_level", "correlation", "abs_correlation", "impact_direction"]],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")
    st.markdown("#### Why Is Severity High? (Simple Explanation)")
    target_mode = st.selectbox(
        "Analyze causes for",
        ["High Severity (Fatal + Grievous)", "Fatal", "Grievous", "Minor"],
    )
    min_samples = st.slider("Ignore tiny groups (minimum records)", min_value=5, max_value=100, value=20, step=5)

    factor_columns = [
        "day_night_label",
        "time_bucket",
        "day_of_week",
        "GEOMETRY",
        "JN/NOT",
        "PRESENCE OF MEDIAN",
        "PRESENCE OF SHOULDER",
        "PRESENCE OF FOOTPATH",
        "PATTERN_OF_COLLISION_LABEL",
        "TYPE_OF_COLLISION_LABEL",
        "TYPE_OF_VEHICLE_1_LABEL",
        "TYPE_OF_VEHICLE_2_LABEL",
    ]
    selected_factor_columns = st.multiselect(
        "Factors to analyze",
        factor_columns,
        default=["day_night_label", "GEOMETRY", "JN/NOT", "time_bucket", "TYPE_OF_COLLISION_LABEL"],
    )

    if target_mode == "High Severity (Fatal + Grievous)":
        target_flag = f["severity_target"].isin(["Fatal", "Grievous"])
        target_name = "High Severity"
    else:
        target_flag = f["severity_target"].eq(target_mode)
        target_name = target_mode

    if not selected_factor_columns:
        st.info("Select at least one factor to run visual cause analysis.")
    else:
        all_driver_rows = []
        for col in selected_factor_columns:
            g = (
                f.assign(_target=target_flag.astype(int))
                .groupby(col, dropna=False)
                .agg(total_records=("_target", "size"), target_cases=("_target", "sum"))
                .reset_index()
            )
            g = g[g["total_records"] >= min_samples].copy()
            if g.empty:
                continue
            g["target_rate"] = (g["target_cases"] / g["total_records"]).round(4)
            g["risk_score"] = g["target_rate"] * (g["total_records"] ** 0.5)
            g["factor"] = col
            g = g.sort_values("target_rate", ascending=False)
            g = g.rename(columns={col: "factor_value"})
            all_driver_rows.append(g)

            fig = px.bar(
                g.head(12),
                x="factor_value",
                y="target_rate",
                color="target_rate",
                title=f"{friendly_factor_names.get(col, col)} and {target_name}",
                hover_data=["total_records", "target_cases", "risk_score"],
            )
            fig.update_yaxes(title=f"Chance of {target_name}")
            st.plotly_chart(style_plotly(fig), use_container_width=True)

        if not all_driver_rows:
            st.warning("No factor groups matched the current minimum sample threshold. Reduce threshold or adjust filters.")
        else:
            drivers = pd.concat(all_driver_rows, ignore_index=True)
            top_drivers = drivers.sort_values(["risk_score", "target_rate"], ascending=False).head(12).copy()
            top_drivers["factor"] = top_drivers["factor"].map(lambda x: friendly_factor_names.get(x, x))
            top_drivers["severity_target"] = target_name
            st.markdown("**Main Reasons (Easy to Understand)**")
            top3_simple = top_drivers.head(3).copy()
            for _, row in top3_simple.iterrows():
                factor_name = str(row["factor"])
                factor_value = str(row["factor_value"])
                chance = float(row["target_rate"]) * 100
                st.write(f"- In **{factor_name} = {factor_value}**, the chance of **{target_name}** is about **{chance:.1f}%**.")
            st.caption("These are data-based associations. Use them as guidance with field inspection.")
            st.dataframe(
                top_drivers[
                    ["severity_target", "factor", "factor_value", "target_rate", "total_records", "target_cases", "risk_score"]
                ],
                use_container_width=True,
                hide_index=True,
            )
            with st.expander("Show detailed technical table"):
                st.dataframe(
                    top_drivers[
                        ["severity_target", "factor", "factor_value", "target_rate", "total_records", "target_cases", "risk_score"]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
