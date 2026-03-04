"""
History page — view uploaded semesters, admin-only delete with confirmation.
"""

import streamlit as st
from utils.theme import theme_manager
from utils.auth import auth_manager


def _try_load():
    try:
        from analytics.analytics import Analytics

        return Analytics()
    except Exception as e:
        st.error(f"❌ Cannot connect to Firebase: {e}")
        return None


def render():
    c = theme_manager.colors
    st.title("📋 Upload History")
    st.markdown("All previously uploaded semester results.")
    st.markdown("---")

    analytics = _try_load()
    if analytics is None:
        return

    with st.spinner("Loading history..."):
        history_df = analytics.list_uploaded_semesters()

    if history_df.empty:
        st.markdown(
            f"""
        <div style="text-align:center; padding:60px; color:{c['text_muted']};">
            <div style="font-size:52px; margin-bottom:12px;">📭</div>
            <div style="font-size:18px; font-weight:600; color:{c['text_sub']};">No uploads yet</div>
            <div style="font-size:13px; margin-top:8px;">
                Go to Upload &amp; Parse to add your first semester
            </div>
        </div>""",
            unsafe_allow_html=True,
        )
        return

    # ── Summary metrics ────────────────────────────────────────────────────────
    h1, h2, h3 = st.columns(3)
    h1.metric("📋 Semesters Uploaded", len(history_df))
    h2.metric("📚 Departments", history_df["Department"].nunique())
    h3.metric("🏛️ Universities", history_df["University"].nunique())

    st.markdown("---")
    st.dataframe(
        history_df.drop(columns=["Semester Key"]),
        use_container_width=True,
        hide_index=True,
    )

    # ── Admin-only: Delete records ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🗑️ Delete Semester Records")
    st.caption("Only admins can delete records from the database.")

    if not auth_manager.is_admin_authenticated:
        st.warning("🔒 Admin authentication required to delete records.")
        admin_pw = st.text_input("🔐 Admin Password", type="password", key="hist_admin_pw")
        if st.button("Authenticate as Admin", type="primary", key="hist_admin_btn"):
            if auth_manager.authenticate_admin(admin_pw):
                st.success("✅ Admin access granted!")
                st.rerun()
            else:
                st.error("❌ Invalid admin password.")
        return

    # Admin is authenticated — show delete controls
    st.success("🔒 Admin authenticated — you can delete records.")

    def fmt_sem(sid):
        row = history_df[history_df["Semester Key"] == sid]
        if row.empty:
            return sid
        r = row.iloc[0]
        return f"{r['Department']} | Sem {r['Semester No']} | {r['Session']} ({r['Students']} students)"

    semester_to_delete = st.selectbox(
        "Select Semester to Delete",
        history_df["Semester Key"].tolist(),
        format_func=fmt_sem,
        key="del_sem_select",
    )

    # Show details of selected semester
    sel_row = history_df[history_df["Semester Key"] == semester_to_delete]
    if not sel_row.empty:
        sr = sel_row.iloc[0]
        st.markdown(
            f"""
        <div style="background:{c['card']}; border:1px solid {c['card_border']};
                    border-radius:10px; padding:14px 18px; margin:8px 0;">
            <b>🏛️ {sr['University']}</b> → <b>{sr['College']}</b><br>
            📚 {sr['Department']} · Semester {sr['Semester No']} · {sr['Session']}<br>
            👥 {sr['Students']} students · Uploaded: {sr['Uploaded At']}
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Two-step confirmation
    confirm = st.checkbox(
        "⚠️ I understand this will **permanently delete** all student records for this semester.",
        key="del_confirm_check",
    )

    del_col, _ = st.columns([2, 3])
    with del_col:
        delete_clicked = st.button(
            "🗑️ Delete Semester",
            type="primary",
            use_container_width=True,
            disabled=not confirm,
            key="del_sem_btn",
        )

    if delete_clicked and confirm:
        try:
            with st.spinner("🗑️ Deleting records from database..."):
                analytics.delete_semester(semester_to_delete)
            st.balloons()
            st.success(f"✅ Successfully deleted: **{fmt_sem(semester_to_delete)}**")
            st.info("The page will refresh to show updated records.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Delete failed: {e}")
