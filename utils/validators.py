"""
ResultOps - Validation Module
Pre-insertion validation of parsed student data.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from parser.student_parser import StudentRecord

logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    is_valid: bool
    total_students: int
    unique_subjects: set
    students_missing_sgpa: list[str]
    students_missing_prn: list[int]
    semester_inconsistency: bool
    expected_semester: Optional[int]
    anomalies: list[str]

    def summary_lines(self) -> list[str]:
        lines = [
            f"✅ Total Students: {self.total_students}",
            f"✅ Unique Subjects Detected: {len(self.unique_subjects)} → {sorted(self.unique_subjects)}",
        ]
        if self.students_missing_sgpa:
            lines.append(f"⚠️ Students Missing SGPA: {self.students_missing_sgpa}")
        if self.students_missing_prn:
            lines.append(f"❌ Blocks with Empty PRN: {len(self.students_missing_prn)}")
        if self.semester_inconsistency:
            lines.append(f"⚠️ Semester number inconsistency detected. Expected: {self.expected_semester}")
        for anomaly in self.anomalies:
            lines.append(f"⚠️ {anomaly}")
        if self.is_valid:
            lines.append("✅ Validation Passed — Ready to Save")
        else:
            lines.append("❌ Validation Failed — Fix issues before saving")
        return lines


def validate_students(
    students: list[StudentRecord],
    expected_semester: Optional[int] = None,
) -> ValidationReport:
    """
    Validate parsed student records before database insertion.

    Checks:
    - No empty PRNs
    - All students have SGPA
    - Consistent semester number
    - Consistent subject count (with tolerance)

    Args:
        students: List of parsed StudentRecord objects.
        expected_semester: Semester number from metadata (for consistency check).

    Returns:
        ValidationReport with pass/fail status and details.
    """
    if not students:
        return ValidationReport(
            is_valid=False,
            total_students=0,
            unique_subjects=set(),
            students_missing_sgpa=[],
            students_missing_prn=[],
            semester_inconsistency=False,
            expected_semester=expected_semester,
            anomalies=["No students found. Check PDF format."],
        )

    anomalies = []
    missing_sgpa = []
    missing_prn_indices = []
    unique_subjects = set()

    semester_numbers = set()
    subject_counts = []

    for i, s in enumerate(students):
        # Check PRN
        if not s.prn or s.prn.strip() == "":
            missing_prn_indices.append(i)

        # Check SGPA
        if s.sgpa is None:
            missing_sgpa.append(s.prn or f"[block {i}]")

        # Track subjects
        for subj in s.subjects:
            unique_subjects.add(subj.subject_code)
        subject_counts.append(len(s.subjects))

        # Track semester numbers
        if s.semester_number:
            semester_numbers.add(s.semester_number)

    # Semester consistency
    semester_inconsistency = False
    if len(semester_numbers) > 1:
        semester_inconsistency = True
        anomalies.append(f"Multiple semester numbers found: {semester_numbers}")
    if expected_semester and semester_numbers and expected_semester not in semester_numbers:
        anomalies.append(f"Metadata says semester {expected_semester} but students show {semester_numbers}")

    # Subject count consistency
    if subject_counts:
        min_count = min(subject_counts)
        max_count = max(subject_counts)
        if max_count - min_count > 2:
            anomalies.append(
                f"Subject count varies widely: min={min_count}, max={max_count}. " f"Check for parsing issues."
            )

    # Determine overall validity
    is_valid = len(missing_prn_indices) == 0 and not semester_inconsistency and len(students) > 0

    return ValidationReport(
        is_valid=is_valid,
        total_students=len(students),
        unique_subjects=unique_subjects,
        students_missing_sgpa=missing_sgpa,
        students_missing_prn=missing_prn_indices,
        semester_inconsistency=semester_inconsistency,
        expected_semester=expected_semester,
        anomalies=anomalies,
    )
