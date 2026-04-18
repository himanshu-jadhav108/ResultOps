"""
ResultOps - Dashboard Page
Management-level overview: KPIs, visual charts, and problem statement.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.theme import theme_manager


def _try_load():
    try:
        from analytics.analytics import Analytics

        return Analytics()
    except Exception as e:
        st.error(f"❌ Cannot connect to Firebase: {e}")
        return None


# ── KPI card helper ───────────────────────────────────────────────────────────


def _kpi(col, icon, label, value, sub=None, color="#6366f1"):
    c = theme_manager.colors
    sub_html = (
        f'<div style="font-size:11px;color:{c["text_muted"]};margin-top:2px;">{sub}</div>'
        if sub
        else ""
    )
    col.markdown(
        f"""
<div class="premium-card" style="border-top:4px solid {color}; text-align:center; height:100%; min-height:140px; display:flex; flex-direction:column; justify-content:center; align-items:center;">
  <div style="font-size:28px; margin-bottom:8px;">{icon}</div>
  <div style="font-size:24px; font-weight:800; color:{color}; line-height:1;">{value}</div>
  <div style="font-size:10px; color:{c['text_muted']}; letter-spacing:1px; text-transform:uppercase; font-weight:700; margin-top:8px;">{label}</div>
  {sub_html}
</div>""",
        unsafe_allow_html=True,
    )


# ── Chart helpers ─────────────────────────────────────────────────────────────


def _plotly_cfg():
    """Common plotly config: no mode bar clutter."""
    return {"displayModeBar": False}


def _bar_subject_avg(subj_df: pd.DataFrame, accent: str):
    if subj_df.empty:
        return None
    tc = theme_manager.colors  # local alias, avoid name clash
    code_col = next(
        (col for col in ["subject_code", "Subject Code"] if col in subj_df.columns),
        subj_df.columns[0],
    )
    avg_col = next(
        (col for col in ["Average", "average", "Avg Marks"] if col in subj_df.columns),
        None,
    )
    if avg_col is None:
        return None
    fig = px.bar(
        subj_df,
        x=code_col,
        y=avg_col,
        labels={code_col: "Subject", avg_col: "Avg Marks"},
        color_discrete_sequence=[accent],
        title="📚 Subject-wise Average Marks",
        text=avg_col,
    )
    fig.update_traces(textposition="outside", textfont_color=tc["text"])
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=tc["text"], family="Inter, sans-serif"),
        title_font=dict(size=14, color=tc["text"]),
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


def _pie_pass_fail(pass_count: int, fail_count: int):
    tc = theme_manager.colors
    fig = go.Figure(
        go.Pie(
            labels=["Pass", "Fail"],
            values=[pass_count, fail_count],
            hole=0.45,
            marker_colors=["#00d97e", "#ff4d6d"],
            textinfo="label+percent",
            textfont=dict(size=13, color=tc["text"]),
            pull=[0, 0.04],
        )
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=tc["text"], family="Inter, sans-serif"),
        title_text="🎯 Pass vs Fail Ratio",
        title_font=dict(size=14, color=tc["text"]),
        margin=dict(t=48, b=10, l=0, r=0),
        showlegend=True,
        legend=dict(font=dict(color=tc["text"])),
    )
    return fig


def _histogram_sgpa(records: list[dict]):
    tc = theme_manager.colors
    sgpas = [r["sgpa"] for r in records if r.get("sgpa") is not None]
    if not sgpas:
        return None
    fig = px.histogram(
        x=sgpas,
        nbins=14,
        labels={"x": "SGPA"},
        color_discrete_sequence=[tc["accent"]],
        title="📊 SGPA Distribution",
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=tc["text"], family="Inter, sans-serif"),
        title_font=dict(size=14, color=tc["text"]),
        margin=dict(t=48, b=30, l=10, r=10),
        xaxis=dict(
            showgrid=False,
            title="SGPA",
            tickfont=dict(color=tc["plotly_tick"], size=11),
            title_font=dict(color=tc["text"]),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=tc["plotly_grid"],
            title="Students",
            tickfont=dict(color=tc["plotly_tick"], size=11),
            title_font=dict(color=tc["text"]),
        ),
        bargap=0.05,
    )
    return fig


# ── Problem statement section ─────────────────────────────────────────────────


def _problem_statement():
    c = theme_manager.colors
    st.markdown("---")
    st.markdown("## 💡 Why ResultOps?")

    col_prob, col_sol = st.columns(2)

    with col_prob:
        st.markdown(
            f"""
<div style="background:{c['card']};border:1px solid {c['card_border']};
            border-left:4px solid #ff4d6d;border-radius:12px;padding:20px 22px;">
  <div style="font-size:16px;font-weight:700;color:#ff4d6d;margin-bottom:12px;">
    ❌ Problems with Traditional Methods
  </div>
  <ul style="color:{c['text_sub']};font-size:13px;line-height:1.9;padding-left:18px;">
    <li>Results exist only as raw tabular data — <b>no visual insights</b></li>
    <li>No ability to <b>track a student’s progress</b> across semesters</li>
    <li>Manual Excel sheets are <b>error-prone and time-consuming</b></li>
    <li>Cannot identify <b>difficult subjects</b> or at-risk students</li>
    <li>Management has <b>no actionable dashboard</b> to make decisions</li>
    <li>Trend analysis across batches is <b>completely absent</b></li>
    <li>No automated <b>rank generation</b> with tie-handling</li>
  </ul>
</div>""",
            unsafe_allow_html=True,
        )

    with col_sol:
        st.markdown(
            f"""
<div style="background:{c['card']};border:1px solid {c['card_border']};
            border-left:4px solid #00d97e;border-radius:12px;padding:20px 22px;">
  <div style="font-size:16px;font-weight:700;color:#00d97e;margin-bottom:12px;">
    ✅ How ResultOps Solves It
  </div>
  <ul style="color:{c['text_sub']};font-size:13px;line-height:1.9;padding-left:18px;">
    <li><b>One-click PDF upload</b> → automatic extraction &amp; storage</li>
    <li><b>Visual dashboards</b> with KPIs, charts &amp; trend lines</li>
    <li><b>Student profile lookup</b> by PRN — full history in seconds</li>
    <li><b>Subject difficulty ranking</b> — identifies weak areas</li>
    <li><b>Semester comparison</b> — track improvement over time</li>
    <li><b>Proper rank calculation</b> with tie-handling (1, 2, 2, 4)</li>
    <li><b>Exportable Excel reports</b> with 5 formatted sheets</li>
  </ul>
</div>""",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
<div style="background:{c['card']};border:1px solid {c['card_border']};
            border-radius:12px;padding:16px 22px;margin-top:16px;text-align:center;">
  <span style="font-size:13px;color:{c['text_muted']};">
    ResultOps transforms raw marksheet PDFs into a
    <b style="color:{c['accent']};">full Academic Performance Intelligence System</b>
    — empowering faculty, management, and institutions to make data-driven decisions.
  </span>
</div>""",
        unsafe_allow_html=True,
    )


# ── Main render ───────────────────────────────────────────────────────────────


def render():
    c = theme_manager.colors

    st.markdown(
        f"""
<div style="background:linear-gradient(135deg,{c['card']} 0%,{c['bg']} 100%);
            border:1px solid {c['card_border']};border-radius:16px;
            padding:28px 32px;margin-bottom:8px;">
  <div style="font-size:30px;font-weight:800;color:{c['text']};">
    🏠 Academic Dashboard
  </div>
  <div style="font-size:14px;color:{c['text_muted']};margin-top:6px;">
    Management-level overview · Select a semester to load live analytics
  </div>
</div>""",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    analytics = _try_load()
    if analytics is None:
        _problem_statement()
        return

    # ── Filters ───────────────────────────────────────────────────────────────
    st.markdown("### 🔎 Select Semester")
    f1, f2, f3, f4 = st.columns(4)

    universities = analytics.get_universities()
    uni_list = [u["name"] for u in universities]
    uni_sel = f1.selectbox("🏛️ University", ["— All —"] + uni_list, key="db_uni")
    uni_filter = uni_sel if uni_sel != "— All —" else None

    colleges = analytics.get_colleges(uni_filter)
    col_list = [c_["name"] for c_ in colleges]
    col_sel = f2.selectbox("🏫 College", ["— All —"] + col_list, key="db_col")
    col_filter = col_sel if col_sel != "— All —" else None

    departments = analytics.get_departments(col_filter)
    dept_list = [d["name"] for d in departments]

    if not dept_list:
        st.info("📂 No departments found. Upload a result PDF first.")
        _problem_statement()
        return

    dept_sel = f3.selectbox("📚 Department", dept_list, key="db_dept")

    semester_key = None
    semesters = analytics.get_semesters_for_department(dept_sel)
    if semesters:
        sem_labels = {
            f"Sem {s['semester_number']} — {s.get('session_type', '')} {s.get('session_year', '')}": s[
                "id"
            ]
            for s in semesters
        }
        sem_sel = f4.selectbox("📋 Semester", list(sem_labels.keys()), key="db_sem")
        semester_key = sem_labels.get(sem_sel)

    if not semester_key:
        st.info("📋 Select a semester to load the dashboard.")
        _problem_statement()
        return

    st.markdown("---")

    # ── Fetch data ────────────────────────────────────────────────────────────
    with st.spinner("Loading analytics…"):
        summary = analytics.semester_summary(semester_key)
        if not summary:
            st.warning("No data found for this semester.")
            _problem_statement()
            return

        records = analytics._get_results(semester_key)
        subj_df = analytics.subject_analytics(semester_key)
        rank_df = analytics.student_rank_list(semester_key)

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    st.markdown("### 📈 Key Performance Indicators")
    k1, k2, k3, k4, k5 = st.columns(5)

    topper_name = "—"
    topper_sgpa = "—"
    if not rank_df.empty:
        top = rank_df.iloc[0]
        topper_name = str(top.get("Name", "—"))[:18]
        topper_sgpa = top.get("SGPA", "—")

    _kpi(k1, "👥", "Total Students", summary["total_students"], color="#2d8cff")
    _kpi(k2, "📊", "Avg SGPA", summary["avg_sgpa"], color="#a78bfa")
    _kpi(
        k3,
        "✅",
        "Pass %",
        f"{summary['pass_percentage']}%",
        sub=f"{summary['pass_count']} passed",
        color="#00d97e",
    )
    _kpi(
        k4,
        "❌",
        "Total Failed",
        summary["fail_count"],
        sub=f"{100 - summary['pass_percentage']:.1f}% fail rate",
        color="#ff4d6d",
    )
    _kpi(
        k5,
        "🏆",
        "Topper SGPA",
        topper_sgpa,
        sub=topper_name,
        color="#f5a623",
    )

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    st.markdown("---")

    # ── Charts row 1: Bar + Pie ───────────────────────────────────────────────
    st.markdown("### 📊 Visual Analytics")
    ch1, ch2 = st.columns([3, 2])

    with ch1:
        fig_bar = _bar_subject_avg(subj_df, c["accent"])
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True, config=_plotly_cfg())
        else:
            st.info("No subject data available.")

    with ch2:
        fig_pie = _pie_pass_fail(summary["pass_count"], summary["fail_count"])
        st.plotly_chart(fig_pie, use_container_width=True, config=_plotly_cfg())

    # ── Charts row 2: SGPA Histogram ─────────────────────────────────────────
    fig_hist = _histogram_sgpa(records)
    if fig_hist:
        st.plotly_chart(fig_hist, use_container_width=True, config=_plotly_cfg())

    st.markdown("---")

    # ── Distinctions breakdown ────────────────────────────────────────────────
    st.markdown("### 🎓 Category Breakdown")
    cats = {
        "🏅 Distinctions (≥7.75)": summary.get("distinctions", 0),
        "⭐ First Class (6.75–7.75)": summary.get("first_class", 0),
        "✅ Passed": summary.get("pass_count", 0),
        "❌ Failed": summary.get("fail_count", 0),
    }
    cat_cols = st.columns(len(cats))
    cat_colors = ["#f5a623", "#2d8cff", "#00d97e", "#ff4d6d"]
    for col, (label, val), color in zip(cat_cols, cats.items(), cat_colors):
        col.markdown(
            f"""
<div style="background:{c['card']};border:1px solid {c['card_border']};
            border-bottom:3px solid {color};border-radius:12px;
            padding:14px;text-align:center;">
  <div style="font-size:24px;font-weight:800;color:{color};">{val}</div>
  <div style="font-size:11px;color:{c['text_muted']};margin-top:4px;">{label}</div>
</div>""",
            unsafe_allow_html=True,
        )

    # ── Problem Statement ─────────────────────────────────────────────────────
    _problem_statement()
