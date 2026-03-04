"""
ResultOps - Student Parser
Parses individual student blocks extracted from the PDF text.
Dynamically detects subject codes and marks components without hardcoding.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SubjectResult:
    subject_code: str
    components: dict  # e.g. {'ESE': 45, 'ISE': 18, 'TW': 20}
    total: Optional[int]
    grade: Optional[str]
    grade_point: Optional[float]
    credit_point: Optional[float]
    is_absent: bool = False
    is_ac: bool = False  # Atkt Carry / AC subject


@dataclass
class StudentRecord:
    prn: str
    seat_no: str
    name: str
    mother_name: str
    semester_number: int
    sgpa: Optional[float]
    credits_earned: Optional[int]
    credits_total: Optional[int]
    subjects: list[SubjectResult] = field(default_factory=list)


# Regex patterns
_PRN_PATTERN = re.compile(r"PRN\s*[:\-]?\s*(\S+)", re.IGNORECASE)
_SEAT_PATTERN = re.compile(r"SEAT\s*NO\.?\s*[:\-]?\s*(\S+)", re.IGNORECASE)
_NAME_PATTERN = re.compile(r"NAME\s*[:\-]?\s*([^\n]+?)(?:\s+Mother|$)", re.IGNORECASE)
_MOTHER_PATTERN = re.compile(r"Mother'?s?\s+Name\s*[:\-]+\s*([^\n]+)", re.IGNORECASE)
_SEM_PATTERN = re.compile(r"SEMESTER\s*[:\-]?\s*(\d+)", re.IGNORECASE)
_SGPA_PATTERN = re.compile(r"SGPA\s*[:\-]?\s*(?:\(\w+\))?\s*([0-9.]+)", re.IGNORECASE)
_CREDITS_PATTERN = re.compile(
    r"Credits?\s+Earned\s*/\s*Total\s*[:\-]?\s*(\d+)\s*/\s*(\d+)", re.IGNORECASE
)

# Subject line: starts with digits and uppercase letters (e.g. 410241, CS101, 22510)
_SUBJECT_LINE_PATTERN = re.compile(r"^\d{4,}[A-Z0-9_]*\b")

# Grade pattern: single letter grades like A+, A, B, C, D, F, O, P, AB
_GRADE_PATTERN = re.compile(r"\b(O|A\+|A|B\+|B|C|D|F|P|AB|FF|E)\b")

# Numeric pattern for mark components
_NUMBER_PATTERN = re.compile(r"\b(\d{1,3})\b")


def parse_students(full_text: str) -> list[StudentRecord]:
    """
    Split full PDF text into per-student blocks and parse each one.

    Args:
        full_text: Complete text extracted from the PDF.

    Returns:
        List of StudentRecord objects.
    """
    # Split on PRN marker; re-attach the prefix
    raw_blocks = re.split(r"\nPRN\s*[:\-]?\s*", full_text)

    students = []
    for i, block in enumerate(raw_blocks):
        if i == 0:
            # First chunk is the header before any PRN — skip
            continue
        # Re-attach prefix that was consumed in split
        block = "PRN: " + block.strip()
        try:
            record = _parse_student_block(block)
            if record:
                students.append(record)
        except Exception as e:
            logger.warning(f"Failed to parse student block #{i}: {e}")

    logger.info(f"Parsed {len(students)} student records")
    return students


def _parse_student_block(block: str) -> Optional[StudentRecord]:
    """Parse a single student text block into a StudentRecord."""
    lines = [line.strip() for line in block.splitlines() if line.strip()]

    # Extract header fields
    prn = _search(block, _PRN_PATTERN)
    if not prn:
        return None

    seat_no = _search(block, _SEAT_PATTERN) or ""
    name = _clean_name(_search(block, _NAME_PATTERN) or "")
    mother_name = _search(block, _MOTHER_PATTERN) or ""
    semester_number = int(_search(block, _SEM_PATTERN) or "0")
    sgpa = _parse_float(_search_last(block, _SGPA_PATTERN))

    credits_match = _CREDITS_PATTERN.search(block)
    credits_earned = int(credits_match.group(1)) if credits_match else None
    credits_total = int(credits_match.group(2)) if credits_match else None

    # Extract subject results
    subjects = _parse_subject_lines(lines)

    return StudentRecord(
        prn=prn.strip(),
        seat_no=seat_no.strip(),
        name=name.strip(),
        mother_name=mother_name.strip(),
        semester_number=semester_number,
        sgpa=sgpa,
        credits_earned=credits_earned,
        credits_total=credits_total,
        subjects=subjects,
    )


def _parse_subject_lines(lines: list[str]) -> list[SubjectResult]:
    """
    Dynamically parse subject lines from a student block.
    Each subject line starts with a subject code (digits/uppercase letters).

    Strategy:
    - Find lines matching subject code pattern
    - Extract all numbers from the line
    - Last number before grade = total (usually)
    - Handle AC (carried/absent) subjects
    """
    subjects = []

    for line in lines:
        if not _SUBJECT_LINE_PATTERN.match(line):
            continue

        tokens = line.split()
        if not tokens:
            continue

        subject_code = tokens[0]
        is_ac = bool(re.search(r"\bAC\b", line, re.IGNORECASE))
        is_absent = bool(re.search(r"\bAB\b|\bAbsent\b", line, re.IGNORECASE))

        # Extract all numbers and grade from the rest of the line
        rest = " ".join(tokens[1:])

        numbers = [int(m) for m in _NUMBER_PATTERN.findall(rest)]
        grade_match = _GRADE_PATTERN.search(rest)
        grade = grade_match.group(1) if grade_match else None

        # Build component dict
        components = {}
        total = None
        grade_point = None
        credit_point = None

        if numbers:
            # Heuristic: last large number (>= 10 typically) before grade position is total
            # grade_point is usually float, credit_point is float too
            # Numbers ordering: component marks... total credits grade_point credit_point

            # Find float values for grade_point and credit_point
            float_vals = [float(m) for m in re.findall(r"\b\d+\.\d+\b", rest)]

            if float_vals:
                credit_point = float_vals[-1] if len(float_vals) >= 2 else None
                grade_point = float_vals[-2] if len(float_vals) >= 2 else float_vals[0]

            # Total is usually the last integer before floats or grade
            if numbers:
                total = numbers[-1]
                component_nums = numbers[:-1]  # everything before total

                # Name components generically if we don't know headers
                component_labels = ["ESE", "ISE", "TW", "PR", "OR"]
                for idx, val in enumerate(component_nums):
                    label = (
                        component_labels[idx]
                        if idx < len(component_labels)
                        else f"C{idx+1}"
                    )
                    components[label] = val

        subjects.append(
            SubjectResult(
                subject_code=subject_code,
                components=components,
                total=total,
                grade=grade,
                grade_point=grade_point,
                credit_point=credit_point,
                is_absent=is_absent,
                is_ac=is_ac,
            )
        )

    return subjects


def _search(text: str, pattern: re.Pattern) -> Optional[str]:
    """Return first group match or None."""
    m = pattern.search(text)
    return m.group(1).strip() if m else None


def _search_last(text: str, pattern: re.Pattern) -> Optional[str]:
    """Return last group match (for SGPA which appears multiple times)."""
    matches = list(pattern.finditer(text))
    return matches[-1].group(1).strip() if matches else None


def _parse_float(value: Optional[str]) -> Optional[float]:
    """Safely parse a float from string."""
    try:
        return float(value) if value else None
    except (ValueError, TypeError):
        return None


def _clean_name(name: str) -> str:
    """Remove trailing junk from extracted name."""
    # Remove patterns like 'Mother', extra whitespace
    name = re.sub(r"\s+Mother.*$", "", name, flags=re.IGNORECASE)
    return name.strip()
