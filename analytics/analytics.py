"""
ResultOps - Analytics Module (Firebase Firestore)
Consolidated analytics: core queries, ranking with tie-handling,
semester comparison, and subject difficulty analysis.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

import pandas as pd
from database.db import get_client

logger = logging.getLogger(__name__)


# ── Dataclasses ───────────────────────────────────────────────────────────────


@dataclass
class SemesterStats:
    semester_id: str
    semester_number: int = 0
    total_students: int = 0
    avg_sgpa: float = 0.0
    pass_count: int = 0
    fail_count: int = 0
    pass_percentage: float = 0.0
    distinction_count: int = 0
    first_class_count: int = 0
    second_class_count: int = 0
    pass_class_count: int = 0


@dataclass
class SubjectDifficulty:
    subject_code: str
    appeared: int = 0
    passed: int = 0
    failed: int = 0
    pass_pct: float = 0.0
    avg_marks: float = 0.0
    highest: int = 0
    lowest: int = 0
    fail_rate: float = 0.0
    difficulty_rank: int = 0


# ── Helpers ───────────────────────────────────────────────────────────────────


def _categorize_sgpa(sgpa: Optional[float]) -> str:
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


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ANALYTICS CLASS
# ══════════════════════════════════════════════════════════════════════════════


class Analytics:
    """Single entry-point for all analytics — queries Firebase Firestore."""

    def __init__(self):
        self.db = get_client()

    # ------------------------------------------------------------------
    # FILTER HELPERS
    # ------------------------------------------------------------------

    def get_universities(self) -> list[dict]:
        docs = self.db.collection("semesters").stream()
        names = sorted({d.to_dict().get("university", "") for d in docs} - {""})
        return [{"id": n, "name": n} for n in names]

    def get_colleges(self, university: Optional[str] = None) -> list[dict]:
        q = self.db.collection("semesters")
        if university:
            q = q.where("university", "==", university)
        names = sorted({d.to_dict().get("college", "") for d in q.stream()} - {""})
        return [{"id": n, "name": n} for n in names]

    def get_departments(self, college: Optional[str] = None) -> list[dict]:
        q = self.db.collection("semesters")
        if college:
            q = q.where("college", "==", college)
        names = sorted({d.to_dict().get("department", "") for d in q.stream()} - {""})
        return [{"id": n, "name": n} for n in names]

    def get_semesters_for_department(self, department: str) -> list[dict]:
        docs = self.db.collection("semesters").where("department", "==", department).stream()
        results = []
        for d in docs:
            data = d.to_dict()
            results.append(
                {
                    "id": d.id,
                    "semester_number": data.get("semester_number"),
                    "session_type": data.get("session_type"),
                    "session_year": data.get("session_year"),
                }
            )
        return sorted(results, key=lambda x: x.get("semester_number") or 0)

    # ------------------------------------------------------------------
    # INTERNAL: fetch all results for a semester
    # ------------------------------------------------------------------

    def _get_results(self, semester_key: str) -> list[dict]:
        docs = self.db.collection("results").where("semester_key", "==", semester_key).stream()
        return [d.to_dict() for d in docs]

    # ------------------------------------------------------------------
    # CORE ANALYTICS
    # ------------------------------------------------------------------

    def semester_summary(self, semester_key: str) -> dict:
        records = self._get_results(semester_key)
        if not records:
            return {}
        sgpas = [r["sgpa"] for r in records if r.get("sgpa") is not None]
        statuses = [r.get("result_status", "") for r in records]
        pass_c = statuses.count("PASS")
        return {
            "total_students": len(records),
            "avg_sgpa": round(sum(sgpas) / len(sgpas), 2) if sgpas else 0,
            "max_sgpa": max(sgpas, default=0),
            "min_sgpa": min(sgpas, default=0),
            "distinctions": sum(1 for s in sgpas if s >= 7.75),
            "first_class": sum(1 for s in sgpas if 6.75 <= s < 7.75),
            "pass_count": pass_c,
            "fail_count": len(records) - pass_c,
            "pass_percentage": (round(pass_c / len(statuses) * 100, 1) if statuses else 0),
        }

    def student_rank_list(self, semester_key: str) -> pd.DataFrame:
        """Return rank list sorted by SGPA descending — sequential numbering (1, 2, 3...)."""
        records = self._get_results(semester_key)
        if not records:
            return pd.DataFrame()

        # Sort by SGPA descending
        records.sort(key=lambda r: r.get("sgpa") or 0, reverse=True)

        rows = []
        for i, r in enumerate(records, start=1):
            sgpa = r.get("sgpa")
            rows.append(
                {
                    "Rank": i,
                    "PRN": r.get("prn", ""),
                    "Seat No": r.get("seat_no", ""),
                    "Name": r.get("name", ""),
                    "SGPA": sgpa,
                    "Status": r.get("result_status", ""),
                    "Category": _categorize_sgpa(sgpa),
                }
            )

        return pd.DataFrame(rows)

    def subject_analytics(self, semester_key: str) -> pd.DataFrame:
        records = self._get_results(semester_key)
        if not records:
            return pd.DataFrame()

        subject_map: dict[str, list] = {}
        for r in records:
            for subj in r.get("subjects", []):
                code = subj.get("subject_code", "?")
                subject_map.setdefault(code, []).append(subj)

        rows = []
        for code, entries in sorted(subject_map.items()):
            totals = [e["total"] for e in entries if e.get("total") is not None]
            grades = [e.get("grade") for e in entries]
            passed = sum(1 for g in grades if g not in ("F", "FF", "AB", None))
            appeared = len(entries)
            rows.append(
                {
                    "subject_code": code,
                    "Appeared": appeared,
                    "Passed": passed,
                    "Failed": appeared - passed,
                    "Pass %": round(passed / appeared * 100, 1) if appeared else 0,
                    "Highest": max(totals, default=0),
                    "Lowest": min(totals, default=0),
                    "Average": round(sum(totals) / len(totals), 2) if totals else 0,
                }
            )
        return pd.DataFrame(rows)

    def sgpa_distribution(self, semester_key: str) -> pd.DataFrame:
        records = self._get_results(semester_key)
        sgpas = [r["sgpa"] for r in records if r.get("sgpa") is not None]
        if not sgpas:
            return pd.DataFrame(columns=["SGPA Range", "Count"])
        bins = [0, 4, 5, 6, 6.75, 7.75, 8.5, 10]
        labels = ["<4", "4-5", "5-6", "6-6.75", "6.75-7.75", "7.75-8.5", ">8.5"]
        df = pd.DataFrame({"SGPA": sgpas})
        df["Range"] = pd.cut(df["SGPA"], bins=bins, labels=labels)
        dist = df["Range"].value_counts().sort_index().reset_index()
        dist.columns = ["SGPA Range", "Count"]
        return dist

    # ------------------------------------------------------------------
    # HISTORY & DELETE
    # ------------------------------------------------------------------

    def list_uploaded_semesters(self) -> pd.DataFrame:
        try:
            docs = self.db.collection("semesters").order_by("created_at", direction="DESCENDING").stream()
        except Exception:
            docs = self.db.collection("semesters").stream()

        rows = []
        for d in docs:
            data = d.to_dict()
            rows.append(
                {
                    "Semester Key": d.id,
                    "University": data.get("university", ""),
                    "College": data.get("college", ""),
                    "Department": data.get("department", ""),
                    "Semester No": data.get("semester_number", ""),
                    "Session": f"{data.get('session_type','')} {data.get('session_year','')}",
                    "Students": data.get("student_count", ""),
                    "Uploaded At": str(data.get("created_at", ""))[:10],
                }
            )
        return pd.DataFrame(rows)

    def delete_semester(self, semester_key: str) -> int:
        """Delete semester + all its result docs. Returns count of deleted results."""
        docs = self.db.collection("results").where("semester_key", "==", semester_key).stream()
        batch = self.db.batch()
        count = 0
        total_deleted = 0
        for d in docs:
            batch.delete(d.reference)
            count += 1
            total_deleted += 1
            if count >= 499:
                batch.commit()
                batch = self.db.batch()
                count = 0
        if count > 0:
            batch.commit()

        self.db.collection("semesters").document(semester_key).delete()
        logger.info(f"Deleted semester {semester_key}: {total_deleted} result docs removed")
        return total_deleted

    # ------------------------------------------------------------------
    # ADVANCED: SEMESTER COMPARISON
    # ------------------------------------------------------------------

    def compare_semesters(self, semester_keys: list[str]) -> pd.DataFrame:
        """
        Compare multiple semesters side-by-side.
        Pass a list of semester_key strings.
        """
        rows = []
        for key in semester_keys:
            summary = self.semester_summary(key)
            if not summary:
                continue
            # Get semester metadata
            doc = self.db.collection("semesters").document(key).get()
            meta = doc.to_dict() if doc.exists else {}
            sem_num = meta.get("semester_number", "")
            sess_type = meta.get("session_type", "")
            sess_year = meta.get("session_year", "")
            rows.append(
                {
                    "Semester": f"Sem {sem_num} {sess_type} {sess_year}",
                    "Students": summary["total_students"],
                    "Avg SGPA": summary["avg_sgpa"],
                    "Max SGPA": summary["max_sgpa"],
                    "Pass %": summary["pass_percentage"],
                    "Distinctions": summary["distinctions"],
                    "First Class": summary["first_class"],
                    "Failures": summary["fail_count"],
                }
            )

        df = pd.DataFrame(rows)
        return df

    def get_trend_analysis(self, comparison_df: pd.DataFrame) -> dict:
        """Analyze SGPA trend across semesters."""
        if len(comparison_df) < 2:
            return {"message": "Need at least 2 semesters for trend analysis"}

        first = comparison_df.iloc[0]["Avg SGPA"]
        last = comparison_df.iloc[-1]["Avg SGPA"]
        change = last - first

        trend = "stable"
        if change > 0.5:
            trend = "📈 improving"
        elif change < -0.5:
            trend = "📉 declining"

        return {
            "sgpa_trend": trend,
            "best_semester": comparison_df.loc[comparison_df["Avg SGPA"].idxmax(), "Semester"],
            "worst_semester": comparison_df.loc[comparison_df["Avg SGPA"].idxmin(), "Semester"],
            "change_per_sem": round(change / len(comparison_df), 2),
        }

    # ------------------------------------------------------------------
    # ADVANCED: SUBJECT DIFFICULTY RANKING
    # ------------------------------------------------------------------

    def subject_difficulty(self, semester_key: str) -> pd.DataFrame:
        """
        Rank subjects by difficulty score.
        Score = (Fail% × 0.6) + ((100 − AvgMarks) × 0.4)  [higher = harder]
        """
        records = self._get_results(semester_key)
        if not records:
            return pd.DataFrame()

        stats: dict[str, dict] = defaultdict(
            lambda: {
                "marks": [],
                "passed": 0,
                "failed": 0,
                "highest": 0,
                "lowest": 9999,
            }
        )
        for r in records:
            for subj in r.get("subjects", []):
                code = subj.get("subject_code", "?")
                total = subj.get("total") or 0
                grade = subj.get("grade", "F")
                s = stats[code]
                s["marks"].append(total)
                if grade in ("F", "FF", "AB"):
                    s["failed"] += 1
                else:
                    s["passed"] += 1
                s["highest"] = max(s["highest"], total)
                if total > 0:
                    s["lowest"] = min(s["lowest"], total)

        rows = []
        for code, s in stats.items():
            appeared = s["passed"] + s["failed"]
            if appeared == 0:
                continue
            avg = sum(s["marks"]) / len(s["marks"]) if s["marks"] else 0
            fail_rate = s["failed"] / appeared * 100
            difficulty = (fail_rate * 0.6) + ((100 - avg) * 0.4)
            rows.append(
                {
                    "Subject Code": code,
                    "Appeared": appeared,
                    "Passed": s["passed"],
                    "Failed": s["failed"],
                    "Pass %": round(s["passed"] / appeared * 100, 1),
                    "Fail %": round(fail_rate, 1),
                    "Avg Marks": round(avg, 1),
                    "Highest": s["highest"],
                    "Lowest": s["lowest"] if s["lowest"] < 9999 else 0,
                    "Difficulty": round(difficulty, 1),
                }
            )

        rows.sort(key=lambda x: x["Difficulty"], reverse=True)
        for i, row in enumerate(rows, 1):
            row["Rank"] = i

        return pd.DataFrame(rows)


# ── Convenience functions (backward compatibility) ────────────────────────────


def categorize_sgpa(sgpa: Optional[float]) -> str:
    return _categorize_sgpa(sgpa)
