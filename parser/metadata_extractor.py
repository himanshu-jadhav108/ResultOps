"""
ResultOps - Metadata Extractor
Dynamically detects university, college, department, session, and semester
from the PDF text without any hardcoding.

Fixes:
  - College: now correctly parses "College :[100] JSPM NARHE TECHNICAL CAMPUS, PUNE" format
  - Semester: now reads from student blocks (most frequent value) not header text,
              avoiding false matches from page titles like "Semester-3"
"""

import re
import logging
from dataclasses import dataclass
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class PDFMetadata:
    university_name: str
    college_name: str
    department_name: str
    semester_number: int
<<<<<<< HEAD
    session_type: str   # 'Winter' or 'Summer'
=======
    session_type: str  # 'Winter' or 'Summer'
>>>>>>> origin/develop
    session_year: int


def extract_metadata(full_text: str) -> PDFMetadata:
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]

    university_name = _extract_university(lines)
<<<<<<< HEAD
    college_name    = _extract_college(full_text)
=======
    college_name = _extract_college(full_text)
>>>>>>> origin/develop
    department_name = _extract_department(full_text)
    session_type, session_year = _extract_session(full_text)
    semester_number = _extract_semester_number(full_text)

    logger.info(
        f"Metadata: University={university_name}, College={college_name}, "
        f"Dept={department_name}, Sem={semester_number}, "
        f"Session={session_type} {session_year}"
    )

    return PDFMetadata(
        university_name=university_name,
        college_name=college_name,
        department_name=department_name,
        semester_number=semester_number,
        session_type=session_type,
        session_year=session_year,
    )


# ── UNIVERSITY ────────────────────────────────────────────────────────────────

<<<<<<< HEAD
def _extract_university(lines: list[str]) -> str:
    """First long non-numeric line near the top of the PDF."""
    for line in lines[:10]:
        if len(line) > 10 and not re.match(r'^\d+$', line):
=======

def _extract_university(lines: list[str]) -> str:
    """First long non-numeric line near the top of the PDF."""
    for line in lines[:10]:
        if len(line) > 10 and not re.match(r"^\d+$", line):
>>>>>>> origin/develop
            return line.strip()
    return lines[0] if lines else "Unknown University"


# ── COLLEGE ───────────────────────────────────────────────────────────────────

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def _extract_college(text: str) -> str:
    """
    Handles SPPU ledger format:
      College :[100] JSPM NARHE TECHNICAL CAMPUS, PUNE
      College:[200] Some Other College Name
      PunCode : 100\nCollege Name

    Priority order:
      1. 'College :[ N ] <name>' pattern  (most specific)
      2. 'College : <name>' pattern
      3. Line after PunCode
      4. Line containing Campus/Institute/College keyword
      5. Second non-empty line (fallback)
    """

    # Pattern 1: College :[100] JSPM NARHE TECHNICAL CAMPUS, PUNE
<<<<<<< HEAD
    match = re.search(
        r'College\s*:\s*\[\d+\]\s*([^\n]+)',
        text, re.IGNORECASE
    )
=======
    match = re.search(r"College\s*:\s*\[\d+\]\s*([^\n]+)", text, re.IGNORECASE)
>>>>>>> origin/develop
    if match:
        return match.group(1).strip()

    # Pattern 2: College : JSPM NARHE TECHNICAL CAMPUS (no bracket)
<<<<<<< HEAD
    match = re.search(
        r'College\s*:\s*([A-Z][^\n]{5,})',
        text, re.IGNORECASE
    )
    if match:
        name = match.group(1).strip()
        # Make sure we didn't grab a ledger label like "College Ledger"
        if not re.match(r'ledger|result|report', name, re.IGNORECASE):
            return name

    # Pattern 3: Line after PunCode : 100
    match = re.search(r'PunCode\s*[:\-]?\s*\d+\s*\n(.+)', text, re.IGNORECASE)
=======
    match = re.search(r"College\s*:\s*([A-Z][^\n]{5,})", text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        # Make sure we didn't grab a ledger label like "College Ledger"
        if not re.match(r"ledger|result|report", name, re.IGNORECASE):
            return name

    # Pattern 3: Line after PunCode : 100
    match = re.search(r"PunCode\s*[:\-]?\s*\d+\s*\n(.+)", text, re.IGNORECASE)
>>>>>>> origin/develop
    if match:
        return match.group(1).strip()

    # Pattern 4: Line with Campus / Institute keyword (not "Engineering" which catches dept)
    match = re.search(
<<<<<<< HEAD
        r'([A-Z][^\n]{5,80}(?:Campus|Institute|Polytechnic|Technology|University)[^\n]*)',
        text, re.IGNORECASE
=======
        r"([A-Z][^\n]{5,80}(?:Campus|Institute|Polytechnic|Technology|University)[^\n]*)",
        text,
        re.IGNORECASE,
>>>>>>> origin/develop
    )
    if match:
        return match.group(1).strip()

    # Fallback: second non-empty line
<<<<<<< HEAD
    lines = [l.strip() for l in text.splitlines() if l.strip()]
=======
    lines = [line.strip() for line in text.splitlines() if line.strip()]
>>>>>>> origin/develop
    if len(lines) > 1:
        return lines[1]

    return "Unknown College"


# ── DEPARTMENT ────────────────────────────────────────────────────────────────

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def _extract_department(text: str) -> str:
    """
    Extracts from 'Branch : <name>' or 'Department : <name>' pattern.
    Also handles 'Branch :[66] ARTIFICIAL INTELLIGENCE AND DATA SCIENCE' format.
    """

    # Pattern: Branch :[66] ARTIFICIAL INTELLIGENCE AND DATA SCIENCE
    match = re.search(
<<<<<<< HEAD
        r'(?:Branch|Department)\s*:\s*\[\d+\]\s*([^\n]+)',
        text, re.IGNORECASE
=======
        r"(?:Branch|Department)\s*:\s*\[\d+\]\s*([^\n]+)", text, re.IGNORECASE
>>>>>>> origin/develop
    )
    if match:
        return match.group(1).strip()

    # Pattern: Branch : ARTIFICIAL INTELLIGENCE AND DATA SCIENCE
    match = re.search(
<<<<<<< HEAD
        r'(?:Branch|Department)\s*[:\-]\s*([^\n]{3,})',
        text, re.IGNORECASE
=======
        r"(?:Branch|Department)\s*[:\-]\s*([^\n]{3,})", text, re.IGNORECASE
>>>>>>> origin/develop
    )
    if match:
        return match.group(1).strip()

    # Fallback: known branch name patterns
    match = re.search(
<<<<<<< HEAD
        r'(Computer Engineering|Information Technology|Electronics|'
        r'Mechanical|Civil|Electrical|E&TC|Chemical|'
        r'Artificial Intelligence|Data Science|AIDS|AIML|'
        r'Computer Science)[^\n]*',
        text, re.IGNORECASE
=======
        r"(Computer Engineering|Information Technology|Electronics|"
        r"Mechanical|Civil|Electrical|E&TC|Chemical|"
        r"Artificial Intelligence|Data Science|AIDS|AIML|"
        r"Computer Science)[^\n]*",
        text,
        re.IGNORECASE,
>>>>>>> origin/develop
    )
    if match:
        return match.group(1).strip()

    return "Unknown Department"


# ── SESSION ───────────────────────────────────────────────────────────────────

<<<<<<< HEAD
def _extract_session(text: str) -> tuple[str, int]:
    """Extract Winter/Summer and year from session markers in PDF."""

    match = re.search(
        r'(Winter|Summer)\s+Session\s+(\d{4})',
        text, re.IGNORECASE
    )
=======

def _extract_session(text: str) -> tuple[str, int]:
    """Extract Winter/Summer and year from session markers in PDF."""

    match = re.search(r"(Winter|Summer)\s+Session\s+(\d{4})", text, re.IGNORECASE)
>>>>>>> origin/develop
    if match:
        return match.group(1).capitalize(), int(match.group(2))

    # Fallback: find year
<<<<<<< HEAD
    year_match = re.search(r'\b(20\d{2})\b', text)
    year = int(year_match.group(1)) if year_match else 2025
    session = "Winter" if re.search(r'winter|nov|dec|jan', text, re.IGNORECASE) else "Summer"
=======
    year_match = re.search(r"\b(20\d{2})\b", text)
    year = int(year_match.group(1)) if year_match else 2025
    session = (
        "Winter" if re.search(r"winter|nov|dec|jan", text, re.IGNORECASE) else "Summer"
    )
>>>>>>> origin/develop
    return session, year


# ── SEMESTER ──────────────────────────────────────────────────────────────────

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def _extract_semester_number(text: str) -> int:
    """
    FIX: Previously picked up semester from page header/title which could be wrong
    (e.g. 'Semester-3' in title but students are actually Sem 5).

    New strategy:
      1. Find ALL occurrences of 'SEMESTER: N' inside student blocks
      2. Take the most frequent value (majority vote)
      3. Only fall back to header patterns if no student-level data found

    This is robust because every student block contains 'SEMESTER: N'
    and they all agree on the same semester.
    """

    # Strategy 1: collect all SEMESTER: N from student blocks
    # Student blocks have pattern like: SEMESTER: 5  (standalone line)
<<<<<<< HEAD
    all_matches = re.findall(
        r'SEMESTER\s*[:\-]?\s*(\d+)',
        text, re.IGNORECASE
    )
=======
    all_matches = re.findall(r"SEMESTER\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
>>>>>>> origin/develop

    if all_matches:
        counts = Counter(int(m) for m in all_matches)
        # Most common semester number across all student blocks
        most_common = counts.most_common(1)[0][0]
        logger.info(f"Semester detection: found {dict(counts)}, using {most_common}")
        return most_common

    # Strategy 2: Roman numerals (Sem-V, SEM IV etc.) — header fallback
<<<<<<< HEAD
    roman = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4,
        'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8
    }
    match = re.search(
        r'Sem(?:ester)?\s*[-]?\s*(VIII|VII|VI|IV|V|III|II|I)\b',
        text, re.IGNORECASE
=======
    roman = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}
    match = re.search(
        r"Sem(?:ester)?\s*[-]?\s*(VIII|VII|VI|IV|V|III|II|I)\b", text, re.IGNORECASE
>>>>>>> origin/develop
    )
    if match:
        val = match.group(1).upper()
        return roman.get(val, 1)

    raise ValueError(
        "Could not detect semester number from PDF.\n"
        "Make sure the PDF contains 'SEMESTER: N' in student records."
<<<<<<< HEAD
    )
=======
    )
>>>>>>> origin/develop
