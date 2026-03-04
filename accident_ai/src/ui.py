from __future__ import annotations

import streamlit as st


def _resolve_icon(icon: str) -> str:
    icon_map = {
        "AI": "smart_toy",
        "HOME": "home",
        "DATA": "dataset",
        "DASHBOARD": "dashboard",
        "MODEL": "neurology",
        "PREDICT": "query_stats",
        "TRAIN": "model_training",
        "UPLOAD": "upload_file",
        "MANAGER": "folder_managed",
        "ANALYTICS": "analytics",
    }
    token = str(icon or "AI").strip().upper()
    if token in icon_map:
        return f"<span class='material-symbols-rounded hero-icon' aria-hidden='true'>{icon_map[token]}</span>"
    if token.isalpha():
        return f"<span class='material-symbols-rounded hero-icon' aria-hidden='true'>auto_awesome</span>"
    return f"<span class='hero-fallback-icon' aria-hidden='true'>{icon}</span>"


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
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,500,0,0');
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
        --focus-ring: rgba(19, 160, 136, 0.45);
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
    [data-testid="stToolbar"] { right: 0.7rem !important; }
    .block-container {
        padding-top: 5.2rem !important;
        padding-bottom: 1.6rem;
        max-width: 1240px;
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
        animation: rise 0.45s ease-out, glowPulse 4s ease-in-out infinite;
        margin: 0.15rem 0 0.95rem 0;
        position: relative;
        overflow: hidden;
    }
    .hero::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(115deg, transparent 10%, rgba(255,255,255,0.22) 40%, transparent 60%);
        transform: translateX(-120%);
        animation: shimmer 3.6s ease-in-out infinite;
        pointer-events: none;
    }
    .hero h1, .hero p { color: white !important; margin: 0; }
    .hero h1 { margin-bottom: 0.26rem; font-size: clamp(1.25rem, 2vw, 2rem); line-height: 1.2; }
    .hero p { opacity: 0.95; font-weight: 600; }
    .hero-title {
        display: flex;
        align-items: center;
        gap: 0.55rem;
    }
    .hero-icon {
        font-family: 'Material Symbols Rounded';
        font-size: clamp(1.35rem, 2vw, 1.9rem);
        line-height: 1;
        color: rgba(255,255,255,0.98);
        font-variation-settings: 'FILL' 1, 'wght' 600, 'GRAD' 0, 'opsz' 24;
    }
    .hero-fallback-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 1.5rem;
        min-height: 1.5rem;
        border-radius: 8px;
        background: rgba(255,255,255,0.2);
        font-weight: 800;
        font-size: 0.9rem;
    }

    .glass-card {
        background: var(--panel-bg);
        border: 1px solid var(--panel-border);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        backdrop-filter: blur(8px);
        animation: rise 0.45s ease-out;
        color: var(--text-main) !important;
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }
    .glass-card * { color: var(--text-main) !important; }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(9, 24, 47, 0.20);
        border-color: color-mix(in srgb, var(--panel-border) 75%, var(--brand-1) 25%);
    }

    .stMetric, [data-testid="stMetric"], [data-testid="metric-container"] {
        background: var(--panel-bg) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 14px;
        padding: 0.45rem 0.5rem;
        box-shadow: 0 6px 16px rgba(9, 24, 47, 0.08);
        transition: transform 180ms ease, border-color 180ms ease;
    }
    .stMetric:hover, [data-testid="metric-container"]:hover {
        transform: translateY(-1px);
        border-color: color-mix(in srgb, var(--panel-border) 72%, var(--brand-2) 28%) !important;
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
        transition: transform 160ms ease, box-shadow 160ms ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 16px rgba(9, 24, 47, 0.16);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(120deg, var(--brand-1), var(--brand-2));
        color: white !important;
        border-color: transparent !important;
        box-shadow: 0 8px 18px rgba(9, 24, 47, 0.24);
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 12px !important;
        border: 1px solid rgba(13, 102, 194, 0.35) !important;
        background: var(--button-bg) !important;
        color: var(--button-text) !important;
        font-weight: 700 !important;
        min-height: 2.55rem !important;
        padding: 0.4rem 0.9rem !important;
        box-shadow: 0 8px 18px rgba(9, 24, 47, 0.12);
        transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: rgba(19, 160, 136, 0.55) !important;
        transform: translateY(-1px) scale(1.01);
        box-shadow: 0 10px 20px rgba(9, 24, 47, 0.18);
    }
    .stButton > button:focus, .stDownloadButton > button:focus {
        outline: none !important;
        box-shadow: 0 0 0 0.2rem var(--focus-ring) !important;
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
    [data-baseweb="select"] > div, .stDateInput > div > div,
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stNumberInput"] input {
        background: color-mix(in srgb, var(--panel-bg) 92%, transparent 8%) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 11px !important;
        min-height: 2.5rem;
        color: var(--text-main) !important;
    }
    [data-baseweb="select"] > div:focus-within, .stDateInput > div > div:focus-within,
    [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus, [data-testid="stNumberInput"] input:focus {
        box-shadow: 0 0 0 0.2rem var(--focus-ring) !important;
        border-color: color-mix(in srgb, var(--brand-2) 65%, var(--panel-border) 35%) !important;
    }

    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid var(--panel-border) !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        background: var(--panel-bg) !important;
    }
    [data-testid="stDataFrame"] * {
        color: var(--text-main) !important;
    }

    [data-testid="stExpander"] details {
        background: var(--panel-bg) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 14px !important;
    }
    [data-testid="stExpander"] summary {
        font-weight: 700 !important;
        color: var(--text-main) !important;
    }
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid var(--panel-border) !important;
    }

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
    html[data-theme="dark"] [data-testid="stDataFrame"],
    body[data-theme="dark"] [data-testid="stDataFrame"],
    html[data-theme="dark"] [data-testid="stTable"],
    body[data-theme="dark"] [data-testid="stTable"] {
        background: rgba(22, 30, 43, 0.92) !important;
        border-color: rgba(117, 161, 207, 0.30) !important;
    }

    @keyframes rise {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes shimmer {
        0% { transform: translateX(-120%); }
        55% { transform: translateX(120%); }
        100% { transform: translateX(120%); }
    }
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 12px 34px rgba(17, 53, 87, 0.22); }
        50% { box-shadow: 0 14px 38px rgba(17, 53, 87, 0.30); }
    }
    @media (max-width: 1024px) {
        .block-container {
            padding-top: 5.6rem !important;
            padding-left: 0.9rem;
            padding-right: 0.9rem;
        }
    }
    @media (max-width: 680px) {
        .block-container {
            padding-top: 6rem !important;
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
    icon_html = _resolve_icon(icon)
    st.markdown(
        f"""
        <section class="hero">
            <h1 class="hero-title">{icon_html}<span>{page_title}</span></h1>
            {subtitle_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def style_plotly(fig):
    base = st.get_option("theme.base") or "light"
    mode = st.session_state.get("ui_theme_mode", "Auto")
    if mode == "Dark":
        is_dark = True
    elif mode == "Light":
        is_dark = False
    else:
        is_dark = base == "dark"
    template = "plotly_dark" if is_dark else "plotly_white"
    fig.update_layout(
        template=template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=42, b=8),
    )
    return fig
