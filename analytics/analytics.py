"""
ResultOps - Analytics Module (Firebase Firestore)
All queries use Firestore collections instead of SQL.
"""

import logging
import pandas as pd
from typing import Optional

from database.db import get_client

logger = logging.getLogger(__name__)


class Analytics:

    def __init__(self):
        self.db = get_client()

    # ------------------------------------------------------------------
    # FILTER HELPERS
    # ------------------------------------------------------------------

    def get_universities(self) -> list[dict]:
        docs  = self.db.collection("semesters").stream()
        names = sorted(set(d.to_dict().get("university", "") for d in docs))
        return [{"id": n, "name": n} for n in names if n]

    def get_colleges(self, university: Optional[str] = None) -> list[dict]:
        q = self.db.collection("semesters")
        if university:
            q = q.where("university", "==", university)
        docs  = q.stream()
        names = sorted(set(d.to_dict().get("college", "") for d in docs))
        return [{"id": n, "name": n} for n in names if n]

    def get_departments(self, college: Optional[str] = None) -> list[dict]:
        q = self.db.collection("semesters")
        if college:
            q = q.where("college", "==", college)
        docs  = q.stream()
        names = sorted(set(d.to_dict().get("department", "") for d in docs))
        return [{"id": n, "name": n} for n in names if n]

    def get_semesters_for_department(self, department: str) -> list[dict]:
        docs = (
            self.db.collection("semesters")
            .where("department", "==", department)
            .stream()
        )
        results = []
        for d in docs:
            data = d.to_dict()
            results.append({
                "id":              d.id,   # semester_key string
                "semester_number": data.get("semester_number"),
                "session_type":    data.get("session_type"),
                "session_year":    data.get("session_year"),
            })
        return sorted(results, key=lambda x: x.get("semester_number") or 0)

    # ------------------------------------------------------------------
    # INTERNAL: fetch all results for a semester
    # ------------------------------------------------------------------

    def _get_results(self, semester_key: str) -> list[dict]:
        docs = (
            self.db.collection("results")
            .where("semester_key", "==", semester_key)
            .stream()
        )
        return [d.to_dict() for d in docs]

    # ------------------------------------------------------------------
    # ANALYTICS
    # ------------------------------------------------------------------

    def semester_summary(self, semester_key: str) -> dict:
        records = self._get_results(semester_key)
        if not records:
            return {}
        sgpas    = [r["sgpa"] for r in records if r.get("sgpa") is not None]
        statuses = [r.get("result_status", "") for r in records]
        return {
            "total_students":  len(records),
            "avg_sgpa":        round(sum(sgpas) / len(sgpas), 2) if sgpas else 0,
            "max_sgpa":        max(sgpas, default=0),
            "min_sgpa":        min(sgpas, default=0),
            "distinctions":    sum(1 for s in sgpas if s >= 7.75),
            "first_class":     sum(1 for s in sgpas if 6.75 <= s < 7.75),
            "pass_count":      statuses.count("PASS"),
            "fail_count":      statuses.count("FAIL"),
            "pass_percentage": round(statuses.count("PASS") / len(statuses) * 100, 1) if statuses else 0,
        }

    def student_rank_list(self, semester_key: str) -> pd.DataFrame:
        records = self._get_results(semester_key)
        if not records:
            return pd.DataFrame()
        records.sort(key=lambda r: r.get("sgpa") or 0, reverse=True)
        rows = []
        for i, r in enumerate(records, start=1):
            sgpa = r.get("sgpa")
            rows.append({
                "Rank":     i,
                "PRN":      r.get("prn", ""),
                "Seat No":  r.get("seat_no", ""),
                "Name":     r.get("name", ""),
                "SGPA":     sgpa,
                "Status":   r.get("result_status", ""),
                "Category": _categorize_sgpa(sgpa),
            })
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
            totals   = [e["total"] for e in entries if e.get("total") is not None]
            grades   = [e.get("grade") for e in entries]
            passed   = sum(1 for g in grades if g not in ("F", "FF", "AB", None))
            appeared = len(entries)
            rows.append({
                "subject_code": code,
                "Appeared":     appeared,
                "Passed":       passed,
                "Failed":       appeared - passed,
                "Pass %":       round(passed / appeared * 100, 1) if appeared else 0,
                "Highest":      max(totals, default=0),
                "Average":      round(sum(totals) / len(totals), 2) if totals else 0,
            })
        return pd.DataFrame(rows)

    def sgpa_distribution(self, semester_key: str) -> pd.DataFrame:
        records = self._get_results(semester_key)
        sgpas   = [r["sgpa"] for r in records if r.get("sgpa") is not None]
        if not sgpas:
            return pd.DataFrame(columns=["SGPA Range", "Count"])
        bins   = [0, 4, 5, 6, 6.75, 7.75, 8.5, 10]
        labels = ["<4", "4-5", "5-6", "6-6.75", "6.75-7.75", "7.75-8.5", ">8.5"]
        df = pd.DataFrame({"SGPA": sgpas})
        df["Range"] = pd.cut(df["SGPA"], bins=bins, labels=labels)
        dist = df["Range"].value_counts().sort_index().reset_index()
        dist.columns = ["SGPA Range", "Count"]
        return dist

    def list_uploaded_semesters(self) -> pd.DataFrame:
        try:
            docs = (
                self.db.collection("semesters")
                .order_by("created_at", direction="DESCENDING")
                .stream()
            )
        except Exception:
            # Fallback if index not yet built
            docs = self.db.collection("semesters").stream()

        rows = []
        for d in docs:
            data = d.to_dict()
            rows.append({
                "Semester Key": d.id,
                "University":   data.get("university", ""),
                "College":      data.get("college", ""),
                "Department":   data.get("department", ""),
                "Semester No":  data.get("semester_number", ""),
                "Session":      f"{data.get('session_type','')} {data.get('session_year','')}",
                "Students":     data.get("student_count", ""),
                "Uploaded At":  (data.get("created_at") or "")[:10],
            })
        return pd.DataFrame(rows)

    def delete_semester(self, semester_key: str) -> bool:
        """Delete semester document and all its student results."""
        # Delete result documents in batches
        docs = (
            self.db.collection("results")
            .where("semester_key", "==", semester_key)
            .stream()
        )
        batch = self.db.batch()
        count = 0
        for d in docs:
            batch.delete(d.reference)
            count += 1
            if count == 499:
                batch.commit()
                batch = self.db.batch()
                count = 0
        if count > 0:
            batch.commit()

        # Delete the semester document itself
        self.db.collection("semesters").document(semester_key).delete()
        logger.info(f"Deleted semester: {semester_key}")
        return True


def _categorize_sgpa(sgpa: Optional[float]) -> str:
    if sgpa is None:  return "N/A"
    if sgpa >= 7.75:  return "Distinction"
    if sgpa >= 6.75:  return "First Class"
    if sgpa >= 6.0:   return "Higher Second"
    if sgpa >= 5.0:   return "Second Class"
    if sgpa >= 4.0:   return "Pass"
    return "Fail"
