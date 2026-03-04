"""
ResultOps - Result Service (Firebase Firestore)
Handles all database write operations using Firestore collections.
"""

import logging
from datetime import datetime, timezone


from database.db import get_client
from parser.metadata_extractor import PDFMetadata
from parser.student_parser import StudentRecord

logger = logging.getLogger(__name__)


class DuplicateSemesterError(Exception):
    """Raised when a semester result has already been uploaded."""

    pass


class ResultService:
    """
    Saves parsed results to Firestore.
    Collections used:
      - semesters  : one doc per semester upload (doc ID = semester_key)
      - results    : one doc per student per semester
    """

    def __init__(self):
        self.db = get_client()

    def save_results(self, metadata: PDFMetadata, students: list[StudentRecord]) -> dict:
        """
        Save all parsed results to Firestore.

        Raises:
            DuplicateSemesterError: If this semester was already uploaded.
        """
        # Build a unique, deterministic semester key
        sem_key = _make_sem_key(metadata)

        # ── Duplicate check ──────────────────────────────────────────────────
        sem_ref = self.db.collection("semesters").document(sem_key)
        if sem_ref.get().exists:
            raise DuplicateSemesterError(
                f"Semester {metadata.semester_number} "
                f"({metadata.session_type} {metadata.session_year}) "
                f"for {metadata.department_name} already exists in ResultOps."
            )

        # ── Save semester metadata document ──────────────────────────────────
        sem_ref.set(
            {
                "university": metadata.university_name,
                "college": metadata.college_name,
                "department": metadata.department_name,
                "semester_number": metadata.semester_number,
                "session_type": metadata.session_type,
                "session_year": metadata.session_year,
                "student_count": len(students),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        # ── Save students in Firestore batches (max 500 per batch) ───────────
        batch = self.db.batch()
        batch_count = 0

        for student in students:
            doc_ref = self.db.collection("results").document()
            batch.set(
                doc_ref,
                {
                    "semester_key": sem_key,
                    "university": metadata.university_name,
                    "college": metadata.college_name,
                    "department": metadata.department_name,
                    "semester_number": metadata.semester_number,
                    "session_type": metadata.session_type,
                    "session_year": metadata.session_year,
                    "prn": student.prn,
                    "seat_no": student.seat_no,
                    "name": student.name,
                    "sgpa": student.sgpa,
                    "credits_earned": student.credits_earned,
                    "credits_total": student.credits_total,
                    "result_status": "PASS" if (student.sgpa or 0) >= 4.0 else "FAIL",
                    "subjects": [
                        {
                            "subject_code": s.subject_code,
                            "components": s.components,
                            "total": s.total,
                            "grade": s.grade,
                            "grade_point": s.grade_point,
                            "credit_point": s.credit_point,
                        }
                        for s in student.subjects
                    ],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            batch_count += 1

            # Commit at Firestore's 499-operation limit
            if batch_count == 499:
                batch.commit()
                batch = self.db.batch()
                batch_count = 0

        if batch_count > 0:
            batch.commit()

        logger.info(f"Saved {len(students)} students under semester key: {sem_key}")

        return {
            "university": metadata.university_name,
            "college": metadata.college_name,
            "department": metadata.department_name,
            "semester": metadata.semester_number,
            "session": f"{metadata.session_type} {metadata.session_year}",
            "students_inserted": len(students),
            "results_inserted": len(students),
            "marks_inserted": sum(len(s.subjects) for s in students),
        }


def save_to_database(metadata, students) -> bool:
    """
    Convenience wrapper used by upload_page.
    Returns True on success, False on failure (including duplicates).
    """
    try:
        service = ResultService()
        service.save_results(metadata, students)
        return True
    except DuplicateSemesterError as e:
        logger.warning(str(e))
        return False
    except Exception as e:
        logger.error(f"save_to_database error: {e}")
        return False


def _make_sem_key(metadata: PDFMetadata) -> str:
    """Creates a deterministic unique key for a semester."""
    parts = [
        metadata.university_name.strip(),
        metadata.college_name.strip(),
        metadata.department_name.strip(),
        str(metadata.semester_number),
        metadata.session_type.strip(),
        str(metadata.session_year),
    ]
    return "|".join(parts).replace("/", "-").replace("\\", "-")
