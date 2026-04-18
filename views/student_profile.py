"""
ResultOps - Student Profile Page
PRN or Name-based student lookup with subject marks chart and SGPA trend analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.theme import theme_manager


def _try_db():
    try:
        from database.db import get_client

        return get_client()
    except Exception as e:
        st.error(f"❌ Cannot connect to Firebase: {e}")
        return None


def _fetch_by_prn(db, prn: str) -> list[dict]:
    """Fetch all result docs for a given PRN (multiple semesters possible)."""
    docs = db.collection("results").where("prn", "==", prn.strip()).stream()
    return [d.to_dict() for d in docs]


def _fetch_by_name(db, name: str) -> list[dict]:
    """Fetch all result docs where name starts with the search query (case-sensitive)."""
    name_clean = name.strip()
    # Firestore range query for prefix match on 'name' field
    docs = (
        db.collection("results")
        .where("name", ">=", name_clean)
        .where("name", "<=", name_clean + "\uf8ff")
        .limit(100)
        .stream()
    )
    return [d.to_dict() for d in docs]


def _group_by_student(records: list[dict]) -> dict[str, list[dict]]:
    """Group records by PRN so each student's semesters are together."""
    grouped: dict[str, list[dict]] = {}
    for r in records:
        key = r.get("prn") or r.get("name", "Unknown")
        grouped.setdefault(key, []).append(r)
    return grouped


def _categorize_sgpa(sgpa) -> str:
    if sgpa is None:
        return "N/A"
    if sgpa >= 7.75:
        return "Distinction"
    if sgpa >= 6.75:
        return "First Class"
    if sgpa >= 6.0:
        return "Higher Second"
    if sgpa >= 5.0:
        return "Second Class"
    if sgpa >= 4.0:
        return "Pass"
    return "Fail"


def _plotly_cfg():
    return {"displayModeBar": False}


# ── Charts ────────────────────────────────────────────────────────────────────


def _bar_subject_marks(subjects: list[dict]):
    if not subjects:
        return None
    tc = theme_manager.colors
    rows = [
        {"Subject": s.get("subject_code", "?"), "Marks": s.get("total") or 0}
        for s in subjects
    ]
    df = pd.DataFrame(rows).sort_values("Subject")
    fig = px.bar(
        df,
        x="Subject",
        y="Marks",
        color_discrete_sequence=[tc["accent"]],
        title="📝 Subject-wise Marks",
        text="Marks",
    )
    fig.update_traces(textposition="outside", textfont_color=tc["text"])
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=tc["text"], family="Plus Jakarta Sans, sans-serif"),
        title_font=dict(size=15, color=tc["text"], weight="bold"),
        margin=dict(t=48, b=80, l=10, r=10),
        xaxis=dict(
            showgrid=False,
            type="category",
            tickangle=-35,
            automargin=True,
            tickfont=dict(color=tc["plotly_tick"], size=11),
            title_font=dict(color=tc["text"]),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=tc["plotly_grid"],
            tickfont=dict(color=tc["plotly_tick"], size=11),
            title_font=dict(color=tc["text"]),
        ),
    )
    return fig


def _line_sgpa_trend(records: list[dict]):
    """Line chart of SGPA across semesters (sorted by semester number)."""
    tc = theme_manager.colors
    rows = []
    for r in records:
        sem_num = r.get("semester_number")
        sess = f"{r.get('session_type', '')} {r.get('session_year', '')}".strip()
        label = f"Sem {sem_num}" + (f" ({sess})" if sess else "")
        rows.append(
            {"Semester": label, "SGPA": r.get("sgpa") or 0, "_num": sem_num or 0}
        )

    df = pd.DataFrame(rows).sort_values("_num")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Semester"],
            y=df["SGPA"],
            mode="lines+markers+text",
            text=[str(v) for v in df["SGPA"]],
            textposition="top center",
            textfont=dict(color=tc["text"], size=12),
            line=dict(color="#2d8cff", width=3),
            marker=dict(size=10, color="#f5a623", line=dict(color="#2d8cff", width=2)),
            name="SGPA",
        )
    )
    # Reference lines
    for val, color, label in [
        (7.75, "#f5a623", "Distinction"),
        (6.75, "#00d97e", "First Class"),
        (4.0, "#ff4d6d", "Pass Line"),
    ]:
        fig.add_hline(
            y=val,
            line_dash="dot",
            line_color=color,
            annotation_text=label,
            annotation_position="top right",
            annotation_font_color=color,
        )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=tc["text"], family="Plus Jakarta Sans, sans-serif"),
        title_text="📈 SGPA Trend Across Semesters",
        title_font=dict(size=15, color=tc["text"], weight="bold"),
        margin=dict(t=52, b=30, l=10, r=10),
        xaxis=dict(
            showgrid=False,
            title="Semester",
            tickfont=dict(color=tc["plotly_tick"], size=11),
            title_font=dict(color=tc["text"]),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=tc["plotly_grid"],
            title="SGPA",
            range=[0, 10.5],
            tickfont=dict(color=tc["plotly_tick"], size=11),
            title_font=dict(color=tc["text"]),
        ),
    )
    return fig


# ── Info card helper ──────────────────────────────────────────────────────────


def _info_card(label, value, color="#6366f1"):
    c = theme_manager.colors
    return f"""
<div class="premium-card" style="border-top: 3px solid {color}; padding: 16px; margin-bottom: 0px;">
    <div style="font-size:10px; text-transform:uppercase; color:{c['text_muted']}; 
                letter-spacing:1px; font-weight:700; margin-bottom:8px;">{label}</div>
    <div style="font-size:14px; font-weight:700; color:{c['text']}; line-height:1.4;">{value}</div>
</div>"""


# ── Render one student detail ─────────────────────────────────────────────────


def _render_student(records: list[dict], c: dict):
    """Render full profile for one student (one or more semesters)."""
    records = sorted(records, key=lambda r: r.get("semester_number") or 0)
    latest = records[-1]

    # Info header
    p1, p2, p3, p4 = st.columns(4)
    p1.markdown(
        _info_card("Name", latest.get("name", "—"), "#2d8cff"), unsafe_allow_html=True
    )
    p2.markdown(
        _info_card("PRN", latest.get("prn", "—"), "#a78bfa"), unsafe_allow_html=True
    )
    p3.markdown(
        _info_card("Department", latest.get("department", "—"), "#f5a623"),
        unsafe_allow_html=True,
    )
    p4.markdown(
        _info_card("University", latest.get("university", "—"), "#00d97e"),
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)

    # Semester tabs or single view
    if len(records) > 1:
        st.markdown("---")
        st.markdown("### 📋 All Semesters")
        tab_labels = [
            f"Sem {r.get('semester_number', '?')} · {r.get('session_type', '')} {r.get('session_year', '')}".strip()
            for r in records
        ]
        tabs = st.tabs(tab_labels)
        for tab, record in zip(tabs, records):
            with tab:
                _render_semester_detail(record, c)
    else:
        st.markdown("---")
        _render_semester_detail(latest, c)

    # SGPA Trend
    if len(records) > 1:
        st.markdown("---")
        st.markdown("### 📈 SGPA Trend")
        fig_trend = _line_sgpa_trend(records)
        st.plotly_chart(fig_trend, use_container_width=True, config=_plotly_cfg())

        sgpas = [r.get("sgpa") or 0 for r in records]
        if len(sgpas) >= 2:
            delta = sgpas[-1] - sgpas[0]
            if delta > 0.3:
                st.success(
                    f"📈 Improving trend — SGPA increased by **{delta:.2f}** from Sem 1 to latest."
                )
            elif delta < -0.3:
                st.warning(
                    f"📉 Declining trend — SGPA dropped by **{abs(delta):.2f}** from Sem 1 to latest."
                )
            else:
                st.info("➡️ SGPA has remained relatively stable across semesters.")


# ── Main render ───────────────────────────────────────────────────────────────


def render():
    c = theme_manager.colors

    st.markdown(
        f"""
<div class="premium-card" style="padding: 24px 32px; border-bottom: 4px solid {c['accent']};">
  <div style="font-size:28px; font-weight:800; color:{c['text']}; letter-spacing:-0.5px;">👤 Student Profile</div>
  <div style="font-size:13px; color:{c['text_muted']}; margin-top:8px; font-weight:500;">
    Search by <span style="color:{c['accent']}; font-weight:700;">PRN</span>
    or <span style="color:{c['accent']}; font-weight:700;">Student Name</span>
    — view detailed marks, SGPA analysis, and academic trends.
  </div>
</div>""",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Search Mode toggle ────────────────────────────────────────────────────
    mode = st.radio(
        "Search by",
        ["🔢 PRN Number", "📛 Student Name"],
        horizontal=True,
        key="profile_mode",
        label_visibility="collapsed",
    )
    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)

    # ── Input row ─────────────────────────────────────────────────────────────
    search_col, btn_col = st.columns([4, 1])

    if mode == "🔢 PRN Number":
        with search_col:
            query = st.text_input(
                "Enter PRN",
                placeholder="e.g. 2021016400123456",
                key="profile_prn",
                label_visibility="collapsed",
            )
        with btn_col:
            search_clicked = st.button(
                "🔍 Search", type="primary", use_container_width=True, key="btn_prn"
            )
    else:
        with search_col:
            query = st.text_input(
                "Enter student name",
                placeholder="e.g. RAHUL SHARMA",
                key="profile_name",
                label_visibility="collapsed",
            )
            st.caption(
                "💡 **Tip**: Name search is case-sensitive (e.g., use uppercase)."
            )
        with btn_col:
            search_clicked = st.button(
                "🔍 Search", type="primary", use_container_width=True, key="btn_name"
            )

    # ── Empty state ───────────────────────────────────────────────────────────
    if not query and not search_clicked:
        st.markdown(
            f"""
<div style="text-align:center;padding:60px;color:{c['text_muted']};">
  <div style="font-size:54px;margin-bottom:14px;">🎓</div>
  <div style="font-size:18px;font-weight:600;color:{c['text_sub']};">Enter a PRN or Name to look up a student</div>
  <div style="font-size:13px;margin-top:8px;">
    Student data must already be saved in the database via Upload &amp; Parse.
  </div>
</div>""",
            unsafe_allow_html=True,
        )
        return

    if not query or not query.strip():
        st.warning("⚠️ Please enter a search term.")
        return

    # ── Database lookup ───────────────────────────────────────────────────────
    db = _try_db()
    if db is None:
        return

    is_name_search = mode == "📛 Student Name"

    with st.spinner("🔍 Searching database…"):
        if is_name_search:
            records = _fetch_by_name(db, query)
        else:
            records = _fetch_by_prn(db, query)

    if not records:
        if is_name_search:
            st.error(
                f'❌ No student found with name matching **"{query.strip()}"**. '
                "Names are case-sensitive. Try uppercase (e.g. RAHUL SHARMA)."
            )
        else:
            st.error(
                f"❌ No student found with PRN **{query.strip()}**. "
                "Make sure the PDF has been uploaded and saved."
            )
        return

    # ── Name search: may return multiple students ──────────────────────────────
    if is_name_search:
        grouped = _group_by_student(records)

        if len(grouped) > 1:
            st.info(
                f'🔎 Found **{len(grouped)} students** matching "{query.strip()}". Select one below.'
            )
            student_options = {}
            for prn, recs in grouped.items():
                latest = sorted(recs, key=lambda r: r.get("semester_number") or 0)[-1]
                label = f"{latest.get('name', '—')} — PRN: {prn} — {latest.get('department', '')}"
                student_options[label] = recs

            selected_label = st.selectbox(
                "Select student",
                list(student_options.keys()),
                key="name_student_select",
            )
            chosen_records = student_options[selected_label]
        else:
            chosen_records = list(grouped.values())[0]

        st.markdown("---")
        _render_student(chosen_records, c)

    else:
        # PRN search: always single student, multiple semesters
        st.markdown("---")
        _render_student(records, c)


def _render_semester_detail(record: dict, c: dict):
    """Render marks table + bar chart for one semester record."""
    sgpa = record.get("sgpa")
    status = record.get("result_status", "—")
    category = _categorize_sgpa(sgpa)

    # Status bar
    status_color = c["success"] if status == "PASS" else c["error"]
    st.markdown(
        f"""
<div class="premium-card" style="border-left: 5px solid {status_color}; padding: 16px 24px; display: flex; gap: 32px; flex-wrap: wrap;">
  <div><span style="color:{c['text_muted']};font-size:10px;font-weight:700;text-transform:uppercase;">SEMESTER</span><br>
       <b style="color:{c['text']};font-size:14px;">
       Sem {record.get('semester_number', '?')} · {record.get('session_type', '')} {record.get('session_year', '')}</b></div>
  <div><span style="color:{c['text_muted']};font-size:10px;font-weight:700;text-transform:uppercase;">SGPA</span><br>
       <b style="color:{status_color};font-size:24px;font-weight:800;">{sgpa if sgpa is not None else '—'}</b></div>
  <div><span style="color:{c['text_muted']};font-size:10px;font-weight:700;text-transform:uppercase;">STATUS</span><br>
       <b style="color:{status_color};font-size:15px;font-weight:700;">{status}</b></div>
  <div><span style="color:{c['text_muted']};font-size:10px;font-weight:700;text-transform:uppercase;">CATEGORY</span><br>
       <b style="color:{c['text']};font-size:14px;font-weight:700;">{category}</b></div>
  <div><span style="color:{c['text_muted']};font-size:10px;font-weight:700;text-transform:uppercase;">CREDITS</span><br>
       <b style="color:{c['text']};font-size:14px;font-weight:700;">{record.get('credits_earned', '—')} / {record.get('credits_total', '—')}</b></div>
</div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    subjects = record.get("subjects", [])
    if not subjects:
        st.info("No subject data found for this semester.")
        return

    # Subject table
    subj_rows = []
    for s in subjects:
        grade = s.get("grade", "—")
        total = s.get("total")
        pass_fail = "Pass" if grade not in ("F", "FF", "AB", None) else "Fail"
        subj_rows.append(
            {
                "Subject Code": s.get("subject_code", "—"),
                "Total Marks": total if total is not None else "—",
                "Grade": grade or "—",
                "Grade Point": s.get("grade_point", "—"),
                "Credit Point": s.get("credit_point", "—"),
                "Result": pass_fail,
            }
        )

    subj_df = pd.DataFrame(subj_rows)

    def _color_result(val):
        if val == "Pass":
            return "color: #00d97e; font-weight:600"
        if val == "Fail":
            return "color: #ff4d6d; font-weight:600"
        return ""

    tbl_col, chart_col = st.columns([2, 3])
    with tbl_col:
        st.markdown("**📋 Subject Marks**")
        st.dataframe(
            subj_df.style.map(_color_result, subset=["Result"]),
            use_container_width=True,
            hide_index=True,
        )

    with chart_col:
        fig = _bar_subject_marks(subjects)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config=_plotly_cfg())
