from __future__ import annotations

import streamlit as st


def apply_theme(page_title: str, icon: str = "AI", subtitle: str | None = None) -> None:
    if "ui_theme_mode" not in st.session_state:
        st.session_state["ui_theme_mode"] = "Auto"
    with st.sidebar:
        with st.expander("Appearance", expanded=False):
            st.selectbox("Theme Mode", ["Auto", "Light", "Dark"], key="ui_theme_mode")

    theme_base = st.get_option("theme.base") or "light"
    mode = st.session_state["ui_theme_mode"]
    if mode == "Dark":
        is_dark = True
    elif mode == "Light":
        is_dark = False
    else:
        is_dark = theme_base == "dark"
    bg_color = st.get_option("theme.backgroundColor") or ("#0f1724" if is_dark else "#ffffff")
    text_color = st.get_option("theme.textColor") or "#1f2937"
    secondary_bg = st.get_option("theme.secondaryBackgroundColor") or "#f3f6fa"
    primary_color = st.get_option("theme.primaryColor") or "#0d66c2"

    if is_dark:
        app_bg = (
            "radial-gradient(circle at 14% 8%, rgba(48, 112, 182, 0.22), transparent 36%),"
            "radial-gradient(circle at 86% 0%, rgba(52, 148, 132, 0.18), transparent 34%),"
            f"linear-gradient(180deg, {bg_color} 0%, #101927 52%, #0f1624 100%)"
        )
        panel_bg = "rgba(22, 30, 43, 0.92)"
        panel_border = "rgba(117, 161, 207, 0.30)"
        tab_bg = "rgba(117, 161, 207, 0.24)"
        text_muted = "rgba(223, 235, 248, 0.90)"
        button_bg = "linear-gradient(120deg, #1a2636, #1e3553)"
        button_text = "#e6f1ff"
    else:
        app_bg = (
            "radial-gradient(circle at 14% 8%, rgba(66, 155, 245, 0.16), transparent 36%),"
            "radial-gradient(circle at 86% 0%, rgba(255, 138, 61, 0.14), transparent 34%),"
            f"linear-gradient(180deg, {bg_color} 0%, {secondary_bg} 52%, #f8fafc 100%)"
        )
        panel_bg = "rgba(255, 255, 255, 0.90)"
        panel_border = "rgba(28, 102, 176, 0.18)"
        tab_bg = "rgba(13, 102, 194, 0.10)"
        text_muted = "rgba(21, 44, 72, 0.84)"
        button_bg = "linear-gradient(120deg, #ffffff, #edf5ff)"
        button_text = "#173458"

    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
    :root {
        --brand-1: __PRIMARY__;
        --brand-2: #13a088;
        --panel-bg: __PANEL_BG__;
        --panel-border: __PANEL_BORDER__;
        --tab-bg: __TAB_BG__;
        --app-bg: __APP_BG__;
        --text-main: __TEXT_MAIN__;
        --text-muted: __TEXT_MUTED__;
        --button-bg: __BUTTON_BG__;
        --button-text: __BUTTON_TEXT__;
    }

    .stApp, [data-testid="stAppViewContainer"] {
        background: var(--app-bg) !important;
        color: var(--text-main) !important;
    }
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background: transparent !important;
        color: var(--text-main) !important;
    }
    [data-testid="stHeader"], header {
        background: transparent !important;
    }
    .block-container {
        padding-top: 4.2rem !important;
        padding-bottom: 1.6rem;
        max-width: 1200px;
    }
    .stMarkdown, .stMarkdown p, .stCaption, h1, h2, h3, h4, h5, h6, label {
        color: var(--text-main) !important;
    }
    .stCaption { color: var(--text-muted) !important; }

    .hero {
        background: linear-gradient(120deg, var(--brand-1), var(--brand-2));
        color: white !important;
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        border: 1px solid rgba(255,255,255,0.20);
        box-shadow: 0 12px 34px rgba(17, 53, 87, 0.22);
        animation: rise 0.45s ease-out;
        margin-bottom: 0.9rem;
    }
    .hero h1, .hero p { color: white !important; margin: 0; }
    .hero h1 { margin-bottom: 0.26rem; font-size: clamp(1.25rem, 2vw, 2rem); line-height: 1.2; }
    .hero p { opacity: 0.95; font-weight: 600; }

    .glass-card {
        background: var(--panel-bg);
        border: 1px solid var(--panel-border);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        backdrop-filter: blur(8px);
        animation: rise 0.45s ease-out;
        color: var(--text-main) !important;
    }
    .glass-card * { color: var(--text-main) !important; }

    .stMetric, [data-testid="stMetric"], [data-testid="metric-container"] {
        background: var(--panel-bg) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 14px;
        padding: 0.45rem 0.5rem;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: var(--text-main) !important;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 0.36rem; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        background: var(--tab-bg) !important;
        border: 1px solid var(--panel-border) !important;
        height: 2.2rem;
        padding: 0.35rem 0.95rem;
        font-weight: 700;
        color: var(--text-main) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(120deg, var(--brand-1), var(--brand-2));
        color: white !important;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 12px !important;
        border: 1px solid rgba(13, 102, 194, 0.35) !important;
        background: var(--button-bg) !important;
        color: var(--button-text) !important;
        font-weight: 700 !important;
        min-height: 2.55rem !important;
        padding: 0.4rem 0.9rem !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: rgba(19, 160, 136, 0.55) !important;
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"], .stForm [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(120deg, var(--brand-1), var(--brand-2)) !important;
        color: white !important;
        border: none !important;
    }

    .stSelectbox > div, .stMultiSelect > div, .stDateInput > div,
    [data-baseweb="select"] > div {
        color: var(--text-main) !important;
    }
    .stSelectbox, .stMultiSelect, .stDateInput { margin-bottom: 0.38rem; }

    html[data-theme="dark"] .glass-card,
    body[data-theme="dark"] .glass-card,
    html[data-theme="dark"] .stMetric,
    body[data-theme="dark"] .stMetric,
    html[data-theme="dark"] [data-testid="metric-container"],
    body[data-theme="dark"] [data-testid="metric-container"] {
        background: rgba(22, 30, 43, 0.92) !important;
        border-color: rgba(117, 161, 207, 0.30) !important;
        color: #e8eef7 !important;
    }
    html[data-theme="dark"] .stMarkdown,
    body[data-theme="dark"] .stMarkdown,
    html[data-theme="dark"] [data-testid="stMetricValue"],
    body[data-theme="dark"] [data-testid="stMetricValue"],
    html[data-theme="dark"] [data-testid="stMetricLabel"],
    body[data-theme="dark"] [data-testid="stMetricLabel"] {
        color: #e8eef7 !important;
    }

    @keyframes rise {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @media (max-width: 1024px) {
        .block-container {
            padding-top: 4.5rem !important;
            padding-left: 0.9rem;
            padding-right: 0.9rem;
        }
    }
    @media (max-width: 680px) {
        .block-container {
            padding-top: 4.8rem !important;
            padding-left: 0.72rem;
            padding-right: 0.72rem;
        }
        .hero { padding: 0.95rem; }
    }
    </style>
    """
    css = (
        css.replace("__PRIMARY__", primary_color)
        .replace("__PANEL_BG__", panel_bg)
        .replace("__PANEL_BORDER__", panel_border)
        .replace("__TAB_BG__", tab_bg)
        .replace("__APP_BG__", app_bg)
        .replace("__TEXT_MAIN__", text_color)
        .replace("__TEXT_MUTED__", text_muted)
        .replace("__BUTTON_BG__", button_bg)
        .replace("__BUTTON_TEXT__", button_text)
    )
    st.markdown(css, unsafe_allow_html=True)

    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""
        <section class="hero">
            <h1>{icon} {page_title}</h1>
            {subtitle_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def style_plotly(fig):
    template = "plotly_dark" if (st.get_option("theme.base") or "light") == "dark" else "plotly_white"
    fig.update_layout(
        template=template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=42, b=8),
    )
    return fig
