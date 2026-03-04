"""
ResultOps - Main Application Entry Point (Firebase Edition)
University-grade result processing platform.
"""

import logging
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
logger = logging.getLogger("resultops")

# ── Must be FIRST Streamlit call ──────────────────────────────────────────────
st.set_page_config(
    page_title="ResultOps",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ─────────────────────────────────────────────────────────────────────
from utils.theme import theme_manager

theme_manager.apply()

# ── Auth ──────────────────────────────────────────────────────────────────────
from utils.auth import auth_manager

# ── SVG icon helpers ──────────────────────────────────────────────────────────
_GITHUB_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="#ffffff"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>'
_LINKEDIN_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="#ffffff"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
_INSTA_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="#ffffff"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>'
_WEB_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="#ffffff"><path d="M12 0a12 12 0 1 0 0 24A12 12 0 0 0 12 0zm-1 17.93V16a1 1 0 0 0-1-1H6.07A10.01 10.01 0 0 1 2 12c0-.34.017-.68.05-1.01L6 15v1a2 2 0 0 0 2 2v.93zM17.9 17.39A2 2 0 0 0 16 16h-1v-3a1 1 0 0 0-1-1H8v-2h2a1 1 0 0 0 1-1V7h2a2 2 0 0 0 2-2v-.41A9.98 9.98 0 0 1 22 12a9.9 9.9 0 0 1-4.1 5.39z"/></svg>'


def _social_btn(url, bg, svg, label):
    return f"""
<a href="{url}" target="_blank" style="text-decoration:none;">
<div style="background:{bg}; border-radius:8px; padding:8px 12px; margin-bottom:7px;
            display:flex; align-items:center; gap:10px; cursor:pointer;">
  {svg}
  <span style="font-size:12px; color:#ffffff !important; font-weight:600;">{label}</span>
</div></a>"""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo
    logo_path = Path("logo.png")
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
        st.markdown(
            '<div style="text-align:center; font-size:11px; color:#7fa8d4; '
            'margin-top:-6px; margin-bottom:4px; letter-spacing:0.5px;">'
            "University Result Processing Platform</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="sidebar-logo">🎓 ResultOps</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-tagline">University Result Processing Platform</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Navigation
    selected_page = st.radio(
        "Navigation",
        [
            "📤 Upload & Parse",
            "📊 Analytics Dashboard",
            "📋 History",
            "⚙️ System Stats",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Theme toggle
    theme_manager.render_toggle()

    st.markdown("---")

    # Auth status
    if auth_manager.is_admin_authenticated:
        st.success("🔒 ADMIN Access")
    if auth_manager.is_write_authenticated:
        st.success("✅ WRITE Access")
    if auth_manager.is_read_authenticated:
        st.success("✅ READ Access")

    auth_manager.render_logout_button()

    st.markdown("---")

    # Footer
    st.markdown(
        '<div style="text-align:center; font-size:11px; color:#5a7fa8; '
        'margin-bottom:4px; letter-spacing:0.5px;">'
        "ResultOps v2.0 · Firebase Edition</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="text-align:center; font-size:12px; color:#93b5e1; font-weight:600; margin-top:8px;">'
        "Built with ❤️ by</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="text-align:center; font-size:15px; color:#ffffff; font-weight:700; margin-bottom:10px;">'
        "Himanshu Jadhav</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        _social_btn(
            "https://github.com/himanshu-jadhav108",
            "#1a1a1a; border:1px solid #555",
            _GITHUB_SVG,
            "GitHub Profile",
        )
        + _social_btn(
            "https://www.linkedin.com/in/himanshu-jadhav-328082339",
            "#0a66c2",
            _LINKEDIN_SVG,
            "LinkedIn",
        )
        + _social_btn(
            "https://www.instagram.com/himanshu_jadhav_108",
            "linear-gradient(135deg,#833ab4 0%,#fd1d1d 50%,#fcb045 100%)",
            _INSTA_SVG,
            "Instagram",
        )
        + _social_btn(
            "https://himanshu-jadhav-portfolio.vercel.app/",
            "linear-gradient(135deg,#1a4a8a,#2d8cff)",
            _WEB_SVG,
            "Portfolio",
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="text-align:center; font-size:10px; color:#3d5a7a; margin-top:6px;">' "© 2025 ResultOps</div>",
        unsafe_allow_html=True,
    )

# ── Route to page modules ─────────────────────────────────────────────────────
if selected_page == "📤 Upload & Parse":
    from views import upload_page

    upload_page.render()

elif selected_page == "📊 Analytics Dashboard":
    if auth_manager.require_read_auth():
        from views import analytics_page

        analytics_page.render()

elif selected_page == "📋 History":
    if auth_manager.require_read_auth():
        from views import history_page

        history_page.render()

elif selected_page == "⚙️ System Stats":
    if auth_manager.require_admin_auth():
        from views import system_stats

        system_stats.render()
