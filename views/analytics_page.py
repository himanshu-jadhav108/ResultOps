"""
Analytics Dashboard — view mode toggle, selective Excel download, charts + tables.
"""

import io
import pandas as pd
import streamlit as st
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from utils.theme import theme_manager


def _try_load():
    try:
        from analytics.analytics import Analytics

        return Analytics()
    except Exception as e:
        st.error(f"❌ Cannot connect to Firebase: {e}")
        return None


# ── Excel export — selective sheets ───────────────────────────────────────────
def _build_excel(summary, rank_df, subj_df, dist_df, include, meta_info=None) -> bytes:
    """Build Excel with only the selected sheets."""
    HFILL = PatternFill("solid", fgColor="1F4E79")
    AFILL = PatternFill("solid", fgColor="EBF2FF")
    HFONT = Font(bold=True, color="FFFFFF", size=11)
    BSIDE = Side(style="thin", color="C5D5EA")
    BORD = Border(left=BSIDE, right=BSIDE, top=BSIDE, bottom=BSIDE)

    def _style(ws, df):
        for col in range(1, len(df.columns) + 1):
            cell = ws.cell(1, col)
            cell.fill = HFILL
            cell.font = HFONT
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = BORD
        for r in range(2, ws.max_row + 1):
            for col in range(1, ws.max_column + 1):
                cell = ws.cell(r, col)
                cell.fill = AFILL if r % 2 == 0 else PatternFill()
                cell.border = BORD
                cell.alignment = Alignment(horizontal="left", vertical="center")
        for col_idx, col_name in enumerate(df.columns, 1):
            ltr = get_column_letter(col_idx)
            mx = max(
                len(str(col_name)),
                *[len(str(ws.cell(r, col_idx).value or "")) for r in range(2, ws.max_row + 1)],
                0,
            )
            ws.column_dimensions[ltr].width = min(mx + 4, 45)
        ws.row_dimensions[1].height = 28

    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        if include.get("summary"):
            # Add college/university metadata to the summary sheet
            summary_data = {}
            if meta_info:
                summary_data["University"] = meta_info.get("university", "")
                summary_data["College"] = meta_info.get("college", "")
                summary_data["Department"] = meta_info.get("department", "")
                summary_data["Semester"] = meta_info.get("semester", "")
                summary_data["---"] = "---"
            summary_data.update(summary)
            s_df = pd.DataFrame(list(summary_data.items()), columns=["Metric", "Value"])
            s_df.to_excel(w, sheet_name="Summary", index=False)
            _style(w.sheets["Summary"], s_df)

        if include.get("rank_list") and not rank_df.empty:
            rank_df.to_excel(w, sheet_name="Rank List", index=False)
            _style(w.sheets["Rank List"], rank_df)

        if include.get("subject") and not subj_df.empty:
            subj_df.to_excel(w, sheet_name="Subject Analytics", index=False)
            _style(w.sheets["Subject Analytics"], subj_df)

        if include.get("sgpa_dist") and not dist_df.empty:
            dist_df.to_excel(w, sheet_name="SGPA Distribution", index=False)
            _style(w.sheets["SGPA Distribution"], dist_df)

    out.seek(0)
    return out.read()


# ── Theme-aware row highlight helpers ─────────────────────────────────────────
def _get_highlight_styles():
    """Return highlight CSS dict appropriate for current theme."""
    if theme_manager.is_dark:
        return {
            "distinction": "background-color:#0a2e1a; color:#00d97e",
            "first_class": "background-color:#0a1f3a; color:#2d8cff",
            "fail": "background-color:#3d0012; color:#ff4d6d",
            "pass_high": "background-color:#0a2e1a; color:#00d97e; font-weight:600",
            "pass_mid": "background-color:#2e2000; color:#f5a623; font-weight:600",
            "pass_low": "background-color:#3d0012; color:#ff4d6d; font-weight:600",
        }
    else:
        return {
            "distinction": "background-color:#d4edda; color:#155724",
            "first_class": "background-color:#cce5ff; color:#004085",
            "fail": "background-color:#f8d7da; color:#721c24",
            "pass_high": "background-color:#d4edda; color:#155724; font-weight:600",
            "pass_mid": "background-color:#fff3cd; color:#856404; font-weight:600",
            "pass_low": "background-color:#f8d7da; color:#721c24; font-weight:600",
        }


def render():
    c = theme_manager.colors
    hl = _get_highlight_styles()
    st.title("📊 Analytics Dashboard")
    st.markdown("---")

    analytics = _try_load()
    if analytics is None:
        return

    # ── Filters ────────────────────────────────────────────────────────────────
    st.markdown("### 🔎 Select Data")
    f1, f2, f3, f4 = st.columns(4)

    universities = analytics.get_universities()
    uni_list = [u["name"] for u in universities]
    uni_select = f1.selectbox("🏛️ University", ["— All —"] + uni_list, key="dash_uni")
    uni_filter = uni_select if uni_select != "— All —" else None

    colleges = analytics.get_colleges(uni_filter)
    col_list = [c_["name"] for c_ in colleges]
    col_select = f2.selectbox("🏫 College", ["— All —"] + col_list, key="dash_col")
    col_filter = col_select if col_select != "— All —" else None

    departments = analytics.get_departments(col_filter)
    dept_list = [d["name"] for d in departments]

    if not dept_list:
        st.info("📂 No departments found. Upload a result PDF first.")
        return

    dept_select = f3.selectbox("📚 Department", dept_list, key="dash_dept")

    semester_key = None
    sem_label = ""
    semesters = analytics.get_semesters_for_department(dept_select)
    if semesters:
        sem_labels = {
            f"Sem {s['semester_number']} — {s.get('session_type','')} {s.get('session_year','')}": s["id"]
            for s in semesters
        }
        sem_select = f4.selectbox("📋 Semester", list(sem_labels.keys()), key="dash_sem")
        semester_key = sem_labels.get(sem_select)
        sem_label = sem_select

    if not semester_key:
        st.info("📋 Select a semester to load analytics.")
        return

    st.markdown("---")

    summary = analytics.semester_summary(semester_key)
    if not summary:
        st.warning("No data found for this semester.")
        return

    # ── Semester overview metrics ──────────────────────────────────────────────
    st.markdown("### 📈 Semester Overview")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("👥 Students", summary["total_students"])
    m2.metric("📊 Avg SGPA", summary["avg_sgpa"])
    m3.metric("⭐ Highest", summary["max_sgpa"])
    m4.metric("🏆 Distinctions", summary["distinctions"])
    m5.metric("✅ Passed", summary["pass_count"])
    m6.metric("📈 Pass %", f"{summary['pass_percentage']}%")

    st.markdown("---")

    # ── Fetch data ─────────────────────────────────────────────────────────────
    rank_df = analytics.student_rank_list(semester_key)
    subj_df = analytics.subject_analytics(semester_key)
    dist_df = analytics.sgpa_distribution(semester_key)

    # Detect the actual subject code column name
    subj_code_col = None
    if not subj_df.empty:
        for possible in ["Subject Code", "subject_code", "Subject_Code"]:
            if possible in subj_df.columns:
                subj_code_col = possible
                break
        if subj_code_col is None:
            subj_code_col = subj_df.columns[0]

    # ── Download Excel — with report + college selection ──────────────────────
    with st.expander("⬇️ Download Excel Report — click to configure"):
        # Show which college/dept the report is for
        chosen_uni = uni_select if uni_select != "— All —" else "(All)"
        chosen_col = col_select if col_select != "— All —" else "(All)"
        st.markdown(f"**Report for:** 🏛️ {chosen_uni} → 🏫 {chosen_col} → " f"📚 {dept_select} → 📋 {sem_label}")

        st.caption("Select which sections to include:")
        dc1, dc2, dc3, dc4 = st.columns(4)
        inc_summary = dc1.checkbox("📋 Summary", value=True, key="dl_summary")
        inc_rank = dc2.checkbox("🏆 Rank List", value=True, key="dl_rank")
        inc_subject = dc3.checkbox("📚 Subject Analytics", value=True, key="dl_subject")
        inc_sgpa = dc4.checkbox("📉 SGPA Distribution", value=True, key="dl_sgpa")

        include = {
            "summary": inc_summary,
            "rank_list": inc_rank,
            "subject": inc_subject,
            "sgpa_dist": inc_sgpa,
        }

        meta_info = {
            "university": uni_select if uni_select != "— All —" else "All",
            "college": col_select if col_select != "— All —" else "All",
            "department": dept_select,
            "semester": sem_label,
        }

        if not any(include.values()):
            st.warning("Select at least one section to download.")
        else:
            try:
                excel_bytes = _build_excel(summary, rank_df, subj_df, dist_df, include, meta_info)
                safe_dept = dept_select.replace(" ", "_")[:20]
                safe_sem = sem_label.replace(" ", "_").replace("—", "").strip()[:15]
                st.download_button(
                    label="⬇️ Download Selected Report",
                    data=excel_bytes,
                    file_name=f"ResultOps_{safe_dept}_{safe_sem}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary",
                )
            except Exception as e:
                st.warning(f"Excel generation failed: {e}")

    st.markdown("---")

    # ── View mode ─────────────────────────────────────────────────────────────
    st.markdown("##### 👁️ View Mode")
    vb1, vb2, vb3, _vb = st.columns([1, 1, 1, 3])

    if "dash_view_mode" not in st.session_state:
        st.session_state.dash_view_mode = "charts"

    with vb1:
        if st.button(
            "📊 Charts Only",
            use_container_width=True,
            type=("primary" if st.session_state.dash_view_mode == "charts" else "secondary"),
        ):
            st.session_state.dash_view_mode = "charts"
            st.rerun()
    with vb2:
        if st.button(
            "📋 Tables Only",
            use_container_width=True,
            type=("primary" if st.session_state.dash_view_mode == "tables" else "secondary"),
        ):
            st.session_state.dash_view_mode = "tables"
            st.rerun()
    with vb3:
        if st.button(
            "📊📋 Both",
            use_container_width=True,
            type=("primary" if st.session_state.dash_view_mode == "both" else "secondary"),
        ):
            st.session_state.dash_view_mode = "both"
            st.rerun()

    show_charts = st.session_state.dash_view_mode in ("charts", "both")
    show_tables = st.session_state.dash_view_mode in ("tables", "both")

    st.markdown("---")

    # ── SGPA Distribution ─────────────────────────────────────────────────────
    st.markdown("### 📉 SGPA Distribution")

    if not dist_df.empty:
        if show_charts:
            st.bar_chart(
                dist_df.set_index("SGPA Range")["Count"],
                color=c["accent"],
                use_container_width=True,
                height=300,
            )
        if show_tables:
            total = dist_df["Count"].sum()
            display_dist = dist_df.copy()
            display_dist["Percentage"] = display_dist["Count"].apply(
                lambda x: f"{round(x/total*100,1)}%" if total > 0 else "0%"
            )
            st.dataframe(display_dist, use_container_width=True, hide_index=True)
    else:
        st.info("No distribution data.")

    st.markdown("---")

    # ── Student Rankings ──────────────────────────────────────────────────────
    st.markdown("### 🏆 Student Rankings")

    if not rank_df.empty:
        top10 = rank_df.head(10)[["Rank", "Name", "SGPA", "Status", "Category"]].copy()

        def _highlight(row):
            cat = row.get("Category", "")
            if cat == "Distinction":
                return [hl["distinction"]] * len(row)
            if cat == "First Class":
                return [hl["first_class"]] * len(row)
            return [""] * len(row)

        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown("#### 🥇 Top 10 Students")
            st.dataframe(
                top10.style.apply(_highlight, axis=1),
                use_container_width=True,
                hide_index=True,
            )

        with col_right:
            if show_charts:
                st.markdown("#### 📊 Top 10 SGPA")
                bar_data = top10.set_index("Name")["SGPA"]
                st.bar_chart(bar_data, color=c["accent"], height=280, use_container_width=True)

        with st.expander("📋 Full Rank List — click to expand"):

            def _hl_full(row):
                if row["Status"] == "FAIL":
                    return [hl["fail"]] * len(row)
                if row["Category"] == "Distinction":
                    return [hl["distinction"]] * len(row)
                if row["Category"] == "First Class":
                    return [hl["first_class"]] * len(row)
                return [""] * len(row)

            st.dataframe(
                rank_df.style.apply(_hl_full, axis=1),
                use_container_width=True,
                hide_index=True,
            )

        fail_df = rank_df[rank_df["Status"] == "FAIL"]
        if not fail_df.empty:
            with st.expander(f"⚠️ Fail List — {len(fail_df)} students"):
                st.dataframe(
                    fail_df[["Rank", "PRN", "Seat No", "Name", "SGPA"]],
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.success("✅ No failed students this semester!")
    else:
        st.info("No rank data available.")

    st.markdown("---")

    # ── Subject Analytics ─────────────────────────────────────────────────────
    st.markdown("### 📚 Subject‑wise Analytics")

    if not subj_df.empty and subj_code_col:
        if show_tables:

            def _color_pass(val):
                try:
                    v = float(val)
                    if v >= 80:
                        return hl["pass_high"]
                    if v >= 60:
                        return hl["pass_mid"]
                    return hl["pass_low"]
                except Exception:
                    return ""

            st.dataframe(
                subj_df.style.map(_color_pass, subset=["Pass %"]),
                use_container_width=True,
                hide_index=True,
            )

        if show_charts:
            ch1, ch2 = st.columns(2)
            with ch1:
                st.markdown("**Pass % by Subject**")
                pass_chart = subj_df.set_index(subj_code_col)["Pass %"]
                st.bar_chart(pass_chart, color=c["accent"], height=280, use_container_width=True)
            with ch2:
                st.markdown("**Average Marks by Subject**")
                avg_chart = subj_df.set_index(subj_code_col)["Average"]
                st.bar_chart(avg_chart, color="#f5a623", height=280, use_container_width=True)
    else:
        st.info("No subject data available.")
