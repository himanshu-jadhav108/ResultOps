"""
System Stats page — global Firebase database metrics.
"""
import pandas as pd
import streamlit as st
from datetime import datetime
from utils.theme import theme_manager


def render():
    c = theme_manager.colors
    st.title("⚙️ System Statistics")
    st.markdown("---")

    try:
        from database.db import get_db
        db = get_db()
    except Exception as e:
        st.error(f"❌ Cannot connect to database: {e}")
        return

    @st.cache_data(ttl=300)
    def get_system_stats():
        stats = {
            "total_students": 0, "total_semesters": 0,
            "total_records": 0, "total_pdfs": 0,
            "department_breakdown": {}, "yearly_stats": {},
            "last_updated": datetime.now(),
        }
        try:
            semesters = list(db.collection("semesters").stream())
            stats["total_semesters"] = len(semesters)
            for sem in semesters:
                d = sem.to_dict()
                stats["total_pdfs"] += 1
                dept = d.get("department", "Unknown")
                stats["department_breakdown"][dept] = stats["department_breakdown"].get(dept, 0) + 1
                year = str(d.get("session_year", "Unknown"))
                if year not in stats["yearly_stats"]:
                    stats["yearly_stats"][year] = {"count": 0, "students": 0}
                stats["yearly_stats"][year]["count"] += 1
                sc = d.get("student_count", 0)
                stats["yearly_stats"][year]["students"] += sc
                stats["total_students"] += sc
            stats["total_records"] = len(list(db.collection("results").stream()))
        except Exception as e:
            st.error(f"Error fetching stats: {e}")
        return stats

    stats = get_system_stats()

    # ── Key metrics ────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👨‍🎓 Total Students",  f"{stats['total_students']:,}",
              f"{stats['total_semesters']} Semesters")
    m2.metric("📁 Total Semesters",   stats["total_semesters"],
              f"{stats['total_pdfs']} PDFs processed")
    m3.metric("📝 Total Records",     f"{stats['total_records']:,}")
    storage_eff = (
        stats["total_students"] / stats["total_records"] * 100
        if stats["total_records"] > 0 else 0
    )
    m4.metric("💾 Storage Efficiency", f"{storage_eff:.1f}%",
              help="Ratio of students to total records")

    st.markdown("---")

    # ── Department breakdown ───────────────────────────────────────────────────
    if stats["department_breakdown"]:
        st.markdown("### 🏛️ Department Distribution")
        dept_df = pd.DataFrame([
            {"Department": k, "Semesters": v}
            for k, v in sorted(stats["department_breakdown"].items(),
                               key=lambda x: x[1], reverse=True)
        ])
        col1, col2 = st.columns([2, 1])
        with col1:
            st.bar_chart(dept_df.set_index("Department"), color=c["accent"])
        with col2:
            st.dataframe(dept_df, use_container_width=True, hide_index=True)

    # ── Yearly trends ──────────────────────────────────────────────────────────
    if stats["yearly_stats"]:
        st.markdown("### 📈 Yearly Trends")
        year_df = pd.DataFrame([
            {"Year": k, "Semesters": v["count"], "Students": v["students"]}
            for k, v in sorted(stats["yearly_stats"].items())
        ])
        st.line_chart(year_df.set_index("Year")[["Semesters", "Students"]])

    # ── System health ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔧 System Health")
    hc1, hc2, hc3 = st.columns(3)
    with hc1:
        if stats["total_semesters"] > 0:
            st.success("✅ Database Connected & Active")
        else:
            st.warning("⚠️ Connected — No Data Yet")
    with hc2:
        st.info(f"🕐 Last Updated: {stats['last_updated'].strftime('%H:%M:%S')}")
    with hc3:
        if stats["total_students"] > 0:
            avg = stats["total_students"] / stats["total_semesters"]
            st.info(f"📊 Avg Students/Semester: {avg:.1f}")

    if st.button("🔄 Refresh Statistics", type="primary"):
        st.cache_data.clear()
        st.rerun()