"""
ResultOps - Professional Premium Theme Engine
Features: Glassmorphism, HSL Design Tokens, Smooth Transitions,
and robust Light/Dark mode differentiation.
"""

import streamlit as st

# ── Color Palettes (Professional HSL-based) ──────────────────────────────────

# DARK: Sleek Deep Slate & Indigo
DARK = {
    "bg": "#0f172a",  # slate-900
    "sidebar_grad": "linear-gradient(165deg, #1e293b 0%, #0f172a 100%)",
    "card": "rgba(30, 41, 59, 0.7)",  # slate-800 with glass
    "card_border": "rgba(51, 65, 85, 0.5)",
    "accent": "#6366f1",  # indigo-500
    "accent2": "#4f46e5",  # indigo-600
    "text": "#f8fafc",  # slate-50
    "text_muted": "#94a3b8",  # slate-400
    "text_sub": "#cbd5e1",  # slate-300
    "sidebar_text": "#f8fafc",
    "sidebar_hr": "rgba(255,255,255,0.1)",
    "success": "#10b981",  # emerald-500
    "warning": "#f59e0b",  # amber-500
    "error": "#ef4444",  # red-500
    "hr": "rgba(51, 65, 85, 0.3)",
    "input_bg": "#1e293b",
    "upload_bg": "rgba(30, 41, 59, 0.4)",
    "upload_border": "rgba(99, 102, 241, 0.3)",
    "select_bg": "#1e293b",
    "expander_bg": "rgba(30, 41, 59, 0.5)",
    "expander_bdr": "rgba(51, 65, 85, 0.5)",
    "metric_label": "#94a3b8",
    "metric_value": "#f8fafc",
    "tab_bg": "rgba(30, 41, 59, 0.5)",
    "plotly_grid": "rgba(255,255,255,0.05)",
    "plotly_tick": "#94a3b8",
}

# LIGHT: Clean Porcelain & Royal Blue
LIGHT = {
    "bg": "#ffffff",  # Pure white for maximum clarity
    "sidebar_grad": "linear-gradient(180deg, #0f172a 0%, #1e293b 100%)",
    "card": "#f8fafc",  # very light gray
    "card_border": "#e2e8f0",
    "accent": "#4f46e5",
    "accent2": "#4338ca",
    "text": "#0f172a",
    "text_muted": "#475569",  # slate-600 for better visibility
    "text_sub": "#1e293b",
    "sidebar_text": "#f8fafc",
    "sidebar_hr": "rgba(255,255,255,0.1)",
    "success": "#059669",
    "warning": "#d97706",
    "error": "#dc2626",
    "hr": "#e2e8f0",
    "input_bg": "#f8fafc",
    "upload_bg": "#f1f5f9",
    "upload_border": "rgba(79, 70, 229, 0.2)",
    "select_bg": "#f8fafc",
    "expander_bg": "#f1f5f9",
    "expander_bdr": "#e2e8f0",
    "metric_label": "#475569",
    "metric_value": "#0f172a",
    "tab_bg": "#f1f5f9",
    "plotly_grid": "rgba(0,0,0,0.05)",
    "plotly_tick": "#475569",
}


class ThemeManager:
    """Advanced Theme Manager with CSS Injection and Glassmorphism."""

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
        """High-visibility theme toggle in sidebar."""
        c = self.colors

        icon = "☀️" if self.is_dark else "🌙"
        label = "Switch to Light Mode" if self.is_dark else "Switch to Dark Mode"

        # Injected Custom CSS for toggle specifically
        st.sidebar.markdown(
            f"""
            <style>
            div.stButton > button[key="theme_toggle_btn"] {{
                background: rgba(255,255,255,0.1) !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
                color: white !important;
                border-radius: 12px !important;
                font-weight: 600 !important;
                margin-top: 10px !important;
                transition: all 0.3s ease !important;
            }}
            div.stButton > button[key="theme_toggle_btn"]:hover {{
                background: rgba(255,255,255,0.2) !important;
                border-color: {c['accent']} !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        if st.sidebar.button(
            f"{icon} {label}", key="theme_toggle_btn", use_container_width=True
        ):
            self.toggle()
            st.rerun()

    def apply(self):
        """Inject robust, premium CSS for the current theme."""
        c = self.colors

        # ── Glassmorphism Effect ─────────────────────────────────────────────
        glass_effect = (
            "backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);"
        )

        # ── Base Styles Injection ────────────────────────────────────────────
        st.markdown(
            f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Main font and bg override */
* {{
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

.stApp {{
    background-color: {c['bg']};
    color: {c['text']};
}}

/* ── APP CONTAINERS ──────────────────────────────────────────────────── */

[data-testid="stAppViewContainer"] {{
    background-color: {c['bg']};
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

/* ── SIDEBAR (STAYS DARK) ────────────────────────────────────────────── */

[data-testid="stSidebar"] {{
    background: {c['sidebar_grad']} !important;
    border-right: 1px solid {c['sidebar_hr']} !important;
}}

[data-testid="stSidebar"] * {{
    color: {c['sidebar_text']} !important;
}}

[data-testid="stSidebarNav"] {{
    background: transparent !important;
}}

/* Active menu item highlight (sidebar) */
[data-testid="stSidebarNav"] ul li div[data-testid="stNavLink"] {{
    background-color: transparent !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}}

[data-testid="stSidebarNav"] ul li div[data-testid="stNavLink"]:hover {{
    background-color: rgba(255,255,255,0.05) !important;
}}

[data-testid="stSidebarNav"] ul li div[data-testid="stNavLink"][aria-current="page"] {{
    background-color: rgba(99, 102, 241, 0.15) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
}}

/* ── MAIN AREA PADDING ────────────────────────────────────────────────── */

.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 5rem !important;
    max-width: 1280px !important;
}}

/* ── HEADINGS ─────────────────────────────────────────────────────────── */

h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {{
    color: {c['text']} !important;
    font-weight: 800 !important;
}}

h1 {{ font-size: 2.2rem !important; margin-bottom: 1rem !important; letter-spacing: -0.02em !important; }}
h2 {{ font-size: 1.6rem !important; opacity: 0.9 !important; border-bottom: none !important; }}

/* ── CARDS & METRICS (GLASS) ────────────────────────────────────────── */

[data-testid="stMetric"] {{
    background: {c['card']} !important;
    border: 1px solid {c['card_border']} !important;
    {glass_effect}
    border-radius: 16px !important;
    padding: 20px 24px !important;
    box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.1) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}}

[data-testid="stMetric"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 30px -4px rgba(0, 0, 0, 0.15) !important;
}}

[data-testid="stMetricLabel"] p {{
    color: {c['metric_label']} !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}}

[data-testid="stMetricValue"] div {{
    color: {c['metric_value']} !important;
    font-size: 28px !important;
    font-weight: 800 !important;
}}

/* ── BUTTONS ─────────────────────────────────────────────────────────── */

.stButton > button,
.stDownloadButton > button {{
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 0.5rem 2rem !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid transparent !important;
}}

/* Primary */
.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {c['accent2']}, {c['accent']}) !important;
    color: white !important;
    border: none !important;
}}

.stButton > button[kind="primary"]:hover {{
    transform: translateY(-1px);
    box-shadow: 0 8px 15px -1px rgba(79, 70, 229, 0.4) !important;
    opacity: 0.95 !important;
}}

/* Secondary */
.stButton > button[kind="secondary"] {{
    background-color: {c['card']} !important;
    border: 1px solid {c['card_border']} !important;
    color: {c['text']} !important;
}}

.stButton > button[kind="secondary"]:hover {{
    border-color: {c['accent']} !important;
    background-color: transparent !important;
    color: {c['accent']} !important;
}}

/* ── INPUTS & FORM ELEMENTS ──────────────────────────────────────────── */

.stTextInput input, .stTextArea textarea, .stNumberInput input, 
[data-testid="stSelectbox"] div[data-baseweb="select"] {{
    background-color: {c['input_bg']} !important;
    border: 1px solid {c['card_border']} !important;
    color: {c['text']} !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
}}

/* Dropdown list */
[data-baseweb="popover"] div, [data-baseweb="menu"] {{
    background-color: {c['input_bg']} !important;
    color: {c['text']} !important;
    border-bottom-left-radius: 12px !important;
    border-bottom-right-radius: 12px !important;
}}

[data-baseweb="option"] {{
    padding: 8px 12px !important;
    transition: background 0.2s !important;
}}

[data-baseweb="option"]:hover {{
    background-color: {c['accent']} !important;
    color: white !important;
}}

/* ── EXPANDER ────────────────────────────────────────────────────────── */

[data-testid="stExpander"] {{
    background-color: {c['expander_bg']} !important;
    border: 1px solid {c['expander_bdr']} !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}}

[data-testid="stExpander"] summary {{
    padding: 14px 20px !important;
    font-weight: 700 !important;
    color: {c['text_sub']} !important;
}}

/* ── DATA TABLES ─────────────────────────────────────────────────────── */

[data-testid="stDataFrame"] {{
    border: 1px solid {c['card_border']} !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}}

/* ── PROGRESS BAR ────────────────────────────────────────────────────── */

[data-testid="stProgressBar"] > div > div > div {{
    background-color: {c['accent']} !important;
}}

/* ── TABS ────────────────────────────────────────────────────────────── */

[data-baseweb="tab-list"] {{
    background-color: transparent !important;
    gap: 8px !important;
    margin-bottom: 1rem !important;
}}

[data-baseweb="tab"] {{
    background-color: {c['tab_bg']} !important;
    border-radius: 100px !important;
    padding: 8px 24px !important;
    font-weight: 600 !important;
    color: {c['text_muted']} !important;
    border: 1px solid {c['card_border']} !important;
    height: 38px !important;
}}

[data-baseweb="tab"][aria-selected="true"] {{
    background-color: {c['accent']} !important;
    color: white !important;
    border-color: {c['accent']} !important;
}}

/* ── ALERTS ─────────────────────────────────────────────────────────── */

.stAlert {{
    border-radius: 16px !important;
    border: none !important;
    padding: 1rem 1.25rem !important;
}}

/* Success Alert */
[data-testid="stAlert"][data-baseweb="notification"][kind="positive"] {{
    background-color: rgba(16, 185, 129, 0.1) !important;
    border: 1px solid rgba(16, 185, 129, 0.2) !important;
    color: {c['success']} !important;
}}

/* ── DIVIDERS ────────────────────────────────────────────────────────── */

hr {{
    margin: 2rem 0 !important;
    border-color: {c['hr']} !important;
    opacity: 1 !important;
}}

/* ── FILE UPLOADER ────────────────────────────────────────────────────── */

[data-testid="stFileUploadDropzone"] {{
    background-color: {c['upload_bg']} !important;
    border: 2px dashed {c['upload_border']} !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    transition: all 0.2s ease !important;
}}

[data-testid="stFileUploadDropzone"]:hover {{
    border-color: {c['accent']} !important;
    background-color: rgba(99, 102, 241, 0.05) !important;
}}

/* ── LIGHT THEME SPECIFIC FIXES ────────────────────────────────────────── */

{"[data-testid='stMain'] *, .main *, [data-testid='stVerticalBlock'] * { color: " + c['text'] + " !important; }" if not self.is_dark else ""}

/* Force white text in certain areas */
.stButton > button[kind="primary"] span, 
.stDownloadButton > button[kind="primary"] span,
[data-baseweb="tab"][aria-selected="true"] span {{
    color: white !important;
}}

/* ── CUSTOM CLASSES (USED IN PAGE MODULES) ───────────────────────────── */

.premium-card {{
    background: {c['card']};
    border: 1px solid {c['card_border']};
    {glass_effect}
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}}

.premium-badge {{
    background-color: {c['accent']};
    color: white;
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

</style>
""",
            unsafe_allow_html=True,
        )


# Global instance
theme_manager = ThemeManager()
