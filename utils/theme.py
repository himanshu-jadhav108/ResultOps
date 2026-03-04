"""
ResultOps - Theme Manager
Dual light/dark theme system. Dark theme uses app2.py navy palette.
Light theme uses a clean, professional white palette.
"""

import streamlit as st

# ── Color palettes ────────────────────────────────────────────────────────────

DARK = {
    "bg": "#060e1f",
    "sidebar_grad": "linear-gradient(180deg, #0a1628 0%, #0f2c59 60%, #1a4a8a 100%)",
    "card": "#0d1f3c",
    "card_border": "rgba(45,140,255,0.25)",
    "accent": "#2d8cff",
    "accent2": "#1a4a8a",
    "text": "#e8f0fe",
    "text_muted": "#7a9cc4",
    "text_sub": "#93b5e1",
    "sidebar_text": "#e8f0fe",
    "sidebar_hr": "rgba(45,140,255,0.3)",
    "success": "#00d97e",
    "warning": "#f5a623",
    "error": "#ff4d6d",
    "hr": "rgba(45,140,255,0.15)",
    "input_bg": "#0d1f3c",
    "upload_bg": "#0d1f3c",
    "upload_border": "rgba(45,140,255,0.4)",
    "select_bg": "#0d1f3c",
    "expander_bg": "#0d1f3c",
    "expander_bdr": "rgba(45,140,255,0.2)",
    "metric_label": "#7a9cc4",
    "metric_value": "#ffffff",
    "tab_bg": "#0d1f3c",
}

LIGHT = {
    "bg": "#f4f7fb",
    "sidebar_grad": "linear-gradient(180deg, #1a3a6b 0%, #1e4d8c 60%, #2563b0 100%)",
    "card": "#ffffff",
    "card_border": "rgba(37,99,176,0.18)",
    "accent": "#2563b0",
    "accent2": "#1a3a6b",
    "text": "#0f1e3a",
    "text_muted": "#4a6fa5",
    "text_sub": "#1a3a6b",
    "sidebar_text": "#e8f0fe",
    "sidebar_hr": "rgba(255,255,255,0.25)",
    "success": "#0d7a45",
    "warning": "#b45309",
    "error": "#be123c",
    "hr": "rgba(37,99,176,0.15)",
    "input_bg": "#ffffff",
    "upload_bg": "#eef3fc",
    "upload_border": "rgba(37,99,176,0.4)",
    "select_bg": "#ffffff",
    "expander_bg": "#eef3fc",
    "expander_bdr": "rgba(37,99,176,0.2)",
    "metric_label": "#4a6fa5",
    "metric_value": "#0f1e3a",
    "tab_bg": "#eef3fc",
}


class ThemeManager:
    """Manages light/dark theme with toggle + CSS injection."""

    def __init__(self):
        if "theme" not in st.session_state:
            st.session_state.theme = "dark"

    @property
    def is_dark(self) -> bool:
        return st.session_state.get("theme", "dark") == "dark"

    @property
    def colors(self) -> dict:
        return DARK if self.is_dark else LIGHT

    def toggle(self):
        st.session_state.theme = "light" if self.is_dark else "dark"

    def render_toggle(self):
        """Render the theme toggle button in the sidebar."""
        label = "☀️ Light Mode" if self.is_dark else "🌙 Dark Mode"
        if st.sidebar.button(label, key="theme_toggle_btn", use_container_width=True):
            self.toggle()
            st.rerun()

    def apply(self):
        """Inject CSS for the current theme."""
        c = self.colors
        # Build the complete light-mode override block
        # This forces text colors on EVERY possible Streamlit element
        light_overrides = (
            ""
            if self.is_dark
            else f"""
/* ══════════════════════════════════════════════════════════════════
   LIGHT THEME — FORCE ALL TEXT TO DARK COLORS
   ══════════════════════════════════════════════════════════════════ */

/* Global: every single element in main area */
.main, .main * {{
    color: {c['text']} !important;
}}

/* Re-apply specific overrides after the global rule */
.main h1, .main h2, .main h3, .main h4 {{
    color: {c['text']} !important;
}}
.main p, .main span, .main li, .main td, .main th, .main label,
.main div, .main small, .main strong, .main em, .main a {{
    color: {c['text']} !important;
}}

/* Captions get muted but still visible */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {{
    color: {c['text_muted']} !important;
}}

/* Metric cards */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {{
    color: {c['metric_label']} !important;
}}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {{
    color: {c['metric_value']} !important;
    font-weight: 700 !important;
}}
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] * {{
    color: {c['text_sub']} !important;
}}

/* All inputs */
input, textarea, select {{
    color: {c['text']} !important;
    background-color: {c['input_bg']} !important;
}}

/* Selectbox dropdown text */
[data-testid="stSelectbox"] span,
[data-testid="stSelectbox"] div {{
    color: {c['text']} !important;
}}

/* Multi-select */
[data-testid="stMultiSelect"] span {{
    color: {c['text']} !important;
}}

/* Radio and checkbox labels */
[data-testid="stRadio"] label,
[data-testid="stRadio"] label span,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] label span {{
    color: {c['text']} !important;
}}

/* File uploader */
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] div,
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploadDropzone"] div {{
    color: {c['text']} !important;
}}

/* Expander text */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p,
.streamlit-expanderHeader,
.streamlit-expanderContent,
.streamlit-expanderContent * {{
    color: {c['text']} !important;
}}

/* Tabs text */
.stTabs [data-baseweb="tab"],
.stTabs [data-baseweb="tab-list"],
.stTabs [data-baseweb="tab"] * {{
    color: {c['text']} !important;
}}

/* Alert/info/success/warning/error boxes */
.stAlert, .stAlert * {{
    color: {c['text']} !important;
}}
[data-testid="stNotification"],
[data-testid="stNotification"] * {{
    color: {c['text']} !important;
}}

/* Dataframe headers and cells */
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] * {{
    color: {c['text']} !important;
}}

/* Download button text */
.stDownloadButton button span {{
    color: white !important;
}}

/* Spinner text */
[data-testid="stSpinner"] span {{
    color: {c['text']} !important;
}}

/* Toast messages */
[data-testid="stToast"],
[data-testid="stToast"] * {{
    color: {c['text']} !important;
}}

/* Status widgets */
[data-testid="stStatusWidget"],
[data-testid="stStatusWidget"] * {{
    color: {c['text']} !important;
}}

/* JSON display */
[data-testid="stJson"],
[data-testid="stJson"] * {{
    color: {c['text']} !important;
}}

/* Code blocks — keep them readable */
.stCodeBlock, .stCodeBlock * {{
    color: {c['text']} !important;
}}

/* Column container labels */
[data-testid="column"] * {{
    color: {c['text']} !important;
}}

/* Sidebar stays with light text (it has dark background) */
[data-testid="stSidebar"],
[data-testid="stSidebar"] * {{
    color: {c['sidebar_text']} !important;
}}
[data-testid="stSidebar"] hr {{
    border-color: {c['sidebar_hr']} !important;
}}

/* Primary buttons still white text on colored bg */
.stButton > button[kind="primary"] span,
.stDownloadButton > button span {{
    color: white !important;
}}

/* File uploader "Browse files" button — white text on dark bg */
[data-testid="stFileUploader"] button,
[data-testid="stFileUploader"] button span,
[data-testid="stFileUploader"] button p,
[data-testid="stFileUploadDropzone"] button,
[data-testid="stFileUploadDropzone"] button span,
[data-testid="baseButton-secondary"] span,
section[data-testid="stFileUploader"] button[kind="secondary"],
section[data-testid="stFileUploader"] button[kind="secondary"] span {{
    color: white !important;
    background-color: {c['accent']} !important;
    border-color: {c['accent']} !important;
}}

/* All secondary buttons — force visible text */
.stButton > button[kind="secondary"] span {{
    color: {c['accent']} !important;
}}
"""
        )

        st.markdown(
            f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

/* ── App background ───────────────────────────────────────────────────── */
.stApp {{
    background-color: {c['bg']};
}}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: {c['sidebar_grad']} !important;
}}
[data-testid="stSidebar"] * {{ color: {c['sidebar_text']} !important; }}
[data-testid="stSidebar"] hr {{ border-color: {c['sidebar_hr']} !important; }}

/* ── Main block ───────────────────────────────────────────────────────── */
.main .block-container {{
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}}

/* ── ALL MAIN CONTENT TEXT ────────────────────────────────────────────── */
.main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {{
    color: {c['text']} !important;
}}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] em,
[data-testid="stMarkdownContainer"] a {{
    color: {c['text']} !important;
}}

[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span {{
    color: {c['text_muted']} !important;
}}

[data-testid="stRadio"] label span,
[data-testid="stCheckbox"] label span {{
    color: {c['text']} !important;
}}

[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label,
[data-testid="stFileUploader"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextArea"] label {{
    color: {c['text']} !important;
    font-weight: 500 !important;
}}

[data-testid="stExpander"] summary span {{
    color: {c['text_sub']} !important;
}}

/* ── Headings ─────────────────────────────────────────────────────────── */
h1 {{
    color: {c['text']} !important;
    font-weight: 700 !important;
    font-size: 28px !important;
    margin-bottom: 6px !important;
}}
h2, h3 {{ color: {c['text_sub']} !important; font-weight: 600 !important; }}

/* ── Metric cards ─────────────────────────────────────────────────────── */
[data-testid="stMetric"] {{
    background: {c['card']};
    border: 1px solid {c['card_border']};
    border-radius: 12px;
    padding: 16px 18px;
}}
[data-testid="stMetricLabel"] span {{
    color: {c['metric_label']} !important; font-size: 12px !important;
}}
[data-testid="stMetricValue"] span {{
    color: {c['metric_value']} !important; font-weight: 700 !important;
    font-size: 22px !important;
}}

/* ── Primary button ───────────────────────────────────────────────────── */
.stButton > button[kind="primary"],
.stDownloadButton > button {{
    background: linear-gradient(135deg, {c['accent2']}, {c['accent']}) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 10px 28px !important;
    transition: opacity 0.2s !important;
}}
.stButton > button[kind="primary"]:hover,
.stDownloadButton > button:hover {{ opacity: 0.85 !important; }}
.stButton > button[kind="primary"] span,
.stDownloadButton > button span {{ color: white !important; }}

/* ── Secondary button ─────────────────────────────────────────────────── */
.stButton > button[kind="secondary"] {{
    background: transparent !important;
    color: {c['accent']} !important;
    border: 1px solid {c['accent']} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}
.stButton > button[kind="secondary"] span {{ color: {c['accent']} !important; }}

/* ── All buttons ──────────────────────────────────────────────────────── */
.stButton > button {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}}

/* ── Alerts ───────────────────────────────────────────────────────────── */
.stAlert {{ border-radius: 10px !important; }}

/* ── Dataframe ────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{ border-radius: 10px; overflow: hidden; }}

/* ── Expander ─────────────────────────────────────────────────────────── */
[data-testid="stExpander"] > details > summary {{
    background: {c['expander_bg']} !important;
    border-radius: 8px !important;
    border: 1px solid {c['expander_bdr']} !important;
    padding: 10px 14px !important;
}}
.streamlit-expanderHeader {{
    background: {c['expander_bg']} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    color: {c['text_sub']} !important;
    border: 1px solid {c['expander_bdr']} !important;
}}

/* ── Divider ──────────────────────────────────────────────────────────── */
hr {{
    border: none !important;
    border-top: 1px solid {c['hr']} !important;
    margin: 24px 0 !important;
}}

/* ── File uploader ────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {{
    border: 2px dashed {c['upload_border']} !important;
    border-radius: 12px !important;
    background: {c['upload_bg']} !important;
}}
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] section > div,
[data-testid="stFileUploadDropzone"] {{
    background: {c['upload_bg']} !important;
}}
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] small {{
    color: {c['text']} !important;
}}

/* ── Selectbox ────────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {{
    background: {c['select_bg']} !important;
    border: 1px solid {c['card_border']} !important;
    border-radius: 8px !important;
}}
[data-testid="stSelectbox"] span {{
    color: {c['text']} !important;
}}

/* ── Text / password input ────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {c['input_bg']} !important;
    color: {c['text']} !important;
    border: 1px solid {c['card_border']} !important;
    border-radius: 8px !important;
}}

/* ── Progress bar ─────────────────────────────────────────────────────── */
[data-testid="stProgressBar"] > div {{ background: {c['accent']} !important; }}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background-color: {c['tab_bg']};
    border-radius: 8px;
    padding: 4px;
}}
.stTabs [data-baseweb="tab"] {{ color: {c['text_sub']}; }}

/* ── Sidebar logo ─────────────────────────────────────────────────────── */
.sidebar-logo {{
    text-align: center;
    padding: 24px 10px 8px 10px;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: 1px;
    color: white;
}}
.sidebar-tagline {{
    text-align: center;
    font-size: 11px;
    color: #7fa8d4;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
}}

/* ── Meta card ────────────────────────────────────────────────────────── */
.meta-card {{
    background: {c['card']};
    border: 1px solid {c['card_border']};
    border-radius: 12px;
    padding: 16px 18px;
    height: 100%;
    margin-bottom: 8px;
}}
.meta-label {{
    font-size: 11px;
    color: {c['text_muted']} !important;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
    font-weight: 500;
}}
.meta-value {{
    font-size: 14px;
    font-weight: 700;
    color: {c['text']} !important;
    line-height: 1.5;
    word-break: break-word;
}}

/* ── Spinner ──────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] span {{ color: {c['text']} !important; }}

{light_overrides}
</style>
""",
            unsafe_allow_html=True,
        )


# Global instance
theme_manager = ThemeManager()
