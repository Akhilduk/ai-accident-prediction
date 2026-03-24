import plotly.express as px
import pandas as pd
import streamlit as st

from src.cleaning import clean_data
from src.data_io import get_active_dataset, load_excel_cached
from src.ui import apply_theme, style_plotly
from src.viz import plot_monthly, plot_severity, plot_top_hotspots

apply_theme(
    "Analytics Dashboard",
    icon="DASHBOARD",
    subtitle="Use the sidebar filters to update charts instantly.",
)

active = get_active_dataset()
if active is None:
    st.warning("No dataset available. Upload data first.")
    st.stop()

df, _ = clean_data(load_excel_cached(str(active)))
place_col = "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION"
place_label = "Jurisdiction / Place"


def _friendly_value_text(value):
    text = str(value).strip()
    mapping = {
        "yes": "junction areas",
        "no": "non-junction areas",
        "day": "daylight hours",
        "night": "night hours",
        "straight": "straight roads",
    }
    lowered = text.lower()
    if lowered in mapping:
        return mapping[lowered]
    return text.replace("_", " ")


def _build_factor_sentence(factor_name: str, factor_value: str, target_name: str, chance: float) -> str:
    readable_value = _friendly_value_text(factor_value)
    factor_name_lower = factor_name.lower()

    if factor_name_lower == "road geometry":
        return f"On **{readable_value}**, the probability of **{target_name.lower()}** is about **{chance:.1f}%**."
    if factor_name_lower == "day / night":
        return f"During **{readable_value}**, the probability of **{target_name.lower()}** is about **{chance:.1f}%**."
    if factor_name_lower == "junction":
        return f"In **{readable_value}**, the probability of **{target_name.lower()}** is about **{chance:.1f}%**."
    return (
        f"For **{factor_name} = {readable_value}**, the probability of **{target_name.lower()}** "
        f"is about **{chance:.1f}%**."
    )


def _build_factor_finding(factor_name: str, factor_value: str, target_name: str, chance: float) -> str:
    readable_value = _friendly_value_text(factor_value)
    target_label = target_name.lower()
    if chance >= 75:
        level = "very strong"
    elif chance >= 60:
        level = "strong"
    elif chance >= 45:
        level = "moderate"
    else:
        level = "limited"

    return (
        f"This suggests **{readable_value}** is a **{level} warning sign** for **{target_label}** in the current filtered data. "
        f"It does not prove the factor directly causes the crash outcome, but it is one of the patterns most often seen with severe cases."
    )

with st.expander("How to Use This Dashboard (Simple)", expanded=False):
    st.markdown(
        """
- Use sidebar filters to focus on **place, year, month, day/night, and severity**.
- All charts update automatically from your selected filters.
- **Map & Severity Trend**: Where accidents happen and how severity changes over time.
- **Collision Insights**: Common collision and vehicle patterns.
- **Hotspots**: Places with highest accident counts in filtered data.
- **What Increases Severity?**: Easy explanation of factors linked with serious outcomes.

**Simple meaning of relationship methods**
- **Pearson**: Best for straight-line relationships.
- **Spearman**: Best for rank/order relationships.
"""
    )



with st.expander("How to read X-axis, Y-axis, matrix, and severity logic", expanded=False):
    st.markdown(
        """
### 1) How to read every chart on this page
- **Map (scatter map)**
  - Latitude + Longitude place the point on map.
  - Color shows severity category.
  - Hover card shows FIR number, date, severity, and collision details.
- **Month-wise Severity Trend (line/stacked chart)**
  - **X-axis** = month number (`1` to `12`).
  - **Y-axis** = number of accident records in that month.
  - If one month bar/line is higher, that month had more accidents in selected filters.
- **Severity Distribution chart**
  - **X-axis** = severity class (Fatal / Serious Injury / Minor).
  - **Y-axis** = count of accidents in each class.
- **Collision Pattern / Collision Type bars**
  - **X-axis** = pattern/type names.
  - **Y-axis** = accident count.
- **Vehicle-1 vs Vehicle-2 heatmap**
  - **X-axis** = first vehicle type, **Y-axis** = second vehicle type.
  - Cell color intensity = how often this pair appears.
- **Junction vs Non-Junction grouped bar**
  - **X-axis** = `JN/NOT` value.
  - **Y-axis** = count.
  - Color split = severity class.
- **Top hotspot table**
  - Sorted from highest accidents to lowest for current filters.
  - First row is the highest-risk hotspot in this filtered view.

### 2) Correlation matrix: exact method used
1. You select X-axis factors and Y-axis factors from sidebar.
2. Only these approved columns are available in selector/filter.
3. If a selected factor is text (like `GEOMETRY`), app converts it into internal category codes.
4. Correlation is computed only for selected X and Y groups:
   - **Pearson**: straight-line relationship.
   - **Spearman**: rank/order relationship.
5. Matrix cell value is from **-1 to +1**.

### 3) How to interpret correlation value with numerical examples
- `+0.62` => medium/strong positive relation (as factor grows, selected severity flag tends to increase).
- `-0.41` => medium negative relation (as factor grows, selected severity flag tends to decrease).
- `+0.03` => very weak relation (almost no pattern).
- **Important:** correlation is **association**, not proof of cause.

### 4) How top factors are picked for selected Y target
- App takes selected Y-axis target column (example: `SEVERITY SCORE`).
- Sorts selected X-axis factors by absolute correlation `abs(correlation)` in descending order.
- Impact level used in this page:
  - **High** if `abs(correlation) >= 0.35`
  - **Medium** if `abs(correlation) >= 0.20`
  - **Low** otherwise
- Direction:
  - Positive => "Increases with target"
  - Negative => "Decreases with target"

### 5) "Why is severity high" section: formula used
For each factor value/group:
- **total_records** = number of records in that group
- **target_cases** = number of selected severity cases in that group
- **target_rate** = `target_cases / total_records`
- **risk_score** = `target_rate * sqrt(total_records)`

Example:
- Group A: 25 severe out of 100 => `target_rate = 0.25`; `risk_score = 0.25 * 10 = 2.5`
- Group B: 8 severe out of 16 => `target_rate = 0.50`; `risk_score = 0.50 * 4 = 2.0`
Even though Group B has higher rate, Group A can rank higher because it has stronger sample support.
"""
    )

place_options = sorted(df[place_col].astype(str).unique().tolist())
month_options = sorted(df["month_num"].astype(int).unique().tolist())
year_options = sorted(df["year"].astype(int).unique().tolist())
dow_options = sorted(df["day_of_week"].astype(str).unique().tolist())
dn_options = sorted(df["day_night_label"].astype(str).unique().tolist())
geometry_options = sorted(df["GEOMETRY"].astype(str).unique().tolist())
severity_options = sorted(df["severity_target"].astype(str).unique().tolist())
correlation_axis_options = [
    "Distance",
    "Latitude",
    "Longitude",
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
    "GEOMETRY",
    "PRESENCE OF MEDIAN",
    "PRESENCE OF SHOULDER",
    "PRESENCE OF FOOTPATH",
    "SIDE ROAD",
    "JN/NOT",
    "SEVERITY SCORE",
]
default_correlation_axes = [c for c in correlation_axis_options if c != "SEVERITY SCORE"]
friendly_factor_names = {
    "NO OF ACCIDENT REPORTED ON THIS CORRIDOR UNDER JURISDICTION": "Jurisdiction / Corridor",
    "FIR NO": "FIR Number",
    "Distance": "Distance",
    "Latitude": "Latitude",
    "Longitude": "Longitude",
    "NO. OF VEHICLE": "Number of Vehicles",
    "Date": "Date",
    "DAY OF THE WEEK": "Day of Week",
    "Month of the year": "Month of Year",
    "Year of Accident": "Year of Accident",
    "Time": "Time",
    "D/N": "Day/Night",
    "PATTERN OF COLLISION": "Pattern of Collision",
    "TYPE OF COLLISION": "Type of Collision",
    "TYPE OF VEHICLE-1": "Type of Vehicle-1",
    "TYPE OF VEHICLE-2": "Type of Vehicle-2",
    "GEOMETRY": "Geometry",
    "PRESENCE OF MEDIAN": "Presence of Median",
    "PRESENCE OF SHOULDER": "Presence of Shoulder",
    "PRESENCE OF FOOTPATH": "Presence of Footpath",
    "SIDE ROAD": "Side Road",
    "JN/NOT": "Junction / Not",
    "SEVERITY SCORE": "Severity Score",
}
severity_label_map = {
    "Fatal": "Fatal",
    "Grievous": "Serious Injury",
    "Minor": "Minor Injury",
}

for key, default in {
    "dash_place": [],
    "dash_year": [],
    "dash_month": [],
    "dash_dow": [],
    "dash_dn": [],
    "dash_geometry": [],
    "dash_severity": [],
    "dash_corr_x": default_correlation_axes.copy(),
    "dash_corr_y": default_correlation_axes.copy(),
    "dash_corr_method": "pearson",
    "dash_corr_color_style": "Soft",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Keep axis selections valid even when options are changed across releases.
st.session_state["dash_corr_x"] = [c for c in st.session_state.get("dash_corr_x", []) if c in correlation_axis_options]
st.session_state["dash_corr_y"] = [c for c in st.session_state.get("dash_corr_y", []) if c in correlation_axis_options]
if not st.session_state["dash_corr_x"]:
    st.session_state["dash_corr_x"] = default_correlation_axes.copy()
if not st.session_state["dash_corr_y"]:
    st.session_state["dash_corr_y"] = default_correlation_axes.copy()

with st.sidebar:
    st.header("Dashboard Filters")
    st.caption("Laptop/Desktop: keep sidebar open. Mobile: tap the left arrow to open filters.")
    st.multiselect(place_label, place_options, key="dash_place")
    st.multiselect("Year", year_options, key="dash_year")
    st.multiselect("Month", month_options, key="dash_month")
    st.multiselect("Day of Week", dow_options, key="dash_dow")
    st.multiselect("Day / Night", dn_options, key="dash_dn")
    st.multiselect("Road Geometry", geometry_options, key="dash_geometry")
    st.multiselect(
        "Severity Level",
        severity_options,
        key="dash_severity",
        format_func=lambda x: severity_label_map.get(str(x), str(x)),
    )
    st.markdown("---")
    st.markdown("**Relationship Settings**")
    st.multiselect("X-axis factors", correlation_axis_options, key="dash_corr_x")
    st.multiselect("Y-axis factors", correlation_axis_options, key="dash_corr_y")
    st.selectbox(
        "Relationship Method",
        ["pearson", "spearman"],
        key="dash_corr_method",
        format_func=lambda x: x.title(),
    )
    st.selectbox(
        "Matrix Color Style",
        ["Soft", "Diverging"],
        key="dash_corr_color_style",
        help="Soft = calmer single-tone colors for easy reading. Diverging = stronger positive/negative contrast.",
    )
    if st.button("Clear all filters", use_container_width=True):
        st.session_state["dash_place"] = []
        st.session_state["dash_year"] = []
        st.session_state["dash_month"] = []
        st.session_state["dash_dow"] = []
        st.session_state["dash_dn"] = []
        st.session_state["dash_geometry"] = []
        st.session_state["dash_severity"] = []
        st.session_state["dash_corr_x"] = default_correlation_axes.copy()
        st.session_state["dash_corr_y"] = default_correlation_axes.copy()
        st.session_state["dash_corr_method"] = "pearson"
        st.session_state["dash_corr_color_style"] = "Soft"
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

t1, t2, t3, t4 = st.tabs(["Map & Severity Trend", "Collision Insights", "Hotspots", "What Increases Severity?"])

with t1:
    st.markdown("#### Accident Map (Filtered Data)")
    st.caption("Map points are accident locations (Latitude/Longitude). Color shows severity level. Use hover to see FIR, date, and collision details.")
    map_df = f.dropna(subset=["Latitude", "Longitude"]).copy()
    if map_df.empty:
        st.info("No geo points available for current filters.")
    else:
        map_df["severity_label"] = map_df["severity_target"].map(lambda x: severity_label_map.get(str(x), str(x)))
        fig_map = px.scatter_mapbox(
            map_df,
            lat="Latitude",
            lon="Longitude",
            color="severity_label",
            hover_data=["FIR NO", "Date", "severity_label", "PATTERN_OF_COLLISION_LABEL", "TYPE_OF_COLLISION_LABEL"],
            zoom=9,
            height=420,
        )
        fig_map.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(style_plotly(fig_map), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        monthly_fig = plot_monthly(f)
        monthly_fig.update_layout(title="Month-wise Severity Trend (Filtered)")
        st.caption("X-axis: month timeline. Y-axis: number of accidents. Each color line is a severity class. Higher line means more cases in that period.")
        st.plotly_chart(monthly_fig, use_container_width=True)
    with c2:
        severity_fig = plot_severity(f)
        severity_fig.update_layout(title="Severity Distribution (Filtered)")
        st.caption("Pie chart share of each severity class. Percent is calculated as class_count / total_filtered_records * 100.")
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
        st.caption("Top collision patterns by count. X-axis: pattern type. Y-axis: number of accidents for each pattern.")
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
        st.caption("Top collision types by count. X-axis: collision type. Y-axis: number of accidents.")
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
    st.caption("Vehicle pair matrix. X-axis: primary vehicle, Y-axis: secondary vehicle. Darker cell means this pair appears more often.")
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
    jn["severity_label"] = jn["severity_target"].map(lambda x: severity_label_map.get(str(x), str(x)))
    st.caption("Junction analysis. X-axis: junction/non-junction. Y-axis: accident count. Colors split the count by severity level.")
    st.plotly_chart(
        style_plotly(px.bar(jn, x="JN/NOT", y="count", color="severity_label", barmode="group", title="Junction vs Non-Junction (Filtered)")),
        use_container_width=True,
    )

with t3:
    st.markdown("#### Top 15 Hotspots (Filtered Data)")
    top_hotspots = plot_top_hotspots(f).head(15)
    st.caption(
        "For each row, severity_score is calculated as (10×FATAL) + (5×GRIEVOUS) + (2×MINOR). "
        "Then average_score(row) = severity_score(row) / total accidents in that corridor (within current filters). "
        "Hotspots are ranked by summed average_score (equivalent to corridor severity_score / corridor total), then by severity_score and total accidents. "
        "'fatal_rate' is fatal / total."
    )
    st.dataframe(top_hotspots.rename(columns={place_col: place_label}), use_container_width=True, height=420)

with t4:
    st.markdown("#### Factor Relationship Matrix (Filtered Data)")
    selected_x = [k for k in st.session_state["dash_corr_x"] if k in f.columns]
    selected_y = [k for k in st.session_state["dash_corr_y"] if k in f.columns]
    if not selected_x or not selected_y:
        st.info("Select at least one X-axis factor and one Y-axis factor from sidebar.")
    else:
        corr_cols = list(dict.fromkeys(selected_x + selected_y))
        corr_df = f[corr_cols].copy()
        for col in corr_cols:
            if not pd.api.types.is_numeric_dtype(corr_df[col]):
                corr_df[col] = corr_df[col].astype("category").cat.codes

        corr_method = st.session_state.get("dash_corr_method", "pearson")
        corr_all = corr_df.corr(method=corr_method, numeric_only=True).round(3)
        corr_view = corr_all.loc[selected_y, selected_x]
        corr_display = corr_view.rename(index=friendly_factor_names, columns=friendly_factor_names)
        matrix_height = max(420, min(1200, 140 + (36 * len(selected_y))))
        color_style = st.session_state.get("dash_corr_color_style", "Soft")
        color_scale = "Blues" if color_style == "Soft" else "RdBu_r"

        st.caption("Matrix values range from -1 to +1. A value near +1 means both items are often seen together in the selected records. A value near -1 means when one is seen more, the other is usually seen less. A value near 0 means there is little clear pattern between them. This shows a pattern in the data, not the reason crashes happen.")
        fig_corr = px.imshow(
            corr_display,
            text_auto=".2f",
            aspect="auto",
            title=f"X vs Y Relationship Matrix ({corr_method.title()})",
            color_continuous_scale=color_scale,
            zmin=-1,
            zmax=1,
        )
        fig_corr.update_layout(height=matrix_height)
        fig_corr.update_xaxes(side="top", tickangle=-35, automargin=True)
        fig_corr.update_yaxes(automargin=True)
        st.plotly_chart(style_plotly(fig_corr), use_container_width=True)
        st.caption("Cell values are shown inside each box; hover and table view are also available for easier reading.")
        with st.expander("Show correlation matrix table", expanded=False):
            st.dataframe(corr_display.round(3), use_container_width=True)

        target_col = st.selectbox(
            "Find X-axis factors affecting (Y target)",
            selected_y,
            format_func=lambda x: friendly_factor_names.get(x, x),
        )
        sev_corr = (
            corr_all[target_col]
            .loc[selected_x]
            .drop(labels=[target_col], errors="ignore")
            .sort_values(key=lambda s: s.abs(), ascending=False)
            .head(15)
            .reset_index()
            .rename(columns={"index": "key", target_col: "correlation"})
        )
        sev_corr["impact_direction"] = sev_corr["correlation"].apply(lambda v: "Increases with target" if v > 0 else "Decreases with target")
        sev_corr["abs_correlation"] = sev_corr["correlation"].abs()
        sev_corr["factor"] = sev_corr["key"].map(lambda k: friendly_factor_names.get(k, str(k).replace("_", " ").title()))
        sev_corr["impact_level"] = sev_corr["abs_correlation"].apply(
            lambda v: "High" if v >= 0.35 else ("Medium" if v >= 0.20 else "Low")
        )

        st.caption("This bar chart ranks selected X-axis factors by relationship strength with selected Y-axis target.")
        st.plotly_chart(
            style_plotly(
                px.bar(
                    sev_corr,
                    x="key",
                    y="correlation",
                    title=f"Top {corr_method.title()} relationships with {friendly_factor_names.get(target_col, target_col)}",
                )
            ),
            use_container_width=True,
        )
        st.dataframe(
            sev_corr[["factor", "impact_level", "correlation", "abs_correlation", "impact_direction"]],
            use_container_width=True,
            hide_index=True,
        )
        if not sev_corr.empty:
            st.markdown("**Correlation Findings in Simple Words**")
            top_corr = sev_corr.head(3).copy()
            target_name = friendly_factor_names.get(target_col, target_col)
            for _, row in top_corr.iterrows():
                strength_text = str(row["impact_level"]).lower()
                if row["correlation"] > 0:
                    pattern_text = (
                        f"In the selected records, **{row['factor']}** and **{target_name}** are often seen together. "
                        f"When this factor appears more often, **{target_name}** also tends to appear more often."
                    )
                else:
                    pattern_text = (
                        f"In the selected records, **{row['factor']}** and **{target_name}** usually move in different directions. "
                        f"When this factor appears more often, **{target_name}** tends to appear less often."
                    )

                if row["impact_level"] == "High":
                    strength_sentence = "This is one of the clearer patterns in the filtered data."
                elif row["impact_level"] == "Medium":
                    strength_sentence = "This pattern is noticeable, but it is not one of the strongest ones."
                else:
                    strength_sentence = "This pattern is weak, so it should be treated as a small hint rather than a strong conclusion."

                st.write(
                    f"- **{row['factor']}** has a **{strength_text} relationship** with **{target_name}** "
                    f"(correlation: **{row['correlation']:.3f}**). {pattern_text} {strength_sentence}"
                )
            st.caption(
                "Read this section like a plain-language summary of the chart: it tells you which items are commonly seen together in the filtered data. A bigger number means a clearer pattern, but it still does not prove why the crash outcome happened."
            )
            with st.expander("Report-ready interpretation help", expanded=False):
                st.markdown(
                    """
**How to write the result in a report**
- Start with the factor name.
- Mention whether the relationship is low, medium, or high.
- Explain the practical meaning in one simple sentence.
- End with one action point.

**Example format**
- "Road geometry shows a meaningful relationship with severity. This suggests severe crashes are more common in some road shapes than others in the selected data. These locations should be checked for speed control, visibility, and lane discipline."

**Important note**
- Correlation shows which factors move with severity.
- The severity analysis below shows where the severe outcome percentage is actually highest.
- Use both together for stronger interpretation.
"""
                )

    st.markdown("---")
    st.markdown("#### Why Is Severity High? (Simple Explanation)")
    target_mode = st.selectbox(
        "Analyze causes for",
        ["High Severity (Fatal + Serious Injury)", "Fatal", "Serious Injury", "Minor Injury"],
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

    if target_mode == "High Severity (Fatal + Serious Injury)":
        target_flag = f["severity_target"].isin(["Fatal", "Grievous"])
        target_name = "High Severity"
    elif target_mode == "Serious Injury":
        target_flag = f["severity_target"].eq("Grievous")
        target_name = target_mode
    elif target_mode == "Minor Injury":
        target_flag = f["severity_target"].eq("Minor")
        target_name = target_mode
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
                .groupby(col, dropna=False, observed=False)
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
            st.caption("Y-axis is target_rate = target_cases / total_records for that factor value. Color shade also follows this rate.")
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
                st.write(f"- {_build_factor_sentence(factor_name, factor_value, target_name, chance)}")
                st.caption(_build_factor_finding(factor_name, factor_value, target_name, chance))
            most_affected_factors = top_drivers["factor"].dropna().astype(str).drop_duplicates().head(5).tolist()
            if most_affected_factors:
                st.markdown("**Overall Finding**")
                st.write(
                    f"The factors that appear to affect **{target_name.lower()}** the most in the current filtered data are: "
                    f"**{', '.join(most_affected_factors)}**."
                )
                st.write(
                    "In simple terms, these are the conditions where severe outcomes are seen more often than in other groups. "
                    "This helps identify where road-safety action, inspection, or awareness should be focused first."
                )
                st.markdown("**Suggested Safety Action**")
                st.write(
                    "Focus first on the factor groups with the highest target rate and risk score. These are the groups where severe cases are both frequent and supported by enough records to deserve practical attention."
                )
            st.caption("These are data-based associations. Use them as guidance with field inspection.")
            st.caption("Columns: target_rate = target_cases / total_records. risk_score = target_rate * sqrt(total_records) to balance rate and sample size.")
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
